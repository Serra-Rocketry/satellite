/**
 * @file test_validation.cpp
 * @brief Testes unitarios para DataValidation
 */

#include "unity.h"
#include "calc/DataValidation.h"
#include "calc/SensorData.h"

static SensorData makeData(float ax, float ay, float az,
                           float pressao, float altura, float vz) {
    SensorData d;
    d.millis_ts = 0;
    d.ax = ax;
    d.ay = ay;
    d.az = az;
    d.gx = 0;
    d.gy = 0;
    d.gz = 0;
    d.pressao = pressao;
    d.temperatura = 25.0f;
    d.umidade = 50.0f;
    d.altura = altura;
    d.vz = vz;
    d.mag_giroscopia = 0;
    d.lat = 0;
    d.lon = 0;
    d.altura_gps = 0;
    d.satellites = 7;
    return d;
}

void test_valid_data_passes(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 101325, 100, 0);
    TEST_ASSERT_TRUE(dv.isValid(d));
}

void test_nan_accel_fails(void) {
    DataValidation dv;
    auto d = makeData(NAN, 0, 9.81f, 101325, 100, 0);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_nan_pressure_fails(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, NAN, 100, 0);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_nan_altitude_fails(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 101325, NAN, 0);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_nan_vz_fails(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 101325, 100, NAN);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_accel_out_of_range_fails(void) {
    DataValidation dv;
    auto d = makeData(200, 0, 9.81f, 101325, 100, 0);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_pressure_too_low_fails(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 20000, 100, 0);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_pressure_too_high_fails(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 150000, 100, 0);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_vz_out_of_range_fails(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 101325, 100, 150);
    TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_liberal_config_allows_higher_accel(void) {
    DataValidation dv(ValidationConfig::liberalConfig());
    auto d = makeData(400, 0, 9.81f, 101325, 100, 0);
    TEST_ASSERT_TRUE(dv.isValid(d));
}

void test_negative_vz_within_range_passes(void) {
    DataValidation dv;
    auto d = makeData(0, 0, 9.81f, 101325, 100, -50);
    TEST_ASSERT_TRUE(dv.isValid(d));
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(test_valid_data_passes);
    RUN_TEST(test_nan_accel_fails);
    RUN_TEST(test_nan_pressure_fails);
    RUN_TEST(test_nan_altitude_fails);
    RUN_TEST(test_nan_vz_fails);
    RUN_TEST(test_accel_out_of_range_fails);
    RUN_TEST(test_pressure_too_low_fails);
    RUN_TEST(test_pressure_too_high_fails);
    RUN_TEST(test_vz_out_of_range_fails);
    RUN_TEST(test_liberal_config_allows_higher_accel);
    RUN_TEST(test_negative_vz_within_range_passes);
    return UNITY_END();
}
