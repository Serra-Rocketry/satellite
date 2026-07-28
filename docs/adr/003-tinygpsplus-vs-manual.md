# ADR-003: TinyGPSPlus vs. Manual NMEA Parsing

## Status

Accepted.

## Context

The test_hardware v3 uses manual NMEA parsing (character-by-character
reading, field extraction, checksum). The TinyGPSPlus library offers
higher-level abstraction with automatic validation.

## Decision

Use TinyGPSPlus as the GPS parser. The manual parsing from v3 is kept as
reference in `test_hardware/integration/sensor_logging_v3/`.

## Rationale

- **Less code, fewer bugs**: TinyGPSPlus implements checksum validation
  and field extraction
- **Testable**: Compiles in native environment for unit tests
- **Stable**: Widely used library in the Arduino/ESP32 community

## Consequences

### Positive

- Cleaner, more maintainable code
- Automatic NMEA checksum validation

### Negative

- TinyGPSPlus adds ~3KB of flash
- Abstraction hides NMEA protocol details

## Alternatives Considered

1. **Manual parsing** (like v3) — more control, but more code and more bugs
2. **TinyGPSPlus** (chosen) — less code, fewer bugs, faster to implement

## Implementation

See `src/sensors/GPSSensor.h` and `src/sensors/GPSSensor.cpp`.
