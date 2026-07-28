/**
 * @file bmp280.ino
 * @brief Hardware validation sketch for the BMP280 sensor (I2C)
 *
 * Tests the BMP280 barometric sensor reading temperature (C),
 * pressure (Pa), and approximate altitude (m).
 *
 * Adapted from Adafruit BMP280 library example.
 * Original by Limor Fried & Kevin Townsend for Adafruit Industries.
 *
 * Hardware setup:
 * - I2C: SDA=GPIO8, SCL=GPIO9
 * - Address: 0x76
 * - Library: Adafruit_BMP280
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BMP280.h>


Adafruit_BMP280 bmp; // I2C

void setup() {
  Serial.begin(115200);
  while ( !Serial ) delay(100);   // wait for native usb
  Serial.println(F("BMP280 test"));
  unsigned status;
  //status = bmp.begin(BMP280_ADDRESS_ALT, BMP280_CHIPID);
  status = bmp.begin(0x76);
  if (!status) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring or "
                      "try a different address!"));
    Serial.print("SensorID was: 0x"); Serial.println(bmp.sensorID(),16);
    Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
    Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
    Serial.print("        ID of 0x60 represents a BME 280.\n");
    Serial.print("        ID of 0x61 represents a BME 680.\n");
    while (1) delay(10);
  }

  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */
}

void loop() {
    Serial.print(F("Temperature = "));
    Serial.print(bmp.readTemperature());
    Serial.println(" *C");

    Serial.print(F("Pressure = "));
    Serial.print(bmp.readPressure());
    Serial.println(" Pa");

    Serial.print(F("Approx altitude = "));
    Serial.print(bmp.readAltitude(1013.25)); /* Adjusted to local forecast! */
    Serial.println(" m");

    Serial.println();
    delay(2000);
}

