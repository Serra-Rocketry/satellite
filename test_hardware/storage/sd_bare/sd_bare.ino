/**
 * @file sd_bare.ino
 * @brief SD card bare read/write test
 *
 * Tests basic SD card read/write operations with incremental
 * file naming (Dados_001.csv, Dados_002.csv, ...).
 *
 * Hardware setup (ESP32-C3 Super Mini):
 * - CS: GPIO5
 * - MOSI: GPIO6 (shared with LoRa SPI)
 * - MISO: GPIO7 (shared with LoRa SPI)
 * - SCK: GPIO4 (shared with LoRa SPI)
 *
 * Note: SD and LoRa share the same SPI bus with different CS pins
 * (SD=5, LoRa=10).
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include "FS.h"
#include "SD.h"
#include "SPI.h"

#define INTERVAL 200
#define CS_PIN 5      // SD card CS pin

String file_name = "";
String file_dir  = "";

unsigned long previous_millis = 0;

// Gera nome único incrementando índice: /Dados_001.csv, /Dados_002.csv ...
String generateFileName()
{
    for (int i = 1; i <= 999; i++)
    {
        char candidate[32];
        snprintf(candidate, sizeof(candidate), "/Dados_%03d.csv", i);

        if (!SD.exists(candidate))
            return String(candidate);
    }

    return "/Dados_overflow.csv";
}

// Setup do cartão SD
bool setupSD()
{
    if (!SD.begin(CS_PIN))
    {
        Serial.println("Failed to mount SD.");
        return false;
    }
    if (SD.cardType() == CARD_NONE)
    {
        Serial.println("SD card not found.");
        return false;
    }
    return true; // Retorna true se tudo ocorreu bem
}

// Registra e imprime os dados do momento
void logData(unsigned long current_millis)
{
    char data_string[150];
    snprintf(data_string, sizeof(data_string),
         "%lu,-22.286898,-42.542294,8,861.80,2025/5/15,12:6:9,0.36,927.76,0.60,-0.01,9.03,-0.01,-0.02,0.02",
         current_millis);
    appendFile(file_dir, data_string);
}

// Escreve os dados no arquivo - escrita
bool writeFile(const String &path, const String &data_string)
{
    File file = SD.open(path, FILE_WRITE);
    if (!file) // Se houver falha ao abrir o arquivo
    {
        Serial.println("Failed to open file for writing.");
        return false;
    }
    if (file.println(data_string)) // Se a escrita no arquivo for bem-sucedida
    {
        Serial.println("File written.");
    }
    else // Se houver falha na escrita
    {
        Serial.println("Failed to write to file.");
        file.close();
        return false;
    }
    file.close();
    return true; // Retorna true se tudo ocorreu bem
}

// Escreve os dados no arquivo - anexação
bool appendFile(const String &path, const String &message)
{
    File file = SD.open(path, FILE_APPEND);
    if (!file) // Se houver falha ao abrir o arquivo
    {
        Serial.println("Failed to open file for appending.");
        return false;
    }
     bool success = file.print(message + "\n");
    file.close(); // Garante fechamento antes de retornar

    if (success)
        Serial.println("Mensagem anexada.");
    else
        Serial.println("Failed to append message.");

    return success;
}

void setup()
{
    Serial.begin(115200);
    delay(1000); // Aguarda a inicialização do Serial
    Serial.println("Iniciando...");

    if (!setupSD()) {
        Serial.println("Failed to init SD card!");
        delay(3000);
        ESP.restart();
    }

    file_name = generateFileName();
    file_dir = file_name;
    Serial.print("Saving data to: ");
    Serial.println(file_dir);
 
    String data_header = "millis,lat,lon,sat,alt,data,hora,altp,p,ax,ay,az,gx,gy,gz";

    // Só escreve o cabeçalho se o arquivo ainda não existir
    bool file_exists = SD.exists(file_dir);

    if (!file_exists && !writeFile(file_dir, data_header))
    {
        Serial.println("Failed to create data file!");
        delay(3000);
        ESP.restart();
    }
}

void loop()
{
    unsigned long current_millis = millis();
    if (current_millis - previous_millis >= INTERVAL) // A cada 200ms
    {
        logData(current_millis);
        previous_millis = current_millis;
    }
}
