/**
 * @file FilesystemModule.cpp
 * @brief Implementation: SD primary, LittleFS fallback
 */

#include "FilesystemModule.h"
#include <SD.h>
#include <LittleFS.h>

FilesystemModule::FilesystemModule(uint8_t sd_cs_pin)
    : _type(STORAGE_NONE), _sd_cs_pin(sd_cs_pin), _lineCount(0) {
}

bool FilesystemModule::begin() {
    // Try SD first
    Serial.println(F("[FS] Tentando SD card..."));
    if (SD.begin(_sd_cs_pin) && SD.cardType() != CARD_NONE) {
        _type = STORAGE_SD;
        Serial.print(F("[FS] SD OK ("));
        Serial.print(SD.cardSize() * 512ULL / 1024 / 1024);
        Serial.println(F(" MB)"));
        return true;
    }

    Serial.println(F("[FS] SD nao disponivel. Tentando LittleFS..."));

    // Fallback to LittleFS
    if (LittleFS.begin(true)) {
        _type = STORAGE_LITTLEFS;
        Serial.print(F("[FS] LittleFS OK ("));
        Serial.print(LittleFS.totalBytes() / 1024);
        Serial.println(F(" KB total)"));
        return true;
    }

    Serial.println(F("[FS] ERRO: Nenhum storage disponivel!"));
    return false;
}

bool FilesystemModule::createFile(const String &path, const String &header) {
    if (_type == STORAGE_NONE) return false;

    File file;
    if (_type == STORAGE_SD) {
        file = SD.open(path.c_str(), FILE_WRITE);
    } else {
        file = LittleFS.open(path.c_str(), FILE_WRITE);
    }

    if (!file) {
        Serial.print(F("[FS] Falha ao abrir: "));
        Serial.println(path);
        return false;
    }

    file.println(header);
    file.close();

    _filename = path;
    _lineCount = 0;
    Serial.print(F("[FS] Arquivo criado: "));
    Serial.println(path);
    return true;
}

bool FilesystemModule::appendLine(const String &line) {
    if (_type == STORAGE_NONE || _filename.length() == 0) return false;

    File file;
    if (_type == STORAGE_SD) {
        file = SD.open(_filename.c_str(), FILE_APPEND);
    } else {
        file = LittleFS.open(_filename.c_str(), FILE_APPEND);
    }

    if (!file) {
        return false;
    }

    bool ok = file.println(line);
    file.close();

    if (ok) _lineCount++;
    return ok;
}

const char* FilesystemModule::getTypeString() const {
    switch (_type) {
        case STORAGE_SD:      return "SD";
        case STORAGE_LITTLEFS: return "LittleFS";
        default:              return "NONE";
    }
}

void FilesystemModule::close() {
    if (_type == STORAGE_SD) {
        SD.end();
    } else if (_type == STORAGE_LITTLEFS) {
        LittleFS.end();
    }
    _type = STORAGE_NONE;
}
