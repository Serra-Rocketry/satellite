# -*- coding: utf-8 -*-
"""SRAB Recovery — Acoplamento sequencial RocketPy ascente + SRAB descida.

Uso básico:
    from rocketpy_samara.srab_recovery import SRABRecovery, SRABSolution
    from samara_pq_simulation import PocketQubeSamaraWing

    wing = PocketQubeSamaraWing(dxf_path="Asa3.DXF", mass=0.200, ...)
    recovery = SRABRecovery(wing, env=env)

    # A partir de um Flight do RocketPy (recomendado):
    srab_sol = recovery.simulate_from_flight(flight, theta_deg=20)

    # Ou standalone (sem RocketPy):
    srab_sol = recovery.simulate(theta_deg=0, altitude_m=1000, ...)
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Garante que src/ esteja no path para import absoluto de samara_pq_simulation
_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from samara_pq_simulation import (  # noqa: E402
    PocketQubeSamaraWing,
    PocketQubeFlightDynamics,
    PocketQubeSamaraOptimizer,
    CONFIG as SRAB_CONFIG,
)


# =============================================================================
# EnvironmentAwareFlightDynamics — rho(z) from RocketPy Environment
# =============================================================================


class EnvironmentAwareFlightDynamics(PocketQubeFlightDynamics):
    """Extends PocketQubeFlightDynamics to use altitude-dependent air density
    from a RocketPy Environment object.

    Updates ``wing.rho`` before every ODE derivative evaluation by querying
    ``env.density.get_value_opt(z)`` at the current altitude.
    No modifications to the original simulation code are required.
    """

    def __init__(self, wing: PocketQubeSamaraWing, env):
        super().__init__(wing)
        self.env = env

    def _state_derivatives(self, t: float, state: list) -> list:
        z = max(state[4], 0.0)
        self.wing.rho = self.env.density.get_value_opt(z)
        return super()._state_derivatives(t, state)


# =============================================================================
# SRABSolution — structured simulation result
# =============================================================================


@dataclass
class SRABSolution:
    """Results from a SRAB descent simulation, with optional horizontal offset
    from a RocketPy apogee position.

    Fields
    ------
    t : (N,) ndarray
        Time since apogee [s].
    theta : (N,) ndarray
        Conicity angle history [rad].
    theta_dot : (N,) ndarray
        Pitch rate history [rad/s].
    phi_dot : (N,) ndarray
        Spin rate history [rad/s].
    v0 : (N,) ndarray
        Vertical velocity (positive up) [m/s].
    altitude : (N,) ndarray
        Altitude AGL [m].
    x : (N,) ndarray
        East position (x0 + wind drift) [m].
    y : (N,) ndarray
        North position (y0 + wind drift) [m].
    x0 : float
        East offset from apogeu [m].
    y0 : float
        North offset from apogeu [m].
    t_impact : float
        Descent duration until ground impact [s].
    v_impact : float
        Vertical speed magnitude at impact [m/s].
    spin_impact_rpm : float
        Spin rate at impact [RPM].
    theta_eq : float
        Equilibrium conicity angle [deg].
    """

    t: np.ndarray
    theta: np.ndarray
    theta_dot: np.ndarray
    phi_dot: np.ndarray
    v0: np.ndarray
    altitude: np.ndarray
    x: np.ndarray
    y: np.ndarray
    x0: float
    y0: float

    t_impact: float
    v_impact: float
    spin_impact_rpm: float
    theta_eq: float

    @property
    def x_impact(self) -> float:
        """East coordinate of ground impact [m]."""
        return float(self.x[-1])

    @property
    def y_impact(self) -> float:
        """North coordinate of ground impact [m]."""
        return float(self.y[-1])

    @classmethod
    def from_ode_solution(
        cls, sol, x0: float = 0.0, y0: float = 0.0, env=None
    ) -> "SRABSolution":
        """Build from a ``scipy.integrate.OdeSolution`` (output of
        ``PocketQubeFlightDynamics.simulate_drop``).

        Parameters
        ----------
        sol : OdeResult
            Result from ``simulate_drop`` (has ``.t``, ``.y``, ``.t_events``).
        x0, y0 : float
            Horizontal offset of the apogee [m].
        env : Environment, optional
            RocketPy Environment for wind-driven horizontal drift integration.
            If ``None``, the horizontal trajectory stays at (x0, y0).
        """
        t = sol.t
        theta, theta_dot, phi_dot, v0, alt = sol.y

        # Impact detection
        if sol.t_events and sol.t_events[0].size > 0:
            t_impact = float(sol.t_events[0][0])
            i_state = sol.y_events[0][0]
        else:
            t_impact = float(t[-1])
            i_state = [s[-1] for s in sol.y]

        # Equilibrium estimate (last 20 % of trajectory)
        n = max(1, len(t) // 5)
        theta_eq = float(np.degrees(np.median(theta[-n:])))

        # Horizontal trajectory with wind drift
        x, y = cls._wind_drift(t, alt, env, x0, y0)

        return cls(
            t=t,
            theta=theta,
            theta_dot=theta_dot,
            phi_dot=phi_dot,
            v0=v0,
            altitude=alt,
            x=x,
            y=y,
            x0=x0,
            y0=y0,
            t_impact=t_impact,
            v_impact=abs(i_state[3]),
            spin_impact_rpm=abs(i_state[2]) * 60.0 / (2.0 * np.pi),
            theta_eq=theta_eq,
        )

    @staticmethod
    def _wind_drift(t, alt, env, x0, y0):
        """Integrate horizontal wind velocity along the descent trajectory.

        If ``env`` is ``None``, returns constant (x0, y0).
        """
        if env is None:
            return np.full_like(t, x0), np.full_like(t, y0)

        x, y = [x0], [y0]
        for i in range(1, len(t)):
            z_mid = max((alt[i] + alt[i - 1]) / 2.0, 0.0)
            dt = t[i] - t[i - 1]
            wx = env.wind_velocity_x.get_value_opt(z_mid)
            wy = env.wind_velocity_y.get_value_opt(z_mid)
            x.append(x[-1] + wx * dt)
            y.append(y[-1] + wy * dt)
        return np.array(x), np.array(y)


# =============================================================================
# SRABRecovery — wrapper connecting RocketPy Flight to SRAB descent
# =============================================================================


class SRABRecovery:
    """End-to-end wrapper that connects a RocketPy ``Flight`` (ascent) to
    the SRAB autorotation descent simulation.

    Usage
    -----
    After a RocketPy flight simulation::

        wing = PocketQubeSamaraWing(dxf_path="Asa3.DXF", mass=0.200, ...)
        recovery = SRABRecovery(wing, env=flight.env, theta_deg=20)

        # Full pipeline: extract apogee → run SRAB → collect results
        srab_sol = recovery.simulate_from_flight(flight)

        # Standalone (no RocketPy Flight):
        srab_sol = recovery.simulate(theta_deg=0, altitude_m=1000, v0_0=0.0)
    """

    def __init__(self, wing: PocketQubeSamaraWing = None, env=None, **kwargs):
        self.wing = wing
        self.env = env

        # Merge defaults from SRAB_CONFIG, override with kwargs
        self.kwargs = dict(SRAB_CONFIG)
        self.kwargs.update(kwargs)

    # ------------------------------------------------------------------
    # Primary API — from a RocketPy Flight object
    # ------------------------------------------------------------------

    def simulate_from_flight(self, flight, **overrides) -> SRABSolution:
        """Run SRAB descent starting from a RocketPy Flight's apogee.

        Parameters
        ----------
        flight : rocketpy.Flight
            Completed RocketPy flight (ascent) simulation. The apogee state
            (altitude, vz, x, y) is used as SRAB initial conditions.
        **overrides
            Override any SRAB config parameter (theta_deg, cd0, etc.).

        Returns
        -------
        SRABSolution
            Full descent solution with horizontal offset from apogee.
        """
        kw = {**self.kwargs, **overrides}
        t_apo = flight.apogee_time

        ic = [
            np.radians(kw["theta_deg"]),
            kw.get("theta_dot_0", 0.0),
            kw.get("phi_dot_0", 0.1),
            float(flight.vz(t_apo)),  # real vz at apogeu
            float(flight.apogee),  # real altitude at apogeu
        ]

        env = self.env or getattr(flight, "env", None)
        x0 = float(flight.x(t_apo))
        y0 = float(flight.y(t_apo))

        return self._run_simulation(ic, env, x0, y0, kw)

    # ------------------------------------------------------------------
    # Standalone API — direct initial conditions (no Flight required)
    # ------------------------------------------------------------------

    def simulate(
        self,
        initial_conditions: list = None,
        t_span: tuple = None,
        max_step: float = None,
        x0: float = 0.0,
        y0: float = 0.0,
        **overrides,
    ) -> SRABSolution:
        """Run SRAB descent with explicit initial conditions.

        Parameters
        ----------
        initial_conditions : list, optional
            ``[theta, theta_dot, phi_dot, v0, z_alt]``.
            If ``None``, built from ``**overrides`` or ``self.kwargs``.
        t_span : tuple, optional
            ``(t_start, t_end)``. Defaults to ``(0, kwargs['t_max'])``.
        max_step : float, optional
            Max integrator step. Defaults to ``kwargs['max_step']``.
        x0, y0 : float
            Horizontal offset [m]. Default 0.
        **overrides
            Override any SRAB config parameter.

        Returns
        -------
        SRABSolution
        """
        kw = {**self.kwargs, **overrides}

        if initial_conditions is None:
            initial_conditions = [
                np.radians(kw["theta_deg"]),
                kw.get("theta_dot_0", 0.0),
                kw.get("phi_dot_0", 0.1),
                kw["v0_0"],
                kw["altitude_m"],
            ]

        t_span = t_span or (0.0, kw["t_max"])
        max_step = max_step or kw["max_step"]
        env = self.env

        return self._run_simulation(
            initial_conditions, env, x0, y0, kw, t_span=t_span, max_step=max_step
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_simulation(
        self, ic, env, x0, y0, kw, t_span=None, max_step=None
    ) -> SRABSolution:
        """Common simulation path shared by ``simulate`` and
        ``simulate_from_flight``.
        """
        t_span = t_span or (0.0, kw["t_max"])
        max_step = max_step or kw["max_step"]

        if env is not None:
            dyn = EnvironmentAwareFlightDynamics(self.wing, env)
        else:
            dyn = PocketQubeFlightDynamics(self.wing)

        if kw.get("optimize"):
            target_vf = -abs(kw.get("target_vf", 20.0))
            optimizer = PocketQubeSamaraOptimizer(dyn, target_vf=target_vf)
            radius_opt = optimizer.optimize_radius_for_impact(
                n_wings=kw["n_wings"],
                target_impact_vf=target_vf,
                sim_t_span=t_span,
                sim_max_step=max_step,
            )
            if radius_opt is not None:
                print(f"  Raio otimizado: {radius_opt * 100:.2f} cm")
                # Wing already updated in-place by optimizer

        sol = dyn.simulate_drop(
            initial_conditions=ic,
            t_span=t_span,
            max_step=max_step,
        )

        return SRABSolution.from_ode_solution(sol, x0, y0, env)
