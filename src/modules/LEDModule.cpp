/**
 * @file LEDModule.cpp
 * @brief LED module implementation
 */

#include "LEDModule.h"

LEDModule::LEDModule() : _state(false) {
}

void LEDModule::begin() {
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
}

void LEDModule::on() {
    digitalWrite(LED_PIN, HIGH);
    _state = true;
}

void LEDModule::off() {
    digitalWrite(LED_PIN, LOW);
    _state = false;
}

void LEDModule::blink(uint8_t times, uint16_t interval_ms) {
    for (uint8_t i = 0; i < times; i++) {
        on();
        delay(interval_ms / 2);
        off();
        delay(interval_ms / 2);
    }
}

void LEDModule::blinkFast(uint8_t times) {
    blink(times, 100);
}

void LEDModule::toggle() {
    if (_state) {
        off();
    } else {
        on();
    }
}
