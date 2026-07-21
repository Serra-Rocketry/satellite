/**
 * @file LEDModule.h
 * @brief Visual feedback module via LED indicator
 *
 * Controls the system status LED indicator.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef LED_MODULE_H
#define LED_MODULE_H

#include <Arduino.h>
#include "config.h"

/**
 * @class LEDModule
 * @brief LED control for visual feedback
 */
class LEDModule {
public:
    LEDModule();

    /**
     * @brief Initializes the LED pin
     */
    void begin();

    /**
     * @brief Turns LED on
     */
    void on();

    /**
     * @brief Turns LED off
     */
    void off();

    /**
     * @brief Blinks LED N times with interval
     * @param times Number of blinks
     * @param interval_ms Interval between blinks (ms)
     */
    void blink(uint8_t times, uint16_t interval_ms = 200);

    /**
     * @brief Fast blink (50ms interval)
     * @param times Number of blinks
     */
    void blinkFast(uint8_t times);

    /**
     * @brief Toggles LED state
     */
    void toggle();

private:
    bool _state;
};

#endif // LED_MODULE_H
