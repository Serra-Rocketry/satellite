/**
 * @file FilesystemModule.cpp
 * @brief Filesystem management with SD card primary, LittleFS fallback
 *
 * Implements the exact SD-to-LittleFS fallback pattern from sensor_logging_fallback.ino
 * Smart storage strategy: SD card primary, LittleFS secondary for permanent storage
 * Persistent file management across reboots
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include "FilesystemModule.h"
#include <LittleFS.h>
#include <SPI.h>
#include <SD.h>

FilesystemModule::FilesystemModule() {
    // Constructor - no initialization needed, done in begin()
}

bool FilesystemModule::begin() {
    if (_initialized) {
        return isAvailable();
    }

    Serial.println("Initializing storage...");
    _initialized = true;

    // --- SD Card Primary (exact pattern from sensor_logging_fallback.ino) ---
    if (setupSD()) {
        _storage_type = STORAGE_SD;
        Serial.println("SD card available - using as primary storage");
        return true;
    }

    // --- LittleFS Secondary (fallback from sensor_logging_fallback.ino) ---
    if (setupLittleFS()) {
        _storage_type = STORAGE_LITTLEFS;
        Serial.println("SD card unavailable - falling back to LittleFS");
        return true;
    }

    Serial.println("ERROR: No storage available!");
    _storage_type = STORAGE_NONE;
    return false;
}

String FilesystemModule::getTypeString() const {
    switch (_storage_type) {
        case STORAGE_SD:
            return "SD card (persistent file)";
        case STORAGE_LITTLEFS:
            return "LittleFS (persistent file)";
        case STORAGE_NONE:
            return "NONE";
        default:
            return "UNKNOWN";
    }
}

bool FilesystemModule::createFile(const char* path, const String& header) {
    if (!isAvailable() || _storage_type == STORAGE_NONE) {
        return false;
    }

    File file;
    if (_storage_type == STORAGE_SD) {
        file = SD.open(path, FILE_WRITE);
    } else {
        file = LittleFS.open(path, FILE_WRITE);
    }

    if (!file) {
        Serial.println("Failed to open data file.");
        return false;
    }

    file.println(header);
    file.flush();
    file.close();
    return true;
}

bool FilesystemModule::appendLine(const String& packet) {
    if (!isAvailable() || _storage_type == STORAGE_NONE) {
        return false;
    }

    File file;
    if (_storage_type == STORAGE_SD) {
        file = SD.open("/telemetry.csv", FILE_APPEND);
    } else {
        file = LittleFS.open("/telemetry.csv", FILE_APPEND);
    }

    if (!file) {
        Serial.println("Failed to open file for writing.");
        return false;
    }

    file.println(packet);
    file.flush();
    file.close();
    return true;
}

bool FilesystemModule::exists(const char* path) const {
    if (!isAvailable() || _storage_type == STORAGE_NONE) {
        return false;
    }

    if (_storage_type == STORAGE_SD) {
        return SD.exists(path);
    } else {
        return LittleFS.exists(path);
    }
}

// --- Private Implementation ---

bool FilesystemModule::setupSD() {
    Serial.println("Initializing SD...");
    if (SD.begin(SD_CS_PIN) && SD.cardType() != CARD_NONE) {
        Serial.printf("SD OK — type: %s  size: %llu MB\n",
            SD.cardType() == CARD_MMC ? "MMC" :
            SD.cardType() == CARD_SD  ? "SDSC" : "SDHC",
            SD.cardSize() * 512ULL / 1048576ULL);
        return true;
    }
    return false;
}

bool FilesystemModule::setupLittleFS() {
    Serial.println("SD failed. Trying LittleFS...");
    if (LittleFS.begin(true)) {
        Serial.printf("LittleFS OK — %u bytes free\n",
            (unsigned)(LittleFS.totalBytes() - LittleFS.usedBytes()));
        return true;
    }
    Serial.println("LittleFS mount failed.");
    return false;
}
