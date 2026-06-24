/**
 * @file SensorData.h
 * @brief Estrutura padronizada de telemetria dos sensores
 *
 * Agrupa todas as leituras de IMU (ICM-20602), barometro (BME280) e GPS (NEO-8M)
 * em uma unica estrutura para logging, validacao e analise.
 *
 * Unidades:
 * - ax/ay/az: m/s^2
 * - gx/gy/gz: rad/s
 * - pressao: Pa
 * - temperatura: °C
 * - umidade: %
 * - altura: metros (barometrica, relativa ao solo)
 * - vz: m/s (positivo = subindo)
 * - mag_giroscopia: rad/s (magnitude total)
 * - lat/lon: graus decimais (GPS)
 * - altura_gps: metros MSL (GPS)
 * - satellites: numero de satelites em fix
 *
 * @author #213 Avionics
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
