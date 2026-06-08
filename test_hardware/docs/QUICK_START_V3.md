# Quick Start - Novos Testes (GPS + BME280)

## Instalação Rápida de Bibliotecas

```bash
# Arduino IDE → Tools → Manage Libraries

Procurar e instalar:
✓ Adafruit_BME280
✓ Adafruit_Sensor
```

Já estão built-in:

- `Wire` (I2C)
- `HardwareSerial` (UART)
- `LittleFS` (Storage)

---

## Teste GPS Isolado

**Arquivo**: `test_hardware/sensor/gps_neo8m/gps_neo8m.ino`

**Hardware**:

```
GPS NEO-8M          ESP32-C3
VCC (5V)     ──────► 5V
GND          ──────► GND
RX (dados)   ──────► GPIO 20 (RX)
TX (comando) ──────► GPIO 21 (TX)
```

**Setup Arduino IDE**:

- Board: ESP32-C3
- Upload Speed: 921600
- Port: /dev/ttyACM0

**Serial Output Esperado**:

```
=== Teste GPS NEO-8M ===
✓ GPS UART inicializado
Aguardando dados NMEA...

--- Status GPS ---
Satélites vistos: 0
Fix quality: Sem fix
Fix type: Sem fix
Aguardando fix GPS...

(após 30-60 segundos em local aberto)

Satélites vistos: 8
Fix quality: GPS fix
Fix type: 3D
Latitude: -23.552140
Longitude: -46.633400
Altitude: 750.23 m
Velocidade: 0.00 km/h
HDOP: 1.2 | VDOP: 1.5
```

**Troubleshooting**:

- Sem dados: Verificar UART RX/TX (pinos 20/21)
- Sem fix por > 2 min: Ficar em local aberto (céu > 45°)
- Dados erráticos: Verificar alimentação 5V do GPS

---

## Teste BME280 Completo

**Arquivo**: `test_hardware/sensor/bme280/bme280.ino`

**Hardware**:

```
BME280           ESP32-C3
VCC (3.3V) ─────► 3.3V
GND        ─────► GND
SDA        ─────► GPIO 8
SCL        ─────► GPIO 9
(SDO=GND para endereço 0x76)
```

**Serial Output Esperado**:

```
=== Teste BME280 ===
Procurando BME280 no endereço 0x76
✓ BME280 encontrado!
✓ Sensor configurado
  - Modo: Normal
  - Amostragem: 2x (todos)
  - Tempo espera: 1000ms

--- Dados BME280 ---
Leituras: 1 | Erros: 0
Temperatura: 25.34 °C
Pressão: 1013.25 hPa (101325 Pa)
Umidade: 45.23 % RH
Altitude: 45.23 m (ISA, P0=101325 Pa)
Ponto orvalho: 14.56 °C
Índice calor: 26.78 °C
```

**Troubleshooting**:

- Sensor não encontrado: Verificar I2C (pinos 8/9), tentar endereço 0x77
- Valores constantes: Reset I2C (desligar/ligar power)
- Dados NaN: Verificar solda/conexão

---

## ⭐ Teste Integrado v3 (RECOMENDADO)

**Arquivo**: `test_hardware/integration/sensor_logging_v3/sensor_logging_v3.ino`

**Hardware Completo**:

```
I2C Sensors (SDA=GPIO8, SCL=GPIO9):
├─ ICM-20602 (0x69)
│  VCC (3.3V)
│  GND
│  SDA → GPIO 8
│  SCL → GPIO 9
│
└─ BME280 (0x76)
   VCC (3.3V)
   GND
   SDA → GPIO 8
   SCL → GPIO 9

UART GPS (RX=GPIO20, TX=GPIO21):
├─ VCC (5V)
├─ GND
├─ RX → GPIO 20
└─ TX → GPIO 21
```

**Serial Output Esperado**:

```
=== Teste Unificado de Sensores v3 ===
ICM-20602 + BME280 + GPS NEO-8M

=== Inicializando Sensores ===
✓ ICM20602 encontrado!
✓ BME280 inicializado!
✓ GPS UART inicializado!
✓ LittleFS montado!

=== Status dos Sensores ===
ICM20602: ✓ OK
BME280:   ✓ OK
GPS:      ✓ OK
Storage:  ✓ OK

=== Taxa de Aquisição: 20 Hz (50 ms) ===
=== Iniciando Leituras ===

[50] A: 0.12 -0.05 9.81 | T:25.34 U:45.23 | Alt: 45.23 Vz: 0.00 | GPS: ...
[100] A: 0.10 -0.03 9.81 | T:25.34 U:45.23 | Alt: 45.23 Vz: 0.00 | GPS: ...

(após 30-60s com GPS fix)

[5000] A: 0.12 -0.05 9.81 | T:25.34 U:45.23 | Alt: 45.23 Vz: 0.00 | GPS: OK
```

**CSV Gerado** (LittleFS):

```
arquivo: /sensores_v3.csv

Colunas (15):
millis, ax, ay, az, gx, gy, gz, pressao_Pa, altura_m, 
temperatura_C, umidade_pct, vz, mag_giroscopia, lat, lon, alt_gps

Exemplo:
0,0.1,-0.05,10.0,0.0,0.0,0.0,101325,50.0,25.3,45.2,0.0,0.0,-23.5521,-46.6333,52.3
```

**Como Acessar Dados**:

1. Arduino IDE → Tools → LittleFS → Upload Data
2. Aguardar testes
3. Arduino IDE → Tools → Serial Monitor
4. Dados já visíveis no monitor + salvos no CSV

---

## Fluxo de Testes Recomendado

1. **Validação Individual** (se houver problemas):
   - `gps_neo8m.ino` → valida GPS UART
- `bme280.ino` → valida sensor barométrico

2. **Teste Integrado** (para Fase 1.3):
- `sensor_logging_v3.ino` → coleta tudo junto
   - Deixar rodando enquanto executa queda
   - Extrair CSV do LittleFS

3. **Análise de Dados**:

   ```bash
   # Pós-processamento (Python)
   python extras/wing-analisys/src/samara_pq_simulation.py
   
   # Gera:
   - Gráfico Vz vs tempo
   - Detecção de apogeu
   - Validação altitude GPS vs BME280
   - Estatísticas de rotação (giroscópio)
   ```

---

## ⚙️ Configurações Importantes

**v3.ino - Principais #defines**:

```cpp
#define INTERVAL_MS 50              // Taxa: 20 Hz
#define MAX_ACCEL_G 50.0            // Validação: aceleração suspeita > 5g
#define MIN_PRESSURE_PA 300         // Validação: pressão mínima
#define MAX_PRESSURE_PA 120000      // Validação: pressão máxima
#define APOGEE_THRESHOLD_MS 100     // Tempo mínimo em descida p/ apogeu
```

**Calibração de Altitude**:

```cpp
#define PRESSAO_MAR_PA 101325.0     // Ajustar se necessário
// Usar valor local de P0 para maior precisão
```

---

## Troubleshooting Rapido

| Problema | Solução |
|----------|---------|
| **GPS: ...** por > 2 min | Ficar em local aberto, 45° de céu mínimo |
| **GPS: Sem dados** | Verificar pinos 20/21, alimentação 5V |
| **BME280 não encontrado** | I2C pull-ups OK? Endereço 0x76 ou 0x77? |
| **I2C erros** | Reset: ligar/desligar power, não soldar pinos |
| **CSV vazio** | Verificar LittleFS mounted, usar `Erase Flash` |
| **Apogeu não detecta** | Aumentar altura de queda, verificar Vz |
| **Dados NaN** | Validação falhou, revisar ranges #defines |

---

**Última atualização**: 09/04/2026  
**Status**: ✅ Pronto para Fase 1.3
