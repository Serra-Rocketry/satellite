# Software

## Visao geral

O firmware e organizado para coleta de sensores, telemetria LoRa, parse de GPS
e registro de dados para analise pos-voo.

## Blocos funcionais

- **Aquisicao de sensores**: ICM-20602 (I2C), BMP280/BME280 (I2C), GPS NEO-8M (UART).
- **Comunicacao LoRa**: SX127x em 915 MHz para telemetria.
- **Tratamento e serializacao**: Validacao, formatacao CSV, JSON para LoRa.
- **Logging local**: SD com fallback para LittleFS, arquivo persistente com flush periodico.
- **Calculo**: Modulos em `lib/calc/` — Vz (EMA), deteccao de apogeu, validacao de dados.

## lib/calc — Modulos de Calculo (header-only)

| Modulo | Header | Dependencias | Descricao |
|--------|--------|-------------|-----------|
| `SensorData` | `lib/calc/SensorData.h` | nenhuma | Struct padronizada de telemetria |
| `VerticalVelocity` | `lib/calc/VerticalVelocity.h` | math.h | Vz por diferenciacao + filtro EMA |
| `ApogeeDetection` | `lib/calc/ApogeeDetection.h` | nenhuma | Deteccao de apogeu por threshold de Vz |
| `DataValidation` | `lib/calc/DataValidation.h` | math.h, SensorData.h | Validacao contra NaN e ranges |

Nao dependem de Arduino, ESP32 ou qualquer hardware — compilaveis em nativo para testes.

## Base de testes

- Testes unitarios nativos (Unity): `test/` — rodam no PC com `pio test -e native`.
- Testes de hardware: `test_hardware/` — sketches para validacao em placa real.
- Documentacao de testes: `test_hardware/docs/`.

## Build

Config de build em `platformio.ini` com ambientes separados para satelite,
beacon e ground station, alem de `[env:native]` para testes unitarios.

```bash
pio run -e satellite_esp32       # Firmware do satelite
pio run -e groundstation_esp32c3 # Ground station
pio test -e native               # Testes unitarios
```
