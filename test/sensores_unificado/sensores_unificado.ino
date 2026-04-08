/*
 * Teste Unificado de Sensores
 * Acelerômetro (ICM20602) + Giroscópio (ICM20602) + Pressão + Altura (BMP280)
 * Salva dados em arquivo CSV via LittleFS
 */

#include <Wire.h>
#include "FS.h"
#include "LittleFS.h"
#include <Adafruit_BMP280.h>

// ============= Configurações dos Sensores =============

// ICM20602
#define ICM_ADDR 0x69

// BMP280
Adafruit_BMP280 bmp;

// ============= Definições de Pinos e Constantes =============

#define INTERVAL 500  // Intervalo de leitura em ms
#define FILE_NAME "sensores.csv"

// ============= Variáveis Globais =============

unsigned long previous_millis = 0;
String file_path = "";
bool sd_ok = false;
bool icm_ok = false;
bool bmp_ok = false;

// ============= Funções I2C para ICM20602 =============

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
  return Wire.read();
}

int16_t icm_read16(uint8_t reg) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ICM_ADDR, 2);
  return (Wire.read() << 8) | Wire.read();
}

// ============= Inicialização do ICM20602 =============

bool setupICM20602() {
  // Reset
  icm_writeReg(0x6B, 0x80);
  delay(100);

  // Wake up
  icm_writeReg(0x6B, 0x01);
  delay(50);

  // Teste WHO_AM_I
  uint8_t who = icm_readReg(0x75);
  Serial.print("ICM20602 WHO_AM_I: 0x");
  Serial.println(who, HEX);

  if (who == 0x12) {  // ID correto do ICM20602
    Serial.println("ICM20602 encontrado!");
    return true;
  } else {
    Serial.println("Erro: ICM20602 não encontrado!");
    return false;
  }
}

// ============= Inicialização do BMP280 =============

bool setupBMP280() {
  unsigned status = bmp.begin(0x76);
  if (!status) {
    Serial.println("BMP280 não encontrado! Verifique conexão.");
    return false;
  }

  // Configurações padrão
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);

  Serial.println("BMP280 inicializado com sucesso!");
  return true;
}

// ============= Inicialização do LittleFS =============

bool setupLittleFS() {
  if (!LittleFS.begin(true)) {
    Serial.println("Erro ao montar LittleFS.");
    return false;
  }
  Serial.println("LittleFS montado com sucesso!");
  return true;
}

// ============= Funções de Arquivo =============

bool writeFile(const String &path, const String &data) {
  File file = LittleFS.open(path, FILE_WRITE);
  if (!file) {
    Serial.println("Falha ao abrir arquivo para gravação.");
    return false;
  }
  if (file.println(data)) {
    Serial.println("Cabeçalho escrito.");
    file.close();
    return true;
  } else {
    Serial.println("Falha na gravação do arquivo.");
    file.close();
    return false;
  }
}

void appendFile(const String &path, const String &message) {
  File file = LittleFS.open(path, FILE_APPEND);
  if (!file) {
    Serial.println("Falha ao abrir arquivo para anexar.");
    return;
  }
  if (file.print(message + "\n")) {
    Serial.println("Dados anexados ao arquivo.");
  } else {
    Serial.println("Falha ao anexar mensagem.");
  }
  file.close();
}

// ============= Função de Leitura de Sensores =============

void readSensors(float &ax, float &ay, float &az, float &gx, float &gy, float &gz,
                 float &pressao, float &altura) {
  // Lê ICM20602
  if (icm_ok) {
    int16_t ax_raw = icm_read16(0x3B);
    int16_t ay_raw = icm_read16(0x3D);
    int16_t az_raw = icm_read16(0x3F);

    int16_t gx_raw = icm_read16(0x43);
    int16_t gy_raw = icm_read16(0x45);
    int16_t gz_raw = icm_read16(0x47);

    // Conversões
    ax = ax_raw * (9.80665 / 16384.0);
    ay = ay_raw * (9.80665 / 16384.0);
    az = az_raw * (9.80665 / 16384.0);

    gx = gx_raw * (3.14159265359 / (180.0 * 131.0));
    gy = gy_raw * (3.14159265359 / (180.0 * 131.0));
    gz = gz_raw * (3.14159265359 / (180.0 * 131.0));
  }

  // Lê BMP280
  if (bmp_ok) {
    pressao = bmp.readPressure();
    altura = bmp.readAltitude(1013.25);
  }
}

// ============= Função de Log de Dados =============

void logData(unsigned long current_millis) {
  float ax, ay, az, gx, gy, gz, pressao, altura;
  readSensors(ax, ay, az, gx, gy, gz, pressao, altura);

  // Formata a string com os dados
  String data_string = String(current_millis) + ",";
  data_string += String(ax, 2) + "," + String(ay, 2) + "," + String(az, 2) + ",";
  data_string += String(gx, 4) + "," + String(gy, 4) + "," + String(gz, 4) + ",";
  data_string += String(pressao, 2) + "," + String(altura, 2);

  // Imprime no serial para monitoramento
  Serial.printf("[%lu] A[m/s²]: %.2f %.2f %.2f | G[rad/s]: %.2f %.2f %.2f | P[Pa]: %.0f | Alt[m]: %.2f\n",
                current_millis, ax, ay, az, gx, gy, gz, pressao, altura);

  // Salva no arquivo
  if (sd_ok) {
    appendFile(file_path, data_string);
  }
}

#define SDA_PIN 21
#define SCL_PIN 22

void resetI2C() {
  pinMode(SDA_PIN, INPUT_PULLUP);
  pinMode(SCL_PIN, OUTPUT);

  for (int i = 0; i < 9; i++) {
    digitalWrite(SCL_PIN, HIGH);
    delayMicroseconds(5);
    digitalWrite(SCL_PIN, LOW);
    delayMicroseconds(5);
  }

  pinMode(SCL_PIN, INPUT_PULLUP);
}

// ============= Setup =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=== Teste Unificado de Sensores ===\n");

  Wire.begin(21, 22);
  delay(100);

  // icm_ok = setupICM20602();

  resetI2C();
  Wire.begin(21, 22);

  bmp_ok = setupBMP280();

  Serial.println("\nInicializando LittleFS...");
  sd_ok = setupLittleFS();

  // Configura arquivo
  if (sd_ok) {
    file_path = "/" + String(FILE_NAME);
    Serial.print("Salvando dados em: ");
    Serial.println(file_path);

    // Cabeçalho: millis, ax, ay, az, gx, gy, gz, pressao, altura
    String header = "millis,ax_ms2,ay_ms2,az_ms2,gx_rads,gy_rads,gz_rads,pressao_Pa,altura_m";
    if (!writeFile(file_path, header)) {
      Serial.println("Erro ao criar arquivo!");
      sd_ok = false;
    }
  }

  Serial.println("\n=== Status dos Sensores ===");
  Serial.printf("ICM20602: %s\n", icm_ok ? "OK" : "FALHA");
  Serial.printf("BMP280: %s\n", bmp_ok ? "OK" : "FALHA");
  Serial.printf("LittleFS: %s\n", sd_ok ? "OK" : "FALHA");
  Serial.println("\n=== Iniciando Leituras ===\n");
}

// ============= Loop =============

void loop() {
  unsigned long current_millis = millis();

  if (current_millis - previous_millis >= INTERVAL) {
    logData(current_millis);
    previous_millis = current_millis;
  }

  delay(10);  // Pequeno delay para não sobrecarregar
}
