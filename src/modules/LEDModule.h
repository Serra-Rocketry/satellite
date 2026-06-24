/**
 * @file LEDModule.h
 * @brief Modulo de feedback visual via LED
 *
 * Controla o LED indicador de estado do sistema.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef LED_MODULE_H
#define LED_MODULE_H

#include <Arduino.h>
#include "config.h"

/**
 * @class LEDModule
 * @brief Controle do LED para feedback visual
 */
class LEDModule {
public:
    LEDModule();

    /**
     * @brief Inicializa o pino do LED
     */
    void begin();

    /**
     * @brief Liga LED
     */
    void on();

    /**
     * @brief Desliga LED
     */
    void off();

    /**
     * @brief Pisca LED N vezes com intervalo
     * @param times Numero de piscadas
     * @param interval_ms Intervalo entre piscadas (ms)
     */
    void blink(uint8_t times, uint16_t interval_ms = 200);

    /**
     * @brief Pisca LED rapido (intervalo 50ms)
     * @param times Numero de piscadas
     */
    void blinkFast(uint8_t times);

    /**
     * @brief Alterna estado do LED
     */
    void toggle();

private:
    bool _state;
};

#endif // LED_MODULE_H
