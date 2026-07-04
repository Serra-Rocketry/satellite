# SRAB — Fundamentos Teoricos

**Sistema de Recuperacao Autorrotativo Bioinspirado** para PocketQube 1P.
Documentacao dos principios fisicos e modelo matematico.

---

## 1. Conceito de Autorotacao

### O que e uma Samara?

Sementes de arvores como o bordo (_Acer rubrum_, _Fraxinus_) — "helicopteros"
naturais. Fruto seco com extensao achatada que atua como superficie
aerodinamica. A assimetria estrutural (massa concentrada na semente, superficie
expandida na asa) induz rotacao conica estavel que reduz a velocidade terminal
e maximiza a dispersao horizontal.

### Vortece de Bordo de Ataque (LEV)

Durante a rotacao, forma-se um vortece no bordo de ataque que reduz a pressao
sobre o extradorso, elevando a sustentacao efetiva de forma analoga ao voo de
insetos \citep{lentink2009, mcconnell2023, rezgui2020}.

### Aplicacao no PocketQube

Arquitetura passiva e mecanicamente simples: substitui a semente pelo
nanossatelite e as asas da samara por superficies aerodinamicas impressas em
PETG. A plataforma alvo e o PocketQube 1P (50x50x50 mm, massa maxima 250 g).

---

## 2. Modelo Matematico (4ª Ordem)

### Hipotese e Simplificacoes

O sistema e modelado em referencial fixo no corpo da asa (x3, y3, z3):

1. **Deslocamento lateral do CM**: desprezivel -> angulo de rolagem ψ ≈ 0
2. **Esbeltez extrema da lamina**: Ix3x3 = 0, Iz3z3 = Iy3y3
3. **Distribuicao nao uniforme de massa**: fator fenomenologico _f_

### Vetor de Estado

θ = angulo de conicidade | θ̇ = taxa de arfagem | φ̇ = taxa de guinada (rotacao) | v0 = velocidade vertical

### Equacoes Governantes

```
θ̇   = θ̇                                          (cinematica)
θ̈   = −My3/Iy3y3 − φ̇² sinθ cosθ                  (arfagem)
φ̈   = Mz3/(Iy3y3 cosθ) + 2 φ̇ θ̇ tanθ             (guinada)
v̇0  = −g + Fz3 cosθ / m                           (vertical)
```

O termo φ̇² sinθ cosθ mostra que a rotacao gera momento de restauracao conico;
2 φ̇ θ̇ tanθ representa o acoplamento giroscopico.

### Blade Element Theory (BET)

Forcas e momentos aerodinamicos sao integrados numericamente ao longo da
envergadura:

```
Fz3 = ∫ [½ ρ w(r) ||U∞||² (cosα CL + sinα CD)] dr
My3 = ∫ [−r · dFz3] dr
Mz3 = ∫ [ r · dFy3] dr
```

### Coeficientes Aerodinamicos

- **Sustentacao**: CL(α) = 2π sinα (aerofolio fino), saturado em CL_max = 1.5
- **Arrasto**: CD(α) = CL sinα + CD0 (com ganho LEV implicito em CD0)

### Estado Estacionario

Quando θ̈ = φ̈ = v̇0 = 0, o sistema atinge regime terminal com velocidade
constante e segura.

---

## 3. Modelo 6DOF (Extensao)

As equacoes de Newton-Euler completas (sem assumir ψ ≈ 0 ou Ix3x3 = 0):

```
Ix3x3 ω̇x3 + (Iz3z3 − Iy3y3) ωy3 ωz3 = Mx3
Iy3y3 ω̇y3 + (Ix3x3 − Iz3z3) ωx3 ωz3 = My3
Iz3z3 ω̇z3 + (Iy3y3 − Ix3x3) ωx3 ωy3 = Mz3

m v̇0 = −mg + Fx3 sinθ + Fy3 sinψ cosθ + Fz3 cosψ cosθ
```

Necessario quando o sistema precisar prever efeitos de ventos laterais ou
cisalhamento em quedas de 1000+ m.

---

## 4. Referencias

- LASC. _Satellite Challenge Standards Manual_. Ed. 7, Rev. 1. 2026.
- Lentink et al. Leading-Edge Vortices Elevate Lift of Autorotating Plant Seeds. _Science_, 2009.
- McConnell & Das. Control Oriented Modeling... of an Autorotating Samara. _JDSMC_, 2023.
- Rezgui et al. Model for Sectional LEV Lift... _AIAA Journal_, 2020.
- Limacher. _PhD Thesis_. UCalgary, 2015.
- European Commission. Whirling maple seeds create vortex to fly high and far. _CORDIS_, 2009.
