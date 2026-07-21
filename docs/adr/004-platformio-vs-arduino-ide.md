# ADR-004: PlatformIO vs. Arduino IDE

## Status

Accepted.

## Context

The flight-computer uses Arduino IDE for development. The satellite uses
PlatformIO with a native environment for unit tests.

## Decision

Keep PlatformIO as the build tool for the satellite.

## Rationale

- **Native unit tests (Unity)**: Integrated via `pio test -e native`
- **Reproducible CLI builds**: `pio run -e helike_esp32c3`
- **Multiple environments**: ESP32-C3 (firmware) + native (tests) in same project
- **Dependency management**: `lib_deps` resolves automatically
- **CI/CD friendly**: Build and tests accessible via command line

## Consequences

### Positive

- Automated tests
- Automatic dependency resolution
- Separate test environment from hardware

### Negative

- Learning curve for new members
- Requires PlatformIO installation (via pip or VS Code extension)

## Alternatives Considered

1. **Arduino IDE** (like flight-computer) — simple, but no native tests
2. **ESP-IDF native** — more control, but more complex for beginners
3. **PlatformIO** (chosen) — balances simplicity and test capability

## Implementation

See `platformio.ini` with environments `[env:helike_esp32c3]` and `[env:native]`.
