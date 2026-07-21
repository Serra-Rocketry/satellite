#ifndef I2C_HELPER_H
#define I2C_HELPER_H

#include <Arduino.h>
#include "config.h"

/**
 * @brief Recovers a stuck I2C bus by toggling the SCL line.
 * This is a common fix for sensors that leave the SDA line low.
 */
inline void resetI2C() {
    pinMode(I2C_SDA, INPUT_PULLUP);
    pinMode(I2C_SCL, OUTPUT);

    for (int i = 0; i < 9; i++) {
        digitalWrite(I2C_SCL, HIGH);
        delayMicroseconds(5);
        digitalWrite(I2C_SCL, LOW);
        delayMicroseconds(5);
    }

    pinMode(I2C_SCL, INPUT_PULLUP);
}

#endif // I2C_HELPER_H
