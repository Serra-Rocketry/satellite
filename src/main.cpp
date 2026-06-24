/**
 * @file main.cpp
 * @brief Firmware do satellite Helike PocketQube (#213 - LASC 2026)
 *
 * CONTEXTO CRITICO: O satellite fica COMPLETAMENTE DESLIGADO (sem energia)
 * ate o deploy do foguete no apogeu. Ao receber energia, o sistema ja esta
 * em descida.
 *
 * Fluxo de operacao:
 * 1. setup(): inicializa Serial, I2C, sensores, LoRa, buzzer/LED
 * 2. loop(): le sensores a cada SAMPLE_INTERVAL_MS, monta CSV, TX Serial+LoRa
 *
 * Sem FSM, sem filesystem, sem FreeRTOS — apenas loop continuo.
 *
 * @author #213 Avionics
 * @date 2026
 */

//==============================================================================
// INCLUDES
//==============================================================================

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <esp_task_wdt.h>

#include "config.h"
#include "calc/SensorData.h"
#include "calc/DataValidation.h"
#include "calc/VerticalVelocity.h"
#include "sensors/BME280Sensor.h"
#include "sensors/ICM20602Sensor.h"
#include "sensors/GPSSensor.h"
#include "modules/LoRaModule.h"
#include "modules/BuzzerModule.h"
#include "modules/LEDModule.h"
#include "modules/TelemetryModule.h"
#include "modules/FilesystemModule.h"

//==============================================================================
// OBJETOS GLOBAIS (estaticos, sem heap)
//==============================================================================

static TwoWire i2c_bus = Wire;
static BME280Sensor g_bme;
static ICM20602Sensor g_icm;
static GPSSensor g_gps;
static BuzzerModule g_buzzer;
static LEDModule g_led;
static TelemetryModule g_telemetry;
static VerticalVelocity g_vz_filter(0.4f);
static DataValidation g_validator(ValidationConfig{VALID_MAX_ACCEL, VALID_MIN_PRESSURE, VALID_MAX_PRESSURE, VALID_MAX_VZ});
static FilesystemModule g_fs;

//==============================================================================
// ESTADO
//==============================================================================

static uint32_t g_last_sample = 0;
static uint32_t g_last_debug_print = 0;
static bool g_bme_ok = false;
static bool g_icm_ok = false;
static bool g_lora_ok = false;
static uint32_t g_lora_failures = 0;
static uint32_t g_fs_failures = 0;

//==============================================================================
// SETUP
//==============================================================================

/**
 * @brief Inicializacao unica do sistema
 *
 * Sequencia:
 * 1. Serial para debug
 * 2. I2C para sensores
 * 3. Buzzer/LED para feedback
 * 4. BME280 (temperatura, pressao, umidade)
 * 5. ICM-20602 (acelerometro, giroscopio)
 * 6. GPS (posicao, tempo)
 * 7. LoRa (telemetria)
 * 8. Watchdog
 */
void setup() {
    // --- Serial ---
    Serial.begin(SERIAL_BAUD);
    unsigned long serialStart = millis();
    while (!Serial && (millis() - serialStart < 2000)) { ; }
    Serial.println();
    Serial.println(F("========================================"));
    Serial.print(F("  "));
    Serial.print(MISSION_NAME);
    Serial.print(F("  TEAM "));
    Serial.println(TEAM_ID);
    Serial.println(F("  LASC 2026"));
    Serial.println(F("========================================"));
    Serial.println();

    // --- I2C ---
    i2c_bus.begin(I2C_SDA, I2C_SCL);
    i2c_bus.setClock(400000); // 400kHz Fast Mode
    Serial.println(F("[I2C] Bus initialized (SDA=8, SCL=9, 400kHz)"));

    // --- Buzzer & LED ---
    g_buzzer.begin();
    g_led.begin();
    Serial.println(F("[ACT] Buzzer & LED initialized"));

    // --- BME280 ---
    g_bme_ok = g_bme.begin(i2c_bus, BME280_ADDR);
    if (g_bme_ok) {
        Serial.println(F("[BME] BME280 OK"));
    } else {
        Serial.println(F("[BME] ERROR: BME280 not found!"));
    }

    // --- ICM-20602 ---
    g_icm_ok = g_icm.begin(ICM20602_ADDR, i2c_bus);
    if (g_icm_ok) {
        Serial.println(F("[ICM] ICM-20602 OK"));
    } else {
        Serial.println(F("[ICM] ERROR: ICM-20602 not found!"));
    }

    // --- GPS ---
    g_gps.begin();
    Serial.println(F("[GPS] NEO-8M initialized (9600 baud)"));

    // --- LoRa ---
    g_lora_ok = g_telemetry.begin();
    if (g_lora_ok) {
        Serial.println(F("[LORA] RFM95W OK (915MHz)"));
    } else {
        Serial.println(F("[LORA] ERROR: RFM95W not found!"));
    }

    // --- Storage (SD primario, LittleFS fallback) ---
    if (g_fs.begin()) {
        String csv_header = "TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi";
        g_fs.createFile("/telemetry.csv", csv_header);
        Serial.print(F("[FS] Storage: "));
        Serial.println(g_fs.getTypeString());
    } else {
        Serial.println(F("[FS] ERRO: Nenhum storage disponivel!"));
    }

    // --- Status final ---
    Serial.println();
    Serial.println(F("--- Initialization Summary ---"));
    Serial.print(F("  BME280:    ")); Serial.println(g_bme_ok ? F("OK") : F("FAIL"));
    Serial.print(F("  ICM-20602: ")); Serial.println(g_icm_ok ? F("OK") : F("FAIL"));
    Serial.print(F("  GPS:       ")); Serial.println(F("ACTIVE"));
    Serial.print(F("  LoRa:      ")); Serial.println(g_lora_ok ? F("OK") : F("FAIL"));
    Serial.println();

    // --- Feedback sonoro/visual ---
    if (g_bme_ok && g_icm_ok) {
        g_buzzer.playStartup();
        g_led.blink(3, 300);
    } else {
        g_buzzer.playError();
        g_led.blinkFast(10);
    }

    // --- Watchdog (ESP32-C3 TWDT) ---
    esp_task_wdt_init(WATCHDOG_TIMEOUT_MS * 1000, true);
    esp_task_wdt_add(NULL); // Subscribe current task

    // --- Inicializa timestamps ---
    g_last_sample = millis();
    g_last_debug_print = millis();

    Serial.println(F("[SYS] Setup complete. Starting main loop..."));
    Serial.println();
}

//==============================================================================
// LOOP
//==============================================================================

/**
 * @brief Loop principal — leitura e transmissao de telemetria
 *
 * A cada SAMPLE_INTERVAL_MS:
 * 1. Le GPS (sempre, para manter parser atualizado)
 * 2. Atualiza IMU
 * 3. Coleta dados BME280
 * 4. Valida dados
 * 5. Calcula Vz
 * 6. Monta pacote CSV
 * 7. Transmite Serial + LoRa
 * 8. Toggle LED (heartbeat)
 * 9. Feed watchdog
 */
void loop() {
    unsigned long now = millis();

    // --- GPS update (sempre, para manter parser fresco) ---
    g_gps.update();

    // --- Loop principal no intervalo de amostragem ---
    if (now - g_last_sample < SAMPLE_INTERVAL_MS) {
        return;
    }
    // --- Feed watchdog ---
    esp_task_wdt_reset();

    // --- Atualiza IMU ---
    if (g_icm_ok) {
        g_icm.update();
    }

    // --- Coleta dados ---
    SensorData data;
    g_telemetry.collectData(g_bme, g_icm, g_gps, data);

    // --- Valida dados ---
    bool valid = g_validator.isValid(data);

    // --- Calcula Vz (pular primeiro sample — filtro sem historico) ---
    static bool g_first_sample = true;
    if (valid && !isnan(data.altura)) {
        if (g_first_sample) {
            g_first_sample = false;
            data.vz = NAN;
        } else {
            data.vz = g_vz_filter.update(data.altura, now);
        }
    } else {
        data.vz = NAN;
    }

    // --- Calcula magnitude giroscopia ---
    if (valid) {
        data.mag_giroscopia = sqrtf(data.gx * data.gx + data.gy * data.gy + data.gz * data.gz);
    } else {
        data.mag_giroscopia = NAN;
    }

    // --- Monta pacote CSV ---
    char packetBuf[160];
    g_telemetry.formatPacket(data, packetBuf, sizeof(packetBuf));
    String packet(packetBuf);

    // --- Transmite ---
    if (!g_telemetry.send(packet)) {
        g_lora_failures++;
        Serial.println(F("[LORA] ERROR: send() failed"));
    }

    // --- Grava em LittleFS (se ativo) ---
    if (!g_fs.appendLine(packet)) {
        g_fs_failures++;
        Serial.println(F("[FS] ERROR: appendLine() failed"));
    }

    // --- Heartbeat LED ---
    g_led.toggle();

    // --- Debug periodico ---
    if (DEBUG_ENABLED && (now - g_last_debug_print >= DEBUG_PRINT_INTERVAL_MS)) {
        g_last_debug_print = now;
        unsigned long loop_duration = now - g_last_sample;
        Serial.print(F("[DEBUG] Packet #"));
        Serial.print(g_telemetry.getPacketCount());
        Serial.print(F(" | BME:"));
        Serial.print(g_bme_ok ? F("ok") : F("--"));
        Serial.print(F(" ICM:"));
        Serial.print(g_icm_ok ? F("ok") : F("--"));
        Serial.print(F(" LoRa:"));
        Serial.print(g_lora_ok ? F("ok") : F("--"));
        Serial.print(F(" GPS sats:"));
        Serial.print(g_gps.getSatellites());
        Serial.print(F(" | Vz:"));
        Serial.print(data.vz);
        Serial.print(F(" | loop:"));
        Serial.print(loop_duration);
        Serial.print(F("ms | LoRa fails:"));
        Serial.print(g_lora_failures);
        Serial.print(F(" FS fails:"));
        Serial.print(g_fs_failures);
        Serial.println();
    }
    g_last_sample = now;
}
