/**
 * @file ApogeeDetection.h
 * @brief Automatic apogee detection via vertical velocity threshold
 *
 * Monitors vertical velocity and detects apogee when Vz crosses
 * a negative threshold (ascent -> descent transition). Tracks
 * peak altitude and maximum descent speed.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef APOGEE_DETECTION_H
#define APOGEE_DETECTION_H

/**
 * @struct ApogeeEvent
 * @brief Result of apogee detection
 */
struct ApogeeEvent {
  bool detected;              ///< Was apogee detected? (Vz crossed negative threshold)
  unsigned long timestamp_ms; ///< Detection timestamp in ms
  float altitude_max;         ///< Maximum altitude recorded during ascent (peak)
  float velocidade_max_descida; ///< Highest |Vz| recorded during descent
};

/**
 * @class ApogeeDetection
 * @brief Automatic apogee detection via vertical velocity threshold
 *
 * Monitors vertical velocity and detects apogee when Vz crosses
 * a negative threshold (ascent -> descent transition). Tracks
 * peak altitude and maximum descent speed.
 *
 * Usage:
 * @code
 * ApogeeDetection ad(-0.5f);
 *
 * void loop() {
 *   float vz = ...;
 *   if (ad.update(vz, millis(), altitude)) {
 *     Serial.println("Apogee detected!");
 *   }
 * }
 * @endcode
 */
class ApogeeDetection {
public:
  /**
   * @param vz_threshold Vz threshold (m/s) to consider descent
   *        Typical values: -0.5 (liberal) to -2.0 (conservative)
   */
  ApogeeDetection(float vz_threshold = -0.5f)
    : _threshold(vz_threshold), _descending(false), _altitude_peak(-1e6f),
      _event{false, 0, 0.0f, 0.0f} {}

  /** @brief Resets detection and events */
  void reset() {
    _descending = false;
    _altitude_peak = -1e6f;
    _event = {false, 0, 0.0f, 0.0f};
  }

  /**
   * @brief Updates detection with a new reading
   * @param vz Current vertical velocity (m/s)
   * @param millis_ts Reading timestamp (ms)
   * @param altitude Current altitude (m)
   * @return true if apogee was detected on this call (transition)
   *
   * @note Returns true only once (first detection)
   * @note Peak altitude is tracked continuously during ascent
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

  /** @return true if currently in descent phase */
  bool isDescending() const { return _descending; }

  /** @return Const reference to the apogee event */
  const ApogeeEvent& event() const { return _event; }

private:
  float _threshold;
  bool _descending;
  float _altitude_peak;
  ApogeeEvent _event;
};

#endif // APOGEE_DETECTION_H
