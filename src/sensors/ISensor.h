/**
 * @file ISensor.h
 * @brief Abstract interface for all satellite sensors
 *
 * Defines the minimum contract that every sensor must implement:
 * initialization, periodic update, and new data signaling.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef ISENSOR_H
#define ISENSOR_H

#include <Arduino.h>

/**
 * @class ISensor
 * @brief Abstract interface for satellite sensors
 */
class ISensor {
public:
    virtual ~ISensor() {}

    /**
     * @brief Initializes the sensor
     * @return true if initialized successfully
     */
    virtual bool begin() = 0;

    /**
     * @brief Updates sensor readings
     * @note Call periodically in the main loop
     */
    virtual void update() = 0;

    /**
     * @brief Checks if sensor is operational
     */
    virtual bool isReady() const = 0;

    /**
     * @brief Checks if new data is available since last read
     */
    virtual bool hasNewData() const = 0;

    /**
     * @brief Marks data as read/consumed
     */
    virtual void markDataRead() = 0;
};

#endif // ISENSOR_H
