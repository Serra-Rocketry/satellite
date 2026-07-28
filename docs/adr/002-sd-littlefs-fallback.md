# ADR-002: SD Primary with LittleFS Fallback

## Status

Accepted.

## Context

The flight-computer uses LittleFS as the primary storage for CSV logging.
The satellite has an SD card slot (test_hardware) but SD is not present in
real flight.

The `test_hardware/storage/sd_littlefs_fallback` test demonstrates the
pattern: try SD first, use LittleFS as fallback.

## Decision

Implement FilesystemModule with runtime detection:

1. Try `SD.begin(CS)` first
2. If that fails, use `LittleFS.begin(true)` as fallback
3. Automatic dispatch of operations based on active storage type

No compile-time flag — the module always compiles and detects available
storage at runtime.

## Consequences

### Positive

- Works on the bench (with SD) and in flight (without SD)
- No dead code overhead when SD is not present
- Pattern already validated in hardware tests

### Negative

- SD card library adds ~2KB of flash even when unused
- More complex than using LittleFS only

## Alternatives Considered

1. **LittleFS only** — simpler but no SD support on the bench
2. **SD only** — fails in flight without SD card
3. **SD + LittleFS fallback** (chosen) — works in both scenarios

## Implementation

See `src/modules/FilesystemModule.h` and `src/modules/FilesystemModule.cpp`.
