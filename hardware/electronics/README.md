# Electronics Hardware

This directory contains the electrical design files for the Helike satellite, including schematics and PCB layouts.

## Project Structure

```text
electronics/
├── electronics.kicad_pro   # KiCad project file
├── electronics.kicad_sch   # Circuit schematic
├── electronics.kicad_pcb    # PCB layout
├── electronics.pretty/      # Custom footprints
└── Library.pretty/         # Local component library
```

## Design Notes

- **MCU**: ESP32-C3 Super Mini
- **Interface**: I2C for sensors, SPI for LoRa and SD Card, UART for GPS.
- **Tools**: Designed using KiCad 8.0.

For the mechanical integration of the PCB, see `hardware/mechanical/electronics/`.
