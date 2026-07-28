/**
 * @file GPSSensor.h
 * @brief GPS NEO-8M wrapper with TinyGPSPlus parser
 *
 * Serial1 (UART) communication at 9600 baud. Provides time, date,
 * coordinates, altitude, and satellite count.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef GPS_SENSOR_H
#define GPS_SENSOR_H

#include <Arduino.h>
#include <TinyGPS++.h>
#include "config.h"
#include "ISensor.h"

/**
 * @class GPSSensor
 * @brief Abstraction for the NEO-8M GPS module
 */
class GPSSensor : public ISensor {
public:
    GPSSensor();

    ///@name ISensor interface
    ///@{
    bool begin() override;
    void update() override;
    bool isReady() const override;
    bool hasNewData() const override;
    void markDataRead() override;
    ///@}

    /**
     * @brief UTC time formatted as HH:MM:SS
     * @return Time string or "nan" if invalid
     */
    String getTimeString() const;

    /**
     * @brief Date formatted as DD/MM/YYYY
     * @return Date string or "nan" if invalid
     */
    String getDateString() const;

    /**
     * @brief Latitude in decimal degrees
     * @return Latitude or NAN if no fix
     */
    float getLatitude() const;

    /**
     * @brief Longitude in decimal degrees
     * @return Longitude or NAN if no fix
     */
    float getLongitude() const;

    /**
     * @brief GPS altitude in meters (MSL)
     * @return Altitude or NAN if no fix
     */
    float getAltitude() const;

    /**
     * @brief Number of satellites in fix
     * @return Count or 0 if no fix
     */
    uint8_t getSatellites() const;

    /**
     * @brief Checks if valid 3D fix is available
     */
    bool isValid() const;

    /**
     * @brief Checks if parser has new data (consumes the flag)
     */
    bool isUpdated();

private:
    TinyGPSPlus _gps;
    bool _initialized;
    bool _lastUpdated;
};

#endif // GPS_SENSOR_H
