/**
 * @file BuzzerModule.h
 * @brief Audio feedback module via piezo buzzer
 *
 * Generates beep patterns to indicate system states.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef BUZZER_MODULE_H
#define BUZZER_MODULE_H

#include <Arduino.h>
#include "config.h"

/**
 * @class BuzzerModule
 * @brief Buzzer control for audio feedback
 */
class BuzzerModule {
public:
    BuzzerModule();

    /**
     * @brief Initializes the buzzer pin
     */
    void begin();

    /**
     * @brief Startup signal (3 short beeps)
     */
    void playStartup();

    /**
     * @brief Error signal (5 fast beeps)
     */
    void playError();

    /**
     * @brief Short confirmation beep
     */
    void playBeep();

    /**
     * @brief Continuous tone (for debugging)
     */
    void playContinuous(uint16_t duration_ms);

    /**
     * @brief Stops any sound
     */
    void stop();

private:
    static const uint16_t FREQUENCY = 500;     // Hz
    static const uint16_t SHORT_MS = 80;
    static const uint16_t LONG_MS = 300;
    static const uint16_t PAUSE_MS = 80;
};

#endif // BUZZER_MODULE_H
