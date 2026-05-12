#include <unity.h>
#include "calc/ApogeeDetection.h"

void setUp(void) {}
void tearDown(void) {}

void test_apogee_not_detected_while_ascending(void) {
  ApogeeDetection ad(-0.5f);

  for (unsigned long t = 1000; t <= 2000; t += 100) {
    bool detected = ad.update(2.0f, t, 100.0f + (t - 1000) * 0.1f);
    TEST_ASSERT_FALSE(detected);
  }

  TEST_ASSERT_FALSE(ad.event().detected);
}

void test_apogee_detected_at_vz_crossing(void) {
  ApogeeDetection ad(-0.5f);

  ad.update(2.0f, 1000, 90.0f);
  ad.update(1.0f, 1100, 95.0f);
  ad.update(0.5f, 1200, 97.0f);

  bool detected = ad.update(-1.0f, 1300, 96.0f);
  TEST_ASSERT_TRUE(detected);
}

void test_apogee_recorded_correctly(void) {
  ApogeeDetection ad(-0.5f);

  ad.update(2.0f, 1000, 90.0f);
  ad.update(1.0f, 1100, 95.0f);
  ad.update(0.5f, 1200, 98.0f);
  ad.update(-1.0f, 1300, 97.0f);

  TEST_ASSERT_TRUE(ad.event().detected);
  TEST_ASSERT_EQUAL(1300, ad.event().timestamp_ms);
  TEST_ASSERT_FLOAT_WITHIN(0.1f, 98.0f, ad.event().altitude_max);
}

void test_apogee_tracks_max_descent_speed(void) {
  ApogeeDetection ad(-0.5f);

  ad.update(2.0f, 1000, 100.0f);
  ad.update(-1.0f, 1100, 99.0f);
  ad.update(-5.0f, 1200, 97.0f);
  ad.update(-8.0f, 1300, 94.0f);
  ad.update(-3.0f, 1400, 92.0f);

  TEST_ASSERT_FLOAT_WITHIN(0.1f, -8.0f, ad.event().velocidade_max_descida);
}

void test_apogee_only_once(void) {
  ApogeeDetection ad(-0.5f);

  ad.update(2.0f, 1000, 100.0f);
  TEST_ASSERT_TRUE(ad.update(-1.0f, 1100, 99.0f));

  TEST_ASSERT_FALSE(ad.update(-2.0f, 1200, 97.0f));
}

void test_is_descending_flag(void) {
  ApogeeDetection ad(-0.5f);

  TEST_ASSERT_FALSE(ad.isDescending());
  ad.update(2.0f, 1000, 100.0f);
  TEST_ASSERT_FALSE(ad.isDescending());

  ad.update(-1.0f, 1100, 99.0f);
  TEST_ASSERT_TRUE(ad.isDescending());
}

void test_reset_clears_event(void) {
  ApogeeDetection ad(-0.5f);

  ad.update(2.0f, 1000, 100.0f);
  ad.update(-1.0f, 1100, 99.0f);
  TEST_ASSERT_TRUE(ad.event().detected);

  ad.reset();
  TEST_ASSERT_FALSE(ad.event().detected);
  TEST_ASSERT_FALSE(ad.isDescending());
}

int main(int argc, char** argv) {
  UNITY_BEGIN();

  RUN_TEST(test_apogee_not_detected_while_ascending);
  RUN_TEST(test_apogee_detected_at_vz_crossing);
  RUN_TEST(test_apogee_recorded_correctly);
  RUN_TEST(test_apogee_tracks_max_descent_speed);
  RUN_TEST(test_apogee_only_once);
  RUN_TEST(test_is_descending_flag);
  RUN_TEST(test_reset_clears_event);

  return UNITY_END();
}
