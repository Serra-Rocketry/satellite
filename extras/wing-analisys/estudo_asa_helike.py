# -*- coding: utf-8 -*-
"""Otimização do Sistema de Descida Helike - APENAS ASAS (TPU)

Análise de configurações de asas rotativas para descida controlada.
Sem paraquedas - confiando apenas na autorrotação samara.
"""

import numpy as np
from scipy.optimize import minimize_scalar

# === CONSTANTES ===
g = 9.81
rho_ar = 1.225


# === MODELO DE VELOCIDADE TERMINAL (SAMARA) ===
def v_terminal_samara(m, R, n, k=3.2):
    """Modelo empírico para velocidade terminal de samara.

    Args:
        m: massa total (kg)
        R: raio da asa (m)
        n: número de asas
        k: constante empírica (ajustada com testes)

    Returns:
        Velocidade terminal (m/s)
    """
    # v ∝ √m / (R·√n)
    v = k * np.sqrt(m) / (R * np.sqrt(n))
    return np.clip(v, 1.5, 20.0)


def massa_asas(R, n, esp=0.6e-3, rho_tpu=1200):
    """Massa total das asas de TPU.

    Área de cada asa ≈ 0.03·R² (formato samara otimizado)
    """
    area_por_asa = 0.03 * R**2  # m²
    return n * area_por_asa * esp * rho_tpu


def momento_inercia(R, n, m_pq, esp=0.6e-3, rho_tpu=1200):
    """Momento de inércia total do sistema."""
    # Corpo (cubo)
    I_corpo = (1 / 6) * m_pq * (0.05**2)

    # Asas (placas finas rotando em torno do centro)
    def integrar_inercia_asa(R):
        # I ≈ (1/3)·m·R² para placa fina
        m_asa = 0.03 * R**2 * esp * rho_tpu
        return (1 / 3) * m_asa * R**2

    I_asas = n * integrar_inercia_asa(R)
    return I_corpo + I_asas


def velocidade_rotacao(R, v0):
    """Velocidade angular estimada em autorrotação estável.

    Relação: ω = v₀ / (λ·R), onde λ ≈ 0.05-0.1
    """
    lambda_avanco = 0.065
    omega = v0 / (lambda_avanco * R)
    return min(omega, 100)  # Limitar a ~16 Hz


def energia_impacto(m, v):
    """Energia cinética no impacto."""
    return 0.5 * m * v**2


def classificar(v, E):
    """Classificação de segurança."""
    if v < 4.0 and E < 2.0:
        return "SEGURO", "✓"
    elif v < 5.5 and E < 5.0:
        return "ACEITÁVEL", "○"
    elif v < 7.0 and E < 10.0:
        return "MODERADO", "△"
    elif v < 10.0:
        return "RISCADO", "!"
    else:
        return "PERIGOSO", "✗"


def dobravel(R, n):
    """Verifica se a configuração cabe no envelope 5x5x5cm dobrada."""
    # Cada asa dobrada ocupa ~R/2 de comprimento + largura da corda
    # Máximo: 5cm = 0.05m
    espaco_por_asa = R / 2 + 0.01  # Raio/2 + espessura margem

    if n == 1:
        return espaco_por_asa <= 0.05
    elif n == 2:
        # 2 asas opostas, cada uma R/2
        return espaco_por_asa <= 0.05
    elif n == 4:
        # 4 asas, cada uma R/4 quando dobrada
        return (R / 4 + 0.008) <= 0.05
    else:
        return False


# === PARÂMETROS DO SATÉLITE ===
m_pq_base = 0.350  # kg (350g)

# === SIMULAÇÃO ===
print("=" * 90)
print("OTIMIZAÇÃO DO SISTEMA DE DESCIDA HELIKE - APENAS ASAS (TPU)")
print("=" * 90)
print(f"""
Objetivo: Encontrar configuração de asas para v₀ < 5.5 m/s
Restrição: Sem paraquedas - apenas autorrotação samara
Material: TPU 95A (espessura 0.6mm)

Parâmetros do satélite:
  Massa base:          {m_pq_base * 1000:.0f} g
  Dimensões:           5x5x5 cm (envelope PocketQube)
  Dobragem:            Asas devem caber em 5cm fechadas
""")

# Configurações para teste
raios = [0.10, 0.12, 0.14, 0.15, 0.16, 0.18, 0.20, 0.22, 0.25]
num_asas = [1, 2, 3, 4, 6]

print(f"{'─' * 90}")
print(
    f"{'N°':>2} │ {'Asas':>1} │ {'Raio':>4} │ {'Massa':>6} │ {'v₀':>6} │ {'ω':>7} │ {'Freq':>5} │ {'E':>5} │ {'Queda':>5} │ {'Dobra':>5} │ {'Class':>10}"
)
print(
    f"{'':>2} │ {'':>1} │ {'(cm)':>4} │ {'(g)':>6} │ {'(m/s)':>6} │ {'(rad/s)':>7} │ {'(Hz)':>5} │ {'(J)':>5} │ {'(min)':>5} │ {'':>5} │ {'':>10}"
)
print(f"{'─' * 90}")

resultados = []
idx = 0

for n in num_asas:
    for R in raios:
        # Calcular massa total
        m_asas = massa_asas(R, n)
        m_total = m_pq_base + m_asas

        # Velocidade terminal
        v0 = v_terminal_samara(m_total, R, n)

        # Velocidade de rotação
        omega = velocidade_rotacao(R, v0)
        freq = omega / (2 * np.pi)

        # Energia de impacto
        E = energia_impacto(m_total, v0)

        # Tempo de queda (1000m)
        tempo = 1000 / v0 / 60

        # Verificar dobragem
        cabe = dobravel(R, n)

        # Classificação
        classificacao, simbolo = classificar(v0, E)

        # Só mostrar se cabe no envelope ou for interessante
        if cabe or v0 < 6.0:
            idx += 1
            dob_str = "✓" if cabe else "✗"
            print(
                f"{idx:>2} │ {n:>1} │ {R * 100:>3.0f} │ {m_total * 1000:>5.1f} │ {v0:>5.2f} │ {omega:>6.1f} │ {freq:>4.1f} │ {E:>4.1f} │ {tempo:>4.1f} │ {dob_str:>5} │ {simbolo} {classificacao:<8}"
            )

            resultados.append(
                {
                    "n": n,
                    "R": R,
                    "m": m_total,
                    "v0": v0,
                    "omega": omega,
                    "freq": freq,
                    "E": E,
                    "tempo": tempo,
                    "cabe": cabe,
                    "class": classificacao,
                }
            )

print(f"{'─' * 90}")

# === ANÁLISE ===
print(f"\n{'=' * 90}")
print("ANÁLISE - CONFIGURAÇÕES QUE CABEM NO ENVELOPE")
print(f"{'=' * 90}")

configs_viaveis = [r for r in resultados if r["cabe"]]
configs_viaveis.sort(key=lambda x: x["v0"])

print(f"\n  {'Configuração':<20} │ {'v₀':>6} │ {'E':>5} │ {'Freq':>5} │ {'Status':<12}")
print(f"  {'':20} │ {'(m/s)':>6} │ {'(J)':>5} │ {'(Hz)':>5} │ {'':12}")
print(f"  {'─' * 65}")

for r in configs_viaveis:
    classificacao, simbolo = classificar(r["v0"], r["E"])
    print(
        f"  {r['n']} asa(s) R={r['R'] * 100:.0f}cm{'':<8} │ {r['v0']:>5.2f} │ {r['E']:>4.1f} │ {r['freq']:>4.1f} │ {simbolo} {classificacao:<9}"
    )

# === MELHOR CONFIGURAÇÃO ===
print(f"\n{'=' * 90}")
print("MELHOR CONFIGURAÇÃO QUE CABE NO ENVELOPE")
print(f"{'=' * 90}")

if configs_viaveis:
    melhor = configs_viaveis[0]
    print(f"""
  Configuração:        {melhor["n"]} asa(s) de {melhor["R"] * 100:.0f}cm de raio
  Massa total:         {melhor["m"] * 1000:.1f} g
  Veloc. descida:      {melhor["v0"]:.2f} m/s ({melhor["v0"] * 3.6:.1f} km/h)
  Veloc. rotação:      {melhor["omega"]:.1f} rad/s ({melhor["freq"]:.1f} Hz)
  Energia impacto:     {melhor["E"]:.2f} J
  Tempo queda 1000m:   {melhor["tempo"]:.1f} min
  Cabe no envelope:    Sim

  DIMENSÕES DA ASA:
    Raio:              {melhor["R"] * 100:.0f} cm
    Corda máxima:      ~{melhor["R"] * 100 * 2.5:.0f} mm (estimada)
    Espessura:         0.6 mm
    Material:          TPU 95A
    Massa por asa:     {melhor["m"] * 1000 / melhor["n"] - 350:.1f} g
""")

    # Verificar se atende critérios
    print(f"  CRITÉRIOS DE ACEITAÇÃO:")
    print(
        f"    v₀ < 5.5 m/s:      {'✓' if melhor['v0'] < 5.5 else '✗'} ({melhor['v0']:.2f} m/s)"
    )
    print(
        f"    E < 5 J:           {'✓' if melhor['E'] < 5 else '✗'} ({melhor['E']:.2f} J)"
    )
    print(
        f"    Freq < 15 Hz:      {'✓' if melhor['freq'] < 15 else '✗'} ({melhor['freq']:.1f} Hz)"
    )
    print(f"    Cabe no envelope:  {'✓' if melhor['cabe'] else '✗'}")
else:
    print("\n  Nenhuma configuração cabe no envelope 5x5x5cm!")

# === SENSIBILIDADE À MASSA ===
print(f"\n{'=' * 90}")
print("ANÁLISE DE SENSIBILIDADE - EFEITO DA MASSA DO SATÉLITE")
print(f"{'=' * 90}")

if configs_viaveis:
    melhor_R = melhor["R"]
    melhor_n = melhor["n"]

    print(f"\n  Configuração fixa: {melhor_n} asa(s) R={melhor_R * 100:.0f}cm")
    print(f"\n  {'Massa (g)':>10} │ {'v₀ (m/s)':>10} │ {'E (J)':>8} │ {'Status':<12}")
    print(f"  {'─' * 50}")

    for m_g in [250, 280, 300, 320, 350, 380, 400, 450, 500]:
        m_kg = m_g / 1000
        v0 = v_terminal_samara(m_kg, melhor_R, melhor_n)
        E = energia_impacto(m_kg, v0)
        classificacao, simbolo = classificar(v0, E)
        print(f"  {m_g:>9} │ {v0:>9.2f} │ {E:>7.1f} │ {simbolo} {classificacao:<9}")

# === RECOMENDAÇÕES ===
print(f"\n{'=' * 90}")
print("RECOMENDAÇÕES FINAIS")
print(f"{'=' * 90}")

print(f"""
  1. CONFIGURAÇÃO RECOMENDADA
     ┌────────────────────────────────────────────────────────┐
     │  {melhor["n"]} asa(s) de TPU 95A                                 │
     │  Raio: {melhor["R"] * 100:.0f} cm                                         │
     │  Espessura: 0.6 mm                                     │
     │  Formato: samara (corda variável, máximo em 30% R)    │
     │  Esperado: v₀ ≈ {melhor["v0"]:.1f} m/s, E ≈ {melhor["E"]:.1f} J                  │
     └────────────────────────────────────────────────────────┘

  2. GEOMETRIA DA ASA (FORMATO SAMARA)
     
        ╭────────────────╮
       ╱                  ╲
      │    Máxima corda    │  ← Ponto mais largo (~30% do raio)
      │      aqui          │
       ╲                  ╱
        ╰──────┬─────────╯
               │ ← Raio R = {melhor["R"] * 100:.0f}cm
               │
            [CORPO]
     
     - Perfil aerodinâmico assimétrico (côncavo no lado de baixo)
     - Superfície texturizada (TPU impresso) para turbulência controlada
     - Borda de ataque arredondada, borda de fuga afilada

  3. MECANISMO DE LIBERAÇÃO
     - Dobragem: {melhor["n"]} asa(s) dobrada(s) em zigzag
     - Espaço necessário: ~{melhor["R"] * 50 / melhor["n"]:.0f}mm por asa dobrada
     - Liberação: mola + trava solenóide ou SMA
     - Trigger: acelerômetro detecta queda livre (0g por >0.5s)

  4. TESTES RECOMENDADOS
     a) Prototipar asa em TPU (impressão FDM, layer 0.2mm)
     b) Teste de queda de 3m (mesa) - medir com câmera lenta
     c) Teste de queda de 10m (escada) - validar modelo
     d) Teste de queda de 30m (prédio) - confirmar v₀ estável
     e) Medir frequência de rotação real vs prevista

  5. OTIMIZAÇÕES FUTURAS
     - Aumentar área da asa se massa diminuir (<300g)
     - Testar TPU mais macio (Shore 85A) para flexão controlada
     - Adicionar texturas na superfície (micro-ranhuras)
     - Explorar asa com torção (twist) para autorrotação mais estável
""")

print("=" * 90)
