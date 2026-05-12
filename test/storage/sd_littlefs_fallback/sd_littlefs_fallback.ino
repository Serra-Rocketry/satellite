/*
 * Teste BMP280 com Salvamento em SD com Fallback para LittleFS
 * Tenta SD primeiro, se falhar usa LittleFS
 */

#include <Wire.h>
#include "FS.h"
#include "SD.h"
#include "LittleFS.h"
#include <Adafruit_BMP280.h>

// ============= Configurações =============

#define INTERVAL 500
#define SD_CS_PIN 5

#if CONFIG_IDF_TARGET_ESP32C3
  #define I2C_SDA_PIN 8
  #define I2C_SCL_PIN 9
#else
  #define I2C_SDA_PIN 21
  #define I2C_SCL_PIN 22
#endif

// ============= Variáveis Globais =============

enum StorageType { STORAGE_NONE, STORAGE_SD, STORAGE_LITTLEFS };
StorageType storage_type = STORAGE_NONE;

Adafruit_BMP280 bmp;
unsigned long previous_millis = 0;
bool bmp_ok = false;

// ============= Inicialização do BMP280 =============

bool setupBMP280() {
  unsigned status = bmp.begin(0x76);
  if (!status) {
    Serial.println("BMP280 nao encontrado! Verifique conexao.");
    Serial.print("SensorID: 0x");
    Serial.println(bmp.sensorID(), HEX);
    return false;
  }

  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                 Adafruit_BMP280::SAMPLING_X2,
                 Adafruit_BMP280::SAMPLING_X16,
                 Adafruit_BMP280::FILTER_X16,
                 Adafruit_BMP280::STANDBY_MS_500);

  Serial.println("BMP280 inicializado!");
  return true;
}

// ============= Inicialização do Storage (SD + LittleFS) =============

bool setupStorage() {
  // Tenta SD primeiro
  Serial.println("Inicializando SD...");
  if (SD.begin(SD_CS_PIN) && SD.cardType() != CARD_NONE) {
    storage_type = STORAGE_SD;
    Serial.println("SD iniciado com sucesso!");
    Serial.printf("SD Card Type: %s\n",
      SD.cardType() == CARD_MMC ? "MMC" :
      SD.cardType() == CARD_SD ? "SDSC" :
      SD.cardType() == CARD_SDHC ? "SDHC" : "UNKNOWN");
    Serial.printf("SD Total: %llu bytes\n", SD.cardSize() * 512ULL);
    return true;
  }

  Serial.println("SD falhou. Tentando LittleFS...");

  // Fallback para LittleFS
  if (LittleFS.begin(true)) {
    storage_type = STORAGE_LITTLEFS;
    Serial.println("LittleFS iniciado com sucesso!");
    Serial.printf("LittleFS: %u bytes total, %u bytes usados\n",
      (unsigned)LittleFS.totalBytes(), (unsigned)LittleFS.usedBytes());
    return true;
  }

  Serial.println("ERRO: Nenhum storage disponivel!");
  return false;
}

// ============= Geração de Nome de Arquivo =============

String generateFileName(const char* prefix, const char* ext) {
  for (int i = 1; i <= 999; i++) {
    char candidate[32];
    snprintf(candidate, sizeof(candidate), "/%s_%03d.%s", prefix, i, ext);

    bool exists = false;
    if (storage_type == STORAGE_SD) {
      exists = SD.exists(candidate);
    } else if (storage_type == STORAGE_LITTLEFS) {
      exists = LittleFS.exists(candidate);
    }

    if (!exists) {
      return String(candidate);
    }
  }
  return String("/overflow.csv");
}

// ============= Operações de Arquivo =============

bool writeFile(const char* path, const char* message) {
  File file;

  if (storage_type == STORAGE_SD) {
    file = SD.open(path, FILE_WRITE);
  } else if (storage_type == STORAGE_LITTLEFS) {
    file = LittleFS.open(path, FILE_WRITE);
  } else {
    return false;
  }

  if (!file) {
    Serial.println("Falha ao abrir arquivo para gravacao.");
    return false;
  }

  if (file.println(message)) {
    Serial.println("Arquivo escrito.");
    file.close();
    return true;
  }

  Serial.println("Falha na gravacao.");
  file.close();
  return false;
}

void appendFile(const char* path, const char* message) {
  File file;

  if (storage_type == STORAGE_SD) {
    file = SD.open(path, FILE_APPEND);
  } else if (storage_type == STORAGE_LITTLEFS) {
    file = LittleFS.open(path, FILE_APPEND);
  } else {
    return;
  }

  if (!file) {
    Serial.println("Falha ao abrir arquivo para anexar.");
    return;
  }

  if (file.println(message)) {
    Serial.println("Dados anexados.");
  } else {
    Serial.println("Falha ao anexar mensagem.");
  }
  file.close();
}

// ============= Função de Leitura =============

void readAndLogBMP280(unsigned long current_millis) {
  if (!bmp_ok) return;

  float temperatura = bmp.readTemperature();
  float pressao = bmp.readPressure();
  float altura = bmp.readAltitude(1013.25);

  Serial.printf("[%lu] T: %.2fC | P: %.2f Pa | Alt: %.2f m\n",
                current_millis, temperatura, pressao, altura);

  char buffer[100];
  snprintf(buffer, sizeof(buffer), "%lu,%.2f,%.2f,%.2f",
           current_millis, temperatura, pressao, altura);

  appendFile(file_path.c_str(), buffer);
}

String file_path;

// ============= Setup =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== Teste BMP280 com SD/LittleFS Fallback ===\n");

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  delay(100);

  Serial.println("Inicializando BMP280...");
  bmp_ok = setupBMP280();

  Serial.println("\nInicializando Storage...");
  if (!setupStorage()) {
    Serial.println("ERRO CRITICO: Sem storage!");
    while (1) delay(1000);
  }

  // Gera nome do arquivo
  const char* prefix = (storage_type == STORAGE_SD) ? "Dados" : "dados";
  file_path = generateFileName(prefix, "csv");
  Serial.printf("\nArquivo: %s\n", file_path.c_str());

  // Escreve cabeçalho
  const char* header = "millis,temperatura_C,pressao_Pa,altura_m";
  if (!writeFile(file_path.c_str(), header)) {
    Serial.println("ERRO ao criar arquivo!");
    while (1) delay(1000);
  }

  Serial.println("\n=== Status ===");
  Serial.printf("BMP280: %s\n", bmp_ok ? "OK" : "FALHA");
  Serial.printf("Storage: %s\n",
    storage_type == STORAGE_SD ? "SD" :
    storage_type == STORAGE_LITTLEFS ? "LittleFS" : "NENHUM");
  Serial.printf("Arquivo: %s\n", file_path.c_str());
  Serial.println("\n=== Iniciando Leituras ===\n");
}

// ============= Loop =============

void loop() {
  unsigned long current_millis = millis();

  if (current_millis - previous_millis >= INTERVAL) {
    readAndLogBMP280(current_millis);
    previous_millis = current_millis;
  }

  delay(10);
}