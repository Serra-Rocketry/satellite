/*
 * Teste BMP280 com Salvamento em SPIFFS
 * Salva dados de pressão e altura em arquivo CSV
 */

#include <Wire.h>
#include "FS.h"
#include "SPIFFS.h"
#include <Adafruit_BMP280.h>

// ============= Configurações =============

#define INTERVAL 500  // Intervalo de leitura em ms
#define FILE_NAME "/dados_bmp280.csv"

// ============= Variáveis Globais =============

Adafruit_BMP280 bmp;
unsigned long previous_millis = 0;
bool bmp_ok = false;
bool spiffs_ok = false;

// ============= Inicialização do BMP280 =============

bool setupBMP280() {
  unsigned status = bmp.begin(0x76);
  if (!status) {
    Serial.println("BMP280 não encontrado! Verifique conexão.");
    Serial.print("SensorID: 0x");
    Serial.println(bmp.sensorID(), HEX);
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

// ============= Inicialização do SPIFFS =============

bool setupSPIFFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("Erro ao montar SPIFFS.");
    return false;
  }
  Serial.println("SPIFFS montado com sucesso!");
  
  // Exibe informações sobre o espaço
  size_t total = SPIFFS.totalBytes();
  size_t used = SPIFFS.usedBytes();
  Serial.printf("SPIFFS: %d bytes total, %d bytes usados\n", total, used);
  
  return true;
}

// ============= Funções de Arquivo =============

bool writeFile(const char *path, const char *message) {
  File file = SPIFFS.open(path, FILE_WRITE);
  if (!file) {
    Serial.println("Falha ao abrir arquivo para gravação.");
    return false;
  }
  if (file.println(message)) {
    Serial.println("Cabeçalho escrito.");
    file.close();
    return true;
  } else {
    Serial.println("Falha na gravação do arquivo.");
    file.close();
    return false;
  }
}

void appendFile(const char *path, const char *message) {
  File file = SPIFFS.open(path, FILE_APPEND);
  if (!file) {
    Serial.println("Falha ao abrir arquivo para anexar.");
    return;
  }
  if (file.print(String(message) + "\n")) {
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

  // Imprime no serial
  Serial.printf("[%lu] T: %.2f°C | P: %.2f Pa | Alt: %.2f m\n",
                current_millis, temperatura, pressao, altura);

  // Prepara string para salvar
  char buffer[100];
  snprintf(buffer, sizeof(buffer), "%lu,%.2f,%.2f,%.2f",
           current_millis, temperatura, pressao, altura);

  // Salva no arquivo
  if (spiffs_ok) {
    appendFile(FILE_NAME, buffer);
  }
}

// ============= Setup =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=== Teste BMP280 com SPIFFS ===\n");

  // Inicializa I2C
  Wire.begin(21, 22);
  delay(100);

  // Inicializa BMP280
  Serial.println("Inicializando BMP280...");
  bmp_ok = setupBMP280();

  // Inicializa SPIFFS
  Serial.println("\nInicializando SPIFFS...");
  spiffs_ok = setupSPIFFS();

  // Cria arquivo com cabeçalho
  if (spiffs_ok) {
    Serial.printf("\nCriando arquivo: %s\n", FILE_NAME);
    const char *header = "millis,temperatura_C,pressao_Pa,altura_m";
    if (!writeFile(FILE_NAME, header)) {
      Serial.println("Erro ao criar arquivo!");
      spiffs_ok = false;
    }
  }

  Serial.println("\n=== Status ===");
  Serial.printf("BMP280: %s\n", bmp_ok ? "OK" : "FALHA");
  Serial.printf("SPIFFS: %s\n", spiffs_ok ? "OK" : "FALHA");
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
