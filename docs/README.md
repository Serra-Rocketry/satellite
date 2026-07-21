# Documentation

Technical documentation for the Helike PocketQube satellite (#213 - LASC 2026).

## Contents

| Document | Description |
|----------|-------------|
| [software.md](software.md) | Software architecture, modules, and data flow |
| [hardware.md](hardware.md) | Hardware specifications, pinouts, and BOM |
| [firmware.md](firmware.md) | Firmware build and deployment guide |
| [flowchart.md](flowchart.md) | System flowcharts (Mermaid diagrams) |
| [adr/](adr/) | Architecture Decision Records |

## Architecture Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](adr/001-no-fsm-no-sleep.md) | No FSM, No Sleep Mode | Accepted |
| [ADR-002](adr/002-sd-littlefs-fallback.md) | SD Primary + LittleFS Fallback | Accepted |
| [ADR-003](adr/003-tinygpsplus-vs-manual.md) | TinyGPSPlus vs Manual NMEA | Accepted |
| [ADR-004](adr/004-platformio-vs-arduino-ide.md) | PlatformIO vs Arduino IDE | Accepted |

## Related Documentation

- [Hardware tests](../test_hardware/docs/) — Bench guides and checklists
- [Wing analysis](../extras/wing-analysis/docs/) — SRAB aerodynamic study
- [Mechanical assembly](../hardware/mechanical/README.md) — CAD file structure
