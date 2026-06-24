# ADR-001: Ausencia de FSM e Modo Sleep

## Status

Aceito.

## Contexto

O satellite (#213) e um PocketQube que permanece completamente desligado (sem
energia) ate o deploy do foguete no apogeu. Ao receber energia, o sistema ja
esta em descida — nao ha necessidade de detectar liftoff, gerenciar estados
de voo, ou manter modo sleep.

O flight-computer (#11) utiliza uma FSM de 4 estados (IDLE/ASCENT/DESCENT/LANDED)
com FreeRTOS para gerenciar o ciclo completo de voo. Essa complexidade nao
se aplica ao satellite.

## Decisao

Implementar o firmware como um loop continuo simples, sem FSM, sem FreeRTOS,
sem modo sleep. O sistema:

1. Inicializa sensores e LoRa o mais rapido possivel
2. Entra em loop de leitura + transmissao a 5Hz
3. Nao possui estados de voo

## Consequencias

**Positivos**:
- Codigo simples e facil de debug
- Menor superficie de bugs
- Consumo de RAM/Flash reduzido
- Build mais rapido

**Negativos**:
- Nao suporta logica de voo complexa (deploy de paraquedas, etc)
- Nao distingue fases de voo para ajustar taxa de amostragem

**Mitigacao**: Se necessario no futuro, adicionar FSM simplificado (3 estados)
como modulo opcional.

---

# ADR-002: LittleFS como Fallback (nao primario)

## Status

Aceito.

## Contexto

O flight-computer utiliza LittleFS como storage primario para logging CSV.
O satellite possui um slot para SD card (test_hardware) mas o SD nao esta
presente em voo real.

O teste `test_hardware/storage/sd_littlefs_fallback` demonstra o padrao de
tentar SD primeiro e usar LittleFS como fallback.

## Decisao

Implementar o FilesystemModule com deteccao em runtime:

1. Tenta `SD.begin(CS)` primeiro
2. Se falhar, usa `LittleFS.begin(true)` como fallback
3. Dispatch automatico de operacoes baseado no tipo ativo

Sem flag de compilacao — o modulo sempre compila e detecta o storage disponivel
em runtime.

## Consequencias

**Positivos**:
- Funciona em bancada (com SD) e em voo (sem SD)
- Sem overhead de codigo morto quando SD nao presente
- Padrao ja validado nos testes de hardware

**Negativos**:
- SD card library adiciona ~2KB de flash mesmo quando nao usado
- Complexidade de codigo vs. apenas LittleFS

---

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

**Razoes**:
- Menor codigo, menos bugs
- Validacao automatica de checksum
- Testado e estavel
- Compila em nativo (testes unitarios)

## Consequencias

**Positivos**:
- Codigo mais limpo e manutenivel
- Testavel em ambiente nativo

**Negativos**:
- TinyGPSPlus adiciona ~3KB de flash
- Abstracao esconde detalhes do protocolo NMEA

---

# ADR-004: PlatformIO vs. Arduino IDE

## Status

Aceito.

## Contexto

O flight-computer utiliza Arduino IDE para desenvolvimento. O satellite utiliza
PlatformIO com ambiente nativo para testes unitarios.

## Decisao

Manter PlatformIO como ferramenta de build para o satellite.

**Razoes**:
- Testes unitarios nativos (Unity) integrados
- Build reprodutivel via CLI
- Suporte a multiplos ambientes (ESP32 + native)
- Gerenciamento de dependencias automatico

## Consequencias

**Positivos**:
- CI/CD friendly
- Testes automatizados
- Dependencies resolvidas automaticamente

**Negativos**:
- Curva de aprendizado para novos membros
- Requer instalacao do PlatformIO

---

# ADR-005: Objeticos Globais Estaticos (sem heap)

## Status

Aceito.

## Contexto

ESP32-C3 possui apenas 320KB de RAM. Alocacao dinamica (new/malloc) em sistemas
embarcados pode causar fragmentacao e falhas em execucao prolongada.

## Decisao

Todos os objetos de modulo sao declarados como `static` globais. Nenhuma
alocacao dinamica e utilizada no firmware principal.

**Razoes**:
- Determinismo de memoria
- Sem fragmentacao
- Facil de rastrear uso de RAM

## Consequencias

**Positivos**:
- Uso de RAM previsivel
- Sem risco de out-of-memory em execucao prolongada

**Negativos**:
- Objetos nao podem ser destruidos/recriados
- Testes unitarios requerem setup/teardown cuidadoso
