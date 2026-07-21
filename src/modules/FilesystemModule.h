/**
 * @file FilesystemModule.h
 * @brief Storage module with SD as primary and LittleFS as fallback
 *
 * Follows the test_hardware pattern:
 * 1. Attempts SD.begin() first
 * 2. If that fails, uses LittleFS.begin() as fallback
 * 3. File operations dispatch automatically based on active type
 *
 * In real flight (no SD card), the system detects absence and uses LittleFS.
 * On the bench (with SD), it writes to SD for easy data retrieval.
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#ifndef FILESYSTEM_MODULE_H
#define FILESYSTEM_MODULE_H

#include <Arduino.h>
#include "config.h"

/**
 * @enum StorageType
 * @brief Active storage type
 */
enum StorageType {
    STORAGE_NONE = 0,       ///< No storage available
    STORAGE_SD,             ///< SD card active
    STORAGE_LITTLEFS        ///< LittleFS active (fallback)
};

/**
 * @class FilesystemModule
 * @brief Manages SD primary with LittleFS fallback
 */
class FilesystemModule {
public:
    FilesystemModule(uint8_t sd_cs_pin = 5);

    /**
     * @brief Initializes storage: SD first, LittleFS as fallback
     * @return true if any storage was initialized
     */
    bool begin();

    /**
     * @brief Creates file with header line
     * @param path File path (e.g. "/telemetry.csv")
     * @param header Header line
     * @return true if created successfully
     */
    bool createFile(const String &path, const String &header);

    /**
     * @brief Appends a line to an existing file
     * @param line CSV line
     * @return true if written successfully
     */
    bool appendLine(const String &line);

    /**
     * @brief Checks if storage is active
     */
    bool isReady() const { return _type != STORAGE_NONE; }

    /**
     * @brief Returns the active storage type
     */
    StorageType getType() const { return _type; }

    /**
     * @brief Returns a descriptive string for the storage type
     */
    const char* getTypeString() const;

    /**
     * @brief Number of lines written
     */
    uint32_t getLineCount() const { return _lineCount; }

    /**
     * @brief Closes files and unmounts
     */
    void close();

private:
    StorageType _type;
    uint8_t _sd_cs_pin;
    String _filename;
    uint32_t _lineCount;
};

#endif // FILESYSTEM_MODULE_H
