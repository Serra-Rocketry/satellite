#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo SRABMonteCarlo — validação com variação de massa, beta e cd0.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from samara_pq_simulation import PocketQubeSamaraWing  # noqa: E402
from rocketpy_samara.srab_recovery import SRABRecovery  # noqa: E402
from rocketpy_samara.monte_carlo import SRABMonteCarlo  # noqa: E402

# =============================================================================
# Parâmetros base
# =============================================================================
DXF = _SRC.parent / "geometry" / "Asa3.DXF"

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

    mc = SRABMonteCarlo(recovery, n=50, seed=42)

    # Parâmetros estocásticos
    mc.add_param("mass_kg", "normal", (0.200, 0.010))  # ±5%
    mc.add_param("beta_deg", "normal", (8.0, 0.5))  # ±0.5°
    mc.add_param("cd0", "normal", (1.0, 0.15))  # ±15%
    mc.add_param("n_wings", "discrete", (2, 4))  # topologia

    print("=" * 65)
    print("  SRABMonteCarlo — Demo")
    print("=" * 65)
    print(f"  Iterações:      {mc.n}")
    print(f"  Parâmetros:     {[p.name for p in mc._params]}")
    print(f"  DXF:            {DXF}")
    print("=" * 65)

    mc.run(verbose=True)
    mc.print_summary()
    mc.export_csv(str(_SRC.parent.parent / "results" / "mc_srab_demo.csv"))
