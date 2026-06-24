/**
 * @file BuzzerModule.h
 * @brief Modulo de feedback sonoro via buzzer piezoeletrico
 *
 * Gera padroes de beeps para indicar estados do sistema.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef BUZZER_MODULE_H
#define BUZZER_MODULE_H

#include <Arduino.h>
#include "config.h"

/**
 * @class BuzzerModule
 * @brief Controle do buzzer para feedback audio
 */
class BuzzerModule {
public:
    BuzzerModule();

    /**
     * @brief Inicializa o pino do buzzer
     */
    void begin();

    /**
     * @brief Sinal de boot (3 beeps curtos)
     */
    void playStartup();

    /**
     * @brief Sinal de erro (5 beeps rapidos)
     */
    void playError();

    /**
     * @brief Beep curto de confirmacao
     */
    void playBeep();

    /**
     * @brief Sinal continuo (para debug)
     */
    void playContinuous(uint16_t duration_ms);

    /**
     * @brief Para qualquer som
     */
    void stop();

private:
    static const uint16_t FREQUENCY = 500;     // Hz
    static const uint16_t SHORT_MS = 80;
    static const uint16_t LONG_MS = 300;
    static const uint16_t PAUSE_MS = 80;
};

#endif // BUZZER_MODULE_H
