/**
 * @file TelemetryModule.h
 * @brief Telemetry formatting and transmission module
 *
 * Builds CSV packets from sensor data and transmits via Serial and LoRa.
 * Format: 18 fields (no time/date — filled by the receiver with local GPS).
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef TELEMETRY_MODULE_H
#define TELEMETRY_MODULE_H

#include <Arduino.h>
#include "config.h"
#include "calc/SensorData.h"
#include "sensors/BME280Sensor.h"
#include "sensors/ICM20602Sensor.h"
#include "sensors/GPSSensor.h"
#include "modules/LoRaModule.h"

class TelemetryModule {
public:
    TelemetryModule();

    bool begin();

    void collectData(BME280Sensor &bme, ICM20602Sensor &icm, GPSSensor &gps, SensorData &data);

    /**
     * @brief Formats sensor data into a CSV line (18 fields)
     *
     * Builds the CSV packet in the provided buffer. Time/date fields are omitted
     * (filled by the receiver with local GPS). The rssi field is a placeholder (-1)
     * replaced by the receiver with the actual LoRa RSSI.
     *
     * Format:
     * TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi
     *
     * @param data      Structured sensor data (SensorData)
     * @param packet    Output buffer (char*) for the CSV line
     * @param packetSize Size of the output buffer
     *
     * @return void
     */
    void formatPacket(const SensorData &data, char *packet, size_t packetSize);

    bool send(const String &packet);

    uint32_t getPacketCount() const { return _packetCount; }

private:
    LoRaModule _lora;
    uint32_t _packetCount;
};

#endif // TELEMETRY_MODULE_H
