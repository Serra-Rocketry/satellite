/**
 * @file sensor_logging_lfs_v2.ino
 * @brief Unified sensor test v2 — ICM-20602 + BMP280 with improved features
 *
 * Improvements over v1:
 * - 500ms -> 50ms (20 Hz) sample rate
 * - Vertical velocity (Vz) calculation
 * - Data validation (NaN, outliers)
 * - Automatic apogee detection
 * - Better error handling
 *
 * Hardware setup (ESP32-C3):
 * - I2C: SDA=GPIO8, SCL=GPIO9
 * - Storage: LittleFS
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include <Wire.h>
#include "FS.h"
#include "LittleFS.h"
#include <Adafruit_BMP280.h>

#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9

// ============= Configurações =============

#define ICM_ADDR 0x69
#define INTERVAL_MS 50        // 20 Hz (era 500ms)
#define FILE_NAME "sensores.csv"

// Thresholds de validação
#define MAX_ACCEL_G 50.0      // >5g é suspeito
#define MIN_PRESSURE_PA 300
#define MAX_PRESSURE_PA 120000
#define APOGEE_THRESHOLD_MS 100  // Tempo mínimo em descida

// ============= Estruturas =============

struct SensorData {
  unsigned long millis;
  float ax, ay, az;           // m/s²
  float gx, gy, gz;           // rad/s
  float pressao;              // Pa
  float altura;               // m
  float vz;                   // m/s (velocidade vertical)
  float mag_giroscopia;       // rad/s (magnitude)
};

struct EventosQueda {
  bool apogeu_detectado;
  unsigned long tempo_apogeu_ms;
  float altitude_max;
  float velocidade_max_descida;
  float aceleracacao_max;
} eventos;

// ============= Variáveis Globais =============

unsigned long previous_millis = 0;
String file_path = "";
bool sd_ok = false;
bool icm_ok = false;
bool bmp_ok = false;

// Para cálculo de Vz
float altura_anterior = 0.0;
unsigned long millis_anterior = 0;
float vz_anterior = 0.0;  // Para detecção de apogeu

// Para detecção de apogeu
bool em_descida = false;
unsigned long tempo_descida_inicio = 0;

Adafruit_BMP280 bmp;

// ============= Funções I2C para ICM-20602 =============

void icm_writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

uint8_t icm_readReg(uint8_t reg) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ICM_ADDR, 1);
  if (Wire.available()) return Wire.read();
  return 0xFF;
}

int16_t icm_read16(uint8_t reg) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ICM_ADDR, 2);
  if (Wire.available() < 2) return 0;
  return (Wire.read() << 8) | Wire.read();
}

// ============= Inicialização =============

bool setupICM20602() {
  icm_writeReg(0x6B, 0x80);  // Reset
  delay(100);
  icm_writeReg(0x6B, 0x01);  // Wake up
  delay(50);

  uint8_t who = icm_readReg(0x75);
  Serial.print("ICM20602 WHO_AM_I: 0x");
  Serial.println(who, HEX);

  if (who == 0x12) {
    Serial.println("✅ ICM20602 encontrado!");
    return true;
  } else {
    Serial.println("❌ Erro: ICM20602 não encontrado!");
    return false;
  }
}

bool setupBMP280() {
  unsigned status = bmp.begin(0x76);
  if (!status) {
    Serial.println("❌ BMP280 não encontrado! Verifique conexão.");
    return false;
  }

  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);

  Serial.println("✅ BMP280 inicializado com sucesso!");
  return true;
}

bool setupLittleFS() {
  if (!LittleFS.begin(true)) {
    Serial.println("❌ Erro ao montar LittleFS.");
    return false;
  }
  Serial.println("✅ LittleFS montado com sucesso!");
  return true;
}

void resetI2C() {
  pinMode(I2C_SDA_PIN, INPUT_PULLUP);
  pinMode(I2C_SCL_PIN, OUTPUT);

  for (int i = 0; i < 9; i++) {
    digitalWrite(I2C_SCL_PIN, HIGH);
    delayMicroseconds(5);
    digitalWrite(I2C_SCL_PIN, LOW);
    delayMicroseconds(5);
  }

  pinMode(I2C_SCL_PIN, INPUT_PULLUP);
}

bool writeFile(const String &path, const String &data) {
  File file = LittleFS.open(path, FILE_WRITE);
  if (!file) return false;
  bool ok = file.println(data);
  file.close();
  return ok;
}

void appendFile(const String &path, const String &message) {
  File file = LittleFS.open(path, FILE_APPEND);
  if (!file) return;
  file.println(message);
  file.close();
}

// ============= Validação de Dados (NOVO) =============

bool validarDados(const SensorData &data) {
  // Verificar NaN
  if (isnan(data.ax) || isnan(data.ay) || isnan(data.az)) return false;
  if (isnan(data.pressao) || isnan(data.altura)) return false;
  if (isnan(data.vz)) return false;

  // Verificar ranges
  if (fabs(data.ax) > MAX_ACCEL_G || fabs(data.ay) > MAX_ACCEL_G || fabs(data.az) > MAX_ACCEL_G) {
    Serial.printf("⚠️ Aceleração fora do range: %.2f, %.2f, %.2f\n", data.ax, data.ay, data.az);
    return false;
  }

  if (data.pressao < MIN_PRESSURE_PA || data.pressao > MAX_PRESSURE_PA) {
    Serial.printf("⚠️ Pressão fora do range: %.0f Pa\n", data.pressao);
    return false;
  }

  // Velocidade vertical > 30 m/s é suspeito (seria 108 km/h)
  if (fabs(data.vz) > 30.0) {
    Serial.printf("⚠️ Vz fora do range: %.2f m/s\n", data.vz);
    return false;
  }

  return true;
}

// ============= Cálculo de Taxa de Descida (NOVO) =============

float calcularVelocidadeVertical(float altura_atual, unsigned long millis_atual) {
  if (millis_anterior == 0) {
    millis_anterior = millis_atual;
    altura_anterior = altura_atual;
    return 0.0;
  }

  unsigned long dt_ms = millis_atual - millis_anterior;
  if (dt_ms == 0) return vz_anterior;

  float dt_s = dt_ms / 1000.0;
  float vz = (altura_atual - altura_anterior) / dt_s;

  // Filtro simples: média de 3 amostras para suavização
  static float vz_filtrada = 0;
  vz_filtrada = 0.7 * vz_filtrada + 0.3 * vz;

  millis_anterior = millis_atual;
  altura_anterior = altura_atual;
  vz_anterior = vz_filtrada;

  return vz_filtrada;
}

// ============= Magnitude do Giroscópio (NOVO) =============

float calcularMagnitudeGiroscopia(float gx, float gy, float gz) {
  return sqrt(gx * gx + gy * gy + gz * gz);
}

// ============= Detecção de Apogeu (NOVO) =============

void verificarApogeu(float vz, unsigned long millis_atual) {
  // Apogeu é quando Vz muda de positivo para negativo e permanece em descida
  
  if (!em_descida && vz < -0.5) {
    // Acabou de começar a descer
    em_descida = true;
    tempo_descida_inicio = millis_atual;
    
    if (!eventos.apogeu_detectado) {
      // Primeira detecção de descida = apogeu!
      eventos.apogeu_detectado = true;
      eventos.tempo_apogeu_ms = millis_atual;
      eventos.altitude_max = altura_anterior;
      
      Serial.printf("\nAPOGEU DETECTADO!\n");
      Serial.printf("   Tempo: %lu ms\n", eventos.tempo_apogeu_ms);
      Serial.printf("   Altitude: %.2f m\n", eventos.altitude_max);
      Serial.printf("   Vz: %.2f m/s\n\n", vz);
    }
  }
  
  // Atualizar velocidade máxima de descida
  if (em_descida && vz < eventos.velocidade_max_descida) {
    eventos.velocidade_max_descida = vz;
  }
}

// ============= Leitura de Sensores =============

void readSensors(SensorData &data) {
  data.millis = millis();

  // ICM20602
  if (icm_ok) {
    int16_t ax_raw = icm_read16(0x3B);
    int16_t ay_raw = icm_read16(0x3D);
    int16_t az_raw = icm_read16(0x3F);
    int16_t gx_raw = icm_read16(0x43);
    int16_t gy_raw = icm_read16(0x45);
    int16_t gz_raw = icm_read16(0x47);

    data.ax = ax_raw * (9.80665 / 16384.0);
    data.ay = ay_raw * (9.80665 / 16384.0);
    data.az = az_raw * (9.80665 / 16384.0);

    data.gx = gx_raw * (3.14159265359 / (180.0 * 131.0));
    data.gy = gy_raw * (3.14159265359 / (180.0 * 131.0));
    data.gz = gz_raw * (3.14159265359 / (180.0 * 131.0));

    data.mag_giroscopia = calcularMagnitudeGiroscopia(data.gx, data.gy, data.gz);
  }

  // BMP280
  if (bmp_ok) {
    data.pressao = bmp.readPressure();
    data.altura = bmp.readAltitude(1013.25);
    data.vz = calcularVelocidadeVertical(data.altura, data.millis);
  }
}

// ============= Logging com Validação =============

void logData() {
  SensorData data;
  readSensors(data);

  // Validar dados
  if (!validarDados(data)) {
    Serial.println("❌ Dados inválidos, skipping...");
    return;
  }

  // Verificar apogeu
  verificarApogeu(data.vz, data.millis);

  // Atualizar máximos
  eventos.aceleracacao_max = max(eventos.aceleracacao_max, 
                                  sqrt(data.ax*data.ax + data.ay*data.ay + data.az*data.az));

  // Formatar CSV
  String data_string = String(data.millis) + ",";
  data_string += String(data.ax, 2) + "," + String(data.ay, 2) + "," + String(data.az, 2) + ",";
  data_string += String(data.gx, 4) + "," + String(data.gy, 4) + "," + String(data.gz, 4) + ",";
  data_string += String(data.pressao, 2) + "," + String(data.altura, 2) + ",";
  data_string += String(data.vz, 2) + "," + String(data.mag_giroscopia, 4);

  // Serial output
  Serial.printf("[%lu] A: %.2f %.2f %.2f | G: %.2f %.2f %.2f | P: %.0f | Alt: %.2f | Vz: %.2f | Rot: %.4f\n",
                data.millis, data.ax, data.ay, data.az, data.gx, data.gy, data.gz, 
                data.pressao, data.altura, data.vz, data.mag_giroscopia);

  // Log
  if (sd_ok) {
    appendFile(file_path, data_string);
  }
}

// ============= Setup =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=== Teste Unificado de Sensores v2 (MELHORADO) ===\n");

  // Inicializar estruturas
  eventos.apogeu_detectado = false;
  eventos.altitude_max = 0;
  eventos.velocidade_max_descida = 0.0;
  eventos.aceleracacao_max = 0.0;

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  delay(100);

  icm_ok = setupICM20602();
  resetI2C();
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  bmp_ok = setupBMP280();

  Serial.println("\nInicializando LittleFS...");
  sd_ok = setupLittleFS();

  if (sd_ok) {
    file_path = "/" + String(FILE_NAME);
    String header = "millis,ax_ms2,ay_ms2,az_ms2,gx_rads,gy_rads,gz_rads,pressao_Pa,altura_m,vz_ms,mag_giroscopia_rads";
    writeFile(file_path, header);
    Serial.printf("✅ Salvando em: %s\n", file_path.c_str());
  }

  Serial.println("\n=== Status dos Sensores ===");
  Serial.printf("ICM20602: %s\n", icm_ok ? "✅ OK" : "❌ FALHA");
  Serial.printf("BMP280: %s\n", bmp_ok ? "✅ OK" : "❌ FALHA");
  Serial.printf("LittleFS: %s\n", sd_ok ? "✅ OK" : "❌ FALHA");
  Serial.printf("\n=== Taxa de Aquisição: 20 Hz (50 ms) ===\n");
  Serial.println("=== Iniciando Leituras ===\n");
}

// ============= Loop =============

void loop() {
  unsigned long current_millis = millis();

  if (current_millis - previous_millis >= INTERVAL_MS) {
    logData();
    previous_millis = current_millis;
  }

  delay(5);  // Yield para outras tarefas
}

// ============= Debug (Opcional: chamar via Serial) =============

void printEventos() {
  Serial.println("\n=== EVENTOS DETECTADOS ===");
  Serial.printf("Apogeu detectado: %s\n", eventos.apogeu_detectado ? "SIM" : "NÃO");
  Serial.printf("Tempo apogeu: %lu ms\n", eventos.tempo_apogeu_ms);
  Serial.printf("Altitude máxima: %.2f m\n", eventos.altitude_max);
  Serial.printf("Velocidade máxima de descida: %.2f m/s\n", eventos.velocidade_max_descida);
  Serial.printf("Aceleração máxima: %.2f m/s²\n", eventos.aceleracacao_max);
  Serial.println("========================\n");
}
