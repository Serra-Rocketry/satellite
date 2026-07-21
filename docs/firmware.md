# Firmware Guide

## Build System

The project uses **PlatformIO** with two environments:

| Environment | Target | Purpose |
|-------------|--------|---------|
| `helike_esp32c3` | ESP32-C3 | Satellite firmware |
| `native` | PC (x86_64) | Unit tests (Unity) |

### Dependencies

Managed automatically by PlatformIO (`lib_deps` in platformio.ini):

| Library | Version | Used By |
|---------|---------|---------|
| `sandeepmistry/LoRa` | ^0.8.0 | LoRaModule (RFM95W) |
| `adafruit/Adafruit BME280 Library` | ^2.2.4 | BME280Sensor |
| `mikalhart/TinyGPSPlus` | ^1.0.3 | GPSSensor |

### Build Configuration

Key settings in `platformio.ini`:

```ini
[env:helike_esp32c3]
board = esp32-c3-devkitm-1
board_build.mcu = esp32c3
board_build.f_cpu = 160000000L
build_src_filter = +<*> -<sensors_disabled/**>
build_flags =
    -D CORE_DEBUG_LEVEL=4
    -D CONFIG_FREERTOS_UNICORE=1
    -D SERIAL_USB_BUFFER_SIZE=64
    -I lib
```

The `build_src_filter` excludes the `sensors_disabled/` directory (legacy
GPSModule files kept for reference).

## Build and Upload Commands

### Build All

```bash
pio run
```

### Build ESP32-C3 Firmware

```bash
pio run -e helike_esp32c3
```

### Upload to Satellite

```bash
pio run -e helike_esp32c3 -t upload --upload-port /dev/ttyACM0
```

### Serial Monitor

```bash
pio device monitor -b 115200
```

### Run Unit Tests

```bash
pio test -e native            # All tests
pio test -e native -v         # Verbose output
```

## Hardware Test Sketches

Individual `.ino` sketches in `test_hardware/` validate specific hardware
components before integration.

### Sensor tests (`test_hardware/sensor/`)

| Sketch | Tests |
|--------|-------|
| `bme280/bme280.ino` | BME280 temperature, pressure, humidity, altitude |
| `bmp280/bmp280.ino` | BMP280 temperature, pressure, altitude |
| `gps_neo8m/gps_neo8m.ino` | NEO-8M GPS NMEA parsing |
| `icm20602/icm20602.ino` | ICM-20602 accelerometer, gyroscope |

### Integration tests (`test_hardware/integration/`)

| Sketch | Description |
|--------|-------------|
| `sensor_logging_lfs/` | ICM-20602 + BMP280, LittleFS logging |
| `sensor_logging_lfs_v2/` | v2: +20Hz, Vz, validation, apogee detection |
| `sensor_logging_v3/` | v3: +GPS NEO-8M, 15-column CSV |
| `sensor_logging_fallback/` | SD + LittleFS fallback with persistent file |

### Storage tests (`test_hardware/storage/`)

| Sketch | Description |
|--------|-------------|
| `sd_bare/` | Bare SD card read/write |
| `bmp280_littlefs/` | BMP280 + SPIFFS/LittleFS |
| `sd_littlefs_fallback/` | SD failed -> LittleFS fallback |

### Compile and Upload a Hardware Test

```bash
# Method 1: Using PlatformIO CLI
pio run -e helike_esp32c3 --project-option="src_dir=test_hardware/sensor/bme280"

# Method 2: Open .ino in VS Code with PlatformIO and click Upload
```

## Firmware Boot Sequence

```text
Power On
  │
  ├─ Serial (115200 baud, wait 2s for USB)
  ├─ I2C (400 kHz Fast Mode)
  ├─ Buzzer + LED (indicate startup)
  ├─ BME280 (I2C address 0x76)
  ├─ ICM-20602 (I2C address 0x69, WHO_AM_I = 0x12)
  ├─ GPS (Serial1, 9600 baud)
  ├─ LoRa (RFM95W, 915 MHz)
  ├─ Storage (SD > LittleFS)
  ├─ Watchdog (5s timeout)
  │
  └─ Main Loop (5 Hz)
       ├─ Read GPS
       ├─ Update IMU
       ├─ Collect sensor data
       ├─ Validate (NaN + range checks)
       ├─ Calculate Vz (EMA filter)
       ├─ Format CSV packet
       ├─ Transmit (Serial + LoRa)
       ├─ Log (SD/LittleFS)
       ├─ Toggle LED
       └─ Feed watchdog
```

## Debugging

The system provides three debug outputs:

1. **Serial console** (115200 baud): All initialization messages and periodic
   debug prints every 2 seconds
2. **LED heartbeat**: Toggles every sample (5 Hz = 10 toggles/sec)
3. **Buzzer tones**: Startup (3 beeps) or error (5 beeps) on init

### Debug Configuration

In `src/config.h`:

```cpp
#define DEBUG_ENABLED      1     // Enable serial debug output
#define LORA_DEBUG_LOGS    0     // Enable LoRa-specific debug
```

### Watchdog

The ESP32-C3 TWDT (Task WatchDog Timer) is configured with a 5-second timeout.
If `esp_task_wdt_reset()` is not called within this window, the system resets.
This prevents lockups from I2C hangs or sensor stalls.
