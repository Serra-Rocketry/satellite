/**
 * @file config.h
 * @brief Configuracao global do satellite Helike PocketQube (#213 - LASC 2026)
 *
 * CONTEXTO CRITICO: O satellite fica COMPLETAMENTE DESLIGADO (sem energia)
 * ate o deploy do foguete no apogeu. Ao receber energia, o sistema ja esta
 * em descida. Nao ha modo sleep, nao ha deteccao de liftoff.
 *
 * Objetivo do sistema:
 * 1. Ao ligar, inicializar sensores e LoRa o mais rapido possivel
 * 2. Ler sensores e transmitir telemetria continuamente
 * 3. Sem FSM, sem filesystem, sem complexidade desnecessaria
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

//==============================================================================
// IDENTIFICACAO
//==============================================================================

#define TEAM_ID             "#213"
#define MISSION_NAME        "Helike PocketQube"

//==============================================================================
// PINOUT (ESP32-C3 Super Mini)
//==============================================================================

// I2C
#define I2C_SDA             8
#define I2C_SCL             9

// LoRa SPI (RFM95W)
#define LORA_MOSI           7
#define LORA_MISO           5
#define LORA_SCK            6
#define LORA_CS             10
#define LORA_RST            4
#define LORA_DIO0           3

// GPS UART (NEO-8M)
#define GPS_RX              20
#define GPS_TX              21

// Atuadores
#define LED_PIN             1
#define BUZZER_PIN          0
#define BUTTON_PIN          2

//==============================================================================
// TIMING
//==============================================================================

#define SERIAL_BAUD         115200
#define GPS_BAUD            9600

// Intervalo de amostragem (ms) — 200ms = 5Hz
#define SAMPLE_INTERVAL_MS  200

// Intervalo de transmissao LoRa (ms) — mesmo do sample
#define LORA_INTERVAL_MS    200

// Intervalo de leitura GPS (ms)
#define GPS_READ_INTERVAL_MS 1000

// Intervalo de print debug na Serial (ms)
#define DEBUG_PRINT_INTERVAL_MS 2000

//==============================================================================
// LORA
//==============================================================================

#define LORA_FREQ           915E6           // Americas (Brasil)
#define LORA_SYNC_WORD      0xF3
#define LORA_TX_POWER       20              // dBm maximo
#define LORA_SPREADING      7               // SF7
#define LORA_BANDWIDTH      125E3           // 125kHz

//==============================================================================
// SENSORES
//==============================================================================

// BME280
#define BME280_ADDR         0x76
#define BME280_SEALEVEL_HPA 1013.25f

// ICM-20602
#define ICM20602_ADDR       0x68
#define ACCEL_SCALE         16.0f           // ±16g
#define GYRO_SCALE           2000.0f         // ±2000°/s

// Validacao de dados
#define VALID_MAX_ACCEL     (20.0f * 9.80665f)  // ±20g maximo
#define VALID_MIN_PRESSURE  30000.0f            // Pa
#define VALID_MAX_PRESSURE  120000.0f           // Pa
#define VALID_MAX_VZ        200.0f              // m/s

//==============================================================================
// WATCHDOG
//==============================================================================

#define WATCHDOG_TIMEOUT_MS 5000            // 5 segundos

//==============================================================================
// DEBUG
//==============================================================================

#define DEBUG_ENABLED      1
#define LORA_DEBUG_LOGS     0

// LittleFS: habilitar para logging em flash (test hardware / bancada)
// Em voo real, desabilitar para economizar energia/flash wear
#define USE_LITTLEFS       1

#endif // CONFIG_H
