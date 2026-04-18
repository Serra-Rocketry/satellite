# Hardware

## Visao geral

O projeto utiliza placas ESP32/ESP32-C3, LoRa em 915 MHz, GPS NEO-8M e
sensores ambientais/inerciais para telemetria e validacao de voo.

## Componentes principais

- Microcontroladores: ESP32 e ESP32-C3.
- Radio: modulo LoRa SX127x.
- Navegacao: GPS NEO-8M.
- Sensores: BME280 e ICM-20602.
- Armazenamento local para logs de teste.

## Referencias

- BOM principal: `hardware/CDB_bom.md`.
- Artefatos Fritzing/PDF: `hardware/CDB.fzz` e `hardware/CDB.pdf`.
- Guia de bancada: `test/checklist_bancada_pre_sd.md`.
