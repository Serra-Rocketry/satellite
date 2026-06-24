# Hardware

## Visao geral

Missao Helike (#213 - LASC 2026) — Serra Rocketry.
Plataforma unica: **ESP32-C3 Super Mini** com LoRa 915 MHz, GPS NEO-8M e
sensores ambientais/inerciais para telemetria e validacao de voo.

## Especificacoes do Microcontrolador

| Caracteristica | Valor |
|----------------|-------|
| MCU | ESP32-C3 (single-core RISC-V) |
| Clock | 160 MHz |
| RAM | 320 KB (400 KB nominal) |
| Flash | 4 MB |
| GPIO | 22 pinos |
| I2C | 1 interface |
| SPI | 1 interface (FSPI) |
| UART | 2 (UART0 + UART1) |
| ADC | 6 canais 12-bit |
| Consumo deep sleep | ~5 uA |

## Componentes Principais

| Componente | Interface | Descricao |
|------------|-----------|-----------|
| BME280 | I2C 0x76 | Pressao, temperatura, umidade |
| ICM-20602 | I2C 0x68 | Acelerometro ±16g, giroscopio ±2000°/s |
| RFM95W | SPI | LoRa 915 MHz, 20 dBm |
| NEO-8M | UART 9600 | GPS (lat, lon, alt, tempo, satelites) |
| LED | GPIO1 | Indicador de estado |
| Buzzer | GPIO8 | Feedback sonoro |

## Pinagem (ESP32-C3 Super Mini)

| Pino | Funcao | Componente |
|------|--------|------------|
| 0 | LoRa RST | RFM95W reset |
| 1 | LED | Indicador |
| 2 | Button | Entrada |
| 3 | LoRa DIO0 | RFM95W IRQ |
| 4 | LoRa RST | RFM95W reset |
| 5 | SPI MISO | RFM95W MISO |
| 6 | SPI SCK | RFM95W SCK |
| 7 | SPI MOSI | RFM95W MOSI |
| 8 | I2C SDA / Buzzer | Sensores + Buzzer |
| 9 | I2C SCL | Sensores clock |
| 10 | SPI CS | RFM95W chip select |
| 20 | UART1 RX | GPS TX |
| 21 | UART1 TX | GPS RX |

**Nota**: O pino 8 e compartilhado entre I2C SDA e Buzzer. Isso funciona porque
o buzzer so e usado durante a inicializacao (antes do I2C comecar) e depois
desligado.

## Diagrama de Blocos

```
                    +------------------+
                    |   ESP32-C3       |
                    |   Super Mini     |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
    I2C (8,9)           SPI (5,6,7,10)      UART (20,21)
         |                   |                   |
   +-----+-----+       +-----+-----+       +-----+-----+
   |           |       |     |     |       |           |
 BME280    ICM-20602  MOSI MISO SCK  CS    NEO-8M GPS
 (0x76)    (0x68)     (7)  (5)  (6)  (10)  (9600 baud)
   |           |       |     |     |       |
   +-----+-----+       +-----+-----+       |
         |                   |                   |
   Temp/Press/Hum      RFM95W 915MHz      Lat/Lon/Alt
                       (LoRa TX)           Satelites
```

## Alimentacao

O satellite e alimentado por bateria (LiPo 3.7V) que so e conectada no momento
do deploy (apogeu). O sistema liga instantaneamente e comeca a transmitir.

| Parametro | Valor |
|-----------|-------|
| Tensao operacao | 3.3V (regulador onboard) |
| Consumo estimado | ~120mA (TX LoRa) |
| Armazenamento | LittleFS (flash interna) |

## Recursos de Armazenamento

| Tipo | Capacidade | Uso |
|------|-----------|-----|
| LittleFS (flash) | ~512KB | Logging fallback |
| SD card (externo) | ate 32GB | Logging primario (bancada) |

O sistema detecta automaticamente qual storage esta disponivel (SD primeiro,
LittleFS como fallback).

## Referencias

- BOM principal: `hardware/CDB_bom.md`
- Artefatos Fritzing/PDF: `hardware/CDB.fzz` e `hardware/CDB.pdf`
- Guia de bancada: `test_hardware/docs/checklist_bancada_pre_sd.md`
- Testes de hardware: `test_hardware/`
