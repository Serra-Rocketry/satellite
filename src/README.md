# Firmware Source Code

Main source code for the Helike PocketQube satellite.

## Organization

### `sensors/`
Contains drivers and abstractions for the hardware sensors. Every sensor implements the `ISensor` interface for consistent data retrieval.
- `BME280Sensor`: Pressure, Temperature, Humidity.
- `ICM20602Sensor`: Accelerometer and Gyroscope.
- `GPSSensor`: Position and Timing.

### `modules/`
High-level system modules that orchestrate hardware and logic:
- `LoRaModule`: Manages radio transmission and packet formatting.
- `TelemetryModule`: Collects data from sensors and prepares it for storage/transmission.
- `FilesystemModule`: Handles dual-storage logic (SD card primary, LittleFS fallback).
- `LEDModule` & `BuzzerModule`: System status and alert indicators.

## Entry Point

The `main.cpp` file handles the system initialization and the primary execution loop, coordinating the telemetry sampling and transmission cycles.
