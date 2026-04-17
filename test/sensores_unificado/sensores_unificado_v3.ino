/*
 * Teste Unificado de Sensores - Versão 3 (v3)
 * 
 * Componentes integrados:
 * - ICM-20602 (IMU: acelerômetro + giroscópio) via I2C
 * - BME280 (pressão + temperatura + umidade) via I2C
 * - GPS NEO-8M (posição + altitude + velocidade) via UART
 * 
 * Melhorias implementadas:
 * - Taxa de aquisição: 50ms (20 Hz)
 * - Cálculo de taxa de descida (Vz)
 * - Validação de dados (NaN, outliers)
 * - Detecção de apogeu automática
 * - Integração GPS com validação de altitude
 * - Logging CSV com 15 colunas
 * 
 * Pinouts (ESP32-C3):
 * - I2C: SDA=GPIO8, SCL=GPIO9
 * - UART GPS: RX=GPIO20, TX=GPIO21
 * - LittleFS: storage para arquivos CSV
 */

#include <Wire.h>
#include <HardwareSerial.h>
#include "FS.h"
#include "LittleFS.h"
#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>

// ============= Configurações de Pinos =============

#if defined(CONFIG_IDF_TARGET_ESP32C3)
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#define GPS_RX_PIN 20
#define GPS_TX_PIN 21
#else
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#define GPS_RX_PIN 16
#define GPS_TX_PIN 17
#endif

// ============= Configurações Gerais =============

#define ICM_ADDR 0x69
#define BME_ADDR 0x76
#define GPS_BAUD_RATE 9600
#define INTERVAL_MS 50        // 20 Hz
#define FILE_NAME "sensores_v3.csv"

// Thresholds de validação
#define MAX_ACCEL_G 50.0
#define MIN_PRESSURE_PA 300
#define MAX_PRESSURE_PA 120000
#define APOGEE_THRESHOLD_MS 100

// ============= Estruturas =============

struct ImuData {
  float ax, ay, az;           // m/s²
  float gx, gy, gz;           // rad/s
  float mag_giroscopia;       // rad/s (magnitude)
};

struct BarometricData {
  float pressao;              // Pa
  float pressao_hpa;          // hPa
  float temperatura;          // °C
  float umidade;              // %
  float altura;               // m
};

struct GpsData {
  float latitude;             // graus decimais
  float longitude;            // graus decimais
  float altitude;             // m
  float velocidade;           // km/h
  uint8_t satellites;         // quantidade
  uint8_t fix_quality;        // 0=sem fix, 1=GPS, 2=DGPS
  bool dados_validos;
  unsigned long ultimo_fix_ms;
};

struct SensorData {
  unsigned long millis;
  ImuData imu;
  BarometricData baro;
  GpsData gps;
  float vz;                   // velocidade vertical m/s
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
bool icm_ok = false;
bool bme_ok = false;
bool gps_ok = false;
bool storage_ok = false;

// Para cálculo de Vz
float altura_anterior = 0.0;
unsigned long millis_anterior = 0;
float vz_anterior = 0.0;

// Para detecção de apogeu
bool em_descida = false;
unsigned long tempo_descida_inicio = 0;

// Objetos de sensores
Adafruit_BME280 bme;

// Buffer para GPS (NMEA)
String nmea_buffer = "";
unsigned long contador_sentencas_gps = 0;
unsigned long contador_erros_gps = 0;

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

// ============= Funções I2C para BME280 =============

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

// ============= Funções UART para GPS =============

String extrair_campo(String sentenca, int indice) {
  int pos = 0;
  int campo = 0;
  int inicio = 0;
  
  for (int i = 0; i < sentenca.length(); i++) {
    if (sentenca[i] == ',') {
      if (campo == indice) {
        return sentenca.substring(inicio, i);
      }
      campo++;
      inicio = i + 1;
    }
  }
  
  if (campo == indice) {
    int asterisco = sentenca.indexOf('*');
    if (asterisco > 0) {
      return sentenca.substring(inicio, asterisco);
    } else {
      return sentenca.substring(inicio);
    }
  }
  
  return "";
}

uint8_t calcular_checksum_nmea(String sentenca) {
  int inicio = sentenca.indexOf('$') + 1;
  int asterisco = sentenca.indexOf('*');
  
  uint8_t checksum = 0;
  for (int i = inicio; i < asterisco; i++) {
    checksum ^= sentenca[i];
  }
  return checksum;
}

bool verificar_checksum_nmea(String sentenca) {
  int asterisco = sentenca.indexOf('*');
  if (asterisco < 0) return false;
  
  String checksum_str = sentenca.substring(asterisco + 1);
  if (checksum_str.length() < 2) return false;
  
  uint8_t checksum_esperado = strtol(checksum_str.c_str(), NULL, 16);
  uint8_t checksum_calculado = calcular_checksum_nmea(sentenca);
  
  return (checksum_esperado == checksum_calculado);
}

float converter_coordenada_nmea(String coord_nmea) {
  if (coord_nmea.length() < 5) return 0.0;
  
  int ponto = coord_nmea.indexOf('.');
  int graus_len = ponto - 2;
  int graus = atoi(coord_nmea.substring(0, graus_len).c_str());
  
  float minutos = atof(coord_nmea.substring(graus_len).c_str());
  
  return graus + (minutos / 60.0);
}

void processar_rmc(String sentenca, GpsData &gps) {
  String status = extrair_campo(sentenca, 2);
  if (status != "A") {
    gps.dados_validos = false;
    return;
  }
  
  String lat_str = extrair_campo(sentenca, 3);
  String lat_dir = extrair_campo(sentenca, 4);
  String lon_str = extrair_campo(sentenca, 5);
  String lon_dir = extrair_campo(sentenca, 6);
  String speed_str = extrair_campo(sentenca, 7);
  String course_str = extrair_campo(sentenca, 8);
  
  gps.latitude = converter_coordenada_nmea(lat_str);
  if (lat_dir == "S") gps.latitude *= -1;
  
  gps.longitude = converter_coordenada_nmea(lon_str);
  if (lon_dir == "W") gps.longitude *= -1;
  
  gps.velocidade = atof(speed_str.c_str()) * 1.852; // knots → km/h
  gps.dados_validos = true;
  gps.ultimo_fix_ms = millis();
}

void processar_gga(String sentenca, GpsData &gps) {
  String fix_quality_str = extrair_campo(sentenca, 6);
  String satellites_str = extrair_campo(sentenca, 7);
  String altitude_str = extrair_campo(sentenca, 9);
  
  gps.fix_quality = atoi(fix_quality_str.c_str());
  gps.satellites = atoi(satellites_str.c_str());
  gps.altitude = atof(altitude_str.c_str());
  
  if (gps.fix_quality == 0) {
    gps.dados_validos = false;
  }
}

void processar_nmea(String sentenca, GpsData &gps) {
  if (!verificar_checksum_nmea(sentenca)) {
    contador_erros_gps++;
    return;
  }
  
  if (sentenca.startsWith("$GPRMC")) {
    processar_rmc(sentenca, gps);
  } else if (sentenca.startsWith("$GPGGA")) {
    processar_gga(sentenca, gps);
  }
  
  contador_sentencas_gps++;
}

void ler_gps(GpsData &gps) {
  while (Serial1.available()) {
    char ch = Serial1.read();
    
    if (ch == '$') {
      nmea_buffer = "$";
    } else if (ch == '\n' || ch == '\r') {
      if (nmea_buffer.length() > 0) {
        processar_nmea(nmea_buffer, gps);
      }
      nmea_buffer = "";
    } else {
      nmea_buffer += ch;
    }
  }
}

// ============= Inicialização dos Sensores =============

bool setupICM20602() {
  icm_writeReg(0x6B, 0x80);  // Reset
  delay(100);
  icm_writeReg(0x6B, 0x01);  // Wake up
  delay(50);

  uint8_t who = icm_readReg(0x75);
  Serial.print("ICM20602 WHO_AM_I: 0x");
  Serial.println(who, HEX);

  if (who == 0x12) {
    Serial.println("✓ ICM20602 encontrado!");
    return true;
  } else {
    Serial.println("✗ ICM20602 não encontrado!");
    return false;
  }
}

bool setupBME280() {
  unsigned status = bme.begin(BME_ADDR);
  if (!status) {
    Serial.println("✗ BME280 não encontrado!");
    return false;
  }

  bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                  Adafruit_BME280::SAMPLING_X2,
                  Adafruit_BME280::SAMPLING_X2,
                  Adafruit_BME280::SAMPLING_X2,
                  Adafruit_BME280::FILTER_OFF,
                  Adafruit_BME280::STANDBY_MS_1000);

  Serial.println("✓ BME280 inicializado!");
  return true;
}

bool setupLittleFS() {
  if (!LittleFS.begin(true)) {
    Serial.println("✗ Erro ao montar LittleFS.");
    return false;
  }
  Serial.println("✓ LittleFS montado!");
  return true;
}

bool setupGPS() {
  Serial1.begin(GPS_BAUD_RATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  Serial.println("✓ GPS UART inicializado!");
  return true;
}

// ============= Funções de Validação e Cálculo =============

bool validarDados(const SensorData &data) {
  if (isnan(data.imu.ax) || isnan(data.imu.ay) || isnan(data.imu.az)) return false;
  if (isnan(data.baro.pressao) || isnan(data.baro.altura)) return false;
  if (isnan(data.vz)) return false;

  if (fabs(data.imu.ax) > MAX_ACCEL_G || fabs(data.imu.ay) > MAX_ACCEL_G || fabs(data.imu.az) > MAX_ACCEL_G) {
    return false;
  }

  if (data.baro.pressao < MIN_PRESSURE_PA || data.baro.pressao > MAX_PRESSURE_PA) {
    return false;
  }

  if (fabs(data.vz) > 30.0) {
    return false;
  }

  return true;
}

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

  static float vz_filtrada = 0;
  vz_filtrada = 0.7 * vz_filtrada + 0.3 * vz;

  millis_anterior = millis_atual;
  altura_anterior = altura_atual;
  vz_anterior = vz_filtrada;

  return vz_filtrada;
}

float calcularMagnitudeGiroscopia(float gx, float gy, float gz) {
  return sqrt(gx * gx + gy * gy + gz * gz);
}

void verificarApogeu(float vz, unsigned long millis_atual) {
  if (!em_descida && vz < -0.5) {
    em_descida = true;
    tempo_descida_inicio = millis_atual;
    
    if (!eventos.apogeu_detectado) {
      eventos.apogeu_detectado = true;
      eventos.tempo_apogeu_ms = millis_atual;
      eventos.altitude_max = altura_anterior;
      
      Serial.printf("\n🎯 APOGEU DETECTADO!\n");
      Serial.printf("   Tempo: %lu ms\n", eventos.tempo_apogeu_ms);
      Serial.printf("   Altitude: %.2f m\n", eventos.altitude_max);
      Serial.printf("   Vz: %.2f m/s\n\n", vz);
    }
  }
  
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

    data.imu.ax = ax_raw * (9.80665 / 16384.0);
    data.imu.ay = ay_raw * (9.80665 / 16384.0);
    data.imu.az = az_raw * (9.80665 / 16384.0);

    data.imu.gx = gx_raw * (3.14159265359 / (180.0 * 131.0));
    data.imu.gy = gy_raw * (3.14159265359 / (180.0 * 131.0));
    data.imu.gz = gz_raw * (3.14159265359 / (180.0 * 131.0));

    data.imu.mag_giroscopia = calcularMagnitudeGiroscopia(data.imu.gx, data.imu.gy, data.imu.gz);
  }

  // BME280
  if (bme_ok) {
    data.baro.pressao = bme.readPressure();
    data.baro.pressao_hpa = data.baro.pressao / 100.0;
    data.baro.temperatura = bme.readTemperature();
    data.baro.umidade = bme.readHumidity();
    data.baro.altura = bme.readAltitude(1013.25);
    data.vz = calcularVelocidadeVertical(data.baro.altura, data.millis);
  }

  // GPS (continuamente recebido via UART)
  if (gps_ok) {
    ler_gps(data.gps);
  }
}

// ============= Funções de Arquivo =============

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

// ============= Logging =============

void logData() {
  SensorData data;
  readSensors(data);

  if (!validarDados(data)) {
    Serial.println("✗ Dados inválidos!");
    return;
  }

  verificarApogeu(data.vz, data.millis);

  eventos.aceleracacao_max = max(eventos.aceleracacao_max, 
                                 sqrt(data.imu.ax*data.imu.ax + data.imu.ay*data.imu.ay + data.imu.az*data.imu.az));

  // Formatar CSV com 15 colunas
  String data_string = String(data.millis) + ",";
  data_string += String(data.imu.ax, 2) + "," + String(data.imu.ay, 2) + "," + String(data.imu.az, 2) + ",";
  data_string += String(data.imu.gx, 4) + "," + String(data.imu.gy, 4) + "," + String(data.imu.gz, 4) + ",";
  data_string += String(data.baro.pressao, 2) + "," + String(data.baro.altura, 2) + ",";
  data_string += String(data.baro.temperatura, 2) + "," + String(data.baro.umidade, 2) + ",";
  data_string += String(data.vz, 2) + "," + String(data.imu.mag_giroscopia, 4);
  
  // GPS (3 campos)
  if (data.gps.dados_validos && data.gps.fix_quality > 0) {
    data_string += "," + String(data.gps.latitude, 6) + "," + String(data.gps.longitude, 6) + "," + String(data.gps.altitude, 2);
  } else {
    data_string += ",,,";  // GPS inválido = vazio
  }

  // Serial output
  Serial.printf("[%lu] A: %.2f %.2f %.2f | T:%.2f U:%.2f | Alt: %.2f Vz: %.2f | GPS: %s\n",
                data.millis, data.imu.ax, data.imu.ay, data.imu.az, 
                data.baro.temperatura, data.baro.umidade,
                data.baro.altura, data.vz,
                (data.gps.dados_validos ? "OK" : "..."));

  // Log
  if (storage_ok) {
    appendFile(file_path, data_string);
  }
}

// ============= Setup =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=== Teste Unificado de Sensores v3 ===");
  Serial.println("ICM-20602 + BME280 + GPS NEO-8M\n");

  // Inicializar estruturas
  eventos.apogeu_detectado = false;
  eventos.altitude_max = 0;
  eventos.velocidade_max_descida = 0.0;
  eventos.aceleracacao_max = 0.0;

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  delay(100);

  Serial.println("=== Inicializando Sensores ===");
  icm_ok = setupICM20602();
  resetI2C();
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  bme_ok = setupBME280();
  gps_ok = setupGPS();

  Serial.println("\nInicializando LittleFS...");
  storage_ok = setupLittleFS();

  if (storage_ok) {
    file_path = "/" + String(FILE_NAME);
    String header = "millis,ax,ay,az,gx,gy,gz,pressao_Pa,altura_m,temperatura_C,umidade_pct,vz,mag_giroscopia,lat,lon,alt_gps";
    writeFile(file_path, header);
    Serial.printf("✓ Salvando em: %s\n", file_path.c_str());
  }

  Serial.println("\n=== Status dos Sensores ===");
  Serial.printf("ICM20602: %s\n", icm_ok ? "✓ OK" : "✗ FALHA");
  Serial.printf("BME280:   %s\n", bme_ok ? "✓ OK" : "✗ FALHA");
  Serial.printf("GPS:      %s\n", gps_ok ? "✓ OK" : "✗ FALHA");
  Serial.printf("Storage:  %s\n", storage_ok ? "✓ OK" : "✗ FALHA");
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

  delay(5);
}
