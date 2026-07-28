#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo SRABRecovery — validação com parâmetros do usuário.

Simula descida SRAB standalone (sem RocketPy Flight) e exibe resultados.
Roda com os parâmetros exatos do CLI de referência.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from samara_pq_simulation import PocketQubeSamaraWing  # noqa: E402
from rocketpy_samara.srab_recovery import SRABRecovery  # noqa: E402

# =============================================================================
# Parâmetros do usuário
# =============================================================================
DXF = _SRC.parent / "geometry" / "Asa3.DXF"

params = dict(
    dxf_path=str(DXF),
    n_wings=2,
    mass_kg=0.200,
    altitude_m=1000.0,
    theta_deg=0.0,
    theta_dot_0=0.0,
    phi_dot_0=0.0,
    v0_0=0.0,
    beta_deg=3.0,
    cd0=1.0,
    f_factor=0.3,
    rho=1.225,
    t_max=600.0,
    max_step=0.2,
    optimize=True,
    target_vf=20.0,
    safety_factor=1.5,
)

# =============================================================================
# Execução
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("  SRABRecovery — Demo")
    print("=" * 70)
    print(f"  DXF:       {DXF}")
    print(f"  n_wings:   {params['n_wings']}")
    print(f"  Massa:     {params['mass_kg'] * 1000:.0f} g")
    print(f"  Altitude:  {params['altitude_m']:.0f} m")
    print(f"  Beta:      {params['beta_deg']:.1f}°")
    print(
        f"  Otimizar:  sim (target_vf={params['target_vf']} m/s, "
        f"safety={params['safety_factor']})"
    )
    print("=" * 70)

    # Cria asa
    wing = PocketQubeSamaraWing(
        dxf_path=params["dxf_path"],
        n_wings=params["n_wings"],
        mass=params["mass_kg"],
        f_factor=params["f_factor"],
        cd0=params["cd0"],
        rho=params["rho"],
        beta_deg=params["beta_deg"],
    )

    # Aplica safety factor ao target_vf e corrige o dict
    params["target_vf"] = params["target_vf"] / params["safety_factor"]

    # SRABRecovery sem Environment (rho constante)
    recovery = SRABRecovery(
        wing,
        env=None,
        **params,
    )

    # Simula standalone (usa kwargs já configurados no SRABRecovery)
    sol = recovery.simulate()

    # =========================================================================
    # Relatório
    # =========================================================================
    print("\n" + "=" * 70)
    print("  RESULTADOS DA DESCIDA SRAB")
    print("=" * 70)
    print(f"  Duração:              {sol.t_impact:.2f} s")
    print(f"  v_impacto:            {sol.v_impact:.2f} m/s")
    print(f"  Spin impacto:         {sol.spin_impact_rpm:.1f} RPM")
    print(f"  θ equilíbrio:         {sol.theta_eq:.1f}°")
    print(f"  x_impacto:            {sol.x_impact:.2f} m")
    print(f"  y_impacto:            {sol.y_impact:.2f} m")
    print(f"  Amostras trajetória:  {len(sol.t)}")
    print(f"  Altitude inicial:     {sol.altitude[0]:.1f} m")
    print(f"  Altitude final:       {sol.altitude[-1]:.1f} m")
    print(f"  v0 inicial:           {sol.v0[0]:.2f} m/s")
    print(f"  v0 final:             {sol.v0[-1]:.2f} m/s")
    print(f"  RPM final:            {sol.spin_impact_rpm:.1f}")
    print("=" * 70)

    # Summary JSON-like
    print("\n  JSON:")
    print("  {")
    print(f'    "t_impact": {sol.t_impact:.3f},')
    print(f'    "v_impact": {sol.v_impact:.3f},')
    print(f'    "spin_rpm": {sol.spin_impact_rpm:.1f},')
    print(f'    "theta_eq_deg": {sol.theta_eq:.2f},')
    print(f'    "x_impact": {sol.x_impact:.2f},')
    print(f'    "y_impact": {sol.y_impact:.2f}')
    print("  }")
    print("=" * 70)
