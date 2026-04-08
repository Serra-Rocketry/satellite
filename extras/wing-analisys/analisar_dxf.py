# -*- coding: utf-8 -*-
"""Análise de asas a partir de arquivo DXF

Extrai geometria de um DXF e roda simulações de descida.
Processo reverso de gerar_dxf_asa.py
"""

import ezdxf
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from scipy.interpolate import interp1d


def extrair_contorno_dxf(caminho_dxf):
    """Extrai contorno (polilinha, spline ou linhas) do DXF.

    Interpola splines em alta resolução para obter contorno suave.

    Returns:
        pontos: lista de (x, y) do contorno
    """
    doc = ezdxf.readfile(caminho_dxf)
    msp = doc.modelspace()

    pontos = []

    # Procurar por polylines ou lwpolylines
    for entity in msp.query("LWPOLYLINE"):
        pontos = list(entity.get_points())
        print(f"  Encontrado LWPOLYLINE: {len(pontos)} pontos")
        return pontos

    for entity in msp.query("POLYLINE"):
        pontos = [(pt[0], pt[1]) for pt in entity.points()]
        print(f"  Encontrado POLYLINE: {len(pontos)} pontos")
        return pontos

    # Procurar por splines e interpolar
    splines = list(msp.query("SPLINE"))
    if splines:
        print(f"  Encontradas {len(splines)} SPLINE(s), interpolando...")

        try:
            from scipy.interpolate import splprep, splev

            for i, spline in enumerate(splines):
                try:
                    # Obter control points das splines
                    cpts = np.array(list(spline.control_points))[:, :2]  # Apenas X, Y

                    if len(cpts) < 3:
                        print(f"    ⚠ SPLINE {i}: muito poucos pontos ({len(cpts)})")
                        continue

                    # Usar splprep para interpolar a spline
                    # s=0 significa passar exatamente pelos pontos (smoothing spline)
                    try:
                        tck, u = splprep(
                            cpts.T, s=None, k=min(3, len(cpts) - 1), per=False
                        )

                        # Gerar muitos pontos interpolados
                        u_interp = np.linspace(0, 1, max(100, len(cpts) * 10))
                        pontos_interp = splev(u_interp, tck)

                        # Converter de volta para lista de tuplas
                        pontos_spline = list(zip(pontos_interp[0], pontos_interp[1]))
                        print(
                            f"    SPLINE {i}: {len(cpts)} control points → {len(pontos_spline)} interpolados"
                        )
                        pontos.extend(pontos_spline)
                    except Exception as e:
                        print(f"    ⚠ Erro interpolando SPLINE {i}: {e}")
                        # Fallback: usar control points diretos
                        pontos_spline = [(pt[0], pt[1]) for pt in cpts]
                        pontos.extend(pontos_spline)

                except Exception as e:
                    print(f"    ⚠ Erro ao extrair SPLINE {i}: {e}")

        except ImportError:
            print("    ⚠ scipy não disponível, usando control points diretos")
            for i, spline in enumerate(splines):
                cpts = list(spline.control_points)
                pontos_spline = [(pt[0], pt[1]) for pt in cpts]
                print(f"    SPLINE {i}: {len(pontos_spline)} control points")
                pontos.extend(pontos_spline)

        if pontos:
            print(f"  ✓ Total: {len(pontos)} pontos (splines interpoladas)")

    # Se ainda não achou, procurar por linhas individuais
    if not pontos:
        print("  ⚠ Procurando por linhas...")
        linhas = []
        for entity in msp.query("LINE"):
            p1 = (entity.dxf.start[0], entity.dxf.start[1])
            p2 = (entity.dxf.end[0], entity.dxf.end[1])
            linhas.append((p1, p2))

        if linhas:
            print(f"  Encontradas {len(linhas)} linhas, conectando...")
            pontos = conectar_linhas(linhas)

    return pontos


def conectar_linhas(linhas):
    """Conecta linhas desconexas em ordem."""
    if not linhas:
        return []

    pontos = [linhas[0][0]]
    usadas = {0}

    while len(usadas) < len(linhas):
        atual = pontos[-1]
        encontrou = False

        for i, (p1, p2) in enumerate(linhas):
            if i in usadas:
                continue

            dist1 = np.sqrt((atual[0] - p1[0]) ** 2 + (atual[1] - p1[1]) ** 2)
            dist2 = np.sqrt((atual[0] - p2[0]) ** 2 + (atual[1] - p2[1]) ** 2)

            if dist1 < dist2:
                if dist1 < 1e-3:  # Tolerância
                    pontos.append(p2)
                    usadas.add(i)
                    encontrou = True
                    break
            else:
                if dist2 < 1e-3:
                    pontos.append(p1)
                    usadas.add(i)
                    encontrou = True
                    break

        if not encontrou:
            break

    return pontos


def analisar_geometria_asa(pontos):
    """Analisa contorno para extrair raio e distribuição de corda.

    Calcula área usando Polygon (Shoelace formula) para maior precisão.

    Returns:
        dict com R, corda_func, estatísticas
    """
    if not pontos:
        raise ValueError("Nenhum ponto no contorno")

    try:
        from shapely.geometry import Polygon

        usar_shapely = True
    except ImportError:
        usar_shapely = False
        print("  ⚠ shapely não disponível, usando integração numérica")

    pts_array = np.array(pontos)
    x_coords = pts_array[:, 0]
    y_coords = pts_array[:, 1]

    # Encontrar raio máximo
    R = np.max(x_coords)
    x_min = np.min(x_coords)

    print(f"\n📐 Geometria extraída:")
    print(f"  X (raio): {x_min:.2f} a {R:.2f} mm")
    print(f"  Y: {np.min(y_coords):.2f} a {np.max(y_coords):.2f} mm")

    # Calcular área real do contorno
    if usar_shapely:
        # Fechar contorno se necessário
        pontos_fechados = list(pontos)
        if pontos_fechados[0] != pontos_fechados[-1]:
            pontos_fechados.append(pontos_fechados[0])

        poly = Polygon(pontos_fechados)
        area_mm2 = poly.area
        area_real_cm2 = area_mm2 / 100
    else:
        # Fallback: shoelace formula manualmente
        area_mm2 = 0
        for i in range(len(pontos) - 1):
            area_mm2 += (
                pontos[i][0] * pontos[i + 1][1] - pontos[i + 1][0] * pontos[i][1]
            )
        area_mm2 = abs(area_mm2) / 2
        area_real_cm2 = area_mm2 / 100

    print(f"  Área do contorno: {area_real_cm2:.2f} cm² ({area_mm2:.0f} mm²)")

    # Separar lado superior e inferior para corda
    # Ordenar por X para reconstruir perfil
    indices_sorted = np.argsort(x_coords)
    x_sorted = x_coords[indices_sorted]
    y_sorted = y_coords[indices_sorted]

    # Detectar mudança de direção em X para separar lados
    dx = np.diff(x_sorted)
    mudanca_idx = np.where(dx < 0)[0]

    if len(mudanca_idx) > 0:
        # Contorno vai e volta (típico de uma asa)
        ponto_mudanca = mudanca_idx[0]

        x_ida = x_sorted[: ponto_mudanca + 1]
        y_ida = y_sorted[: ponto_mudanca + 1]

        x_volta = x_sorted[ponto_mudanca:]
        y_volta = y_sorted[ponto_mudanca:]
    else:
        # Contorno monótono em X - assumir simetria
        x_ida = x_sorted
        y_ida = y_sorted
        x_volta = x_sorted[::-1]
        y_volta = -y_sorted[::-1]

    # Interpolar corda em função de r
    x_comum = np.linspace(0, R, 200)

    try:
        f_ida = interp1d(x_ida, np.abs(y_ida), kind="linear", fill_value="extrapolate")
        y_ida_interp = f_ida(x_comum)
    except:
        y_ida_interp = np.zeros_like(x_comum)

    try:
        f_volta = interp1d(
            x_volta, np.abs(y_volta), kind="linear", fill_value="extrapolate"
        )
        y_volta_interp = f_volta(x_comum)
    except:
        y_volta_interp = np.zeros_like(x_comum)

    # Corda total = soma dos dois lados
    corda_total = y_ida_interp + y_volta_interp
    corda_total = np.clip(corda_total, 0, None)

    # Criar função interpoladora
    def corda_func(r):
        """Corda em função do raio r (em mm)."""
        if np.isscalar(r):
            if r <= 0 or r >= R:
                return 0.0
            idx = int((r / R) * (len(x_comum) - 1))
            return corda_total[idx]
        else:
            resultado = np.zeros_like(r, dtype=float)
            for i, r_val in enumerate(r):
                if 0 < r_val < R:
                    idx = int((r_val / R) * (len(x_comum) - 1))
                    resultado[i] = corda_total[idx]
            return resultado

    # Estatísticas
    corda_max = np.max(corda_total)
    r_corda_max = x_comum[np.argmax(corda_total)]

    stats = {
        "R_mm": float(R),
        "corda_max_mm": float(corda_max),
        "r_corda_max_mm": float(r_corda_max),
        "area_real_cm2": float(area_real_cm2),
        "num_pontos_contorno": len(pontos),
    }

    return {
        "R": R,
        "corda_func": corda_func,
        "x_comum": x_comum,
        "corda_total": corda_total,
        "stats": stats,
        "pontos_originais": pontos,
    }


def simular_descida(R, corda_func, area_real_cm2, masa_pq_kg=0.450, configs=None):
    """Simula descida com múltiplas configurações.

    Usa fórmula aerodinâmica correta: v = √(2*m*g / (ρ*Cd*A))

    Args:
        R: raio em mm
        corda_func: função corda(r) em mm
        area_real_cm2: área real da asa em cm² (extraída do DXF via Shapely)
        masa_pq_kg: massa do pocketqube em kg
        configs: lista de (num_asas, raio_config_mm) ou None para auto

    Returns:
        lista de resultados por configuração
    """

    # Constantes físicas
    g = 9.81  # m/s²
    rho_ar = 1.225  # kg/m³ (ar ao nível do mar)
    rho_tpu = 1200  # kg/m³ (material das asas)
    espessura = 0.6e-3  # m (6/10 mm)

    # Coeficiente de arrasto (para asa retangular/elíptica em descida)
    # Cd ≈ 1.0-1.3 para superfícies planas
    # Usaremos 1.1 como valor intermediário realista
    Cd = 1.1

    # Converter área real de cm² para m²
    area_asa_m2 = area_real_cm2 * 1e-4

    def massa_asas(R_config, n):
        """Calcula massa das asas em kg.

        Usa a área real extraída do DXF, escalada proporcionalmente
        se o raio for diferente de R.
        """
        # Se raio é diferente, escalar área proporcionalmente
        # Área ∝ R² para geometria similar
        escala_raio = (R_config / R) ** 2
        area_escalada_m2 = area_asa_m2 * escala_raio

        # Massa = ρ * volume = ρ * área * espessura
        return n * area_escalada_m2 * espessura * rho_tpu

    def v_terminal_aerodinamica(m_total, n):
        """Velocidade terminal usando fórmula aerodinâmica correta.

        v = √(2*m*g / (ρ*Cd*A*n))

        Onde:
        - m_total: massa total do objeto (PocketQube + asas)
        - n: número de asas
        - A: área de cada asa
        - Cd: coeficiente de arrasto
        - ρ: densidade do ar
        - g: gravidade

        A arrasto total = n * Cd * A (n asas em paralelo)
        """
        # Área total de arrasto (todas as asas)
        area_total_m2 = n * area_asa_m2

        # v² = 2*m*g / (ρ*Cd*A_total)
        v_sqr = (2 * m_total * g) / (rho_ar * Cd * area_total_m2)
        v = np.sqrt(v_sqr)

        # Clamp apenas ao mínimo (sem asas deveria cair rápido)
        # Máximo depende da aplicação real
        return np.clip(v, 0.5, None)

    def energia_impacto(m, v):
        """Energia de impacto em Joules."""
        return 0.5 * m * v**2

    def velocidade_rotacao(R_config, v0):
        """RPM de rotação."""
        omega = v0 / (0.065 * R_config * 1e-3)
        return np.minimum(omega, 120)

    if configs is None:
        # Auto-gerar configurações razoáveis
        configs = []
        for n_asas in [2, 3, 4, 6]:
            configs.append((n_asas, R))
            if R > 100:
                configs.append((n_asas, R * 0.8))
            if R < 100:
                configs.append((n_asas, R * 1.2))

    resultados = []

    print(f"\n🔬 Simulações de descida (m_pq = {masa_pq_kg * 1000:.0f}g):")
    print(
        f"{'Config':<15} | {'v₀ (m/s)':>8} | {'E (J)':>7} | {'ω (RPM)':>8} | {'m_total (g)':>10}"
    )
    print("-" * 70)

    for n_asas, R_config in configs:
        try:
            m_asas = massa_asas(R_config, n_asas)
            m_total = masa_pq_kg + m_asas

            # Verificar se cabe dobrado (simplicidade)
            espaco_min = R_config * 1e-3 / n_asas
            cabe = espaco_min <= 0.05

            v0 = v_terminal_aerodinamica(m_total, n_asas)
            E = energia_impacto(m_total, v0)
            omega = velocidade_rotacao(R_config, v0)

            config_str = f"{n_asas}×R{R_config:.0f}mm"
            status = "✓" if cabe else "✗"

            print(
                f"{config_str:<15} | {v0:>8.2f} | {E:>7.1f} | {omega:>8.0f} | {m_total * 1000:>10.0f}"
            )

            resultados.append(
                {
                    "n_asas": n_asas,
                    "R_mm": R_config,
                    "m_asas_g": m_asas * 1000,
                    "m_total_g": m_total * 1000,
                    "v_terminal_ms": v0,
                    "energia_J": E,
                    "rpm": omega,
                    "cabe_dobrado": cabe,
                }
            )
        except Exception as e:
            print(f"  ⚠ Erro em config {n_asas}×R{R_config}mm: {e}")

    return resultados


def gerar_relatorio(caminho_dxf, geom, resultados, output_dir=None):
    """Gera relatório em texto e JSON."""

    if output_dir is None:
        output_dir = Path(caminho_dxf).parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    # Nome do arquivo de saída
    nome_base = Path(caminho_dxf).stem

    # Arquivo JSON com resultados
    json_path = output_dir / f"{nome_base}_analise.json"

    # Converter tipos especiais para JSON
    resultados_json = []
    for res in resultados:
        res_copy = dict(res)
        res_copy["cabe_dobrado"] = bool(
            res_copy["cabe_dobrado"]
        )  # Converter numpy bool
        resultados_json.append(res_copy)

    json_data = {
        "arquivo_dxf": str(caminho_dxf),
        "geometria": geom["stats"],
        "simulacoes": resultados_json,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 JSON salvo: {json_path}")

    # Arquivo de texto com relatório
    txt_path = output_dir / f"{nome_base}_relatorio.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"ANÁLISE DE ASA - {Path(caminho_dxf).name}\n")
        f.write("=" * 80 + "\n\n")

        f.write("📐 GEOMETRIA\n")
        f.write("-" * 80 + "\n")
        stats = geom["stats"]
        f.write(f"  Raio máximo (R):        {stats['R_mm']:.1f} mm\n")
        f.write(f"  Corda máxima:           {stats['corda_max_mm']:.1f} mm\n")
        f.write(
            f"  Posição corda máx:      {stats['r_corda_max_mm']:.1f} mm ({stats['r_corda_max_mm'] / stats['R_mm'] * 100:.0f}% do raio)\n"
        )
        f.write(f"  Área real do contorno:  {stats['area_real_cm2']:.2f} cm²\n")
        f.write(f"  Pontos no contorno:     {stats['num_pontos_contorno']}\n\n")

        f.write("🔬 SIMULAÇÕES DE DESCIDA\n")
        f.write("-" * 80 + "\n")
        f.write(
            f"{'Config':<20} | {'v₀ (m/s)':>8} | {'E (J)':>7} | {'ω (RPM)':>8} | {'m (g)':>9}\n"
        )
        f.write("-" * 80 + "\n")

        for res in resultados:
            config_str = f"{res['n_asas']}×R{res['R_mm']:.0f}mm"
            f.write(
                f"{config_str:<20} | {res['v_terminal_ms']:>8.2f} | {res['energia_J']:>7.1f} | {res['rpm']:>8.0f} | {res['m_total_g']:>9.0f}\n"
            )

        f.write("\n" + "=" * 80 + "\n")
        f.write("RECOMENDAÇÕES\n")
        f.write("=" * 80 + "\n")

        # Encontrar melhor config
        melhor = min(resultados, key=lambda x: x["v_terminal_ms"])
        f.write(f"\n✓ Configuração com menor v₀:\n")
        f.write(f"  {melhor['n_asas']}×R{melhor['R_mm']:.0f}mm\n")
        f.write(f"  v₀ = {melhor['v_terminal_ms']:.2f} m/s\n")
        f.write(f"  E = {melhor['energia_J']:.1f} J\n")
        f.write(f"  Cabe dobrado: {'Sim ✓' if melhor['cabe_dobrado'] else 'Não ✗'}\n")

    print(f"📄 Relatório salvo: {txt_path}")

    return json_path, txt_path


def plotar_geometria(geom, nome_asa="Asa", output_dir=None):
    """Plota geometria e corda da asa."""

    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Contorno original
    pts = np.array(geom["pontos_originais"])
    ax1.plot(pts[:, 0], pts[:, 1], "b-", linewidth=2, label="Contorno")
    ax1.fill(pts[:, 0], pts[:, 1], alpha=0.2)
    ax1.set_xlabel("Raio r (mm)")
    ax1.set_ylabel("Meia-corda y (mm)")
    ax1.set_title(f"{nome_asa} - Contorno do DXF")
    ax1.grid(True, alpha=0.3)
    ax1.axis("equal")
    ax1.legend()

    # Distribuição de corda
    x = geom["x_comum"]
    c = geom["corda_total"]
    ax2.plot(x, c, "r-", linewidth=2)
    ax2.fill_between(x, 0, c, alpha=0.3, color="red")
    ax2.set_xlabel("Raio r (mm)")
    ax2.set_ylabel("Corda (mm)")
    ax2.set_title(f"{nome_asa} - Distribuição de corda")
    ax2.grid(True, alpha=0.3)

    # Marcar corda máxima
    r_max = geom["stats"]["r_corda_max_mm"]
    c_max = geom["stats"]["corda_max_mm"]
    ax2.plot(
        r_max, c_max, "go", markersize=10, label=f"Max: {c_max:.1f}mm @ {r_max:.0f}mm"
    )
    ax2.legend()

    plt.tight_layout()

    output_path = output_dir / f"{nome_asa}_geometria.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"📊 Gráfico salvo: {output_path}")
    plt.close()


def main():
    """Script principal."""

    # Arquivo a analisar
    caminho_dxf = "extras/wing-analisys/Asa2.DXF"

    print("=" * 80)
    print("ANÁLISE DE ASA A PARTIR DE DXF")
    print("=" * 80)

    # Extrair contorno
    print(f"\n📂 Lendo: {caminho_dxf}")
    try:
        pontos = extrair_contorno_dxf(caminho_dxf)
        print(f"  ✓ Contorno extraído: {len(pontos)} pontos")
    except Exception as e:
        print(f"  ✗ Erro ao ler DXF: {e}")
        return

    # Analisar geometria
    print(f"\n🔬 Analisando geometria...")
    try:
        geom = analisar_geometria_asa(pontos)
        print(f"  ✓ Geometria analisada com sucesso")
    except Exception as e:
        print(f"  ✗ Erro na análise: {e}")
        return

    # Plotar
    nome_asa = Path(caminho_dxf).stem
    plotar_geometria(geom, nome_asa=nome_asa, output_dir=Path(caminho_dxf).parent)

    # Simular
    print(f"\n⚙️ Rodando simulações...")
    resultados = simular_descida(
        geom["R"],
        geom["corda_func"],
        geom["stats"]["area_real_cm2"],
        masa_pq_kg=0.450,
        configs=None,
    )

    # Gerar relatório
    print(f"\n📝 Gerando relatório...")
    gerar_relatorio(caminho_dxf, geom, resultados, output_dir=Path(caminho_dxf).parent)

    print("\n" + "=" * 80)
    print("✅ Análise concluída!")
    print("=" * 80)


if __name__ == "__main__":
    main()
