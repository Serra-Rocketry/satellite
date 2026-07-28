# -*- coding: utf-8 -*-
"""SRABMonteCarlo — Análise de sensibilidade paramétrica do SRAB.

Fase 1: varia apenas parâmetros do SRAB (massa, beta, cd0).
        A subida (RocketPy Flight) é fixa.
Fase 2 (futuro): adiciona perturbação no ascent (inclination, vento).

Uso básico:
from rocketpy_samara.srab_recovery import SRABRecovery  # noqa: E402
    from rocketpy_samara.monte_carlo import SRABMonteCarlo, StochParam

    mc = SRABMonteCarlo(base_recovery, n=200)
    mc.add_param("mass_kg", "normal", (0.200, 0.005))
    mc.add_param("beta_deg", "normal", (8.0, 0.5))
    mc.run()
    stats = mc.process()
    mc.export_csv("mc_results.csv")
"""

import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_SRC = Path(__file__).resolve().parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from rocketpy_samara.srab_recovery import SRABRecovery  # noqa: E402


@dataclass
class StochParam:
    """Definition of a stochastic parameter and its distribution.

    Attributes
    ----------
    name : str
        Parameter name (must match a kwarg of SRABRecovery or
        PocketQubeSamaraWing).
    dist : str
        Distribution type: ``"normal"``, ``"uniform"``, or ``"discrete"``.
    params : tuple
        Distribution parameters:

        - ``"normal"``: ``(mean, std)``
        - ``"uniform"``: ``(min, max)``
        - ``"discrete"``: ``list`` or ``tuple`` of values to sample from.
    """

    name: str
    dist: str
    params: tuple


class SRABMonteCarlo:
    """Monte Carlo analysis for SRAB descent parameters.

    Parameters
    ----------
    base_recovery : SRABRecovery
        Base recovery instance (wing + config). Will be deep-copied
        for each MC iteration with perturbed parameters.
    n : int
        Number of Monte Carlo iterations.
    seed : int, optional
        Random seed for reproducibility.
    """

    def __init__(self, base_recovery, n: int = 200, seed: int = None):
        self._base = base_recovery
        self.n = n
        self._params: list[StochParam] = []
        self._rng = np.random.default_rng(seed)

        # Results storage
        self.input_log: list[dict] = []
        self.results: dict[str, list] = {
            "t_impact": [],
            "v_impact": [],
            "spin_rpm": [],
            "theta_eq_deg": [],
            "x_impact": [],
            "y_impact": [],
        }

    # ------------------------------------------------------------------
    # Parameter registration
    # ------------------------------------------------------------------

    def add_param(self, name: str, dist: str, params: tuple):
        """Register a stochastic parameter.

        Parameters
        ----------
        name : str
            Parameter name (matches kwarg in SRABRecovery).
        dist : str
            ``"normal"``, ``"uniform"``, or ``"discrete"``.
        params : tuple
            See ``StochParam``.
        """
        self._params.append(StochParam(name, dist, params))

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def _sample_one(self, param: StochParam) -> float:
        """Draw a single sample from the given distribution."""
        if param.dist == "normal":
            return float(self._rng.normal(*param.params))
        elif param.dist == "uniform":
            return float(self._rng.uniform(*param.params))
        elif param.dist == "discrete":
            return float(self._rng.choice(param.params))
        else:
            raise ValueError(f"Unknown distribution: {param.dist}")

    def _sample_all(self) -> dict:
        """Draw one sample from every registered parameter."""
        return {p.name: self._sample_one(p) for p in self._params}

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self, verbose: bool = True):
        """Execute all Monte Carlo iterations serially.

        Parameters
        ----------
        verbose : bool
            Print progress every 50 iterations.
        """
        self.input_log.clear()
        for k in self.results:
            self.results[k].clear()

        for i in range(self.n):
            sampled = self._sample_all()

            # Clone wing and apply sampled parameters
            wing_i = deepcopy(self._base.wing)

            # Apply scalar overrides to wing object directly
            for k, v in sampled.items():
                if k == "mass_kg":
                    wing_i.mass = v
                    wing_i._initialize_inertia_tensor()
                elif k == "n_wings":
                    wing_i.n_wings = int(v)
                    wing_i._apply_geometry_scaling()
                elif k == "beta_deg":
                    wing_i.beta_mount = np.radians(v)
                elif k == "f_factor":
                    wing_i.f_factor = v
                    wing_i._initialize_inertia_tensor()
                elif k == "cd0":
                    wing_i.cd0 = v
                elif k == "rho":
                    wing_i.rho = v
                # radius update is handled by the optimizer if active

            # Build kwargs for SRABRecovery (don't duplicate wing params)
            kw = dict(self._base.kwargs)
            kw.update(sampled)

            rec = SRABRecovery(wing_i, env=self._base.env, **kw)
            # simulate() uses the wing from rec.wing, which is wing_i
            sol = rec.simulate()

            self.input_log.append(sampled)
            self.results["t_impact"].append(sol.t_impact)
            self.results["v_impact"].append(sol.v_impact)
            self.results["spin_rpm"].append(sol.spin_impact_rpm)
            self.results["theta_eq_deg"].append(sol.theta_eq)
            self.results["x_impact"].append(sol.x_impact)
            self.results["y_impact"].append(sol.y_impact)

            if verbose and (i + 1) % 50 == 0:
                print(f"  MC progress: {i + 1}/{self.n}")

        # Convert all to numpy arrays
        for k in self.results:
            self.results[k] = np.array(self.results[k])

    # ------------------------------------------------------------------
    # Post-processing
    # ------------------------------------------------------------------

    def process(self) -> dict:
        """Compute summary statistics over all MC iterations.

        Returns
        -------
        dict
            Dictionary with keys like ``v_impact_mean``, ``v_impact_std``,
            ``v_impact_p5``, ``v_impact_p95``, ``cep_radius``, etc.
        """
        stats = {}
        for k, arr in self.results.items():
            stats[f"{k}_mean"] = float(np.mean(arr))
            stats[f"{k}_std"] = float(np.std(arr))
            stats[f"{k}_p5"] = float(np.percentile(arr, 5))
            stats[f"{k}_p95"] = float(np.percentile(arr, 95))
            stats[f"{k}_min"] = float(np.min(arr))
            stats[f"{k}_max"] = float(np.max(arr))

        # Circular Error Probable (50th percentile of impact distance)
        dx = self.results["x_impact"]
        dy = self.results["y_impact"]
        stats["cep_radius"] = float(np.median(np.sqrt(dx**2 + dy**2)))

        # LASC window compliance (|v_impact| between 20 and 45 m/s)
        v = self.results["v_impact"]
        stats["lasc_window_pass_rate"] = float(np.mean((v >= 20.0) & (v <= 45.0)))

        return stats

    def print_summary(self):
        """Print key statistics to stdout."""
        stats = self.process()
        print("\n" + "=" * 65)
        print("  MONTE CARLO — Summary")
        print("=" * 65)
        print(f"  Iterações:                {self.n}")
        print(f"  Parâmetros variados:      {', '.join(p.name for p in self._params)}")
        print("─" * 65)
        print(
            f"  v_impacto médio:          "
            f"{stats['v_impact_mean']:.2f} ± {stats['v_impact_std']:.2f} m/s"
        )
        print(
            f"  v_impacto [P5, P95]:      "
            f"[{stats['v_impact_p5']:.2f}, {stats['v_impact_p95']:.2f}] m/s"
        )
        print(
            f"  t_descida médio:          "
            f"{stats['t_impact_mean']:.1f} ± {stats['t_impact_std']:.1f} s"
        )
        print(
            f"  Spin médio:               "
            f"{stats['spin_rpm_mean']:.0f} ± {stats['spin_rpm_std']:.0f} RPM"
        )
        print(f"  θ_eq médio:               {stats['theta_eq_deg_mean']:.1f}°")
        print(f"  CEP radius:               {stats['cep_radius']:.2f} m")
        print(
            f"  LASC window pass rate:    {stats['lasc_window_pass_rate'] * 100:.1f}%"
        )
        print("=" * 65)

    def export_csv(self, path: str):
        """Export all MC results (inputs + outputs) to CSV.

        Parameters
        ----------
        path : str
            Output CSV file path.
        """
        import csv

        # Build column names from input params + result fields
        input_keys = [p.name for p in self._params]
        result_keys = list(self.results.keys())
        fieldnames = input_keys + result_keys

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            for i in range(self.n):
                row = [self.input_log[i].get(k, "") for k in input_keys]
                row += [self.results[k][i] for k in result_keys]
                writer.writerow(row)

        print(f"  MC results saved: {path}")


# Re-import needed by run() — at module level for clarity
