/**
 * @file ICM20602Sensor.h
 * @brief Driver para sensor inercial ICM-20602 (acelerometro + giroscopio)
 *
 * Comunicacao I2C. Fornece aceleracao (m/s^2) e velocidade angular (rad/s)
 * com ranges configurados para ±16g e ±2000°/s.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef ICM20602_SENSOR_H
#define ICM20602_SENSOR_H

#include <Arduino.h>
#include <Wire.h>
#include "ISensor.h"

/**
 * @class ICM20602Sensor
 * @brief Abstracao para o sensor inercial ICM-20602
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
     * @brief Inicializa o sensor I2C
     * @param addr Endereco I2C (0x68 ou 0x69)
     * @param wire Barramento I2C
     * @return true se inicializado com sucesso
     */
    bool begin(uint8_t addr = 0x69, TwoWire &wire = Wire);

    /**
     * @brief Aceleracao em X (m/s^2)
     */
    float getAx() const;

    /**
     * @brief Aceleracao em Y (m/s^2)
     */
    float getAy() const;

    /**
     * @brief Aceleracao em Z (m/s^2)
     */
    float getAz() const;

    /**
     * @brief Velocidade angular em X (rad/s)
     */
    float getGx() const;

    /**
     * @brief Velocidade angular em Y (rad/s)
     */
    float getGy() const;

    /**
     * @brief Velocidade angular em Z (rad/s)
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

    // Conversion factors para ±16g (AFS_SEL=3) e ±2000°/s (FS_SEL=3)
    // ±16g: 2048 LSB/g -> 16.0 * 9.80665 / 32768.0 m/s² per LSB
    // ±2000°/s: 16.384 LSB/°/s -> pi / (180 * 16.384) rad/s per LSB
    static constexpr float ACCEL_FACTOR = 16.0f * 9.80665f / 32768.0f;
    static constexpr float GYRO_FACTOR = 3.14159265359f / (180.0f * 16.384f);

    void wakeUp();
    bool testConnection();
};

#endif // ICM20602_SENSOR_H
