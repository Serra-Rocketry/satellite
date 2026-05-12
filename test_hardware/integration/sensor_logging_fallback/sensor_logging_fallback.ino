/*
 * SRAB Logger v2 — ICM-20602 + BMP280
 * Serra Rocketry Team — Helike Mission
 */

#include <Wire.h>
#include "FS.h"
#include "SD.h"
#include "LittleFS.h"
#include <Adafruit_BMP280.h>

#if defined(CONFIG_IDF_TARGET_ESP32C3)
  #define I2C_SDA_PIN 8
  #define I2C_SCL_PIN 9
#else
  #define I2C_SDA_PIN 21
  #define I2C_SCL_PIN 22
#endif

// ============= Configurações =============
#define ICM_ADDR          0x69
#define INTERVAL_MS       50        // 20 Hz
#define SD_CS_PIN         5
#define FLUSH_EVERY_N     10        // flush SD a cada 10 amostras (~0.5 s)

// [1] ±2000°/s: fator = 16.4 LSB/(°/s)
#define GYRO_SENS_FACTOR  (float)(3.14159265359 / (180.0 * 16.4))

// [2] ±16g: fator = 2048 LSB/g
#define ACCEL_SENS_FACTOR (float)(9.80665 / 2048.0)
#define MAX_ACCEL_MS2     (16.0 * 9.80665)  // 16g em m/s²

#define MIN_PRESSURE_PA   30000
#define MAX_PRESSURE_PA   120000
#define MAX_VZ_MS         100.0    // limite generoso para ±2000°/s de spin real

// ============= Estruturas =============
enum StorageType { STORAGE_NONE, STORAGE_SD, STORAGE_LITTLEFS };

struct SensorData {
  unsigned long millis_ts;
  float ax, ay, az;      // m/s²
  float gx, gy, gz;      // rad/s  (eixos corpo)
  float pressao;         // Pa
  float altura;          // m  (relativa ao solo — fix [4])
  float vz;             // m/s
  float mag_giroscopia;  // rad/s  (magnitude total)
  // gz é o eixo primário de spin do SRAB (vertical no corpo)
};

struct EventosQueda {
  bool          apogeu_detectado;
  unsigned long tempo_apogeu_ms;
  float         altitude_max;
  float         velocidade_max_descida;
  float         aceleracao_max;
};

// ============= Variáveis Globais =============
StorageType   storage_type     = STORAGE_NONE;
unsigned long previous_millis  = 0;
String        file_path        = "";
bool          icm_ok           = false;
bool          bmp_ok           = false;

// Barômetro — estado interno
float         p0_ground        = 1013.25;   // hPa — capturado no setup [4]
float         altura_anterior  = 0.0;
unsigned long millis_anterior  = 0;
float         vz_anterior      = 0.0;
bool          em_descida       = false;

EventosQueda  eventos          = {false, 0, 0.0, 0.0, 0.0};
Adafruit_BMP280 bmp;

// SD — arquivo persistente [5]
File          data_file;
int           sample_count     = 0;

// ============= I2C helpers =============
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
  return Wire.available() ? Wire.read() : 0xFF;
}

int16_t icm_read16(uint8_t reg) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ICM_ADDR, 2);
  if (Wire.available() < 2) return 0;
  return (Wire.read() << 8) | Wire.read();
}

// ============= Inicialização ICM-20602 =============
bool setupICM20602() {
  // Reset
  icm_writeReg(0x6B, 0x80);
  delay(100);
  // Sair do sleep, usar PLL
  icm_writeReg(0x6B, 0x01);
  delay(50);

  uint8_t who = icm_readReg(0x75);
  Serial.print("ICM-20602 WHO_AM_I: 0x");
  Serial.println(who, HEX);
  if (who != 0x12) {
    Serial.println("Erro: ICM-20602 nao encontrado!");
    return false;
  }

  // [1] GYRO_CONFIG (0x1B): FS_SEL = 3 → ±2000°/s
  //     Bits [4:3] = 11 → 0b00011000 = 0x18
  icm_writeReg(0x1B, 0x18);

  // [2] ACCEL_CONFIG (0x1C): AFS_SEL = 3 → ±16g
  //     Bits [4:3] = 11 → 0b00011000 = 0x18
  icm_writeReg(0x1C, 0x18);

  // DLPF: CONFIG (0x1A) = 3 → BW 41Hz gyro / 44Hz accel (bom para 20 Hz de logging)
  icm_writeReg(0x1A, 0x03);

  // Verificar escrita
  uint8_t gc = icm_readReg(0x1B);
  uint8_t ac = icm_readReg(0x1C);
  Serial.printf("  GYRO_CONFIG  (0x1B): 0x%02X  (esperado 0x18)\n", gc);
  Serial.printf("  ACCEL_CONFIG (0x1C): 0x%02X  (esperado 0x18)\n", ac);

  Serial.println("ICM-20602 OK: ±2000°/s | ±16g | DLPF 41Hz");
  return true;
}

// ============= Inicialização BMP280 =============
bool setupBMP280() {
  if (!bmp.begin(0x76)) {
    Serial.println("BMP280 nao encontrado!");
    return false;
  }

  // [3] STANDBY_MS_1 para atualização >20 Hz (era STANDBY_MS_500 = 2 Hz efetivo)
  //     Com SAMPLING_X2 (temp) + SAMPLING_X16 (press) + FILTER_X16:
  //     t_medida ≈ 0.5 + 2*2.3 + 16*2.3 ≈ 42ms → ~24 Hz máximo
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_1);

  // [4] Capturar pressão de referência no solo (média de 20 leituras)
  delay(200);
  double soma = 0;
  for (int i = 0; i < 20; i++) {
    soma += bmp.readPressure();
    delay(50);
  }
  p0_ground = (float)(soma / 20.0) / 100.0;  // Pa → hPa
  Serial.printf("BMP280 OK. Pressao solo: %.2f hPa → altura relativa zerada.\n", p0_ground);
  return true;
}

void resetI2C() {
  pinMode(I2C_SDA_PIN, INPUT_PULLUP);
  pinMode(I2C_SCL_PIN, OUTPUT);
  for (int i = 0; i < 9; i++) {
    digitalWrite(I2C_SCL_PIN, HIGH); delayMicroseconds(5);
    digitalWrite(I2C_SCL_PIN, LOW);  delayMicroseconds(5);
  }
  pinMode(I2C_SCL_PIN, INPUT_PULLUP);
}

// ============= Storage =============
bool setupStorage() {
  Serial.println("Inicializando SD...");
  if (SD.begin(SD_CS_PIN) && SD.cardType() != CARD_NONE) {
    storage_type = STORAGE_SD;
    Serial.printf("SD OK — tipo: %s  tamanho: %llu MB\n",
      SD.cardType() == CARD_MMC ? "MMC" :
      SD.cardType() == CARD_SD  ? "SDSC" : "SDHC",
      SD.cardSize() * 512ULL / 1048576ULL);
    return true;
  }
  Serial.println("SD falhou. Tentando LittleFS...");
  if (LittleFS.begin(true)) {
    storage_type = STORAGE_LITTLEFS;
    Serial.printf("LittleFS OK — %u bytes livres\n",
      (unsigned)(LittleFS.totalBytes() - LittleFS.usedBytes()));
    return true;
  }
  Serial.println("ERRO: Nenhum storage disponivel!");
  return false;
}

String generateFileName(const char* prefix, const char* ext) {
  for (int i = 1; i <= 999; i++) {
    char c[32];
    snprintf(c, sizeof(c), "/%s_%03d.%s", prefix, i, ext);
    bool exists = (storage_type == STORAGE_SD)      ? SD.exists(c)
                : (storage_type == STORAGE_LITTLEFS) ? LittleFS.exists(c)
                : false;
    if (!exists) return String(c);
  }
  return "/overflow.csv";
}

// [5] Abrir arquivo uma vez e manter aberto
bool openDataFile(const char* path, const char* header) {
  if (storage_type == STORAGE_SD) {
    data_file = SD.open(path, FILE_WRITE);
  } else if (storage_type == STORAGE_LITTLEFS) {
    data_file = LittleFS.open(path, FILE_WRITE);
  } else {
    return false;
  }
  if (!data_file) {
    Serial.println("Falha ao abrir arquivo de dados.");
    return false;
  }
  data_file.println(header);
  data_file.flush();
  return true;
}

// ============= Validação =============
bool validarDados(const SensorData &d) {
  if (isnan(d.ax) || isnan(d.ay) || isnan(d.az)) return false;
  if (isnan(d.pressao) || isnan(d.altura))        return false;
  if (isnan(d.vz))                                return false;

  // [2] Limite coerente com ±16g
  float a_mag = sqrt(d.ax*d.ax + d.ay*d.ay + d.az*d.az);
  if (a_mag > MAX_ACCEL_MS2) {
    Serial.printf("Aceleracao fora do range: %.1f m/s²\n", a_mag);
    return false;
  }
  if (d.pressao < MIN_PRESSURE_PA || d.pressao > MAX_PRESSURE_PA) {
    Serial.printf("Pressao fora do range: %.0f Pa\n", d.pressao);
    return false;
  }
  if (fabs(d.vz) > MAX_VZ_MS) {
    Serial.printf("Vz fora do range: %.2f m/s\n", d.vz);
    return false;
  }
  return true;
}

// ============= Velocidade Vertical =============
float calcularVz(float altura_atual, unsigned long millis_atual) {
  if (millis_anterior == 0) {
    millis_anterior = millis_atual;
    altura_anterior = altura_atual;
    return 0.0;
  }
  unsigned long dt_ms = millis_atual - millis_anterior;
  if (dt_ms == 0) return vz_anterior;

  float dt_s = dt_ms / 1000.0;
  float vz_raw = (altura_atual - altura_anterior) / dt_s;

  // EMA leve (α=0.5): equilibra ruído e latência
  static float vz_filt = 0.0;
  vz_filt = 0.5 * vz_filt + 0.5 * vz_raw;

  millis_anterior = millis_atual;
  altura_anterior = altura_atual;
  vz_anterior     = vz_filt;
  return vz_filt;
}

// ============= Detecção de Apogeu =============
void verificarApogeu(float vz, unsigned long ts) {
  if (!em_descida && vz < -0.5) {
    em_descida = true;
    if (!eventos.apogeu_detectado) {
      eventos.apogeu_detectado  = true;
      eventos.tempo_apogeu_ms   = ts;
      eventos.altitude_max      = altura_anterior;
      Serial.printf("\n>> APOGEU: t=%lu ms  alt=%.2f m  vz=%.2f m/s\n\n",
                    ts, eventos.altitude_max, vz);
    }
  }
  if (em_descida && vz < eventos.velocidade_max_descida)
    eventos.velocidade_max_descida = vz;
}

// ============= Leitura de Sensores =============
void readSensors(SensorData &d) {
  d.millis_ts = millis();

  if (icm_ok) {
    int16_t ax_r = icm_read16(0x3B);
    int16_t ay_r = icm_read16(0x3D);
    int16_t az_r = icm_read16(0x3F);
    int16_t gx_r = icm_read16(0x43);
    int16_t gy_r = icm_read16(0x45);
    int16_t gz_r = icm_read16(0x47);

    // [2] ±16g
    d.ax = ax_r * ACCEL_SENS_FACTOR;
    d.ay = ay_r * ACCEL_SENS_FACTOR;
    d.az = az_r * ACCEL_SENS_FACTOR;

    // [1] ±2000°/s
    d.gx = gx_r * GYRO_SENS_FACTOR;
    d.gy = gy_r * GYRO_SENS_FACTOR;
    d.gz = gz_r * GYRO_SENS_FACTOR;

    d.mag_giroscopia = sqrt(d.gx*d.gx + d.gy*d.gy + d.gz*d.gz);
  }

  if (bmp_ok) {
    d.pressao = bmp.readPressure();
    // [4] altitude relativa ao solo
    d.altura  = bmp.readAltitude(p0_ground);
    d.vz      = calcularVz(d.altura, d.millis_ts);
  }
}

// ============= Logging =============
void logData() {
  SensorData d;
  readSensors(d);

  if (!validarDados(d)) {
    Serial.println("Dados invalidos, skipping.");
    return;
  }

  verificarApogeu(d.vz, d.millis_ts);
  eventos.aceleracao_max = max(eventos.aceleracao_max,
    sqrt(d.ax*d.ax + d.ay*d.ay + d.az*d.az));

  // [6] gz separado como eixo primário de spin
  //     Colunas: millis, ax, ay, az, gx, gy, gz, mag_giro, gz_spin_rads,
  //              pressao, altura_rel, vz
  char buf[180];
  snprintf(buf, sizeof(buf),
    "%lu,%.2f,%.2f,%.2f,%.4f,%.4f,%.4f,%.4f,%.4f,%.2f,%.2f,%.2f",
    d.millis_ts,
    d.ax, d.ay, d.az,
    d.gx, d.gy, d.gz,
    d.mag_giroscopia,
    d.gz,          // eixo de spin (yaw no corpo)
    d.pressao, d.altura, d.vz);

  Serial.printf("[%lu] A:%.1f,%.1f,%.1f | G:%.2f,%.2f,%.2f | gz=%.2f rad/s (%.1f RPM) | Alt:%.2f m | Vz:%.2f m/s\n",
    d.millis_ts, d.ax, d.ay, d.az, d.gx, d.gy, d.gz,
    d.gz, fabs(d.gz) * 60.0 / (2.0 * 3.14159265),
    d.altura, d.vz);

  // [5] Escrever sem fechar — flush periódico
  if (data_file) {
    data_file.println(buf);
    sample_count++;
    if (sample_count % FLUSH_EVERY_N == 0) {
      data_file.flush();
    }
  }
}

// ============= Setup =============
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== SRAB Logger v2 ===\n");

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  delay(100);

  icm_ok = setupICM20602();

  resetI2C();
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  bmp_ok = setupBMP280();

  if (!setupStorage()) {
    Serial.println("AVISO: sem storage. Apenas Serial.");
  }

  if (storage_type != STORAGE_NONE) {
    const char* prefix = (storage_type == STORAGE_SD) ? "Dados" : "dados";
    file_path = generateFileName(prefix, "csv");

    // [6] Header com gz_spin separado
    const char* header =
      "millis,ax_ms2,ay_ms2,az_ms2,"
      "gx_rads,gy_rads,gz_rads,"
      "mag_giroscopia_rads,gz_spin_rads,"
      "pressao_Pa,altura_rel_m,vz_ms";

    if (!openDataFile(file_path.c_str(), header)) {
      Serial.println("ERRO ao criar arquivo de dados!");
    } else {
      Serial.printf("Arquivo: %s\n", file_path.c_str());
    }
  }

  Serial.println("\n=== Status ===");
  Serial.printf("ICM-20602: %s  (±2000°/s | ±16g)\n", icm_ok ? "OK" : "FALHA");
  Serial.printf("BMP280:    %s  (standby 1ms | ref=%.2f hPa)\n", bmp_ok ? "OK" : "FALHA", p0_ground);
  Serial.printf("Storage:   %s\n",
    storage_type == STORAGE_SD      ? "SD (arquivo persistente)" :
    storage_type == STORAGE_LITTLEFS ? "LittleFS (arquivo persistente)" : "NENHUM");
  Serial.printf("Arquivo:   %s\n", file_path.c_str());
  Serial.printf("\n=== 20 Hz | flush a cada %d amostras ===\n\n", FLUSH_EVERY_N);
}

// ============= Loop =============
void loop() {
  unsigned long now = millis();
  if (now - previous_millis >= INTERVAL_MS) {
    previous_millis = now;
    logData();
  }
  // sem delay() fixo — deixa o scheduler respirar
  yield();
}
