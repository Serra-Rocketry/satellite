# Native Unit Tests

This directory contains the unit tests for the satellite's core logic.

## Framework

We use the **Unity** test framework, running natively on the host machine (PC) instead of the target hardware. This allows for rapid iteration and the use of large datasets for validation.

## Test Suites

- `test_vz/`: Validates the Vertical Velocity calculation and EMA filter accuracy.
- `test_apogee/`: Verifies the apogee detection logic against known flight profiles.
- `test_validation/`: Checks the data validation filters for edge cases and sensor failures.

## How to Run

Use PlatformIO to execute the native tests:

```bash
pio test -e native
```

For more detailed output:
```bash
pio test -e native -v
```
