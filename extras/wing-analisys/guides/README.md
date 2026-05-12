# Wing Analysis (Helike / SRAB)

Estudo de asa autorrotativa para PocketQube 1P — modelagem aerodinâmica,
comparação de geometrias DXF, simulação e rastreabilidade técnica.

```
extras/wing-analisys/
├── src/                              # Código-fonte
│   └── samara_pq_simulation.py       # Pipeline de simulação
├── geometry/                         # Geometrias de entrada (DXF)
│   ├── asa1.dxf                      # Design original (Test #1)
│   └── Asa2.DXF                      # Design otimizado (Test #2)
├── results/                          # Saídas das simulações
│   ├── test_1_asa1/                  # Artefatos do Test #1
│   ├── test_2_asa2/                  # Artefatos do Test #2
│   ├── samara_pq_impact_report.json
│   ├── samara_pq_impact_report.txt
│   ├── samara_pq_lrr_report.png
│   └── samara_pq_frontal_area.png
├── docs/                             # Documentação técnica
│   ├── analise-simulacao-helike.md
│   ├── helike-historico-testes.md
│   ├── helike-quick-reference.md
│   ├── plano-instrumentacao-helike-test3.md
│   ├── proposta-tecnica-srab-lasc.md
│   ├── srab-conceitos-fundamentais.md
│   └── technical-proposal-srab-lasc-en.tex
├── guides/                           # Guias de uso
│   ├── README.md                     ← este arquivo
│   ├── quickstart.md
│   ├── usage_manual.md
│   └── script_considerations.md
└── requirements.txt
```

## Início rápido

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r extras/wing-analisys/requirements.txt
python extras/wing-analisys/src/samara_pq_simulation.py
```

Saídas em `extras/wing-analisys/results/`.

## Como navegar

| Documento | Conteúdo |
|-----------|----------|
| `docs/helike-historico-testes.md` | Contexto geral dos testes |
| `docs/analise-simulacao-helike.md` | Comparação test 1 vs test 2 |
| `docs/srab-conceitos-fundamentais.md` | Base teórica SRAB |
| `docs/plano-instrumentacao-helike-test3.md` | Plano do test #3 instrumentado |
| `docs/helike-quick-reference.md` | Checklist operacional |
| `docs/proposta-tecnica-srab-lasc.md` | Proposta LASC (PT-BR) |
| `guides/quickstart.md` | Comandos prontos |
| `guides/usage_manual.md` | Manual de uso completo |
| `guides/script_considerations.md` | Notas sobre o script |

## Dados de referência

| Métrica | test_1_asa1 | test_2_asa2 | Delta |
|---|---:|---:|---:|
| Tempo até impacto | 97.33 s | 100.02 s | +2.69 s |
| Velocidade de impacto | 10.33 m/s | 10.05 m/s | -2.7% |
| Energia de impacto | 13.33 J | 12.62 J | -5.4% |
| Rotação final | 444.86 rpm | 439.08 rpm | -1.3% |
| Reynolds médio | 13,246 | 18,270 | +37.9% |

Fonte: `results/test_1_asa1/` e `results/test_2_asa2/`.

## Convenções

- Linux diferencia maiúsculas/minúsculas: `geometry/Asa2.DXF` ≠ `geometry/asa2.dxf`
- Para comparar cenários, manter fixos `t_span`, `max_step`, `dxf_path` e parâmetros aerodinâmicos
- Mudar apenas uma variável por vez (`radius_scale`, `n_wings` ou geometria)

## Fluxo para novo estudo

1. Adicionar DXF em `geometry/`
2. Rodar simulação: `python extras/wing-analisys/src/samara_pq_simulation.py`
3. Mover artefatos para `results/test_N_nome/`
4. Atualizar documentos de comparação
