# -*- coding: utf-8 -*-
"""Gera gráficos do estudo de asa Helike - Material TPU"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings

warnings.filterwarnings("ignore")

# Configuração dos gráficos
plt.rcParams["figure.figsize"] = (14, 10)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

# === CONSTANTES E MODELO ===
g = 9.81
rho_ar = 1.225
m_pq = 0.350
rho_tpu = 1200
espessura = 0.6e-3


def v_terminal(m, R, n, k=3.2):
    v = k * np.sqrt(m) / (R * np.sqrt(n))
    return np.clip(v, 1.5, 20.0)


def massa_asas(R, n):
    area = 0.03 * R**2
    return n * area * espessura * rho_tpu


def massa_total(R, n):
    return m_pq + massa_asas(R, n)


def energia_impacto(m, v):
    return 0.5 * m * v**2


def velocidade_rotacao(R, v0, lambda_=0.065):
    omega = v0 / (lambda_ * R)
    return np.minimum(omega, 100)


def perfil_samara(r, R):
    if r <= 0 or r >= R:
        return 0
    x = r / R
    return 0.08 * R * 4 * x * (1 - x) ** 2


# === FIGURA 1: Velocidade e Energia vs Raio ===
print("Gerando Figura 1: Velocidade e Energia vs Raio...")

fig1, axes1 = plt.subplots(2, 2, figsize=(14, 10))

R_range = np.linspace(0.08, 0.30, 100)
n_asas_list = [1, 2, 3, 4, 6]
cores = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"]

# 1a: Velocidade vs Raio
ax = axes1[0, 0]
for n, cor in zip(n_asas_list, cores):
    v_vals = [v_terminal(massa_total(R, n), R, n) for R in R_range]
    ax.plot(R_range * 100, v_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.7, label="Limite seguro")
ax.axhline(y=8.0, color="orange", linestyle="--", alpha=0.7, label="Limite aceitável")
ax.axvspan(8, 16, alpha=0.1, color="green", label="Envelope dobrável")
ax.set_xlabel("Raio da Asa (cm)")
ax.set_ylabel("Velocidade Terminal (m/s)")
ax.set_title("Velocidade de Descida vs Raio")
ax.legend(loc="upper right", fontsize=9)
ax.set_ylim(0, 15)

# 1b: Energia vs Raio
ax = axes1[0, 1]
for n, cor in zip(n_asas_list, cores):
    m_vals = [massa_total(R, n) for R in R_range]
    v_vals = [v_terminal(m, R, n) for m, R in zip(m_vals, R_range)]
    E_vals = [energia_impacto(m, v) for m, v in zip(m_vals, v_vals)]
    ax.plot(R_range * 100, E_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=5, color="orange", linestyle="--", alpha=0.7, label="Limite energia (5 J)")
ax.axvspan(8, 16, alpha=0.1, color="green")
ax.set_xlabel("Raio da Asa (cm)")
ax.set_ylabel("Energia de Impacto (J)")
ax.set_title("Energia de Impacto vs Raio")
ax.legend(loc="upper right", fontsize=9)
ax.set_ylim(0, 25)

# 1c: Rotação vs Raio
ax = axes1[1, 0]
for n, cor in zip(n_asas_list, cores):
    omega_vals = [
        velocidade_rotacao(R, v_terminal(massa_total(R, n), R, n)) for R in R_range
    ]
    ax.plot(R_range * 100, omega_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.set_xlabel("Raio da Asa (cm)")
ax.set_ylabel("Velocidade Angular (rad/s)")
ax.set_title("Velocidade de Rotação vs Raio")
ax.legend(fontsize=9)

# 1d: Massa vs Raio
ax = axes1[1, 1]
for n, cor in zip(n_asas_list, cores):
    m_vals = [massa_total(R, n) * 1000 for R in R_range]
    ax.plot(R_range * 100, m_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=350, color="gray", linestyle=":", alpha=0.7, label="Massa base (350g)")
ax.set_xlabel("Raio da Asa (cm)")
ax.set_ylabel("Massa Total (g)")
ax.set_title("Massa Total vs Raio")
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig("extras/fig1_velocidade_energia.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 2: Mapas de Calor ===
print("Gerando Figura 2: Mapas de Calor (Espaço de Design)...")

fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5))

R_mesh = np.linspace(0.08, 0.25, 50)
n_mesh = np.array([1, 2, 3, 4, 6])
R_grid, N_grid = np.meshgrid(R_mesh, n_mesh)

V_grid = np.zeros_like(R_grid)
E_grid = np.zeros_like(R_grid)

for i in range(len(n_mesh)):
    for j in range(len(R_mesh)):
        R = R_mesh[j]
        n = n_mesh[i]
        m = massa_total(R, n)
        v = v_terminal(m, R, n)
        V_grid[i, j] = v
        E_grid[i, j] = energia_impacto(m, v)

# Mapa Velocidade
ax = axes2[0]
im = ax.pcolormesh(R_grid * 100, N_grid, V_grid, cmap="RdYlGn_r", vmin=3, vmax=12)
CS = ax.contour(
    R_grid * 100, N_grid, V_grid, levels=[5, 6, 8], colors="black", linewidths=1.5
)
ax.clabel(CS, inline=True, fontsize=9)
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("Número de Asas")
ax.set_title("Velocidade Terminal (m/s)")
plt.colorbar(im, ax=ax, label="m/s")

# Mapa Energia
ax = axes2[1]
im = ax.pcolormesh(R_grid * 100, N_grid, E_grid, cmap="RdYlGn_r", vmin=1, vmax=15)
CS = ax.contour(
    R_grid * 100, N_grid, E_grid, levels=[3, 5, 10], colors="black", linewidths=1.5
)
ax.clabel(CS, inline=True, fontsize=9)
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("Número de Asas")
ax.set_title("Energia de Impacto (J)")
plt.colorbar(im, ax=ax, label="J")

# Mapa Velocidade Rotação
ax = axes2[2]
Omega_grid = np.zeros_like(R_grid)
for i in range(len(n_mesh)):
    for j in range(len(R_mesh)):
        R = R_mesh[j]
        n = n_mesh[i]
        v = V_grid[i, j]
        Omega_grid[i, j] = velocidade_rotacao(R, v) / (2 * np.pi)

im = ax.pcolormesh(R_grid * 100, N_grid, Omega_grid, cmap="viridis")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("Número de Asas")
ax.set_title("Frequência de Rotação (Hz)")
plt.colorbar(im, ax=ax, label="Hz")

plt.tight_layout()
plt.savefig("extras/fig2_mapas_calor.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 3: Sensibilidade à Massa ===
print("Gerando Figura 3: Sensibilidade à Massa...")

fig3, axes3 = plt.subplots(2, 2, figsize=(14, 10))

m_range = np.linspace(0.200, 0.500, 100)
configs = [
    (0.12, 4, "4 asas 12cm"),
    (0.15, 4, "4 asas 15cm"),
    (0.16, 4, "4 asas 16cm"),
    (0.20, 4, "4 asas 20cm"),
]

# Velocidade vs Massa
ax = axes3[0, 0]
for R, n, label in configs:
    v_vals = [v_terminal(m, R, n) for m in m_range]
    ax.plot(m_range * 1000, v_vals, linewidth=2.5, label=label)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.5, label="v₀ alvo")
ax.axvline(x=350, color="gray", linestyle=":", alpha=0.5, label="Massa atual")
ax.set_xlabel("Massa (g)")
ax.set_ylabel("Velocidade (m/s)")
ax.set_title("Velocidade vs Massa do Satélite")
ax.legend(fontsize=9)

# Energia vs Massa
ax = axes3[0, 1]
for R, n, label in configs:
    E_vals = [energia_impacto(m, v_terminal(m, R, n)) for m in m_range]
    ax.plot(m_range * 1000, E_vals, linewidth=2.5, label=label)
ax.axhline(y=5, color="orange", linestyle="--", alpha=0.5, label="Limite 5 J")
ax.axvline(x=350, color="gray", linestyle=":", alpha=0.5)
ax.set_xlabel("Massa (g)")
ax.set_ylabel("Energia (J)")
ax.set_title("Energia de Impacto vs Massa")
ax.legend(fontsize=9)

# Massa máxima para v0=5.5
ax = axes3[1, 0]
R_range2 = np.linspace(0.10, 0.25, 50)
for n, cor in zip([2, 3, 4, 6], cores):
    m_target = [(5.5 * R * np.sqrt(n) / 3.2) ** 2 * 1000 for R in R_range2]
    ax.plot(R_range2 * 100, m_target, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=350, color="gray", linestyle=":", alpha=0.7, label="Massa atual")
ax.axhline(y=300, color="green", linestyle="--", alpha=0.7, label="Meta 300g")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("Massa Máxima (g)")
ax.set_title("Massa Máxima para v₀ ≤ 5.5 m/s")
ax.legend(fontsize=9)

# Velocidade de rotação vs Massa
ax = axes3[1, 1]
for R, n, label in configs:
    omega_vals = [
        velocidade_rotacao(R, v_terminal(m, R, n)) / (2 * np.pi) for m in m_range
    ]
    ax.plot(m_range * 1000, omega_vals, linewidth=2.5, label=label)
ax.axvline(x=350, color="gray", linestyle=":", alpha=0.5)
ax.set_xlabel("Massa (g)")
ax.set_ylabel("Frequência (Hz)")
ax.set_title("Frequência de Rotação vs Massa")
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig("extras/fig3_sensibilidade_massa.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 4: Perfil da Asa e Visualizações ===
print("Gerando Figura 4: Perfil da Asa...")

fig4 = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 3, figure=fig4, height_ratios=[1, 1, 1])

# --- Linha 1: Perfil da corda e Área ---

# Perfis para diferentes raios
ax1 = fig4.add_subplot(gs[0, 0])
for R_cm in [12, 15, 16, 20]:
    R = R_cm / 100
    r = np.linspace(0, R, 100)
    w = [perfil_samara(ri, R) for ri in r]
    ax1.plot(r * 100, [wi * 1000 for wi in w], linewidth=2.5, label=f"R={R_cm}cm")
ax1.fill_between([], [], alpha=0.3, color="#3498db", label="Área da asa")
ax1.set_xlabel("Posição radial (cm)")
ax1.set_ylabel("Corda (mm)")
ax1.set_title("Perfil da Corda (vista lateral)")
ax1.legend(fontsize=9)
ax1.annotate(
    "Largura máxima\nem ~30% do raio",
    xy=(4.8, 10),
    xytext=(8, 12),
    arrowprops=dict(arrowstyle="->", color="gray"),
    fontsize=9,
    color="gray",
)

# Área total vs Raio
ax2 = fig4.add_subplot(gs[0, 1])
R_range3 = np.linspace(0.08, 0.25, 50)
for n in [1, 2, 4]:
    areas = []
    for R in R_range3:
        r_int = np.linspace(1e-6, R - 1e-6, 100)
        w_int = [perfil_samara(r, R) for r in r_int]
        area = np.trapz(w_int, r_int) * n * 10000
        areas.append(area)
    ax2.plot(R_range3 * 100, areas, linewidth=2.5, label=f"{n} asa(s)")
ax2.set_xlabel("Raio (cm)")
ax2.set_ylabel("Área Total (cm²)")
ax2.set_title("Área Aerodinâmica vs Raio")
ax2.legend()

# Espaço de dobragem
ax3 = fig4.add_subplot(gs[0, 2])
n_range = np.array([1, 2, 3, 4, 6])
R_dobra = np.linspace(0.05, 0.25, 50)
for n in n_range:
    espaco = R_dobra / n + 0.005
    ax3.plot(R_dobra * 100, espaco * 1000, linewidth=2, label=f"{n} asa(s)")
ax3.axhline(y=50, color="red", linestyle="--", linewidth=2, label="Limite 50mm")
ax3.fill_between(R_dobra * 100, 0, 50, alpha=0.1, color="green")
ax3.set_xlabel("Raio (cm)")
ax3.set_ylabel("Espaço necessário (mm)")
ax3.set_title("Espaço de Dobragem vs Raio")
ax3.legend(fontsize=9)
ax3.set_ylim(0, 80)

# --- Linha 2 e 3: Visualizações 2D (vista de cima) ---


def desenhar_asa_2d(ax, n_asas, R, cor="#2ecc71", titulo=""):
    """Desenha vista de cima da configuração de asas."""
    for i in range(n_asas):
        offset = 2 * np.pi * i / n_asas
        r_plot = np.linspace(0, R, 100)
        w_plot = np.array([perfil_samara(r, R) for r in r_plot])
        x_asa = r_plot * np.cos(offset)
        y_asa = r_plot * np.sin(offset)
        x_l = x_asa - w_plot * np.sin(offset) / 2
        x_r = x_asa + w_plot * np.sin(offset) / 2
        y_l = y_asa + w_plot * np.cos(offset) / 2
        y_r = y_asa - w_plot * np.cos(offset) / 2
        ax.fill_betweenx(y_asa, x_l, x_r, alpha=0.5, color=cor)
        ax.plot(x_l, y_l, "-", color=cor, linewidth=1.5)
        ax.plot(x_r, y_r, "-", color=cor, linewidth=1.5)

    # Corpo central
    corpo = plt.Rectangle(
        (-0.025, -0.025),
        0.05,
        0.05,
        fill=True,
        facecolor="#34495e",
        edgecolor="black",
        linewidth=2,
    )
    ax.add_patch(corpo)
    ax.set_xlim(-0.22, 0.22)
    ax.set_ylim(-0.22, 0.22)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(titulo, fontweight="bold")
    ax.grid(True, alpha=0.2)


# 1 asa - R=20cm
ax4 = fig4.add_subplot(gs[1, 0])
desenhar_asa_2d(ax4, 1, 0.20, cor="#e74c3c", titulo="1 asa - R=20cm")
ax4.text(0.05, -0.20, "v₀≈10.4 m/s\nE≈18.8 J", fontsize=9, color="red")

# 2 asas - R=20cm
ax5 = fig4.add_subplot(gs[1, 1])
desenhar_asa_2d(ax5, 2, 0.20, cor="#e67e22", titulo="2 asas - R=20cm")
ax5.text(0.05, -0.20, "v₀≈7.3 m/s\nE≈9.5 J", fontsize=9, color="orange")

# 4 asas - R=16cm (recomendada)
ax6 = fig4.add_subplot(gs[1, 2])
desenhar_asa_2d(ax6, 4, 0.16, cor="#2ecc71", titulo="4 asas - R=16cm (RECOMENDADA)")
ax6.text(0.05, -0.20, "v₀≈5.9 m/s\nE≈6.2 J", fontsize=9, color="green")

# 2 asas - R=16cm
ax7 = fig4.add_subplot(gs[2, 0])
desenhar_asa_2d(ax7, 2, 0.16, cor="#f1c40f", titulo="2 asas - R=16cm")
ax7.text(0.05, -0.20, "v₀≈8.4 m/s\nE≈12.4 J", fontsize=9, color="#b8860b")

# 4 asas - R=20cm
ax8 = fig4.add_subplot(gs[2, 1])
desenhar_asa_2d(ax8, 4, 0.20, cor="#3498db", titulo="4 asas - R=20cm")
ax8.text(
    0.05, -0.20, "v₀≈4.8 m/s\nE≈4.0 J\n(Não cabe dobrada)", fontsize=9, color="blue"
)

# 3 asas - R=20cm
ax9 = fig4.add_subplot(gs[2, 2])
desenhar_asa_2d(ax9, 3, 0.20, cor="#9b59b6", titulo="3 asas - R=20cm")
ax9.text(
    0.05, -0.20, "v₀≈5.5 m/s\nE≈5.3 J\n(Não cabe dobrada)", fontsize=9, color="purple"
)

plt.tight_layout()
plt.savefig("extras/fig4_perfil_asa.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 5: Tempo de Descida ===
print("Gerando Figura 5: Tempo de Descida...")

fig5, axes5 = plt.subplots(1, 2, figsize=(14, 5))

alturas = np.linspace(100, 5000, 100)
configs_tempo = [
    (0.12, 4, "4 asas 12cm"),
    (0.15, 4, "4 asas 15cm"),
    (0.16, 4, "4 asas 16cm"),
    (0.20, 4, "4 asas 20cm"),
]

ax = axes5[0]
for R, n, label in configs_tempo:
    m = massa_total(R, n)
    v0 = v_terminal(m, R, n)
    tempos = alturas / v0 / 60
    ax.plot(alturas, tempos, linewidth=2.5, label=f"{label} (v₀={v0:.1f} m/s)")
ax.axvline(x=1000, color="gray", linestyle=":", alpha=0.5, label="Referência 1000m")
ax.set_xlabel("Altura (m)")
ax.set_ylabel("Tempo (min)")
ax.set_title("Tempo de Descida vs Altura")
ax.legend(fontsize=9)
ax.set_ylim(0, 15)

ax = axes5[1]
t = np.linspace(0, 30, 200)
for R, n, label in configs_tempo[:3]:
    m = massa_total(R, n)
    v_term = v_terminal(m, R, n)
    tau = 2.0
    v = v_term * (1 - np.exp(-t / tau))
    ax.plot(t, v, linewidth=2.5, label=label)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.5, label="v₀ alvo")
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Velocidade (m/s)")
ax.set_title("Aceleração até Velocidade Terminal")
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig("extras/fig5_tempo_descida.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 6: Comparação Final ===
print("Gerando Figura 6: Comparação Final...")

raios = [0.10, 0.12, 0.14, 0.15, 0.16, 0.18, 0.20]
num_asas = [1, 2, 3, 4, 6]
resultados = []

for n in num_asas:
    for R in raios:
        m = massa_total(R, n)
        v0 = v_terminal(m, R, n)
        E = energia_impacto(m, v0)
        espaco = R / n + 0.005
        cabe = espaco <= 0.05
        resultados.append({"n": n, "R": R, "m": m, "v0": v0, "E": E, "cabe": cabe})

configs_viaveis = [r for r in resultados if r["cabe"]]
configs_viaveis.sort(key=lambda x: x["v0"])

fig6, axes6 = plt.subplots(2, 1, figsize=(14, 10))

labels = [f"{r['n']}×R{r['R'] * 100:.0f}" for r in configs_viaveis]
v0_vals = [r["v0"] for r in configs_viaveis]
E_vals = [r["E"] for r in configs_viaveis]

cores_v0 = [
    "#2ecc71" if v < 5.5 else "#f1c40f" if v < 7 else "#e74c3c" for v in v0_vals
]
cores_E = ["#2ecc71" if e < 3 else "#f1c40f" if e < 6 else "#e74c3c" for e in E_vals]

ax = axes6[0]
bars = ax.bar(labels, v0_vals, color=cores_v0, edgecolor="black", linewidth=0.5)
ax.axhline(y=5.5, color="red", linestyle="--", linewidth=2, label="Limite seguro")
ax.set_ylabel("Velocidade (m/s)")
ax.set_title("Velocidade por Configuração (configs que cabem)")
ax.legend()
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
for bar, val in zip(bars, v0_vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.1,
        f"{val:.1f}",
        ha="center",
        fontsize=8,
    )

ax = axes6[1]
bars = ax.bar(labels, E_vals, color=cores_E, edgecolor="black", linewidth=0.5)
ax.axhline(y=5, color="orange", linestyle="--", linewidth=2, label="Limite energia")
ax.set_ylabel("Energia (J)")
ax.set_title("Energia de Impacto por Configuração")
ax.legend()
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
for bar, val in zip(bars, E_vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.1,
        f"{val:.1f}",
        ha="center",
        fontsize=8,
    )

plt.tight_layout()
plt.savefig("extras/fig6_comparacao_final.png", dpi=150, bbox_inches="tight")
plt.close()

print("\n" + "=" * 60)
print("GRÁFICOS GERADOS COM SUCESSO!")
print("=" * 60)
print("\nArquivos salvos em extras/:")
print("  1. fig1_velocidade_energia.png")
print("  2. fig2_mapas_calor.png")
print("  3. fig3_sensibilidade_massa.png")
print("  4. fig4_perfil_asa.png")
print("  5. fig5_tempo_descida.png")
print("  6. fig6_comparacao_final.png")
print("\nNotebook interativo: estudo_asa_helike.ipynb")
print("=" * 60)
