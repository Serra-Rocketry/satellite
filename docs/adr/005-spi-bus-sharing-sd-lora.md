# ADR-005: Single SPI Bus Sharing Between SD Card and LoRa Radio

## Status

Accepted (2026-08-24, bench session findings).

## Context

The satellite shares one SPI bus (SCK=GPIO4, MISO=GPIO5, MOSI=GPIO6)
between the RFM95W LoRa radio (CS=GPIO7) and the SD card slot
(CS=GPIO10). During first-power-on bench testing, the system showed
confusing intermittent behavior:

- LoRa init failed ("RFM95W not found") whenever the SD mount was
  attempted first;
- SD mount itself was intermittent across boots;
- The same binary alternated between working and failing without any
  code change.

Isolation with minimal probe sketches (`/tmp` PlatformIO projects,
not committed) narrowed the root causes:

1. **SD driver reconfigures the SPI peripheral.** `spi->begin()` called
   again by `FilesystemModule::setupSD()`, and especially `SD.end()`
   inside the old retry path, tear down / reconfigure the ESP32-C3 SPI
   peripheral. Any LoRa configuration already applied to the radio is
   not lost, but the bus-level state the library expects is.
2. **Initialization order matters.** With LoRa initialized *after* an
   SD attempt, `endPacket()` calls fail 100%. With LoRa initialized
   *first*, SD failure does not affect radio TX at all (verified:
   TX 5/5 after a failed `SD.begin()`).
3. **A pre-existing logic bug masked radio health.** `LoRaModule::send()`
   treated `LoRa.endPacket() != 0` as failure, but the sandeepmistry
   library returns **1 on success**. Every successful transmission was
   being reported as an error since the module was created.

## Decision

1. **Single SPI initialization in `main.cpp setup()`**, before any
   device: explicit `SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI)` with
   both CS pins driven HIGH. Devices never call `spi->begin()` on their
   own.

2. **Boot order: LoRa first, storage second.** The radio is configured
   once and never touched by storage code. SD/LittleFS mount afterwards.

3. **No `SD.end()` anywhere.** A failed mount leaves the bus alone; the
   module falls back to LittleFS instead of retrying destructively.

4. **Runtime SD-to-LittleFS fallback.** If the SD dies mid-flight
   (`appendLine()` fails 5 consecutive times), `FilesystemModule`
   switches to LittleFS automatically and keeps logging.

5. **`send()` success check corrected** to `endPacket() == 1`.

## Consequences

- SD mount is best-effort; telemetry never depends on it.
- Any future SPI device on this bus must follow the same rules: reuse
  the global `SPI` instance via `setSPI()`/shared handle, never call
  `SPI.begin()` again, never call `<lib>.end()` on shared buses.
- The RFM95W must be initialized before any SD mount attempt for the
  rest of the project's lifetime unless the driver situation changes.

## Verification

Bench sequence that must pass before flight (all steps on the final
wiring):

```
[LORA] Pre-begin RegVersion: 0x12     <- radio reachable over SPI
[LORA] RFM95W OK (915MHz)             <- radio configured
[FS] Storage: ...                     <- SD or LittleFS active
#213,... packets with zero [LORA] ERROR lines
```

Reference probes used during isolation are described in
`docs/hardware.md` (Known Issues section).
