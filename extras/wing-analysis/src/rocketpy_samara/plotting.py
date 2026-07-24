# -*- coding: utf-8 -*-
"""Plotting utilities para trajetória SRAB completa (ascent + descent)
e dispersão de impacto Monte Carlo.

Uso básico:
    from rocketpy_samara.plotting import plot_ascent_descent_3d, plot_dispersion

    plot_ascent_descent_3d(flight, srab_sol)
    plot_dispersion(mc_results)
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (ativa projeção 3d)


def plot_ascent_descent_3d(flight, srab_sol, n=500, filename=None):
    """Trajetória 3D completa: subida (RocketPy) + descida (SRAB).

    Parameters
    ----------
    flight : rocketpy.Flight
        Flight object da subida do foguete (já simulado).
    srab_sol : SRABSolution
        Solução da descida SRAB.
    n : int
        Número de pontos para amostrar a trajetória de subida.
    filename : str, optional
        Caminho para salvar a figura. Se None, exibe na tela.
    """
    if flight is None:
        # Modo standalone — só descida SRAB (sem RocketPy)
        return _plot_srab_only(srab_sol, filename)

    t_apo = flight.apogee_time

    # --- Ascent: amostragem via Funções do RocketPy ---
    t_arr = np.linspace(0, t_apo, n)
    x_asc = np.array([flight.x(t) for t in t_arr])
    y_asc = np.array([flight.y(t) for t in t_arr])
    z_asc = np.array([flight.z(t) for t in t_arr])

    z_elev = flight.env.elevation

    # --- Descent ---
    z_desc = srab_sol.altitude + z_elev
    x_desc = srab_sol.x
    y_desc = srab_sol.y

    # --- Plot ---
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(x_asc, y_asc, z_asc, "b-", lw=1.5, label="Subida (RocketPy)")
    ax.plot(x_desc, y_desc, z_desc, "r-", lw=1.5, label="Descida (SRAB)")

    ax.scatter(
        flight.x(t_apo),
        flight.y(t_apo),
        flight.z(t_apo),
        c="g",
        s=60,
        marker="^",
        label="Apogeu",
        zorder=5,
    )
    ax.scatter(
        srab_sol.x_impact,
        srab_sol.y_impact,
        z_elev,
        c="k",
        s=60,
        marker="v",
        label="Impacto",
        zorder=5,
    )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Altitude (m)")
    ax.set_title("Trajetória Completa — Subida (RocketPy) + Descida (SRAB)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if filename:
        fig.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"  3D plot saved: {filename}")
    return fig


def _plot_srab_only(srab_sol, filename=None):
    """Plot 3D da descida SRAB (sem RocketPy)."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    z = srab_sol.altitude
    ax.plot(srab_sol.x, srab_sol.y, z, "r-", lw=1.5, label="Descida (SRAB)")

    ax.scatter(0, 0, z[0], c="g", s=60, marker="^", label="Liberação", zorder=5)
    ax.scatter(
        srab_sol.x_impact,
        srab_sol.y_impact,
        0,
        c="k",
        s=60,
        marker="v",
        label="Impacto",
        zorder=5,
    )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Altitude (m)")
    ax.set_title("Descida SRAB — Trajetória 3D")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if filename:
        fig.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"  3D plot saved: {filename}")
    return fig


def plot_dispersion(mc, filename=None):
    """Scatter plot dos pontos de impacto do Monte Carlo + elipse CEP.

    Parameters
    ----------
    mc : SRABMonteCarlo
        Objeto MC já executado (com ``mc.results`` populado).
    filename : str, optional
        Caminho para salvar a figura.
    """
    x = np.array(mc.results.get("x_impact", []))
    y = np.array(mc.results.get("y_impact", []))

    if len(x) == 0:
        print("  [AVISO] Nenhum resultado MC para plotar dispersão.")
        return

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

    # Scatter
    ax.scatter(x, y, alpha=0.5, s=20, c="crimson", label="Impactos MC")

    # Centro médio
    xm, ym = np.mean(x), np.mean(y)
    ax.scatter(xm, ym, c="k", s=80, marker="x", label="Centro médio")

    # Elipse CEP (1 sigma)
    if len(x) > 2:
        cov = np.cov(x, y)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))
        width, height = 2.0 * np.sqrt(eigenvalues)

        from matplotlib.patches import Ellipse

        ellipse = Ellipse(
            xy=(xm, ym),
            width=width,
            height=height,
            angle=angle,
            edgecolor="navy",
            fc="none",
            lw=1.5,
            linestyle="--",
            label=f"1σ elipse (CEP ≈ {np.median(np.sqrt(x**2 + y**2)):.1f} m)",
        )
        ax.add_patch(ellipse)

    # Formatação
    ax.set_xlabel("X impacto (m)")
    ax.set_ylabel("Y impacto (m)")
    ax.set_title("Dispersão de Impacto — Monte Carlo")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    if filename:
        fig.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"  Dispersion plot saved: {filename}")
    return fig


def plot_lrr_dashboard(srab_sol, filename=None):
    """LRR-style 2×2 dashboard (reimplementação leve do
    PocketQubeLRRVisualizer, mas consumindo SRABSolution).

    Painéis:
    [0,0] Altitude vs tempo
    [0,1] Velocidade vertical vs LASC window
    [1,0] Ângulo de conicidade θ
    [1,1] Spin φ̇ (RPM)
    """
    t = srab_sol.t
    alt = srab_sol.altitude
    v = abs(srab_sol.v0)
    theta_deg = np.degrees(srab_sol.theta)
    spin_rpm = np.abs(srab_sol.phi_dot) * 60.0 / (2.0 * np.pi)

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "LRR Certification Report — SRAB Descent", fontsize=14, fontweight="bold"
    )

    # [0,0] Altitude
    axs[0, 0].plot(t, alt, color="#1a6ea8", lw=2)
    axs[0, 0].set_title("Perfil de Descida — Altitude AGL")
    axs[0, 0].set_ylabel("Altitude (m)")
    axs[0, 0].set_xlabel("Tempo (s)")
    axs[0, 0].grid(True, alpha=0.3)

    # [0,1] Velocidade vertical
    axs[0, 1].plot(t, v, color="#333", lw=2, label="|v₀|")
    axs[0, 1].axhspan(20, 45, color="green", alpha=0.15, label="Janela LASC")
    axs[0, 1].axhline(45, color="red", ls="--", lw=1.2, label="Máx LASC (45)")
    axs[0, 1].axhline(20, color="orange", ls="--", lw=1.2, label="Mín LASC (20)")
    v_term = float(np.median(v[-len(v) // 5 :]))
    axs[0, 1].axhline(
        v_term, color="#1a6ea8", ls=":", lw=2, label=f"v_term ≈ {v_term:.1f} m/s"
    )
    axs[0, 1].set_title("Velocidade Vertical vs Janela LASC")
    axs[0, 1].set_ylabel("|v₀| (m/s)")
    axs[0, 1].set_xlabel("Tempo (s)")
    axs[0, 1].legend(fontsize=9)
    axs[0, 1].grid(True, alpha=0.3)

    # [1,0] Theta
    axs[1, 0].plot(t, theta_deg, color="#8e44ad", lw=2, label="θ")
    th_eq = float(np.median(theta_deg[-len(theta_deg) // 5 :]))
    axs[1, 0].axhline(
        th_eq, color="#8e44ad", ls=":", lw=1.5, label=f"θ_eq ≈ {th_eq:.1f}°"
    )
    axs[1, 0].set_title("Ângulo de Conicidade θ")
    axs[1, 0].set_ylabel("θ (graus)")
    axs[1, 0].set_xlabel("Tempo (s)")
    axs[1, 0].legend(fontsize=9)
    axs[1, 0].grid(True, alpha=0.3)

    # [1,1] Spin
    axs[1, 1].plot(t, spin_rpm, color="#27ae60", lw=2, label="φ̇")
    sp_eq = float(np.median(spin_rpm[-len(spin_rpm) // 5 :]))
    axs[1, 1].axhline(
        sp_eq, color="#27ae60", ls=":", lw=1.5, label=f"Spin_eq ≈ {sp_eq:.0f} RPM"
    )
    axs[1, 1].set_title("Spin de Autorrotação φ̇")
    axs[1, 1].set_ylabel("RPM")
    axs[1, 1].set_xlabel("Tempo (s)")
    axs[1, 1].legend(fontsize=9)
    axs[1, 1].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    if filename:
        fig.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"  LRR dashboard saved: {filename}")
    return fig


def plot_trajectory_map(srab_sol, lat, lon, filename=None, zoom=16):
    """Mapa interativo (satélite) da descida SRAB com folium.

    Parâmetros
    ----------
    srab_sol : SRABSolution
        Solução da descida SRAB.
    lat, lon : float
        Coordenadas geográficas do ponto de liberação (graus decimais).
    filename : str, optional
        Caminho para salvar o HTML. Se None, retorna objeto folium.Map.
    zoom : int
        Nível de zoom inicial (default 16).

    Retorna
    -------
    folium.Map
        Mapa interativo (retornado apenas se filename for None).
    """
    try:
        import folium as _folium
    except ImportError as exc:
        raise ImportError(
            "folium é necessário para plot_trajectory_map. "
            "Instale com: pip install folium"
        ) from exc

    # Converter x,y (metros offset) para lat/lng
    lat_rad = np.radians(lat)
    m_per_deg_lat = 111320.0
    m_per_deg_lon = 111320.0 * np.cos(lat_rad)

    x_corrigido = srab_sol.x - srab_sol.x[0]  # Força o primeiro ponto a ser 0
    y_corrigido = srab_sol.y - srab_sol.y[0]  # Força o primeiro ponto a ser 0

    lats = lat + y_corrigido / m_per_deg_lat
    lngs = lon + x_corrigido / m_per_deg_lon

    # lats = lat + srab_sol.y / m_per_deg_lat
    # lngs = lon + srab_sol.x / m_per_deg_lon

    # Amostrar trajetória
    step = max(1, len(lats) // 200)
    xs = lats[::step]
    ys = lngs[::step]
    zs = srab_sol.altitude[::step]
    max_z = zs.max() if zs.max() > 0 else 1

    # Mapa base ESRI World Imagery (satélite gratuita)
    m = _folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="ESRI World Imagery",
    )

    # Liberação
    _folium.Marker(
        [lat, lon],
        popup=(f"Deploy<br>"
               f"{srab_sol.altitude[0]:.0f} m<br>" 
               f"lat={lat:.6f}<br>" 
               f"lon={lon:.6f}"),
        icon=_folium.Icon(color="green", icon="cloud", prefix="fa"),
    ).add_to(m)

    # Impacto
    _folium.Marker(
        [lats[-1], lngs[-1]],
        popup=(
            f"Impacto<br>"
            f"lat={lats[-1]:.6f}<br>"  
            f"lon={lngs[-1]:.6f}<br>"
            f"v={srab_sol.v_impact:.2f} m/s"
        ),
        icon=_folium.Icon(color="red", icon="bullseye", prefix="fa"),
    ).add_to(m)

    # Trajetória com gradiente de altitude (verde→vermelho)
    points = list(zip(xs, ys))
    for i in range(len(points) - 1):
        alt_frac = zs[i] / max_z
        r = int(255 * (1 - alt_frac))
        g = int(255 * alt_frac)
        color = f"#{r:02x}{g:02x}00"
        _folium.PolyLine(
            [points[i], points[i + 1]], color=color, weight=3, opacity=0.85
        ).add_to(m)

    # Círculo 100 m no impacto
    _folium.Circle(
        [lats[-1], lngs[-1]],
        radius=100,
        color="red",
        fill=True,
        fill_opacity=0.12,
        popup="Zona 100 m",
    ).add_to(m)

    if filename:
        m.save(filename)
        print(f"  Map saved: {filename}")
        return None
    return m
