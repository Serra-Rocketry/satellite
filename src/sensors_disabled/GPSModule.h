/**
 * @file GPSModule.h
 * @brief Legacy GPS module wrapper (DISABLED from build)
 *
 * @deprecated Replaced by src/sensors/GPSSensor.h which implements the
 *             ISensor interface. Kept for reference only.
 *
 * This file is excluded from compilation via build_src_filter in platformio.ini.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef GPS_MODULE_H
#define GPS_MODULE_H

#include <Arduino.h>
#include <HardwareSerial.h>
#include <TinyGPS++.h>

/**
 * @class GPSModule
 * @brief Legacy GPS module (replaced by GPSSensor)
 * @deprecated Use src/sensors/GPSSensor.h instead
 */
class GPSModule {
public:
  GPSModule(HardwareSerial &serialPort, uint32_t baud = 9600);

  bool begin();
  void update();

  float getLatitude() const;    ///< Latitude in decimal degrees
  float getLongitude() const;   ///< Longitude in decimal degrees
  float getAltitude() const;    ///< Altitude in meters
  float getSpeed() const;       ///< Speed in km/h
  uint8_t getSatellites() const; ///< Number of satellites
  uint8_t getFixQuality() const; ///< 0=no fix, 1=GPS, 2=DGPS
  bool hasFix() const;          ///< True if fix quality > 0
  bool isReady() const;         ///< True if serial began successfully

private:
  HardwareSerial& _serial;
  TinyGPSPlus _gps;
  uint32_t _baud;
  bool _ready;
};

#endif // GPS_MODULE_H
