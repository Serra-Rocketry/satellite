#include <unity.h>
#include "calc/VerticalVelocity.h"

void setUp(void) {}
void tearDown(void) {}

void test_vz_zero_when_stationary(void) {
  VerticalVelocity vz;
  float result = vz.update(100.0f, 1000);
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, result);
}

void test_vz_positive_when_ascending(void) {
  VerticalVelocity vz;
  vz.update(100.0f, 1000);
  float result = vz.update(101.0f, 1200);
  TEST_ASSERT_TRUE(result > 0.0f);
}

void test_vz_negative_when_descending(void) {
  VerticalVelocity vz;
  vz.update(100.0f, 1000);
  float result = vz.update(99.0f, 1200);
  TEST_ASSERT_TRUE(result < 0.0f);
}

void test_vz_approximates_5ms_up(void) {
  VerticalVelocity vz(0.5f);
  vz.update(100.0f, 1000);

  float result = 0;
  for (int i = 0; i < 10; i++) {
    result = vz.update(100.0f + 5.0f * (i + 1) * 0.05f, 1000 + (i + 1) * 50);
  }

  TEST_ASSERT_FLOAT_WITHIN(1.0f, 5.0f, result);
}

void test_vz_approximates_10ms_down(void) {
  VerticalVelocity vz(0.5f);
  vz.update(200.0f, 1000);

  float result = 0;
  for (int i = 0; i < 10; i++) {
    result = vz.update(200.0f - 10.0f * (i + 1) * 0.05f, 1000 + (i + 1) * 50);
  }

  TEST_ASSERT_FLOAT_WITHIN(1.0f, -10.0f, result);
}

void test_vz_reset_clears_state(void) {
  VerticalVelocity vz;
  vz.update(100.0f, 1000);
  vz.update(101.0f, 1200);

  vz.reset();

  float result = vz.update(100.0f, 2000);
  TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, result);
}

void test_vz_returns_previous_on_zero_dt(void) {
  VerticalVelocity vz;
  vz.update(100.0f, 1000);
  float first = vz.update(101.0f, 1200);
  float second = vz.update(102.0f, 1200);
  TEST_ASSERT_EQUAL_FLOAT(first, second);
}

int main(int argc, char** argv) {
  UNITY_BEGIN();

  RUN_TEST(test_vz_zero_when_stationary);
  RUN_TEST(test_vz_positive_when_ascending);
  RUN_TEST(test_vz_negative_when_descending);
  RUN_TEST(test_vz_approximates_5ms_up);
  RUN_TEST(test_vz_approximates_10ms_down);
  RUN_TEST(test_vz_reset_clears_state);
  RUN_TEST(test_vz_returns_previous_on_zero_dt);

  return UNITY_END();
}
