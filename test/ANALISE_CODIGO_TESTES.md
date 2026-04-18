# Análise Técnica - Código de Testes de Queda

## 📊 Visão Geral

O código em `sensores_unificado/sensores_unificado.ino` implementa coleta integrada de dados de **ICM-20602 (IMU)** e **BMP280 (pressão/altitude)** com logging em CSV via LittleFS.

**Métricas**:

- **Linhas de código**: 274
- **Sensores integrados**: 2 (ICM-20602, BMP280)
- **Output**: CSV com 9 colunas de telemetria
- **Intervalo de aquisição**: 500ms (configurável)
- **Plataformas**: ESP32 / ESP32-C3 (detecção automática)

---

## ✅ Pontos Fortes

### 1. **Suporte Multi-Plataforma**

```cpp
#if defined(CONFIG_IDF_TARGET_ESP32C3)
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#else
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#endif
```

- Detecta plataforma em compile-time
- Pinagem automática (ESP32 vs ESP32-C3)
- ✅ Excelente para testes portáveis

### 2. **ICM-20602 Raw I2C**

```cpp
int16_t ax_raw = icm_read16(0x3B);  // Aceleração X
int16_t gx_raw = icm_read16(0x43);  // Giroscópio X
```

- **Vantagem**: Sem dependência de biblioteca externa (menor memória)
- **Conversão correta**:
  - Aceleração: `* (9.80665 / 16384.0)` → m/s² ✅
  - Giroscópio: `* (π / (180 * 131))` → rad/s ✅

### 3. **BMP280 com Calibração**

```cpp
altura = bmp.readAltitude(1013.25);  // Pressão ao nível do mar
```

- Usa pressão de referência fixa (1013.25 hPa)
- ✅ Bom para testes em curtos períodos

### 4. **Logging Estruturado em CSV**

```
millis,ax_ms2,ay_ms2,az_ms2,gx_rads,gy_rads,gz_rads,pressao_Pa,altura_m
1000,0.12,0.05,9.81,0.0001,0.0002,0.0003,101325,45.23
```

- ✅ Formato facilita pós-processamento
- ✅ Timestamps absolutos para sincronização
- ✅ Precisão de 2 casas decimais para aceleração

### 5. **Reset I2C com Clock Recovery**

```cpp
void resetI2C() {
  for (int i = 0; i < 9; i++) {
    digitalWrite(I2C_SCL_PIN, HIGH);
    delayMicroseconds(5);
    digitalWrite(I2C_SCL_PIN, LOW);
    delayMicroseconds(5);
  }
}
```

- ✅ Recupera barramento travado (9-clock recovery I2C)
- Essencial para confiabilidade em campo

### 6. **Detecção de Sensores**

```cpp
uint8_t who = icm_readReg(0x75);  // ICM20602 WHO_AM_I = 0x12
if (who == 0x12) { ... }
```

- ✅ Valida presença do sensor antes de usar
- Previne crashes por hardware desconectado

---

## ⚠️ Áreas de Melhoria

### 1. **Falta de Cálculo de Taxa de Descida**

**Problema**: Para testes de freio aerodinâmico, necessitamos calcular **velocidade vertical** (dh/dt)

**Código atual**: Apenas coleta altitude instantânea

**Sugestão**:

```cpp
// Adicionar após readSensors()
float calcularTaxaDescent() {
  static float alt_anterior = 0;
  static unsigned long tempo_anterior = 0;
  
  unsigned long tempo_atual = millis();
  float alt_atual = bmp.readAltitude(1013.25);
  
  if (tempo_anterior == 0) {
    tempo_anterior = tempo_atual;
    alt_anterior = alt_atual;
    return 0.0;
  }
  
  float dt_s = (tempo_atual - tempo_anterior) / 1000.0;
  float v_z = (alt_atual - alt_anterior) / dt_s;  // m/s
  
  tempo_anterior = tempo_atual;
  alt_anterior = alt_atual;
  
  return v_z;  // Negativo = descendo
}
```

**Benefício**: Detectar apogeu (Vz passa de positivo para negativo) e validar taxa de descida

### 2. **Falta de Análise de Rotação**

**Problema**: Não detecta padrão de rotação durante queda

**Código atual**: Apenas coleta giroscópio raw (rad/s)

**Sugestão** - Adicionar magnitude de rotação:

```cpp
float magnitude_giroscopia = sqrt(gx*gx + gy*gy + gz*gz);
// Se magnitude_giroscopia > threshold → está em autogiro
```

**Para análise avançada**: Integrar para calcular ângulo de rotação

### 3. **Calibração BMP280 Manual**

**Problema**: Pressão de referência (1013.25 hPa) é fixa - não adequada para locais em altitude

**Código atual**:

```cpp
altura = bmp.readAltitude(1013.25);  // Fixo!
```

**Sugestão**:

```cpp
// Ler pressão de referência de um GPS acurado ou config
void calibrateAltitude() {
  // Coletar 100 amostras em repouso
  float soma_pressao = 0;
  for (int i = 0; i < 100; i++) {
    soma_pressao += bmp.readPressure();
    delay(10);
  }
  referencia_pressao = soma_pressao / 100;
}
```

### 4. **Ausência de Detecção de Eventos**

**Problema**: Não detecta eventos críticos automaticamente

**Sugestão** - Adicionar flags:

```cpp
struct EventoQueda {
  bool apogeu_detectado;        // Vz mudou de + para -
  float altitude_max;           // Pico de altitude
  float tempo_apogeu_ms;        // When apogee occurred
  float velocidade_max_descida; // Máxima taxa de descida
};
```

### 5. **Sem Tratamento de NaN/Overflow**

**Problema**: Valores inválidos não são detectados

**Código atual**:

```cpp
String data_string = String(ax, 2) + "," + String(ay, 2) + ...
```

**Risco**: Se sensor falhar, produz valores corrupting CSV

**Sugestão**:

```cpp
bool validarDados(float ax, float ay, float az, float pressao) {
  if (isnan(ax) || isnan(ay) || isnan(az)) return false;
  if (pressao < 300 || pressao > 120000) return false;  // Pa range
  if (fabs(ax) > 50 || fabs(ay) > 50 || fabs(az) > 50) return false;  // > 5g é suspeito
  return true;
}
```

### 6. **Sem Checksum ou Validação de Arquivo**

**Problema**: Arquivo CSV pode ser corrompido sem aviso

**Sugestão**:

```cpp
// Adicionar coluna extra: checksum
uint16_t calcularChecksum(float ax, float ay, float az, ...) {
  uint16_t sum = 0;
  // Simples: soma todos os valores inteiros
  return sum % 65536;
}

// CSV final:
// millis,ax_ms2,...,altura_m,checksum
```

### 7. **Intervalo Fixo (500ms) Pode Perder Picos**

**Problema**: Taxa de aquisição de 2 Hz é baixa para testes dinâmicos

**Contexto**:

- Queda de 20m com v_terminal 5 m/s = 4s de queda
- Em 4s, apenas 8 amostras!
- Se pico de aceleração ocorre entre amostras, é perdido

**Sugestão**:

```cpp
#define INTERVAL 50  // 20 Hz melhor para testes dinâmicos
// Ou ainda melhor: usar timer ISR para 100 Hz (10ms)
```

### 8. **Sem Sincronização com GPS**

**Problema**: Não há correlação com altitude real do GPS

**Para Fase 1.3 (testes de queda)**:

```cpp
// Adicionar:
#include <TinyGPS++.h>
TinyGPSPlus gps;

// Coletar: gps_altitude, gps_satellites, gps_hdop
// Comparar com BMP280 para validação
```

---

## 🔧 Recomendações por Prioridade

### 🔴 CRÍTICO (Implementar para Fase 1.3)

1. **Cálculo de taxa de descida** (dh/dt)
   - Necessário para validar freio aerodinâmico
   - ~20 linhas de código
   - Impacto: Alto

2. **Aumentar taxa de aquisição** (500ms → 50ms ou ISR 100Hz)
   - Atualmente perde dados de eventos rápidos
   - ~30 linhas de código
   - Impacto: Alto

3. **Validação de dados** (NaN, outliers)
   - Evita corrupção de CSV
   - ~15 linhas de código
   - Impacto: Médio

### 🟡 IMPORTANTE (Implementar para Fase 4)

1. **Detecção de apogeu automática**
   - Dispara servo motor automaticamente
   - ~30 linhas de código
   - Impacto: Muito Alto

2. **Integração com GPS**
   - Validação cruzada de altitude
   - ~50 linhas de código
   - Impacto: Alto

3. **Cálculo de ângulo de rotação**
   - Análise de estabilidade do freio
   - ~40 linhas de código
   - Impacto: Médio

### 🟢 OPCIONAL (Nice-to-have)

1. Checksum em CSV
2. Calibração automática de BMP280
3. Logging de eventos em arquivo separado

---

## 📋 Plano de Próximos Passos

### Para Testes de Queda (Fase 1.3)

**Semana 1**:

- [ ] Aumentar taxa de aquisição para 50ms
- [ ] Implementar cálculo de Vz (velocidade vertical)
- [ ] Adicionar validação de dados

**Semana 2**:

- [ ] Integrar GPS para validação de altitude
- [ ] Detectar apogeu automaticamente
- [ ] Testar com primeira série de quedas

**Semana 3**:

- [ ] Análise de dados coletados
- [ ] Ajustar parâmetros de detecção
- [ ] Iteração com servo motor

---

## 🧪 Sugestão: Script Python para Análise

Para pós-processar dados de teste:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Ler CSV
df = pd.read_csv('sensores.csv')

# Calcular velocidade vertical suavizada
df['vz_ms'] = df['altura_m'].diff() / (df['millis'].diff() / 1000)
df['vz_suavizada'] = df['vz_ms'].rolling(5).mean()

# Encontrar apogeu
apogeu_idx = df['vz_suavizada'].idxmin() if (df['vz_suavizada'] > 0).any() else None

# Plots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

ax1.plot(df['millis'], df['altura_m'], label='Altitude')
ax2.plot(df['millis'], df['vz_suavizada'], label='Vz suavizada')
ax3.plot(df['millis'], df[['ax_ms2', 'ay_ms2', 'az_ms2']])

plt.show()
```

---

## 📚 Referências

- **Registers ICM-20602**:
  - 0x3B-0x3D: Aceleração raw
  - 0x43-0x47: Giroscópio raw
  - 0x75: WHO_AM_I = 0x12

- **BMP280**: Fórmula de altitude = 44330 * (1 - (P/P0)^(1/5.255))

- **I2C Recovery**: 9-clock pulses para resetar barramento travado

---

**Última atualização**: 09/04/2026
**Status**: ✅ Código funcional, ⏳ Aguardando testes de queda
