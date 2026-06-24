/**
 * @file ApogeeDetection.h
 * @brief Deteccao automatica de apogeu por threshold de velocidade vertical
 *
 * Monitora a velocidade vertical e detecta o apogeu quando Vz cruza
 * o threshold negativo (transicao subida -> descida). Mantem registro
 * da altitude maxima atingida e da velocidade maxima de descida.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef APOGEE_DETECTION_H
#define APOGEE_DETECTION_H

/**
 * @struct ApogeeEvent
 * @brief Resultado da deteccao de apogeu
 */
struct ApogeeEvent {
  bool detected;              ///< Apogeu foi detectado? (Vz cruzou threshold negativo)
  unsigned long timestamp_ms; ///< Timestamp da deteccao em ms
  float altitude_max;         ///< Altitude maxima registrada durante a subida (pico)
  float velocidade_max_descida; ///< Maior |Vz| registrada durante a descida
};

/**
 * @class ApogeeDetection
 * @brief Deteccao automatica de apogeu por threshold de velocidade vertical
 *
 * Monitora a velocidade vertical e detecta o apogeu quando Vz cruza
 * o threshold negativo (transicao subida -> descida). Mantem registro
 * da altitude maxima atingida e da velocidade maxima de descida.
 *
 * Uso:
 * @code
 * ApogeeDetection ad(-0.5f);
 *
 * void loop() {
 *   float vz = ...;
 *   if (ad.update(vz, millis(), altitude)) {
 *     Serial.println("Apogeu detectado!");
 *   }
 * }
 * @endcode
 */
class ApogeeDetection {
public:
  /**
   * @param vz_threshold Threshold de Vz (m/s) para considerar descida
   *        Valores tipicos: -0.5 (liberal) a -2.0 (conservador)
   */
  ApogeeDetection(float vz_threshold = -0.5f)
    : _threshold(vz_threshold), _descending(false), _altitude_peak(-1e6f),
      _event{false, 0, 0.0f, 0.0f} {}

  /** @brief Reseta deteccao e eventos */
  void reset() {
    _descending = false;
    _altitude_peak = -1e6f;
    _event = {false, 0, 0.0f, 0.0f};
  }

  /**
   * @brief Atualiza deteccao com nova leitura
   * @param vz Velocidade vertical atual (m/s)
   * @param millis_ts Timestamp da leitura (ms)
   * @param altitude Altitude atual (m)
   * @return true se apogeu foi detectado nesta chamada (transicao)
   *
   * @note Retorna true apenas uma vez (primeira deteccao)
   * @note A altitude maxima e rastreada continuamente durante a subida
   */
  bool update(float vz, unsigned long millis_ts, float altitude) {
    if (altitude > _altitude_peak) {
      _altitude_peak = altitude;
    }

    if (!_descending && vz < _threshold) {
      _descending = true;

      if (!_event.detected) {
        _event.detected = true;
        _event.timestamp_ms = millis_ts;
        _event.altitude_max = _altitude_peak;
        return true;
      }
    }

    if (_descending && vz < _event.velocidade_max_descida) {
      _event.velocidade_max_descida = vz;
    }

    return false;
  }

  /** @return true se esta em fase de descida */
  bool isDescending() const { return _descending; }

  /** @return Referencia const para o evento de apogeu */
  const ApogeeEvent& event() const { return _event; }

private:
  float _threshold;
  bool _descending;
  float _altitude_peak;
  ApogeeEvent _event;
};

#endif // APOGEE_DETECTION_H
