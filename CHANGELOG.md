# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-04

### Changed
- Documentacao SRAB refatorada: guias removidos, docs reorganizados em
  `extras/wing-analysis/docs/` (teoria.md, resultados.md, proposta-lasc.md,
  scripts.md)
- `README.md`: corrigido caminho `extras/wing-analisys/` → `extras/wing-analysis/`
- `README.md`: arvore de diretorios atualizada (guides/ removido)

## [1.1.0] - 2026-06-23

### Added
- Watchdog via ESP-IDF `esp_task_wdt` (5s timeout)
- Loop execution time measurement in debug output
- CHANGELOG.md

### Changed
- Buzzer moved from GPIO8 to GPIO0 (avoids I2C SDA conflict)

## [1.0.0] - 2026-06-22

### Added
- Complete firmware for Helike PocketQube (#213 - LASC 2026)
- Modular sensor drivers: BME280Sensor, ICM20602Sensor, GPSSensor
- Communication: LoRaModule (RFM95W, 915MHz)
- Storage: FilesystemModule with SD primary + LittleFS fallback
- Telemetry: CSV formatting, Serial + LoRa dual output
- Feedback: BuzzerModule (startup/error/beep), LEDModule (on/off/blink)
- Calculation modules (lib/calc/): SensorData, VerticalVelocity, ApogeeDetection, DataValidation
- Unit tests: 25 tests (ApogeeDetection, DataValidation, VerticalVelocity) — all passing
- Documentation: software.md, firmware.md, hardware.md, flowchart.md, ADRs
- PlatformIO build: ESP32-C3 Super Mini (RAM 4.7%, Flash 31.8%)

### Hardware
- ESP32-C3 Super Mini (single-core, 400KB RAM)
- BME280 (I2C 0x76): temperature, pressure, humidity, altitude
- ICM-20602 (I2C 0x68): accelerometer ±16g, gyroscope ±2000°/s
- RFM95W (SPI): LoRa 915MHz, SF7, 20dBm
- NEO-8M (UART): GPS with TinyGPSPlus parser
- LED (GPIO1), Buzzer (GPIO0), Button (GPIO2)

[Unreleased]: https://github.com/1barizon/satellite/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/1barizon/satellite/releases/tag/v1.1.0
[1.0.0]: https://github.com/1barizon/satellite/releases/tag/v1.0.0
