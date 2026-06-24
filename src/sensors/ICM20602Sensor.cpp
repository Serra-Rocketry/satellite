#include "ICM20602Sensor.h"

ICM20602Sensor::ICM20602Sensor()
    : _wire(nullptr), _ready(false), _hasNewData(false),
      _ax(0.0f), _ay(0.0f), _az(0.0f),
      _gx(0.0f), _gy(0.0f), _gz(0.0f) {
}

bool ICM20602Sensor::begin(uint8_t addr, TwoWire &wire) {
  _addr = addr;
  _wire = &wire;

  // Wake up the sensor: clear sleep bit (bit 6) in PWR_MGMT_1 (0x6B)
  _wire->beginTransmission(_addr);
  _wire->write(0x6B);
  _wire->write(0x00); // Wake up, disable sleep
  if (_wire->endTransmission() != 0) {
    return false;
  }

  // Check WHO_AM_I
  if (!testConnection()) {
    return false;
  }

  // Configurar ranges:
  // GYRO_CONFIG (0x1B): FS_SEL = 3 → ±2000°/s (0x18 = 0b00011000)
  _wire->beginTransmission(_addr);
  _wire->write(0x1B);
  _wire->write(0x18);
  if (_wire->endTransmission() != 0) {
    _ready = false;
    return false;
  }

  // ACCEL_CONFIG (0x1C): AFS_SEL = 3 → ±16g (0x18 = 0b00011000)
  _wire->beginTransmission(_addr);
  _wire->write(0x1C);
  _wire->write(0x18);
  if (_wire->endTransmission() != 0) {
    _ready = false;
    return false;
  }

  _ready = true;
  return true;
}

void ICM20602Sensor::update() {
  if (!_ready) return;

  // Ler dados do acelerometro (0x3B a 0x40)
  _wire->beginTransmission(_addr);
  _wire->write(0x3B);
  _wire->endTransmission(false);
  if (_wire->requestFrom(_addr, 6) != 6) {
    return; // Erro I2C: dados indisponiveis
  }
  int16_t ax_raw = (_wire->read() << 8) | _wire->read();
  int16_t ay_raw = (_wire->read() << 8) | _wire->read();
  int16_t az_raw = (_wire->read() << 8) | _wire->read();

  // Ler dados do giroscopio (0x43 a 0x4A)
  _wire->beginTransmission(_addr);
  _wire->write(0x43);
  _wire->endTransmission(false);
  if (_wire->requestFrom(_addr, 6) != 6) {
    return; // Erro I2C: dados indisponiveis
  }
  int16_t gx_raw = (_wire->read() << 8) | _wire->read();
  int16_t gy_raw = (_wire->read() << 8) | _wire->read();
  int16_t gz_raw = (_wire->read() << 8) | _wire->read();

  // Convert to physical units
  _ax = ax_raw * ACCEL_FACTOR;
  _ay = ay_raw * ACCEL_FACTOR;
  _az = az_raw * ACCEL_FACTOR;
  _gx = gx_raw * GYRO_FACTOR;
  _gy = gy_raw * GYRO_FACTOR;
  _gz = gz_raw * GYRO_FACTOR;

  _hasNewData = true;
}

float ICM20602Sensor::getAx() const { return _ax; }
float ICM20602Sensor::getAy() const { return _ay; }
float ICM20602Sensor::getAz() const { return _az; }
float ICM20602Sensor::getGx() const { return _gx; }
float ICM20602Sensor::getGy() const { return _gy; }
float ICM20602Sensor::getGz() const { return _gz; }

void ICM20602Sensor::wakeUp() {
  // Already done in begin()
}

bool ICM20602Sensor::testConnection() {
  _wire->beginTransmission(_addr);
  _wire->write(0x75); // WHO_AM_I
  _wire->endTransmission(false);
  _wire->requestFrom(_addr, 1);
  if (_wire->available() != 1) {
    return false;
  }
  uint8_t who = _wire->read();
  return (who == 0x12); // ICM-20602 returns 0x12
}
