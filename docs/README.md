# Documentacao do Projeto

Diretorio central para documentacao de arquitetura, processo e operacao.

## Objetivo

Organizar referencias de engenharia para desenvolvimento, testes e validacao
da missao Helike (#213 - LASC 2026) — Serra Rocketry.

## Estrutura

- `docs/hardware.md`: especificacoes de hardware e interfaces.
- `docs/software.md`: arquitetura de firmware, modulos `lib/calc/`, fluxos de dados.
- `docs/flowchart.md`: fluxos operacionais e de estado.
- `docs/adr/`: registros de decisoes arquiteturais (ADR).

## Relacao com outros diretorios

- Testes unitarios nativos (Unity): `test/`.
- Testes de hardware e guias praticos: `test_hardware/`.
- Modulos de calculo reutilizaveis: `lib/calc/`.
- Estudos de asa e simulacao: `extras/wing-analisys/`.
- Arquivos de hardware e BOM: `hardware/`.

## Convencoes

- Preferir Markdown simples e objetivo.
- Registrar contexto, decisao e impacto em mudancas tecnicas.
- Manter links relativos para navegacao local no repositorio.
- Documentacao de codigo C/C++: Doxygen comments nos headers.
