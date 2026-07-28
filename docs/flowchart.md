# System Flowcharts

## Boot and Initialization Sequence

```mermaid
flowchart TD
    START[Power On] --> SERIAL[Serial Init\n115200 baud]
    SERIAL --> I2C[I2C Init\nSDA=8, SCL=9, 400kHz]
    I2C --> ACT[Buzzer + LED Init]
    ACT --> BME{BME280 Init\n0x76}
    BME -->|OK| BME_OK[✓ BME Ready]
    BME -->|FAIL| BME_FAIL[✗ BME Error]
    BME_OK --> ICM{ICM-20602 Init\n0x69}
    BME_FAIL --> ICM
    ICM -->|OK| ICM_OK[✓ ICM Ready]
    ICM -->|FAIL| ICM_FAIL[✗ ICM Error]
    ICM_OK --> GPS[GPS Init\nSerial1 9600]
    ICM_FAIL --> GPS
    GPS --> LORA{LoRa Init\nRFM95W 915MHz}
    LORA -->|OK| LORA_OK[✓ LoRa Ready]
    LORA -->|FAIL| LORA_FAIL[✗ LoRa Error]
    LORA_OK --> FS{Storage Init\nSD > LittleFS}
    LORA_FAIL --> FS
    FS -->|OK| FS_OK[✓ FS Ready\nCreate telemetry.csv]
    FS -->|FAIL| FS_FAIL[✗ No Storage]
    FS_OK --> WDT[Watchdog Init\n5s timeout]
    FS_FAIL --> WDT
    WDT --> STATUS[Print Status Summary]
    STATUS --> FB{All Critical Sensors OK?}
    FB -->|Yes| STARTUP_BEEP[3 beeps\n3 blinks]
    FB -->|No| ERROR_BEEP[5 beeps\n10 fast blinks]
    STARTUP_BEEP --> LOOP
    ERROR_BEEP --> LOOP
    LOOP[Enter Main Loop\n5 Hz]
```

## Main Telemetry Loop

```mermaid
flowchart TD
    LOOP[Loop Start] --> GPS_UPDATE[GPS Update\nContinuous NMEA parsing]
    GPS_UPDATE --> CHECK_SAMPLE{Time since\nlast sample > 200ms?}
    CHECK_SAMPLE -->|No| LOOP
    CHECK_SAMPLE -->|Yes| WDT_RESET[Feed Watchdog]
    WDT_RESET --> IMU_UPDATE[ICM-20602 Update\nRead accel + gyro]
    IMU_UPDATE --> COLLECT[Collect All Sensor Data\nBME + ICM + GPS]
    COLLECT --> VALIDATE{Data Valid?\nNaN + Range Check}
    VALIDATE -->|No| SKIP[Skip: set NaN]
    VALIDATE -->|Yes| VZ_CALC[Calculate Vz\nEMA filter alpha=0.4]
    VZ_CALC --> GYRO_MAG[Calculate Gyro Magnitude]
    SKIP --> GYRO_MAG
    GYRO_MAG --> FORMAT[Format 18-field CSV Packet]
    FORMAT --> LORA_TX{LoRa Send}
    LORA_TX -->|Success| LORA_OK2[✓]
    LORA_TX -->|Fail| LORA_FAIL2[✗ Count failure]
    LORA_OK2 --> FS_LOG{FS AppendLine}
    LORA_FAIL2 --> FS_LOG
    FS_LOG -->|Success| FS_OK2[✓]
    FS_LOG -->|Fail| FS_FAIL2[✗ Count failure]
    FS_OK2 --> LED[Toggle Heartbeat LED]
    FS_FAIL2 --> LED
    LED --> DEBUG{Debug Enabled\nand 2s elapsed?}
    DEBUG -->|Yes| PRINT[Print Status:\nCounts, Vz, Failures]
    DEBUG -->|No| SKIP_PRINT
    PRINT --> SKIP_PRINT
    SKIP_PRINT --> UPDATE_TS[Update last_sample\n= now]
    UPDATE_TS --> LOOP
```

## Data Validation Pipeline

```mermaid
flowchart LR
    RAW[Raw Sensor Data] --> NAN{NaN Check\nax, ay, az,\npressure, altitude, vz}
    NAN -->|Any NaN| REJECT[✗ Reject Packet]
    NAN -->|All valid| ACCEL_MAG{Accel Magnitude\n< 20g?}
    ACCEL_MAG -->|≥ 20g| REJECT
    ACCEL_MAG -->|< 20g| PRESSURE{Pressure Range\n30-120 kPa?}
    PRESSURE -->|Out of range| REJECT
    PRESSURE -->|In range| VZ_RANGE{|Vz| < 200 m/s?}
    VZ_RANGE -->|≥ 200 m/s| REJECT
    VZ_RANGE -->|< 200 m/s| ACCEPT[✓ Valid Data → Process & Transmit]
```

## Storage Fallback Decision

```mermaid
flowchart TD
    FS_INIT[FilesystemModule::begin] --> TRY_SD{SD.begin\nCS=GPIO5}
    TRY_SD -->|Success| SD_OK[Type = STORAGE_SD]
    TRY_SD -->|Fail| TRY_LFS{LittleFS.begin}
    TRY_LFS -->|Success| LFS_OK[Type = STORAGE_LITTLEFS]
    TRY_LFS -->|Fail| NONE[Type = STORAGE_NONE]
    SD_OK --> CREATE_FILE[Create /telemetry.csv\nWrite CSV Header]
    LFS_OK --> CREATE_FILE
    NONE --> LOG_ERROR[Log: No Storage Available]
    CREATE_FILE --> READY[System Ready]

    subgraph Runtime Ops
        APPEND[appendLine] --> DISPATCH{Storage Type?}
        DISPATCH -->|SD| SD_APPEND[SD.open APPEND]
        DISPATCH -->|LittleFS| LFS_APPEND[LittleFS.open APPEND]
        DISPATCH -->|NONE| SKIP_APPEND[Skip - No Storage]
    end
```

## LoRa Telemetry Packet (Satellite → Receiver)

```mermaid
sequenceDiagram
    participant S as Satellite
    participant L as LoRa RF
    participant R as Receiver

    loop Every 200ms (5Hz)
        S->>S: Read Sensors
        S->>S: Validate + Compute Vz
        S->>S: Format CSV (18 fields)
        S->>L: beginPacket()
        S->>L: print(CSV)
        S->>L: endPacket()
        L-->>R: RF Packet (915MHz, SF7, 125kHz)
        R->>R: Receive + Decode
        R->>R: Add Timestamp + RSSI
        R->>R: Forward to WebUI (21 fields)
    end
```

## Hardware Test Flowchart

```mermaid
flowchart TD
    A[Hardware Validation] --> B[Individual Sensor Tests]
    B --> B1[BME280 Test]
    B --> B2[BMP280 Test]
    B --> B3[ICM-20602 Test]
    B --> B4[GPS NEO-8M Test]

    A --> C[Storage Tests]
    C --> C1[SD Card Bare Test]
    C --> C2[LittleFS/SPIFFS Test]
    C --> C3[SD + LittleFS Fallback Test]

    A --> D[Integration Tests]
    D --> D1[v1: ICM + BMP + LittleFS]
    D --> D2[v2: +20Hz + Vz + Apogee]
    D --> D3[v3: +GPS + 15-col CSV]
    D --> D4[Fallback: SD + LFS]

    B1 --> E[Consolidate Firmware]
    B2 --> E
    B3 --> E
    B4 --> E
    C1 --> E
    C2 --> E
    C3 --> E
    D1 --> E
    D2 --> E
    D3 --> E
    D4 --> E
    E --> F[Flight Integration]
```
