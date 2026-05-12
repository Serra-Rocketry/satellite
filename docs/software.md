# Software

## Visao geral

O firmware e organizado para coleta de sensores, telemetria LoRa, parse de GPS
e registro de dados para analise pos-voo.

## Blocos funcionais

- Aquisição de sensores (I2C/UART).
- Comunicacao LoRa para telemetria.
- Tratamento e serializacao de dados.
- Logging local para analise posterior.

## Base de testes atual

- Integracao de sensores: `test/integration/`.
- Guia de implementacao: `test/GUIA_IMPLEMENTACAO_FASE_1_3.md`.
- Estudo aerodinamico acoplado: `extras/wing-analisys/`.

## Build

Config de build em `platformio.ini` com ambientes separados para satelite,
beacon e ground station.
