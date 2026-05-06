// Inclusão de bibliotecas
#include "FS.h"
#include "SD.h"
#include "SPI.h"

// Definições de pinos e constantes
#define INTERVAL 200
#define CS_PIN 5      // Pino do cartão SD

//determinando nome
String file_name = "";
String file_dir  = "";

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
        Serial.println("Erro ao montar SD.");
        return false;
    }
    if (SD.cardType() == CARD_NONE)
    {
        Serial.println("Cartão SD não encontrado.");
        return false;
    }
    return true; // Retorna true se tudo ocorreu bem
}

// Registra e imprime os dados do momento
void logData(unsigned long current_millis)
{
    String data_string = String(current_millis) + ",-22.286898,-42.542294,8,861.80,2025/5/15,12:6:9,0.36,927.76,0.60,-0.01,9.03,-0.01,-0.02,0.02"; // String com os dados atuais
    appendFile(file_dir, data_string);
}

// Escreve os dados no arquivo - escrita
bool writeFile(const String &path, const String &data_string)
{
    File file = SD.open(path, FILE_WRITE);
    if (!file) // Se houver falha ao abrir o arquivo
    {
        Serial.println("Falha ao abrir arquivo para gravação.");
        return false;
    }
    if (file.println(data_string)) // Se a escrita no arquivo for bem-sucedida
    {
        Serial.println("Arquivo escrito.");
    }
    else // Se houver falha na escrita
    {
        Serial.println("Falha na gravação do arquivo.");
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
        Serial.println("Falha ao abrir arquivo para anexar.");
        return false;
    }
     bool success = file.print(message + "\n");
    file.close(); // Garante fechamento antes de retornar

    if (success)
        Serial.println("Mensagem anexada.");
    else
        Serial.println("Falha ao anexar mensagem.");

    return success;
}

void setup()
{
    Serial.begin(115200);
    delay(10000); // Aguarda a inicialização do Serial
    Serial.println("Iniciando...");

    file_dir = "/" + file_name; // Diretório do arquivo de dados
    Serial.print("Salvando dados em: ");
    Serial.println(file_dir);
 
    String data_header = "millis,lat,lon,sat,alt,data,hora,altp,p,ax,ay,az,gx,gy,gz";

    if (!setupSD()) 
    {
        Serial.println("Erro ao iniciar o cartão SD!");
        delay(3000);
        ESP.restart();
    }

    // Só escreve o cabeçalho se o arquivo ainda não existir
    bool file_exists = SD.exists(file_dir);

    if (!file_exists && !writeFile(file_dir, data_header))
    {
        Serial.println("Erro ao criar arquivo de dados!");
        delay(3000);
        ESP.restart();
    }
}

void loop()
{
    unsigned long current_millis = millis();
    if (current_millis - previous_millis >= INTERVAL) // A cada 200ms (vc tinha comentado a cada 100ms mas o intervalo ta 200, não sei oq ta errado o intervalo, o comentario ou teu amigo aqui)
    {
        logData(current_millis);
        previous_millis = current_millis;
    }
}
