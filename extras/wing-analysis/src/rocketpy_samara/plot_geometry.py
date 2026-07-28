#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as três vistas geométricas do satélite com o raio de asa otimizado."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from samara_pq_simulation import (
    PocketQubeSamaraWing,
    PocketQubeFlightDynamics,
    plot_wing_geometry_views,
)
import numpy as np

# Mesmo raio otimizado do pipeline: 7.92 cm
RAIO_OTIMIZADO_M = 0.0792

DXF = _SRC.parent / "geometry" / "Asa3.DXF"

wing = PocketQubeSamaraWing(
    dxf_path=str(DXF),
    n_wings=2,
    mass=0.200,
    radius=RAIO_OTIMIZADO_M,
    f_factor=0.3,
    cd0=1.0,
    rho=1.225,
    beta_deg=5.0,
)

# Simula uma descida para extrair theta_eq
dyn = PocketQubeFlightDynamics(wing)
ic = [np.radians(0.0), 0.0, 0.0, 0.0, 1000.0]
sol = dyn.simulate_drop(initial_conditions=ic, t_span=(0, 600), max_step=0.2)

n = max(1, len(sol.t) // 5)
theta_eq = float(np.degrees(np.median(sol.y[0][-n:])))

OUT = _SRC.parent.parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

plot_wing_geometry_views(wing, theta_eq_deg=theta_eq, output_dir=str(OUT))

print(f"  Raio: {wing.radius * 100:.2f} cm")
print(f"  θ_eq: {theta_eq:.1f}°")
print(f"  r0: {wing.r0 * 1e3:.1f} mm, rf: {wing.rf * 1e3:.1f} mm")
print(f"  Área total asas: {wing.n_wings * wing.wing_area_one_m2 * 1e4:.1f} cm²")
