/**
 * @file ICM20602Sensor.h
 * @brief Driver for the ICM-20602 inertial sensor (accelerometer + gyroscope)
 *
 * I2C communication. Provides acceleration (m/s^2) and angular velocity (rad/s)
 * with ranges configured for ±16g and ±2000°/s.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef ICM20602_SENSOR_H
#define ICM20602_SENSOR_H

#include <Arduino.h>
#include <Wire.h>
#include "ISensor.h"

/**
 * @class ICM20602Sensor
 * @brief Abstraction for the ICM-20602 inertial sensor
 */
class ICM20602Sensor : public ISensor {
public:
    ICM20602Sensor();

    ///@name ISensor interface
    ///@{
    bool begin() override { return _ready; }
    void update() override;
    bool isReady() const override { return _ready; }
    bool hasNewData() const override { return _hasNewData; }
    void markDataRead() override { _hasNewData = false; }
    ///@}

    /**
     * @brief Initializes the I2C sensor
     * @param addr I2C address (0x68 or 0x69)
     * @param wire I2C bus
     * @return true if initialized successfully
     */
    bool begin(uint8_t addr = 0x69, TwoWire &wire = Wire);

    /**
     * @brief Acceleration X (m/s^2)
     */
    float getAx() const;

    /**
     * @brief Acceleration Y (m/s^2)
     */
    float getAy() const;

    /**
     * @brief Acceleration Z (m/s^2)
     */
    float getAz() const;

    /**
     * @brief Angular velocity X (rad/s)
     */
    float getGx() const;

    /**
     * @brief Angular velocity Y (rad/s)
     */
    float getGy() const;

    /**
     * @brief Angular velocity Z (rad/s)
     */
    float getGz() const;

private:
    uint8_t _addr;
    TwoWire* _wire;
    bool _ready;
    bool _hasNewData;

    // Sensor data
    float _ax;
    float _ay;
    float _az;
    float _gx;
    float _gy;
    float _gz;

    // Conversion factors for ±16g (AFS_SEL=3) and ±2000°/s (FS_SEL=3)
    // ±16g: 2048 LSB/g -> 16.0 * 9.80665 / 32768.0 m/s² per LSB
    // ±2000°/s: 16.384 LSB/°/s -> pi / (180 * 16.384) rad/s per LSB
    static constexpr float ACCEL_FACTOR = 16.0f * 9.80665f / 32768.0f;
    static constexpr float GYRO_FACTOR = 3.14159265359f / (180.0f * 16.384f);

    void wakeUp();
    bool testConnection();
};

#endif // ICM20602_SENSOR_H
