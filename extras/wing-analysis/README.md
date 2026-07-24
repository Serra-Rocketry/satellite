# Helike #213 — SRAB Deploy Simulation

Modelagem e simulação do sistema de recuperação SRAB (Samara Recovery
System) para o PocketQube Helike #213 — LASC 2026.

## Notebook principal

[`notebooks/01_simulacao_deploy_srab.ipynb`](notebooks/01_simulacao_deploy_srab.ipynb)
— Pipeline completo de simulação:

| Fase | Veículo | Método |
|------|---------|--------|
| Stage 1 | Foguete completo | RocketPy `Flight` (subida até apogeu) |
| Stage 2 | Foguete vazio | RocketPy `Flight` + `initial_solution` (descida c/ paraquedas) |
| Stage 3 | PocketQube (payload) | `SRABRecovery.simulate_from_flight()` (descida SRAB) |

## Estrutura

```
wing-analysis/
├── notebooks/
│   └── 01_simulacao_deploy_srab.ipynb   ← Notebook principal (único)
├── src/
│   ├── samara_pq_simulation.py           ← Módulo de simulação SRAB
│   ├── rocketpy_samara/
│   │   ├── srab_recovery.py              ← Recuperação SRAB
│   │   └── plotting.py                   ← Plotagem LRR
│   └── ...
├── geometry/
│   └── Asa3.DXF                          ← Geometria da asa SRAB
├── docs/
│   ├── readme-explicativo.md
│   └── ...
└── data/                                 ← Dados de motor, etc.
```

## Requisitos

- Python 3.10+
- `rocketpy` (>= 1.x)
- `numpy`, `matplotlib`, `scipy`, `folium`

## Execução

```bash
cd notebooks/
jupyter notebook 01_simulacao_deploy_srab.ipynb
```

Ou via nbconvert:

```bash
jupyter nbconvert --to notebook --execute \
  notebooks/01_simulacao_deploy_srab.ipynb \
  --output executed.ipynb
```

## Parâmetros principais

- **Target velocidade**: 20 m/s ÷ SF 1.5 = **13.33 m/s** (SF sobre limite estrutural/LASC)
- **Raio otimizado**: **7.88 cm** (ala Asa3.DXF, 2 asas, β=5°)
- **Paraquedas foguete**: Main (cd_s=7.2) acionado no apogeu (drogue removido)
- **Atmosfera**: GFS forecast (vento real do modelo)
- **Motor**: Cesaroni Pro75 M1670 (placeholder — Calisto)
