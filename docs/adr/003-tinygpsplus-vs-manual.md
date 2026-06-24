# ADR-003: TinyGPSPlus vs. Parsing NMEA Manual

## Status

Aceito.

## Contexto

O test_hardware v3 utiliza parsing NMEA manual (leitura caractere a caractere,
extracao de campos, checksum). A biblioteca TinyGPSPlus oferece uma abstracao
mais alta com validacao automatica.

## Decisao

Utilizar TinyGPSPlus como parser de GPS. O parsing manual do v3 e mantido
como referencia em `test_hardware/integration/sensor_logging_v3/`.

## Rationale

- **Menor codigo, menos bugs**: TinyGPSPlus ja implementa validacao de checksum
  e extracao de campos
- **Testavel**: Compila em ambiente nativo para testes unitarios
- **Estavel**: Biblioteca amplamente utilizada na comunidade Arduino/ESP32

## Consequencias

### Positivo
- Codigo mais limpo e manutenivel
- Validacao automatica de checksum NMEA

### Negativo
- TinyGPSPlus adiciona ~3KB de flash
- Abstracao esconde detalhes do protocolo NMEA

## Alternativas Consideradas

1. **Parsing manual** (como v3): Mais controle, mas mais codigo e mais bugs
2. **TinyGPSPlus** (escolhido): Menos codigo, menos bugs, mais rapido de implementar

## Implementation

Ver `src/sensors/GPSSensor.h` e `src/sensors/GPSSensor.cpp`.
