# AGENTS.md - PocketQube LoRa Triangulation

## Build/Upload Commands

```bash
pio run                           # Build all
pio run -e groundstation_esp32c3  # ESP32-C3 Super Mini (padrao)

# Upload (ttyACM*)
pio run -e groundstation_esp32c3 -t upload --upload-port /dev/ttyACM0

# Testes nativos (Unity, roda no PC)
pio test -e native                # Todos os testes
pio test -e native -v             # Com verbose

# Serial monitor
pio device monitor -b 115250
```

## Architecture

- **Plataforma unica**: ESP32-C3 Super Mini (single-core, 400KB RAM)
- **Build**: PlatformIO with Arduino framework
- **Unit tests**: Native (PC) with Unity framework (`pio test -e native`)
- **Lib modules**: `lib/calc/` — header-only, no hardware deps

## Pinouts (ESP32-C3 Super Mini)

| Interface | Pinos | Componente |
|-----------|-------|------------|
| I2C | SDA=8, SCL=9 | ICM-20602, BMP280/BME280 |
| LoRa SPI | MOSI=7, MISO=5, SCK=6, CS=10, RST=4, DIO0=3 | SX127x |
| GPS UART | TX=21, RX=20 | NEO-8M |
| LED | 1 | Indicador |
| Buzzer | 8 | Alerta |
| Button | 2 | Entrada |

## Key Conventions

- **Language**: C++ (C++11), Portuguese comments/docs
- **Naming**: snake_case functions/variables, SCREAMING_SNAKE_CASE defines, PascalCase classes
- **Memory**: Avoid heap (new/malloc) - use static buffers, ESP32-C3 stack max 2048 bytes
- **Single-core**: xTaskCreate com core 0, sem FreeRTOS pinning
- **Tests**: Each test in own directory under `test/`, Unity framework
- **Lib**: Header-only in `lib/calc/`, no Arduino/ESP32 dependencies

## Critical Constraints

- ESP32-C3: 400KB RAM, 4KB default stack - be conservative
- GPS: min 4 satellites for 3D fix, prefer 6+
- LoRa: 915MHz, check all return values, implement retry with backoff
- Documentation in Portuguese
