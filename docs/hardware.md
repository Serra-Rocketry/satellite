# Hardware Specifications

## Platform

- **Microcontroller**: ESP32-C3 Super Mini (RISC-V single-core, 400KB RAM)
- **Radio**: RFM95W LoRa module (915 MHz, SPI)
- **GPS**: NEO-8M (UART, 9600 baud)
- **Sensors**: BME280 (I2C, primary) with BMP280 fallback, ICM-20602 (I2C)
- **Storage**: SD card slot (GPIO10, SPI) + LittleFS flash (fallback)
- **Actuators**: LED (GPIO3), Active buzzer (GPIO0)

## Pinout (ESP32-C3 Super Mini — per schematic)

```text
                     ESP32-C3 Super Mini
  ┌─────────────────────────────────────────────┐
  │  0  BUZZER ─────────── Active buzzer        │
  │  1  RESET ──────────── RFM95W (LoRa RST)    │
  │  2  DIO0 ───────────── RFM95W (LoRa IRQ)    │
  │  3  LED ────────────── Status indicator     │
  │  4  SCK ─── SPI ────── RFM95W + SD Card     │
  │  5  MISO ── SPI ────── RFM95W + SD Card     │
  │  6  MOSI ── SPI ────── RFM95W + SD Card     │
  │  7  NSS ────────────── RFM95W (LoRa CS)     │
  │  8  SDA ─── I2C ────── BME280 + ICM-20602   │
  │  9  SCL ─── I2C ────── BME280 + ICM-20602   │
  │ 10  CS_SD ──────────── SD Card (CS)          │
  │ 20  TX_GPS ── UART ─── GPS NEO-8M (TX)      │
  │ 21  RX_GPS ── UART ─── GPS NEO-8M (RX)      │
  └─────────────────────────────────────────────┘
```

### Pin Summary Table

| GPIO | Label       | Function / Protocol | Connected To              |
|------|-------------|---------------------|---------------------------|
| 0    | BUZZER      | GPIO (digitalWrite) | Active buzzer              |
| 1    | RESET       | GPIO output         | RFM95W (pin 6, RST)      |
| 2    | DIO0        | GPIO input (IRQ)    | RFM95W (pin 14, DIO0)    |
| 3    | LED         | GPIO output         | Status indicator          |
| 4    | SCK         | SPI Clock           | RFM95W + SD Card          |
| 5    | MISO        | SPI MISO            | RFM95W + SD Card          |
| 6    | MOSI        | SPI MOSI            | RFM95W + SD Card          |
| 7    | NSS         | SPI Chip Select     | RFM95W (LoRa CS)          |
| 8    | SDA         | I2C Data            | BME280 + ICM-20602        |
| 9    | SCL         | I2C Clock           | BME280 + ICM-20602        |
| 10   | CS_SD       | SPI Chip Select     | SD Card module (CS)       |
| 20   | TX_GPS      | UART RX (ESP input) | GPS NEO-8M (TX pin)       |
| 21   | RX_GPS      | UART TX (ESP output)| GPS NEO-8M (RX pin)       |

### Notes

- **SPI bus is shared** between RFM95W and SD Card (same MOSI/MISO/SCK). Each has a
  dedicated CS pin: LoRa CS = GPIO7, SD CS = GPIO10.
- **I2C bus is shared** between BME280/BMP280 and ICM-20602. Both use address 0x76
  (BME/BMP) and 0x69 (ICM).
- **UART**: GPS uses Serial1 with custom pins RX=GPIO20, TX=GPIO21.
- **Buzzer**: Active buzzer (built-in oscillator) — controlled via `digitalWrite`.
  No PWM required.

## Sensor Specifications

### BME280/BMP280 (Environmental — BMP280 fallback)

| Parameter        | Value                              |
|------------------|------------------------------------|
| Interface        | I2C                                |
| Address          | 0x76 (SDO=GND) or 0x77 (SDO=VCC)  |
| Pressure range   | 300-1100 hPa                       |
| Temperature range| -40 to +85°C                       |
| Humidity range   | 0-100% RH (BME280 only, N/A on BMP280) |
| I2C speed        | 400 kHz (Fast Mode)                |

**Fallback strategy**: The firmware tries BME280 first. If not found, falls back
to BMP280. `getHumidity()` returns NAN when using BMP280 (no humidity sensor).

### ICM-20602 (IMU)

| Parameter   | Accelerometer      | Gyroscope            |
|-------------|--------------------|----------------------|
| Interface   | I2C                | I2C                  |
| Address     | 0x69               | 0x69                 |
| Range       | ±16g (±157 m/s²)   | ±2000°/s (±34.9 rad/s)|
| Resolution  | 16-bit             | 16-bit               |
| Sensitivity | 2048 LSB/g         | 16.384 LSB/°/s       |

### NEO-8M (GPS)

| Parameter      | Value              |
|----------------|--------------------|
| Interface      | UART (Serial1)     |
| Baud rate      | 9600               |
| Protocol       | NMEA 0183          |
| Update rate    | 1 Hz (default)     |
| Fix types      | 2D, 3D             |
| Min satellites | 4 (3D fix)         |

### RFM95W (LoRa Radio)

| Parameter       | Value          |
|-----------------|----------------|
| Interface       | SPI            |
| Frequency       | 915 MHz        |
| Sync Word       | 0xF3           |
| Spreading Factor| 7              |
| Bandwidth       | 125 kHz        |
| Coding Rate     | 4/5            |
| CRC             | Enabled        |
| TX Power        | 20 dBm         |

## LoRa Compatibility

Satellite and receiver MUST use identical LoRa parameters:

| Parameter | Satellite | Receiver |
|-----------|-----------|----------|
| Frequency | 915 MHz   | 915 MHz  |
| Sync Word | 0xF3      | 0xF3     |
| SF        | 7         | 7        |
| BW        | 125 kHz   | 125 kHz  |
| CR        | 4/5       | 4/5      |
| CRC       | Enabled   | Enabled  |

## Known ESP32-C3 Issues

### 1. tone() / LEDC Bug
The Arduino core for ESP32-C3 has a bug where `tone()` fails with
`ledc: ledc_get_duty(745): LEDC is not initialized`.
**Fix**: Use `ledcSetup()` + `ledcAttachPin()` + `ledcWrite()` instead of `tone()`.
(The buzzer module uses `digitalWrite` since the active buzzer has a built-in
oscillator — no PWM needed. The bug remains relevant for passive buzzers or
PWM-driven peripherals.)

### 2. USB CDC Serial
`Serial.println()` output does not appear unless the firmware is compiled with:
```
-D ARDUINO_USB_MODE=1 -DARDUINO_USB_CDC_ON_BOOT=1
```
Without these flags, Serial uses UART0 (pins GPIO20/21) instead of USB CDC.

### 3. I2C Bus Recovery
`resetI2C()` (toggling SCL via pinMode/digitalWrite) breaks the I2C peripheral
configuration on ESP32-C3. **Do not use GPIO-level recovery with TwoWire.**

### 4. Shared SPI Bus: SD + LoRa (bench session 2026-08-24)

The SD card and RFM95W share SCK/MISO/MOSI. Three rules discovered during
first power-on testing (full rationale in ADR-005):

- **Initialize SPI exactly once** in `main.cpp`, with CS pins HIGH, before
  any library touches the bus. Libraries (`SD`, LoRa sandeepmistry) call
  `SPI.begin()` internally on their own `begin()`; a second init corrupts
  the peripheral state.
- **Boot order: LoRa first, storage after.** An SD mount attempt before
  radio configuration makes every subsequent `endPacket()` fail. The
  reverse order is safe: after a failed `SD.begin()`, TX still works.
- **Never call `SD.end()` or re-`begin()` SPI at runtime.** Both tear down
  the peripheral shared with the radio.

Additional SD notes:
- SD mount needs ≥74 wake-up clocks with CS high before CMD0;
  `FilesystemModule::setupSD()` sends them manually.
- If `appendLine()` fails 5× consecutively in flight, the module degrades
  to LittleFS automatically (no code path requires SD).
- Cards must be FAT32; exFAT mounts fail with `f_mount failed (13)`.
- **Wiring**: long untwisted dupont jumpers between ESP and RFM95W cause
  intermittent SPI corruption (worked/failed depending on cable position).
  Keep SPI leads short (<10 cm); if twisted pairs are used, twist each
  signal with GND, never signal-with-signal.

### 5. LoRa sandeepmistry Library API Notes

- `LoRa.endPacket()` returns **1 on success**, 0 on failure. Check
  `== 1`. (A pre-existing inverted check reported every successful TX as
  an error for the module's whole early life.)
- Use `LoRa.setSPI(SPI)` before `LoRa.setPins()` so the library shares
  the bus instance initialized by `main.cpp`.
