/**
 * @file BME280Sensor.cpp
 * @brief Implementacao do driver BME280
 */

#include "BME280Sensor.h"

BME280Sensor::BME280Sensor(float seaLevelPressure)
    : _seaLevelPressure(seaLevelPressure), _ready(false), _hasNewData(false) {
}

bool BME280Sensor::begin(TwoWire &wire, uint8_t addr) {
    if (!_bme.begin(addr, &wire)) {
        return false;
    }
    _ready = true;
    _hasNewData = true;
    return true;
}

float BME280Sensor::getTemperature() {
    if (!_ready) return NAN;
    _hasNewData = true;
    return _bme.readTemperature();
}

float BME280Sensor::getPressure() {
    if (!_ready) return NAN;
    _hasNewData = true;
    return _bme.readPressure(); // Returns Pa
}

float BME280Sensor::getHumidity() {
    if (!_ready) return NAN;
    _hasNewData = true;
    return _bme.readHumidity();
}

float BME280Sensor::getAltitude() {
    if (!_ready) return NAN;
    float pressure = getPressure();
    // Validar pressao antes de usar na formula (evita propagacao de NAN)
    if (isnan(pressure) || pressure <= 0.0f) {
        return NAN;
    }
    _hasNewData = true;
    float pressure_hpa = pressure / 100.0f;
    return 44330.0f * (1.0f - pow(pressure_hpa / _seaLevelPressure, 0.1903f));
}

void BME280Sensor::setSeaLevelPressure(float pressure) {
    _seaLevelPressure = pressure;
}

float BME280Sensor::getSeaLevelPressure() {
    return _seaLevelPressure;
}
