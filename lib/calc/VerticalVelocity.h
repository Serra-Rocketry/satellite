/**
 * @file VerticalVelocity.h
 * @brief Vertical velocity (Vz) computation via numerical differentiation with EMA
 *
 * Converts altitude/time differences into vertical velocity using
 * an Exponential Moving Average (EMA) filter for smoothing.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef VERTICAL_VELOCITY_H
#define VERTICAL_VELOCITY_H

#include <math.h>

/**
 * @class VerticalVelocity
 * @brief Vertical velocity (Vz) computation via numerical differentiation with EMA
 *
 * Converts altitude/time differences into vertical velocity using
 * an Exponential Moving Average (EMA) filter for smoothing.
 *
 * Usage:
 * @code
 * VerticalVelocity vz(0.5f);
 * float v = vz.update(current_altitude, millis());
 * @endcode
 */
class VerticalVelocity {
public:
  /**
   * @param alpha EMA smoothing factor (0.0 = maximum smoothing, 1.0 = no filter)
   */
  VerticalVelocity(float alpha = 0.5f) : _alpha(alpha), _alt_prev(0), _vz_prev(0), _vz_filt(0), _ts_prev(0) {}

  /** @brief Resets internal state (previous altitude, filter, timestamp) */
  void reset() {
    _alt_prev = 0;
    _vz_prev = 0;
    _vz_filt = 0;
    _ts_prev = 0;
  }

  /**
   * @brief Updates the calculation with a new reading
   * @param altitude Current altitude in meters
   * @param millis_ts Reading timestamp in ms
   * @return Filtered Vz in m/s (positive = ascending)
   *
   * @note Returns 0 on first call (initializes internal state)
   * @note Returns previous value if dt=0 (division-by-zero protection)
   */
  float update(float altitude, unsigned long millis_ts) {
    if (_ts_prev == 0) {
      _ts_prev = millis_ts;
      _alt_prev = altitude;
      return 0.0f;
    }

    unsigned long dt_ms = millis_ts - _ts_prev;
    if (dt_ms == 0) return _vz_prev;

    float dt_s = dt_ms / 1000.0f;
    float vz_raw = (altitude - _alt_prev) / dt_s;

    _vz_filt = _alpha * vz_raw + (1.0f - _alpha) * _vz_filt;

    _ts_prev = millis_ts;
    _alt_prev = altitude;
    _vz_prev = _vz_filt;

    return _vz_filt;
  }

  /** @brief Current EMA filter value */
  float current() const { return _vz_filt; }

  /** @brief Last value returned by update() */
  float previous() const { return _vz_prev; }

private:
  float _alpha;
  float _alt_prev;
  float _vz_prev;
  float _vz_filt;
  unsigned long _ts_prev;
};

#endif // VERTICAL_VELOCITY_H
