/**
 * @file VerticalVelocity.h
 * @brief Calculo de velocidade vertical (Vz) por diferenciacao numerica com EMA
 *
 * Converte diferencas de altitude/tempo em velocidade vertical,
 * aplicando filtro exponencial movel (EMA) para suavizacao.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef VERTICAL_VELOCITY_H
#define VERTICAL_VELOCITY_H

#include <math.h>

/**
 * @class VerticalVelocity
 * @brief Calculo de velocidade vertical (Vz) por diferenciacao numerica com EMA
 *
 * Converte diferencas de altitude/tempo em velocidade vertical,
 * aplicando filtro exponencial movel (EMA) para suavizacao.
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
   * @param alpha Fator de suavizacao EMA (0.0 = maxima suavizacao, 1.0 = sem filtro)
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
   * @brief Atualiza o calculo com nova leitura
   * @param altura Altitude atual em metros
   * @param millis_ts Timestamp da leitura em ms
   * @return Vz filtrada em m/s (positivo = subindo)
   *
   * @note Na primeira chamada retorna 0 (inicializa o estado interno)
   * @note Se dt=0 retorna o valor anterior (protecao contra divisao por zero)
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

    _vz_filt = _alpha * vz_raw + (1.0f - _alpha) * _vz_filt;

    _ts_prev = millis_ts;
    _alt_prev = altura;
    _vz_prev = _vz_filt;

    return _vz_filt;
  }

  /** @brief Valor atual do filtro EMA */
  float current() const { return _vz_filt; }

  /** @brief Ultimo valor retornado por update() */
  float previous() const { return _vz_prev; }

private:
  float _alpha;
  float _alt_prev;
  float _vz_prev;
  float _vz_filt;
  unsigned long _ts_prev;
};

#endif // VERTICAL_VELOCITY_H
