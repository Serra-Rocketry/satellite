/**
 * @file bme280.ino
 * @brief Hardware validation sketch for the BME280 sensor (I2C)
 *
 * Tests the BME280 environmental sensor reading temperature (C),
 * pressure (hPa/Pa), humidity (% RH), and barometric altitude (m).
 * Also computes dew point and heat index.
 *
 * Hardware setup:
 * - I2C: SDA=GPIO8, SCL=GPIO9
 * - Address: 0x76 (SDO=GND) or 0x77 (SDO=VCC)
 * - Library: Adafruit_BME280
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include <Wire.h>
#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>

// Configuração I2C
#if defined(CONFIG_IDF_TARGET_ESP32C3)
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#else
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#endif

#define BME280_ADDR 0x76        // Endereço I2C (0x77 se SDO=VCC)
#define INTERVAL_MS 500         // Taxa de leitura: 2 Hz

// Estrutura para dados BME280
struct Bme280Data {
  float pressao;           // Pa (Pascal)
  float pressao_hpa;       // hPa (hectopascal)
  float temperatura;       // °C
  float umidade;           // % RH (Relative Humidity)
  float altitude;          // m (calculada usando ISA)
  bool sensor_ok;
};

Adafruit_BME280 bme;
Bme280Data bme_data = {0};
unsigned long contador_leituras = 0;
unsigned long ultimo_print = 0;
unsigned long contador_erros = 0;

// Pressão ao nível do mar (Pa) - usar valor local para cálculo de altitude mais preciso
const float PRESSAO_MAR_PA = 101325.0;

// Altitude padrão (ISA) - calcula altitude com base em pressão
float calcular_altitude_isa(float pressao_pa) {
  if (pressao_pa <= 0) return 0.0;
  
  // Fórmula barométrica internacional:
  // h = (T0 / L) * [(P0 / P)^(R*L/g*M) - 1]
  // Simplificada para troposfera: h = 44330 * (1 - (P/P0)^(1/5.255))
  
  float altitude = 44330.0 * (1.0 - pow(pressao_pa / PRESSAO_MAR_PA, 1.0 / 5.255));
  return altitude;
}

// Cálculo de Índice de Calor (Heat Index) em °C
float calcular_indice_calor(float temp_c, float umidade_pct) {
  if (temp_c < 27.0) return temp_c;  // Heat Index válido apenas > 27°C
  
  float T = temp_c;
  float RH = umidade_pct;
  
  // Fórmula de Steadman aproximada
  float HI = 0.5555 * ((T - 14.55) + 0.5555 * (T - 14.55) * (RH / 100.0) - (T - 14.55) * 0.2);
  HI = T + 0.5555 * (RH / 100.0) * (T - 14.55);
  
  return HI;
}

// ============= Setup =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== Teste BME280 ===");
  
  // Inicializa I2C
  Serial.print("Inicializando I2C (SDA=");
  Serial.print(I2C_SDA_PIN);
  Serial.print(" SCL=");
  Serial.print(I2C_SCL_PIN);
  Serial.println(")...");
  
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  delay(100);
  
  // Tenta inicializar BME280
  Serial.print("Procurando BME280 no endereço 0x");
  Serial.println(BME280_ADDR, HEX);
  
  if (!bme.begin(BME280_ADDR)) {
    Serial.println("✗ BME280 não encontrado!");
    Serial.println("Verifique:");
    Serial.println("  - Conexão I2C (SDA/SCL)");
    Serial.println("  - Endereço I2C (0x76 ou 0x77)");
    Serial.println("  - Alimentação do sensor");
    bme_data.sensor_ok = false;
    return;
  }
  
  Serial.println("✓ BME280 encontrado!");
  
  // Configura modo de operação
  // Modo Normal: mede continuamente
  // Modo Forced: mede uma vez por leitura
  // Modo Sleep: economiza energia
  
  Serial.println("\nConfigurando sensor...");
  bme.setSampling(
    Adafruit_BME280::MODE_NORMAL,           // Mode
    Adafruit_BME280::SAMPLING_X2,           // Pressure sampling
    Adafruit_BME280::SAMPLING_X2,           // Temperature sampling
    Adafruit_BME280::SAMPLING_X2,           // Humidity sampling
    Adafruit_BME280::FILTER_OFF,            // Filter
    Adafruit_BME280::STANDBY_MS_1000        // Standby time
  );
  
  Serial.println("✓ Sensor configurado");
  Serial.println("  - Modo: Normal");
  Serial.println("  - Amostragem de pressão: 2x");
  Serial.println("  - Amostragem de temperatura: 2x");
  Serial.println("  - Amostragem de umidade: 2x");
  Serial.println("  - Tempo de espera: 1000ms");
  
  bme_data.sensor_ok = true;
  
  Serial.println("\nAguardando primeira leitura...\n");
  delay(2000);
}

// ============= Loop =============

void loop() {
  unsigned long agora = millis();
  
  // Lê sensor a cada INTERVAL_MS
  static unsigned long ultima_leitura = 0;
  if (agora - ultima_leitura >= INTERVAL_MS) {
    ultima_leitura = agora;
    
    if (!bme_data.sensor_ok) {
      Serial.println("✗ Sensor não inicializado!");
      return;
    }
    
    // Lê valores
    bme_data.temperatura = bme.readTemperature();
    bme_data.pressao_hpa = bme.readPressure() / 100.0;
    bme_data.pressao = bme.readPressure();
    bme_data.umidade = bme.readHumidity();
    bme_data.altitude = calcular_altitude_isa(bme_data.pressao);
    
    // Verifica valores válidos
    if (isnan(bme_data.temperatura) || isnan(bme_data.pressao) || isnan(bme_data.umidade)) {
      contador_erros++;
      Serial.println("✗ Erro na leitura do sensor!");
      return;
    }
    
    contador_leituras++;
  }
  
  // A cada 2 segundos, imprime dados
  if (agora - ultimo_print >= 2000) {
    ultimo_print = agora;
    
    Serial.println("--- Dados BME280 ---");
    Serial.print("Leituras: ");
    Serial.print(contador_leituras);
    Serial.print(" | Erros: ");
    Serial.println(contador_erros);
    
    Serial.print("Temperatura: ");
    Serial.print(bme_data.temperatura, 2);
    Serial.println(" °C");
    
    Serial.print("Pressão:     ");
    Serial.print(bme_data.pressao_hpa, 2);
    Serial.print(" hPa (");
    Serial.print(bme_data.pressao);
    Serial.println(" Pa)");
    
    Serial.print("Umidade:     ");
    Serial.print(bme_data.umidade, 2);
    Serial.println(" % RH");
    
    Serial.print("Altitude:    ");
    Serial.print(bme_data.altitude, 2);
    Serial.println(" m (ISA, P0=101325 Pa)");
    
    // Calcula ponto de orvalho (aproximado)
    // Formula Magnus simplificada
    float a = 17.27;
    float b = 237.7;  // °C
    float alpha = ((a * bme_data.temperatura) / (b + bme_data.temperatura)) + 
                   log(bme_data.umidade / 100.0);
    float ponto_orvalho = (b * alpha) / (a - alpha);
    
    Serial.print("Ponto orvalho:");
    Serial.print(ponto_orvalho, 2);
    Serial.println(" °C");
    
    Serial.print("Índice calor: ");
    Serial.print(calcular_indice_calor(bme_data.temperatura, bme_data.umidade), 2);
    Serial.println(" °C");
    
    Serial.println();
  }
}
