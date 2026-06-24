/**
 * @file GPSSensor.h
 * @brief Wrapper para o GPS NEO-8M com TinyGPSPlus
 *
 * Comunicacao Serial1 (UART) a 9600 baud. Fornece tempo, data,
 * coordenadas e numero de satelites.
 *
 * @author #213 Avionics
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
 * @brief Abstracao para o modulo GPS NEO-8M
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
     * @brief Tempo UTC formatado HH:MM:SS
     * @return String com tempo ou "nan" se invalido
     */
    String getTimeString() const;

    /**
     * @brief Data formatada DD/MM/YYYY
     * @return String com data ou "nan" se invalido
     */
    String getDateString() const;

    /**
     * @brief Latitude em graus decimais
     * @return Latitude ou NAN se sem fix
     */
    float getLatitude() const;

    /**
     * @brief Longitude em graus decimais
     * @return Longitude ou NAN se sem fix
     */
    float getLongitude() const;

    /**
     * @brief Altitude GPS em metros (MSL)
     * @return Altitude ou NAN se sem fix
     */
    float getAltitude() const;

    /**
     * @brief Numero de satelites em fix
     * @return Count ou 0 se sem fix
     */
    uint8_t getSatellites() const;

    /**
     * @brief Verifica se tem fix 3D valido
     */
    bool isValid() const;

    /**
     * @brief Verifica se o parser tem dados novos (consome o flag)
     */
    bool isUpdated();

private:
    TinyGPSPlus _gps;
    bool _initialized;
    bool _lastUpdated;
};

#endif // GPS_SENSOR_H
