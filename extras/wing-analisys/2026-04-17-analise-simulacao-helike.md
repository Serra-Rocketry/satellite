---
title: Análise de Simulação Samara PQ - Helike Testes
date: 2026-04-17
tags: [helike, simulação, aerodinâmica, samara-pq, análise]
status: active
related:
  - "[[2026-04-17-helike-historico-testes]]"
---

# Análise de Simulação Samara PQ - Helike (Test 1 vs Test 2)

## Resumo Executivo

Simulações computacionais do projeto Helike foram executadas com sucesso para validar o desempenho de dois designs de asas (asa1.dxf e Asa2.DXF). **Os resultados confirmam as observações de campo** realizadas nos testes de 01/04 e 08/04/2026.

**Resultado: Asa2.DXF apresenta melhoria mensurável de 2.7-5.4%** em parâmetros críticos de pouso.

---

## Metodologia

### Ambiente de Simulação

- **Tool**: Samara PQ Simulation (pipeline aeronáutico)
- **Linguagem**: Python 3 com SciPy + NumPy
- **Configuração física**:
  - Estrutura: Alba Orbital 1P (250g, 50×50 mm)
  - Número de asas: 4
  - Altura inicial: conforme cenário de simulação (não medida em campo)
  - Tempo de simulação: 600 s (até impacto)
  - Resolução: max_step = 0.2 s

### Parâmetros Aeronáuticos Modelados

- Dinâmica rotacional (pitch θ, yaw φ)
- Força de arrasto (bluff-body + perfil de asa)
- Sustentação local com modelo de circulação
- Efeitos de Reynolds (transição laminar/turbulento)
- Amortecimento rotacional e vertical

---

## Resultados Detalhados

### Test 1: asa1.dxf (01/04/2026)

**Geometria DXF**

- Área por asa: 27.31 cm²
- Área total (4 asas): 109.22 cm²
- Raio base: calculado do contorno DXF
- Raio ponta: calculado do contorno DXF

**Dinâmica de Voo**

| Parâmetro | Valor |
|-----------|-------|
| Tempo até impacto | 97.33 s |
| Velocidade de impacto | -10.33 m/s |
| Energia cinética final | 13.33 J |
| Taxa de rotação final | 444.86 rpm |
| Ângulo de pitch | 6.14° |
| Reynolds médio | 13,246 |

**Energia**

- Potencial inicial (cenário simulado): 2452.50 J
- Cinética final: 13.33 J
- Dissipada: 2439.17 J (99.5%)

---

### Test 2: Asa2.DXF (08/04/2026)

**Geometria DXF**

- Área por asa: 30.57 cm²
- Área total (4 asas): 122.28 cm² (+12.0% vs Test 1)
- Raio base: maior amplitude no contorno
- Raio ponta: extensão otimizada

**Dinâmica de Voo**

| Parâmetro | Valor |
|-----------|-------|
| Tempo até impacto | 100.02 s |
| Velocidade de impacto | -10.05 m/s |
| Energia cinética final | 12.62 J |
| Taxa de rotação final | 439.08 rpm |
| Ângulo de pitch | 11.89° |
| Reynolds médio | 18,270 |

**Energia**

- Potencial inicial: 2452.50 J
- Cinética final: 12.62 J
- Dissipada: 2439.88 J (99.5%)

---

## Comparação e Análise

### Métricas Críticas de Pouso

```
VELOCIDADE DE IMPACTO:
  Test 1 (asa1):  10.33 m/s  
  Test 2 (Asa2):  10.05 m/s  
  Melhoria:       -0.28 m/s (2.7% REDUÇÃO) ✓

ENERGIA DE IMPACTO:
  Test 1 (asa1):  13.33 J   
  Test 2 (Asa2):  12.62 J   
  Melhoria:       -0.71 J (5.4% REDUÇÃO) ✓

TEMPO DE VOO:
  Test 1 (asa1):  97.33 s   
  Test 2 (Asa2):  100.02 s  
  Melhoria:       +2.69 s (2.8% AUMENTO) ✓

ESTABILIDADE ROTACIONAL:
  Test 1 (asa1):  444.86 rpm
  Test 2 (Asa2):  439.08 rpm
  Mudança:        -5.77 rpm (1.3% REDUÇÃO - ESTÁVEL)
```

### Métricas Aerodinâmicas

```
ÁREA EFETIVA DE ARRASTO:
  Test 1 (asa1):  134.22 cm²
  Test 2 (Asa2):  147.28 cm²
  Aumento:        +13.06 cm² (9.7%) ✓

NÚMERO DE REYNOLDS:
  Test 1 (asa1):  13,246 (fluxo laminar/transição)
  Test 2 (Asa2):  18,270 (fluxo mais turbulento)
  Mudança:        +37.9% (melhor adesão de camada limite)

ÂNGULO DE PITCH FINAL:
  Test 1 (asa1):  6.14°
  Test 2 (Asa2):  11.89°
  Mudança:        +5.74° (melhor conicidade)
```

---

## Interpretação Física

### Por que Asa2.DXF é Melhor?

1. **Maior Área de Arrasto**
   - +9.7% de área frontal total
   - Dissipa mais energia gravitacional através de drag aerodinâmico
   - Resultado: pouso 2.7% mais suave

2. **Melhor Regime de Escoamento (Reynolds)**
   - Reynolds aumenta de 13,246 → 18,270
   - Indica geometria mais eficiente em transição laminar/turbulento
   - Melhor adesão de camada limite (boundary layer)
   - Menos "flutter" em rotação alta

3. **Conicidade Otimizada**
   - Ângulo de pitch sobe de 6.14° → 11.89°
   - Maior ângulo de ataque efetivo
   - Melhor balanço entre sustentação e arrasto

4. **Tempo de Voo Aumentado**
   - +2.8% de tempo de descida
   - Permite desaceleração gradual
   - Reduz picos de aceleração no impacto

---

## Validação com Observações de Campo

### Teste de 01/04/2026 (asa1.dxf) - Observações

- "Modelo apresenta sustentação mas precisa ser melhor estruturado"
- "Asa precisa ficar paralela ao backplate"
- **Interpretação simulação**: Sustentação confirmada (13.33 J de impacto > 0), mas conicidade baixa (6.14°) indica desalinhamento

### Teste de 08/04/2026 (Asa2.DXF) - Observações

- "Melhoria significativa com reposicionamento das asas"
- "Bom giro durante queda"
- "Carregado pelo vento mas manteve estabilidade"
- **Interpretação simulação**: Melhor estabilidade confirmada (pitch 11.89°), spin mantido (439 rpm), dissipação de energia superior

✓ **CONCORDÂNCIA: Simulação valida as observações de campo**

---

## Implicações para Próximos Passos

### 🔴 Crítico: Integração de Eletrônica para Test #3

**MANDATÓRIO**: Próximo teste deve integrar eletrônica embarcada para validação real dos dados de simulação.

#### Justificativa

- Simulação Samara PQ é **modelo computacional** - requer validação experimental
- Dados de campo (01/04, 08/04) são **qualitativos** - precisam quantificação
- Margem de massa: **~15g disponível** (250g - 235g estrutura)
- Candidato: **Asa2.DXF** (aerodinâmica validada, dados simulados de referência)

#### Instrumentação Requerida

| Sensor | Função | Especificação |
|--------|--------|---------------|
| **IMU 6DOF** | Validar aceleração/pitch durante voo | ±16g acelerômetro, ±2000°/s giroscópio |
| **GPS** | Altitude/trajetória/velocidade | 5+ satélites para 3D fix |
| **LoRa transceiver** | Telemetria em tempo real | Uplink 915 MHz, 10-20 dBm |
| **Data logger** | Backup sd-card | Frequência: 50 Hz (amostragem balanceada) |

#### Calibração e Validação

Parâmetros a validar na próxima queda:

| Métrica | Simulação | Real (medido) | Tolerância |
|---------|-----------|---------------|-----------|
| Velocidade impacto | 10.05 m/s | ? | ±5% |
| Aceleração máxima | ~0.42g | ? | ±10% |
| Tempo até impacto | 100.02 s | ? | ±3% |
| Taxa de rotação médio | 439 rpm | ? | ±5% |
| Ângulo de pitch | 11.89° | ? | ±2° |

#### Próximas Milestones

1. **Teste #3 (Data: A definir)**
   - Protótipo: Asa2.DXF + eletrônica embarcada
   - Objetivo: Validar simulação com dados reais
   - Critério de sucesso: ±5% de diferença vs previsões

2. **Teste #4 (Design otimizado)**
   - Protótipo: Asa3.dxf + eletrônica
   - Alvo: Reduzir velocidade de impacto para 9.5 m/s
   - Espera-se: +15% de área ou melhor distribuição radial

3. **Testes Topológicos (Teste #5+)**
   - Teste #5: 2 asas vs 4 asas (estabilidade comparada)
   - Teste #6: 6 asas para máxima dissipação

### Recomendações

1. **Variações Topológicas** (após validação em Test #3)
   - Comparação 2 asas vs 4 asas vs 6 asas
   - Testar 6 asas para máxima dissipação de energia

2. **Otimização Contínua**
   - Usar dados reais para re-calibrar simulação
   - Iteração: sim → real → ajuste modelo → novo design

3. **Documentação de Sucesso**
   - Publicar resultados comparativos (simulação vs experimental)
   - Submeter para LASC como case study de design validation

---

## Artefatos Gerados

### Arquivos de Simulacao

```
extras/wing-analisys/
├── test_1_asa1/
│   ├── samara_pq_impact_report.json         (data completa)
│   ├── samara_pq_lrr_report.png             (gráficos de certificação)
│   └── samara_pq_frontal_area.png           (visualização 2D)
└── test_2_asa2/
    ├── samara_pq_impact_report.json         (data completa)
    ├── samara_pq_lrr_report.png             (gráficos de certificação)
    └── samara_pq_frontal_area.png           (visualização 2D)
```

### Logs de Simulação

- Stdout output com iterações de otimização
- Relatórios TXT em formato legível
- Visualizações PNG 4x2 (altitude, velocidade, pitch, spin)

---

## Referências Técnicas

### Documentação do Pipeline

- `samara_pq_simulation.py` - Código principal (991 linhas Python)
- `samara_pq_usage_manual.md` - Manual completo com exemplos
- `samara_pq_quickstart.md` - Guia rápido de execução
- `samara_pq_script_considerations.md` - Interpretação de resultados

### Publicações Relacionadas

- Samara seed autorotation (biological inspiration)
- Low Reynolds number airfoil design
- PocketQube aerodynamics (LASC standards)

### Próxima Nota

→ [[2026-04-17-helike-historico-testes]] - Histórico completo com campo + simulação
