# ADR-004: PlatformIO vs. Arduino IDE

## Status

Aceito.

## Contexto

O flight-computer utiliza Arduino IDE para desenvolvimento. O satellite utiliza
PlatformIO com ambiente nativo para testes unitarios.

## Decisao

Manter PlatformIO como ferramenta de build para o satellite.

## Rationale

- **Testes unitarios nativos (Unity)**: Integrados via `pio test -e native`
- **Build reprodutivel via CLI**: `pio run -e helike_esp32c3`
- **Multiplos ambientes**: ESP32-C3 (firmware) + native (testes) no mesmo projeto
- **Gerenciamento de dependencias**: `lib_deps` resolve automaticamente
- **CI/CD friendly**: Build e testes acessiveis via linha de comando

## Consequencias

### Positivo
- Testes automatizados
- Dependencies resolvidas automaticamente
- Ambiente de testes separado do hardware

### Negativo
- Curva de aprendizado para novos membros
- Requer instalacao do PlatformIO (via pip ou VSCode extension)

## Alternativas Consideradas

1. **Arduino IDE** (como flight-computer): Simples, mas sem testes nativos
2. **ESP-IDF nativo**: Mais controle, mas mais complexo para iniciantes
3. **PlatformIO** (escolhido): Balanceia simplicidade e capacidade de testes

## Implementation

Ver `platformio.ini` com ambientes `[env:helike_esp32c3]` e `[env:native]`.
