# Hardware Validation Tests

This directory contains a set of isolated Arduino sketches used to validate individual hardware components and their integration before they are incorporated into the main satellite firmware.

Unlike the main firmware (located in `src/`), these tests are designed to be run as simple Arduino sketches to ensure that the hardware is responding correctly on the bench.

## Structure

```text
test_hardware/
├── docs/               # Bench guides and implementation checklists
├── sensor/             # Isolated sensor tests (BME280, ICM-20602, GPS)
├── storage/            # Filesystem tests (SD Card, LittleFS)
└── integration/        # Multi-sensor logging and fallback tests
```

## How to use

1. Select the appropriate sketch for the component you are testing.
2. Upload the sketch to the ESP32-C3 using the Arduino IDE or PlatformIO.
3. Open the Serial Monitor at 115200 baud to verify the output.
4. Consult the guides in `docs/` for expected behavior and calibration steps.
