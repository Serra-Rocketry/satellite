# Wing Analysis (Helike / SRAB)

Repositorio de estudo de asa autorrotativa para PocketQube 1P, com foco em:

- modelagem aerodinamica reduzida (Samara PQ);
- comparacao de geometrias DXF (testes reais e simulados);
- rastreabilidade tecnica para validacao em campanha de voo.

## Objetivo do diretorio

Este diretorio centraliza o pacote tecnico do estudo de asa:

- codigo de simulacao;
- geometrias de entrada;
- relatorios e figuras de saida;
- documentos tecnicos (conceitos, plano de testes e proposta).

## Estrutura

```text
extras/wing-analisys/
|-- README.md
|-- samara_pq_simulation.py
|-- samara_pq_quickstart.md
|-- samara_pq_usage_manual.md
|-- samara_pq_script_considerations.md
|-- asa1.dxf
|-- Asa2.DXF
|-- test_1_asa1/
|   |-- samara_pq_impact_report.json
|   |-- samara_pq_impact_report.txt
|   |-- samara_pq_lrr_report.png
|   `-- samara_pq_frontal_area.png
|-- test_2_asa2/
|   |-- samara_pq_impact_report.json
|   |-- samara_pq_impact_report.txt
|   |-- samara_pq_lrr_report.png
|   `-- samara_pq_frontal_area.png
|-- 2026-04-17-helike-historico-testes.md
|-- 2026-04-17-analise-simulacao-helike.md
|-- 2026-04-17-srab-conceitos-fundamentais.md
|-- 2026-04-17-plano-instrumentacao-helike-test3.md
|-- 2026-04-17-helike-quick-reference.md
|-- 2026-04-17-proposta-tecnica-srab-lasc.md
`-- 2026-04-17-technical-proposal-srab-lasc-en.tex
```

## Inicio rapido

1. Criar/ativar ambiente Python na raiz do projeto.
2. Instalar dependencias do simulador.
3. Executar pipeline principal.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy scipy matplotlib ezdxf
python extras/wing-analisys/samara_pq_simulation.py
```

Saidas padrao geradas em `extras/wing-analisys/`:

- `samara_pq_impact_report.json`
- `samara_pq_impact_report.txt`
- `samara_pq_lrr_report.png`
- `samara_pq_frontal_area.png`

## Como navegar na documentacao

- **Contexto geral dos testes**:
  `2026-04-17-helike-historico-testes.md`
- **Comparacao tecnica test 1 vs test 2**:
  `2026-04-17-analise-simulacao-helike.md`
- **Base teorica SRAB (com equacoes)**:
  `2026-04-17-srab-conceitos-fundamentais.md`
- **Plano instrumentado do test #3**:
  `2026-04-17-plano-instrumentacao-helike-test3.md`
- **Checklist operacional rapido**:
  `2026-04-17-helike-quick-reference.md`
- **Proposta formal LASC (PT-BR)**:
  `2026-04-17-proposta-tecnica-srab-lasc.md`
- **Proposta formal LASC (EN, LaTeX)**:
  `2026-04-17-technical-proposal-srab-lasc-en.tex`

## Dados de referencia atuais

Comparacao consolidada (simulacao) entre geometrias:

| Metrica | test_1_asa1 | test_2_asa2 | Delta |
|---|---:|---:|---:|
| Tempo ate impacto | 97.33 s | 100.02 s | +2.69 s |
| Velocidade de impacto | 10.33 m/s | 10.05 m/s | -2.7% |
| Energia de impacto | 13.33 J | 12.62 J | -5.4% |
| Rotacao final | 444.86 rpm | 439.08 rpm | -1.3% |
| Reynolds medio | 13,246 | 18,270 | +37.9% |

Fonte: `test_1_asa1/samara_pq_impact_report.txt` e
`test_2_asa2/samara_pq_impact_report.txt`.

## Convencoes

- Sistema de arquivos em Linux diferencia maiusculas e minusculas:
  `Asa2.DXF` e `asa2.dxf` nao sao o mesmo arquivo.
- Para comparacoes justas, manter fixos:
  `t_span`, `max_step`, `dxf_path` e parametros aerodinamicos.
- Mudar apenas uma variavel por vez (`radius_scale`, `n_wings` ou geometria).

## Fluxo recomendado para novo estudo

1. Duplicar um DXF base e versionar o novo arquivo.
2. Rodar simulacao com parametros fixos (baseline).
3. Gerar relatorios JSON/TXT e figuras.
4. Salvar artefatos em subpasta dedicada (`test_N_nome/`).
5. Atualizar documentos de comparacao e plano de validacao.

## Pendencias tecnicas conhecidas

- O modelo dinamico atual e reduzido (nao 6DOF completo).
- Validacao quantitativa depende de campanha instrumentada (test #3).
- Qualquer novo teste deve registrar: DXF, `n_wings`, `radius_scale`, `t_span`, `max_step`.
