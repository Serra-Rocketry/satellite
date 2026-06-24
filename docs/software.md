# Software

## Visao geral

Firmware da missao Helike (#213 - LASC 2026) — Serra Rocketry.
Organizado para coleta de sensores, telemetria LoRa, parse de GPS e registro
de dados para analise pos-voo.

**Contexto critico**: O satellite fica completamente desligado (sem energia) ate
o deploy do foguete no apogeu. Ao receber energia, o sistema ja esta em descida.
Nao ha modo sleep, nao ha FSM de voo — apenas loop continuo de leitura e
transmissao.

## Arquitetura

```
src/
  main.cpp               — Entry point: setup() + loop()
  config.h               — Configuracoes globais (pinos, thresholds, intervalos)
  sensors/
    BME280Sensor.h/cpp   — Driver BME280 (I2C 0x76)
    ICM20602Sensor.h/cpp — Driver ICM-20602 (I2C 0x68, WHO_AM_I = 0x12)
    GPSSensor.h/cpp      — Wrapper TinyGPSPlus (Serial1 9600 baud)
  modules/
    LoRaModule.h/cpp     — Radio RFM95W (915 MHz, SPI)
    BuzzerModule.h/cpp   — Feedback sonoro (piezo)
    LEDModule.h/cpp      — Feedback visual
    TelemetryModule.h/cpp — Coleta + formatacao CSV + TX Serial/LoRa
    FilesystemModule.h/cpp — SD primario + LittleFS fallback
lib/calc/
  SensorData.h           — Struct padronizada de telemetria (14 campos)
  VerticalVelocity.h     — Vz por diferenciacao + filtro EMA
  ApogeeDetection.h    — Deteccao de apogeu por threshold de Vz
  DataValidation.h       — Validacao contra NaN e ranges fisicos
test/
  test_apogee/           — 7 testes ApogeeDetection (Unity)
  test_validation/       — 10 testes DataValidation (Unity)
  test_vz/               — 6 testes VerticalVelocity (Unity)
```

## Blocos funcionais

| Bloco | Modulo(s) | Responsabilidade |
|-------|-----------|-----------------|
| Sensores | BME280Sensor, ICM20602Sensor, GPSSensor | Leitura de dados fisicos |
| Comunicacao | LoRaModule | Telemetria via radio 915MHz |
| Logging | FilesystemModule | Armazenamento SD/LittleFS |
| Calculo | lib/calc/ | Vz, apogeu, validacao |
| Feedback | BuzzerModule, LEDModule | Indicacao visual/sonora |
| Telemetria | TelemetryModule | Aggregacao + formatacao + TX |

## lib/calc — Modulos de Calculo (header-only)

| Modulo | Header | Dependencias | Descricao |
|--------|--------|-------------|-----------|
| `SensorData` | `lib/calc/SensorData.h` | nenhuma | Struct padronizada de telemetria |
| `VerticalVelocity` | `lib/calc/VerticalVelocity.h` | math.h | Vz por diferenciacao + filtro EMA |
| `ApogeeDetection` | `lib/calc/ApogeeDetection.h` | nenhuma | Deteccao de apogeu por threshold de Vz |
| `DataValidation` | `lib/calc/DataValidation.h` | math.h, SensorData.h | Validacao contra NaN e ranges |

Nao dependem de Arduino, ESP32 ou qualquer hardware — compilaveis em nativo
para testes unitarios.

## Formato de Telemetria (CSV)

O satellite transmite 18 campos via LoRa. O receiver preenche hora/data com GPS
local e retransmite 21 campos para o Recovery WebUI.

Formato do satellite (18 campos, via LoRa):
```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi
```

Exemplo:
```
#213,1205,1,152.30,25.30,45.20,1013.25,0.10,-0.20,0.05,0.12,-0.05,1.02,156.50,-22.908500,-43.176300,7,0,-1
```

Formato completo (21 campos, receiver -> WebUI via Serial):
```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,rssi
```

Campos `hora` e `data` sao preenchidos pelo receiver com GPS local. Campo `rssi`
e medido pelo receiver (placeholder -1 do satellite e substituido).

## Storage (SD + LittleFS Fallback)

O sistema segue o padrao do `test_hardware/storage/sd_littlefs_fallback`:

1. Tenta `SD.begin(CS)` primeiro
2. Se falhar, usa `LittleFS.begin(true)` como fallback
3. Dispatch automatico baseado no tipo ativo

Em voo real (sem SD card), o sistema detecta ausencia e usa LittleFS.
Em bancada (com SD), grava no SD para facilidade de leitura.

## Build e Testes

```bash
pio run -e helike_esp32c3          # Build ESP32-C3 Super Mini
pio run -e helike_esp32c3 -t upload --upload-port /dev/ttyACM0  # Upload
pio test -e native                  # Testes unitarios (25 testes)
pio device monitor -b 115200        # Serial monitor
```

## Uso de Recursos (ESP32-C3)

| Recurso | Uso | Disponivel |
|---------|-----|------------|
| RAM | ~15.5 KB (4.7%) | 320 KB |
| Flash | ~417 KB (31.8%) | 1.3 MB |

## Convencoes de Codigo

- **Linguagem**: C++11, Arduino framework
- **Naming**: snake_case funcoes/variaveis, SCREAMING_SNAKE_CASE defines, PascalCase classes
- **Memoria**: Sem heap (new/malloc) — objetos globais estaticos
- **Validacao**: Cada leitura de sensor validada antes de uso
- **Documentacao**: Doxygen comments em PT-BR nos headers
- **Indentacao**: 2 espacos
- **Encoding**: UTF-8
