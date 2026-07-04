# Proposta Tecnica SRAB v2 — Integracao RocketPy

**Notificacao obrigatoria para uso de metodo nao-paraquedas**
**Serra Rocketry — Missao Helike (#213 — LASC 2026)**

---

## Resumo

Esta revisao (v2) atualiza a proposta com integracao do simulador SRAB ao
framework **RocketPy** (v1.2+). A nova pipeline substitui densidade constante
por perfis atmosfericos reais (GFS/ISA), adiciona deriva por vento,
visualizacao 3D da trajetoria em mapas de satelite e analise de dispersao
Monte Carlo.

---

## Pipeline de Simulacao

```
RocketPy (subida do foguete)
    ↓ apogeu (altitude, velocidade, posicao)
SRABRecovery (descida autorrotativa)
    ├── EnvironmentAwareFlightDynamics (ρ(z) variavel)
    ├── Otimizacao de raio (opcional)
    └── Deriva por vento (modelo simplificado)
SRABSolution → graficos, relatorios, mapa
```

### Classes Principais

- `SRABSolution`: dataclass com trajetoria completa (t, θ, v0, altitude, x, y,
  t_impact, v_impact, spin, theta_eq, x_impact, y_impact)
- `EnvironmentAwareFlightDynamics`: estende PocketQubeFlightDynamics com
  densidade ρ(z) do ambiente RocketPy
- `SRABRecovery`: wrapper que conecta subida (RocketPy Flight) com descida
  SRAB; metodos `simulate()` e `simulate_from_flight(flight)`

### Monte Carlo com RocketPy

- `SRABMonteCarlo`: loop serial com parametros estocasticos
- `StochParam`: define distribuicoes (normal, uniform, discrete)
- Metricas: media, σ, P5, P95, CEP, LASC pass rate

### Visualizacoes

| Funcao | Descricao |
|---|---|
| `plot_ascent_descent_3d()` | Trajetoria 3D subida + descida |
| `plot_dispersion()` | Scatter de impactos + elipse CEP |
| `plot_lrr_dashboard()` | Relatorio LRR 2x2 |
| `plot_trajectory_map()` | Mapa interativo (folium + ESRI) |

---

## Resultados da Configuracao Candidata

Asa3.DXF, 2 asas, 200 g, β=8°, altitude 1000 m.

| Metrica | Valor |
|---|---|
| Velocidade de impacto | ~13 m/s (ajustavel por otimizacao de raio) |
| Tempo de descida | ~80 s |
| Conicidade θeq | ~17° |
| Rotacao | ~370 RPM |

Monte Carlo (200 iteracoes) com variacao de massa ±5%, β ±0,5°, CD0 ±15%,
n_wings {2,4}: CV < 2% na velocidade de impacto.

---

## Planos de Validacao

- **Teste 3 — Parte A**: simulacao computacional (OK, resultados neste doc)
- **Teste 3 — Parte B**: ensaio de campo instrumentado (trabalho futuro)
  - Criterios: erro < ±5% em velocidade, < ±3% em tempo de voo
  - Telemetria: ESP32-C3 + ICM-20602 + BMP280 + LoRa RFM95W a 20 Hz

---

## Referencias

- RocketPy Development Team. _RocketPy: Six-DOF Rocket Trajectory Simulation_. JOSS, 2024.
- LASC. _Satellite Challenge Standards Manual_. Ed. 7, Rev. 1. 2026.
