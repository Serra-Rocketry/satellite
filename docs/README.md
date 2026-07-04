# Documentacao do Projeto

Diretorio central para documentacao de arquitetura, processo e operacao.

## Objetivo

Organizar referencias de engenharia para desenvolvimento, testes e validacao
da missao Helike (#213 - LASC 2026) — Serra Rocketry.

## Estrutura

- `docs/software.md`: arquitetura de firmware, modulos, build, uso de recursos.
- `docs/firmware.md`: documentacao detalhada de cada modulo (sensores, comunicacao, dados).
- `docs/hardware.md`: especificacoes de hardware, pinagem, componentes.
- `docs/flowchart.md`: fluxos operacionais, de dados e de desenvolvimento.
- `docs/adr/`: registros de decisoes arquiteturais (ADR).

## Relacao com outros diretorios

- Testes unitarios nativos (Unity): `test/`.
- Testes de hardware e guias praticos: `test_hardware/`.
- Modulos de calculo reutilizaveis: `lib/calc/`.
- Estudos de asa autorrotativa SRAB: `extras/wing-analysis/` (teoria, resultados, scripts, proposta LASC em `extras/wing-analysis/docs/`).
- Arquivos de hardware e BOM: `hardware/`.

## Convencoes

- Preferir Markdown simples e objetivo.
- Registrar contexto, decisao e impacto em mudancas tecnicas.
- Manter links relativos para navegacao local no repositorio.
- Documentacao de codigo C/C++: Doxygen comments nos headers.
