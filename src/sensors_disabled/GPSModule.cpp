#include "GPSModule.h"

GPSModule::GPSModule(HardwareSerial &serialPort, uint32_t baud = 9600)
  : _serial(serialPort), _baud(baud), _ready(false) {}

bool GPSModule::begin() {
  _serial.begin(_baud);
  // Wait a bit for serial to stabilize? Not strictly necessary.
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
  return _gps.altitude.meters(); // Returns meters
}

float GPSModule::getSpeed() {
  if (!_ready) return NAN;
  return _gps.speed.kmh(); // km/h
}

uint8_t GPSModule::getSatellites() {
  if (!_ready) return 255;
  return _gps.satellites.value();
}

uint8_t GPSModule::getFixQuality() {
  if (!_ready) return 255;
  // TinyGPSPlus doesn't directly give fix quality; we can infer from satellites > 4 or HDOP
  // For simplicity, return 1 if location is valid, else 0
  return _gps.location.isValid() ? 1 : 0;
}

bool GPSModule::hasFix() {
  if (!_ready) return false;
  return _gps.location.isValid() && _gps.satellites.value() >= 4;
}

bool GPSModule::isReady() {
  return _ready;
}
