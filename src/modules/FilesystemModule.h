/**
 * @file FilesystemModule.h
 * @brief Modulo de storage com SD como primario e LittleFS como fallback
 *
 * Segue o padrao do test_hardware:
 * 1. Tenta SD.begin() primeiro
 * 2. Se falhar, usa LittleFS.begin() como fallback
 * 3. Operacoes de arquivo fazem dispatch automatico
 *
 * Em voo real (sem SD card), o sistema detecta ausencia e usa LittleFS.
 * Em bancada (com SD), grava no SD para facilidade de leitura.
 *
 * @author #213 Avionics
 * @date 2026
 */

#ifndef FILESYSTEM_MODULE_H
#define FILESYSTEM_MODULE_H

#include <Arduino.h>
#include "config.h"

/**
 * @enum StorageType
 * @brief Tipo de storage ativo
 */
enum StorageType {
    STORAGE_NONE = 0,       ///< Nenhum storage disponivel
    STORAGE_SD,             ///< SD card ativo
    STORAGE_LITTLEFS        ///< LittleFS ativo (fallback)
};

/**
 * @class FilesystemModule
 * @brief Gerencia SD primario com LittleFS fallback
 */
class FilesystemModule {
public:
    FilesystemModule(uint8_t sd_cs_pin = 5);

    /**
     * @brief Inicializa storage: SD primeiro, LittleFS como fallback
     * @return true se algum storage foi inicializado
     */
    bool begin();

    /**
     * @brief Cria arquivo com header
     * @param path Caminho (ex: "/telemetry.csv")
     * @param header Linha header
     * @return true se criou com sucesso
     */
    bool createFile(const String &path, const String &header);

    /**
     * @brief Append linha a arquivo existente
     * @param line Linha CSV
     * @return true se gravou com sucesso
     */
    bool appendLine(const String &line);

    /**
     * @brief Verifica se ha storage ativo
     */
    bool isReady() const { return _type != STORAGE_NONE; }

    /**
     * @brief Retorna tipo de storage ativo
     */
    StorageType getType() const { return _type; }

    /**
     * @brief Retorna string descritiva do storage
     */
    const char* getTypeString() const;

    /**
     * @brief Numero de linhas gravadas
     */
    uint32_t getLineCount() const { return _lineCount; }

    /**
     * @brief Fecha arquivos e desmonta
     */
    void close();

private:
    StorageType _type;
    uint8_t _sd_cs_pin;
    String _filename;
    uint32_t _lineCount;
};

#endif // FILESYSTEM_MODULE_H
