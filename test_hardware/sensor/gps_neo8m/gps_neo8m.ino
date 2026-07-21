/**
 * @file gps_neo8m.ino
 * @brief Hardware validation sketch for the NEO-8M GPS module (UART)
 *
 * Tests GPS NMEA parsing with manual checksum validation.
 * Monitors $GPRMC, $GPGGA, and $GPGSA sentences.
 *
 * Hardware setup:
 * - UART: RX=GPIO20, TX=GPIO21
 * - Baud: 9600
 * - Protocol: NMEA 0183
 *
 * Features:
 * - Manual NMEA checksum verification
 * - Coordinate conversion (NMEA ddmm.mmmm -> decimal degrees)
 * - Satellite count, HDOP/VDOP, fix quality/type tracking
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include <HardwareSerial.h>

// Configuração de UART para GPS (Serial1)
#if defined(CONFIG_IDF_TARGET_ESP32C3)
#define GPS_RX_PIN 20
#define GPS_TX_PIN 21
#else
#define GPS_RX_PIN 16
#define GPS_TX_PIN 17
#endif

#define GPS_BAUD_RATE 9600
#define UART_NUM 1

// Estrutura para dados GPS
struct GpsData {
  float latitude;        // graus decimais
  float longitude;       // graus decimais
  float altitude;        // metros acima do nível do mar
  float velocidade;      // km/h
  float curso;           // graus
  uint8_t satellites;    // número de satélites vistos
  uint8_t fix_quality;   // 0=sem fix, 1=GPS fix, 2=DGPS fix
  uint8_t fix_type;      // 1=sem fix, 2=2D, 3=3D
  float hdop;            // diluição horizontal
  float vdop;            // diluição vertical
  bool dados_validos;
};

GpsData gps_data = {0};
String nmea_buffer = "";
unsigned long ultimo_fix_ms = 0;
unsigned long contador_sentencas = 0;
unsigned long contador_erros = 0;

// ============= NMEA Utility Functions =============

// Extrai campo de uma sentença NMEA
String extrair_campo(String sentenca, int indice) {
  int pos = 0;
  int campo = 0;
  int inicio = 0;
  
  for (int i = 0; i < sentenca.length(); i++) {
    if (sentenca[i] == ',') {
      if (campo == indice) {
        return sentenca.substring(inicio, i);
      }
      campo++;
      inicio = i + 1;
    }
  }
  
  // Último campo antes do *
  if (campo == indice) {
    int asterisco = sentenca.indexOf('*');
    if (asterisco > 0) {
      return sentenca.substring(inicio, asterisco);
    } else {
      return sentenca.substring(inicio);
    }
  }
  
  return "";
}

// Calcula checksum XOR de sentença NMEA
uint8_t calcular_checksum_nmea(String sentenca) {
  // Remove $ no início e checksum no final
  int inicio = sentenca.indexOf('$') + 1;
  int asterisco = sentenca.indexOf('*');
  
  uint8_t checksum = 0;
  for (int i = inicio; i < asterisco; i++) {
    checksum ^= sentenca[i];
  }
  return checksum;
}

// Verifica integridade do checksum
bool verificar_checksum_nmea(String sentenca) {
  int asterisco = sentenca.indexOf('*');
  if (asterisco < 0) return false;
  
  String checksum_str = sentenca.substring(asterisco + 1);
  if (checksum_str.length() < 2) return false;
  
  uint8_t checksum_esperado = strtol(checksum_str.c_str(), NULL, 16);
  uint8_t checksum_calculado = calcular_checksum_nmea(sentenca);
  
  return (checksum_esperado == checksum_calculado);
}

// Converte graus NMEA (ddmm.mmmm) para decimais
float converter_coordenada_nmea(String coord_nmea) {
  if (coord_nmea.length() < 5) return 0.0;
  
  // Encontra o ponto decimal
  int ponto = coord_nmea.indexOf('.');
  
  // Graus: tudo antes dos últimos 2 dígitos antes do ponto
  int graus_len = ponto - 2;
  int graus = atoi(coord_nmea.substring(0, graus_len).c_str());
  
  // Minutos: últimos 2 dígitos antes do ponto + decimais
  float minutos = atof(coord_nmea.substring(graus_len).c_str());
  
  return graus + (minutos / 60.0);
}

// ============= NMEA Sentence Processors =============

// Processa sentença $GPRMC (Recommended Minimum Navigation Information)
void processar_rmc(String sentenca) {
  /*
   * Formato: $GPRMC,hhmmss.ss,A,ddmm.mmmm,N/S,dddmm.mmmm,E/W,spd,cog,ddmmyy*hh
   * Campos:
   * 0: $GPRMC
   * 1: UTC time
   * 2: Status (A=active, V=void)
   * 3: Latitude
   * 4: N/S
   * 5: Longitude
   * 6: E/W
   * 7: Speed knots
   * 8: Course
   * 9: Date
   */
  
  String status = extrair_campo(sentenca, 2);
  if (status != "A") {
    gps_data.dados_validos = false;
    return;
  }
  
  String lat_str = extrair_campo(sentenca, 3);
  String lat_dir = extrair_campo(sentenca, 4);
  String lon_str = extrair_campo(sentenca, 5);
  String lon_dir = extrair_campo(sentenca, 6);
  String speed_str = extrair_campo(sentenca, 7);
  String course_str = extrair_campo(sentenca, 8);
  
  gps_data.latitude = converter_coordenada_nmea(lat_str);
  if (lat_dir == "S") gps_data.latitude *= -1;
  
  gps_data.longitude = converter_coordenada_nmea(lon_str);
  if (lon_dir == "W") gps_data.longitude *= -1;
  
  gps_data.velocidade = atof(speed_str.c_str()) * 1.852; // knots → km/h
  gps_data.curso = atof(course_str.c_str());
  
  gps_data.dados_validos = true;
  ultimo_fix_ms = millis();
}

// Processa sentença $GPGGA (Fix Data)
void processar_gga(String sentenca) {
  /*
   * Formato: $GPGGA,hhmmss.ss,ddmm.mmmm,N/S,dddmm.mmmm,E/W,q,xx,hdop,alt,M,geoid,M*hh
   * Campos:
   * 0: $GPGGA
   * 1: UTC time
   * 2: Latitude
   * 3: N/S
   * 4: Longitude
   * 5: E/W
   * 6: Fix quality (0=invalid, 1=GPS fix, 2=DGPS fix)
   * 7: Number of satellites
   * 8: HDOP
   * 9: Altitude
   * 10: Altitude unit (M)
   * 11: Geoid height
   * 12: Geoid height unit (M)
   */
  
  String fix_quality_str = extrair_campo(sentenca, 6);
  String satellites_str = extrair_campo(sentenca, 7);
  String hdop_str = extrair_campo(sentenca, 8);
  String altitude_str = extrair_campo(sentenca, 9);
  
  gps_data.fix_quality = atoi(fix_quality_str.c_str());
  gps_data.satellites = atoi(satellites_str.c_str());
  gps_data.hdop = atof(hdop_str.c_str());
  gps_data.altitude = atof(altitude_str.c_str());
  
  if (gps_data.fix_quality == 0) {
    gps_data.dados_validos = false;
  }
}

// Processa sentença $GPGSA (DOP and Active Satellites)
void processar_gsa(String sentenca) {
  /*
   * Formato: $GPGSA,mode,fixtype,prn1,prn2,...,prn12,pdop,hdop,vdop*hh
   * Campos:
   * 0: $GPGSA
   * 1: Mode (M=manual, A=automatic)
   * 2: Fix type (1=no fix, 2=2D, 3=3D)
   * 3-14: PRNs de satélites
   * 15: PDOP
   * 16: HDOP
   * 17: VDOP
   */
  
  String fix_type_str = extrair_campo(sentenca, 2);
  String vdop_str = extrair_campo(sentenca, 17);
  
  gps_data.fix_type = atoi(fix_type_str.c_str());
  gps_data.vdop = atof(vdop_str.c_str());
}

// Processa sentença NMEA genérica
void processar_nmea(String sentenca) {
  if (!verificar_checksum_nmea(sentenca)) {
    contador_erros++;
    return;
  }
  
  if (sentenca.startsWith("$GPRMC")) {
    processar_rmc(sentenca);
  } else if (sentenca.startsWith("$GPGGA")) {
    processar_gga(sentenca);
  } else if (sentenca.startsWith("$GPGSA")) {
    processar_gsa(sentenca);
  }
  
  contador_sentencas++;
}

// ============= Serial Read =============

void ler_gps() {
  while (Serial1.available()) {
    char ch = Serial1.read();
    
    if (ch == '$') {
      // Novo começo de sentença
      nmea_buffer = "$";
    } else if (ch == '\n' || ch == '\r') {
      // Fim de sentença
      if (nmea_buffer.length() > 0) {
        processar_nmea(nmea_buffer);
      }
      nmea_buffer = "";
    } else {
      // Acumula caracteres
      nmea_buffer += ch;
    }
  }
}

// ============= Setup e Loop =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== Teste GPS NEO-8M ===");
  Serial.print("Initializing GPS UART on pin RX=");
  Serial.print(GPS_RX_PIN);
  Serial.print(" TX=");
  Serial.println(GPS_TX_PIN);
  
  // Inicializa UART para GPS
  Serial1.begin(GPS_BAUD_RATE, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  
  Serial.println(" GPS UART initialized");
  Serial.println("Waiting for NMEA data...\n");
  
  delay(2000);
}

void loop() {
  unsigned long agora = millis();
  
  // Lê dados do GPS
  ler_gps();
  
  // A cada 2 segundos, imprime status
  static unsigned long ultimo_print = 0;
  if (agora - ultimo_print >= 2000) {
    ultimo_print = agora;
    
    Serial.println("--- Status GPS ---");
    Serial.print("Sentencas NMEA recebidas: ");
    Serial.println(contador_sentencas);
    Serial.print("Errors (checksum fail): ");
    Serial.println(contador_erros);
    
    Serial.print("Satellites seen: ");
    Serial.println(gps_data.satellites);
    
    Serial.print("Fix quality: ");
    switch (gps_data.fix_quality) {
      case 0: Serial.println("Sem fix"); break;
      case 1: Serial.println("GPS fix"); break;
      case 2: Serial.println("DGPS fix"); break;
      default: Serial.println("Desconhecido");
    }
    
    Serial.print("Fix type: ");
    switch (gps_data.fix_type) {
      case 1: Serial.println("Sem fix"); break;
      case 2: Serial.println("2D"); break;
      case 3: Serial.println("3D"); break;
      default: Serial.println("Desconhecido");
    }
    
    if (gps_data.dados_validos && gps_data.fix_quality > 0) {
      Serial.print("Latitude:  ");
      Serial.println(gps_data.latitude, 6);
      Serial.print("Longitude: ");
      Serial.println(gps_data.longitude, 6);
      Serial.print("Altitude:  ");
      Serial.print(gps_data.altitude);
      Serial.println(" m");
      Serial.print("Velocidade: ");
      Serial.print(gps_data.velocidade);
      Serial.println(" km/h");
      Serial.print("Curso: ");
      Serial.print(gps_data.curso);
      Serial.println("°");
      Serial.print("HDOP: ");
      Serial.print(gps_data.hdop);
      Serial.print(" | VDOP: ");
      Serial.println(gps_data.vdop);
      
      unsigned long tempo_sem_fix = agora - ultimo_fix_ms;
      Serial.print("Time since last fix: ");
      Serial.print(tempo_sem_fix);
      Serial.println(" ms");
    } else {
      Serial.println("Waiting for GPS fix...");
    }
    
    Serial.println();
  }
}
