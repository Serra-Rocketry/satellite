/**
 * @file BuzzerModule.cpp
 * @brief Buzzer module implementation using LEDC directly
 *
 * Uses ledcWrite instead of tone() to avoid the ESP32-C3 LEDC init bug.
 */

#include "BuzzerModule.h"

BuzzerModule::BuzzerModule() {
}

void BuzzerModule::begin() {
    ledcSetup(BUZZER_LEDC_CHANNEL, FREQUENCY, BUZZER_LEDC_RES);
    ledcAttachPin(BUZZER_PIN, BUZZER_LEDC_CHANNEL);
    ledcWrite(BUZZER_LEDC_CHANNEL, 0);
}

void BuzzerModule::playStartup() {
    for (int i = 0; i < 3; i++) {
        ledcWrite(BUZZER_LEDC_CHANNEL, 128);  // 50% duty
        delay(SHORT_MS);
        ledcWrite(BUZZER_LEDC_CHANNEL, 0);
        delay(PAUSE_MS);
    }
}

void BuzzerModule::playError() {
    for (int i = 0; i < 5; i++) {
        ledcWrite(BUZZER_LEDC_CHANNEL, 128);
        delay(SHORT_MS);
        ledcWrite(BUZZER_LEDC_CHANNEL, 0);
        delay(40);
    }
}

void BuzzerModule::playBeep() {
    ledcWrite(BUZZER_LEDC_CHANNEL, 128);
    delay(SHORT_MS);
    ledcWrite(BUZZER_LEDC_CHANNEL, 0);
    delay(PAUSE_MS);
}

void BuzzerModule::playContinuous(uint16_t duration_ms) {
    ledcWrite(BUZZER_LEDC_CHANNEL, 128);
    delay(duration_ms);
    ledcWrite(BUZZER_LEDC_CHANNEL, 0);
}

void BuzzerModule::stop() {
    ledcWrite(BUZZER_LEDC_CHANNEL, 0);
    ledcDetachPin(BUZZER_PIN);
}
