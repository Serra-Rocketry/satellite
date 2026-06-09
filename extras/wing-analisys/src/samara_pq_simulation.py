# -*- coding: utf-8 -*-
"""Samara_PQ_Simulation — Bio-Inspired Autorotative Recovery System (SRAB)
Serra Rocketry Team — Helike Mission

Usage (pipeline completo com defaults):
    python samara_pq_simulation.py

Sobrescrever parâmetros via CLI:
    python samara_pq_simulation.py --dxf Asa2.DXF --n-wings 4 --mass 0.250 --altitude 1000
    python samara_pq_simulation.py --output resultados/ --max-step 0.1 --t-max 300
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar
from scipy.optimize import root

try:
    import ezdxf
except ImportError as import_error:
    raise ImportError(
        "Missing dependency 'ezdxf'. Install it with: .venv/bin/pip install ezdxf"
    ) from import_error


# =============================================================================
# CONFIG — Parâmetros principais da missão
# Altere aqui para mudar o comportamento padrão do pipeline.
# Todos os valores podem ser sobrescritos via argumentos CLI (ver --help).
# =============================================================================
CONFIG = {
    # --- Geometria da asa ---
    "dxf_path": Path(__file__).resolve().parent / "Asa2.DXF",  # arquivo DXF da asa
    "n_wings": 4,           # número de asas simétricas

    # --- Massa e estrutura ---
    "mass_kg": 0.250,       # massa total do sistema [kg] (limite regulatório PQ 1P)

    # --- Condições iniciais da simulação ---
    "altitude_m": 1000.0,   # altitude de liberação [m] (altura do apogeu do foguete)
    "theta_deg": 20.0,      # ângulo de conicidade inicial [graus]
    "theta_dot_0": 0.0,     # taxa de variação do pitch inicial [rad/s]
    "phi_dot_0": 0.1,       # spin inicial [rad/s] (~1 RPM — praticamente parado)
    "v0_0": 0.0,            # velocidade vertical inicial [m/s] (liberado no apogeu)

    # --- Parâmetros aerodinâmicos ---
    "f_factor": 0.3,        # fração de inércia de massa ao longo da asa (tensor I_yy)
    "beta_deg": 8.0,        # ângulo de passo geométrico β [graus] — rotação da asa em torno
                            # do eixo radial (X), visível na vista lateral (YZ). Fixado
                            # pelo encaixe circular. δ (diedro) é determinado pela flexão
                            # do material e capturado dinamicamente por θ.
    "cd0": 1.0,             # coeficiente de arrasto basal (captura efeito LEV)
    "rho": 1.225,           # densidade do ar [kg/m³] (nível do mar, ISA)

    # --- Integração numérica ---
    "t_max": 600.0,         # tempo máximo de simulação [s]
    "max_step": 0.2,        # passo máximo do integrador RK45 [s]

    # --- Saída ---
    "output_dir": str(Path(__file__).resolve().parent.parent / "results"),  # diretório de saída dos relatórios
}
# =============================================================================


class DxfWingProfile:
    """Load a single-wing contour from DXF and build a chord-width profile."""

    # pylint: disable=too-few-public-methods

    def __init__(self, dxf_path):
        self.dxf_path = Path(dxf_path)
        self.outline_points_mm = self._load_outline_points_mm()
        (
            self.outline_points_m,
            self.r0_m,
            self.rf_m,
            self.area_one_wing_m2,
            self._chord_width_m,
        ) = self._build_profile()

    def _load_outline_points_mm(self):
        """Read one contour from LWPOLYLINE, POLYLINE, or SPLINE entities."""
        if not self.dxf_path.exists():
            raise FileNotFoundError(f"DXF file not found: {self.dxf_path}")

        document = ezdxf.readfile(str(self.dxf_path))
        model_space = document.modelspace()

        lwpolylines = list(model_space.query("LWPOLYLINE"))
        if lwpolylines:
            points = [(point[0], point[1]) for point in lwpolylines[0].get_points()]
            if len(points) >= 3:
                return np.array(points, dtype=float)

        polylines = list(model_space.query("POLYLINE"))
        if polylines:
            points = [(point[0], point[1]) for point in polylines[0].points()]
            if len(points) >= 3:
                return np.array(points, dtype=float)

        splines = list(model_space.query("SPLINE"))
        if splines:
            points = []
            for spline in splines:
                points.extend((point[0], point[1]) for point in spline.control_points)
            if len(points) >= 3:
                return np.array(points, dtype=float)

        raise ValueError(
            f"No valid contour entity found in DXF: {self.dxf_path}. "
            "Expected one LWPOLYLINE, POLYLINE, or SPLINE with >= 3 points."
        )

    def _build_profile(self):
        """Convert contour into normalized coordinates and chord interpolation."""
        # pylint: disable=too-many-locals
        x_mm = self.outline_points_mm[:, 0]
        y_mm = self.outline_points_mm[:, 1]

        x_mm = x_mm - np.min(x_mm)
        y_center_mm = 0.5 * (np.min(y_mm) + np.max(y_mm))
        y_mm = y_mm - y_center_mm
        normalized_points_mm = np.column_stack([x_mm, y_mm])

        radius_max_mm = float(np.max(x_mm))
        if radius_max_mm <= 0.0:
            raise ValueError("Invalid DXF contour: maximum radius must be positive.")

        radial_centers_mm = np.linspace(0.0, radius_max_mm, 260)
        window_mm = max(radius_max_mm / 45.0, 1.0)

        chord_samples_mm = np.full_like(
            radial_centers_mm, fill_value=np.nan, dtype=float
        )
        for idx, radius_center in enumerate(radial_centers_mm):
            mask = np.abs(x_mm - radius_center) <= window_mm
            if not np.any(mask):
                nearest_index = np.argsort(np.abs(x_mm - radius_center))[:6]
                y_window = y_mm[nearest_index]
            else:
                y_window = y_mm[mask]

            if len(y_window) < 2:
                continue

            chord_samples_mm[idx] = np.max(y_window) - np.min(y_window)

        valid_mask = np.isfinite(chord_samples_mm)
        if np.count_nonzero(valid_mask) < 2:
            raise ValueError("Could not derive a valid chord distribution from DXF.")

        chord_samples_mm = np.interp(
            radial_centers_mm,
            radial_centers_mm[valid_mask],
            chord_samples_mm[valid_mask],
            left=0.0,
            right=0.0,
        )
        chord_samples_mm = np.clip(chord_samples_mm, 0.0, None)

        nonzero_mask = chord_samples_mm > 1e-6
        if not np.any(nonzero_mask):
            raise ValueError("Derived chord profile is zero across all radii.")

        r0_mm = float(radial_centers_mm[nonzero_mask][0])
        rf_mm = float(radial_centers_mm[nonzero_mask][-1])

        contour_area_mm2 = self._polygon_area_mm2(normalized_points_mm)
        chord_area_mm2 = float(np.trapezoid(chord_samples_mm, radial_centers_mm))
        area_one_wing_mm2 = (
            contour_area_mm2 if contour_area_mm2 > 0.0 else chord_area_mm2
        )

        chord_function_mm = interp1d(
            radial_centers_mm,
            chord_samples_mm,
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )

        def chord_width_m(radial_position_m):
            radial_position_mm = np.asarray(radial_position_m, dtype=float) * 1e3
            chord_mm = chord_function_mm(radial_position_mm)
            return np.clip(chord_mm * 1e-3, 0.0, None)

        return (
            normalized_points_mm * 1e-3,
            r0_mm * 1e-3,
            rf_mm * 1e-3,
            area_one_wing_mm2 * 1e-6,
            chord_width_m,
        )

    @staticmethod
    def _polygon_area_mm2(points_mm):
        """Compute closed-polygon area with the shoelace formula."""
        if len(points_mm) < 3:
            return 0.0

        points = np.asarray(points_mm, dtype=float)
        if not np.allclose(points[0], points[-1]):
            points = np.vstack([points, points[0]])

        return 0.5 * abs(
            np.sum(points[:-1, 0] * points[1:, 1] - points[1:, 0] * points[:-1, 1])
        )

    def chord_width_m(self, radial_position_m):
        """Return local chord width w(r) in meters."""
        return self._chord_width_m(radial_position_m)


class PocketQubeSamaraWing:
    """Aerodynamic and inertial model for a PocketQube samara wing set."""

    # pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        dxf_path=None,
        n_wings=4,
        mass=0.250,
        radius=None,
        f_factor=0.3,
        cd0=1.0,
        rho=1.225,
        beta_deg=8.0,
        k_induced=0.0,
        c_damp=0.0,
    ):
        if dxf_path is None:
            dxf_path = CONFIG["dxf_path"]
        self.dxf_path = Path(dxf_path)
        self.profile = DxfWingProfile(self.dxf_path)

        # 1. Regulatory mass and topology constraints
        self.mass = float(mass)   # massa total do sistema [kg]
        self.n_wings = n_wings

        # 2. Aerodynamic geometry from DXF profile
        self.base_r0 = self.profile.r0_m
        self.base_rf = self.profile.rf_m
        self.radius = self.base_rf if radius is None else float(radius)
        self.radius_scale = max(self.radius / self.base_rf, 1e-6)

        # 3. Bluff-body and atmospheric constants
        self.pocketqube_side_m = 0.05
        self.a_face = 0.058 * 0.064
        self.cd_bluff_body = 1.05
        self.rho = float(rho)

        # 4. Corrections and coefficients
        self.f_factor = f_factor
        self.cd0 = cd0
        self.k_induced = k_induced
        self.c_damp = c_damp
        self.mu_air = 1.8e-5
        self.last_reynolds_mean = np.nan

        # Aerodynamic realism tuning knobs
        self.cl_max = 1.50
        self.lift_efficiency = 0.95
        self.k_tip_loss = 0.12
        self.k_induced_drag = 0.04
        self.k_profile_loss = 0.03
        self.k_spin_drag = 0.004
        self.c_rot_damp = 3.0e-6
        # psi_bias_deg e psi_rate_gain removidos — vertical_alignment_factor
        # agora usa cos(θ) puro conforme equações do documento §6.1.

        # β — ângulo de passo geométrico (vista lateral, plano YZ)
        # Rotação da asa em torno do eixo radial X, fixada pelo encaixe circular.
        # δ (diedro, vista frontal XZ) é capturado dinamicamente por θ via flexão do material.
        self.beta_mount = np.radians(beta_deg)

        self.i_xx = 0.0
        self.i_yy = 0.0
        self.i_zz = 0.0

        self._apply_geometry_scaling()

    def _apply_geometry_scaling(self):
        """Scale DXF geometry according to target aerodynamic radius.

        O DXF é desenhado com x=0 na borda do cubo (não no eixo de rotação).
        body_h = metade do lado do PQ (25mm) é somado a r0 e rf para que
        representem distâncias físicas reais desde o eixo de rotação.
        Isso afeta: BET (integração de r0 a rf), tensor de inércia e plots.
        """
        body_h = self.pocketqube_side_m / 2.0          # 0.025 m
        self.r0 = body_h + self.base_r0 * self.radius_scale
        self.rf = body_h + self.base_rf * self.radius_scale
        self.wing_area_one_m2 = self.profile.area_one_wing_m2 * (self.radius_scale**2)
        # Offset x do contorno para que a raiz parta da borda do cubo na vista superior
        outline_scaled = self.profile.outline_points_m * self.radius_scale
        self.wing_outline_points_m = outline_scaled + np.array([body_h, 0.0])
        self.integration_nodes = np.linspace(self.r0, self.rf, 96)
        self.integration_chord = self.chord_width(self.integration_nodes)
        self._initialize_inertia_tensor()

    def _initialize_inertia_tensor(self):
        """Inertia tensor around pitch/yaw axes — corpo + asas separados.

        Documento §3.1: I_y3y3 = I_z3z3, I_x3x3 = 0.
        Decomposição física:
          • Corpo PQ (massa concentrada em r0): I_corpo = m_body * r0²
          • Asas (vareta uniforme de r0 a rf):   I_asas  = (1/3)*m_wings*(rf²-r0²)
        f_factor calibra a fração de massa alocada às asas vs corpo.
        """
        m_wings = self.f_factor * self.mass          # massa efetiva das asas
        m_body  = self.mass - m_wings                # massa restante (corpo PQ)
        r0 = max(self.r0, 1e-6)
        rf = max(self.rf, r0 + 1e-6)
        i_wings = (1.0 / 3.0) * m_wings * (rf**2 - r0**2)
        i_body  = m_body * r0**2                     # ponto concentrado em r0
        self.i_xx = 0.0
        self.i_yy = i_wings + i_body
        self.i_zz = self.i_yy

    def update_geometry(self, radius, f_factor, cd0, n_wings):
        """Update scaled geometry and inertial factors for optimization iterations."""
        self.radius = float(radius)
        self.radius_scale = max(self.radius / self.base_rf, 1e-6)
        self.f_factor = f_factor
        self.cd0 = cd0
        self.n_wings = n_wings
        self._apply_geometry_scaling()

    def chord_width(self, radial_position_m):
        """Scaled chord width function w(r) from the DXF contour.

        radial_position_m é medido a partir do eixo de rotação (centro do satélite).
        O perfil DXF usa coordenadas a partir da borda do cubo (x=0 = borda),
        portanto subtraímos body_h antes de consultar o perfil.
        """
        body_h = self.pocketqube_side_m / 2.0          # 0.025 m
        radial_array = np.asarray(radial_position_m, dtype=float)
        chord_result = np.zeros_like(radial_array, dtype=float)

        valid_mask = (radial_array >= self.r0) & (radial_array <= self.rf)
        if np.any(valid_mask):
            # Converter de coordenada global (centro) para coordenada DXF (borda)
            r_dxf = (radial_array[valid_mask] - body_h) / self.radius_scale
            base_chord = np.asarray(
                self.profile.chord_width_m(np.clip(r_dxf, 0.0, None)), dtype=float
            )
            chord_result[valid_mask] = np.clip(
                base_chord * self.radius_scale, 0.0, None
            )

        if np.isscalar(radial_position_m):
            return float(chord_result)
        return chord_result

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _local_kinematics(self, r, theta, theta_dot, phi_dot, v_0):
        """Compute local freestream magnitude and angle of attack."""
        v_py = r * phi_dot * np.cos(theta)
        # Simplified inflow: optional induced velocity scales with local rotational speed.
        v_induced = self.k_induced * np.abs(r * phi_dot)
        v_pz = v_0 * np.cos(theta) + r * theta_dot + v_induced
        u_inf_sq = v_py**2 + v_pz**2
        # α_eff = α cinemático + β geométrico (passo do encaixe, vista lateral YZ)
        # β desloca o ângulo de ataque independentemente da cinemática de voo.
        alpha = np.arctan2(-v_pz, v_py) + self.beta_mount
        return u_inf_sq, alpha

    def vertical_alignment_factor(self, theta, theta_dot, phi_dot):
        """Projeção vertical da força aerodinâmica — equação do documento §6.1.

        v̇₀ = −g + F_z3·cos(θ)/m
        Retorna cos(θ) diretamente, sem fator ψ empírico não documentado.
        """
        _ = theta_dot, phi_dot
        return np.cos(theta)

    # pylint: disable=too-many-locals
    def compute_forces_and_moments(self, theta, theta_dot, phi_dot, v_0):
        """Compute aerodynamic force and moment components for one wing."""

        radial = self.integration_nodes
        chord_local = self.integration_chord
        radial_ratio = np.clip(radial / max(self.rf, 1e-6), 0.0, 1.0)

        u_inf_sq, alpha = self._local_kinematics(radial, theta, theta_dot, phi_dot, v_0)
        cl_raw = 2.0 * np.pi * np.sin(alpha)
        cl = self.cl_max * np.tanh(cl_raw / self.cl_max)

        tip_factor = np.clip(1.0 - self.k_tip_loss * (radial_ratio**2), 0.55, 1.0)
        cl_eff = cl * self.lift_efficiency * tip_factor

        # Polar aerodinâmica — documento §3.3: CD(α) = CL(α)·sin(α) + CD₀
        # usa cl_raw (teoria de perfil fino) para manter a relação polar intacta;
        # cl_eff (com tip_factor e lift_efficiency) só é aplicado à sustentação.
        cd_base = self.cd0 + cl_raw * np.sin(alpha)
        cd_induced = self.k_induced_drag * (cl_eff**2)
        cd_profile = self.k_profile_loss * (1.0 - tip_factor)
        spin_ratio = (
            np.abs(phi_dot) * max(self.rf, 1e-4) / max(np.sqrt(np.mean(u_inf_sq)), 1e-3)
        )
        cd_spin = self.k_spin_drag * (spin_ratio**2)
        cd = np.clip(cd_base + cd_induced + cd_profile + cd_spin, self.cd0, 4.0)

        local_speed = np.sqrt(np.clip(u_inf_sq, 0.0, None))
        reynolds = self.rho * local_speed * chord_local / self.mu_air
        self.last_reynolds_mean = float(np.mean(reynolds))

        force_scale = 0.5 * self.rho * chord_local * u_inf_sq
        integrand_fy3 = force_scale * (np.sin(alpha) * cl_eff - np.cos(alpha) * cd)
        integrand_fz3 = force_scale * (np.cos(alpha) * cl_eff + np.sin(alpha) * cd)

        f_y3 = float(np.trapezoid(integrand_fy3, radial))
        f_z3 = float(np.trapezoid(integrand_fz3, radial))
        m_y3 = float(np.trapezoid(-radial * integrand_fz3, radial))
        m_z3 = float(np.trapezoid(radial * integrand_fy3, radial))
        m_z3 -= self.c_rot_damp * phi_dot * np.abs(phi_dot)

        return f_y3, f_z3, m_y3, m_z3


class PocketQubeFlightDynamics:
    """Dynamic model and integration utilities for samara descent."""

    def __init__(self, pq_wing):
        self.wing = pq_wing
        self.g = 9.81

    # pylint: disable=too-many-locals
    def _state_derivatives(self, t, state):
        _ = t
        theta, theta_dot, phi_dot, v_0, z_alt = state
        _ = z_alt

        cos_theta = np.clip(np.cos(theta), 1e-3, None)
        tan_theta = np.tan(np.clip(theta, -np.pi / 2 + 1e-3, np.pi / 2 - 1e-3))

        f_y3_1, f_z3_1, m_y3_1, m_z3_1 = self.wing.compute_forces_and_moments(
            theta, theta_dot, phi_dot, v_0
        )

        n_wings = self.wing.n_wings
        f_y3 = f_y3_1 * n_wings
        f_z3_wings = f_z3_1 * n_wings
        m_y3 = m_y3_1 * n_wings
        m_z3 = m_z3_1 * n_wings
        _ = f_y3

        m_y3 -= self.wing.c_damp * theta_dot
        m_z3 -= self.wing.c_damp * phi_dot

        # Arrasto do corpo: sempre opõe-se à direção do movimento (−sign(v₀)).
        # v₀ < 0 em descida → drag > 0 (↑, correto); v₀ > 0 → drag < 0 (↓, correto).
        f_drag_cube = (
            -np.sign(v_0)
            * 0.5
            * self.wing.rho
            * v_0**2
            * self.wing.a_face
            * self.wing.cd_bluff_body
        )
        f_z3_total = f_z3_wings + f_drag_cube
        vertical_factor = self.wing.vertical_alignment_factor(theta, theta_dot, phi_dot)

        d_theta = theta_dot
        d_theta_dot = (-m_y3 / self.wing.i_yy) - (phi_dot**2) * np.sin(
            theta
        ) * cos_theta
        d_phi_dot = (
            m_z3 / (self.wing.i_yy * cos_theta)
        ) + 2 * phi_dot * theta_dot * tan_theta
        d_v0 = -self.g + (f_z3_total * vertical_factor) / self.wing.mass
        d_z_alt = v_0

        return [d_theta, d_theta_dot, d_phi_dot, d_v0, d_z_alt]

    # pylint: disable=too-many-locals
    def calculate_steady_state(self, preferred_vf=None):
        """Solve for a steady operating point using a multi-start strategy."""

        def system_equations(state_vars):
            theta, phi_dot, v_0 = state_vars
            state = [theta, 0.0, phi_dot, v_0, 1000.0]
            derivs = self._state_derivatives(0, state)
            return np.array([derivs[1], derivs[2], derivs[3]], dtype=float)

        theta_guesses = np.radians([5.0, 10.0, 20.0, 30.0, 45.0])
        phi_guesses = [2.0, 5.0, 10.0, 20.0, 40.0, 80.0]
        v0_guesses = [-5.0, -10.0, -15.0, -20.0, -25.0, -35.0, -50.0]

        best_solution = None
        best_score = np.inf

        for theta_guess in theta_guesses:
            for phi_guess in phi_guesses:
                for v0_guess in v0_guesses:
                    solution = root(
                        system_equations,
                        [theta_guess, phi_guess, v0_guess],
                        method="hybr",
                    )
                    if not solution.success:
                        continue

                    theta_sol, phi_dot_sol, v0_sol = solution.x
                    residual_norm = float(np.linalg.norm(system_equations(solution.x)))
                    if preferred_vf is None:
                        score = residual_norm
                    else:
                        score = abs(v0_sol - preferred_vf) + 0.05 * residual_norm

                    if score < best_score:
                        best_score = score
                        best_solution = (theta_sol, 0.0, phi_dot_sol, v0_sol)

        return best_solution

    def simulate_drop(self, initial_conditions=None, t_span=(0, 150.0), max_step=0.05):
        """Run time-domain drop simulation until ground impact."""
        if initial_conditions is None:
            initial_conditions = [np.radians(20), 0.0, 0.1, 0.0, 1000.0]

        def hit_ground(_, state_vector):
            return state_vector[4]

        hit_ground.terminal = True
        hit_ground.direction = -1

        print("-> Propagating ballistic trajectory (this may take a few seconds)...")
        return solve_ivp(
            fun=self._state_derivatives,
            t_span=t_span,
            y0=initial_conditions,
            method="RK45",
            events=hit_ground,
            max_step=max_step,
        )


class PocketQubeLRRVisualizer:
    """Generate LRR-oriented plots from simulation output."""

    # pylint: disable=too-few-public-methods
    def __init__(self, simulation_solution, output_dir="extras/wing-analisys"):
        self.t = simulation_solution.t
        self.theta = np.degrees(simulation_solution.y[0])
        self.theta_dot = simulation_solution.y[1]
        self.phi_dot = simulation_solution.y[2] / (2 * np.pi)
        self.v0 = simulation_solution.y[3]
        self.z_alt = simulation_solution.y[4]
        self.output_dir = Path(output_dir)

    def generate_lrr_report(self, beta_deg=None, show_plot=False):
        """Render a 2x2 diagnostics dashboard for descent certification."""
        beta_str = f"β={beta_deg:.1f}°" if beta_deg is not None else ""
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(
            f"LRR Certification Report — PocketQube 1P SRAB  {beta_str}",
            fontsize=15, fontweight="bold",
        )

        # ── [0,0] Altitude vs tempo ─────────────────────────
        ax = axs[0, 0]
        ax.plot(self.t, self.z_alt, color="#1a6ea8", linewidth=2, label="Altitude simulada")
        alt0 = self.z_alt[0]
        ax.axhline(alt0, color="gray", linestyle=":", linewidth=1, alpha=0.6,
                   label=f"Altitude inicial ({alt0:.0f} m)")
        ax.set_title("Perfil de Descida — Altitude AGL")
        ax.set_ylabel("Altitude (m)")
        ax.set_xlabel("Tempo (s)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

        # ── [0,1] Velocidade vertical ────────────────────────
        ax = axs[0, 1]
        v_abs = np.abs(self.v0)
        ax.plot(self.t, v_abs, color="#333", linewidth=2, label="|v₀| simulado")
        ax.axhspan(20, 45, color="green", alpha=0.15, label="Janela LASC (20–45 m/s)")
        ax.axhline(45, color="red", linestyle="--", linewidth=1.2, label="Limite máx. LASC (45 m/s)")
        ax.axhline(20, color="orange", linestyle="--", linewidth=1.2, label="Limite mín. LASC (20 m/s)")
        # velocidade terminal mediana (regime estacionário — última 20% da trajetória)
        n_steady = max(1, len(self.v0) // 5)
        v_term = float(np.median(v_abs[-n_steady:]))
        ax.axhline(v_term, color="#1a6ea8", linestyle=":", linewidth=2,
                   label=f"v_terminal ≈ {v_term:.1f} m/s")
        ax.set_title("Velocidade Vertical vs Janela LASC")
        ax.set_ylabel("|v₀| (m/s)")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylim(bottom=0)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

        # ── [1,0] Ângulo de conicidade θ (δ dinâmico) ───────
        ax = axs[1, 0]
        ax.plot(self.t, self.theta, color="#8e44ad", linewidth=2, label="θ (conicidade)")
        theta_eq = float(np.median(self.theta[-n_steady:]))
        ax.axhline(theta_eq, color="#8e44ad", linestyle=":", linewidth=1.5,
                   label=f"θ_eq ≈ {theta_eq:.1f}° (equilíbrio)")
        ax.set_title("Ângulo de Conicidade θ — Diedro Dinâmico (δ)")
        ax.set_ylabel("θ (graus)")
        ax.set_xlabel("Tempo (s)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

        # ── [1,1] Spin φ̇ em RPM ─────────────────────────────
        ax = axs[1, 1]
        spin_rpm = self.phi_dot * 60.0   # phi_dot já em rev/s (÷2π foi feito no __init__)
        ax.plot(self.t, spin_rpm, color="#27ae60", linewidth=2, label="Spin φ̇")
        spin_eq = float(np.median(spin_rpm[-n_steady:]))
        ax.axhline(spin_eq, color="#27ae60", linestyle=":", linewidth=1.5,
                   label=f"Spin_eq ≈ {spin_eq:.0f} RPM")
        ax.set_title("Spin de Autorrotação φ̇")
        ax.set_ylabel("RPM")
        ax.set_xlabel("Tempo (s)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

        plt.tight_layout(rect=[0, 0.02, 1, 0.96])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / "samara_pq_lrr_report.png"
        fig.savefig(report_path, dpi=150, bbox_inches="tight")
        print(f"Saved LRR plot:    {report_path}")

        if show_plot:
            plt.show()
        else:
            plt.close(fig)
        
        return float(theta_eq), float(spin_eq)


# pylint: disable=too-many-locals,too-many-statements
def plot_wing_geometry_views(wing, theta_eq_deg=None, output_dir="extras/wing-analisys"):
    """Gera três vistas ortogonais do sistema asa+cubo.

    Vista superior (XY) — plano horizontal, mostra varredura Λ (forma do DXF).
    Vista frontal (XZ)  — olhando ao longo de Y, mostra δ/θ (diedro / conicidade).
    Vista lateral (YZ)  — olhando ao longo de X (da ponta para a raiz), mostra β (passo).

    theta_eq_deg: ângulo de conicidade de equilíbrio [graus] para a vista frontal.
                  Se None, usa 15° como estimativa conservadora.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    body_s   = wing.pocketqube_side_m          # 0.050 m
    body_h   = body_s / 2.0
    rf_m     = wing.rf
    r0_m     = wing.r0
    beta     = wing.beta_mount                 # rad — passo geométrico (vista lateral)
    theta_eq = np.radians(theta_eq_deg if theta_eq_deg is not None else 15.0)
    n        = wing.n_wings

    COLOR_BODY = "#264653"
    COLOR_WING = "#2a9d8f"
    COLOR_EDGE = "#1f7f76"
    ALPHA_FILL = 0.50

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.suptitle(
        f"Wing Geometry — {n} wings | DXF: {wing.dxf_path.name} | "
        f"β = {np.degrees(beta):.1f}°  |  θ_eq ≈ {np.degrees(theta_eq):.1f}°",
        fontsize=13, fontweight="bold",
    )

    # ── VISTA SUPERIOR (XY) ─────────────────────────────────
    ax = axes[0]
    # Corpo
    bxy = np.array([[-body_h,-body_h],[body_h,-body_h],[body_h,body_h],[-body_h,body_h]])
    ax.fill(bxy[:,0]*1e3, bxy[:,1]*1e3, color=COLOR_BODY, alpha=0.45)
    ax.plot(np.r_[bxy[:,0],bxy[0,0]]*1e3, np.r_[bxy[:,1],bxy[0,1]]*1e3,
            color=COLOR_BODY, linewidth=2)
    ax.text(0, 0, "PocketQube\n50×50 mm", ha="center", va="center", fontsize=9)
    # Asas (planforma DXF, projetada no plano XY — sem projeção de θ ou β)
    for wi in range(n):
        ang = wi * (2.0 * np.pi / n)
        R = np.array([[np.cos(ang), -np.sin(ang)],[np.sin(ang), np.cos(ang)]])
        pts = wing.wing_outline_points_m @ R.T
        # Clipar pontos que entram dentro do cubo (|x| < body_h na direção radial)
        radial_dist = np.sqrt(pts[:,0]**2 + pts[:,1]**2)
        pts_plot = pts[radial_dist >= body_h * 0.95]
        if len(pts_plot) >= 3:
            ax.fill(pts_plot[:,0]*1e3, pts_plot[:,1]*1e3, color=COLOR_WING, alpha=ALPHA_FILL)
            ax.plot(np.r_[pts_plot[:,0],pts_plot[0,0]]*1e3,
                    np.r_[pts_plot[:,1],pts_plot[0,1]]*1e3,
                    color=COLOR_EDGE, linewidth=1.2)
        else:
            ax.fill(pts[:,0]*1e3, pts[:,1]*1e3, color=COLOR_WING, alpha=ALPHA_FILL)
            ax.plot(np.r_[pts[:,0],pts[0,0]]*1e3, np.r_[pts[:,1],pts[0,1]]*1e3,
                    color=COLOR_EDGE, linewidth=1.2)
    lim = max(rf_m, body_h)*1e3*1.35
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
    body_a = body_s**2 * 1e4
    wing_a = n * wing.wing_area_one_m2 * 1e4
    ax.set_title(f"Vista Superior (XY) — Varredura Λ\nÁrea corpo: {body_a:.1f} cm²  |  Asas: {wing_a:.1f} cm²  |  Total: {body_a+wing_a:.1f} cm²")

    # ── VISTA FRONTAL (XZ) ──────────────────────────────────
    # Olhando ao longo de Y → plano XZ.
    # A asa se estende radialmente em X e sobe em Z pelo diedro dinâmico θ_eq.
    # Projeção da asa: x_proj = r·cos(θ_eq), z_proj = r·sin(θ_eq)
    ax = axes[1]
    # Corpo (quadrado XZ)
    bxz = np.array([[-body_h,-body_h],[body_h,-body_h],[body_h,body_h],[-body_h,body_h]])
    ax.fill(bxz[:,0]*1e3, bxz[:,1]*1e3, color=COLOR_BODY, alpha=0.45)
    ax.plot(np.r_[bxz[:,0],bxz[0,0]]*1e3, np.r_[bxz[:,1],bxz[0,1]]*1e3,
            color=COLOR_BODY, linewidth=2)
    ax.text(0, 0, "PQ", ha="center", va="center", fontsize=9)
    # Asas: para cada asa, projeta contorno no plano XZ com inclinação θ_eq
    # Extrai perfil de corda ao longo do raio para montar o contorno 3D projetado
    r_arr = np.linspace(r0_m, rf_m, 60)
    for wi in range(n):
        # sinal do lado (asas opostas vão para ±X)
        side = 1 if wi < n/2 else -1
        # contorno superior e inferior da asa na vista frontal
        # aproximação: retângulo com largura = corda média, inclinado em θ_eq
        chord_vals = np.array([wing.chord_width(r) for r in r_arr])
        # A asa parte do canto superior do cubo: (±body_h, +body_h).
        # r_local = distância desde a borda do cubo (não desde o eixo de rotação),
        # evitando dupla contagem de body_h no deslocamento vertical e horizontal.
        r_local = r_arr - body_h   # 0 na raiz, (rf-body_h) na ponta
        x_top = side * (body_h + r_local * np.cos(theta_eq))
        z_top = body_h + r_local * np.sin(theta_eq) + chord_vals * np.sin(beta) / 2
        x_bot = side * (body_h + r_local * np.cos(theta_eq))
        z_bot = body_h + r_local * np.sin(theta_eq) - chord_vals * np.sin(beta) / 2
        # Polígono fechado
        x_poly = np.concatenate([x_top, x_bot[::-1]]) * 1e3
        z_poly = np.concatenate([z_top, z_bot[::-1]]) * 1e3
        ax.fill(x_poly, z_poly, color=COLOR_WING, alpha=ALPHA_FILL)
        ax.plot(x_poly, z_poly, color=COLOR_EDGE, linewidth=1.0)
    # Anotação do ângulo θ — parte do canto superior direito do cubo
    r_ann_loc = (rf_m - body_h) * 0.6   # r_local para anotação
    x0_ann = body_h * 1e3
    z0_ann = body_h * 1e3
    ax.annotate("", xy=(x0_ann + r_ann_loc*np.cos(theta_eq)*1e3,
                        z0_ann + r_ann_loc*np.sin(theta_eq)*1e3),
                xytext=(x0_ann + r_ann_loc*1e3, z0_ann),
                arrowprops=dict(arrowstyle="-|>", color="purple", lw=1.2))
    ax.text(x0_ann + r_ann_loc*np.cos(theta_eq/2)*1e3*1.05,
            z0_ann + r_ann_loc*np.sin(theta_eq/2)*1e3,
            f"θ≈{np.degrees(theta_eq):.0f}°", color="purple", fontsize=9)
    lim_xz = max(rf_m, body_h)*1e3*1.35
    ax.set_xlim(-lim_xz, lim_xz); ax.set_ylim(-lim_xz*0.4, lim_xz)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")
    ax.set_title(f"Vista Frontal (XZ) — Diedro δ / conicidade θ\nθ_eq ≈ {np.degrees(theta_eq):.1f}°  (dinâmico, flexão do material)")

    # ── VISTA LATERAL (YZ) ──────────────────────────────────
    # Olhando ao longo de X (da ponta para a raiz) → plano YZ.
    # Mostra a seção transversal da asa inclinada em β.
    ax = axes[2]
    # Corpo
    byz = np.array([[-body_h,-body_h],[body_h,-body_h],[body_h,body_h],[-body_h,body_h]])
    ax.fill(byz[:,0]*1e3, byz[:,1]*1e3, color=COLOR_BODY, alpha=0.45)
    ax.plot(np.r_[byz[:,0],byz[0,0]]*1e3, np.r_[byz[:,1],byz[0,1]]*1e3,
            color=COLOR_BODY, linewidth=2)
    ax.text(0, 0, "PQ", ha="center", va="center", fontsize=9)
    # Seção da asa: a corda se projeta no plano YZ inclinada em β
    # Para cada raio r, a corda tem comprimento w(r) inclinada em β
    # Na vista lateral, a projeção em Y = w·cos(β), em Z = w·sin(β)
    # Mostramos apenas a seção em r médio como representativa
    r_mid   = (r0_m + rf_m) / 2.0
    chord_m = wing.chord_width(r_mid)
    # Seção no ponto de encaixe: topo do cubo (z = +body_h)
    attach_y = 0.0
    attach_z = body_h
    # borda de ataque sobe em β, bordo de fuga desce
    le_y = attach_y - (chord_m / 2) * np.cos(beta)
    le_z = attach_z + (chord_m / 2) * np.sin(beta)
    te_y = attach_y + (chord_m / 2) * np.cos(beta)
    te_z = attach_z - (chord_m / 2) * np.sin(beta)
    # Desenha espessura simbólica da asa (0.6mm PETG)
    t_asa = 0.0006  # m
    perp_y = -np.sin(beta)  # vetor perpendicular à corda
    perp_z = -np.cos(beta)
    wing_yz = np.array([
        [le_y + perp_y*t_asa/2, le_z + perp_z*t_asa/2],
        [te_y + perp_y*t_asa/2, te_z + perp_z*t_asa/2],
        [te_y - perp_y*t_asa/2, te_z - perp_z*t_asa/2],
        [le_y - perp_y*t_asa/2, le_z - perp_z*t_asa/2],
    ]) * 1e3
    ax.fill(wing_yz[:,0], wing_yz[:,1], color=COLOR_WING, alpha=0.7)
    ax.plot(np.r_[wing_yz[:,0],wing_yz[0,0]], np.r_[wing_yz[:,1],wing_yz[0,1]],
            color=COLOR_EDGE, linewidth=1.5)
    # Linha de corda (eixo de β)
    ax.plot([le_y*1e3, te_y*1e3], [le_z*1e3, te_z*1e3],
            color="orange", linewidth=1.5, linestyle="--", label="linha de corda")
    # Linha horizontal de referência (β=0)
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.5,
               label="β = 0° (referência)")
    # Arco de β
    ang_arr = np.linspace(0, beta, 30)
    r_arc = chord_m * 0.35 * 1e3
    ax.plot(r_arc*np.cos(ang_arr + np.pi), r_arc*np.sin(ang_arr + np.pi),
            color="steelblue", linewidth=1.5)
    ax.text(-(r_arc*1.15)*np.cos(beta/2), (r_arc*1.15)*np.sin(beta/2),
            f"β={np.degrees(beta):.1f}°", color="steelblue", fontsize=10, fontweight="bold")
    # Anotações LE/TE
    ax.annotate("LE", xy=(le_y*1e3, le_z*1e3), fontsize=9, color="#1f7f76",
                xytext=(le_y*1e3-5, le_z*1e3+3))
    ax.annotate("TE", xy=(te_y*1e3, te_z*1e3), fontsize=9, color="#1f7f76",
                xytext=(te_y*1e3+1, te_z*1e3-4))
    lim_yz = max(chord_m*0.8, body_h) * 1e3 * 2.2
    ax.set_xlim(-lim_yz, lim_yz); ax.set_ylim(-lim_yz*0.6, lim_yz*0.6)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.25)
    ax.set_xlabel("Y (mm)"); ax.set_ylabel("Z (mm)")
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title(f"Vista Lateral (YZ) — Passo β\nβ = {np.degrees(beta):.1f}°  (encaixe circular)  |  corda em r_mid = {chord_m*1e3:.1f} mm")

    plt.tight_layout()
    out_path = out_dir / "samara_pq_geometry_views.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved geometry views: {out_path}")


class PocketQubeSamaraOptimizer:
    """Numerical optimizer for topology-specific descent tuning."""

    # pylint: disable=too-few-public-methods
    def __init__(self, flight_solver, target_vf=-25.0):
        self.solver = flight_solver
        self.target_vf = target_vf
        self._impact_cache = {}

    def _cost_function_radius(self, radius, n_wings, f_factor, cd0):
        """Objective: squared error using radius as the only decision variable."""
        self.solver.wing.update_geometry(radius, f_factor, cd0, n_wings)
        steady_states = self.solver.calculate_steady_state(preferred_vf=self.target_vf)
        if steady_states is None:
            return 1e6
        return (steady_states[3] - self.target_vf) ** 2

    def optimize_radius_for_topology(self, n_wings):
        """Optimize only aerodynamic radius for a fixed configuration."""
        print(
            f"\n[ENGINEERING] Solving required radius for topology N={n_wings} wings..."
        )

        f_factor_fixed = self.solver.wing.f_factor
        cd0_fixed = self.solver.wing.cd0
        base_radius = self.solver.wing.base_rf
        bounds = (0.10 * base_radius, 1.80 * base_radius)

        result = minimize_scalar(
            self._cost_function_radius,
            args=(n_wings, f_factor_fixed, cd0_fixed),
            method="bounded",
            bounds=bounds,
            options={"xatol": 1e-4, "maxiter": 120},
        )

        if result.success:
            radius_opt = float(result.x)
            velocity_error = float(np.sqrt(max(result.fun, 0.0)))
            print("[SUCCESS] Radius target solved!")
            print(f" -> Required aerodynamic radius: {radius_opt * 100:.2f} cm")
            print(f" -> Fixed inertia factor (f): {f_factor_fixed:.3f}")
            print(f" -> Fixed vortex requirement (Cd0): {cd0_fixed:.3f}")
            print(f" -> Residual |vf - target|: {velocity_error:.3f} m/s")
            return radius_opt

        print("[FAILURE] Could not solve radius for the requested target vf.")
        return None

    @staticmethod
    def _impact_vertical_velocity(solution):
        """Get vertical velocity at impact event or fallback to final sample."""
        if solution.t_events and len(solution.t_events[0]) > 0:
            return float(solution.y_events[0][0][3]), True
        return float(solution.y[3][-1]), False

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _cost_function_radius_impact(
        self,
        radius,
        n_wings,
        f_factor,
        cd0,
        target_impact_vf,
        sim_t_span,
        sim_max_step,
    ):
        """Objective based on impact velocity mismatch from time simulation."""
        cache_key = (
            round(float(radius), 6),
            n_wings,
            round(float(f_factor), 4),
            round(float(cd0), 4),
            round(float(target_impact_vf), 3),
            sim_t_span,
            round(float(sim_max_step), 3),
        )
        if cache_key in self._impact_cache:
            return self._impact_cache[cache_key]

        self.solver.wing.update_geometry(radius, f_factor, cd0, n_wings)
        solution = self.solver.simulate_drop(t_span=sim_t_span, max_step=sim_max_step)
        impact_vz, impact_detected = self._impact_vertical_velocity(solution)
        error_sq = (impact_vz - target_impact_vf) ** 2

        if impact_detected:
            score = error_sq
        else:
            # Prefer solutions that actually hit the ground inside t_span.
            altitude_penalty = abs(float(solution.y[4][-1])) * 0.01
            score = error_sq + altitude_penalty

        self._impact_cache[cache_key] = score
        return score

    def optimize_radius_for_impact(
        self,
        n_wings,
        target_impact_vf=-25.0,
        sim_t_span=(0.0, 600.0),
        sim_max_step=0.2,
    ):
        """Optimize radius to match target impact vertical velocity."""
        print("\n[ENGINEERING] Solving required radius for target impact vf=")
        print(f"{target_impact_vf:.2f} m/s...")

        f_factor_fixed = self.solver.wing.f_factor
        cd0_fixed = self.solver.wing.cd0
        base_radius = self.solver.wing.base_rf
        bounds = (0.08 * base_radius, 2.00 * base_radius)

        self._impact_cache.clear()
        result = minimize_scalar(
            self._cost_function_radius_impact,
            args=(
                n_wings,
                f_factor_fixed,
                cd0_fixed,
                target_impact_vf,
                sim_t_span,
                sim_max_step,
            ),
            method="bounded",
            bounds=bounds,
            options={"xatol": 1e-4, "maxiter": 45},
        )

        if result.success:
            radius_opt = float(result.x)
            self.solver.wing.update_geometry(
                radius_opt, f_factor_fixed, cd0_fixed, n_wings
            )
            verification = self.solver.simulate_drop(
                t_span=sim_t_span, max_step=sim_max_step
            )
            impact_vz, impact_detected = self._impact_vertical_velocity(verification)
            velocity_error = abs(impact_vz - target_impact_vf)

            print("[SUCCESS] Impact-velocity radius solved!")
            print(f" -> Required aerodynamic radius: {radius_opt * 100:.2f} cm")
            print(f" -> Impact event detected: {impact_detected}")
            print(f" -> Impact vertical velocity: {impact_vz:.3f} m/s")
            print(f" -> Residual |vf_impact - target|: {velocity_error:.3f} m/s")
            return radius_opt

        print("[FAILURE] Could not solve radius for target impact velocity.")
        return None


class PocketQubeMissionReporter:
    """Create mission report artifacts and print key impact metrics."""

    # pylint: disable=too-few-public-methods
    def __init__(self, wing, simulation_solution):
        self.wing = wing
        self.solution = simulation_solution
        self.initial_altitude_m = float(simulation_solution.y[4][0])

    def _extract_impact_state(self):
        """Return the state at impact or the final simulated sample."""
        impact_detected = bool(
            self.solution.t_events and len(self.solution.t_events[0]) > 0
        )

        if impact_detected:
            return {
                "impact_detected": True,
                "time_s": float(self.solution.t_events[0][0]),
                "theta_rad": float(self.solution.y_events[0][0][0]),
                "theta_dot_rads": float(self.solution.y_events[0][0][1]),
                "phi_dot_rads": float(self.solution.y_events[0][0][2]),
                "v_vertical_ms": float(self.solution.y_events[0][0][3]),
                "altitude_m": float(self.solution.y_events[0][0][4]),
            }

        return {
            "impact_detected": False,
            "time_s": float(self.solution.t[-1]),
            "theta_rad": float(self.solution.y[0][-1]),
            "theta_dot_rads": float(self.solution.y[1][-1]),
            "phi_dot_rads": float(self.solution.y[2][-1]),
            "v_vertical_ms": float(self.solution.y[3][-1]),
            "altitude_m": float(self.solution.y[4][-1]),
        }

    def build_summary(self):
        """Compute impact, angular, and geometry metrics."""
        impact_state = self._extract_impact_state()
        impact_speed_ms = abs(impact_state["v_vertical_ms"])
        impact_energy_j = 0.5 * self.wing.mass * (impact_speed_ms**2)
        omega_rads = abs(impact_state["phi_dot_rads"])
        omega_rpm = omega_rads * 60.0 / (2.0 * np.pi)
        initial_potential_energy_j = self.wing.mass * 9.81 * self.initial_altitude_m
        dissipated_energy_j = initial_potential_energy_j - impact_energy_j
        energy_non_physical = dissipated_energy_j < -1e-6

        body_area_cm2 = self.wing.pocketqube_side_m * self.wing.pocketqube_side_m * 1e4
        wing_area_one_cm2 = self.wing.wing_area_one_m2 * 1e4
        wing_area_total_cm2 = self.wing.n_wings * wing_area_one_cm2

        return {
            "mass_kg": float(self.wing.mass),
            "geometry": {
                "dxf_file": str(self.wing.dxf_path),
                "n_wings": int(self.wing.n_wings),
                "radius_scale": float(self.wing.radius_scale),
                "root_radius_m": float(self.wing.r0),
                "tip_radius_m": float(self.wing.rf),
                "wing_area_one_cm2": float(wing_area_one_cm2),
                "wing_area_total_cm2": float(wing_area_total_cm2),
                "body_square_area_cm2": float(body_area_cm2),
                "total_frontal_area_cm2": float(body_area_cm2 + wing_area_total_cm2),
            },
            "impact": {
                "detected": impact_state["impact_detected"],
                "time_s": impact_state["time_s"],
                "altitude_m": impact_state["altitude_m"],
                "vertical_velocity_ms": impact_state["v_vertical_ms"],
                "speed_magnitude_ms": impact_speed_ms,
                "kinetic_energy_j": impact_energy_j,
            },
            "energy": {
                "initial_potential_j": float(initial_potential_energy_j),
                "final_kinetic_j": float(impact_energy_j),
                "dissipated_j": float(dissipated_energy_j),
                "non_physical": bool(energy_non_physical),
            },
            "angular": {
                "theta_deg": float(np.degrees(impact_state["theta_rad"])),
                "theta_dot_rads": impact_state["theta_dot_rads"],
                "phi_dot_rads": impact_state["phi_dot_rads"],
                "spin_rpm": float(omega_rpm),
            },
        }

    def print_summary(self, summary):
        """Print key report values in a compact engineering format."""
        print("\n" + "=" * 70)
        print("IMPACT REPORT")
        print("=" * 70)
        status = (
            "GROUND IMPACT DETECTED"
            if summary["impact"]["detected"]
            else "NO IMPACT EVENT"
        )
        print(f"DXF profile:              {summary['geometry']['dxf_file']}")
        print(f"Status: {status}")
        print(f"Impact time:              {summary['impact']['time_s']:.2f} s")
        print(f"Altitude at final state:  {summary['impact']['altitude_m']:.2f} m")
        print(
            f"Impact speed |v|:         {summary['impact']['speed_magnitude_ms']:.2f} m/s"
        )
        print(
            f"Vertical speed vz:        {summary['impact']['vertical_velocity_ms']:.2f} m/s"
        )
        print(
            f"Impact kinetic energy:    {summary['impact']['kinetic_energy_j']:.2f} J"
        )
        print(
            f"Angular speed phi_dot:    {summary['angular']['phi_dot_rads']:.2f} rad/s"
        )
        print(f"Angular speed spin:       {summary['angular']['spin_rpm']:.2f} rpm")
        print(f"Mean Reynolds number:     {self.wing.last_reynolds_mean:.0f}")
        print(
            f"Initial potential energy: {summary['energy']['initial_potential_j']:.2f} J"
        )
        print(f"Final kinetic energy:     {summary['energy']['final_kinetic_j']:.2f} J")
        print(f"Dissipated energy:        {summary['energy']['dissipated_j']:.2f} J")
        if summary["energy"]["non_physical"]:
            print("[WARNING] Non-physical energy balance detected.")
        print(
            f"Total frontal area:       {summary['geometry']['total_frontal_area_cm2']:.2f} cm²"
        )
        print("=" * 70)

    def save_report_files(self, summary, output_dir="extras/wing-analisys"):
        """Persist report in JSON and TXT files."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        json_path = out_dir / "samara_pq_impact_report.json"
        txt_path = out_dir / "samara_pq_impact_report.txt"

        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)

        with open(txt_path, "w", encoding="utf-8") as handle:
            status_text = (
                "GROUND IMPACT DETECTED"
                if summary["impact"]["detected"]
                else "NO IMPACT EVENT"
            )
            handle.write("=" * 70 + "\n")
            handle.write("IMPACT REPORT\n")
            handle.write("=" * 70 + "\n")
            handle.write(
                f"DXF profile:             {summary['geometry']['dxf_file']}\n"
            )
            handle.write(f"Status: {status_text}\n")
            handle.write(
                f"Impact time:             {summary['impact']['time_s']:.2f} s\n"
            )
            handle.write(
                f"Altitude at final state: {summary['impact']['altitude_m']:.2f} m\n"
            )
            handle.write(
                f"Impact speed |v|:        {summary['impact']['speed_magnitude_ms']:.2f} m/s\n"
            )
            handle.write(
                f"Vertical speed vz:       {summary['impact']['vertical_velocity_ms']:.2f} m/s\n"
            )
            handle.write(
                f"Impact kinetic energy:   {summary['impact']['kinetic_energy_j']:.2f} J\n"
            )
            handle.write(
                f"Angular speed phi_dot:   {summary['angular']['phi_dot_rads']:.2f} rad/s\n"
            )
            handle.write(
                f"Angular speed spin:      {summary['angular']['spin_rpm']:.2f} rpm\n"
            )
            handle.write(
                f"Mean Reynolds number:    {self.wing.last_reynolds_mean:.0f}\n"
            )
            handle.write(
                f"Initial potential energy: {summary['energy']['initial_potential_j']:.2f} J\n"
            )
            handle.write(
                f"Final kinetic energy:     {summary['energy']['final_kinetic_j']:.2f} J\n"
            )
            handle.write(
                f"Dissipated energy:        {summary['energy']['dissipated_j']:.2f} J\n"
            )
            if summary["energy"]["non_physical"]:
                handle.write("WARNING: Non-physical energy balance detected.\n")
            handle.write(
                "Total frontal area:      "
                f"{summary['geometry']['total_frontal_area_cm2']:.2f} cm²\n"
            )

        print(f"Saved JSON report: {json_path}")
        print(f"Saved TXT report:  {txt_path}")

    def save_trajectory_csv(self, output_dir="extras/wing-analisys"):
        """Exporta trajetória ponto a ponto no mesmo formato do CSV do satélite.

        Colunas: millis, t_s, theta_deg, theta_dot_rads, phi_dot_rads,
                 spin_rpm, v0_ms, altitude_m
        Permite comparação direta com dados de telemetria real (Teste 3 etc.).
        """
        import csv as _csv
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        csv_path = out_dir / "samara_pq_trajectory.csv"

        t    = self.solution.t
        th   = self.solution.y[0]
        thdot= self.solution.y[1]
        phdot= self.solution.y[2]
        v0   = self.solution.y[3]
        alt  = self.solution.y[4]

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = _csv.writer(f)
            writer.writerow([
                "millis", "t_s",
                "theta_deg", "theta_dot_rads",
                "phi_dot_rads", "spin_rpm",
                "v0_ms", "altitude_m",
            ])
            for i, ti in enumerate(t):
                writer.writerow([
                    f"{ti * 1000:.0f}",           # millis
                    f"{ti:.4f}",                   # t_s
                    f"{np.degrees(th[i]):.4f}",   # theta_deg
                    f"{thdot[i]:.6f}",             # theta_dot_rads
                    f"{phdot[i]:.6f}",             # phi_dot_rads
                    f"{phdot[i] * 60 / (2*np.pi):.3f}",  # spin_rpm
                    f"{v0[i]:.4f}",                # v0_ms
                    f"{alt[i]:.4f}",               # altitude_m
                ])
        print(f"Saved trajectory CSV: {csv_path}")


def _parse_args():
    """Parse optional CLI arguments that override CONFIG values."""
    parser = argparse.ArgumentParser(
        description="SRAB — Samara PQ Simulation Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Geometria
    parser.add_argument("--dxf", type=Path, metavar="FILE",
                        help="Arquivo DXF da asa (ex: Asa2.DXF)")
    parser.add_argument("--n-wings", type=int, metavar="N",
                        help="Número de asas simétricas")
    # Massa
    parser.add_argument("--mass", type=float, metavar="KG",
                        help="Massa total do sistema [kg]")
    # Condições iniciais
    parser.add_argument("--altitude", type=float, metavar="M",
                        help="Altitude de liberação [m]")
    parser.add_argument("--theta-deg", type=float, metavar="DEG",
                        help="Ângulo de conicidade inicial [graus]")
    parser.add_argument("--phi-dot", type=float, metavar="RAD_S",
                        help="Spin inicial [rad/s]")
    parser.add_argument("--v0", type=float, metavar="M_S",
                        help="Velocidade vertical inicial [m/s]")
    # Aerodinâmica
    parser.add_argument("--cd0", type=float, metavar="COEF",
                        help="Coeficiente de arrasto basal (LEV)")
    parser.add_argument("--f-factor", type=float, metavar="F",
                        help="Fração de inércia de massa nas asas")
    parser.add_argument("--beta-deg", type=float, metavar="DEG",
                        help="Ângulo de passo geométrico β [graus]")
    parser.add_argument("--rho", type=float, metavar="KG_M3",
                        help="Densidade do ar [kg/m³]")
    # Integração
    parser.add_argument("--t-max", type=float, metavar="S",
                        help="Tempo máximo de simulação [s]")
    parser.add_argument("--max-step", type=float, metavar="S",
                        help="Passo máximo do integrador RK45 [s]")
    # Saída
    parser.add_argument("--output", type=Path, metavar="DIR",
                        help="Diretório de saída dos relatórios e figuras")
    
    # --- NOVOS ARGUMENTOS DE OTIMIZAÇÃO ---
    parser.add_argument("--optimize", action="store_true",
                        help="Ativa o otimizador numérico para encontrar o raio aerodinâmico ideal")
    parser.add_argument("--target-vf", type=float, metavar="M_S", default=25.0,
                        help="Velocidade vertical alvo (módulo) para o impacto [m/s] (ex: 30)")
                        
    return parser.parse_args()


def _build_config_from_args(args):
    """Merge CONFIG defaults with CLI arguments (CLI takes precedence)."""
    cfg = dict(CONFIG)
    overrides = {
        "dxf_path":   args.dxf,
        "n_wings":    args.n_wings,
        "mass_kg":    args.mass,
        "altitude_m": args.altitude,
        "theta_deg":  args.theta_deg,
        "phi_dot_0":  args.phi_dot,
        "v0_0":       args.v0,
        "cd0":        args.cd0,
        "f_factor":   args.f_factor,
        "beta_deg":   args.beta_deg,
        "rho":        args.rho,
        "t_max":      args.t_max,
        "max_step":   args.max_step,
        "output_dir": args.output,
        "optimize":   args.optimize,   # Adicionado
        "target_vf":  args.target_vf,  # Adicionado
    }
    for key, val in overrides.items():
        if val is not None:
            cfg[key] = val
            
    # Valores fallback caso não estejam no dicionário original CONFIG
    if "optimize" not in cfg:
        cfg["optimize"] = False
    if "target_vf" not in cfg:
        cfg["target_vf"] = 25.0
        
    return cfg


def main():
    """Execute simulation and visualization pipeline."""
    args = _parse_args()
    cfg = _build_config_from_args(args)

    print("==========================================================")
    print(" LASC POCKETQUBE 1P — SRAB SIMULATION PIPELINE")
    print("==========================================================")
    print(f"  DXF:          {cfg['dxf_path']}")
    print(f"  Asas:         {cfg['n_wings']}")
    print(f"  Massa:        {cfg['mass_kg']*1000:.0f} g")
    print(f"  Altitude:     {cfg['altitude_m']:.0f} m")
    print(f"  Spin inicial: {cfg['phi_dot_0']:.2f} rad/s")
    print(f"  θ inicial:    {cfg['theta_deg']:.1f}°")
    print(f"  v₀ inicial:   {cfg['v0_0']:.1f} m/s")
    print(f"  β (passo):    {cfg['beta_deg']:.1f}°")
    if cfg.get("optimize"):
        print(f"  [OTIMIZADOR]  Ativo -> Alvo v_impacto: -{abs(cfg['target_vf'])} m/s")
    print("==========================================================\n")

    initial_conditions = [
        np.radians(cfg["theta_deg"]),
        cfg["theta_dot_0"],
        cfg["phi_dot_0"],
        cfg["v0_0"],
        cfg["altitude_m"],
    ]

    wing = PocketQubeSamaraWing(
        dxf_path=cfg["dxf_path"],
        n_wings=cfg["n_wings"],
        mass=cfg["mass_kg"],
        f_factor=cfg["f_factor"],
        cd0=cfg["cd0"],
        rho=cfg["rho"],
        beta_deg=cfg["beta_deg"],
    )

    solver = PocketQubeFlightDynamics(wing)

    # --- BLOCO DE OTIMIZAÇÃO AQUI ---
    if cfg.get("optimize"):
        # Garante que o target seja negativo para a velocidade de descida
        target_impact_vf = -abs(cfg["target_vf"])
        optimizer = PocketQubeSamaraOptimizer(solver, target_vf=target_impact_vf)
        
        radius_opt = optimizer.optimize_radius_for_impact(
            n_wings=cfg["n_wings"],
            target_impact_vf=target_impact_vf,
            sim_t_span=(0.0, cfg["t_max"]),
            sim_max_step=cfg["max_step"],
        )
        
        if radius_opt is None:
            print("\n[AVISO] A otimização numércia não convergiu. Mantendo o raio do DXF.")
        else:
            print(f"\n[INFO] Simulando voo final com raio otimizado: {radius_opt*100:.2f} cm")
    # --------------------------------

    solution = solver.simulate_drop(
        initial_conditions=initial_conditions,
        t_span=(0.0, cfg["t_max"]),
        max_step=cfg["max_step"],
    )

    reporter = PocketQubeMissionReporter(wing, solution)
    summary = reporter.build_summary()
    reporter.print_summary(summary)
    reporter.save_report_files(summary, output_dir=str(cfg["output_dir"]))
    reporter.save_trajectory_csv(output_dir=str(cfg["output_dir"]))

    visualizer = PocketQubeLRRVisualizer(solution, output_dir=str(cfg["output_dir"]))
    theta_eq, spin_eq = visualizer.generate_lrr_report(beta_deg=cfg["beta_deg"])
    plot_wing_geometry_views(wing, theta_eq_deg=theta_eq, output_dir=str(cfg["output_dir"]))

if __name__ == "__main__":
    main()
