# Testes — Validação de Hardware e Firmware

```
test/
├── docs/                          # Documentação dos testes
├── sensor/                        # Testes isolados de cada sensor
├── integration/                   # Integração multi-sensor + logging
└── storage/                       # Testes de sistema de arquivos
```

---

## docs/ — Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `ANALISE_CODIGO_TESTES.md` | Análise técnica do código v1 original |
| `GUIA_IMPLEMENTACAO_FASE_1_3.md` | Protocolo completo de testes de queda |
| `checklist_bancada_pre_sd.md` | Checklist para validação pré-SD |
| `QUICK_START_V3.md` | Quick start para v3 com GPS |

---

## sensor/ — Testes Isolados

Testa **um sensor por vez** para validar hardware e comunicação.

| Teste | Sensor | Interface | Funcionalidades |
|-------|--------|-----------|-----------------|
| `bmp280/` | BMP280 | I2C | Pressão, altitude, temperatura |
| `bme280/` | BME280 | I2C | Pressão, altitude, temperatura, umidade, ponto de orvalho |
| `icm20602/` | ICM-20602 | I2C | Aceleração (m/s²), giroscópio (rad/s), WHO_AM_I |
| `gps_neo8m/` | NEO-8M | UART | Parser NMEA, posição, altitude, satélites, HDOP/VDOP |

**Uso**: Diagnosticar problemas de comunicação ou sensor com defeito.

---

## integration/ — Testes de Integração

Múltiplos sensores + logging contínuo em CSV.

| Teste | Sensores | Taxa | Storage | CSV |
|-------|----------|------|---------|-----|
| `sensor_logging_lfs/` | ICM + BMP280 | 2 Hz | LittleFS | 9 colunas |
| `sensor_logging_lfs_v2/` | ICM + BMP280 | **20 Hz** | LittleFS | 11 colunas (+ Vz, mag_giro) |
| `sensor_logging_v3/` | ICM + **BME280 + GPS** | 20 Hz | LittleFS | 15 colunas |
| `sensor_logging_fallback/` | ICM + BMP280 | 20 Hz | **SD + LittleFS fallback** | 12 colunas |

### v2 — Recomendado para testes de queda sem GPS
- 20 Hz, cálculo de Vz, detecção de apogeu, validação de dados

### v3 — Recomendado para fase 1.3
- Adiciona BME280 (umidade) e GPS NEO-8M, validação cruzada de altitude

### sensor_logging_fallback — SD com fallback
- Tenta SD primeiro; se falhar, usa LittleFS
- Arquivo mantido aberto com flush periódico (menos perda em queda de energia)
- Geração automática de nome (`Dados_001.csv`)

---

## storage/ — Testes de Sistema de Arquivos

| Teste | Storage | Descrição |
|-------|---------|-----------|
| `sd_bare/` | SD cartão | Teste básico de montagem, escrita e leitura SD |
| `bmp280_littlefs/` | LittleFS | BMP280 com logging em LittleFS (valida FS antes do SD) |
| `sd_littlefs_fallback/` | SD + LittleFS | Fallback automático SD→LittleFS com geração incremental de nome |

---

## Como Usar

```bash
# Abrir um teste no Arduino IDE:
File → Open → test/<categoria>/<teste>/<teste>.ino

# Serial Monitor:
115200 baud

# Upload (ESP32-C3):
pio run -e groundstation_esp32c3 -t upload --upload-port /dev/ttyACM0
```
