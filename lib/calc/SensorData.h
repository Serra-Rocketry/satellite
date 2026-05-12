#pragma once

/**
 * @struct SensorData
 * @brief Estrutura padronizada de telemetria dos sensores
 *
 * Agrupa todas as leituras de IMU (ICM-20602) e barômetro (BMP280/BME280)
 * em uma única estrutura para logging, validação e análise.
 *
 * Unidades:
 * - ax/ay/az: m/s²
 * - gx/gy/gz: rad/s
 * - pressao: Pa
 * - altura: metros (relativa ao solo)
 * - vz: m/s (positivo = subindo)
 * - mag_giroscopia: rad/s (magnitude total)
 */
struct SensorData {
  unsigned long millis_ts;
  float ax, ay, az;
  float gx, gy, gz;
  float pressao;
  float altura;
  float vz;
  float mag_giroscopia;
};
