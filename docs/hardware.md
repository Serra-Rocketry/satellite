# Hardware Specifications

## Platform

- **Microcontroller**: ESP32-C3 Super Mini (RISC-V single-core, 400KB RAM)
- **Radio**: RFM95W LoRa module (915 MHz, SPI)
- **GPS**: NEO-8M (UART, 9600 baud)
- **Sensors**: BME280 (I2C), ICM-20602 (I2C)
- **Storage**: SD card slot (primary) + LittleFS flash (fallback)
- **Actuators**: LED (indicator), Piezo buzzer (audio alert), Button (input)

## Pinout (ESP32-C3 Super Mini)

```text
┌─────────────────────────────────────────────┐
│  ESP32-C3 Super Mini                        │
│                                             │
│  GPIO8  (SDA) ───── I2C ───── BME280       │
│  GPIO9  (SCL) ───── I2C ───── ICM-20602    │
│                                             │
│  GPIO6  (MOSI) ─┐                           │
│  GPIO5  (MISO) ─┤ SPI ─────── RFM95W (CS=7)│
│  GPIO4  (SCK)  ─┘            SD Card (CS=5)│
│  GPIO7  (CS)                                │
│  GPIO0  (RST)                               │
│  GPIO1  (DIO0)                              │
│                                             │
│  GPIO20 (RX) ──── UART ───── NEO-8M GPS    │
│  GPIO21 (TX)                                │
│                                             │
│  GPIO1  ───────── LED (indicator)           │
│  GPIO0  ───────── Buzzer (piezo)            │
│  GPIO2  ───────── Button (input)            │
└─────────────────────────────────────────────┘
```

### Pin Summary Table

| Interface | Function | GPIO Pin | Component |
|-----------|----------|----------|-----------|
| I2C | SDA | 8 | BME280, ICM-20602 |
| I2C | SCL | 9 | BME280, ICM-20602 |
| SPI | MOSI | 6 | RFM95W, SD Card |
| SPI | MISO | 5 | RFM95W, SD Card |
| SPI | SCK | 4 | RFM95W, SD Card |
| SPI | CS (LoRa) | 7 | RFM95W |
| SPI | CS (SD) | 10 | SD Card |
| LoRa | RST | 0 | RFM95W |
| LoRa | DIO0 | 1 | RFM95W |
| UART | RX | 20 | NEO-8M GPS |
| UART | TX | 21 | NEO-8M GPS |
| Digital | LED | 1 | Status indicator |
| Digital | Buzzer | 0 | Audio alert |
| Digital | Button | 2 | User input |

## Sensor Specifications

### BME280 (Environmental)

| Parameter | Value |
|-----------|-------|
| Interface | I2C |
| Address | 0x76 (SDO=GND) or 0x77 (SDO=VCC) |
| Pressure range | 300-1100 hPa |
| Temperature range | -40 to +85°C |
| Humidity range | 0-100% RH |
| I2C speed | 400 kHz (Fast Mode) |

### ICM-20602 (IMU)

| Parameter | Accelerometer | Gyroscope |
|-----------|--------------|-----------|
| Interface | I2C | I2C |
| Address | 0x69 | 0x69 |
| Range | ±16g (±157 m/s²) | ±2000°/s (±34.9 rad/s) |
| Resolution | 16-bit | 16-bit |
| LSB sensitivity | 2048 LSB/g | 16.384 LSB/°/s |

### NEO-8M (GPS)

| Parameter | Value |
|-----------|-------|
| Interface | UART (Serial1) |
| Baud rate | 9600 |
| Protocol | NMEA 0183 |
| Update rate | 1 Hz (default) |
| Fix types | 2D, 3D |
| Min satellites (3D fix) | 4 |

### RFM95W (LoRa Radio)

| Parameter | Value |
|-----------|-------|
| Interface | SPI |
| Frequency | 915 MHz (Americas) |
| Sync Word | 0xF3 |
| Spreading Factor | 7 |
| Bandwidth | 125 kHz |
| Coding Rate | 4/5 |
| CRC | Enabled |
| TX Power | 20 dBm |

## LoRa Compatibility

The satellite and ground station receiver MUST use identical LoRa parameters:

| Parameter | Satellite | Receiver |
|-----------|-----------|----------|
| Frequency | 915 MHz | 915 MHz |
| Sync Word | 0xF3 | 0xF3 |
| SF | 7 | 7 |
| BW | 125 kHz | 125 kHz |
| CR | 4/5 | 4/5 |
| CRC | Enabled | Enabled |

## Power Supply

- 3.3V regulated (ESP32-C3 built-in regulator)
- All peripherals operate at 3.3V
- Maximum current: ~300mA (all modules active, LoRa transmitting)
