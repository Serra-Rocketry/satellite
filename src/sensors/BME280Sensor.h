/**
 * @file BME280Sensor.h
 * @brief Driver for BME280 (primary) with BMP280 fallback
 *
 * Tries Adafruit_BME280 first; if not found, falls back to
 * Adafruit_BMP280 (pressure/temperature only — humidity = NAN).
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef BME280_SENSOR_H
#define BME280_SENSOR_H

#include <Arduino.h>
#include <Adafruit_BME280.h>
#include <Adafruit_BMP280.h>
#include "config.h"
#include "ISensor.h"

class BME280Sensor : public ISensor {
public:
    BME280Sensor(float seaLevelPressure = BME280_SEALEVEL_HPA);

    bool begin() override { return _ready; }
    void update() override {}
    bool isReady() const override { return _ready; }
    bool hasNewData() const override { return _hasNewData; }
    void markDataRead() override { _hasNewData = false; }

    /** Try BME280 first, fallback to BMP280 */
    bool begin(TwoWire &wire, uint8_t addr = BME280_ADDR);

    float getTemperature();
    float getPressure();
    /** Returns NAN when using BMP280 fallback (no humidity sensor) */
    float getHumidity();
    float getAltitude();
    void setSeaLevelPressure(float pressure);
    float getSeaLevelPressure();

private:
    Adafruit_BME280 _bme;
    Adafruit_BMP280 _bmp;
    bool _useBME;       // true = BME280, false = BMP280 fallback
    bool _ready;
    bool _hasNewData;
    float _seaLevelPressure;
};

#endif // BME280_SENSOR_H
