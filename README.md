# PocketQube LoRa Triangulation Mission

Projeto de satelite PocketQube com foco em telemetria LoRa, localizacao por GPS
e estudo de recuperacao por freio aerodinamico tipo samara.

## Status

- Projeto em desenvolvimento.
- Foco atual em validacao de sensores e estudo aerodinamico.
- Estudos de asa em `extras/wing-analisys/`.
- Testes de bancada em `test/`.

## Objetivos

- Coletar telemetria de voo com sensores embarcados.
- Transmitir dados via LoRa em 915 MHz.
- Avaliar estrategia de localizacao com GPS e apoio de beacons.
- Validar recuperacao com arquitetura bioinspirada (samara).

## Arquitetura resumida

### Blocos do sistema

- **Satelite**: ESP32 + LoRa + GPS + sensores + armazenamento local.
- **Beacons terrestres**: ESP32-C3 + LoRa + GPS para apoio de localizacao.
- **Ground station**: gateway LoRa/USB para monitoramento em PC.

### Sensores e subsistemas principais

- BME280 para pressao, temperatura e umidade.
- ICM-20602 para aceleracao e rotacao.
- GPS NEO-8M para posicao e altitude.
- Modulo LoRa SX127x em 915 MHz.
- Registro local de dados para pos-processamento.

## Estrutura do repositorio

```text
satellite/
|-- README.md
|-- AGENTS.md
|-- platformio.ini
|-- docs/
|-- firmware/
|-- hardware/
|   |-- CDB_bom.md
|   |-- CDB.pdf
|   `-- CDB.fzz
|-- extras/
|   `-- wing-analisys/
`-- test/
    |-- README.md
    |-- checklist_bancada_pre_sd.md
    |-- GUIA_IMPLEMENTACAO_FASE_1_3.md
    `-- ... (sketches de validacao)
```

## Build e upload

Comandos principais (PlatformIO):

```bash
pio run
pio run -e satellite_esp32
pio run -e beacon_esp32c3
pio run -e groundstation_esp32c3
```

Upload (ajuste a porta serial conforme o dispositivo):

```bash
pio run -e satellite_esp32 -t upload --upload-port /dev/ttyUSB0
pio run -e beacon_esp32c3 -t upload --upload-port /dev/ttyACM0
```

Monitor serial:

```bash
pio device monitor -b 115200
```

## Fluxo de desenvolvimento recomendado

1. Validar sensores isolados em `test/`.
2. Rodar integracao de sensores (`sensores_unificado_v3.ino`).
3. Executar estudos aerodinamicos em `extras/wing-analisys/`.
4. Consolidar resultados em documentacao tecnica.
5. Integrar firmware final em `firmware/`.

## Documentacao

- Guia de testes: `test/README.md`.
- Plano experimental: `test/GUIA_IMPLEMENTACAO_FASE_1_3.md`.
- Checklist de bancada: `test/checklist_bancada_pre_sd.md`.
- Estudo de asa: `extras/wing-analisys/README.md`.
- BOM de hardware: `hardware/CDB_bom.md`.

## Ferramentas de qualidade de documentacao

Rodar markdownlint via npx:

```bash
npx -y markdownlint-cli "**/*.md"
```

Opcionalmente, limitar aos docs de projeto (ignorando arquivos de framework):

```bash
npx -y markdownlint-cli "README.md" "test/**/*.md" "extras/wing-analisys/**/*.md" "hardware/**/*.md"
```

## Roadmap tecnico (alto nivel)

- Fechar validacao de bancada dos sensores.
- Correlacionar simulacao de asa com testes de queda.
- Consolidar protocolo de telemetria LoRa em campo.
- Integrar pipeline de firmware para campanha completa.

## Time

Serra Rocketry - PocketQube Mission
