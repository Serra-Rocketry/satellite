/**
 * @file BuzzerModule.h
 * @brief Audio feedback module via active buzzer
 *
 * Active buzzer has a built-in oscillator — just needs DC HIGH/LOW.
 * No PWM / LEDC required.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef BUZZER_MODULE_H
#define BUZZER_MODULE_H

#include <Arduino.h>
#include "config.h"

class BuzzerModule {
public:
    BuzzerModule();

    void begin();

    /** Startup signal (3 short beeps) */
    void playStartup();

    /** Error signal (5 fast beeps) */
    void playError();

    /** Short confirmation beep */
    void playBeep();

    /** Continuous tone (for debugging) */
    void playContinuous(uint16_t duration_ms);

    /** Stops any sound */
    void stop();

private:
    static const uint16_t SHORT_MS = 80;
    static const uint16_t LONG_MS = 300;
    static const uint16_t PAUSE_MS = 80;
};

#endif // BUZZER_MODULE_H
