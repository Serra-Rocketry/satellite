# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Full project documentation in English (Doxygen on all .h/.cpp/.ino files)
- `docs/software.md` — software architecture and data flow documentation
- `docs/hardware.md` — hardware specifications, pinout, and wiring
- `docs/firmware.md` — build, upload, and testing guide
- `docs/flowchart.md` — Mermaid system flowcharts
- `docs/README.md` — documentation index
- `CHANGELOG.md` — project changelog following Keep a Changelog

### Changed

- All Doxygen comments translated from Portuguese to English
- `README.md` fully translated to English with restructured content
- AGENTS.md conventions updated to English documentation standard

## [1.1.0] - 2026-XX-XX

### Added

- LittleFS logging support with USE_LITTLEFS compile flag
- Integrated validation with lib/calc (NaN and range checks)
- BME280/BMP280 and ICM-20602 support

### Changed

- Pin adjustments and driver refinements
- Standardized CSV format for post-flight analysis

### Removed

- Legacy items from previous project version

## [1.0.0] - 2026-01-27

### Added

- Initial release
- BMP280 barometric sensor support
- ICM-20602 IMU support
- GPS NEO-8M integration
- LoRa telemetry (RFM95W)
- LittleFS data logging
- Hardware validation sketches (test_hardware/)
- Wing analysis study (extras/wing-analysis/)
- Architecture Decision Records (docs/adr/)

[Unreleased]: https://github.com/team100/satellite/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/team100/satellite/releases/tag/v1.0.0
