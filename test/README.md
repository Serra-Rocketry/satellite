# 🧪 Testes - Validação de Hardware e Firmware

Este diretório contém testes de bancada e testes experimentais para validação dos sensores e sistema embarcado do satélite PocketQube.

## 📂 Estrutura

```
test/
├── README.md                           ← Você está aqui
├── ANALISE_CODIGO_TESTES.md            ← Análise técnica do sensores_unificado.ino
├── GUIA_IMPLEMENTACAO_FASE_1_3.md      ← Guia completo para testes de queda
├── checklist_bancada_pre_sd.md         ← Checklist para validação pré-SD
├── bmp280/                             ← Teste isolado do BMP280
│   └── bmp280.ino
├── bmp280_spiffs/                      ← Teste BMP280 + SPIFFS/LittleFS
│   └── bmp280_spiffs.ino
├── icm20602/                           ← Teste isolado do ICM-20602
│   └── icm20602.ino
├── sd/                                 ← Teste de interface SD
│   └── sd.ino
└── sensores_unificado/                 ← ⭐ INTEGRAÇÃO COMPLETA
    ├── sensores_unificado.ino          ← v1 (original, funcional)
    └── sensores_unificado_v2_melhorado.ino  ← v2 (RECOMENDADO para Fase 1.3)
```

## 🎯 Propósito de Cada Teste

### 1. **sensores_unificado.ino** (274 linhas)
**Status**: ✅ Funcional, produção  
**Descrição**: Integração completa de ICM-20602 (IMU) + BMP280 (pressão/altitude)

- Lê aceleração (m/s²), giroscópio (rad/s), pressão (Pa), altitude (m)
- Logging contínuo em LittleFS com formato CSV
- Suporte automático a ESP32 e ESP32-C3
- Taxa: 500ms (2 Hz)
- **CSV Output**:
  ```
  millis,ax_ms2,ay_ms2,az_ms2,gx_rads,gy_rads,gz_rads,pressao_Pa,altura_m
  ```

**Próximo**: Usar v2 melhorada para testes de queda (veja abaixo)

---

### 2. **sensores_unificado_v2_melhorado.ino** (402 linhas) ⭐ NOVO
**Status**: ✅ Pronto para Fase 1.3  
**Descrição**: Versão melhorada com recomendações críticas implementadas

**Melhorias Implementadas**:
- ✅ Taxa aumentada: 50ms (20 Hz) - melhor captura de eventos
- ✅ Cálculo de velocidade vertical (Vz = dh/dt)
- ✅ Detecção automática de apogeu
- ✅ Validação de dados (NaN, outliers)
- ✅ Magnitude do giroscópio (rotação)
- ✅ Estrutura de eventos para análise

**CSV Output** (11 colunas):
```
millis,ax_ms2,ay_ms2,az_ms2,gx_rads,gy_rads,gz_rads,pressao_Pa,altura_m,vz_ms,mag_giroscopia_rads
```

**Quando usar**:
- Testes de queda (Fase 1.3) ← RECOMENDADO
- Validação de freio aerodinâmico
- Coleta de dados experimentais

**Analise automática**: Serial Monitor mostra:
```
[50] A: 0.12 -0.05 9.81 | G: 0.0001 0.0002 0.0003 | P: 101325 | Alt: 45.23 | Vz: 0.00 | Rot: 0.0003

🎯 APOGEU DETECTADO!
   Tempo: 1234 ms
   Altitude: 50.12 m
   Vz: -0.52 m/s
```

---

### 3. **bmp280.ino** (67 linhas)
**Status**: ✅ Teste isolado  
**Descrição**: Validar apenas sensor de pressão/altitude

- Teste simples sem gravação
- Ideal para debug de hardware I2C
- Verifica WHO_AM_I do BMP280 (0x76)

**Uso**: Diagnosticar problemas de conexão I2C

---

### 4. **bmp280_spiffs.ino** (173 linhas)
**Status**: ✅ Teste de integração SPIFFS  
**Descrição**: BMP280 com logging em LittleFS/SPIFFS

- Coleta dados de pressão e altitude
- Salva em CSV via SPIFFS
- Útil para validar escrita em FS antes de migrar para SD

---

### 5. **icm20602.ino** (76 linhas)
**Status**: ✅ Teste isolado  
**Descrição**: Validar apenas acelerômetro + giroscópio

- Lê valores raw do ICM-20602
- Conversão para m/s² e rad/s
- Verifica WHO_AM_I (0x12)

**Uso**: Debug de IMU e calibração

---

### 6. **sd.ino** (100 linhas)
**Status**: ✅ Teste de interface SD  
**Descrição**: Validar comunicação com módulo SD externo

- Teste de montagem, escrita, leitura
- Verifica performance de I/O
- Útil para preparar integração futura

---

## 📋 Checklist de Validação

### Pré-Testes
- [ ] ESP32-C3 + ICM-20602 + BMP280 montados
- [ ] I2C conectado: GPIO 8 (SDA), GPIO 9 (SCL)
- [ ] Arduino IDE preparado com bibliotecas
- [ ] Serial Monitor configurado (115200 baud)

### Durante Testes
- [ ] Carregar código (v1 original ou v2 melhorada)
- [ ] Monitorar Serial: dados aparecem?
- [ ] CSV sendo gravado em LittleFS?
- [ ] Sem crashes ou reboots?

### Pós-Testes
- [ ] Extrair arquivo CSV
- [ ] Analisar com script Python (veja `GUIA_IMPLEMENTACAO_FASE_1_3.md`)
- [ ] Comparar com simulação (se aplicável)

---

## 🔧 Setup Rápido

### 1. Hardware
```
ESP32-C3 + Protoboard
├─ ICM-20602 I2C
│  ├─ SDA → GPIO 8
│  ├─ SCL → GPIO 9
│  ├─ VCC → 3.3V
│  └─ GND → GND
├─ BMP280 I2C
│  ├─ SDA → GPIO 8 (compartilhado)
│  ├─ SCL → GPIO 9 (compartilhado)
│  ├─ VCC → 3.3V
│  └─ GND → GND
└─ USB Power
   └─ Via USB-C direto
```

### 2. Software
```bash
# Arduino IDE
1. Tools → Board: "ESP32-C3 Dev Module"
2. Tools → Upload Speed: 921600
3. Tools → Port: /dev/ttyACM0 (ESP32-C3)
4. File → Open: sensores_unificado_v2_melhorado.ino
5. Upload (Ctrl+U)
6. Tools → Serial Monitor (115200)
```

### 3. Validação
```
Serial Monitor deve mostrar:
✅ ICM20602 encontrado!
✅ BMP280 inicializado com sucesso!
✅ LittleFS montado com sucesso!
=== Taxa de Aquisição: 20 Hz (50 ms) ===
[50] A: 0.12 -0.05 9.81 | ...
[100] A: 0.10 -0.03 9.81 | ...
```

---

## 📚 Documentação Relacionada

### Documentos Técnicos
- **`ANALISE_CODIGO_TESTES.md`** (347 linhas)
  - Análise técnica do sensores_unificado.ino
  - 8 áreas de melhoria identificadas
  - Script Python para análise

- **`GUIA_IMPLEMENTACAO_FASE_1_3.md`** (485 linhas)
  - Protocolo completo de testes de queda
  - 4 fases: Bancada → Baseline → Asa → Iteração
  - Cronograma, análise, troubleshooting

- **`checklist_bancada_pre_sd.md`** (83 linhas)
  - Checklist para validação pré-SD
  - Critérios de aprovação

### Simulação de Asas
- **`../extras/wing-analisys/`**
  - Análise de geometria de asas
  - Simulação de descida
  - Relatórios para comparação com testes

---

## 🚀 Recomendações por Fase

### Fase 1.2 (Desenvolvimento em Progresso)
- ✅ Usar `sensores_unificado.ino` (v1) - funciona, validado
- ✅ Validar com checklist em `checklist_bancada_pre_sd.md`
- ⏳ Começar testes com v2 em bancada

### Fase 1.3 (Próximo: Testes de Queda)
- 🚀 Usar `sensores_unificado_v2_melhorado.ino` (v2) - RECOMENDADO
- 🚀 Seguir guia completo: `GUIA_IMPLEMENTACAO_FASE_1_3.md`
- 🚀 4 fases de testes: Bancada → Baseline → Asa → Iteração

### Fase 2+ (Integração)
- Usar código v2 como base para firmware completo
- Adicionar: LoRa, GPS, servo motor, state machine
- Integrar em `firmware/main.cpp`

---

## 📊 Estatísticas

| Arquivo | Linhas | Status | Uso |
|---------|--------|--------|-----|
| sensores_unificado.ino | 274 | ✅ Funcional | Produção atual |
| sensores_unificado_v2_melhorado.ino | 402 | ✅ Pronto | Fase 1.3 (recomendado) |
| icm20602.ino | 76 | ✅ Funcional | Debug isolado |
| bmp280.ino | 67 | ✅ Funcional | Debug isolado |
| bmp280_spiffs.ino | 173 | ✅ Funcional | Teste FS |
| sd.ino | 100 | ✅ Funcional | Futuro SD |
| **TOTAL** | **690** | | |

---

## 🔗 Links Úteis

- [README do Projeto](../README.md) - Visão geral do PocketQube
- [AGENTS.md](../AGENTS.md) - Pinouts e arquitetura
- [Análise Técnica](./ANALISE_CODIGO_TESTES.md) - Detalhes do código
- [Guia Fase 1.3](./GUIA_IMPLEMENTACAO_FASE_1_3.md) - Procedimentos de testes

---

## 👥 Responsáveis

**Time de Desenvolvimento**  
**Última atualização**: 09 de Abril de 2026

---

**Status**: 🚀 Pronto para Fase 1.3 - Testes de Queda Experimental
