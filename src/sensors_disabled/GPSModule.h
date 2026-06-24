#ifndef GPS_MODULE_H
#define GPS_MODULE_H

#include <Arduino.h>
#include <HardwareSerial.h>
#include <TinyGPS++.h>

class GPSModule {
public:
  GPSModule(HardwareSerial &serialPort, uint32_t baud = 9600);

  bool begin();
  void update();

  float getLatitude() const;    // degrees
  float getLongitude() const;   // degrees
  float getAltitude() const;    // meters
  float getSpeed() const;       // km/h
  uint8_t getSatellites() const; // number
  uint8_t getFixQuality() const; // 0=no fix, 1=GPS, 2=DGPS
  bool hasFix() const;          // true if fix quality > 0
  bool isReady() const;         // true if serial began successfully

private:
  HardwareSerial& _serial;
  TinyGPSPlus _gps;
  uint32_t _baud;
  bool _ready;
};

#endif // GPS_MODULE_H
