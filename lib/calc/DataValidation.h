/**
 * @file DataValidation.h
 * @brief Telemetry data validation against physical limits and NaN
 *
 * Checks each field of SensorData against:
 * - NaN (not-a-number) values
 * - Physical operating ranges (acceleration, pressure, Vz)
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef DATA_VALIDATION_H
#define DATA_VALIDATION_H

#include <math.h>
#include "SensorData.h"

/**
 * @struct ValidationConfig
 * @brief Configurable limits for sensor data validation
 */
struct ValidationConfig {
  float max_accel_ms2;    ///< Maximum acceleration in m/s^2
  float min_pressure_pa;  ///< Minimum pressure in Pa
  float max_pressure_pa;  ///< Maximum pressure in Pa
  float max_vz_ms;        ///< Maximum |Vz| in m/s

  /** @brief Default configuration for ±16g */
  static ValidationConfig defaultConfig() {
    return {
      .max_accel_ms2   = 16.0f * 9.80665f,
      .min_pressure_pa = 30000.0f,
      .max_pressure_pa = 120000.0f,
      .max_vz_ms       = 100.0f,
    };
  }

  /** @brief More permissive configuration for ±50g */
  static ValidationConfig liberalConfig() {
    return {
      .max_accel_ms2   = 50.0f * 9.80665f,
      .min_pressure_pa = 300.0f,
      .max_pressure_pa = 120000.0f,
      .max_vz_ms       = 100.0f,
    };
  }
};

/**
 * @class DataValidation
 * @brief Telemetry data validation against physical limits and NaN
 *
 * Checks each field of SensorData against:
 * - NaN (not-a-number) values
 * - Physical operating ranges (acceleration, pressure, Vz)
 *
 * Usage:
 * @code
 * DataValidation dv;
 * if (!dv.isValid(data)) {
 *   Serial.println("Invalid data, skipping...");
 *   return;
 * }
 * @endcode
 */
class DataValidation {
public:
  /**
   * @param cfg Limits configuration (defaultConfig or liberalConfig)
   */
  DataValidation(ValidationConfig cfg = ValidationConfig::defaultConfig())
    : _cfg(cfg) {}

  /**
   * @brief Validates a complete sensor reading
   * @param d Sensor data to validate
   * @return true if all fields are within limits
   *
   * @note Checks NaN on ax, ay, az, pressure, altitude, vz
   * @note Checks acceleration magnitude against max_accel_ms2
   * @note Checks pressure against [min_pressure_pa, max_pressure_pa]
   * @note Checks |Vz| against max_vz_ms
   */
  bool isValid(const SensorData& d) const {
    if (isnan(d.ax) || isnan(d.ay) || isnan(d.az)) return false;
    if (isnan(d.pressao) || isnan(d.altura))        return false;
    if (isnan(d.vz))                                return false;

    float a_mag = sqrtf(d.ax*d.ax + d.ay*d.ay + d.az*d.az);
    if (a_mag > _cfg.max_accel_ms2) return false;

    if (d.pressao < _cfg.min_pressure_pa || d.pressao > _cfg.max_pressure_pa) return false;
    if (fabsf(d.vz) > _cfg.max_vz_ms) return false;

    return true;
  }

  /** @return Current limits configuration */
  const ValidationConfig& config() const { return _cfg; }

private:
  ValidationConfig _cfg;
};

#endif // DATA_VALIDATION_H
