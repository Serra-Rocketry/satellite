# Helike — PocketQube Mission (#213 - LASC 2026)

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](.)
[![License](https://img.shields.io/badge/license-MIT-blue)](.)
[![Platform](https://img.shields.io/badge/platform-ESP32--C3-orange)](.)

PocketQube satellite project by **Serra Rocketry Team** for the Latin American
Space Challenge (LASC) 2026. Focus on bioinspired autorotating recovery system
(SRAB) and LoRa-based telemetry triangulation.

## Overview

The Helike satellite collects flight telemetry (IMU, barometric data, GPS)
and transmits it via LoRa radio at 915 MHz to a ground station. The payload
is a passive autorotating recovery system inspired by maple seed aerodynamics.

## Features

- BME280 environmental sensor (temperature, pressure, humidity)
- ICM-20602 6-axis IMU (accelerometer + gyroscope)
- NEO-8M GPS receiver (position, altitude, time)
- RFM95W LoRa radio (915 MHz, SF7, 125 kHz)
- SD card (primary) + LittleFS (fallback) data logging
- 18-field CSV telemetry packet format
- Vertical velocity computation (EMA filter)
- Automatic apogee detection
- Data validation (NaN + physical range checks)
- 5 Hz sample rate

## Hardware Requirements

| Component | Model | Interface |
|-----------|-------|-----------|
| MCU | ESP32-C3 Super Mini | - |
| Barometric | BME280 (or BMP280) | I2C (0x76) |
| IMU | ICM-20602 | I2C (0x69) |
| GPS | NEO-8M | UART (9600 baud) |
| Radio | RFM95W | SPI (915 MHz) |
| Storage | microSD card + LittleFS | SPI / flash |

## Software Requirements

- [PlatformIO](https://platformio.org/) (VS Code extension or CLI)
- Python 3.8+ (for analysis scripts in `extras/`)

Dependencies managed automatically by PlatformIO:

| Library | Version |
|---------|---------|
| sandeepmistry/LoRa | ^0.8.0 |
| Adafruit BME280 Library | ^2.2.4 |
| Adafruit BMP280 Library | ^2.6.8 |
| TinyGPSPlus | ^1.0.3 |

## Quick Start

### 1. Build the Firmware

```bash
pio run -e helike_esp32c3
```

### 2. Upload to Satellite

```bash
pio run -e helike_esp32c3 -t upload --upload-port /dev/ttyACM0
```

### 3. Monitor Serial Output

```bash
pio device monitor -b 115200
```

### 4. Run Unit Tests

```bash
pio test -e native
```

## Repository Structure

```text
satellite/
├── src/                       # Main firmware source
│   ├── main.cpp               # Entry point (setup + loop)
│   ├── config.h               # Global configuration
│   ├── sensors/               # Sensor drivers (ISensor interface)
│   │   ├── BME280Sensor.h/.cpp
│   │   ├── ICM20602Sensor.h/.cpp
│   │   └── GPSSensor.h/.cpp
│   └── modules/               # System modules
│       ├── LoRaModule.h/.cpp
│       ├── TelemetryModule.h/.cpp
│       ├── FilesystemModule.h/.cpp
│       ├── LEDModule.h/.cpp
│       └── BuzzerModule.h/.cpp
├── lib/calc/                  # Header-only calculation library
│   ├── SensorData.h
│   ├── VerticalVelocity.h
│   ├── ApogeeDetection.h
│   └── DataValidation.h
├── test/                      # Native unit tests (Unity)
│   ├── test_vz/
│   ├── test_apogee/
│   └── test_validation/
├── test_hardware/             # Hardware validation sketches
│   ├── sensor/                # Isolated sensor tests
│   ├── integration/           # Multi-sensor integration
│   └── storage/               # Filesystem tests
├── docs/                      # Documentation
│   ├── software.md
│   ├── hardware.md
│   ├── firmware.md
│   ├── flowchart.md
│   └── adr/                   # Architecture Decision Records
├── extras/
│   └── wing-analysis/         # SRAB aerodynamic study
├── hardware/                  # CAD and PCB files
└── platformio.ini             # PlatformIO configuration
```

## Documentation

| Document | Description |
|----------|-------------|
| [Software Architecture](docs/software.md) | Module structure, data flow, validation |
| [Hardware Specs](docs/hardware.md) | Pinout, sensors, LoRa configuration |
| [Firmware Guide](docs/firmware.md) | Build, upload, testing, debug |
| [Flowcharts](docs/flowchart.md) | System diagrams (Mermaid) |
| [ADRs](docs/adr/) | Architecture Decision Records |
| [Hardware Tests](test_hardware/docs/) | Bench guides and checklists |
| [Wing Analysis](extras/wing-analysis/docs/) | SRAB aerodynamics |

## Development Workflow

1. Validate individual sensors in `test_hardware/sensor/`
2. Run integration tests in `test_hardware/integration/`
3. Execute unit tests: `pio test -e native`
4. Run aerodynamic studies: `extras/wing-analysis/`
5. Consolidate results in technical documentation
6. Integrate final firmware

## Quality Tools

```bash
# Markdown linting
npx -y markdownlint-cli "README.md" "docs/**/*.md" "test_hardware/docs/**/*.md" "extras/**/*.md" "hardware/**/*.md"

# Native unit tests
pio test -e native
```

## License

MIT License — see LICENSE file for details.

## Team

**Serra Rocketry Team** — Missão Helike (#213 - LASC 2026)
