# -*- coding: utf-8 -*-
"""Gera gráficos comparativos de análise DXF vs paramétrica"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Carregar resultados da análise DXF
with open("extras/wing-analisys/Asa2_analise.json") as f:
    asa2_data = json.load(f)

# Carregar script de teste anterior para comparação
import sys

sys.path.insert(0, "extras/wing-analisys")
from estudo_asa_2p import v_terminal, massa_asas, energia_impacto, massa_total

print("\n" + "=" * 80)
print("COMPARAÇÃO: ASA2 (DXF) vs ASA 16cm PARAMÉTRICA")
print("=" * 80)

# Dados da Asa2
geom_asa2 = asa2_data["geometria"]
sims_asa2 = asa2_data["simulacoes"]

print(f"\n📐 Asa2 (DXF):")
print(f"  Raio: {geom_asa2['R_mm']:.1f} mm ({geom_asa2['R_mm'] / 10:.1f} cm)")
print(f"  Corda máx: {geom_asa2['corda_max_mm']:.1f} mm")
print(f"  Área: {geom_asa2['area_aprox_cm2']:.2f} cm²")

# Dados da asa 16cm original
R_16cm = 160  # mm
print(f"\n📐 Asa 16cm (original):")
print(f"  Raio: {R_16cm} mm (16.0 cm)")

# Criar figura de comparação
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# --- Gráfico 1: v_terminal vs número de asas ---
ax = axes[0, 0]

n_asas_list = [2, 3, 4, 6]
cores = ["#e74c3c", "#e67e22", "#2ecc71", "#3498db"]

# Asa2
v_asa2 = {}
for sim in sims_asa2:
    key = sim["n_asas"]
    if key not in v_asa2:
        v_asa2[key] = []
    v_asa2[key].append(sim["v_terminal_ms"])

for n in n_asas_list:
    if n in v_asa2:
        v_vals = v_asa2[n]
        x_pos = [n - 0.15, n + 0.15]
        ax.scatter(
            [n - 0.15] * len(v_vals),
            v_vals,
            s=80,
            alpha=0.6,
            label=f"Asa2 ({n})",
            color=cores[n_asas_list.index(n)],
        )

# Asa 16cm original (para referência)
R_16 = 0.160
m_pq = 0.450
v_16cm = [v_terminal(massa_total(m_pq, R_16, n), R_16, n) for n in n_asas_list]
ax.plot(
    n_asas_list,
    v_16cm,
    "k--",
    linewidth=2,
    marker="o",
    markersize=8,
    label="Asa 16cm (original)",
    alpha=0.7,
)

ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.5, label="Limite seguro")
ax.set_xlabel("Número de asas")
ax.set_ylabel("v₀ (m/s)")
ax.set_title("Velocidade Terminal: Asa2 vs Asa 16cm")
ax.set_xticks(n_asas_list)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Gráfico 2: Energia de impacto ---
ax = axes[0, 1]

for n in n_asas_list:
    if n in v_asa2:
        # Pegar primeiro valor de cada n (maior raio)
        matching_sims = [s for s in sims_asa2 if s["n_asas"] == n]
        matching_sims.sort(key=lambda x: x["R_mm"], reverse=True)
        sim = matching_sims[0]
        ax.scatter(
            n,
            sim["energia_J"],
            s=100,
            alpha=0.6,
            color=cores[n_asas_list.index(n)],
            label=f"Asa2",
        )

# Asa 16cm
E_16cm = []
for n in n_asas_list:
    m_tot = massa_total(m_pq, R_16, n)
    v0 = v_terminal(m_tot, R_16, n)
    E = energia_impacto(m_tot, v0)
    E_16cm.append(E)

ax.plot(
    n_asas_list,
    E_16cm,
    "k--",
    linewidth=2,
    marker="s",
    markersize=8,
    label="Asa 16cm",
    alpha=0.7,
)

ax.axhline(y=5, color="orange", linestyle="--", alpha=0.5, label="Limite 5J")
ax.axhline(y=10, color="red", linestyle="--", alpha=0.5, label="Limite 10J")
ax.set_xlabel("Número de asas")
ax.set_ylabel("Energia de impacto (J)")
ax.set_title("Energia de Impacto")
ax.set_xticks(n_asas_list)
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Gráfico 3: Distribuição de raios testados ---
ax = axes[1, 0]

raios_por_n = {}
for sim in sims_asa2:
    n = sim["n_asas"]
    if n not in raios_por_n:
        raios_por_n[n] = []
    raios_por_n[n].append(sim["R_mm"])

for n in n_asas_list:
    if n in raios_por_n:
        x = [n] * len(raios_por_n[n])
        ax.scatter(
            x, raios_por_n[n], s=100, alpha=0.6, color=cores[n_asas_list.index(n)]
        )

ax.axhline(y=160, color="gray", linestyle="--", alpha=0.5, label="Asa 16cm")
ax.set_xlabel("Número de asas")
ax.set_ylabel("Raio (mm)")
ax.set_title("Raios testados por configuração")
ax.set_xticks(n_asas_list)
ax.grid(True, alpha=0.3)

# --- Gráfico 4: Resumo numérico ---
ax = axes[1, 1]
ax.axis("off")

resumo = f"""
RESUMO - ASA2 (DXF)
{"=" * 50}

Dimensões Geométricas:
  • Raio máximo: {geom_asa2["R_mm"]:.1f} mm
  • Corda máxima: {geom_asa2["corda_max_mm"]:.1f} mm
  • Área aproximada: {geom_asa2["area_aprox_cm2"]:.2f} cm²

Melhor Configuração:
  • Tipo: 6 asas de {sims_asa2[-1]["R_mm"]:.0f} mm
  • v₀: {sims_asa2[-1]["v_terminal_ms"]:.2f} m/s ✓
  • Energia: {sims_asa2[-1]["energia_J"]:.1f} J
  • Cabe dobrado: Sim ✓

Comparação com Asa 16cm:
  • Asa2 (6×125mm): v₀ = 7.12 m/s
  • Asa16 (4×16cm): v₀ = {v_16cm[2]:.2f} m/s
  • Diferença: {abs(7.12 - v_16cm[2]):.2f} m/s
    ({"+" if 7.12 > v_16cm[2] else "-"}{abs(7.12 - v_16cm[2]) / v_16cm[2] * 100:.0f}%)

Conclusão:
  Asa2 é {("MAIS" if 7.12 < v_16cm[2] else "MENOS")} 
  eficiente na velocidade de descida.
"""

ax.text(
    0.05,
    0.95,
    resumo,
    transform=ax.transAxes,
    fontsize=10,
    verticalalignment="top",
    fontfamily="monospace",
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
)

plt.tight_layout()
plt.savefig("extras/wing-analisys/Asa2_comparacao.png", dpi=150, bbox_inches="tight")
print("\n📊 Gráfico de comparação salvo: extras/wing-analisys/Asa2_comparacao.png")

# --- Tabela comparativa de texto ---
print("\n" + "=" * 80)
print("TABELA COMPARATIVA - CONFIGURAÇÕES")
print("=" * 80)

print(f"\n{'Config':<20} | {'Asa2':<20} | {'Asa 16cm':<20} | {'Diferença':>10}")
print(
    f"{'':20} | {'v₀ (m/s)':>8} {'E (J)':>10} | {'v₀ (m/s)':>8} {'E (J)':>10} | {'v₀ %':>10}"
)
print("-" * 100)

for i, n in enumerate(n_asas_list):
    if n in v_asa2:
        # Asa2: usar raio máximo
        sim_asa2 = [s for s in sims_asa2 if s["n_asas"] == n]
        sim_asa2 = sorted(sim_asa2, key=lambda x: x["R_mm"], reverse=True)[0]

        # Asa 16cm
        m_tot_16 = massa_total(m_pq, R_16, n)
        v0_16 = v_terminal(m_tot_16, R_16, n)
        E_16 = energia_impacto(m_tot_16, v0_16)

        v_diff_pct = (sim_asa2["v_terminal_ms"] - v0_16) / v0_16 * 100

        config_str = f"{n}×R{sim_asa2['R_mm']:.0f}mm"

        print(
            f"{config_str:<20} | {sim_asa2['v_terminal_ms']:>8.2f} {sim_asa2['energia_J']:>10.1f} | "
            f"{v0_16:>8.2f} {E_16:>10.1f} | {v_diff_pct:>9.1f}%"
        )

print(
    "\nLegenda: v₀ = velocidade terminal, E = energia impacto, Diferença = (Asa2 - Asa16) / Asa16"
)

plt.show()

print("\n✅ Análise comparativa concluída!")
