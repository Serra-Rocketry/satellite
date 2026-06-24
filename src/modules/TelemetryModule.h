/**
 * @file TelemetryModule.h
 * @brief Modulo de formatacao e transmissao de telemetria
 *
 * Monta pacotes CSV com dados dos sensores e envia via Serial e LoRa.
 * Formato: 18 campos (sem hora/data — preenchidos pelo receiver com GPS local).
 *
 * @author #213 Avionics
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
     * @brief Formata dados em linha CSV (18 campos)
     *
     * Monta o pacote CSV no buffer fornecido. Os campos hora/data sao omitidos
     * (preenchidos pelo receiver com GPS local). O campo rssi e placeholder (-1)
     * e substituido pelo receiver com o RSSI real do LoRa.
     *
     * Formato:
     * TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi
     *
     * @param data      Dados estruturados do sensor (SensorData)
     * @param packet    Buffer de saida (char*) para a linha CSV
     * @param packetSize Tamanho do buffer de saida
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
