/**
 * @file GPSModule.cpp
 * @brief Legacy GPS module implementation (DISABLED from build)
 *
 * @deprecated Replaced by src/sensors/GPSSensor.cpp which implements the
 *             ISensor interface. Kept for reference only.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include "GPSModule.h"

GPSModule::GPSModule(HardwareSerial &serialPort, uint32_t baud)
  : _serial(serialPort), _baud(baud), _ready(false) {}

bool GPSModule::begin() {
  _serial.begin(_baud);
  _ready = true;
  return true;
}

void GPSModule::update() {
  if (!_ready) return;
  while (_serial.available()) {
    char c = _serial.read();
    _gps.encode(c);
  }
}

float GPSModule::getLatitude() {
  if (!_ready) return NAN;
  return _gps.location.lat();
}

float GPSModule::getLongitude() {
  if (!_ready) return NAN;
  return _gps.location.lng();
}

float GPSModule::getAltitude() {
  if (!_ready) return NAN;
  return _gps.altitude.meters();
}

float GPSModule::getSpeed() {
  if (!_ready) return NAN;
  return _gps.speed.kmh();
}

uint8_t GPSModule::getSatellites() {
  if (!_ready) return 255;
  return _gps.satellites.value();
}

uint8_t GPSModule::getFixQuality() {
  if (!_ready) return 255;
  return _gps.location.isValid() ? 1 : 0;
}

bool GPSModule::hasFix() {
  if (!_ready) return false;
  return _gps.location.isValid() && _gps.satellites.value() >= 4;
}

bool GPSModule::isReady() {
  return _ready;
}
