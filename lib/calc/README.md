# Calculation Library (`lib/calc`)

This is a header-only C++ library containing the core mathematical and physical logic for the satellite. 

## Purpose

By keeping these calculations in a separate, hardware-independent library, we can:
1. **Test in Isolation**: Run native unit tests on a PC (`pio test -e native`) without needing an ESP32.
2. **Ensure Portability**: Reuse the logic in different flight computer versions or ground station tools.
3. **Simplify Debugging**: Verify complex formulas (like vertical velocity or apogee detection) using simulated CSV data.

## Modules

- `SensorData.h`: Common structures for holding telemetry data.
- `VerticalVelocity.h`: Implements EMA (Exponential Moving Average) filtering for altitude-to-velocity conversion.
- `ApogeeDetection.h`: Logic for detecting the highest point of flight.
- `DataValidation.h`: Range and NaN checks to filter out sensor noise/failures.

## Usage

Since it is header-only, simply include the required file:
```cpp
#include <VerticalVelocity.h>
```
