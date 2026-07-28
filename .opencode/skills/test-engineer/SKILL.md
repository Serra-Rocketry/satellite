---
name: test-engineer
description: Test engineer specializing in embedded systems validation, hardware-in-the-loop testing, and simulation-based verification.
license: MIT
compatibility: opencode
---

## Expertise
- Unit testing for embedded systems
- Hardware-in-the-loop (HIL) testing
- Python-based simulation and data analysis
- Test automation and CI/CD
- Data analysis and validation

## Responsibilities
1. **Create Test Plans**
   - Define test cases for each module
   - Specify acceptance criteria
   - Document test procedures
   
2. **Implement Tests**
   - Write unit tests (Unity framework)
   - Create hardware test firmware
   - Develop Python simulators
   
3. **Validate System**
   - Run validation with real data
   - Perform bench tests
   - Analyze telemetry logs

## Testing Pyramid

```
         /\
        /  \  Manual Hardware Tests
       /____\
      /      \ Hardware-in-Loop (Arduino)
     /________\
    /          \ Unit Tests (Native)
   /____________\
  /              \ Simulation (Python)
 /________________\
```

## Test Types

### 1. Simulation Tests (Python)

**Purpose**: Validate algorithms with real data before hardware testing

**Location**: `extras/wing-analysis/`

#### Wing Analysis Validation
**File**: `src/samara_pq_simulation.py`

**Usage**:
```bash
python extras/wing-analysis/src/samara_pq_simulation.py
```

**What it Tests**:
- Parametric impact on descent metrics
- Sensitivity to geometry changes
- Consistency of simulation outputs

**Expected Output**:
```
Simulation completed
Outputs generated in extras/wing-analysis/results/
```

**Creating New Simulation Tests**:
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load simulation outputs
df = pd.read_csv('extras/wing-analysis/results/test_1_asa1/samara_pq_impact_report.csv')

# Extract metrics
velocity = df['velocity'].values

# Calculate derived values
v_mean = np.mean(velocity)

# Simple sanity check
assert v_mean > 0, "Invalid mean velocity"
print("Simulation metrics validated")
```

---

### 2. Unit Tests (Native C++)
**Framework**: Unity Test Framework (PlatformIO)

**Location**: `test/`

**Setup**:
```ini
; platformio.ini
[env:native]
platform = native
test_framework = unity
build_flags = -std=c++11
```

#### Example: Sensor Unit Test
**File**: `test/test_native/test_calc_validation.cpp`

```cpp
#include <unity.h>
#include "lib/calc/DataValidation.h"

static float mock_pressure_pa = 101325.0f;

void setUp(void) {
  // Setup before each test
}

void tearDown(void) {
  // Cleanup after each test
}

// Test: Pressure validation
void test_pressure_validation(void) {
  SensorData data = {};
  data.pressao = mock_pressure_pa;
  data.ax = data.ay = data.az = 0.0f;
  data.altura = 0.0f;
  data.vz = 0.0f;
  DataValidation dv;
  TEST_ASSERT_TRUE(dv.isValid(data));
}

// Test: NaN handling
void test_nan_handling(void) {
  SensorData data = {};
  data.pressao = NAN;
  DataValidation dv;
  TEST_ASSERT_FALSE(dv.isValid(data));
}

// Test: Range guard
void test_range_guard(void) {
  SensorData data = {};
  data.pressao = 10.0f;
  DataValidation dv;
  TEST_ASSERT_FALSE(dv.isValid(data));
}

int main(int argc, char **argv) {
  UNITY_BEGIN();
  
RUN_TEST(test_pressure_validation);
RUN_TEST(test_nan_handling);
RUN_TEST(test_range_guard);
  
  return UNITY_END();
}
```

**Run Tests**:
```bash
pio test -e native
```

**Expected Output**:
```
test/test_native/test_bmp585.cpp:45: test_altitude_calculation [PASSED]
test/test_native/test_bmp585.cpp:56: test_nan_handling [PASSED]
test/test_native/test_bmp585.cpp:67: test_vertical_velocity [PASSED]

------------------
3 Tests 0 Failures 0 Ignored
OK
```

---

### 3. Hardware Tests (Arduino)

**Purpose**: Validate modules with real hardware

**Location**: `test_hardware/`

#### Sensor Integration Test
**File**: `test_hardware/integration/sensor_logging_v3/sensor_logging_v3.ino`

```cpp
// Veja o sketch de integracao em test_hardware/integration/sensor_logging_v3/
// Ele cobre ICM-20602, BME280 e GPS NEO-8M com logging em LittleFS.
```

**Test Procedure**:
1. Upload firmware to ESP32-C3
2. Open Serial Monitor (115200 baud)
3. Observe initialization logs
4. Move board up/down and observe altitude/vz
5. Confirm CSV is written in LittleFS

**Expected Output**:
```
=== Teste Unificado de Sensores v3 ===
 ICM20602 encontrado!
 BME280 initialized!
 GPS UART initialized!
 LittleFS montado!
```

---

## Test Data Management

### Bench Data
**Location**: `test_hardware/integration/`

**Format**:
```csv
millis,ax,ay,az,gx,gy,gz,pressao_Pa,altura_m,temperatura_C,umidade_pct,vz,mag_giroscopia,lat,lon,alt_gps
0,0.1,-0.05,10.0,0.0,0.0,0.0,101325,50.0,25.3,45.2,0.0,0.0,-23.5521,-46.6333,52.3
50,-0.2,0.15,10.2,-0.001,0.001,0.002,101320,49.96,25.3,45.2,-0.08,0.0024,-23.5521,-46.6333,52.3
...
```

---

## Continuous Integration (Future)

### GitHub Actions Workflow
**File**: `.github/workflows/test.yml`

```yaml
name: Test

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install PlatformIO
        run: pip install platformio
      
      - name: Run Native Tests
        run: pio test -e native
  
  wing-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      
      - name: Install Dependencies
        run: pip install -r extras/wing-analysis/requirements.txt
      
      - name: Run Wing Analysis
        run: python extras/wing-analysis/src/samara_pq_simulation.py
```

---

## Test Documentation Template

### Test Case Template
```markdown
## Test Case: TC-001 - Sensor Logging Baseline

**Module**: Sensor Logging  
**Priority**: Critical  
**Type**: Functional

### Objective
Verify that sensor logging generates valid CSV with stable rates.

### Preconditions
- Sensors initialized
- LittleFS mounted

### Test Data
- Stable bench readings
- Acquisition interval = 50 ms

### Steps
1. Start logging sketch
2. Wait 60 seconds
3. Extract CSV from LittleFS
4. Check for NaN/invalid ranges

### Expected Result
- CSV contains header and continuous rows
- No invalid values in pressure/altitude columns

### Actual Result
[To be filled during test execution]

### Pass/Fail
[ ] Pass  [ ] Fail

### Notes
Based on bench test data from test_hardware
```

---

## Resources
- `test_hardware/docs/` - Guias e checklists
- `extras/wing-analysis/` - Simulacao e relatorios
- Unity Test Framework documentation
