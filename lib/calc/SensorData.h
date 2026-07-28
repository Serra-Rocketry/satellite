/**
 * @file SensorData.h
 * @brief Standardized sensor telemetry data structure
 *
 * Groups all sensor readings from the ICM-20602 IMU, BME280 barometer,
 * and NEO-8M GPS into a single structure for logging, validation,
 * and post-flight analysis.
 *
 * Units:
 * - ax/ay/az: m/s^2 (acceleration)
 * - gx/gy/gz: rad/s (angular velocity)
 * - pressao: Pa (pressure)
 * - temperatura: °C (temperature)
 * - umidade: % (humidity)
 * - altura: m (barometric altitude, relative to ground)
 * - vz: m/s (vertical velocity, positive = ascending)
 * - mag_giroscopia: rad/s (total gyroscope magnitude)
 * - lat/lon: decimal degrees (GPS)
 * - altura_gps: m MSL (GPS altitude)
 * - satellites: number of satellites in fix
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef SENSOR_DATA_H
#define SENSOR_DATA_H

struct SensorData {
  unsigned long millis_ts;
  float ax, ay, az;
  float gx, gy, gz;
  float pressao;
  float temperatura;  // °C
  float umidade;      // %
  float altura;        // barometrica (m)
  float vz;
  float mag_giroscopia;
  float lat;          // GPS latitude (graus)
  float lon;          // GPS longitude (graus)
  float altura_gps;   // GPS altitude (m MSL)
  uint8_t satellites; // numero de satelites
};

#endif // SENSOR_DATA_H
