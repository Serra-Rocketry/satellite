# extras/

Estudos, simulações e ferramentas auxiliares.

```
extras/
├── wing-analysis/       # Estudo de asa autorrotativa SRAB — simulação, MC, telemetria
│   ├── src/             # Scripts Python (samara_pq_simulation, field_analysis, MC, benchmark)
│   ├── geometry/        # Perfis DXF (asa1.dxf, Asa2.DXF, Asa3.DXF, Asa4.DXF)
│   ├── docs/            # Documentação: teoria, resultados, proposta LASC, scripts
│   └── results/         # Saídas geradas (gráficos, relatórios, CSVs)
├── ...                  # Futuros: análise de logs SD, etc.
└── README.md
```

Cada subdiretório tem seu próprio README. Documentação completa do SRAB em
`wing-analysis/docs/`:
- `README.md` — índice da documentação
- `teoria.md` — fundamentos da autorrotação e modelo matemático
- `resultados.md` — resultados experimentais, MC, benchmark
- `proposta-lasc.md` — proposta técnica SRAB v2 com RocketPy
- `scripts.md` — referência rápida de todos os scripts
