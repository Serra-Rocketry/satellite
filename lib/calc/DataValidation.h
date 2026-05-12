#pragma once

#include <math.h>
#include "SensorData.h"

/**
 * @struct ValidationConfig
 * @brief Limites configuráveis para validação de dados dos sensores
 */
struct ValidationConfig {
  float max_accel_ms2;    ///< Aceleração máxima em m/s²
  float min_pressure_pa;  ///< Pressão mínima em Pa
  float max_pressure_pa;  ///< Pressão máxima em Pa
  float max_vz_ms;        ///< |Vz| máxima em m/s

  /** @brief Configuração padrão para ±16g */
  static ValidationConfig defaultConfig() {
    return {
      .max_accel_ms2   = 16.0f * 9.80665f,
      .min_pressure_pa = 30000.0f,
      .max_pressure_pa = 120000.0f,
      .max_vz_ms       = 100.0f,
    };
  }

  /** @brief Configuração mais permissiva para ±50g */
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
 * @brief Validação de telemetria contra limites físicos e NaN
 *
 * Verifica cada campo da struct SensorData contra:
 * - Valores NaN (not-a-number)
 * - Faixas físicas de operação (aceleração, pressão, Vz)
 *
 * Uso:
 * @code
 * DataValidation dv;
 * if (!dv.isValid(data)) {
 *   Serial.println("Dado inválido, ignorando...");
 *   return;
 * }
 * @endcode
 */
class DataValidation {
public:
  /**
   * @param cfg Configuração de limites (defaultConfig ou liberalConfig)
   */
  DataValidation(ValidationConfig cfg = ValidationConfig::defaultConfig())
    : _cfg(cfg) {}

  /**
   * @brief Valida uma leitura completa dos sensores
   * @param d Dados do sensor a validar
   * @return true se todos os campos estão dentro dos limites
   *
   * @note Verifica NaN em ax, ay, az, pressao, altura, vz
   * @note Verifica magnitude da aceleração contra max_accel_ms2
   * @note Verifica pressão contra [min_pressure_pa, max_pressure_pa]
   * @note Verifica |Vz| contra max_vz_ms
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

  /** @return Configuração atual de limites */
  const ValidationConfig& config() const { return _cfg; }

private:
  ValidationConfig _cfg;
};
