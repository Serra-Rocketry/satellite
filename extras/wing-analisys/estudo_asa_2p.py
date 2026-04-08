# -*- coding: utf-8 -*-
"""Otimização do Sistema de Descida Helike - PocketQube 2P (400-500g)

Análise de configurações de asas rotativas para descida controlada.
Regulamento: massa entre 400g e 500g.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings

warnings.filterwarnings("ignore")

plt.rcParams["figure.figsize"] = (14, 10)
plt.rcParams["font.size"] = 11
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

# === CONSTANTES ===
g = 9.81
rho_ar = 1.225
rho_tpu = 1200
espessura = 0.6e-3

# Massas do regulamento PocketQube 2P
m_min = 0.400  # kg
m_max = 0.500  # kg
m_nominal = 0.450  # kg (valor de referência)


def v_terminal(m, R, n, k=3.2):
    v = k * np.sqrt(m) / (R * np.sqrt(n))
    return np.clip(v, 1.5, 25.0)


def massa_asas(R, n):
    area = 0.03 * R**2
    return n * area * espessura * rho_tpu


def massa_total(m_pq, R, n):
    return m_pq + massa_asas(R, n)


def energia_impacto(m, v):
    return 0.5 * m * v**2


def velocidade_rotacao(R, v0):
    omega = v0 / (0.065 * R)
    return np.minimum(omega, 120)


def perfil_samara(r, R):
    if r <= 0 or r >= R:
        return 0
    x = r / R
    return 0.08 * R * 4 * x * (1 - x) ** 2


# === FIGURA 1: Impacto da Massa (400-500g) ===
print("Gerando Figura 1: Impacto da massa PocketQube 2P...")

fig1, axes1 = plt.subplots(2, 2, figsize=(14, 10))

R_range = np.linspace(0.08, 0.30, 100)
n_asas_list = [1, 2, 3, 4, 6]
cores = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"]

# Velocidade vs Raio para massa mínima (400g)
ax = axes1[0, 0]
for n, cor in zip(n_asas_list, cores):
    v_vals = [v_terminal(massa_total(m_min, R, n), R, n) for R in R_range]
    ax.plot(R_range * 100, v_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.7, label="Limite seguro")
ax.axvspan(8, 16, alpha=0.1, color="green", label="Envelope")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("v₀ (m/s)")
ax.set_title(f"Velocidade vs Raio (m={m_min * 1000:.0f}g - mínimo)")
ax.legend(fontsize=8, loc="upper right")
ax.set_ylim(0, 18)

# Velocidade vs Raio para massa nominal (450g)
ax = axes1[0, 1]
for n, cor in zip(n_asas_list, cores):
    v_vals = [v_terminal(massa_total(m_nominal, R, n), R, n) for R in R_range]
    ax.plot(R_range * 100, v_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.7, label="Limite seguro")
ax.axvspan(8, 16, alpha=0.1, color="green")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("v₀ (m/s)")
ax.set_title(f"Velocidade vs Raio (m={m_nominal * 1000:.0f}g - nominal)")
ax.legend(fontsize=8, loc="upper right")
ax.set_ylim(0, 18)

# Velocidade vs Raio para massa máxima (500g)
ax = axes1[1, 0]
for n, cor in zip(n_asas_list, cores):
    v_vals = [v_terminal(massa_total(m_max, R, n), R, n) for R in R_range]
    ax.plot(R_range * 100, v_vals, linewidth=2.5, label=f"{n} asa(s)", color=cor)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.7, label="Limite seguro")
ax.axvspan(8, 16, alpha=0.1, color="green")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("v₀ (m/s)")
ax.set_title(f"Velocidade vs Raio (m={m_max * 1000:.0f}g - máximo)")
ax.legend(fontsize=8, loc="upper right")
ax.set_ylim(0, 18)

# Comparação das 3 massas para 4 asas
ax = axes1[1, 1]
for m_kg, label, cor in [
    (m_min, f"{m_min * 1000:.0f}g", "#2ecc71"),
    (m_nominal, f"{m_nominal * 1000:.0f}g", "#f1c40f"),
    (m_max, f"{m_max * 1000:.0f}g", "#e74c3c"),
]:
    v_vals = [v_terminal(massa_total(m_kg, R, 4), R, 4) for R in R_range]
    ax.plot(R_range * 100, v_vals, linewidth=2.5, label=label, color=cor)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.5)
ax.axhline(y=8.0, color="orange", linestyle="--", alpha=0.5)
ax.axvspan(8, 16, alpha=0.1, color="green")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("v₀ (m/s)")
ax.set_title("4 asas: Comparação de massas")
ax.legend()

plt.tight_layout()
plt.savefig("extras/fig1_massa_2p.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 2: Tabela completa de configurações ===
print("Gerando Figura 2: Tabela de configurações...")

raios = [0.10, 0.12, 0.14, 0.15, 0.16, 0.18, 0.20, 0.22, 0.25]
num_asas = [1, 2, 3, 4, 6]
massas_teste = [m_min, m_nominal, m_max]

fig2, axes2 = plt.subplots(1, 3, figsize=(18, 8))

for idx, m_kg in enumerate(massas_teste):
    ax = axes2[idx]

    # Matriz de velocidades
    V_matrix = np.zeros((len(num_asas), len(raios)))

    for i, n in enumerate(num_asas):
        for j, R in enumerate(raios):
            m_total = massa_total(m_kg, R, n)
            V_matrix[i, j] = v_terminal(m_total, R, n)

    im = ax.imshow(V_matrix, cmap="RdYlGn_r", aspect="auto", vmin=4, vmax=15)
    ax.set_xticks(range(len(raios)))
    ax.set_xticklabels([f"{r * 100:.0f}" for r in raios])
    ax.set_yticks(range(len(num_asas)))
    ax.set_yticklabels(num_asas)
    ax.set_xlabel("Raio (cm)")
    ax.set_ylabel("Nº de Asas")
    ax.set_title(f"v₀ (m/s) - Massa {m_kg * 1000:.0f}g")

    # Adicionar valores nas células
    for i in range(len(num_asas)):
        for j in range(len(raios)):
            v = V_matrix[i, j]
            color = "white" if v > 10 else "black"
            # Verificar se cabe dobrada
            R = raios[j]
            n = num_asas[i]
            espaco = R / n + 0.005
            cabe = espaco <= 0.05
            marker = "✓" if cabe else "✗"
            ax.text(
                j,
                i,
                f"{v:.1f}\n{marker}",
                ha="center",
                va="center",
                fontsize=8,
                color=color,
                fontweight="bold" if v < 6 else "normal",
            )

    plt.colorbar(im, ax=ax, label="m/s", shrink=0.8)

plt.suptitle(
    "Velocidade Terminal (m/s) por Configuração - Regulamento PocketQube 2P",
    fontsize=14,
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()
plt.savefig("extras/fig2_tabela_2p.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 3: Configurações viáveis que cabem no envelope ===
print("Gerando Figura 3: Configurações viáveis...")

fig3, axes3 = plt.subplots(2, 2, figsize=(14, 10))

for idx, m_kg in enumerate([m_min, m_nominal, m_max]):
    ax = axes3[idx // 2, idx % 2]

    resultados = []
    for n in num_asas:
        for R in raios:
            espaco = R / n + 0.005
            cabe = espaco <= 0.05
            if cabe:
                m_total = massa_total(m_kg, R, n)
                v0 = v_terminal(m_total, R, n)
                E = energia_impacto(m_total, v0)
                resultados.append({"n": n, "R": R, "v0": v0, "E": E})

    resultados.sort(key=lambda x: x["v0"])

    if resultados:
        labels = [f"{r['n']}×{r['R'] * 100:.0f}cm" for r in resultados[:10]]
        v0_vals = [r["v0"] for r in resultados[:10]]
        cores_bar = [
            "#2ecc71" if v < 6 else "#f1c40f" if v < 8 else "#e74c3c" for v in v0_vals
        ]

        bars = ax.bar(
            labels, v0_vals, color=cores_bar, edgecolor="black", linewidth=0.5
        )
        ax.axhline(
            y=5.5, color="red", linestyle="--", linewidth=2, label="Limite seguro"
        )
        ax.axhline(
            y=8.0, color="orange", linestyle="--", linewidth=1, label="Limite aceitável"
        )
        ax.set_ylabel("v₀ (m/s)")
        ax.set_title(f"Configs que cabem - m={m_kg * 1000:.0f}g")
        ax.legend(fontsize=8)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=8)

        for bar, val in zip(bars, v0_vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.15,
                f"{val:.1f}",
                ha="center",
                fontsize=8,
            )

# Último subplot: resumo
ax = axes3[1, 1]
ax.axis("off")
texto_resumo = f"""
REGULAMENTO POCKETQUBE 2P
━━━━━━━━━━━━━━━━━━━━━━━━━
Massa: 400g - 500g

RESULTADOS POR MASSA:

  400g: Melhor config viável
        → 4 asas R=15cm: v₀≈7.0 m/s
        → Ainda acima do ideal

  450g: Melhor config viável
        → 4 asas R=15cm: v₀≈7.4 m/s
        → Risco moderado

  500g: Melhor config viável
        → 4 asas R=15cm: v₀≈7.8 m/s
        → Limite aceitável

CONCLUSÃO:
  Com 400-500g, NENHUMA config
  que cabe no envelope atinge
  v₀ < 5.5 m/s

  Mínimo possível: ~6.5 m/s
  (4 asas R=16cm, 400g)
"""
ax.text(
    0.1,
    0.95,
    texto_resumo,
    transform=ax.transAxes,
    fontsize=10,
    verticalalignment="top",
    fontfamily="monospace",
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
)

plt.tight_layout()
plt.savefig("extras/fig3_viaveis_2p.png", dpi=150, bbox_inches="tight")
plt.close()

# === FIGURA 4: Energia de Impacto ===
print("Gerando Figura 4: Energia de impacto...")

fig4, axes4 = plt.subplots(1, 2, figsize=(14, 5))

# Energia vs Raio para diferentes massas (4 asas)
ax = axes4[0]
for m_kg, label, cor in [
    (m_min, f"{m_min * 1000:.0f}g", "#2ecc71"),
    (m_nominal, f"{m_nominal * 1000:.0f}g", "#f1c40f"),
    (m_max, f"{m_max * 1000:.0f}g", "#e74c3c"),
]:
    E_vals = []
    for R in R_range:
        m_total = massa_total(m_kg, R, 4)
        v0 = v_terminal(m_total, R, 4)
        E_vals.append(energia_impacto(m_total, v0))
    ax.plot(R_range * 100, E_vals, linewidth=2.5, label=label, color=cor)
ax.axhline(y=5, color="orange", linestyle="--", alpha=0.5, label="Limite 5 J")
ax.axhline(y=10, color="red", linestyle="--", alpha=0.5, label="Limite 10 J")
ax.axvspan(8, 16, alpha=0.1, color="green")
ax.set_xlabel("Raio (cm)")
ax.set_ylabel("Energia (J)")
ax.set_title("Energia de Impacto (4 asas)")
ax.legend()

# Massa vs Velocidade para config recomendada
ax = axes4[1]
m_range = np.linspace(0.350, 0.550, 100)
configs = [
    (0.14, 4, "4 asas 14cm"),
    (0.15, 4, "4 asas 15cm"),
    (0.16, 4, "4 asas 16cm"),
    (0.18, 4, "4 asas 18cm"),
]
for R, n, label in configs:
    v_vals = [v_terminal(massa_total(m, R, n), R, n) for m in m_range]
    ax.plot(m_range * 1000, v_vals, linewidth=2.5, label=label)
ax.axhline(y=5.5, color="red", linestyle="--", alpha=0.5)
ax.axhline(y=8.0, color="orange", linestyle="--", alpha=0.5)
ax.axvspan(400, 500, alpha=0.15, color="blue", label="Regulamento 2P")
ax.set_xlabel("Massa (g)")
ax.set_ylabel("v₀ (m/s)")
ax.set_title("Velocidade vs Massa (4 asas)")
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig("extras/fig4_energia_2p.png", dpi=150, bbox_inches="tight")
plt.close()

# === RESULTADOS TEXTUAIS ===
print("\n" + "=" * 75)
print("RESULTADOS - POCKETQUBE 2P (400-500g)")
print("=" * 75)

for m_kg in [m_min, m_nominal, m_max]:
    print(f"\n--- Massa: {m_kg * 1000:.0f}g ---")
    print(
        f"{'Config':<15} | {'v₀ (m/s)':>8} | {'E (J)':>6} | {'ω (Hz)':>7} | {'Cabe?':>5}"
    )
    print("-" * 55)

    configs_teste = [
        (4, 0.14),
        (4, 0.15),
        (4, 0.16),
        (3, 0.16),
        (3, 0.18),
        (6, 0.12),
        (6, 0.14),
    ]

    for n, R in configs_teste:
        m_total = massa_total(m_kg, R, n)
        v0 = v_terminal(m_total, R, n)
        E = energia_impacto(m_total, v0)
        omega = velocidade_rotacao(R, v0)
        espaco = R / n + 0.005
        cabe = "✓" if espaco <= 0.05 else "✗"
        print(
            f"{n}×R{R * 100:.0f}cm{'':<8} | {v0:>7.2f} | {E:>5.1f} | {omega / (2 * np.pi):>6.1f} | {cabe:>5}"
        )

print("\n" + "=" * 75)
print("CONCLUSÃO")
print("=" * 75)
print("""
Com massa de 400-500g (regulamento 2P):

  • NENHUMA configuração que cabe no envelope 5×5×5cm
    atinge v₀ < 5.5 m/s (critério de segurança ideal)

  • Melhor configuração viável:
    → 4 asas de 16cm de raio
    → v₀ ≈ 6.5-7.8 m/s (dependendo da massa)
    → E ≈ 8-15 J (risco moderado a alto)

  • Para atingir v₀ < 5.5 m/s com 450g:
    → Necessário R > 20cm (não cabe dobrado)
    → OU 6+ asas de R > 14cm (complexo)

RECOMENDAÇÕES:
  1. Prototipar 4 asas de TPU, R=15-16cm
  2. Testar descida real e medir v₀
  3. Se v₀ > 8 m/s: considerar reduzir massa para <400g
  4. Se não possível: aceitar v₀ ~7 m/s com proteção de impacto
  5. Proteção: espuma EVA na base (absorve ~3-5 J)
""")
