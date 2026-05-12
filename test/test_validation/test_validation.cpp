#include <unity.h>
#include "calc/DataValidation.h"

void setUp(void) {}
void tearDown(void) {}

static SensorData makeData(float ax, float ay, float az,
                           float pressao, float altura, float vz) {
  return {0, ax, ay, az, 0, 0, 0, pressao, altura, vz, 0};
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
  auto d = makeData(0, 0, 200, 101325, 100, 0);
  TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_pressure_too_low_fails(void) {
  DataValidation dv;
  auto d = makeData(0, 0, 9.81f, 100, 100, 0);
  TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_pressure_too_high_fails(void) {
  DataValidation dv;
  auto d = makeData(0, 0, 9.81f, 200000, 100, 0);
  TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_vz_out_of_range_fails(void) {
  DataValidation dv;
  auto d = makeData(0, 0, 9.81f, 101325, 100, 150);
  TEST_ASSERT_FALSE(dv.isValid(d));
}

void test_liberal_config_allows_higher_accel(void) {
  DataValidation dv(ValidationConfig::liberalConfig());
  auto d = makeData(0, 0, 400, 101325, 100, 0);
  TEST_ASSERT_TRUE(dv.isValid(d));
}

void test_negative_vz_within_range_passes(void) {
  DataValidation dv;
  auto d = makeData(0, 0, 9.81f, 101325, 100, -25);
  TEST_ASSERT_TRUE(dv.isValid(d));
}

int main(int argc, char** argv) {
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
