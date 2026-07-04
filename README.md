# Helike — PocketQube Mission (#213 - LASC 2026)

Projeto de satelite PocketQube da Serra Rocketry, com foco no Sistema de
Recuperacao Autorrotativo Bioinspirado (SRAB) e triangulacao LoRa.

## Status

- Projeto em desenvolvimento.
- Foco atual em validacao de sensores e estudo aerodinamico.
- Estudos de asa em `extras/wing-analysis/`.
- Testes de hardware em `test_hardware/`.
- Testes unitarios nativos em `test/`.

## Objetivos

- Coletar telemetria de voo com sensores embarcados.
- Transmitir dados via LoRa em 915 MHz.
- Avaliar triangulacao LoRa para localizacao e recuperacao.
- Validar recuperacao com arquitetura bioinspirada (SRAB/samara).

## Arquitetura resumida

Missao Helike (#213 - LASC 2026) — Serra Rocketry.
Plataforma unica: **ESP32-C3 Super Mini**.

### Sensores e subsistemas principais

- BME280 para pressao, temperatura e umidade (I2C).
- ICM-20602 para aceleracao e rotacao (I2C).
- GPS NEO-8M para posicao e altitude (UART).
- Modulo LoRa RFM95W em 915 MHz (SPI).
- SD + LittleFS fallback para armazenamento local.

## Estrutura do repositorio

```text
satellite/
|-- README.md
|-- AGENTS.md
|-- platformio.ini
|-- CHANGELOG.md
|-- lib/
|   `-- calc/                 # Modulos de calculo reutilizaveis
|       |-- SensorData.h
|       |-- VerticalVelocity.h
|       |-- ApogeeDetection.h
|       `-- DataValidation.h
|-- firmware/                 # Firmware principal (em desenvolvimento)
|-- test/                     # Testes unitarios nativos (Unity)
|   |-- test_vz/
|   |-- test_apogee/
|   `-- test_validation/
|-- test_hardware/            # Sketches de validacao de hardware
|   |-- sensor/               #   Testes isolados de cada sensor
|   |-- integration/          #   Testes multi-sensor + logging
|   |-- storage/              #   Testes de sistema de arquivos
|   `-- docs/                 #   Documentacao dos testes
|-- extras/
|   `-- wing-analysis/        # Estudo de asa autorrotativa
|       |-- src/              # Scripts Python
|       |-- geometry/         # Perfis DXF
|       |-- results/          # Saidas graficas e CSVs
|       `-- docs/             # Documentacao SRAB (teoria, resultados, scripts, proposta)
|-- hardware/                 # Schematics, BOM, PCB
|-- docs/                     # Documentacao geral
`-- .opencode/                # Configuracao de ferramentas
```

## Build e Testes

### Firmware embarcado (ESP32-C3 Super Mini)

```bash
pio run                           # Build all
pio run -e helike_esp32c3  # ESP32-C3 Super Mini

# Upload
pio run -e helike_esp32c3 -t upload --upload-port /dev/ttyACM0

# Monitor serial
pio device monitor -b 115200
```

### Testes unitarios nativos (Unity)

```bash
pio test -e native             # Roda todos os testes nativos
pio test -e native -v          # Com output detalhado
```

### Testes de hardware

Os sketches em `test_hardware/` sao compilados e carregados individualmente:

```bash
# Exemplo: compilar um teste de sensor
pio run -e helike_esp32c3 --project-option="src_dir=test_hardware/sensor/bmp280"
```

Ou abrir o arquivo `.ino` no VS Code com PlatformIO e clicar em "Upload".

## Fluxo de desenvolvimento recomendado

1. Validar sensores isolados em `test_hardware/sensor/`.
2. Rodar integracao de sensores em `test_hardware/integration/`.
3. Executar testes unitarios: `pio test -e native`.
4. Executar estudos aerodinamicos em `extras/wing-analysis/`.
5. Consolidar resultados em documentacao tecnica.
6. Integrar firmware final em `firmware/`.

## lib/calc — Modulos de Calculo

Modulos header-only (sem dependencia de hardware) para logica de voo:

| Modulo | Arquivo | Funcao |
|--------|---------|--------|
| `VerticalVelocity` | `lib/calc/VerticalVelocity.h` | Velocidade vertical por EMA |
| `ApogeeDetection` | `lib/calc/ApogeeDetection.h` | Deteccao de apogeu |
| `DataValidation` | `lib/calc/DataValidation.h` | Validacao de telemetria |
| `SensorData` | `lib/calc/SensorData.h` | Struct padronizada |

## Documentacao

- Guia de hardware: `docs/hardware.md`.
- Arquitetura de software: `docs/software.md`.
- Documentacao por skill: `.opencode/README.md`.
- Testes de hardware: `test_hardware/docs/`.
- Estudo de asa: `extras/wing-analysis/docs/README.md`.
- BOM: `hardware/CDB_bom.md`.

## Ferramentas de qualidade

```bash
# Markdown lint
npx -y markdownlint-cli "README.md" "docs/**/*.md" "test_hardware/docs/**/*.md" "extras/**/*.md" "hardware/**/*.md"

# Testes nativos
pio test -e native
```

## Time

Serra Rocketry — Missao Helike (#213 - LASC 2026)
