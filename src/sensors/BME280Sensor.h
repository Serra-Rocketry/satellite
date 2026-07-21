/**
 * @file BME280Sensor.h
 * @brief Driver for the BME280 sensor (temperature, pressure, humidity)
 *
 * I2C communication. Provides temperature (C), pressure (Pa),
 * humidity (%) and altitude (m) calculated via the barometric formula.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef BME280_SENSOR_H
#define BME280_SENSOR_H

#include <Arduino.h>
#include <Adafruit_BME280.h>
#include "config.h"
#include "ISensor.h"

/**
 * @class BME280Sensor
 * @brief Abstraction for the BME280 barometric sensor
 */
class BME280Sensor : public ISensor {
public:
    /**
     * @brief Constructor
     * @param seaLevelPressure Sea level pressure reference (hPa)
     */
    BME280Sensor(float seaLevelPressure = BME280_SEALEVEL_HPA);

    ///@name ISensor interface
    ///@{
    /**
     * @brief Returns the current initialization state
     *
     * This begin() overload does NOT physically initialize the sensor.
     * It only returns the _ready flag, which is set to true after
     * the explicit begin(TwoWire&, uint8_t) call.
     *
     * @return true if the sensor was already initialized via begin(TwoWire&, uint8_t)
     */
    bool begin() override { return _ready; }
    void update() override {}
    bool isReady() const override { return _ready; }
    bool hasNewData() const override { return _hasNewData; }
    void markDataRead() override { _hasNewData = false; }
    ///@}

    /**
     * @brief Initializes the I2C sensor
     * @param wire I2C bus
     * @param addr I2C address of the sensor (0x76 or 0x77)
     * @return true if initialized successfully
     */
    bool begin(TwoWire &wire, uint8_t addr = BME280_ADDR);

    /**
     * @brief Reads temperature in Celsius
     * @return Temperature or NAN on error
     */
    float getTemperature();

    /**
     * @brief Reads pressure in Pa
     * @return Pressure or NAN on error
     */
    float getPressure();

    /**
     * @brief Reads humidity in %
     * @return Humidity or NAN on error
     */
    float getHumidity();

    /**
     * @brief Calculates altitude in meters (relative to sea level)
     * @return Altitude or NAN on error
     */
    float getAltitude();

    /**
     * @brief Sets the sea level pressure reference for altitude
     * @param pressure Pressure in hPa
     */
    void setSeaLevelPressure(float pressure);

    /**
     * @brief Returns the reference sea level pressure (hPa)
     */
    float getSeaLevelPressure();

private:
    Adafruit_BME280 _bme;
    bool _ready;
    bool _hasNewData;
    float _seaLevelPressure;
};

#endif // BME280_SENSOR_H
