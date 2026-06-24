# Satellite Helike PocketQube (#213 - LASC 2026)

## Contexto Critico

O satellite fica **completamente desligado** (energia cortada) ate o deploy do foguete no apogeu. Ao receber energia, o sistema ja esta em descida (apos apogeu).

**Objetivo**: Ao ligar, inicializar sensores e LoRa o mais rapido possivel, entao ler sensores e transmitir telemetria continuamente via Serial + LoRa.

**O que NAO ha neste sistema:**
- Sem FSM (maquina de estados de voo)
- Sem modo SLEEP
- Sem filesystem/LittleFS
- Sem FreeRTOS
- Sem deteccao de liftoff ou apogeu

**O que ha:**
- Leitura continua de sensores (BME280, ICM-20602, GPS NEO-8M)
- Transmissao telemetria via LoRa + Serial
- LED e buzzer para feedback
- Watchdog

## Hardware

- ESP32-C3 Super Mini (single-core, 400KB RAM)
- BME280 (I2C 0x76): temperatura, pressao, umidade, altitude
- ICM-20602 (I2C 0x68): acelerometro + giroscopio
- RFM95W (SPI): LoRa 915MHz
- NEO-8M (UART): GPS
- LED pino 1, Buzzer pino 8

## Build

```bash
pio run -e helike_esp32c3          # Build
pio run -e helike_esp32c3 -t upload --upload-port /dev/ttyACM0  # Upload
pio test -e native                  # Testes unitarios
```

## Estrutura de Arquivos

```
src/
  config.h               # Configuracoes globais (ja criado)
  main.cpp               # Loop principal (IMPLEMENTAR)
  sensors/
    BME280Sensor.h/cpp   # Driver BME280 (IMPLEMENTAR)
    ICM20602Sensor.h/cpp # Driver ICM-20602 (IMPLEMENTAR)
    GPSSensor.h/cpp      # Driver GPS NEO-8M (IMPLEMENTAR)
  modules/
    LoRaModule.h/cpp     # Modulo LoRa (IMPLEMENTAR)
    BuzzerModule.h/cpp   # Modulo Buzzer (IMPLEMENTAR)
    LEDModule.h/cpp      # Modulo LED (IMPLEMENTAR)
    TelemetryModule.h/cpp # Telemetria/pacotes (IMPLEMENTAR)
lib/
  calc/
    SensorData.h         # Struct de dados (ja existe)
    DataValidation.h     # Validacao de dados (ja existe)
    VerticalVelocity.h   # Calculo de Vz (ja existe)
    ApogeeDetection.h    # Deteccao de apogeu (ja existe)
test/                    # Testes unitarios (IMPLEMENTAR)
```

## Formato Telemetria (CSV)

Header:
```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi
```

Exemplo:
```
#213,1205,1,152.30,25.30,45.20,1013.25,0.10,-0.20,0.05,0.12,-0.05,1.02,156.50,-22.908500,-43.176300,7,0,-1
```

## Tarefas para Implementar

1. Criar `src/sensors/BME280Sensor.h` e `.cpp`
2. Criar `src/sensors/ICM20602Sensor.h` e `.cpp`
3. Criar `src/sensors/GPSSensor.h` e `.cpp`
4. Criar `src/modules/LoRaModule.h` e `.cpp`
5. Criar `src/modules/BuzzerModule.h` e `.cpp`
6. Criar `src/modules/LEDModule.h` e `.cpp`
7. Criar `src/modules/TelemetryModule.h` e `.cpp`
8. Reescrever `src/main.cpp` com o loop principal
9. Criar testes unitarios em `test/`
10. Build limpo e testes passando
