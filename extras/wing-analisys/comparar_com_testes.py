# -*- coding: utf-8 -*-
"""
Script para comparar resultados de simulação com dados de teste físico.

Este script facilita a validação da física comparando velocidades terminais
calculadas com medições de teste.

Uso:
    python comparar_com_testes.py
"""

import json
from pathlib import Path
import numpy as np


def comparar_simulacao_com_teste(arquivo_json, dados_teste):
    """Compara simulação com dados de teste.

    Args:
        arquivo_json: caminho para arquivo JSON de simulação (ex: Asa2_analise.json)
        dados_teste: dict com formato:
            {
                'config': '4×R124mm',  # deve corresponder a uma config na simulação
                'v_terminal_ms': 19.5,  # velocidade medida em m/s
                'notas': 'Teste em câmara de vento'
            }

    Returns:
        dict com análise de erro
    """

    # Carregar simulação
    with open(arquivo_json, "r") as f:
        sim_data = json.load(f)

    # Procurar configuração correspondente
    config_nome = dados_teste.get("config", "")
    v_teste = dados_teste.get("v_terminal_ms")

    if not v_teste:
        print("⚠ Erro: 'v_terminal_ms' não fornecido nos dados de teste")
        return None

    # Encontrar simulação correspondente
    resultado_sim = None
    for res in sim_data["simulacoes"]:
        config_str = f"{res['n_asas']}×R{res['R_mm']:.0f}mm"
        if config_str == config_nome or (
            res["n_asas"] == int(config_nome.split("×")[0])
            and res["R_mm"] == int(config_nome.split("R")[1].split("mm")[0])
        ):
            resultado_sim = res
            config_nome = config_str
            break

    if not resultado_sim:
        print(f"⚠ Configuração '{config_nome}' não encontrada na simulação")
        return None

    v_simulado = resultado_sim["v_terminal_ms"]

    # Calcular erros
    erro_abs = v_teste - v_simulado
    erro_pct = (erro_abs / v_simulado) * 100

    return {
        "config": config_nome,
        "v_simulado_ms": v_simulado,
        "v_teste_ms": v_teste,
        "erro_abs_ms": erro_abs,
        "erro_pct": erro_pct,
        "notas": dados_teste.get("notas", ""),
        "data_teste": dados_teste.get("data", "N/A"),
    }


def gerar_relatorio_comparacao(comparacoes):
    """Gera relatório com comparações de testes.

    Args:
        comparacoes: lista de dicts retornados por comparar_simulacao_com_teste()
    """

    if not comparacoes:
        print("Nenhuma comparação disponível")
        return

    print("\n" + "=" * 90)
    print("RELATÓRIO DE VALIDAÇÃO - SIMULAÇÃO vs TESTES FÍSICOS")
    print("=" * 90)
    print()
    print(
        f"{'Config':<15} | {'v_sim (m/s)':>12} | {'v_teste (m/s)':>14} | {'Erro':>10} | {'%':>7}"
    )
    print("-" * 90)

    erros_pct = []
    for comp in comparacoes:
        if comp is None:
            continue

        print(
            f"{comp['config']:<15} | "
            f"{comp['v_simulado_ms']:>12.2f} | "
            f"{comp['v_teste_ms']:>14.2f} | "
            f"{comp['erro_abs_ms']:>10.2f} | "
            f"{comp['erro_pct']:>6.1f}%"
        )
        erros_pct.append(abs(comp["erro_pct"]))

        if comp["notas"]:
            print(f"  Notas: {comp['notas']}")

    print()
    if erros_pct:
        print(f"Erro médio: {np.mean(erros_pct):.1f}%")
        print(f"Erro máximo: {np.max(erros_pct):.1f}%")
        print(f"Erro RMS: {np.sqrt(np.mean(np.array(erros_pct) ** 2)):.1f}%")
        print()

        # Análise
        if np.mean(erros_pct) < 5:
            print("✅ Simulação está bem calibrada!")
        elif np.mean(erros_pct) < 15:
            print("⚠️  Simulação está razoavelmente calibrada (revisar Cd ou área)")
        else:
            print("❌ Simulação precisa de recalibração significativa")


def exemplo_uso():
    """Mostra como usar este script."""

    print("""
    EXEMPLO DE USO:
    ===============
    
    1. Fazer testes físicos e medir velocidades terminais
    
    2. Criar lista de dados de teste:
    
        testes = [
            {
                'config': '4×R124mm',
                'v_terminal_ms': 20.5,
                'data': '2026-04-08',
                'notas': 'Teste em câmara de vento, temp 20°C'
            },
            {
                'config': '6×R124mm',
                'v_terminal_ms': 17.2,
                'data': '2026-04-08',
                'notas': 'Mesmo ambiente'
            },
        ]
    
    3. Rodar comparação:
    
        arquivo = 'extras/wing-analisys/Asa2_analise.json'
        comparacoes = [comparar_simulacao_com_teste(arquivo, t) for t in testes]
        gerar_relatorio_comparacao(comparacoes)
    
    """)


if __name__ == "__main__":
    # Exemplo de uso
    exemplo_uso()

    # Teste dummy (comentado)
    # arquivo_json = 'extras/wing-analisys/Asa2_analise.json'
    #
    # testes = [
    #     {
    #         'config': '4×R124mm',
    #         'v_terminal_ms': 21.0,  # Teste hipotético
    #         'notas': 'Teste de câmara de vento'
    #     },
    # ]
    #
    # comparacoes = [comparar_simulacao_com_teste(arquivo_json, t) for t in testes]
    # gerar_relatorio_comparacao(comparacoes)
