---
title: Plano de Instrumentacao - Helike #213 (LASC 2026) Test #3
date: 2026-04-17
tags: [helike, test-3, instrumentação, eletrônica, validação]
status: active
priority: high
related:
  - "[[2026-04-17-helike-historico-testes]]"
  - "[[2026-04-17-analise-simulacao-helike]]"
  - "[[satellite]]"
---

# Plano de Instrumentacao - Helike #213 (LASC 2026) Test #3

## Objetivo

Validar predições computacionais (Samara PQ) com dados experimentais reais durante queda de protótipo com eletrônica embarcada integrada.

---

## Contexto

### Problema

- Testes #1 e #2 foram **qualitativos** (observação visual)
- Simulações Samara PQ são **quantitativas** mas **não-validadas**
- Margem de massa disponível: **~15g** (250g - 235g estrutura)
- Necessário: Fechar loop de validação (sim → real → ajuste)

### Solução

Integrar sensores embarcados em Asa2.DXF (design validado) para capturar:

- Aceleração 3D (impacto, vibrações)
- Velocidade angular (taxa de rotação)
- Altitude e trajetória (GPS)
- Telemetria em tempo real (LoRa)

---

## Arquitetura de Instrumentação

### Hardware Stack

```
┌─────────────────────────────────────────────────────────────┐
│               Prototipo Helike #213 (LASC 2026) Test #3     │
│                  (Alba Orbital 1P)                          │
├─────────────────────────────────────────────────────────────┤
│  [Asa2.DXF]         [Eletrônica Embarcada]         [Body]   │
│   4 asas              @ 15g ± 2g                  (50x50mm)  │
├─────────────────────────────────────────────────────────────┤
│ Central Processing Unit:  ESP32 C3 (satellite variant)      │
├─────────────────────────────────────────────────────────────┤
│  IMU (I2C)      │  GPS (UART)     │  LoRa (SPI)             │
│  ICM-20602      │  NEO-8M         │  RFM95W 915MHz          │
│  ±16g/±2000°/s  │  5+ sat 3D fix  │  10-20 dBm              │
│  50 Hz          │  1 Hz           │  SF7-SF10 adaptativo    │
└─────────────────────────────────────────────────────────────┘
```

### Distribuição de Massa (Budget)

| Componente | Massa | % do Total |
|------------|-------|-----------|
| Estrutura Asa2.DXF | 180 g | 72% |
| ESP32-C3 (MCU) | 4 g | 1.6% |
| IMU (ICM-20602) | 3 g | 1.2% |
| GPS (NEO-8M) | 2.5 g | 1% |
| RFM95W (transceiver) | 2 g | 0.8% |
| Bateria (LiPo 250mAh) | 1.5 g | 0.6% |
| Suportes/Cabeamento/SD | 4.5 g | 1.8% |
| **TOTAL DA ELETRÔNICA** | **~15 g** | **100% do budget eletrônico** |

**⚠️ Nota**: Este budget representa apenas a eletrônica embarcada adicional para o Test #3.

---

## Especificação de Sensores

### 1. IMU: ICM-20602 (6DOF)

**Função**: Capturar acelerações e velocidade angular durante voo e impacto

**Especificações**:

- Acelerômetro: ±16g máx, resolução 2 mg/LSB
- Giroscópio: ±2000°/s máx, resolução 16.4°/s/LSB
- Interface: I2C (0x68)
- Frequência de amostragem: **50 Hz** (0.02 s entre amostras)
- Consumo: ~3.6 mA ativo

**Dados Esperados**:

```
Aceleração no eixo Z (vertical):
  - Voo normal: ~0 g (queda livre)
  - Impacto: pico de -0.4 a -0.6 g (a validar vs sim ~0.42g)
  
Velocidade angular (rotação):
  - Regime estável: ~439 rpm = 46 rad/s (a validar)
  - Detectar mudanças durante descida
```

**Validação**:

- ∫a_z dt = Δv (integrar aceleração → velocidade)
- Comparar com GPS (velocidade vertical)
- Detectar picos de g-force no impacto

---

### 2. GPS: NEO-8M

**Função**: Rastrear altitude, velocidade, posição durante descida e impacto

**Especificações**:

- Canais: 72 (até 6+ satélites simultâneos)
- Precisão: ±2.5 m (95% confidence)
- Velocidade vertical: ±0.1 m/s típico
- Taxa de atualização: **1 Hz** (sincronizar com IMU em software)
- Interface: UART (9600 baud)
- Consumo: ~45 mA ativo

**Dados Esperados**:

```
Altitude (m):
  - Início: altura real de lançamento (a registrar no teste)
  - Final: 0 m (impacto)
  - Taxa de descida: alvo de ordem de grandeza ~10 m/s (validar vs simulação)
  
Velocidade vertical (m/s):
  - Regime estável: ~-10 m/s (concordar com simulação: 10.05 m/s)
  - Variação: indicaria instabilidade ou vento
```

**Validação**:

- Comparar v_z GPS com ∫a_z IMU
- Detectar se 10.05 m/s simulado é realístico
- Medir duração total do voo: 100.02 s esperado

---

### 3. LoRa: RFM95W (915 MHz)

**Função**: Transmitir telemetria em tempo real para ground station

**Especificações**:

- Frequência: 915 MHz (US band)
- Potência TX: 10-20 dBm
- Spreading factor: SF7-SF12 (automático com adaptação)
- Interface: SPI
- Consumo TX: ~120 mA (durante transmissão)
- Consumo RX: ~10 mA (standby)

**Formato de Mensagem** (formato comprimido):

```
[timestamp_ms][ax_g][ay_g][az_g][gx_dps][gy_dps][gz_dps][alt_m][vz_ms]
Exemplo: 2500,0.05,-0.02,-1.03,10,5,438,997,9.8
Envio: A cada 2s durante voo, 100ms durante impacto (alta frequência)
```

**Validação**:

- Confirmar link antes de lançamento
- Verificar RSSI e SNR durante descida
- Usar para early warning de anomalias

---

### 4. Data Logger: SD Card (backup)

**Função**: Gravar todos os dados em SD para análise post-voo (backup contra perda LoRa)

**Especificações**:

- Capacidade: 1-4 GB
- Taxa de escrita: 256 KB/s típico
- Arquivo: CSV com timestamp, IMU, GPS, status

**Frequência**:

- Modo normal: 10 Hz (0.1s)
- Modo impacto (detecção de g-force > 0.2g): 100 Hz (0.01s)

---

## Plano de Voo - Test #3

### Timeline Estimada

```
T = 0:00:00  → Preparação e verificação de sensores
T = 0:05:00  → Aquecimento GPS (mínimo 3 satélites)
T = 0:10:00  → Verificação de link LoRa
T = 0:15:00  → Armamento e colocação em altitude
T = 0:20:00  → LANÇAMENTO

T = 0:20:00 a 1:40:00  → VOO NORMAL (100s esperado)
  - IMU: 50 Hz contínuo
  - GPS: 1 Hz contínuo
  - LoRa: telemetria a cada 2s
  - SD: 10 Hz backup

T = 1:40:00 → IMPACTO (detection em a_z > 0.2g)
  - IMU: switch para 100 Hz high-speed
  - Duração pós-impacto: 10s (capturar vibrações)

T = 1:50:00 → RECUPERAÇÃO e coleta de dados
```

### Pré-voo Checklist

- [ ] Bateria LiPo carregada (4.2V)
- [ ] GPS com fix (≥5 satélites)
- [ ] LoRa link estabelecido com ground station
- [ ] SD card formatada e com espaço livre (>100 MB)
- [ ] IMU calibrada (acelerômetro offset verificado)
- [ ] Massa total ≤ 250g confirmada
- [ ] Estrutura Asa2.DXF inspecionada
- [ ] Câmera de vídeo (opcional, para visual validation)

---

## Procedimento de Validação

### Fase 1: Processamento de Dados (Pós-voo)

```python
# Pseudocódigo para análise
data = load_csv("helike_test3_flight.csv")

# Sincronização de sensores
imu_data = resample(data.imu, 50)  # 50 Hz
gps_data = resample(data.gps, 1)   # 1 Hz

# Validação 1: Velocidade vertical
v_z_imu = integrate(imu_data.az)
v_z_gps = gps_data.velocity_z
assert abs(v_z_imu - v_z_gps) < 0.5  # ±0.5 m/s tolerância

# Validação 2: Comparação com simulação
sim_impact_speed = 10.05  # m/s
real_impact_speed = abs(v_z_gps[-1])
error = abs(real_impact_speed - sim_impact_speed) / sim_impact_speed
assert error < 0.05  # ±5% tolerância

# Validação 3: Tempo de voo
sim_flight_time = 100.02  # s
real_flight_time = max(gps_data.t) - min(gps_data.t)
time_error = abs(real_flight_time - sim_flight_time) / sim_flight_time
assert time_error < 0.03  # ±3% tolerância

# Validação 4: Energia de impacto
g_force_max = max(imu_data.az)
energy_real = 0.5 * 0.250 * real_impact_speed**2
energy_sim = 12.62  # J
assert abs(energy_real - energy_sim) / energy_sim < 0.1  # ±10%
```

### Fase 2: Análise Visual (Matplotlib)

```
Plotar 4 subplots:
1. Altitude vs tempo (GPS)
2. Velocidade vertical vs tempo (GPS + IMU integrada)
3. Aceleração Z vs tempo (IMU, destacar pico de impacto)
4. Taxa de rotação (giroscópio Z) vs tempo
```

### Fase 3: Relatório Comparativo

| Métrica | Simulação | Real | Erro | Status |
|---------|-----------|------|------|--------|
| Tempo impacto | 100.02 s | ? | ? | ✓/✗ |
| Velocidade impacto | 10.05 m/s | ? | ? | ✓/✗ |
| Energia impacto | 12.62 J | ? | ? | ✓/✗ |
| Taxa de rotação | 439 rpm | ? | ? | ✓/✗ |
| Ângulo pitch | 11.89° | ? | ? | ✓/✗ |

**Pass criteria**: ≥ 4/5 métricas com erro < 5%

---

## Instrumentação do Ground Station

### Setup Receptor LoRa

```
Ground Station Hardware:
├── Raspberry Pi 4 (ou PC com USB)
├── RFM95W receptor (915 MHz)
├── Antenna (dipolo, omnidireccional)
└── GPS disciplinado (sincronização)

Software:
├── TTN Console (The Things Network) - cloud backend
├── Python script (real-time plotting)
└── Backup SD logs
```

### Dashboard em Tempo Real

```
┌─────────────────────────────────────────┐
│  HELIKE TEST #3 - LIVE TELEMETRY        │
├─────────────────────────────────────────┤
│ Altitude:   (live)  │ Vz:     -9.8 m/s │
│ Satélites:   6      │ RSSI:   -110 dBm │
│ Temperature: 22°C   │ SNR:    +8.5 dB  │
│ Spin Rate:   438 rpm│ G-force: 0.02 g │
├─────────────────────────────────────────┤
│ [Live Plot] Altitude vs Time            │
│ [Live Plot] Aceleração Z vs Time        │
└─────────────────────────────────────────┘
```

---

## Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| GPS perder fix durante voo | Dados de altitude inválidos | Validar com IMU integrada |
| LoRa link falhar | Perder telemetria em tempo real | Usar SD card como backup |
| Bateria insuficiente | Shutdown precoce | Testar duração (alvo: 120s) |
| Impacto danificar SD | Perder dados pós-voo | Adicionar proteção física |
| Sobrecarga de peso | Violação da regra PocketQube | Pesar novamente antes do lançamento |
| Eletrônica interferir aerodinâmica | Mudança de características | Montar suportes em "pods" aerodinâmicos |

---

## Critérios de Sucesso

### Test #3 é considerado **sucesso** se

✓ Voo completo (T > 95s) sem falhas estruturais  
✓ Dados GPS válidos durante 100% do voo  
✓ LoRa link mantido com RSSI > -120 dBm  
✓ Erro simulação vs real < 5% em velocidade de impacto  
✓ Espinha dorsal IMU-GPS sincronizada com erro < 0.5 m/s  
✓ Energia de impacto predita vs medida concordam (±10%)  

### Test #3 é **inconclusivo** se

⚠ Erro 5-10% (executar Test #3b com ajustes)  
⚠ Perda parcial de dados mas suficiente para análise  
⚠ Anomalias aerodinâmicas detectadas (wind, vibration)  

### Test #3 é **falha** se

✗ Protótipo não consegue voo > 50s  
✗ Perda total de telemetria e SD card  
✗ Erro > 15% em velocidades (indica modelo inadequado)  
✗ Hardware danificado em impacto (inviável para design)  

---

## Próximos Documentos

→ [[2026-04-17-helike-historico-testes]] - Histórico + observações campo  
→ [[2026-04-17-analise-simulacao-helike]] - Análise completa simulação  
→ [[satellite]] - Projeto satélite principal (eletrônica base)  

---

## Timeline de Execução

| Data | Atividade | Responsável | Status |
|------|-----------|-------------|--------|
| 17/04 - 30/04 | Procurar e integrar sensores | Hardware | Pendente |
| 01/05 - 15/05 | Desenvolvimento firmware ESP32 | Software | Pendente |
| 16/05 - 22/05 | Testes de integração e calibração | Eng. | Pendente |
| 23/05 - 24/05 | Voo Test #3 | Campo | Agendado |
| 25/05 - 31/05 | Análise de dados e relatório | Data | Pendente |

**Próximo marco**: Procurar componentes até 30/04/2026
