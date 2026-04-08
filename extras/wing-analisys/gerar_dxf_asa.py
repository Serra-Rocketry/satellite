# -*- coding: utf-8 -*-
"""Gera DXF da asa samara Helike - 16cm de raio"""

import ezdxf
import numpy as np

# Parâmetros da asa
R = 160  # Raio em mm (16cm = 160mm)


def corda(r, r_max):
    """Corda da asa samara na posição r (mm).

    Formato: máximo em ~30% do raio, zero nas extremidades.
    Corda máxima ≈ 38mm para R=160mm
    """
    if r <= 0 or r >= r_max:
        return 0.0
    x = r / r_max
    # Máximo de 4x(1-x)² em x=1/3 é 16/27 ≈ 0.593
    # Fator 0.32: corda máx = 0.32 * 160 * 0.593 ≈ 30mm
    return r_max * 0.32 * 4 * x * (1 - x) ** 2


# Gerar pontos do contorno da asa
n_pontos = 200

# Lado direito do contorno (borda de ataque)
r_direito = np.linspace(0.5, R - 0.5, n_pontos)  # Evitar zero exato
contorno_direito = []
for r in r_direito:
    w = corda(r, R)
    contorno_direito.append((r, w / 2))  # Metade da corda

# Ponta da asa
contorno_ponta = [(R, 0)]

# Lado esquerdo do contorno (borda de fuga)
r_esquerdo = np.linspace(R - 0.5, 0.5, n_pontos)
contorno_esquerdo = []
for r in r_esquerdo:
    w = corda(r, R)
    contorno_esquerdo.append((r, -w / 2) if w > 0 else (r, 0))

# Base da asa (junta com o corpo)
contorno_base = [(0.5, 0)]

# Montar contorno completo
contorno = contorno_direito + contorno_ponta + contorno_esquerdo + contorno_base

# Criar documento DXF
doc = ezdxf.new("R2010")  # Formato compatível
msp = doc.modelspace()

# Adicionar contorno como polilinha fechada
polyline = msp.add_lwpolyline(contorno, close=True)
polyline.dxf.color = 7  # Branco/preto

# Adicionar linha central (referência visual discreta)
msp.add_line((0, 0), (R, 0), dxfattribs={"color": 8, "linetype": "CENTER"})  # Cinza

# Adicionar camada para o perfil
doc.layers.add("ASA_PRINCIPAL", color=7)
polyline.dxf.layer = "ASA_PRINCIPAL"

# Salvar arquivo
arquivo = "extras/asa_16cm.dxf"
doc.saveas(arquivo)

print(f"Arquivo DXF gerado: {arquivo}")
print(f"\nParâmetros da asa:")
print(f"  Raio: {R} mm")
print(f"  Corda máxima: {corda(R * 0.3, R):.1f} mm (em r={R * 0.3:.0f}mm)")
print(f"  Espessura: 0.6 mm (extrudar no SolidWorks)")
print(f"  Pontos no contorno: {len(contorno)}")

# Mostrar alguns valores-chave
print(f"\nValores de corda (mm):")
for r_pct in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    r_mm = R * r_pct
    c_mm = corda(r_mm, R)
    print(f"  r = {r_mm:5.1f} mm ({r_pct * 100:.0f}%): corda = {c_mm:5.1f} mm")

# Gerar também CSV para referência
with open("extras/asa_16cm_perfil.csv", "w") as f:
    f.write("r_mm,corda_mm\n")
    for r in np.linspace(1, R - 1, 100):
        f.write(f"{r:.2f},{corda(r, R):.4f}\n")

print(f"\nCSV do perfil: extras/asa_16cm_perfil.csv")
print(f"\nPara importar no SolidWorks:")
print(f"  1. File → Open → selecionar asa_16cm.dxf")
print(f"  2. Importar como esboço 2D")
print(f"  3. Extrudar com 0.6mm de espessura")
print(f"  4. A asa fica no plano XY, raio ao longo do eixo X")
