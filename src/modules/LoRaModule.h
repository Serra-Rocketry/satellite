/**
 * @file LoRaModule.h
 * @brief Modulo de comunicacao LoRa com RFM95W
 *
 * Comunicacao SPI. Envia pacotes de telemetria via radio LoRa
 * na frequencia configurada (915MHz Americas).
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef LORA_MODULE_H
#define LORA_MODULE_H

#include <Arduino.h>
#include <LoRa.h>
#include "config.h"

/**
 * @class LoRaModule
 * @brief Controle do radio LoRa RFM95W
 */
class LoRaModule {
public:
    LoRaModule();

    /**
     * @brief Inicializa LoRa com pinos e frequencia configurados
     * @return true se inicializado com sucesso
     */
    bool begin();

    /**
     * @brief Envia mensagem via LoRa
     * @param message String a transmitir
     * @return true se transmitiu com sucesso
     */
    bool send(const String &message);

    /**
     * @brief Verifica se modulo esta operacional
     */
    bool isReady() const { return _ready; }

private:
    bool _ready;
};

#endif // LORA_MODULE_H
