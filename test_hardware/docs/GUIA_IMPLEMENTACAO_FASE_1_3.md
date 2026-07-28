# Guia de Implementação - Fase 1.3: Testes Experimentais de Queda
> **NOTA**: BME280 e BMP280 são intercambiáveis. O firmware atual tenta
> BME280 primeiro; se não encontrado, usa BMP280 (umidade = NAN).


## Visao Geral

Este guia detalha como implementar e executar os testes experimentais de queda do freio aerodinâmico usando o código integrado em `sensor_logging_v3.ino`.

**Objetivos**:

1. Validar modelos aerodinâmicos do `extras/wing-analysis/`
2. Medir taxa de descida real vs. simulada
3. Detectar padrão de rotação (estabilidade)
4. Coletar dados para calibração de detecção de apogeu
5. Testar integração de servo motor

---

## Hardware Necessario

### Componentes Eletrônicos

- [ ] **Microcontrolador**: ESP32-C3 Super Mini (ou ESP32)
- [ ] **IMU**: ICM-20602 (acelerômetro + giroscópio)
- [ ] **Sensor Barométrico**: BME280 (pressão/temperatura/umidade)
- [ ] **GPS**: NEO-8M (posição/altitude/velocidade)
- [ ] **Armazenamento**: LittleFS integrado (não precisa SD externo para testes iniciais)
- [ ] **Conectores**: I2C com pull-ups (4.7kΩ normalmente já estão na placa)
- [ ] **Bateria**: USB powerbank 5V para alimentação

### Pinagem (ESP32-C3)

```
I2C Sensors:
  SDA → GPIO 8  (BME280 + ICM-20602)
  SCL → GPIO 9
  GND → GND
  VCC → 3.3V

GPS UART:
  RX → GPIO 20  (recebe dados do GPS NEO-8M)
  TX → GPIO 21  (envia comandos para GPS)
  GND → GND
  VCC → 5V

Serial Debug:
  TX → USB (nativo)
  RX → USB (nativo)
```

### Estrutura Mecânica de Teste

```
┌─────────────────────────────────┐
│  Suporte estrutural (3D print)  │
├─────────────────────────────────┤
│  Asa de Samara (TPU)            │ ← Prototipo a testar
│  - Número: 2/3/4/6 conforme     │
│  - Material: TPU com espessura  │
│  - Raio: conforme simulação     │
├─────────────────────────────────┤
│  Servo Motor (opcional para     │
│  fase 2 - acionamento)          │
├─────────────────────────────────┤
│  Cápsula com sensores:              │
│  - ESP32-C3 + ICM-20602 + BME280 +  │
│  - GPS NEO-8M                       │
│  - Bateria USB powerbank            │
│  - Proteção: foam/cápsula       │
└─────────────────────────────────┘
```

---

## Pre-Requisitos de Software

### 1. Arduino IDE Setup

```bash
# Adicionar board manager URL:
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

# Em Preferences → Additional Boards Manager URLs
# Instalar: ESP32 boards version 2.0.3+
```

### 2. Bibliotecas Necessárias

```
- Adafruit_BME280 (via Arduino Library Manager)
- Adafruit_Sensor (via Arduino Library Manager)
- Wire (built-in)
- FS (built-in)
- LittleFS (built-in no ESP32)
- HardwareSerial (built-in)
```

### 3. Preparação do Código

```bash
cd test_hardware/integration/sensor_logging_v3/

# Usar versão v3 com todos os componentes
# sensor_logging_v3.ino - integra ICM-20602 + BME280 + GPS NEO-8M

# Ou usar diretamente em Arduino IDE
```

---

## ⚙️ Configuração e Upload

### 1. Conectar Hardware

1. Montagem de protoboard com ICM-20602, BME280 e GPS NEO-8M
2. Conectar GPIO 8 (SDA) e GPIO 9 (SCL) para sensores I2C
3. Conectar GPIO 20 (RX) e GPIO 21 (TX) para GPS UART
4. Alimentar com 3.3V (sensores I2C e ICM), 5V (GPS) e GND
5. Conectar ESP32-C3 via USB-C

### 2. Arduino IDE

```
Tools → Board: ESP32-C3 (ou ESP32 se usar DevKit)
Tools → Upload Speed: 921600
Tools → Port: /dev/ttyACM0 (ESP32-C3) ou /dev/ttyUSB0 (ESP32)
```

### 3. Upload

```
Sketch → Upload (ou Ctrl+U)
```

### 4. Monitorar Serial

```
Tools → Serial Monitor (115200 baud)

Esperado ver:
=== Teste Unificado de Sensores v3 ===
ICM-20602 + BME280 + GPS NEO-8M
✓ ICM20602 encontrado!
✓ BME280 inicializado!
✓ GPS UART inicializado!
✓ LittleFS montado!
=== Taxa de Aquisição: 20 Hz (50 ms) ===
=== Iniciando Leituras ===

[50] A: 0.12 -0.05 9.81 | T:25.34 U:45.23 | Alt: 45.23 Vz: 0.00 | GPS: ...
[100] A: 0.10 -0.03 9.81 | T:25.34 U:45.23 | Alt: 45.23 Vz: 0.00 | GPS: ...
(Aguardando GPS fix...)

[5000] A: 0.12 -0.05 9.81 | T:25.34 U:45.23 | Alt: 45.23 Vz: 0.00 | GPS: OK
```

---

## Checklist de Validação de Hardware (CRÍTICO)

**Executar ANTES de qualquer teste de queda**

### Validação de Níveis Lógicos (GPS TX)

- [ ] **Medir tensão de TX do GPS com multímetro DC**
  - Esperado: 0V ou 3.3V (nunca 5V!)
  - **Risco**: Se GPS transmitir em 5V direto, danificará GPIO 20 (RX) do ESP32-C3
  - **Correção**: Usar level shifter ou resistor voltage divider (10kΩ + 20kΩ)

- [ ] **Verificar fios da antena GPS**
  - A antena deve estar firme e apontando para o céu (teste em local aberto)
  - Verificar se há danos no conector de antena
  - Distância mínima de componentes de alta frequência (LoRa, eletrolíticos)

### Validação de Alimentação

- [ ] **Tensão 3.3V nos sensores I2C (BME280, ICM-20602)**
  - Com multímetro: medir entre VCC e GND dos sensores
  - Esperado: 3.3V ±0.1V
  - Duração: manter por 5 segundos (deve estar estável)

- [ ] **Tensão 5V no GPS NEO-8M**
  - Com multímetro: medir entre VCC e GND do GPS
  - Esperado: 5V ±0.2V
  - Verificar se há condensador de 100µF próximo ao GPS

- [ ] **GND comum entre ESP32, sensores e GPS**
  - Usar multímetro em modo continuidade (deve dar bip)
  - Conectar todas as conexões de GND em um ponto comum

### Validação de Comunicação I2C

- [ ] **Verificar pull-ups nos pinos SDA/SCL**
  - Esperado: resistores de 4.7kΩ entre SDA→3.3V e SCL→3.3V
  - Se não houver, adicionar resistores de pull-up

- [ ] **Teste de scan I2C** (use código de diagnóstico):

  ```cpp
  Wire.begin(8, 9);  // SDA=GPIO8, SCL=GPIO9
  for (byte i = 1; i < 127; i++) {
      Wire.beginTransmission(i);
      if (Wire.endTransmission() == 0) {
          Serial.printf("Encontrado I2C: 0x%02X\n", i);
      }
  }
  ```

  - **BME280**: endereço 0x77 (ou 0x76 se configurado)
  - **ICM-20602**: endereço 0x68

### Validação de UART GPS

- [ ] **Teste de comunicação UART** (use `gps_neo8m.ino`):
  - Serial Monitor deve mostrar strings NMEA: `$GPRMC`, `$GPGGA`
  - Se não receber dados, verificar:
    - Velocidade baud: 9600 (padrão do NEO-8M)
    - Pinos RX/TX invertidos?
    - Fio solto?

- [ ] **Verificar ruído no UART**:
  - Se Serial Monitor mostrar caracteres estranhos ou linhas corrompidas:
    - Aumentar distância entre LoRa e GPS
    - Adicionar ferrite no fio de alimentação do GPS
    - Encurtar cabos (máximo 10 cm)

### Validação de Capacitores e Decoupling

- [ ] **Verificar condensadores próximos aos sensores I2C**
  - Esperado: 100µF eletrônico + 100nF cerâmico perto de VCC
  - Soldagem firme e sem fraturas

### Teste Rápido de Funcionalidade

- [ ] **Executar `sensor_logging_v3.ino` por 2 minutos em repouso**
  - Esperado no Serial Monitor:
    - Aceleração: ~(0, 0, 9.81) m/s² (sem movimento)
    - Temperatura: valor consistente (ex: 25°C)
    - Umidade: valor dentro da faixa (0-100%)
    - Sem "Encontrado I2C: ???" ou erros de paridade

- [ ] **Girar o dispositivo manualmente**
  - Giroscópio deve mostrar valores não-zero enquanto girado
  - Ao parar, deve voltar para ~0

---

## Protocolo de Testes

### Fase 1.3.1: Validação de Bancada (30 min)

**Objetivo**: Confirmar que hardware está funcionando e dados são coletados

**Procedimento**:

1. [ ] Deixar rodando por 2 minutos em repouso
2. [ ] Verificar Serial Monitor: dados consistentes?
3. [ ] Manualmente mover para cima/baixo
   - Esperado: Vz positivo (subindo) → negativo (descendo)
4. [ ] Girar no ar rapidamente
   - Esperado: Mag_giroscopia aumenta

**Sucesso**: CSV sendo preenchido, dados faz sentido

---

### Fase 1.3.2: Teste de Queda Livre (Sem Asa) - 1 hora

**Objetivo**: Estabelecer baseline de queda (referência)

**Setup**:

- Altura: 10 metros (primeiro teste)
- Local: Area aberta, sem obstáculos
- Repetições: 5×

**Procedimento por repetição**:

1. [ ] Resetar ESP32
2. [ ] Deixar gravando (Serial Monitor aberto)
3. [ ] **Iniciar queda de 10m**: largar manualmente
4. [ ] **Recuperar** do chão
5. [ ] Extrair dados via Serial
6. [ ] Salvar como `teste_baseline_rep1.csv`

**Análise esperada**:

```
Tempo de queda: ~1.4 segundos (v = √(2gh) = 14 m/s)
Vz final (fundo): ~-14 m/s
Apogeu: Não (caindo desde início)
Aceleração durante queda: ~9.81 m/s² (gravidade)
```

**CSV típico**:

```
millis,ax,ay,az,gx,gy,gz,pressao_Pa,altura_m,temperatura_C,umidade_pct,vz,mag_giroscopia,lat,lon,alt_gps
0,0.1,-0.05,10.0,0.0,0.0,0.0,101325,50.0,25.3,45.2,0.0,0.0,-23.5521,-46.6333,52.3
50,-0.2,0.15,10.2,-0.001,0.001,0.002,101320,49.96,25.3,45.2,-0.08,0.0024,-23.5521,-46.6333,52.3
100,-0.3,0.10,9.9,0.0,0.001,0.001,101315,49.92,25.3,45.2,-0.16,0.0014,-23.5521,-46.6333,52.3
... (cada 50ms por ~1400ms)
1400,-0.1,0.05,-5.0,0.001,0.0,0.0,100800,35.0,25.2,45.8,-14.3,0.0015,-23.5520,-46.6334,35.2
```

---

### Fase 1.3.3: Teste com Asa Samara (Protótipo 1) - 2 horas

**Objetivo**: Validar freio - compare vs baseline

**Setup**:

- Asa: Config conforme `extras/wing-analysis/` (ex: 2 asas, R=100mm)
- Altura: 10 metros (mesmo que baseline)
- Repetições: 5×

**Procedimento**: Idêntico ao baseline, mas com asa acoplada

**Análise esperada** (se freio funciona):

```
Tempo de queda: ~2.0-3.0 segundos (mais lento!)
Vz final: ~-5 m/s (muito menor que -14 m/s)
Padrão de rotação: Mag_giroscopia alta e constante (autogiro)
Apogeu detector: Pode detectar "flutuação" inicial
```

**Comparação com simulação**:

```
IMPORTANTE: Em quedas de 10m NÃO atingimos regime terminal!
   
Simulação (`extras/wing-analysis/results/test_2_asa2/samara_pq_impact_report.txt`):
   - Config 2×R124mm: v₀ = 27.65 m/s (regime terminal)
   - Config 2×R100mm: v₀ = 27.61 m/s (regime terminal)
   
Esperado no teste (10m, ~2s):
   - Vz_médio = ∫vz(t) dt / tempo
   - Vz_máximo ≈ -8 a -12 m/s (ainda acelerando)
   - Comparar com simulação PARA MESMA ALTURA (usar script Python)
```

---

### Fase 1.3.4: Iteração com Variações (3-4 horas)

**Objetivo**: Otimizar design - testar diferentes configs

**Testes propostos**:

1. **Espessura**: 0.4mm vs 0.6mm vs 0.8mm
2. **Número de asas**: 2 vs 3 vs 4
3. **Raio**: 80mm vs 100mm vs 120mm

**Tabela de Testes** (altura 10m, tempo ~2.0-3.0s):

```
ID  | Config          | Simul v_terminal | Vz_esperado* | Vz_medido | Variação | Status
----|-----------------|------------------|--------------|-----------|----------|--------
T01 | 2 asas,0.6mm    | 27.61 m/s        | -8 a -12 m/s | -9.2 m/s  | ±5%      | ✅
T02 | 2 asas,0.4mm    | 27.61 m/s        | -7 a -11 m/s | -8.8 m/s  | ±4%      | ✅
T03 | 3 asas,0.6mm    | 23.81 m/s        | -9 a -13 m/s | -11.1 m/s | ±3%      | ✅
T04 | 6 asas,0.6mm    | 17.85 m/s        | -11 a -15 m/s| -12.5 m/s | +8%      | (mais lento)

*Vz_esperado = Simulação de altura 10m com mesmo coef. aerodinâmico (não usar v_terminal direto!)
```

**Critério de aceitação**:

- Vz_medido dentro de ±15% da simulação
- Estabilidade em 5 repetições (desvio padrão < 5%)
- Sem danos visíveis à asa

---

## Analise de Dados

### 1. Extrair CSV do LittleFS

**Opção A**: Via Serial Monitor

```
# Após teste, copiar todo output do Serial Monitor
# Salvar como: teste_queda_rep1.csv
```

**Opção B**: Via terminal (direto do Arduino)

```bash
# Em Arduino IDE, Tools > Serial Monitor
# Copiar dados linha por linha
# Ou usar script Python com pyserial
```

### 2. Script Python para Análise

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Carregar dados
df = pd.read_csv('teste_queda_rep1.csv')

# Calcular estatísticas
altitude_max = df['altura_m'].max()
tempo_queda = df['millis'].iloc[-1] / 1000
vz_min = df['vz_ms'].min()
vz_media = df[df['altura_m'] < altitude_max - 1]['vz_ms'].mean()  # Excluir início
aceleracao_max = np.sqrt(df['ax_ms2']**2 + df['ay_ms2']**2 + df['az_ms2']**2).max()
rotacao_media = df['mag_giroscopia_rads'].mean()

print(f"""
=== RESULTADOS DO TESTE ===
Altitude máxima: {altitude_max:.2f} m
Tempo de queda: {tempo_queda:.2f} s
Vz mínimo (máx descida): {vz_min:.2f} m/s
Vz médio (estável): {vz_media:.2f} m/s
Aceleração máxima: {aceleracao_max:.2f} m/s²
Rotação média: {rotacao_media:.6f} rad/s
""")

# Gráficos
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))

# Altitude vs Tempo
ax1.plot(df['millis']/1000, df['altura_m'], 'b-', linewidth=2)
ax1.set_xlabel('Tempo (s)')
ax1.set_ylabel('Altitude (m)')
ax1.set_title('Altitude vs Tempo')
ax1.grid()

# Velocidade Vertical
ax2.plot(df['millis']/1000, df['vz_ms'], 'r-', linewidth=2)
ax2.axhline(y=vz_min, color='k', linestyle='--', label=f'Mín: {vz_min:.2f} m/s')
ax2.set_xlabel('Tempo (s)')
ax2.set_ylabel('Vz (m/s)')
ax2.set_title('Velocidade Vertical (negativo = descendo)')
ax2.grid()
ax2.legend()

# Aceleração
acel = np.sqrt(df['ax_ms2']**2 + df['ay_ms2']**2 + df['az_ms2']**2)
ax3.plot(df['millis']/1000, accel, 'g-', linewidth=2)
ax3.axhline(y=9.81, color='k', linestyle='--', label='Gravidade')
ax3.set_xlabel('Tempo (s)')
ax3.set_ylabel('Aceleração (m/s²)')
ax3.set_title('Magnitude de Aceleração')
ax3.grid()
ax3.legend()

# Rotação
ax4.plot(df['millis']/1000, df['mag_giroscopia_rads'], 'm-', linewidth=2)
ax4.set_xlabel('Tempo (s)')
ax4.set_ylabel('Rotação (rad/s)')
ax4.set_title('Magnitude do Giroscópio')
ax4.grid()

plt.tight_layout()
plt.show()

# Exportar summary
with open('teste_queda_rep1_analise.txt', 'w') as f:
    f.write(f"""
TESTE DE QUEDA - ANÁLISE
=======================
Data: {pd.Timestamp.now()}

Estatísticas:
- Altitude máxima: {altitude_max:.2f} m
- Tempo de queda: {tempo_queda:.2f} s
- Vz mínimo: {vz_min:.2f} m/s
- Vz médio: {vz_media:.2f} m/s
- Aceleração máxima: {aceleracao_max:.2f} m/s²
- Rotação média: {rotacao_media:.6f} rad/s

Validações:
- Apogeu detectado: {df['altura_m'].diff().min() < 0}
- Impacto detectado: {aceleracao_max > 15}
""")
```

### 3. Comparar com Simulação

```python
# Dados da simulação (extras/wing-analysis/results/test_2_asa2/samara_pq_impact_report.txt)
# Terminal velocities por configuração:
# - 2×R124mm: v₀ = 27.65 m/s
# - 2×R100mm: v₀ = 27.61 m/s
# - 3×R124mm: v₀ = 23.81 m/s
# - 6×R100mm: v₀ = 17.85 m/s (recomendado)

import pandas as pd
import numpy as np

df_teste = pd.read_csv('teste_queda_rep1.csv')

# Extrair dados estáveis (excluir primeiros/últimos 500ms)
tempo_estavel = df_teste[(df_teste['millis'] > 500) & (df_teste['millis'] < (df_teste['millis'].max() - 500))]
vz_estavel_medio = tempo_estavel['vz'].mean()
vz_estavel_std = tempo_estavel['vz'].std()

simul_config = "2 asas, R=100mm"
simul_vz_terminal = 27.61  # m/s (absoluto, descendo)

print(f"""
COMPARAÇÃO SIMULAÇÃO vs TESTE
============================
Config: {simul_config}
Simulação (regime terminal): {simul_vz_terminal:.2f} m/s
Teste real (Vz médio estável): {abs(vz_estavel_medio):.2f} ± {vz_estavel_std:.2f} m/s

 NOTA: Teste em 10m NÃO atinge regime terminal
   Compare com simulação para MESMA ALTURA usando script de física
   (calcular posição teórica em t=tempo_queda_real)

Critério: Desvio padrão (5 reps) < 5% da média
Status: {"VALIDADO" if vz_estavel_std < (abs(vz_estavel_medio) * 0.05) else "REJEITAR - Instabilidade"}
""")
```

---

## Iteracao e Ajustes

### Se Vz for TOO FAST (>-8 m/s)

→ Aumentar área das asas

- Aumentar raio: 100mm → 120mm
- Aumentar espessura: 0.6mm → 0.8mm
- Adicionar mais asas: 2 → 3 ou 4

### Se Vz for TOO SLOW (<-2 m/s)

→ Diminuir área das asas

- Diminuir raio: 100mm → 80mm
- Diminuir espessura: 0.6mm → 0.4mm
- Menos asas: 4 → 3 ou 2

### Se Padrão for INSTÁVEL (Rotação inconsistente)

→ Revisar design mecânico

- Verificar simetria das asas
- Aumentar raio para estabilizar (momento angular maior)
- Testar em altura maior (mais tempo para estabilizar)

---

## Cronograma Sugerido

```
Semana 1:
  Seg-Ter: Setup hardware, validação de bancada (Fase 1.3.1)
  Qua-Qui: Testes de baseline (Fase 1.3.2) - 5 quedas
  Sex: Análise e preparação de asas

Semana 2:
  Seg-Ter: Testes com asa protótipo 1 (Fase 1.3.3) - 5 quedas
  Qua: Análise comparativa vs simulação
  Qui-Sex: Iteração com variações (Fase 1.3.4) - 3 configs

Semana 3:
  Seg-Ter: Testes finais, validação
  Qua: Documentação de resultados
  Qui-Sex: Ajustes finais para integração com servo
```

---

## Checklist de Execucao

### Pré-Teste

- [ ] Hardware montado e testado
- [ ] Código v2 melhorado carregado
- [ ] Serial Monitor funcionando
- [ ] Bateria carregada
- [ ] Area de queda segura (sem pessoas)
- [ ] Câmera de vídeo preparada (opcional - para análise visual)

### Durante Teste

- [ ] Anotar: configuração, altura, peso, clima
- [ ] Realizar 5 repetições idênticas
- [ ] Monitorar Serial para eventos (Apogeu?)
- [ ] Registrar duração de queda manualmente (cronômetro)
- [ ] Fotografar/Filmar cada queda

### Pós-Teste

- [ ] Extrair CSV do ESP32
- [ ] Executar script de análise Python
- [ ] Comparar com simulação
- [ ] Documentar resultados
- [ ] Decidir próximos ajustes

---

## Troubleshooting

### "GPS mostra apenas pontos (... em vez de OK)"

- [ ] GPS precisa de 30-60 segundos para primeiro fix
- [ ] Ficar em local aberto (mais de 45° de céu visível)
- [ ] Verificar antena GPS - deve estar apontando para cima
- [ ] Problema: GPS perto de grandes estruturas metálicas → afastar 10m
- [ ] Se permanecer como "..." por > 2 min: verificar UART RX/TX nos pinos 20/21

### "Apogeu não é detectado"

- [ ] Verificar se `altura` está aumentando no início
- [ ] Aumentar altura de queda (maior Vz para detectar)
- [ ] Verificar threshold: `if (vz < -0.5)` - ajustar se necessário

### "Dados erráticos ou NaN"

- [ ] Verificar conexão I2C (pull-ups OK?)
- [ ] Reset barramento: ligar/desligar power
- [ ] Verificar solda nos pinos
- [ ] Para GPS: verificar se está recebendo serial (coloque breakpoint na UART)

### "Velocidade vertical não muda"

- [ ] Verificar se `millis_anterior` está sendo atualizado
- [ ] Aumentar altura de queda
- [ ] Verificar se BME280 está calibrado (1013.25 hPa correto?)

### "ESP32 não grava dados"

- [ ] Verificar if LittleFS está montado (Serial output)
- [ ] Tentar formatar LittleFS: Menu → Tools → Erase All Flash Contents
- [ ] Testar com Serial Monitor (não via CSV)

### "BME280 mostra pressão constantemente igual"

- [ ] Verificar endereço I2C: é 0x76 ou 0x77? (SDO=GND vs VCC)
- [ ] Se o jumper SDO não está conectado, tente 0x77
- [ ] Validar com teste isolado: `test_hardware/sensor/bme280/bme280.ino`

---

## Proximos Passos Apos Validacao

1. **Integração de Servo Motor**
   - Disparar em apogeu automático
   - Testar confiabilidade

2. **Integração de GPS**
    - Validação cruzada de altitude GPS vs BME280
    - Registrar posição de pouso
    - Testar confiabilidade em ambiente aberto

3. **Refinamento de Detecção de Apogeu**
   - Usar dados reais dos testes para calibração
   - Validar estado de máquina

4. **Firmware Final do Satélite**
   - Integrar todo código em firmware.ino
   - Adicionar lógica de acionamento de servo
   - Preparar para lançamento real

---

**Status**: Pronto para testes
**Última atualização**: 09/04/2026  
**Responsável**: Time de Desenvolvimento
