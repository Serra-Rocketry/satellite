# -*- coding: utf-8 -*-
"""rocketpy_samara — Integração SRAB × RocketPy para a Missão Helike #213.

Módulos
-------
srab_recovery :
    SRABSolution, EnvironmentAwareFlightDynamics, SRABRecovery
monte_carlo :
    SRABMonteCarlo, StochParam
plotting :
    plot_ascent_descent_3d, plot_dispersion, plot_lrr_dashboard,
    plot_trajectory_map
"""

__all__ = [
    "SRABSolution",
    "SRABRecovery",
    "EnvironmentAwareFlightDynamics",
    "SRABMonteCarlo",
    "StochParam",
    "plot_ascent_descent_3d",
    "plot_dispersion",
]

from .srab_recovery import SRABSolution, SRABRecovery, EnvironmentAwareFlightDynamics

try:
    from .monte_carlo import SRABMonteCarlo, StochParam  # noqa: F401
except ImportError:
    pass

try:
    from .plotting import (  # noqa: F401
        plot_ascent_descent_3d,
        plot_dispersion,
        plot_lrr_dashboard,
        plot_trajectory_map,
    )
except ImportError:
    pass
