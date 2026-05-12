# AGENTS.md - PocketQube LoRa Triangulation

## Build/Upload Commands

```bash
pio run                          # Build all
pio run -e satellite_esp32      # Satellite (ESP32)
pio run -e beacon_esp32c3       # Beacon (ESP32-C3)
pio run -e groundstation_esp32c3 # Ground Station (ESP32-C3)

# Upload (ESP32 uses ttyUSB*, C3 uses ttyACM*)
pio run -e satellite_esp32 -t upload --upload-port /dev/ttyUSB0
pio run -e beacon_esp32c3 -t upload --upload-port /dev/ttyACM0

# Testes nativos (Unity, roda no PC)
pio test -e native               # Todos os testes
pio test -e native -v            # Com verbose

# Serial monitor
pio device monitor -b 115250
```

## Architecture

- **Satellite**: ESP32 DevKit V1 (dual-core) - Core 0 for LoRa/SD, Core 1 for sensors/fusion
- **Beacons/GS**: ESP32-C3 (single-core, 400KB RAM - smaller than ESP32)
- **Build**: PlatformIO with Arduino framework
- **Unit tests**: Native (PC) with Unity framework (`pio test -e native`)
- **Lib modules**: `lib/calc/` — header-only, no hardware deps

## Pinouts (see README for full tables)

| Component | LoRa SPI | GPS UART | I2C | Other |
|-----------|----------|----------|-----|-------|
| Satellite | 19,23,18,5,14,2 | 16,17 | 21,22 | Servo: 4, SD: 15 |
| Beacon | 4,5,6,7,10,3 | 20,21 | - | LED:1, Buzzer:8, Button:2 |

## Key Conventions

- **Language**: C++ (C++11), Portuguese comments/docs
- **Naming**: snake_case functions/variables, SCREAMING_SNAKE_CASE defines, PascalCase classes
- **Memory**: Avoid heap (new/malloc) - use static buffers, ESP32-C3 stack max 2048 bytes
- **Multi-core**: Use `xTaskCreatePinnedToCore()` with core 0 or 1, protect shared data with mutexes
- **Tests**: Each test in own directory under `test/`, Unity framework
- **Lib**: Header-only in `lib/calc/`, no Arduino/ESP32 dependencies

## Critical Constraints

- ESP32-C3: 400KB RAM, 4KB default stack - be conservative
- GPS: min 4 satellites for 3D fix, prefer 6+
- LoRa: 915MHz, check all return values, implement retry with backoff
- Documentation in Portuguese
