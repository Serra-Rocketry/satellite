/**
 * @file icm20602.ino
 * @brief Hardware validation sketch for the ICM-20602 IMU (I2C)
 *
 * Tests the ICM-20602 6-axis IMU reading accelerometer (m/s^2)
 * and gyroscope (rad/s) data via raw I2C register access.
 *
 * Hardware setup:
 * - I2C: SDA=GPIO8, SCL=GPIO9
 * - Address: 0x69
 *
 * @author Serra Rocketry Team — Mission #213
 * @date 2026
 */

#include <Wire.h>

#define ICM_ADDR 0x69

#if defined(CONFIG_IDF_TARGET_ESP32C3)
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#else
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#endif

void writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ICM_ADDR, 1);
  return Wire.read();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  // Reset
  writeReg(0x6B, 0x80);
  delay(100);

  // Wake up
  writeReg(0x6B, 0x01);

  // Teste WHO_AM_I
  uint8_t who = readReg(0x75);
  Serial.print("WHO_AM_I: 0x");
  Serial.println(who, HEX);
}

int16_t read16(uint8_t reg) {
  Wire.beginTransmission(ICM_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ICM_ADDR, 2);
  return (Wire.read() << 8) | Wire.read();
}

void loop() {
  int16_t ax = read16(0x3B);
  int16_t ay = read16(0x3D);
  int16_t az = read16(0x3F);

  int16_t gx = read16(0x43);
  int16_t gy = read16(0x45);
  int16_t gz = read16(0x47);

  // Conversões
  float ax_ms2 = ax * (9.80665 / 16384.0);
  float ay_ms2 = ay * (9.80665 / 16384.0);
  float az_ms2 = az * (9.80665 / 16384.0);

  float gx_rads = gx * (3.14159265359 / (180.0 * 131.0));
  float gy_rads = gy * (3.14159265359 / (180.0 * 131.0));
  float gz_rads = gz * (3.14159265359 / (180.0 * 131.0));

  Serial.printf("A[m/s²]: %.2f %.2f %.2f | G[rad/s]: %.2f %.2f %.2f\n",
                ax_ms2, ay_ms2, az_ms2,
                gx_rads, gy_rads, gz_rads);

  delay(500);
}
