# AGENTS.md - Missao Helike PocketQube (#213 - LASC 2026)

## Build/Upload Commands

```bash
pio run                           # Build all
pio run -e helike_esp32c3  # ESP32-C3 Super Mini (padrao)

# Upload (ttyACM*)
pio run -e helike_esp32c3 -t upload --upload-port /dev/ttyACM0

# Testes nativos (Unity, roda no PC)
pio test -e native                # Todos os testes
pio test -e native -v             # Com verbose

# Serial monitor
pio device monitor -b 115200
```

## Arquitetura

- **Plataforma unica**: ESP32-C3 Super Mini (single-core, 400KB RAM)
- **Build**: PlatformIO com Arduino framework
- **Unit tests**: Native (PC) com Unity (`pio test -e native`)
- **Lib modules**: `lib/calc/` — header-only, sem deps de hardware

## Pinouts (ESP32-C3 Super Mini — conforme esquemático)

| GPIO | Rótulo | Periférico | Função |
|------|--------|------------|--------|
| 0 | BUZZER | Alerta sonoro | PWM (tone/LEDC) |
| 1 | RESET | RFM95W | Reset do Rádio (LoRa) |
| 2 | DIO0 | RFM95W | Interrupção do Rádio (LoRa) |
| 3 | LED | Indicador | Saída digital |
| 4 | SCK | RFM95W + SD Card | SPI Clock (compartilhado) |
| 5 | MISO | RFM95W + SD Card | SPI MISO (compartilhado) |
| 6 | MOSI | RFM95W + SD Card | SPI MOSI (compartilhado) |
| 7 | NSS | RFM95W | SPI Chip Select (LoRa) |
| 8 | SDA | BME280 + ICM-20602 | I2C Data |
| 9 | SCL | BME280 + ICM-20602 | I2C Clock |
| 10 | CS_SD | SD Card | SPI Chip Select (SD) |
| 20 | TX_GPS | GPS NEO-8M | UART TX |
| 21 | RX_GPS | GPS NEO-8M | UART RX |

## Convencoes

- **Language**: C++ (C++11), comentarios/docs em PT-BR
- **Naming**: snake_case functions/variables, SCREAMING_SNAKE_CASE defines, PascalCase classes
- **Memory**: Evitar heap (new/malloc) - usar buffers estaticos, ESP32-C3 stack max 2048 bytes
- **Single-core**: tarefas sem pinning; evitar suposicoes de multi-core
- **Tests**: Cada teste em seu diretorio sob `test/`, Unity framework
- **Lib**: Header-only em `lib/calc/`, sem dependencias Arduino/ESP32

## ESP32-C3 Pitfalls (aprendidos hoje)

- **USB CDC**: Compilar com `-DARDUINO_USB_MODE=1 -DARDUINO_USB_CDC_ON_BOOT=1` nas build_flags senao Serial.println() nao aparece
- **tone()**: Bug no core do C3 — usar `ledcSetup/ledcAttachPin/ledcWrite` ao inves de tone()
- **I2C**: Nao usar `pinMode/digitalWrite` nos pinos SDA/SCL pois quebra o periferico I2C (TwoWire). O `resetI2C()` foi removido
- **SPI defaults**: Variante esp32c3 tem MISO=5, MOSI=6, SCK=4, SS=7. O hardware Helike segue estes defaults. SD_CS=GPIO10, LORA_CS=GPIO7

## Critical Constraints

- ESP32-C3: 400KB RAM, 4KB default stack - be conservative
- GPS: min 4 satellites for 3D fix, prefer 6+
- LoRa: 915MHz, check all return values, implement retry with backoff
- Documentation in Portuguese

## Sistema Completo

```
satellite/          — firmware do satellite (ESP32-C3, este repo)
├── src/            — codigo fonte
├── lib/calc/       — modulos de calculo (header-only)
└── docs/           — documentacao

recovery-webui/     — sistema de recolhimento (ground station)
├── components/receiver-lora/firmware/Receiver/ — firmware do receiver
│   ├── include/    — headers (config, drivers, payload)
│   ├── src/        — implementacao (main, LoRa, GPS, buzzer)
│   └── docs/       — documentacao do receiver
├── src/            — backend Python (Flask + SocketIO)
└── docs/           — documentacao do protocolo e arquitetura
```

### Compatibilidade LoRa (satellite <-> receiver)

Os parametros LoRa DEVEM ser iguais nos dois firmwares:
- Frequencia: 915 MHz
- Sync Word: 0xF3
- SF: 7, BW: 125 kHz, CR: 4/5, CRC: enabled

Formato do pacote: 18 campos (satellite) -> receiver preenche hora/data/vz/maxAltitude/state/parachute/rssi -> 24 campos (WebUI). Ver recovery-webui/docs/protocol.md (v2.0).
