/**
 * @file BME280Sensor.cpp
 * @brief BME280 sensor with BMP280 fallback implementation
 */

#include "BME280Sensor.h"

BME280Sensor::BME280Sensor(float seaLevelPressure)
    : _seaLevelPressure(seaLevelPressure), _useBME(false), _ready(false), _hasNewData(false) {
}

bool BME280Sensor::begin(TwoWire &wire, uint8_t addr) {
    // Try BME280 first (with humidity)
    if (_bme.begin(addr, &wire)) {
        _useBME = true;
        _ready = true;
        _hasNewData = true;
        return true;
    }

    // Fallback to BMP280 (no humidity) — uses default Wire internally
    if (_bmp.begin(addr)) {
        _bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                         Adafruit_BMP280::SAMPLING_X2,
                         Adafruit_BMP280::SAMPLING_X16,
                         Adafruit_BMP280::FILTER_X16,
                         Adafruit_BMP280::STANDBY_MS_500);
        _useBME = false;
        _ready = true;
        _hasNewData = true;
        return true;
    }

    return false;
}

float BME280Sensor::getTemperature() {
    if (!_ready) return NAN;
    return _useBME ? _bme.readTemperature() : _bmp.readTemperature();
}

float BME280Sensor::getPressure() {
    if (!_ready) return NAN;
    return _useBME ? _bme.readPressure() : _bmp.readPressure();
}

float BME280Sensor::getHumidity() {
    if (!_ready) return NAN;
    if (_useBME) return _bme.readHumidity();
    return NAN;  // BMP280 has no humidity sensor
}

float BME280Sensor::getAltitude() {
    if (!_ready) return NAN;
    return _useBME ? _bme.readAltitude(_seaLevelPressure)
                   : _bmp.readAltitude(_seaLevelPressure);
}

void BME280Sensor::setSeaLevelPressure(float pressure) {
    _seaLevelPressure = pressure;
}

float BME280Sensor::getSeaLevelPressure() {
    return _seaLevelPressure;
}
