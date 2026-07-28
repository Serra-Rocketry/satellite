/**
 * @file BuzzerModule.cpp
 * @brief Active buzzer implementation (digital on/off, no PWM needed)
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
        digitalWrite(BUZZER_PIN, HIGH);
        delay(SHORT_MS);
        digitalWrite(BUZZER_PIN, LOW);
        delay(PAUSE_MS);
    }
}

void BuzzerModule::playError() {
    for (int i = 0; i < 5; i++) {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(SHORT_MS);
        digitalWrite(BUZZER_PIN, LOW);
        delay(40);
    }
}

void BuzzerModule::playBeep() {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(SHORT_MS);
    digitalWrite(BUZZER_PIN, LOW);
    delay(PAUSE_MS);
}

void BuzzerModule::playContinuous(uint16_t duration_ms) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration_ms);
    digitalWrite(BUZZER_PIN, LOW);
}

void BuzzerModule::stop() {
    digitalWrite(BUZZER_PIN, LOW);
}
