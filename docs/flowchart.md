# Fluxos do Sistema

## Fluxo de Operacao (Runtime)

```mermaid
flowchart TD
    A[Power On / Deploy] --> B[setup: Serial + I2C]
    B --> C[Init Sensores: BME280, ICM-20602]
    C --> D[Init GPS: Serial1 9600]
    D --> E[Init LoRa: 915MHz]
    E --> F[Init Storage: SD → LittleFS fallback]
    F --> G[Feedback: 3 beeps + 3 blinks]
    G --> H[loop: 5Hz]
    H --> I[GPS update]
    I --> J[IMU update]
    J --> K[Coleta dados]
    K --> L[Valida dados]
    L --> M[Calcula Vz]
    M --> N[Formata CSV]
    N --> O[TX Serial + LoRa]
    O --> P[Grava Storage]
    P --> Q[LED toggle]
    Q --> H
```

## Fluxo de Dados

```mermaid
flowchart LR
    subgraph Sensores
        BME[BME280: temp/press/hum/alt]
        ICM[ICM-20602: accel/gyro]
        GPS[NEO-8M: lat/lon/alt/sats]
    end

    subgraph Processamento
        TV[TelemetryModule: coleta + CSV]
        VV[VerticalVelocity: EMA filter]
        DV[DataValidation: NaN + range]
    end

    subgraph Output
        SER[Serial Monitor]
        LOR[LoRa 915MHz]
        FS[SD / LittleFS]
    end

    BME --> TV
    ICM --> TV
    GPS --> TV
    TV --> DV
    DV --> VV
    TV --> SER
    TV --> LOR
    TV --> FS
```

## Fluxo de Storage (SD + LittleFS Fallback)

```mermaid
flowchart TD
    A[begin] --> B{Tenta SD.begin(CS)}
    B -->|Sucesso| C[storage_type = STORAGE_SD]
    B -->|Falha| D{Tenta LittleFS.begin}
    D -->|Sucesso| E[storage_type = STORAGE_LITTLEFS]
    D -->|Falha| F[storage_type = STORAGE_NONE]
    C --> G[Operacões de arquivo via SD lib]
    E --> H[Operacões de arquivo via LittleFS lib]
    F --> I[Sem logging local]
```

## Fluxo de Inicializacao Detalhado

```mermaid
sequenceDiagram
    participant S as Serial
    participant I as I2C Bus
    participant B as BME280
    participant C as ICM-20602
    participant G as GPS
    participant L as LoRa
    participant F as Storage
    participant BZ as Buzzer

    S->>S: begin(115200)
    I->>I: begin(SDA=8, SCL=9, 400kHz)
    BZ->>BZ: begin
    B->>I: begin(0x76)
    alt BME280 OK
        B-->>S: "BME280 OK"
    else BME280 FAIL
        B-->>S: "BME280 ERROR"
    end
    C->>I: begin(0x68)
    alt ICM-20602 OK
        C-->>S: "ICM-20602 OK"
    else ICM-20602 FAIL
        C-->>S: "ICM-20602 ERROR"
    end
    G->>G: begin(9600, RX=20, TX=21)
    L->>L: begin(915MHz)
    alt LoRa OK
        L-->>S: "LoRa OK"
    else LoRa FAIL
        L-->>S: "LoRa ERROR"
    end
    F->>F: begin
    alt SD OK
        F-->>S: "Storage: SD"
    else LittleFS OK
        F-->>S: "Storage: LittleFS"
    else No Storage
        F-->>S: "Storage: NONE"
    end
    BZ->>BZ: playStartup (3 beeps)
```

## Fluxo de Telemetria (Loop Principal)

```
A cada 200ms (5Hz):

1. GPS update (sempre)
   - Le bytes do Serial1
   - Alimenta TinyGPSPlus parser

2. IMU update
   - Le 6 bytes accel (0x3B-0x40)
   - Le 6 bytes gyro (0x43-0x48)
   - Converte para m/s² e rad/s

3. Coleta BME280
   - readTemperature() → °C
   - readPressure() → Pa
   - readHumidity() → %
   - getAltitude() → m

4. Coleta GPS
   - getTimeString() → "HH:MM:SS"
   - getLatitude/getLongitude → graus
   - getAltitude() → m
   - getSatellites() → count

5. Validacao
   - Verifica NaN em todos os campos
   - Verifica ranges fisicos
   - Marca dados como validos/invalidos

6. Calculo Vz
   - Vz = (altura_atual - altura_anterior) / dt
   - Filtro EMA: vz_filt = alpha * vz_filt + (1-alpha) * vz_raw

7. Formatacao CSV
   - TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi

8. Transmissao
   - Serial.println(packet)
   - LoRa.send(packet)
   - Storage.appendLine(packet)

9. Heartbeat
   - LED toggle
```

## Fluxo de Desenvolvimento

```mermaid
flowchart TD
    A[Testes Unitarios: pio test -e native] --> B[Build: pio run -e helike_esp32c3]
    B --> C[Testes de Hardware: test_hardware/]
    C --> D[Integracao de sensores]
    D --> E[Simulacao e estudo de asa]
    E --> F[Teste de queda experimental]
    F --> G[Correlacao sim x real]
    G --> H[Integracao de firmware final]
```
