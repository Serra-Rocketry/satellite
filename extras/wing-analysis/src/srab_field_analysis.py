#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRAB Field Test Analyzer — Serra Rocketry / Missão Helike
=========================================================
Analisa CSVs de telemetria do satélite (firmware v2), detecta fases de voo
automaticamente e gera relatório + gráficos.

Uso:
    python srab_field_analysis.py DADOS_020.csv
    python srab_field_analysis.py DADOS_020.csv --sim samara_pq_trajectory.csv
    python srab_field_analysis.py DADOS_020.csv --out resultados/
    python srab_field_analysis.py DADOS_020.csv --vz-source baro     # padrão
    python srab_field_analysis.py DADOS_020.csv --vz-source imu      # integra acelerômetro

Colunas esperadas no CSV (firmware v2):
    millis, ax_ms2, ay_ms2, az_ms2,
    gx_rads, gy_rads, gz_rads,
    pressao_Pa, altura_m, vz_ms, mag_giroscopia_rads
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
PHASE_COLORS = {
    "static": "#AAAAAA",
    "ascent": "#378ADD",
    "apogee": "#EF9F27",
    "descent": "#1D9E75",
    "landed": "#E24B4A",
}

# Limiares de detecção de fase
VZ_ASCENT_THRESHOLD = 0.3  # m/s — acima disso = subindo
VZ_DESCENT_THRESHOLD = -0.3  # m/s — abaixo disso = descendo
MIN_PHASE_DURATION = 1.0  # s   — fase precisa durar ao menos 1s para ser válida
SPIN_AXIS = "mag"  # "gz" = só eixo Z, "mag" = magnitude total


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
def load_telemetry(path: Path) -> dict:
    """Carrega CSV de telemetria e retorna arrays numpy por coluna."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({k: float(v) for k, v in row.items()})
            except ValueError:
                continue

    if not rows:
        sys.exit(f"Erro: nenhuma linha válida em {path}")

    t0 = rows[0]["millis"]
    return {
        "t": np.array([(r["millis"] - t0) / 1000.0 for r in rows]),
        "alt": np.array([r["altura_m"] for r in rows]),
        "vz": np.array([r["vz_ms"] for r in rows]),
        "ax": np.array([r["ax_ms2"] for r in rows]),
        "ay": np.array([r["ay_ms2"] for r in rows]),
        "az": np.array([r["az_ms2"] for r in rows]),
        "gx": np.array([r["gx_rads"] for r in rows]),
        "gy": np.array([r["gy_rads"] for r in rows]),
        "gz": np.array([r["gz_rads"] for r in rows]),
        "mag": np.array([r["mag_giroscopia_rads"] for r in rows]),
        "p": np.array([r["pressao_Pa"] for r in rows]),
        "n": len(rows),
        "freq": len(rows) / max((rows[-1]["millis"] - t0) / 1000.0, 1e-3),
        "file": path.name,
    }


def load_simulation(path: Path) -> dict | None:
    """Carrega CSV de trajetória simulada (gerado pelo samara_pq_simulation.py)."""
    if path is None or not path.exists():
        return None
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: float(v) for k, v in row.items()})
    return {
        "t": np.array([r["t_s"] for r in rows]),
        "alt": np.array([r["altitude_m"] for r in rows]),
        "v0": np.array([r["v0_ms"] for r in rows]),
        "spin": np.array([r["spin_rpm"] for r in rows]),
        "theta": np.array([r["theta_deg"] for r in rows]),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PHASE DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def detect_phases(data: dict) -> list[dict]:
    """
    Detecta fases de voo automaticamente com base em vz e altitude.

    Fases possíveis: static → ascent → apogee → descent → landed

    Retorna lista de dicts:
        [{"name": str, "t_start": float, "t_end": float,
          "i_start": int, "i_end": int}]
    """
    t = data["t"]
    vz = data["vz"]
    alt = data["alt"]
    n = data["n"]

    # Suavizar vz para detecção (janela 5 amostras)
    kernel = np.ones(5) / 5
    vz_smooth = np.convolve(vz, kernel, mode="same")

    phases = []
    current = "static"
    t_start = t[0]
    i_start = 0

    def close_phase(i_end, next_phase):
        nonlocal current, t_start, i_start
        dur = t[i_end] - t_start
        if dur >= MIN_PHASE_DURATION:
            phases.append(
                {
                    "name": current,
                    "t_start": t_start,
                    "t_end": t[i_end],
                    "i_start": i_start,
                    "i_end": i_end,
                }
            )
        current = next_phase
        t_start = t[i_end]
        i_start = i_end

    for i in range(1, n):
        v = vz_smooth[i]
        if current == "static":
            if v > VZ_ASCENT_THRESHOLD:
                close_phase(i, "ascent")
        elif current == "ascent":
            if v < VZ_ASCENT_THRESHOLD * 0.5:
                close_phase(i, "apogee")
        elif current == "apogee":
            if v < VZ_DESCENT_THRESHOLD:
                close_phase(i, "descent")
            elif v > VZ_ASCENT_THRESHOLD:
                close_phase(i, "ascent")  # bounce / second launch
        elif current == "descent":
            # Landed: altitude estabilizou (std da última janela pequena)
            window = max(1, min(20, i))
            if i > window and np.std(alt[i - window : i]) < 0.05:
                close_phase(i, "landed")

    # Fechar última fase
    phases.append(
        {
            "name": current,
            "t_start": t_start,
            "t_end": t[-1],
            "i_start": i_start,
            "i_end": n - 1,
        }
    )

    return phases


# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────────────────
def compute_metrics(data: dict, phases: list[dict]) -> dict:
    """Extrai métricas por fase e globais."""
    t = data["t"]
    alt = data["alt"]
    vz = data["vz"]
    spin = data[SPIN_AXIS]
    rpm = np.abs(spin) * 60.0 / (2 * np.pi)
    ax, ay, az = data["ax"], data["ay"], data["az"]
    a_mag = np.sqrt(ax**2 + ay**2 + az**2)

    global_metrics = {
        "duration_s": float(t[-1] - t[0]),
        "freq_hz": float(data["freq"]),
        "n_samples": int(data["n"]),
        "alt_min_m": float(np.min(alt)),
        "alt_max_m": float(np.max(alt)),
        "delta_alt_m": float(np.max(alt) - np.min(alt)),
        "vz_min_ms": float(np.min(vz)),
        "vz_max_ms": float(np.max(vz)),
        "spin_max_rpm": float(np.max(rpm)),
        "spin_mean_rpm": float(np.mean(rpm)),
        "accel_max_ms2": float(np.max(a_mag)),
    }

    phase_metrics = {}
    for ph in phases:
        sl = slice(ph["i_start"], ph["i_end"] + 1)
        v = vz[sl]
        a = alt[sl]
        r = rpm[sl]
        phase_metrics[ph["name"]] = {
            "t_start": ph["t_start"],
            "t_end": ph["t_end"],
            "duration_s": ph["t_end"] - ph["t_start"],
            "alt_start_m": float(a[0]) if len(a) else 0,
            "alt_end_m": float(a[-1]) if len(a) else 0,
            "delta_alt_m": float(np.max(a) - np.min(a)) if len(a) else 0,
            "vz_mean_ms": float(np.mean(v)) if len(v) else 0,
            "vz_min_ms": float(np.min(v)) if len(v) else 0,
            "vz_max_ms": float(np.max(v)) if len(v) else 0,
            "spin_mean_rpm": float(np.mean(r)) if len(r) else 0,
            "spin_max_rpm": float(np.max(r)) if len(r) else 0,
        }

    return {"global": global_metrics, "phases": phase_metrics}


# ─────────────────────────────────────────────────────────────────────────────
# DERIVED CHANNELS
# ─────────────────────────────────────────────────────────────────────────────
def imu_vz(data: dict) -> np.ndarray:
    """Estima vz integrando az − g (apenas orientação vertical aproximada)."""
    t = data["t"]
    az = data["az"]
    g = 9.81
    dt = np.diff(t)
    az_mid = (az[:-1] + az[1:]) / 2
    acc = az_mid - g  # aceleração líquida (remove gravidade)
    vz_imu = np.concatenate([[0.0], np.cumsum(acc * dt)])
    # Remover drift lento com filtro HP
    from numpy.fft import fft, ifft, fftfreq

    N = len(vz_imu)
    fs = data["freq"]
    F = fft(vz_imu)
    freqs = fftfreq(N, 1.0 / fs)
    F[np.abs(freqs) < 0.05] = 0  # corte HP em 0.05 Hz
    return np.real(ifft(F))


def relative_altitude(data: dict) -> np.ndarray:
    """Altitude relativa ao valor mediano dos primeiros 5 segundos."""
    t = data["t"]
    alt = data["alt"]
    mask = t < (t[0] + 5.0)
    baseline = np.median(alt[mask]) if np.any(mask) else alt[0]
    return alt - baseline


# ─────────────────────────────────────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────────────────────────────────────
def shade_phases(ax, phases):
    """Adiciona bandas coloridas de fundo por fase."""
    for ph in phases:
        ax.axvspan(
            ph["t_start"],
            ph["t_end"],
            color=PHASE_COLORS.get(ph["name"], "#CCCCCC"),
            alpha=0.12,
            zorder=0,
        )


def add_phase_legend(ax, phases):
    handles = []
    seen = set()
    for ph in phases:
        if ph["name"] not in seen:
            handles.append(
                Patch(
                    facecolor=PHASE_COLORS.get(ph["name"], "#CCC"),
                    alpha=0.4,
                    label=ph["name"],
                )
            )
            seen.add(ph["name"])
    ax.legend(handles=handles, fontsize=8, loc="upper right")


def plot_dashboard(
    data: dict, phases: list, metrics: dict, sim: dict | None, out_path: Path
):
    """Gera dashboard 3×2 com altitude, vz, spin, aceleração e fases."""
    t = data["t"]
    alt = relative_altitude(data)
    vz = data["vz"]
    rpm = np.abs(data[SPIN_AXIS]) * 60.0 / (2 * np.pi)
    gz = data["gz"]
    a_mag = np.sqrt(data["ax"] ** 2 + data["ay"] ** 2 + data["az"] ** 2)
    p = data["p"]

    fig = plt.figure(figsize=(18, 11))
    fig.suptitle(
        f"SRAB Field Test Analysis — {data['file']}\n"
        f"{data['n']} samples  |  {data['freq']:.1f} Hz  |  "
        f"Δalt = {metrics['global']['delta_alt_m']:.2f} m  |  "
        f"spin_max = {metrics['global']['spin_max_rpm']:.1f} RPM",
        fontsize=13,
        fontweight="bold",
    )

    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.42, wspace=0.32)

    # ── [0,0] Altitude relativa ────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])
    shade_phases(ax, phases)
    ax.plot(t, alt, color="#378ADD", lw=1.5, label="Altitude rel. (m)")
    if sim is not None:
        # Alinhar simulação no apogeu
        i_peak = np.argmax(alt)
        t_peak = t[i_peak]
        ax.plot(
            sim["t"] + t_peak,
            sim["alt"] - sim["alt"][0],
            color="#378ADD",
            lw=1.2,
            ls="--",
            alpha=0.55,
            label="Sim.",
        )
    ax.axhline(0, color="gray", lw=0.8, ls=":", alpha=0.5)
    ax.set_ylabel("Altitude rel. (m)")
    ax.set_title("Altitude — relativa ao solo")
    ax.grid(True, alpha=0.25)
    add_phase_legend(ax, phases)

    # ── [0,1] Velocidade vertical (barômetro) ──────────────────
    ax = fig.add_subplot(gs[0, 1])
    shade_phases(ax, phases)
    ax.plot(t, vz, color="#E24B4A", lw=1.2, alpha=0.7, label="vz baro (m/s)")
    ax.axhline(0, color="gray", lw=0.8, ls=":", alpha=0.5)
    ax.axhline(-20, color="orange", lw=1, ls="--", alpha=0.7, label="Limite LASC mín.")
    ax.axhline(-45, color="red", lw=1, ls="--", alpha=0.7, label="Limite LASC máx.")
    if sim is not None:
        i_peak = np.argmax(alt)
        t_peak = t[i_peak]
        ax.plot(
            sim["t"] + t_peak,
            sim["v0"],
            color="#E24B4A",
            lw=1.2,
            ls="--",
            alpha=0.55,
            label="Sim. v₀",
        )
    ax.set_ylabel("vz (m/s)")
    ax.set_title("Velocidade Vertical — barômetro")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(True, alpha=0.25)

    # ── [1,0] Spin — RPM ──────────────────────────────────────
    ax = fig.add_subplot(gs[1, 0])
    shade_phases(ax, phases)
    ax.plot(t, rpm, color="#1D9E75", lw=1.5, label="Spin total (RPM)")
    ax.plot(
        t,
        np.abs(gz) * 60 / (2 * np.pi),
        color="#1D9E75",
        lw=1,
        ls="--",
        alpha=0.55,
        label="|gz| (RPM)",
    )
    if sim is not None:
        i_peak = np.argmax(alt)
        t_peak = t[i_peak]
        ax.plot(
            sim["t"] + t_peak,
            sim["spin"],
            color="#1D9E75",
            lw=1.2,
            ls=":",
            alpha=0.55,
            label="Sim. spin",
        )
    ax.set_ylabel("RPM")
    ax.set_title("Spin de Autorrotação")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.25)

    # ── [1,1] Aceleração total ────────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    shade_phases(ax, phases)
    ax.plot(t, a_mag, color="#8e44ad", lw=1.2, label="|a| total (m/s²)")
    ax.plot(
        t, data["az"], color="#8e44ad", lw=1, ls="--", alpha=0.55, label="az (m/s²)"
    )
    ax.axhline(9.81, color="gray", lw=0.8, ls=":", alpha=0.5, label="g")
    ax.set_ylabel("Aceleração (m/s²)")
    ax.set_title("Aceleração — IMU")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.25)

    # ── [2,0] Pressão ──────────────────────────────────────────
    ax = fig.add_subplot(gs[2, 0])
    shade_phases(ax, phases)
    ax.plot(t, p / 100, color="#BA7517", lw=1.2)
    ax.set_ylabel("Pressão (hPa)")
    ax.set_xlabel("Tempo (s)")
    ax.set_title("Pressão Barométrica")
    ax.grid(True, alpha=0.25)

    # ── [2,1] Tabela de métricas por fase ─────────────────────
    ax = fig.add_subplot(gs[2, 1])
    ax.axis("off")
    rows_table = [["Fase", "Dur (s)", "Δalt (m)", "vz_med", "spin_max"]]
    for name, m in metrics["phases"].items():
        rows_table.append(
            [
                name,
                f"{m['duration_s']:.1f}",
                f"{m['delta_alt_m']:.2f}",
                f"{m['vz_mean_ms']:.2f}",
                f"{m['spin_max_rpm']:.1f} RPM",
            ]
        )
    tbl = ax.table(
        cellText=rows_table[1:], colLabels=rows_table[0], loc="center", cellLoc="center"
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.0, 1.6)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor("#1A4E8A")
            cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#F2F4F7")
        cell.set_edgecolor("#CCCCCC")
    ax.set_title("Métricas por Fase", fontsize=10, fontweight="bold", pad=8)

    # Adicionar marcadores de fase em todos os subplots
    for ax_i in fig.get_axes():
        if not ax_i.get_title().startswith("Métricas"):
            for ph in phases:
                ax_i.axvline(
                    ph["t_start"],
                    color=PHASE_COLORS.get(ph["name"], "#999"),
                    lw=0.8,
                    ls="-",
                    alpha=0.5,
                )

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Dashboard salvo: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# TEXT REPORT
# ─────────────────────────────────────────────────────────────────────────────
def print_report(data: dict, phases: list, metrics: dict, sim: dict | None):
    """Imprime relatório formatado no terminal."""
    g = metrics["global"]
    ph = metrics["phases"]
    sep = "=" * 68

    print(f"\n{sep}")
    print(f"  SRAB FIELD TEST REPORT — {data['file']}")
    print(sep)
    print(f"  Duração total:    {g['duration_s']:.1f} s")
    print(f"  Amostras:         {g['n_samples']}  ({g['freq_hz']:.1f} Hz)")
    print(
        f"  Δ altitude:       {g['delta_alt_m']:.2f} m  "
        f"[{g['alt_min_m']:.2f} → {g['alt_max_m']:.2f} m abs]"
    )
    print(f"  vz range:         {g['vz_min_ms']:.3f} → {g['vz_max_ms']:.3f} m/s")
    print(f"  Spin máx:         {g['spin_max_rpm']:.1f} RPM")
    print(f"  |a| máx:          {g['accel_max_ms2']:.2f} m/s²")
    print()

    print(f"  Fases detectadas ({len(phases)}):")
    for ph_data in phases:
        name = ph_data["name"]
        m = ph.get(name, {})
        print(
            f"    [{name:8s}]  "
            f"{ph_data['t_start']:6.1f}s → {ph_data['t_end']:6.1f}s  "
            f"({ph_data['t_end'] - ph_data['t_start']:.1f}s)  "
            f"spin_max={m.get('spin_max_rpm', 0):.1f} RPM  "
            f"vz_med={m.get('vz_mean_ms', 0):.2f} m/s"
        )

    # Qual fase de descida existe?
    desc = ph.get("descent")
    if desc:
        print()
        print("  ── Fase de Descida ─────────────────────────────────────────")
        print(f"  Duração:          {desc['duration_s']:.1f} s")
        print(f"  Δ altitude:       {desc['delta_alt_m']:.2f} m")
        print(f"  vz médio:         {desc['vz_mean_ms']:.3f} m/s")
        print(f"  Spin médio:       {desc['spin_mean_rpm']:.1f} RPM")
        print(f"  Spin máx:         {desc['spin_max_rpm']:.1f} RPM")

        # Comparação com limites LASC
        vz_desc = abs(desc["vz_mean_ms"])
        print()
        print("  ── Comparação LASC ─────────────────────────────────────────")
        lasc_ok = 20.0 <= vz_desc <= 45.0
        print(f"  |vz| médio descida: {vz_desc:.2f} m/s")
        print(
            f"  Janela LASC:        20–45 m/s  →  {'✅ dentro' if lasc_ok else '⚠️  fora'}"
        )

        if sim is not None:
            # Velocidade terminal simulada (último quinto da trajetória)
            n5 = max(1, len(sim["v0"]) // 5)
            vt_sim = float(np.median(np.abs(sim["v0"][-n5:])))
            print(f"  v_terminal sim:     {vt_sim:.2f} m/s")
            err = abs(vz_desc - vt_sim)
            print(f"  Desvio baro vs sim: {err:.2f} m/s")
    else:
        print()
        print("  ⚠️  Fase de descida não detectada nos dados.")
        print("     O teste pode ter sido em solo ou com altitude insuficiente.")

    print(f"\n{sep}\n")


# ─────────────────────────────────────────────────────────────────────────────
# SAVE JSON
# ─────────────────────────────────────────────────────────────────────────────
def save_json(metrics: dict, phases: list, out_path: Path):
    payload = {
        "global": metrics["global"],
        "phases": metrics["phases"],
        "phase_sequence": [p["name"] for p in phases],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"  JSON salvo:      {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    ap = argparse.ArgumentParser(
        description="SRAB Field Test Analyzer — Serra Rocketry / Helike",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("csv", type=Path, help="CSV de telemetria do satélite")
    ap.add_argument(
        "--sim",
        type=Path,
        default=None,
        metavar="CSV",
        help="CSV de trajetória simulada (samara_pq_trajectory.csv) para comparação",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        metavar="DIR",
        help="Diretório de saída (padrão: mesmo diretório do CSV)",
    )
    ap.add_argument(
        "--vz-source",
        choices=["baro", "imu"],
        default="baro",
        help="Fonte de vz: 'baro' = barômetro (padrão), 'imu' = integração az",
    )
    ap.add_argument(
        "--spin-axis",
        choices=["mag", "gz"],
        default="mag",
        help="Eixo de spin: 'mag' = magnitude total, 'gz' = apenas eixo Z",
    )
    return ap.parse_args()


def main():
    args = parse_args()

    # Diretório de saída
    out_dir = args.out or args.csv.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.csv.stem

    # Configurar eixo de spin global
    global SPIN_AXIS
    SPIN_AXIS = args.spin_axis

    print(f"\nCarregando: {args.csv}")
    data = load_telemetry(args.csv)
    print(
        f"  {data['n']} amostras  |  {data['freq']:.1f} Hz  |  "
        f"duração {data['t'][-1]:.1f}s"
    )

    # Substituir vz por integração IMU se solicitado
    if args.vz_source == "imu":
        print("  Usando vz derivado de integração IMU (az − g)...")
        data["vz"] = imu_vz(data)

    # Simulação (opcional)
    sim = load_simulation(args.sim)
    if sim is not None:
        print(f"  Simulação carregada: {args.sim.name}")

    # Detectar fases
    phases = detect_phases(data)
    print(f"\n  Fases detectadas: {[p['name'] for p in phases]}")

    # Métricas
    metrics = compute_metrics(data, phases)

    # Relatório no terminal
    print_report(data, phases, metrics, sim)

    # Dashboard
    dash_path = out_dir / f"{stem}_dashboard.png"
    plot_dashboard(data, phases, metrics, sim, dash_path)

    # JSON
    json_path = out_dir / f"{stem}_report.json"
    save_json(metrics, phases, json_path)

    print("Análise concluída.\n")


if __name__ == "__main__":
    main()
