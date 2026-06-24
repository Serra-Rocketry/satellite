# Firmware — Documentacao Detalhada

Documentacao de cada modulo do firmware do satellite Helike (#213).

## Indice

1. [main.cpp](#maincpp)
2. [config.h](#configh)
3. [Sensores](#sensores)
4. [Modulos de Comunicacao](#modulos-de-comunicacao)
5. [Modulos de Dados](#modulos-de-dados)
6. [lib/calc](#libcalc)

---

## main.cpp

**Arquivo**: `src/main.cpp`

Ponto de entrada do sistema. Contem `setup()` (inicializacao unica) e `loop()`
(leitura e transmissao continua).

### setup()

Sequencia de inicializacao:

```
Serial → I2C → Buzzer/LED → BME280 → ICM-20602 → GPS → LoRa → Storage → Feedback
```

Cada modulo e inicializado com validacao. Sensores falham de forma nao-critica
(sistema continua operando). Storage e LoRa sao reportados mas nao bloqueiam.

O feedback sonoro (3 beeps) e visual (3 piscadas) indica sucesso na inicializacao
dos sensores criticos (BME280 + ICM-20602).

### loop()

Execucao controlada por `millis()` a cada `SAMPLE_INTERVAL_MS` (200ms = 5Hz):

```
GPS update → IMU update → Coleta dados → Valida → Calcula Vz → Formata CSV → TX → LED toggle
```

O GPS e atualizado a cada iteracao (necessario para manter o parser TinyGPSPlus
atualizado). A IMU e atualizada apenas no intervalo de amostragem.

### Estado Global

| Variavel | Tipo | Descricao |
|----------|------|-----------|
| `g_last_sample` | `uint32_t` | Timestamp do ultimo sample |
| `g_last_debug_print` | `uint32_t` | Timestamp do ultimo print debug |
| `g_bme_ok` | `bool` | BME280 operacional? |
| `g_icm_ok` | `bool` | ICM-20602 operacional? |
| `g_lora_ok` | `bool` | LoRa operacional? |

---

## config.h

**Arquivo**: `src/config.h`

Centraliza todas as configuracoes do sistema.

### Identificacao

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| `TEAM_ID` | `"#213"` | Identificador da equipe |
| `MISSION_NAME` | `"Helike PocketQube"` | Nome da missao |

### Pinout

| Constante | Valor | Interface |
|-----------|-------|-----------|
| `I2C_SDA` | 8 | I2C data |
| `I2C_SCL` | 9 | I2C clock |
| `LORA_MOSI` | 7 | SPI LoRa |
| `LORA_MISO` | 5 | SPI LoRa |
| `LORA_SCK` | 6 | SPI LoRa |
| `LORA_CS` | 10 | SPI chip select |
| `LORA_RST` | 4 | LoRa reset |
| `LORA_DIO0` | 3 | LoRa IRQ |
| `GPS_RX` | 20 | UART GPS |
| `GPS_TX` | 21 | UART GPS |
| `LED_PIN` | 1 | LED indicador |
| `BUZZER_PIN` | 8 | Buzzer piezo |
| `BUTTON_PIN` | 2 | Botao de entrada |

### Timing

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| `SERIAL_BAUD` | 115200 | Serial monitor |
| `GPS_BAUD` | 9600 | UART GPS |
| `SAMPLE_INTERVAL_MS` | 200 | 5Hz sampling |
| `GPS_READ_INTERVAL_MS` | 1000 | 1Hz GPS |
| `DEBUG_PRINT_INTERVAL_MS` | 2000 | Print debug 0.5Hz |

### LoRa

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| `LORA_FREQ` | 915E6 | Frequencia Americas |
| `LORA_SYNC_WORD` | 0xF3 | Network ID |
| `LORA_TX_POWER` | 20 | dBm maximo |
| `LORA_SPREADING` | 7 | Spreading Factor |
| `LORA_BANDWIDTH` | 125E3 | 125 kHz |

### Sensores

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| `BME280_ADDR` | 0x76 | Endereco I2C |
| `BME280_SEALEVEL_HPA` | 1013.25 | Pressao referencia |
| `ICM20602_ADDR` | 0x68 | Endereco I2C |
| `ACCEL_SCALE` | 16.0 | ±16g |
| `GYRO_SCALE` | 2000.0 | ±2000°/s |

### Validacao

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| `VALID_MAX_ACCEL` | 20g | Aceleração maxima |
| `VALID_MIN_PRESSURE` | 30000 Pa | Pressao minima |
| `VALID_MAX_PRESSURE` | 120000 Pa | Pressao maxima |
| `VALID_MAX_VZ` | 200 m/s | Vz maximo |

---

## Sensores

### BME280Sensor

**Arquivos**: `src/sensors/BME280Sensor.h`, `src/sensors/BME280Sensor.cpp`

Driver para o sensor BME280 via I2C. Utiliza a biblioteca `Adafruit_BME280`.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `begin(wire, addr)` | `bool` | Inicializa sensor I2C |
| `getTemperature()` | `float` | Temperatura em Celsius |
| `getPressure()` | `float` | Pressao em Pa |
| `getHumidity()` | `float` | Umidade em % |
| `getAltitude()` | `float` | Altitude em m (relativa ao sea level) |
| `isReady()` | `bool` | Sensor operacional? |
| `setSeaLevelPressure(hPa)` | `void` | Define pressao referencia |

**Conversion factors**: ±16g para acelerometro, ±2000°/s para giroscopio.

### ICM20602Sensor

**Arquivos**: `src/sensors/ICM20602Sensor.h`, `src/sensors/ICM20602Sensor.cpp`

Driver para o IMU ICM-20602 via I2C. Acesso direto aos registradores do sensor.

**WHO_AM_I**: `0x12`

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `begin(addr, wire)` | `bool` | Inicializa e verifica WHO_AM_I |
| `update()` | `void` | Le accel + gyro (6 bytes cada) |
| `getAx()` / `getAy()` / `getAz()` | `float` | Aceleracao m/s² |
| `getGx()` / `getGy()` / `getGz()` | `float` | Velocidade angular rad/s |
| `isReady()` | `bool` | Sensor operacional? |

**Registradores**:
- `0x6B` (PWR_MGMT_1): wake up (bit 6 = 0)
- `0x75` (WHO_AM_I): identificacao
- `0x3B-0x40`: accel data (6 bytes, big-endian)
- `0x43-0x48`: gyro data (6 bytes, big-endian)

**Conversion factors**:
- Accel: `9.80665 / 2048.0` m/s² por LSB (±16g, 16-bit)
- Gyro: `π / (180 * 16.384)` rad/s por LSB (±2000°/s, 16-bit)

### GPSSensor

**Arquivos**: `src/sensors/GPSSensor.h`, `src/sensors/GPSSensor.cpp`

Wrapper para o GPS NEO-8M via Serial1. Utiliza a biblioteca `TinyGPSPlus`.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `begin()` | `bool` | Inicia Serial1 (9600 baud) |
| `update()` | `void` | Alimenta parser com dados seriais |
| `getTimeString()` | `string` | "HH:MM:SS" ou "nan" |
| `getDateString()` | `string` | "DD/MM/YYYY" ou "nan" |
| `getLatitude()` | `float` | Latitude ou NAN |
| `getLongitude()` | `float` | Longitude ou NAN |
| `getAltitude()` | `float` | Altitude MSL (m) ou NAN |
| `getSatellites()` | `uint8_t` | Count ou 0 |
| `isValid()` | `bool` | Fix 3D valido? |
| `isUpdated()` | `bool` | Dados novos? (consome flag) |

**Nota**: `isUpdated()` nao e const porque consome o flag interno.

---

## Modulos de Comunicacao

### LoRaModule

**Arquivos**: `src/modules/LoRaModule.h`, `src/modules/LoRaModule.cpp`

Driver para o radio RFM95W via SPI. Utiliza a biblioteca `LoRa`.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `begin()` | `bool` | Inicializa SPI + LoRa 915MHz |
| `send(message)` | `bool` | Transmite pacote |
| `isReady()` | `bool` | Radio operacional? |

**Configuracao**: SF7, 125kHz bandwidth, 20dBm TX power, CRC habilitado.

### BuzzerModule

**Arquivos**: `src/modules/BuzzerModule.h`, `src/modules/BuzzerModule.cpp`

Feedback sonoro via buzzer piezoeletrico.

**API**:

| Metodo | Descricao |
|--------|-----------|
| `begin()` | Configura pino como output |
| `playStartup()` | 3 beeps curtos (80ms, 80ms pausa) |
| `playError()` | 5 beeps rapidos (80ms, 40ms pausa) |
| `playBeep()` | 1 beep curto (80ms) |
| `playContinuous(ms)` | Tom continuo |
| `stop()` | Para qualquer som |

**Frequencia**: 500 Hz.

### LEDModule

**Arquivos**: `src/modules/LEDModule.h`, `src/modules/LEDModule.cpp`

Feedback visual via LED.

**API**:

| Metodo | Descricao |
|--------|-----------|
| `begin()` | Configura pino como output |
| `on()` | Liga LED |
| `off()` | Desliga LED |
| `blink(times, interval)` | Pisca N vezes |
| `blinkFast(times)` | Pisca rapido (100ms) |
| `toggle()` | Alterna estado |

---

## Modulos de Dados

### TelemetryModule

**Arquivos**: `src/modules/TelemetryModule.h`, `src/modules/TelemetryModule.cpp`

Aggrega dados dos sensores, formata em CSV e transmite via Serial + LoRa.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `begin()` | `bool` | Inicializa LoRa |
| `collectData(bme, icm, gps, data)` | `void` | Preenche SensorData |
| `formatPacket(data, packet)` | `void` | Monta linha CSV |
| `send(packet)` | `bool` | TX Serial + LoRa |
| `getPacketCount()` | `uint32_t` | Contador de pacotes |

**Formato CSV**:
```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi
```

### FilesystemModule

**Arquivos**: `src/modules/FilesystemModule.h`, `src/modules/FilesystemModule.cpp`

Storage com SD primario e LittleFS como fallback (runtime detection).

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `begin()` | `bool` | Tenta SD, fallback LittleFS |
| `createFile(path, header)` | `bool` | Cria arquivo com header |
| `appendLine(line)` | `bool` | Append linha CSV |
| `isReady()` | `bool` | Storage ativo? |
| `getType()` | `StorageType` | SD / LittleFS / NONE |
| `getTypeString()` | `const char*` | "SD" / "LittleFS" / "NONE" |
| `getLineCount()` | `uint32_t` | Numero de linhas |
| `close()` | `void` | Fecha arquivos |

**StorageType enum**:

```cpp
enum StorageType {
    STORAGE_NONE = 0,
    STORAGE_SD,
    STORAGE_LITTLEFS
};
```

---

## lib/calc

Modulos header-only reutilizaveis. Nao dependem de hardware.

### SensorData

**Arquivo**: `lib/calc/SensorData.h`

Struct padronizada com 14 campos:

```cpp
struct SensorData {
    unsigned long millis_ts;
    float ax, ay, az;          // m/s²
    float gx, gy, gz;          // rad/s
    float pressao;              // Pa
    float temperatura;          // °C
    float umidade;              // %
    float altura;                // m (barometrica)
    float vz;                    // m/s
    float mag_giroscopia;        // rad/s
    float lat;                   // graus
    float lon;                   // graus
    float altura_gps;            // m (MSL)
    uint8_t satellites;          // count
};
```

### VerticalVelocity

**Arquivo**: `lib/calc/VerticalVelocity.h`

Calcula velocidade vertical por diferenciacao numerica com filtro EMA.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `update(altura, millis)` | `float` | Vz filtrada (m/s) |
| `current()` | `float` | Valor atual do filtro |
| `previous()` | `float` | Ultimo valor retornado |
| `reset()` | `void` | Reseta estado interno |

**Parametro**: `alpha` (0.0 = max suavizacao, 1.0 = sem filtro). Default: 0.4.

### ApogeeDetection

**Arquivo**: `lib/calc/ApogeeDetection.h`

Detecta apogeu por threshold de Vz negativa.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `update(vz, millis, altitude)` | `bool` | true = apogeu detectado |
| `isDescending()` | `bool` | Em descida? |
| `event()` | `ApogeeEvent&` | Dados do evento |
| `reset()` | `void` | Reseta deteccao |

**ApogeeEvent**:

```cpp
struct ApogeeEvent {
    bool detected;
    unsigned long timestamp_ms;
    float altitude_max;
    float velocidade_max_descida;
};
```

### DataValidation

**Arquivo**: `lib/calc/DataValidation.h`

Valida dados contra NaN e ranges fisicos.

**API**:

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `isValid(data)` | `bool` | Todos campos validos? |
| `config()` | `ValidationConfig&` | Config atual |

**Validacoes**:
- NaN em ax, ay, az, pressao, altura, vz
- Magnitude da accel contra `max_accel_ms2`
- Pressao contra `[min_pressure_pa, max_pressure_pa]`
- |Vz| contra `max_vz_ms`

**Configuracoes predefinidas**:
- `defaultConfig()`: ±16g, 30000-120000 Pa, |Vz| < 100 m/s
- `liberalConfig()`: ±50g, mesmo range de pressao
