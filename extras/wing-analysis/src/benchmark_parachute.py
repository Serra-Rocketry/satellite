#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparativo SRAB vs Paraquedas — PocketQube 1P (200 g)
Simula descida com paraquedas usando modelo de balanco de forcas 1D.
"""

import sys

sys.path.insert(0, "src")

import numpy as np
from scipy.integrate import solve_ivp
from samara_pq_simulation import (
    PocketQubeSamaraWing,
    PocketQubeFlightDynamics,
    PocketQubeMissionReporter,
)

# =============================================================================
# Configuracoes comuns
# =============================================================================
MASS_KG = 0.200
ALTITUDE_M = 1000.0
G = 9.81

# =============================================================================
# 1. SRAB (Samara PQ)
# =============================================================================
print("=" * 65)
print("  SRAB — Simulacao Samara PQ")
print("=" * 65)

DXF = "geometry/Asa3.DXF"
wing = PocketQubeSamaraWing(
    dxf_path=DXF,
    n_wings=4,
    mass=MASS_KG,
    f_factor=0.3,
    cd0=1.0,
    rho=1.225,
    beta_deg=3.0,
)
solver = PocketQubeFlightDynamics(wing)
sol_srab = solver.simulate_drop(
    initial_conditions=[np.radians(0), 0.0, 0.1, 0.0, ALTITUDE_M],
    t_span=(0, 600.0),
    max_step=0.2,
)
reporter_srab = PocketQubeMissionReporter(wing, sol_srab)
summary_srab = reporter_srab.build_summary()

v_srab = summary_srab["impact"]["speed_magnitude_ms"]
t_srab = summary_srab["impact"]["time_s"]
ke_srab = summary_srab["impact"]["kinetic_energy_j"]

print(f"  v_impacto:  {v_srab:.2f} m/s")
print(f"  t_descida:  {t_srab:.2f} s")
print(f"  KE_impacto: {ke_srab:.2f} J")

# =============================================================================
# 2. Paraquedas (modelo 1D de balanco de forcas)
# =============================================================================
print()
print("=" * 65)
print("  PARAQUEDAS — Modelo 1D de balanco de forcas")
print("=" * 65)


# Densidade do ar (ISA simplificada)
def rho_air(z):
    """Densidade do ar [kg/m³] para altitude z [m] (ISA simplificada)."""
    if z > 11000:
        return 0.3639
    return 1.225 * (1 - 2.25577e-5 * z) ** 5.25588


# Parametros do paraquedas
# Paraquedas tipico para PQ 1P: 200 mm de diametro, CD ~1.5 (flat circular)
d_para = 0.200  # diametro [m]
area_para = np.pi * (d_para / 2) ** 2  # area [m²]
cd_para = 1.5  # coeficiente de arrasto (flat circular)
total_mass = MASS_KG

# Equacao de movimento para queda com paraquedas:
# m * dv/dt = m*g - 0.5 * rho * v^2 * CD * A
# (gravidade para baixo, arrasto para cima)
# v positivo = descendo


def parachute_dynamics(t, state):
    """Equacao de movimento: dz/dt = -z (descendo), dv/dt = g - drag/m"""
    z, v = state
    if z <= 0:
        return [0, 0]
    rho = rho_air(z)
    # Arrasto: oposto ao movimento (para cima quando descendo)
    drag = 0.5 * rho * v * abs(v) * cd_para * area_para
    dvdt = G - drag / total_mass
    dzdt = -v  # z diminui quando v > 0 (descendo)
    return [dzdt, dvdt]


# Evento: impacto no solo (z = 0)
def hit_ground(t, state):
    return state[0]


hit_ground.terminal = True
hit_ground.direction = -1

# Simulacao: liberado do repouso na altitude de 1000 m
sol_para = solve_ivp(
    parachute_dynamics,
    t_span=(0, 600),
    y0=[ALTITUDE_M, 0.0],  # z=1000m, v=0
    method="RK45",
    events=hit_ground,
    max_step=0.5,
    rtol=1e-8,
    atol=1e-10,
)

if sol_para.t_events[0].size > 0:
    t_impact_para = sol_para.t_events[0][0]
    v_impact_para = sol_para.y_events[0][0][1]
else:
    t_impact_para = sol_para.t[-1]
    v_impact_para = sol_para.y[1][-1]

ke_impact_para = 0.5 * total_mass * v_impact_para**2

print(f"  D_para:     {d_para*1000:.0f} mm")
print(f"  CD_para:    {cd_para}")
print(f"  A_para:     {area_para*1e4:.1f} cm²")
print(f"  v_impacto:  {v_impact_para:.2f} m/s")
print(f"  t_descida:  {t_impact_para:.2f} s")
print(f"  KE_impacto: {ke_impact_para:.2f} J")

# Velocidade terminal teorica
v_terminal = np.sqrt(2 * total_mass * G / (cd_para * area_para * 1.225))
print(f"  v_terminal (teorica, rho=1.225): {v_terminal:.2f} m/s")

# =============================================================================
# 3. Comparativo
# =============================================================================
print()
print("=" * 65)
print("  COMPARATIVO — SRAB vs Paraquedas")
print("=" * 65)
print(f"  {'Parametro':<25} {'SRAB':>12} {'Paraquedas':>12} {'Diferenca':>12}")
print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*12}")
print(
    f"  {'v_impacto [m/s]':<25} {v_srab:>12.2f} {v_impact_para:>12.2f} {v_srab - v_impact_para:>+12.2f}"
)
print(
    f"  {'t_descida [s]':<25} {t_srab:>12.2f} {t_impact_para:>12.2f} {t_srab - t_impact_para:>+12.2f}"
)
print(
    f"  {'KE_impacto [J]':<25} {ke_srab:>12.2f} {ke_impact_para:>12.2f} {ke_srab - ke_impact_para:>+12.2f}"
)
print(
    f"  {'LASC 20-45 m/s':<25} {'DENTRO' if 20 <= v_srab <= 45 else 'FORA':>12} {'DENTRO' if 20 <= v_impact_para <= 45 else 'FORA':>12}"
)
print("=" * 65)

# =============================================================================
# 4. Tabela resumo para o paper
# =============================================================================
print()
print("Tabela para o paper:")
print()
print("| Parametro | SRAB (Asa3, 2 asas) | Paraquedas (200mm, CD=1.5) |")
print("|---|---|---|")
print(f"| Velocidade de impacto [m/s] | {v_srab:.2f} | {v_impact_para:.2f} |")
print(f"| Tempo de descida [s] | {t_srab:.1f} | {t_impact_para:.1f} |")
print(f"| Energia de impacto [J] | {ke_srab:.2f} | {ke_impact_para:.2f} |")
print(
    f"| Dentro da janela LASC (20-45 m/s) | {'Sim' if 20 <= v_srab <= 45 else 'Nao'} | {'Sim' if 20 <= v_impact_para <= 45 else 'Nao'} |"
)
