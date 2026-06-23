#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo plotting — gera LRR dashboard + 3D trajectory a partir do SRABSolution.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from samara_pq_simulation import PocketQubeSamaraWing  # noqa: E402
from rocketpy_samara.srab_recovery import SRABRecovery  # noqa: E402
from rocketpy_samara.plotting import (  # noqa: E402
    plot_lrr_dashboard,
    _plot_srab_only,
)

DXF = _SRC.parent / "geometry" / "Asa3.DXF"
OUT = _SRC.parent.parent / "results"

params = dict(
    dxf_path=str(DXF),
    n_wings=2,
    mass_kg=0.200,
    altitude_m=1000.0,
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

if __name__ == "__main__":
    wing = PocketQubeSamaraWing(
        dxf_path=params["dxf_path"],
        n_wings=params["n_wings"],
        mass=params["mass_kg"],
        f_factor=params["f_factor"],
        cd0=params["cd0"],
        rho=params["rho"],
        beta_deg=params["beta_deg"],
    )

    recovery = SRABRecovery(wing, env=None, **params)
    sol = recovery.simulate()

    OUT.mkdir(parents=True, exist_ok=True)

    # LRR dashboard
    plot_lrr_dashboard(sol, filename=str(OUT / "srab_lrr_demo.png"))
    print(f"  LRR: {OUT / 'srab_lrr_demo.png'}")

    # 3D standalone
    _plot_srab_only(sol, filename=str(OUT / "srab_3d_demo.png"))
    print(f"  3D:  {OUT / 'srab_3d_demo.png'}")
