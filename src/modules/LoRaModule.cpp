/**
 * @file LoRaModule.cpp
 * @brief RFM95W LoRa module implementation
 */

#include "LoRaModule.h"

LoRaModule::LoRaModule() : _ready(false) {
}

bool LoRaModule::begin() {
    // Compartilha a instancia SPI ja iniciada pelo main (barramento unico
    // com o SD). A lib sandeepmistry chama _spi->begin() sem argumentos,
    // o que reconfiguraria os pinos default da variante e corromperia o
    // barramento compartilhado.
    LoRa.setSPI(SPI);
    LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);

    // Diagnostico: le RegVersion direto antes da lib tentar
    pinMode(LORA_RST, OUTPUT); digitalWrite(LORA_RST, HIGH);
    SPISettings probe(400000, MSBFIRST, SPI_MODE0);
    SPI.beginTransaction(probe);
    digitalWrite(LORA_CS, LOW);
    SPI.transfer(0x42 & 0x7F);
    uint8_t ver = SPI.transfer(0xFF);
    digitalWrite(LORA_CS, HIGH);
    SPI.endTransaction();
    Serial.printf("[LORA] Pre-begin RegVersion: 0x%02X (esperado 0x12)\n", ver);

    if (!LoRa.begin(LORA_FREQ)) {
        return false;
    }

    // Configure LoRa parameters (functions return void, no direct check)
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

    // endPacket() retorna 1 em sucesso (lib sandeepmistry)
    LoRa.beginPacket();
    LoRa.print(message);

    return LoRa.endPacket() == 1;
}
