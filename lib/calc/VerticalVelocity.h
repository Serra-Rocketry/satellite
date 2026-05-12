#pragma once

#include <math.h>

/**
 * @class VerticalVelocity
 * @brief Cálculo de velocidade vertical (Vz) por diferenciação numérica com EMA
 *
 * Converte diferenças de altitude/tempo em velocidade vertical,
 * aplicando filtro exponencial móvel (EMA) para suavização.
 *
 * Uso:
 * @code
 * VerticalVelocity vz(0.5f);
 * float v = vz.update(altura_atual, millis());
 * @endcode
 */
class VerticalVelocity {
public:
  /**
   * @param alpha Fator de suavização EMA (0.0 = máxima suavização, 1.0 = sem filtro)
   */
  VerticalVelocity(float alpha = 0.5f) : _alpha(alpha), _alt_prev(0), _vz_prev(0), _vz_filt(0), _ts_prev(0) {}

  /** @brief Reseta o estado interno (altitude anterior, filtro, timestamp) */
  void reset() {
    _alt_prev = 0;
    _vz_prev = 0;
    _vz_filt = 0;
    _ts_prev = 0;
  }

  /**
   * @brief Atualiza o cálculo com nova leitura
   * @param altura Altitude atual em metros
   * @param millis_ts Timestamp da leitura em ms
   * @return Vz filtrada em m/s (positivo = subindo)
   *
   * @note Na primeira chamada retorna 0 (inicializa o estado interno)
   * @note Se dt=0 retorna o valor anterior (proteção contra divisão por zero)
   */
  float update(float altura, unsigned long millis_ts) {
    if (_ts_prev == 0) {
      _ts_prev = millis_ts;
      _alt_prev = altura;
      return 0.0f;
    }

    unsigned long dt_ms = millis_ts - _ts_prev;
    if (dt_ms == 0) return _vz_prev;

    float dt_s = dt_ms / 1000.0f;
    float vz_raw = (altura - _alt_prev) / dt_s;

    _vz_filt = _alpha * _vz_filt + (1.0f - _alpha) * vz_raw;

    _ts_prev = millis_ts;
    _alt_prev = altura;
    _vz_prev = _vz_filt;

    return _vz_filt;
  }

  /** @brief Valor atual do filtro EMA */
  float current() const { return _vz_filt; }

  /** @brief Último valor retornado por update() */
  float previous() const { return _vz_prev; }

private:
  float _alpha;
  float _alt_prev;
  float _vz_prev;
  float _vz_filt;
  unsigned long _ts_prev;
};
