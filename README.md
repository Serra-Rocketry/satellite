# PocketQube LoRa Triangulation Mission

> **Status do Projeto**: 🚀 EM DESENVOLVIMENTO
> - **Foco Atual**: Estudo e validação do freio aerodinâmico (Fase 1)
> - **Progresso**: Simulações de geometria de asas em andamento em `extras/wing-analisys/`
> - **Testes**: Bancada de sensores validada em `test/`

## 🛰️ Visão Geral do Projeto

Este projeto visa desenvolver um pocketQube capaz de determinar sua posição através da triangulação de sinais LoRa usando três beacons terrestres equipados com GPS. O satélite coletará dados de sensores ambientais (pressão, temperatura e umidade) e transmitirá todas as informações via LoRa à 915MHz.

### Características Principais
- **Triangulação por RSSI**: Determinação da posição baseada na intensidade do sinal LoRa
- **GPS em todos os componentes**: Satélite e beacons equipados com GPS para rastreamento completo
- **Modo de busca ativa**: Beacons móveis podem ser usados para localizar e recuperar o satélite
- **Visualização em tempo real**: Sistema de monitoramento com Leaflet mostrando todas as posições
- **Comunicação sequencial**: Protocolo ordenado entre satélite e beacons terrestres
- **Sensores embarcados**: BMP280 (pressão/temperatura), AHT10 (umidade/temperatura) e MPU6050 (acelerômetro/giroscópio)
- **Freio aerodinâmico tipo samara**: Sistema de recuperação inspirado em sementes de árvores para descida controlada
- **Armazenamento local**: Logging em cartão SD para backup de dados
- **Flexibilidade**: Suporte a configurações variáveis de beacons (fixos ou móveis)

## 🏗️ Arquitetura do Sistema

### Especificação de Hardware

#### Satélite - ESP32-C3 Super Mini
- **Microcontrolador**: ESP32-C3 (single-core RISC-V)
- **Clock**: 160 MHz
- **RAM**: 400 KB SRAM
- **Flash**: 4 MB integrado
- **GPIOs**: 13 pinos disponíveis
- **Justificativa**: Formato 1P requer compactação extrema; ESP32-C3 Super Mini oferece tamanho/peso otimizados com performance suficiente para LoRa + GPS + sensores

#### Beacons (3 unidades) - ESP32-C3 Super Mini
- **Microcontrolador**: ESP32-C3 (single-core RISC-V)
- **Clock**: 160 MHz
- **RAM**: 400 KB SRAM
- **Flash**: 4 MB integrado
- **GPIOs**: 13 pinos disponíveis
- **USB**: CDC nativo (útil para debug)
- **Alimentação**: USB Powerbank (modo móvel)
- **Justificativa**: Compacto, econômico, suficiente para GPS + LoRa + interface de busca; idêntico ao satélite para simplificar logística

#### Ground Station - ESP32-C3 Super Mini
- **Função**: Gateway USB para PC
- **Conexão**: USB CDC nativo (plug-and-play)
- **Tarefas**: Receber LoRa e encaminhar via Serial para software de visualização
- **Alimentação**: USB do computador

### Componentes do Sistema

1. **PocketQube Satélite (Formato 1P)**
   - ESP32-C3 Super Mini (single-core)
   - Módulo LoRa 915MHz (SX1276/SX1278)
   - Módulo GPS (NEO-6M/NEO-7M ou similar)
   - Sensor BMP280 (pressão, temperatura)
   - Sensor AHT10 (umidade, temperatura)
   - Sensor ICM-20602 (acelerômetro 3-eixos, giroscópio 3-eixos)
   - Servo motor para freio aerodinâmico tipo samara (estudado em `extras/wing-analisys/`)
   - Cartão SD para armazenamento (testes em `test/sd/`)
   - LEDs de status (GPS lock, LoRa activity, flight state)

2. **Beacons Terrestres** (3 unidades)
   - Beacon 1: Ground Station (base fixa) - gateway USB para PC
   - Beacon 2: Posição configurável (fixo ou móvel)
   - Beacon 3: Posição configurável (fixo ou móvel)
   - Hardware: ESP32-C3 Super Mini + GPS (NEO-6M/NEO-7M) + LoRa 915MHz
   - Interface: LED (força de sinal PWM) + Buzzer (tom variável) + Botão modo
   - **Modos de operação**:
     - **Modo Estação Fixa**: Posição conhecida para triangulação experimental
     - **Modo Busca Ativa**: Beacon móvel rastreando o satélite via RSSI e GPS

### Protocolo de Comunicação
- **Sequencial**: Satélite se comunica com cada beacon individualmente
- **Bidirecional**: Beacons respondem com suas coordenadas GPS e RSSI medido
- **Frequências**: 
  - Triangulação de posição: 1Hz (tempo real)
  - Telemetria de sensores: 0.1Hz (a cada 10 segundos)
  - Coordenadas GPS: transmitidas em todas as mensagens
- **Algoritmo**: RSSI-based triangulation com fusão GPS

### Arquitetura Single-Core do Satélite (ESP32-C3 Super Mini)

O ESP32-C3 é single-core com 400KB de RAM, requerendo otimização cuidadosa de memória e estratégia de agendamento eficiente.

#### Estratégia de Execução
**Single Task com Scheduler Cooperativo**
- **Loop Principal**: Máquina de estados coordena todas as operações
  - Leitura de sensores I2C (BMP280, AHT10, ICM-20602)
  - Comunicação LoRa com beacons (sequencial, ~1Hz)
  - GPS parsing (UART2, contínuo)
  - Logging em SD (batched para eficiência)
  - Acionamento do servo de freio samara

**Razão**: Single-core elimina sincronização complexa; scheduler cooperativo economiza memória (sem overhead de múltiplos contextos).

#### Restrições Críticas
- **Stack máximo**: ~2KB (padrão) - usar buffers estáticos, evitar recursão
- **Heap**: 400KB total - gerenciar cuidadosamente, preferir alocação estática
- **SPI compartilhado**: LoRa (GPIO 4,5,6,7) e SD (GPIO 15) devem ser multiplexados ou usar portas diferentes
- **Taxa de ciclo**: ~100ms para respeitar latência de comunicação

#### Componentes de Software
- **Main Loop**: State machine que itera entre subsistemas
- **Sensores I2C**: Polling periódico sem interrupção
- **LoRa**: Transmissão síncrona com timeout
- **GPS**: Buffer circular UART para parsing assíncrono
- **Freio Samara**: Detecção de apogeu por pressão/aceleração, acionamento via PWM
- **SD Logger**: Write-behind com buffers de 512 bytes

### Estratégia de Localização
O sistema implementa uma abordagem híbrida em camadas para garantir que o satélite nunca seja perdido:

1. **Modo Primário - Fusão GPS + Triangulação**:
   - GPS fornece posição absoluta precisa de todos os componentes
   - Triangulação RSSI fornece confirmação e redundância
   - Filtro Kalman combina ambas as fontes para melhor precisão
   - Validação cruzada entre GPS e triangulação detecta anomalias

2. **Modo Backup - GPS Puro**:
   - Se triangulação falhar (beacons fora de alcance, RSSI ruim)
   - Sistema automaticamente usa apenas dados GPS
   - Coordenadas transmitidas via LoRa continuamente

3. **Modo Busca e Recuperação**:
   - Após pouso, beacons podem ser transformados em dispositivos de busca portáteis
   - RSSI indica direção e distância aproximada do satélite
   - GPS dos beacons registra trajeto da equipe de recuperação
   - Interface mostra "quente/frio" baseado na força do sinal
   - Ground station visualiza posições em tempo real no mapa

4. **Modo Emergência - Última Posição Conhecida**:
   - GPS e LoRa com problemas no satélite
   - Última posição válida gravada no SD card e transmitida periodicamente
   - Beacons móveis podem se aproximar da última posição conhecida

5. **Vantagens da Abordagem**:
   - **Redundância total**: GPS em todos os componentes garante rastreamento completo
   - **Validação**: GPS e triangulação validam-se mutuamente
   - **Flexibilidade**: Beacons podem ser fixos (para experimento) ou móveis (para recuperação)
   - **Visualização completa**: Mapa mostra trajetória do satélite e posição de todos os beacons
   - **Busca inteligente**: RSSI guia a equipe até o satélite mesmo sem GPS lock

## 📋 Plano de Desenvolvimento

### Fase 1: Estudo e Validação do Freio Aerodinâmico (Semanas 1-4) ⭐ **EM PROGRESSO**

Este é o foco principal inicial. O freio samara é crítico para a missão - sem ele, o satélite desceria em queda livre descontrolada.

#### 1.1 Análise Geométrica e Simulação (Em progresso em `extras/wing-analisys/`)

**Status**: Script `analisar_dxf.py` operacional - análise de geometria de asas a partir de DXF

**Tarefas**:
- [x] Implementar extração de geometria de asas (DXF → análise)
- [x] Fórmula aerodinâmica correta (v_terminal = √(2mg / (ρCdA)))
- [x] Simulação de múltiplas configurações (2, 3, 4, 6 asas)
- [ ] Validação experimental com testes em túnel de vento (se disponível)
- [ ] Estudo de materiais (TPU, espessura, densidade)
- [ ] Definição final: número de asas e dimensões (raio, corda)

**Saídas esperadas**:
- Relatório de simulações (`extras/wing-analisys/Asa2_relatorio.txt`)
- Geometria otimizada (JSON estruturado)
- Especificação para manufatura

#### 1.2 Validação Experimental e Testes de Queda (Semanas 2-4)

**Testes propostos** (ver checklist em `test/`):
- [ ] Manufatura de protótipos de asas (TPU com variações de espessura)
- [ ] Testes de queda controlada (altura 5-20m)
- [ ] Medição de:
  - Taxa de descida (velocidade terminal)
  - Padrão de rotação (estabilidade)
  - Energia de impacto
  - Variabilidade entre repetições
- [ ] Ajustes iterativos baseados em dados
- [ ] Integração com servo motor (acionamento confiável)

**Restrições críticas**:
- Taxa alvo: 3-8 m/s (mantém integridade do satélite)
- Deve ser confiável em primeira tentativa (sem fallback em voo real)
- Acionamento simples (poucos componentes móveis)

### Fase 2: Planejamento e Especificações (Semanas 5-6)

#### 2.1 Definições Técnicas
- [ ] Finalizar formato do pocketQube (confirmado: 1P)
- [ ] Especificar componentes LoRa:
  - Potência de transmissão recomendada: 14-20 dBm
  - Spreading Factor: SF7-SF12 (configurável)
  - Bandwidth: 125kHz (padrão para 915MHz)
  - Coding Rate: 4/5 ou 4/6
- [ ] Definir protocolo de dados e estrutura de mensagens
- [ ] Calcular orçamento de energia e dimensionar bateria
- [ ] Finalizar especificação de freio samara (resultado de Fase 1)

#### 2.2 Algoritmo de Triangulação e Posicionamento
- [ ] Implementar algoritmo RSSI-based triangulation
- [ ] Desenvolver calibração para conversão RSSI → distância
- [ ] Criar sistema de coordenadas geográficas (lat/lon)
- [ ] Implementar filtros para redução de ruído nos cálculos
- [ ] Integrar módulo GPS no satélite e beacons
- [ ] Desenvolver algoritmo de fusão GPS + Triangulação (Kalman Filter)
- [ ] Implementar sistema de fallback automático GPS/Triangulação
- [ ] Criar validação cruzada entre fontes de posição
- [ ] Desenvolver algoritmo de busca por RSSI (hot/cold tracking)

### Fase 3: Desenvolvimento de Hardware (Semanas 7-10)

#### 3.1 Design do PocketQube (Formato 1P)
- [ ] Esquemático eletrônico completo
- [ ] Layout da PCB considerando restrições de tamanho (10×10×11.35cm³ máx)
- [ ] Design mecânico e estrutural
- [ ] Sistema de alimentação e gerenciamento de energia
- [ ] Integração do servo motor com freio samara

#### 3.2 Protótipo dos Beacons
- [ ] Design modular para flexibilidade de configuração
- [ ] Interface GPS com precisão adequada (NEO-6M/NEO-7M)
- [ ] Botão para alternar entre modo fixo e modo busca
- [ ] LED indicador de força de sinal (busca ativa)
- [ ] Buzzer feedback em modo busca
- [ ] Antenas otimizadas para 915MHz
- [ ] Caixas weather-proof para testes de campo
- [ ] Sistema de alimentação portátil (beacons móveis)
- [ ] Suporte para montagem em tripé (beacons fixos)

### Fase 4: Desenvolvimento de Software (Semanas 11-14)

#### 4.1 Firmware do Satélite (Arduino/ESP32-C3 Super Mini - Single-Core)
```cpp
// Estrutura do código principal (ESP32-C3 single-core otimizado para 400KB RAM)
├── src/
│   ├── main.cpp                    // Setup + loop principal com state machine
│   ├── communication/              
│   │   ├── lora_manager.cpp        // TX/RX LoRa (síncrono)
│   │   └── protocol_handler.cpp    // Máquina de estados sequencial
│   ├── sensors/                    
│   │   ├── bmp280_driver.cpp       // I2C pressure/temp
│   │   ├── aht10_driver.cpp        // I2C humidity/temp
│   │   ├── icm20602_driver.cpp     // I2C IMU (menor footprint que MPU6050)
│   │   └── gps_driver.cpp          // UART GPS parsing
│   ├── positioning/                
│   │   ├── rssi_triangulation.cpp  // Algoritmo RSSI
│   │   ├── position_filter.cpp     // Filtros Kalman
│   │   └── position_fusion.cpp     // Fusão GPS+Triangulação
│   ├── recovery/                   
│   │   └── samara_brake.cpp        // Servo control + apogee detection
│   ├── storage/                    
│   │   └── sd_logger.cpp           // SPI SD logging (batch write para eficiência)
│   └── utils/
│       ├── state_machine.cpp       // Loop principal com states
│       ├── power_management.cpp    // Gerenciamento energia
│       └── shared_data.cpp         // Estrutura de telemetria
```

#### 3.2 Firmware dos Beacons (ESP32-C3 Super Mini - Single-Core)
```cpp
// Estrutura para beacons (com GPS para tracking completo)
├── beacon_firmware/
│   ├── main.cpp                    // Setup + loop principal
│   ├── gps_handler.cpp             // Interface GPS
│   ├── lora_beacon.cpp             // Comunicação LoRa
│   ├── position_tracker.cpp        // Rastreamento de posição
│   ├── search_mode.cpp             // Modo de busca ativa (RSSI tracking)
│   ├── led_buzzer.cpp              // Interface LED + Buzzer
│   └── config.cpp                  // Configuração (modo fixo/móvel)
```

#### 3.3 Ground Station / Visualização
```cpp
// Sistema de monitoramento (Python + Web)
├── ground_station/
│   ├── serial_listener.py          // Recebe dados do beacon base via serial/USB
│   ├── data_parser.py              // Parse de mensagens LoRa
│   ├── database.py                 // Armazenamento de telemetria (SQLite)
│   ├── web_server.py               // Servidor web (Flask/FastAPI)
│   └── templates/
│       └── map.html                // Visualização Leaflet com todas as posições
```

#### 3.4 Funcionalidades Principais
- [ ] **Sistema de Comunicação**:
  - Protocolo sequencial de polling
  - Time-slots para cada beacon
  - Retry automático em caso de falha
  - Checksum e validação de dados

- [ ] **Coleta de Sensores**:
  - Interface I2C para BMP280, AHT10 e MPU6050
  - Calibração e compensação de temperatura
  - Fusão de dados do acelerômetro e giroscópio (filtro complementar ou Kalman)
  - Média móvel para redução de ruído
  - Detecção de eventos (queda livre, impacto, rotação)

- [ ] **Triangulação RSSI e Posicionamento**:
  - Algoritmo de mínimos quadrados para triangulação
  - Leitura do GPS como fonte primária de localização
  - Fusão de dados GPS + Triangulação RSSI (filtro Kalman)
  - Fallback automático para GPS puro se triangulação falhar
  - Validação cruzada entre GPS e triangulação
  - Detecção de outliers
  - Modo de emergência: transmissão contínua de coordenadas GPS

- [ ] **Sistema de Armazenamento**:
  - Estrutura de dados otimizada
  - Rotação automática de logs
  - Backup em caso de falha de comunicação

- [ ] **Sistema de Navegação e Recuperação**:
  - Estimativa de orientação 3D usando IMU
  - Detecção de apogeu baseada em pressão e aceleração
  - Acionamento do freio aerodinâmico tipo samara
  - Monitoramento da taxa de descida
  - Estabilização durante a descida

- [ ] **Sistema de Visualização (Ground Station)**:
  - Interface web com mapa Leaflet
  - Exibição em tempo real de todas as posições GPS
  - Trajetória do satélite (linha temporal)
  - Posição atual dos 3 beacons
  - Gráficos de telemetria (altitude, velocidade, sensores)
  - Indicador de qualidade de sinal (RSSI) entre componentes
  - Modo de busca: exibir "radar" de proximidade
  - Export de dados (CSV, KML para Google Earth)

### Fase 5: Integração e Testes (Semanas 15-20)

#### 5.1 Testes de Bancada (Checklist em `test/`)
- [ ] Validação individual de cada sensor
  - Sensores: BMP280, AHT10, ICM-20602 (ver `test/` para testes unificados)
  - Comunicação I2C (teste pré-SD disponível em `test/checklist_bancada_pre_sd.md`)
- [ ] Teste de aquisição e precisão do GPS
- [ ] Testes de comunicação LoRa ponto-a-ponto
- [ ] Verificação do algoritmo com posições conhecidas
- [ ] Teste de fusão GPS + Triangulação
- [ ] Validação dos modos de fallback
- [ ] Testes de consumo energético

#### 5.2 Testes de Campo
- [ ] Setup com 3 beacons em configuração triangular (posições conhecidas)
- [ ] Medição e registro preciso das coordenadas GPS dos beacons
- [ ] Testes de alcance e qualidade do sinal
- [ ] Validação do algoritmo em movimento
- [ ] Comparação GPS vs Triangulação vs Fusão
- [ ] Testes de interferência e robustez
- [ ] Simulação de falha da triangulação (beacons desligados)
- [ ] Verificação de recuperação usando apenas GPS
- [ ] **Teste de busca ativa**: Simular pouso e recuperar usando modo busca
- [ ] **Teste de visualização**: Validar interface web com dados em tempo real

#### 5.3 Testes do Freio Aerodinâmico (Continuação de Fase 1)
- [ ] Integração com servo motor no satélite
- [ ] Testes de acionamento confiável
- [ ] Validação de detecção de apogeu em voo
- [ ] Medição de taxa de descida em condições reais

### Fase 6: Otimização e Preparação (Semanas 21-24)

#### 6.1 Otimização de Performance
- [ ] Fine-tuning dos parâmetros LoRa
- [ ] Otimização do algoritmo de triangulação
- [ ] Redução do consumo energético
- [ ] Melhoria da precisão de posicionamento

#### 6.2 Documentação e Preparação
- [ ] Manual de operação completo
- [ ] Guia de uso do modo de busca ativa
- [ ] Procedimentos de teste pré-lançamento
- [ ] Software de ground station para monitoramento
- [ ] Tutorial de configuração da interface web
- [ ] Análise de missão e contingências
- [ ] Protocolo de recuperação passo-a-passo

## 🔧 Especificações Técnicas Recomendadas

### Configuração LoRa Otimizada
```cpp
// Parâmetros recomendados para 915MHz
#define LORA_FREQUENCY      915000000
#define LORA_TX_POWER       20          // dBm (máximo permitido)
#define LORA_SPREADING_FACTOR 9         // Compromisso alcance/taxa
#define LORA_BANDWIDTH      125000      // Hz
#define LORA_CODING_RATE    5           // 4/5
#define LORA_PREAMBLE_LENGTH 8
#define LORA_SYNC_WORD      0x34
```

### Pinout Recomendado

#### Satélite - ESP32-C3 Super Mini

| Periférico | Função | GPIO | Notas |
|-----------|--------|------|-------|
| **LoRa SPI** | MISO | 5 | SPI |
| | MOSI | 6 | SPI |
| | SCK | 4 | SPI |
| | CS | 7 | Chip Select LoRa |
| | RST | 10 | Reset LoRa |
| | DIO0 | 3 | Interrupt LoRa |
| **GPS UART** | TX | 21 | UART |
| | RX | 20 | UART |
| **I2C Sensors** | SDA | 8 | BMP280 + AHT10 + ICM-20602 |
| | SCL | 9 | I2C Clock |
| **Servo Samara** | PWM | 11 | Controle do freio |
| **Status LEDs** | LED1 | 1 | GPS Lock |
| | LED2 | 2 | LoRa Activity |

**Total utilizado**: 12 pinos (sobra 1)

**Nota**: SD Card será adicionado quando conectado ao SPI (GPIO 4,5,6 compartilhados com LoRa, requer multiplexação ou porta SPI adicional)

#### Beacons - ESP32-C3 Super Mini

| Periférico | Função | GPIO | Notas |
|-----------|--------|------|-------|
| **LoRa SPI** | MISO | 5 | SPI |
| | MOSI | 6 | SPI |
| | SCK | 4 | SPI |
| | CS | 7 | Chip Select |
| | RST | 10 | Reset |
| | DIO0 | 3 | Interrupt |
| **GPS UART** | TX | 21 | UART |
| | RX | 20 | UART |
| **Interface** | LED Status | 1 | Força do sinal (PWM) |
| | Buzzer | 8 | Modo busca (tom variável) |
| | Botão Modo | 2 | Fixo/Busca (pullup interno) |

**Total utilizado**: 11 pinos (sobra 2)

#### Ground Station - ESP32-C3 Super Mini

| Periférico | Função | GPIO | Notas |
|-----------|--------|------|-------|
| **LoRa SPI** | MISO | 5 | SPI |
| | MOSI | 6 | SPI |
| | SCK | 4 | SPI |
| | CS | 7 | Chip Select |
| | RST | 10 | Reset |
| | DIO0 | 3 | Interrupt |
| **Interface** | LED RX | 8 | Recebendo dados |
| | LED TX | 9 | Transmitindo (raro) |
| **USB** | D+ / D- | Nativo | CDC USB para PC |

**Total utilizado**: 8 pinos

### Estrutura de Mensagens
```cpp
typedef struct {
    uint8_t beacon_id;                  // ID do beacon (1-3)
    float beacon_lat, beacon_lon, beacon_alt; // Coordenadas GPS do beacon
    uint32_t timestamp;                 // Timestamp Unix
    int16_t rssi_sat_to_beacon;         // RSSI medido pelo beacon
    int16_t rssi_beacon_to_sat;         // RSSI medido pelo satélite
    uint8_t gps_satellites;             // Número de satélites GPS (beacon)
    uint8_t beacon_mode;                // 0=fixo, 1=móvel/busca
    uint16_t checksum;                  // Verificação de integridade
} beacon_message_t;

typedef struct {
    float temperature_bmp;              // Temperatura BMP280 (°C)
    float pressure;                     // Pressão (hPa)
    float temperature_aht;              // Temperatura AHT10 (°C)
    float humidity;                     // Umidade (%)
    float accel_x, accel_y, accel_z;    // Aceleração (m/s²)
    float gyro_x, gyro_y, gyro_z;       // Velocidade angular (°/s)
    float orientation[4];               // Quaternion de orientação [w,x,y,z]
    float gps_lat, gps_lon, gps_alt;    // Posição GPS (latitude, longitude, altitude)
    float calculated_position[3];       // Posição triangulada [x,y,z]
    float fused_position[3];            // Posição fusionada GPS+Triangulação [lat,lon,alt]
    uint32_t timestamp;                 // Timestamp da leitura
    uint8_t gps_satellites;             // Número de satélites GPS
    uint8_t position_quality;           // Indicador de qualidade (0-100)
    uint8_t position_source;            // Fonte (0=GPS, 1=Triangulação, 2=Fusão)
    uint8_t flight_state;               // Estado do voo (0=standby, 1=ascent, 2=descent, 3=landed)
} telemetry_message_t;
```

## 📊 Estimativas de Performance

### Precisão Esperada
- **Horizontal**: ±50-200m (dependendo da geometria dos beacons)
- **Alcance LoRa**: 5-15km (linha de vista, SF9)
- **Latência de atualização**: <2s para posição, <12s para telemetria

### Consumo Energético

#### Satélite (ESP32-C3 Super Mini)
- **ESP32-C3 ativo**: ~50-100mA (single-core)
- **Transmissão LoRa**: ~120mA @ 20dBm (burst)
- **Recepção LoRa**: ~12mA
- **GPS**: ~25mA (aquisição), ~20mA (tracking)
- **Sensores I2C**: ~3mA (BMP280 + AHT10 + ICM-20602)
- **SD Card**: ~50-100mA (escrita), ~20mA (idle)
- **Servo Samara**: ~100-500mA (acionamento, <5s)
- **ESP32-C3 deep sleep**: ~5µA
- **Estimativa total (operação)**: ~200-300mA
- **Estimativa total (pico com servo)**: ~400-600mA

#### Beacons (ESP32-C3 Super Mini)
- **ESP32-C3 ativo**: ~50-100mA (single-core, mais eficiente)
- **Transmissão LoRa**: ~120mA @ 20dBm (burst)
- **Recepção LoRa**: ~12mA
- **GPS**: ~25mA (aquisição), ~20mA (tracking)
- **LED + Buzzer**: ~20-50mA (modo busca)
- **ESP32-C3 deep sleep**: ~5µA
- **Estimativa total (operação)**: ~130-180mA
- **Autonomia com powerbank 10.000mAh**: ~55-75 horas contínuas

#### Ground Station (ESP32-C3 Super Mini)
- **ESP32-C3 ativo**: ~50-80mA
- **Recepção LoRa**: ~12mA
- **USB alimentado**: Não requer bateria
- **Estimativa total**: ~60-100mA (alimentado por USB do PC)

## 🚀 Cronograma de Marcos

| Semana | Marco | Entregável |
|--------|-------|------------|
| 4 | Estudo freio samara concluído | Relatório de simulações (wing-analisys) |
| 6 | Protótipo de freio validado | Testes de queda com taxa controlada |
| 8 | Especificações finalizadas | Documento técnico + BOM |
| 10 | Hardware básico operando | Sensores + GPS + LoRa funcionando |
| 12 | PCB finalizada | Layout pronto para manufatura |
| 14 | Software básico | Comunicação e sensores funcionando |
| 18 | Triangulação implementada | Algoritmo validado em campo |
| 22 | Testes de campo concluídos | Performance verificada |
| 24 | Sistema final | Pronto para operação

## 🧪 Plano de Testes

### Cenários de Teste
1. **Configuração Estática**: Beacons em posições fixas conhecidas
2. **Beacon Móvel**: Um beacon se movimentando, outros fixos  
3. **Multi-móvel**: Múltiplos beacons em movimento
4. **Condições Adversas**: Chuva, obstáculos, interferência

### Métricas de Sucesso
- Precisão de posicionamento < 200m (95% do tempo)
- Taxa de sucesso de comunicação > 90%
- Autonomia energética > 24h (operação contínua)
- Funcionalidade de todos os sensores
- Taxa de descida controlada entre 3-8 m/s com freio samara ativo

## 🌿 Sistema de Recuperação - Freio Aerodinâmico Tipo Samara

### Conceito
O sistema de recuperação utiliza um freio aerodinâmico inspirado nas **sementes de samara** (como as de bordo/maple), que apresentam movimento autogiro durante a queda. Este design biomimético oferece vantagens sobre sistemas tradicionais de paraquedas para aplicações de pequeno porte.

### Vantagens do Design Samara
- **Compacto**: Ocupa menos espaço que paraquedas convencionais
- **Confiável**: Mecanismo de abertura simples, menos falhas
- **Estável**: Rotação natural estabiliza a descida
- **Controlável**: Taxa de descida ajustável através do ângulo das pás
- **Rastreável**: Movimento de rotação facilita localização visual

### Princípio de Funcionamento
1. **Detecção de Apogeu**: Sistema detecta altitude máxima através de:
   - Pressão (BMP280) mostrando tendência de aumento
   - Aceleração vertical (MPU6050) próxima de zero ou negativa
   
2. **Acionamento**: Servo-motor ou mecanismo de mola libera as pás do freio

3. **Autogiro**: Pás assimétricas induzem rotação natural, criando arrasto aerodinâmico

4. **Descida Controlada**: Taxa de 3-8 m/s mantém comunicação LoRa ativa durante toda a descida

### Especificações do Mecanismo
```cpp
// Parâmetros do freio samara
#define SAMARA_BLADE_COUNT        2       // Número de pás (2 ou 4)
#define SAMARA_DEPLOY_ALTITUDE    100     // Altitude mínima para acionamento (m)
#define SAMARA_SERVO_OPEN_ANGLE   90      // Ângulo de abertura do servo (graus)
#define SAMARA_DESCENT_TARGET     5.0f    // Taxa de descida alvo (m/s)
#define APOGEE_DETECTION_SAMPLES  5       // Amostras para confirmar apogeu
```

### Implementação de Software
- Monitoramento contínuo de altitude e aceleração vertical
- Algoritmo de detecção de apogeu com anti-ruído
- Controle do servo de liberação
- Logging de telemetria durante descida (posição, orientação, velocidade)
- Detecção de pouso baseada em acelerômetro

## 🗺️ Sistema de Visualização e Rastreamento

### Ground Station - Interface Web

A ground station utiliza um beacon como gateway USB/Serial conectado a um computador, que executa uma interface web para visualização em tempo real de todos os componentes do sistema.

#### Características da Interface
- **Mapa interativo** usando Leaflet/OpenStreetMap
- **Marcadores dinâmicos**:
  - 🛰️ Satélite (cor: vermelho) - posição em tempo real
  - 📡 Beacon 1 - Ground Station (cor: azul)
  - 📡 Beacon 2 (cor: verde)
  - 📡 Beacon 3 (cor: amarelo)
- **Trajetória histórica**: Linha mostrando caminho do satélite
- **Área de triangulação**: Polígono formado pelos 3 beacons
- **Painéis de telemetria**:
  - Altitude, velocidade vertical, temperatura, pressão
  - Orientação 3D do satélite
  - Estado do voo (ascent, descent, landed)
  - Qualidade GPS (satélites, HDOP)
  - RSSI entre todos os componentes (matriz de conectividade)

#### Tecnologias Sugeridas
```javascript
// Frontend
- Leaflet.js - Mapas interativos
- Chart.js - Gráficos de telemetria
- WebSocket - Comunicação em tempo real

// Backend
- Python Flask/FastAPI - Servidor web
- PySerial - Comunicação com beacon via USB
- SQLite/PostgreSQL - Armazenamento de dados
- SocketIO - Push de dados em tempo real
```

### Modo de Busca Ativa

Após o pouso do satélite, os beacons podem ser reconfigurados para modo de busca móvel.

#### Funcionamento
1. **Ativação**: Botão no beacon alterna para "Modo Busca"
2. **Display mostra**:
   - RSSI atual do satélite
   - Barra visual "quente/frio" (quanto maior RSSI, mais próximo)
   - Distância estimada baseada em RSSI
   - Direção aproximada (se múltiplos beacons)
3. **LED indicador**: Pisca mais rápido quanto mais próximo
4. **Interface web**: Mostra posição da equipe de recuperação em tempo real

#### Algoritmo de Busca
```cpp
// Pseudocódigo do modo busca
void search_mode() {
    // Solicita transmissão do satélite
    request_satellite_beacon();
    
    // Mede RSSI
    int rssi = measure_rssi();
    float distance = rssi_to_distance(rssi);
    
    // Feedback visual
    update_display(rssi, distance);
    update_led_blink_rate(rssi);  // Mais próximo = pisca mais rápido
    
    // Envia posição atual do beacon para ground station
    send_beacon_position(gps.lat, gps.lon);
}
```

#### Estratégia de Recuperação
1. **Fase 1 - Localização Inicial**:
   - Verificar última posição GPS conhecida do satélite
   - Equipe se desloca até área aproximada

2. **Fase 2 - Triangulação Humana**:
   - Dois operadores com beacons se posicionam em locais diferentes
   - Comparam RSSI para determinar direção
   - Se aproximam usando feedback "quente/frio"

3. **Fase 3 - Busca Final**:
   - Beacon próximo indica distância <50m
   - Busca visual na área indicada

## 📚 Recursos e Referências

### Bibliotecas Arduino Necessárias
- `LoRa.h` ou `RadioLib` - Comunicação LoRa
- `TinyGPS++.h` ou `Adafruit_GPS.h` - Módulo GPS
- `Adafruit_BMP280.h` - Sensor de pressão
- `AHTxx.h` - Sensor de umidade
- `MPU6050.h` ou `Adafruit_MPU6050.h` - Acelerômetro e giroscópio
- `SD.h` - Cartão SD
- `ArduinoJson.h` - Serialização de dados
- `Servo.h` - Controle do mecanismo do freio samara
- `Adafruit_SSD1306.h` ou `LiquidCrystal_I2C.h` - Display para beacons (modo busca)

### Bibliotecas Python/JavaScript (Ground Station)
- `pyserial` - Comunicação serial com beacon
- `flask` ou `fastapi` - Servidor web
- `flask-socketio` - WebSocket para tempo real
- `sqlite3` ou `sqlalchemy` - Banco de dados
- Frontend: `leaflet.js`, `chart.js`, `socket.io-client`

### Literatura Técnica
- ITU-R Radio Regulations (915MHz band)
- RSSI-based positioning algorithms
- CubeSat design standards
- LoRa performance analysis

---

## 📂 Recursos em Progresso (Work-in-Progress)

### `extras/wing-analisys/` - Análise de Freio Aerodinâmico ⭐
Script Python completo para análise de geometria de asas e simulação de descida.

**Arquivos principais**:
- `analisar_dxf.py` - Extrai geometria de DXF do CAD e simula múltiplas configurações
- `gerar_dxf_asa.py` - Gera asas paramétricas para teste
- `DXF_ANALYSIS_README.md` - Documentação completa

**Status**: Fisica corrigida (v3 - 08/04/2026)
- ✅ Fórmula aerodinâmica completa implementada
- ✅ Validação com múltiplas asas (2, 3, 4, 6)
- ✅ Cálculo de energia de impacto

**Próximos passos**: Testes experimentais de queda para validar modelos

### `test/` - Validação de Bancada
Testes e checklists para integração incremental de componentes.

**Arquivos principais**:
- `checklist_bancada_pre_sd.md` - Procedimento para validar sensores antes de integração SD
- `bmp280/`, `icm20602/`, `sd/`, `sensores_unificado/` - Testes por subsistema

**Status**: Sensores com SPIFFS/LittleFS validados
- ✅ BMP280, AHT10, ICM-20602 funcionando
- ✅ Leitura contínua sem instabilidade
- ⏳ Migração para SD Card em progresso

**Próximos passos**: Testes com SD Card e GPS

---

**Próximos Passos**: 
1. Completar Fase 1 (estudo do freio aerodinâmico) com testes experimentais
2. Validar hardware com testes de bancada avançados
3. Iniciar desenvolvimento de software (Fase 4) em paralelo