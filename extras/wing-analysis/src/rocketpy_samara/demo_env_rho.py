#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa SRABRecovery com RocketPy Environment (rho variável com altitude).
Compara resultados com rho constante (1.225).
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from samara_pq_simulation import PocketQubeSamaraWing  # noqa: E402
from rocketpy_samara.srab_recovery import SRABRecovery  # noqa: E402

# =============================================================================
# Parâmetros (sem otimização para comparação direta)
# =============================================================================
DXF = _SRC.parent / "geometry" / "Asa3.DXF"
H = 1000.0  # altitude de liberação [m]

params = dict(
    dxf_path=str(DXF),
    n_wings=2,
    mass_kg=0.200,
    altitude_m=H,
    theta_deg=20.0,
    theta_dot_0=0.0,
    phi_dot_0=0.1,
    v0_0=0.0,
    beta_deg=8.0,
    cd0=1.0,
    f_factor=0.3,
    rho=1.225,
    t_max=300.0,
    max_step=0.2,
    optimize=False,
)


def run_comparison():
    """Compara simulação com rho constante vs rho(z) do Environment."""
    # --- 1. Rho constante ---
    wing_const = PocketQubeSamaraWing(
        dxf_path=params["dxf_path"],
        n_wings=params["n_wings"],
        mass=params["mass_kg"],
        f_factor=params["f_factor"],
        cd0=params["cd0"],
        rho=params["rho"],
        beta_deg=params["beta_deg"],
    )
    rec_const = SRABRecovery(wing_const, env=None, **params)
    sol_const = rec_const.simulate()

    print("\n--- Rho CONSTANTE (1.225) ---")
    print(f"  Duração:    {sol_const.t_impact:.2f} s")
    print(f"  v_impacto:  {sol_const.v_impact:.2f} m/s")
    print(f"  Spin:       {sol_const.spin_impact_rpm:.1f} RPM")
    print(f"  Theta_eq:   {sol_const.theta_eq:.1f}°")

    # --- 2. Rho(z) do RocketPy Environment ---
    try:
        from rocketpy import Environment

        env = Environment(latitude=-23.5, longitude=-46.6, elevation=600)
        env.set_atmospheric_model(type="standard_atmosphere")

        # Mostra perfil de densidade
        rho_0 = env.density.get_value_opt(0)
        rho_H = env.density.get_value_opt(H)
        print(f"\n  Densidade ao nível do mar: {rho_0:.4f} kg/m³")
        print(f"  Densidade em {H}m:           {rho_H:.4f} kg/m³")
        print(f"  Diferença:                 {(1 - rho_H / rho_0) * 100:.1f}%")

        wing_var = PocketQubeSamaraWing(
            dxf_path=params["dxf_path"],
            n_wings=params["n_wings"],
            mass=params["mass_kg"],
            f_factor=params["f_factor"],
            cd0=params["cd0"],
            rho=params["rho"],  # valor inicial (será sobrescrito)
            beta_deg=params["beta_deg"],
        )
        rec_var = SRABRecovery(wing_var, env=env, **params)
        sol_var = rec_var.simulate()

        print("\n--- Rho(z) do StandardAtmosphere ---")
        print(f"  Duração:    {sol_var.t_impact:.2f} s")
        print(f"  v_impacto:  {sol_var.v_impact:.2f} m/s")
        print(f"  Spin:       {sol_var.spin_impact_rpm:.1f} RPM")
        print(f"  Theta_eq:   {sol_var.theta_eq:.1f}°")

        print("\n--- DIFERENÇA (variável - constante) ---")
        dt = sol_var.t_impact - sol_const.t_impact
        dv = sol_var.v_impact - sol_const.v_impact
        print(f"  Δt:       {dt:+.2f} s  ({dt / sol_const.t_impact * 100:+.1f}%)")
        print(f"  Δv:       {dv:+.2f} m/s  ({dv / sol_const.v_impact * 100:+.1f}%)")

    except ImportError as e:
        print(f"\n  [AVISO] RocketPy não disponível: {e}")
        print("  Instale com: pip install rocketpy")
    except Exception as e:
        print(f"\n  [ERRO] {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("  Comparação: rho constante vs rho(z) Environment")
    print("=" * 60)
    run_comparison()
    print("=" * 60)
