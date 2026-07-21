# SRAB Wing Analysis

This directory contains the aerodynamic study, simulations, and design iterations for the Bioinspired Autorotating Recovery System (SRAB).

## Purpose

The goal of this study is to optimize the wing geometry of the PocketQube satellite to ensure a stable autorotating descent, minimizing descent velocity and maximizing recovery accuracy.

## Project Structure

```text
wing-analysis/
├── docs/             # Theoretical basis, results, and LASC proposal
├── geometry/         # DXF profiles for different wing iterations (v1, v2, v3, etc.)
├── results/          # Raw simulation data, trajectory CSVs, and impact reports
└── src/              # Python scripts for simulation and analysis
    └── rocketpy_samara/ # Core simulation engine based on RocketPy
```

## Quick Start

1. **Theoretical Basis**: Start with `docs/teoria.md` to understand the physics of autorotation.
2. **Simulation**: Explore `src/` to see how the Monte Carlo simulations are performed.
3. **Results**: Check `docs/resultados.md` for a summary of the best performing wing profiles.

For detailed script references, see `docs/scripts.md`.
