/**
 * @file BuzzerModule.cpp
 * @brief Implementacao do modulo buzzer
 */

#include "BuzzerModule.h"

BuzzerModule::BuzzerModule() {
}

void BuzzerModule::begin() {
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
}

void BuzzerModule::playStartup() {
    for (int i = 0; i < 3; i++) {
        tone(BUZZER_PIN, FREQUENCY, SHORT_MS);
        delay(SHORT_MS + PAUSE_MS);
    }
}

void BuzzerModule::playError() {
    for (int i = 0; i < 5; i++) {
        tone(BUZZER_PIN, FREQUENCY, SHORT_MS);
        delay(SHORT_MS + 40);
    }
}

void BuzzerModule::playBeep() {
    tone(BUZZER_PIN, FREQUENCY, SHORT_MS);
    delay(SHORT_MS + PAUSE_MS);
}

void BuzzerModule::playContinuous(uint16_t duration_ms) {
    tone(BUZZER_PIN, FREQUENCY, duration_ms);
    delay(duration_ms);
}

void BuzzerModule::stop() {
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
}
