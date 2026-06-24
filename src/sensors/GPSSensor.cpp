/**
 * @file GPSSensor.cpp
 * @brief Implementacao do wrapper GPS NEO-8M
 */

#include "GPSSensor.h"

GPSSensor::GPSSensor()
    : _initialized(false), _lastUpdated(false) {
}

bool GPSSensor::begin() {
    Serial1.begin(GPS_BAUD, SERIAL_8N1, GPS_RX, GPS_TX);
    _initialized = true;
    return true;
}

void GPSSensor::update() {
    if (!_initialized) return;

    while (Serial1.available() > 0) {
        if (_gps.encode(Serial1.read())) {
            _lastUpdated = true;
        }
    }
}

String GPSSensor::getTimeString() const {
    if (!_gps.time.isValid()) {
        return "nan";
    }
    char buf[12];
    TinyGPSTime &t = const_cast<TinyGPSTime&>(_gps.time);
    snprintf(buf, sizeof(buf), "%02d:%02d:%02d",
             t.hour(), t.minute(), t.second());
    return String(buf);
}

String GPSSensor::getDateString() const {
    if (!_gps.date.isValid()) {
        return "nan";
    }
    char buf[12];
    TinyGPSDate &d = const_cast<TinyGPSDate&>(_gps.date);
    snprintf(buf, sizeof(buf), "%02d/%02d/%04d",
             d.day(), d.month(), d.year());
    return String(buf);
}

float GPSSensor::getLatitude() const {
    if (!_gps.location.isValid()) {
        return NAN;
    }
    TinyGPSLocation &loc = const_cast<TinyGPSLocation&>(_gps.location);
    return (float)loc.lat();
}

float GPSSensor::getLongitude() const {
    if (!_gps.location.isValid()) {
        return NAN;
    }
    TinyGPSLocation &loc = const_cast<TinyGPSLocation&>(_gps.location);
    return (float)loc.lng();
}

float GPSSensor::getAltitude() const {
    if (!_gps.altitude.isValid()) {
        return NAN;
    }
    return (float)const_cast<TinyGPSAltitude&>(_gps.altitude).value() / 100.0f;
}

uint8_t GPSSensor::getSatellites() const {
    if (!_gps.satellites.isValid()) {
        return 0;
    }
    return (uint8_t)const_cast<TinyGPSInteger&>(_gps.satellites).value();
}

bool GPSSensor::isValid() const {
    return _gps.location.isValid() && _gps.time.isValid();
}

bool GPSSensor::isReady() const {
    return _initialized;
}

bool GPSSensor::hasNewData() const {
    return _lastUpdated;
}

void GPSSensor::markDataRead() {
    _lastUpdated = false;
}

bool GPSSensor::isUpdated() {
    bool val = _lastUpdated;
    _lastUpdated = false;
    return val;
}
