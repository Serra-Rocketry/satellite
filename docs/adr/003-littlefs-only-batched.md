# ADR-003: LittleFS-Only Storage with Batched Writes

## Status

Accepted (2026-08-14). Supersedes [ADR-002](./002-sd-littlefs-fallback.md).

## Context

The SD card was physically removed from the Helike PocketQube hardware.
LittleFS on the ESP32-C3 internal flash is now the sole storage medium.

The original `appendLine()` called `open()` → `println()` → `flush()` →
`close()` on every packet — one flash page erase+write per telemetry line.
At 5 Hz over a 5-7 minute descent, that is ~1,500-2,100 flash writes per
flight, each blocking the main loop for 5-30 ms.

This has two problems:

1. **Flash wear** — ESP32-C3 SPI flash is rated ~100,000 erase cycles per
   sector. Per-packet flush concentrates writes on a small region; even
   with LittleFS wear-leveling, 2,000 writes are unnecessary overhead.
2. **Loop latency** — 5-30 ms per `flush()` in a 200 ms loop leaves less
   headroom for LoRa TX, I2C reads, and IMU sampling.

## Decision

Replace per-packet flash writes with **batched writes**:

1. Buffer telemetry lines in a **static RAM array** (no heap):
   `BATCH_SIZE = 16` lines × `BATCH_LINE_MAX = 160` bytes = ~2.6 KB
2. `appendLine()` copies the packet into the RAM buffer — no flash access
3. `flushBatch()` opens the file once, writes all 16 lines, `flush()`es,
   and closes — one atomic flash operation per batch
4. When the buffer is full, `appendLine()` returns `false`; the caller
   (`main.cpp`) calls `flushBatch()` and retries
5. **Safety net**: a partial flush (`BATCH_TIMEOUT_MS = 2000 ms`) ensures
   the tail of the flight isn't lost in RAM if power cuts with a partial
   buffer

### Configuration

| Define | Location | Value | Purpose |
|--------|----------|-------|---------|
| `BATCH_SIZE` | `FilesystemModule.h` | 16 | Lines per flush |
| `BATCH_LINE_MAX` | `FilesystemModule.h` | 160 | Max bytes per CSV line |
| `BATCH_TIMEOUT_MS` | `config.h` | 2000 | Partial flush interval |

## Consequences

### Positive

- **16× fewer flash writes** — ~130 writes/mission instead of ~2,000
- **Near-zero loop latency** for 15 of 16 iterations (memcpy in RAM)
- **~2.6 KB static RAM** — negligible on 400 KB total (5.5% used)
- Flash binary shrinks ~2 KB (no `SD.h` library)
- LittleFS journaling survives power-loss mid-batch — only the in-flight
  batch is lost, previous batches persist
- Max data loss on abrupt power-off: `BATCH_TIMEOUT_MS` = 2 s = 10 samples

### Negative

- Last partial batch (< 16 lines) waits up to 2 s to be written —
  mitigated by the `BATCH_TIMEOUT_MS` safety net
- Test hardware sketches in `test_hardware/storage/` still reference SD —
  they are standalone bench sketches and not part of flight firmware

## Alternatives Considered

1. **Per-packet flush** (original) — simplest but maximal wear + latency
2. **SPIFFS** — inferior to LittleFS (no journaling, no wear-leveling,
   fragmentation issues); rejected
3. **LittleFS only, no batching** — simpler but same wear problem as
   per-packet flush
4. **LittleFS + batched writes** (chosen) — minimal wear, minimal latency,
   power-loss resilient

## Implementation

See `src/modules/FilesystemModule.h`, `src/modules/FilesystemModule.cpp`,
and `src/main.cpp` (loop, ~line 200).
