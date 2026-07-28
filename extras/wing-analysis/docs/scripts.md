# Scripts — Referencia Rapida

Todos os scripts em `src/`, seus argumentos e saidas.

---

## Dependencias

| Script | Dependencias |
|---|---|
| `samara_pq_simulation.py` | numpy, scipy, matplotlib, ezdxf |
| `srab_field_analysis.py` | numpy, matplotlib |
| `monte_carlo_samara.py` | numpy + samara_pq_simulation |
| `benchmark_parachute.py` | numpy, scipy + samara_pq_simulation |
| `rocketpy_samara/` | + rocketpy (opcional), folium (opcional) |

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install numpy scipy matplotlib ezdxf
# opcional: pip install rocketpy folium
```

---

## 1. `samara_pq_simulation.py` — Pipeline Principal

Simulacao de descida autorrotativa SRAB. Le geometria de DXF, resolve EDOs
4ª ordem, gera relatorios e graficos.

### Classes

| Classe | Funcao |
|---|---|
| `DxfWingProfile` | Carrega perfil de asa de DXF |
| `PocketQubeSamaraWing` | Modelo geometrico e aerodinamico |
| `PocketQubeFlightDynamics` | EDOs: `simulate_drop()`, `calculate_steady_state()` |
| `PocketQubeLRRVisualizer` | Dashboard 2x2 LRR |
| `PocketQubeSamaraOptimizer` | Otimizacao de raio para v_alvo |
| `PocketQubeMissionReporter` | Relatorio JSON/TXT/CSV |
| `plot_wing_geometry_views()` | 3 vistas ortogonais |

### CLI

| Argumento | Default | Descricao |
|---|---|---|
| `--dxf` | `Asa2.DXF` | Arquivo DXF da asa |
| `--n-wings` | `2` | Numero de asas |
| `--mass` | `0.110` | Massa total [kg] |
| `--altitude` | `20.0` | Altitude de liberacao [m] |
| `--theta-deg` | `20.0` | Conicidade inicial [graus] |
| `--phi-dot` | `0.1` | Spin inicial [rad/s] |
| `--beta-deg` | `8.0` | Passo geometrico β [graus] |
| `--cd0` | `1.0` | Arrasto basal |
| `--f-factor` | `0.3` | Fracao de inercia nas asas |
| `--rho` | `1.225` | Densidade do ar [kg/m³] |
| `--t-max` | `600.0` | Tempo maximo de simulacao [s] |
| `--max-step` | `0.2` | Passo maximo do integrador [s] |
| `--output` | `results/` | Diretorio de saida |
| `--optimize` | — | Ativa otimizacao de raio |
| `--target-vf` | `-25.0` | Velocidade vertical alvo [m/s] |
| `--safety-factor` | `1.0` | Fator de seguranca |

### Exemplo

```bash
python src/samara_pq_simulation.py \
    --dxf geometry/asa1.dxf \
    --n-wings 4 --mass 0.200 --altitude 20 \
    --beta-deg 8 --cd0 1.0 --f-factor 0.3 \
    --rho 1.225 --t-max 600 --max-step 0.2
```

### Saidas

| Arquivo | Conteudo |
|---|---|
| `samara_pq_impact_report.json` | Metricas de impacto, geometria, energia |
| `samara_pq_impact_report.txt` | Relatorio textual |
| `samara_pq_trajectory.csv` | Trajetoria ponto a ponto |
| `samara_pq_lrr_report.png` | Dashboard 2x2 LRR |
| `samara_pq_geometry_views.png` | 3 vistas ortogonais |

---

## 2. `srab_field_analysis.py` — Analise de Telemetria

Analisa CSVs do firmware v2, detecta fases de voo (static→ascent→apogee→descent→landed).

```bash
python src/srab_field_analysis.py DADOS_020.csv --sim results/trajetoria.csv
```

Argumentos: `--sim`, `--out`, `--vz-source` (baro|imu), `--spin-axis` (mag|gz).

Colunas esperadas: `millis, ax_ms2, ay_ms2, az_ms2, gx_rads, gy_rads, gz_rads, pressao_Pa, altura_m, vz_ms, mag_giroscopia_rads`.

Saidas: `{stem}_dashboard.png`, `{stem}_report.json`.

---

## 3. `monte_carlo_samara.py` — Sensibilidade (Standalone)

Varia massa, β, CD0, f_factor, ρ com distribuicoes normais, N iteracoes.

```bash
python src/monte_carlo_samara.py --n 100 --seed 42
python src/monte_carlo_samara.py --mass-mean 0.200 --mass-std 0.010 --export results/mc.csv
```

Saida: terminal com media, σ, P5, P95, LASC pass rate; CSV opcional com todas as iteracoes.

---

## 4. `benchmark_parachute.py` — SRAB vs Paraquedas

Compara SRAB (Asa3, 4 asas) com paraquedas ∅200 mm, CD=1.5.

```bash
python src/benchmark_parachute.py
```

Saida: tabela comparativa no terminal (v_impacto, t_descida, KE, LASC).

---

## 5. `rocketpy_samara/` — Integracao RocketPy

### `srab_recovery.py`

Acoplamento subida (RocketPy) + descida SRAB.

```python
from rocketpy_samara.srab_recovery import SRABRecovery
rec = SRABRecovery(wing, env=None, ...)
sol = rec.simulate()                   # standalone
sol = rec.simulate_from_flight(flight) # apos RocketPy Flight
```

`SRABSolution`: t, theta, theta_dot, phi_dot, v0, altitude, x, y, t_impact, v_impact, spin_impact_rpm, theta_eq.

### `monte_carlo.py`

```python
mc = SRABMonteCarlo(recovery, n=200, seed=42)
mc.add_param("mass_kg", "normal", (0.200, 0.005))
mc.add_param("n_wings", "discrete", (2, 4))
mc.run(); mc.print_summary(); mc.export_csv("mc.csv")
```

### `plotting.py`

`plot_ascent_descent_3d()`, `plot_dispersion()`, `plot_lrr_dashboard()`, `plot_trajectory_map()`.

### Demos

```bash
python src/rocketpy_samara/demo_srab_recovery.py
python src/rocketpy_samara/demo_plotting.py
python src/rocketpy_samara/demo_monte_carlo.py
python src/rocketpy_samara/demo_env_rho.py
```

---

## Troubleshooting

| Problema | Solucao |
|---|---|
| DXF nao encontrado | Verificar maiusculas/minusculas (Linux) |
| `ezdxf` ausente | `pip install ezdxf` |
| Otimizacao vs relatorio diferente | Mesmo `max_step` e `t_span` |
| Impacto nao detectado | Aumentar `--t-max` ou reduzir `--max-step` |
| Energia nao fisica | KE final > potencial inicial |
