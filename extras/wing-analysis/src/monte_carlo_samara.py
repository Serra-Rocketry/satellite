#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monte Carlo — Análise de sensibilidade paramétrica do SRAB (sem RocketPy)

Varia parâmetros do sistema (massa, beta, cd0, f_factor, n_wings, rho)
e executa N descidas completas via PocketQubeFlightDynamics.

Uso:
    python src/monte_carlo_samara.py --dxf geometry/Asa3.DXF --n 100 --seed 42
    python src/monte_carlo_samara.py --mass-mean 0.200 --mass-std 0.010 --beta-mean 3 --beta-std 0.5
    python src/monte_carlo_samara.py --export results/mc_samara.csv
"""

import argparse
import csv
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from samara_pq_simulation import (
    PocketQubeFlightDynamics,
    PocketQubeMissionReporter,
    PocketQubeSamaraWing,
)


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Monte Carlo — Análise de sensibilidade SRAB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Geometria
    p.add_argument("--dxf", default="geometry/Asa3.DXF", help="Arquivo DXF da asa")

    # MC config
    p.add_argument("--n", type=int, default=200, help="Número de iterações")
    p.add_argument("--seed", type=int, default=None, help="Semente aleatória")

    # Parâmetros nominais (usados se os respectivos --*-std forem 0 ou omitidos)
    p.add_argument("--mass-mean", type=float, default=0.200, help="Massa média [kg]")
    p.add_argument("--mass-std", type=float, default=0.005, help="Desvio padrão da massa [kg]")
    p.add_argument("--beta-mean", type=float, default=3.0, help="Ângulo β médio [graus]")
    p.add_argument("--beta-std", type=float, default=0.3, help="Desvio padrão β [graus]")
    p.add_argument("--cd0-mean", type=float, default=1.0, help="Cd0 médio")
    p.add_argument("--cd0-std", type=float, default=0.10, help="Desvio padrão Cd0")
    p.add_argument("--f-factor-mean", type=float, default=0.3, help="f_factor médio")
    p.add_argument("--f-factor-std", type=float, default=0.03, help="Desvio padrão f_factor")
    p.add_argument("--rho-mean", type=float, default=1.225, help="Densidade média [kg/m³]")
    p.add_argument("--rho-std", type=float, default=0.0, help="Desvio padrão densidade")

    # Parâmetros fixos da simulação
    p.add_argument("--n-wings", type=int, default=4, help="Número de asas (fixo)")
    p.add_argument("--altitude", type=float, default=1000.0, help="Altitude inicial [m]")
    p.add_argument("--theta-deg", type=float, default=0.0, help="Ângulo θ inicial [graus]")
    p.add_argument("--theta-dot", type=float, default=0.0, help="θ_dot inicial [rad/s]")
    p.add_argument("--phi-dot", type=float, default=0.0, help="φ_dot inicial [rad/s]")
    p.add_argument("--v0", type=float, default=0.0, help="Velocidade vertical inicial [m/s]")
    p.add_argument("--t-max", type=float, default=600.0, help="Tempo máximo de simulação [s]")
    p.add_argument("--max-step", type=float, default=0.2, help="Passo máximo do integrador [s]")

    # Saída
    p.add_argument("--export", default=None, help="Caminho para exportar CSV")
    p.add_argument("--verbose", action="store_true", default=True, help="Mostrar progresso")

    return p.parse_args(argv)


def _sample_normal(rng, mean, std):
    if std <= 0.0:
        return mean
    return float(rng.normal(mean, std))


def _sample_discrete(rng, values):
    return float(rng.choice(values))


def run_single(wing, args_dict, rng, vary):
    """Clona a asa, aplica parâmetros amostrados, simula e retorna métricas."""
    w = deepcopy(wing)

    if vary["mass_std"] > 0:
        w.mass = _sample_normal(rng, vary["mass_mean"], vary["mass_std"])
    if vary["f_factor_std"] > 0:
        w.f_factor = _sample_normal(rng, vary["f_factor_mean"], vary["f_factor_std"])
        w._initialize_inertia_tensor()
    if vary["cd0_std"] > 0:
        w.cd0 = _sample_normal(rng, vary["cd0_mean"], vary["cd0_std"])
    if vary["beta_std"] > 0:
        w.beta_mount = np.radians(
            _sample_normal(rng, vary["beta_mean"], vary["beta_std"])
        )
    if vary["rho_std"] > 0:
        w.rho = _sample_normal(rng, vary["rho_mean"], vary["rho_std"])

    solver = PocketQubeFlightDynamics(w)
    sol = solver.simulate_drop(
        initial_conditions=[
            np.radians(args_dict["theta_deg"]),
            args_dict["theta_dot"],
            args_dict["phi_dot"],
            args_dict["v0"],
            args_dict["altitude"],
        ],
        t_span=(0, args_dict["t_max"]),
        max_step=args_dict["max_step"],
    )

    reporter = PocketQubeMissionReporter(w, sol)
    summary = reporter.build_summary()

    return {
        "mass_kg": w.mass,
        "beta_deg": float(np.degrees(w.beta_mount)),
        "cd0": w.cd0,
        "f_factor": w.f_factor,
        "rho": w.rho,
        "t_impact": summary["impact"]["time_s"],
        "v_impact": summary["impact"]["speed_magnitude_ms"],
        "spin_rpm": summary["angular"]["spin_rpm"],
        "theta_eq_deg": summary["angular"]["theta_deg"],
        "ke_impact": summary["impact"]["kinetic_energy_j"],
    }


def main():
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    print("=" * 65)
    print("  MONTE CARLO — Samara PQ (sem RocketPy)")
    print("=" * 65)
    print(f"  Iterações:          {args.n}")
    print(f"  Seed:               {args.seed}")
    print(f"  DXF:                {args.dxf}")
    print(f"  Altitude inicial:   {args.altitude} m")
    print(f"  Asas:               {args.n_wings}")
    print("-" * 65)
    print("  Parâmetros variáveis:")
    for name, mean, std in [
        ("Massa [kg]", args.mass_mean, args.mass_std),
        ("β [graus]", args.beta_mean, args.beta_std),
        ("Cd0", args.cd0_mean, args.cd0_std),
        ("f_factor", args.f_factor_mean, args.f_factor_std),
        ("ρ [kg/m³]", args.rho_mean, args.rho_std),
    ]:
        if std > 0:
            print(f"    {name:<20} {mean} ± {std}")
        else:
            print(f"    {name:<20} {mean} (fixo)")
    print("=" * 65)

    # Wing base (parâmetros fixos para clonagem)
    wing_base = PocketQubeSamaraWing(
        dxf_path=args.dxf,
        n_wings=args.n_wings,
        mass=args.mass_mean,
        f_factor=args.f_factor_mean,
        cd0=args.cd0_mean,
        rho=args.rho_mean,
        beta_deg=args.beta_mean,
    )

    vary = {
        "mass_mean": args.mass_mean,
        "mass_std": args.mass_std,
        "beta_mean": args.beta_mean,
        "beta_std": args.beta_std,
        "cd0_mean": args.cd0_mean,
        "cd0_std": args.cd0_std,
        "f_factor_mean": args.f_factor_mean,
        "f_factor_std": args.f_factor_std,
        "rho_mean": args.rho_mean,
        "rho_std": args.rho_std,
    }

    args_dict = {
        "theta_deg": args.theta_deg,
        "theta_dot": args.theta_dot,
        "phi_dot": args.phi_dot,
        "v0": args.v0,
        "altitude": args.altitude,
        "t_max": args.t_max,
        "max_step": args.max_step,
    }

    # Resultados
    results = []
    for i in range(args.n):
        r = run_single(wing_base, args_dict, rng, vary)
        results.append(r)

        if args.verbose and (i + 1) % 50 == 0:
            print(f"  Progresso: {i + 1}/{args.n}")

    # Converte para arrays
    fields = [
        "t_impact",
        "v_impact",
        "spin_rpm",
        "theta_eq_deg",
        "ke_impact",
    ]
    arr = {k: np.array([r[k] for r in results]) for k in fields}
    input_fields = ["mass_kg", "beta_deg", "cd0", "f_factor", "rho"]

    # Estatísticas
    print("\n" + "=" * 65)
    print("  RESUMO ESTATÍSTICO")
    print("=" * 65)
    for k in fields:
        print(
            f"  {k:<20} "
            f"{np.mean(arr[k]):>8.2f} ± {np.std(arr[k]):>6.2f}  "
            f"[P5={np.percentile(arr[k], 5):>7.2f}, "
            f"P95={np.percentile(arr[k], 95):>7.2f}]"
        )

    # LASC window compliance
    v = arr["v_impact"]
    lasc_pass = float(np.mean((v >= 20.0) & (v <= 45.0)))
    print(f"  {'LASC pass rate':<20} {lasc_pass * 100:>6.1f}%")
    print("=" * 65)

    # Exportar CSV
    if args.export:
        path = Path(args.export)
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = input_fields + fields
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(fieldnames)
            for r in results:
                w.writerow([r[k] for k in fieldnames])
        print(f"  Resultados exportados: {path}")


if __name__ == "__main__":
    main()
