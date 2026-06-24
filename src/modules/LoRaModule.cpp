/**
 * @file LoRaModule.cpp
 * @brief Implementacao do modulo LoRa RFM95W
 */

#include "LoRaModule.h"

LoRaModule::LoRaModule() : _ready(false) {
}

bool LoRaModule::begin() {
    LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);

    if (!LoRa.begin(LORA_FREQ)) {
        return false;
    }

    // Configurar parametros LoRa (funcoes retornam void, sem checagem direta)
    LoRa.setSyncWord(LORA_SYNC_WORD);
    LoRa.setTxPower(LORA_TX_POWER);
    LoRa.setSpreadingFactor(LORA_SPREADING);
    LoRa.setSignalBandwidth(LORA_BANDWIDTH);
    LoRa.enableCrc();

    _ready = true;
    return true;
}

bool LoRaModule::send(const String &message) {
    if (!_ready) return false;

    bool success = true;
    LoRa.beginPacket();
    LoRa.print(message);

    if (LoRa.endPacket() != 0) {
        success = false;
    }

    return success;
}
