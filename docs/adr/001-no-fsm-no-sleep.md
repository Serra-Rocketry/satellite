# ADR-001: No FSM, No Sleep Mode

## Status

Accepted.

## Context

The satellite (#213) is a PocketQube that remains completely powered off (no
energy) until the rocket deploys at apogee. Upon power-on, the system is
already descending — there is no need to detect liftoff, manage flight
states, or maintain sleep mode.

The flight-computer (#11) uses a 4-state FSM (IDLE/ASCENT/DESCENT/LANDED)
with FreeRTOS to manage the full flight cycle. This complexity does not
apply to the satellite.

## Decision

Implement the firmware as a simple continuous loop, without FSM, FreeRTOS,
or sleep mode. The system:

1. Initializes sensors and LoRa as quickly as possible
2. Enters a read + transmit loop at 5Hz
3. Has no flight states

## Consequences

### Positive

- Simple code, easy to debug
- Smaller bug surface
- Reduced RAM/flash consumption
- Faster builds

### Negative

- Does not support complex flight logic (parachute deployment, etc.)
- Cannot distinguish flight phases to adjust sampling rate

### Mitigation

If needed in the future, add a simplified FSM (3 states) as an optional module.

## Alternatives Considered

1. **FSM with FreeRTOS** (flight-computer pattern) — rejected: unnecessary
   complexity for a system that powers on already descending
2. **Continuous loop** (chosen) — simpler, sufficient for the mission profile

---

# ADR-005: Static Global Objects (No Heap Allocation)

## Status

Accepted.

## Context

The ESP32-C3 has only 400KB of RAM. Dynamic allocation (new/malloc) in
embedded systems can cause fragmentation and runtime failures during
extended operation.

## Decision

All module objects are declared as `static` globals. No dynamic allocation
is used in the main firmware.

**Rationale**:

- Memory determinism
- No fragmentation
- Easy to track RAM usage

## Consequences

### Positive

- Predictable RAM usage
- No risk of out-of-memory during extended operation

### Negative

- Objects cannot be destroyed/recreated
- Unit tests require careful setup/teardown
