# Hardware

## Visao geral

Plataforma unica: **ESP32-C3 Super Mini** com LoRa 915 MHz, GPS NEO-8M e
sensores ambientais/inerciais para telemetria e validacao de voo.

## Componentes principais

- **Microcontrolador**: ESP32-C3 Super Mini (single-core, 400KB RAM).
- **Radio**: modulo LoRa SX127x (915 MHz).
- **Navegacao**: GPS NEO-8M (UART).
- **Sensores**: BME280 (pressao/temp/umidade) e ICM-20602 (IMU).
- **Armazenamento**: SD cartao + fallback LittleFS.

## Pinagem (ESP32-C3 Super Mini)

| Interface | Pinos | Componente |
|-----------|-------|------------|
| I2C | SDA=GPIO8, SCL=GPIO9 | ICM-20602, BMP280/BME280 |
| LoRa SPI | MOSI=GPIO7, MISO=GPIO5, SCK=GPIO6, CS=GPIO10, RST=GPIO4, DIO0=GPIO3 | SX127x |
| GPS UART | TX=GPIO21, RX=GPIO20 | NEO-8M |
| LED | GPIO1 | Indicador |
| Buzzer | GPIO8 | Alerta |
| Button | GPIO2 | Entrada |

## Referencias

- BOM principal: `hardware/CDB_bom.md`.
- Artefatos Fritzing/PDF: `hardware/CDB.fzz` e `hardware/CDB.pdf`.
- Guia de bancada: `test_hardware/docs/checklist_bancada_pre_sd.md`.
