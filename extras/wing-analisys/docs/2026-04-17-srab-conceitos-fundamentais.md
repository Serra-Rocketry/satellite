---
title: SRAB - Conceitos Fundamentais de Autorotação de Samara
date: 2026-04-17
tags: [helike, samara, autorotação, srab, aerodinâmica, ode, ode-4th-order, lev, blade-element-theory]
status: active
type: técnico
priority: high
related:
  - "[[2026-04-17-helike-historico-testes]]"
  - "[[2026-04-17-analise-simulacao-helike]]"
  - "[[satellite]]"
---

# SRAB - Sistema de Recuperação Autorrotativo Bioinspirado

## Visão Geral

Documentação técnica sobre o **Sistema de Recuperação Autorrotativo Bioinspirado (SRAB)** - proposta de design para recuperação de satélites PocketQube 1P utilizando princípios de autorotação de sementes de samara (maple seeds).

---

## 1. Conceito de Autorotação para Leigo

### O que é uma Samara?

Samaras são sementes de árvores como o bordo (maple), frequentemente descritas como **"helicópteros" naturais**. Em termos funcionais, trata-se de um **fruto seco com extensão achatada que atua como superfície aerodinâmica**.

### Por que gira?

O grande diferencial estrutural que torna esse design viável é a sua **assimetria proposital**:

- O **peso principal** (centro de massa) fica concentrado em **uma das extremidades**
- A **área que interage com o ar** (sustentação) fica no **meio da asa**

Quando essa estrutura é liberada em queda:

1. A diferença entre onde o peso está puxando e onde o ar está empurrando
2. Força a semente a começar a **girar de forma contínua** em torno da sua ponta mais pesada
3. Desenha uma **trajetória em formato de cone** enquanto desce

### O Vórtice de Bordo de Ataque (LEV)

Durante esse giro constante, a asa aciona o principal trunfo de engenharia: um fenômeno chamado de **"Vórtice de Bordo de Ataque"** (Leading-Edge Vortex - LEV).

Em termos leigos:

- A asa cortando o ar em **alta velocidade de rotação** cria um **pequeno túnel de ar em espiral** (um redemoinho horizontal) grudado na sua borda dianteira
- Esse redemoinho **altera o ambiente ao redor do objeto**, diminuindo drasticamente a pressão do ar na parte superior da asa
- O ar empurra a estrutura para cima, **combatendo a gravidade**
- Resultado: **dobra a capacidade de sustentação** do objeto em comparação com uma asa comum que cai sem girar

### Aplicação no PocketQube

A proposta é adotar exatamente esse princípio biológico em nossos veículos:

- **Arquitetura passiva e mecanicamente simples**
- **Elimina** dependência de mecanismos ativos adicionais para desaceleração
- **Utiliza o giro natural** para reduzir velocidade de queda
- Opera com base em equilíbrio aerodinâmico durante a descida

---

## 2. Conceito de Autorotação para Engenheiro

### Fundamentação Técnica

A autorrotação é um fenômeno de **voo aerodinâmico passivo** empregado por sementes com asas (samaras) para reduzir velocidade de descida e aumentar dispersão.

#### Mecanismo Físico

Quando a semente é solta:

1. Centro de massa **deslocado para uma extremidade**
2. Centro de sustentação **posicionado ao longo da asa**
3. Combinam-se sob ação das forças aerodinâmicas
4. Iniciam **rotação contínua** ao redor do centro de massa
5. Trajetória não planar, com **cone** ao redor do eixo vertical

#### Vantagem Fluidodinâmica

A principal vantagem gerada por essa rotação geométrica é a indução de um **Vórtice de Bordo de Ataque (LEV)**:

- Estrutura vortical ao longo do bordo de ataque
- Propriedade: **diminui drasticamente a pressão** na superfície superior do aerofólio
- Zona de baixa pressão **puxa o fluxo de ar para cima**
- **Opõe-se à gravidade**
- Pode elevar significativamente a sustentação efetiva em comparação com asa não rotacionante

### Modelo Matemático Simplificado (4ª Ordem)

#### Hipóteses e Simplificações

O sistema é modelado em referencial fixo no corpo da asa ($x_3, y_3, z_3$). Restrições de projeto:

1. **Deslocamento lateral do centro de massa**: desprezível
   - Ângulo de rolagem (roll, $\psi$) estabiliza em zero: $\psi \approx 0$

2. **Esbeltez extrema da lâmina**:
   - Momento de inércia transversal praticamente nulo: $I_{x3x3} = 0$
   - Inércia em guinada equivale à inércia em arfagem: $I_{z3z3} = I_{y3y3}$

3. **Distribuição não uniforme de massa**:
   - Compensada via fator de sintonia fenomenológico $f$
   - $I_{y3y3} = \frac{1}{3}fmR^2$

#### Vetor de Estado (4 variáveis)

O comportamento da autorrotação é descrito por sistema de **4 Equações Diferenciais Ordinárias (EDOs)** com estado definido por:

- $\theta$ = ângulo de arfagem/conicidade
- $\dot{\theta}$ = taxa de arfagem
- $\dot{\phi}$ = taxa de guinada (rotação do rotor)
- $v_0$ = velocidade vertical de descida

#### Equações Governantes de Movimento

1. **Taxa Cinematica de Arfagem:**
   $$\frac{d\theta}{dt} = \dot{\theta}$$

2. **Dinâmica de Conicidade (Aceleração de Arfagem):**
   $$\ddot{\theta} = \frac{-M_{y3}}{I_{y3y3}} - \dot{\phi}^2 \sin\theta \cos\theta$$

3. **Dinâmica de Autorrotação (Aceleração de Guinada):**
   $$\ddot{\phi} = \frac{M_{z3}}{I_{y3y3} \cos\theta} + 2\dot{\phi}\dot{\theta} \tan\theta$$

4. **Aceleração Vertical de Descida:**
   $$\dot{v}_0 = -g + \frac{F_{z3} \cos\theta}{m}$$

Onde:

- $m$ = massa do satélite
- $g$ = aceleração da gravidade
- $M_{y3}, M_{z3}$ = momentos aerodinâmicos
- $F_{z3}$ = força aerodinâmica vertical

### Modelagem de Cargas Aerodinâmicas via Blade Element Theory

#### Teoria do Elemento de Pá

Para obter as variáveis de força vertical ($F_{z3}$) e momentos ($M_{y3}, M_{z3}$), empregamos a **Teoria do Elemento de Pá (Blade Element Theory)**, integrando numericamente as cargas diferenciais:

- Base da asa: $r_0$
- Extremidade: $r_f$ (descontando perdas de ponta)

#### Forças Bidimensionais por Elemento

Para cada seção infinitesimal $dr$ sob vento relativo $||U_\infty||$ e ângulo de ataque $\alpha$:

$$dF_{y3} = \frac{1}{2} \rho w(r) ||U_\infty||^2 (\sin\alpha C_L(\alpha) - \cos\alpha C_D(\alpha)) \, dr$$

$$dF_{z3} = \frac{1}{2} \rho w(r) ||U_\infty||^2 (\cos\alpha C_L(\alpha) + \sin\alpha C_D(\alpha)) \, dr$$

Onde:

- $\rho$ = densidade do ar (1.225 kg/m³)
- $w(r)$ = largura da corda no raio $r$
- $C_L(\alpha)$ = coeficiente de sustentação
- $C_D(\alpha)$ = coeficiente de arrasto

#### Modelagem de Coeficientes Aerodinâmicos

Estratégia para contornar a não-modelagem explícita do vórtice 3D do LEV:

**Sustentação (aerofólio fino):**
$$C_L(\alpha) = 2\pi \sin\alpha$$

**Arrasto (com parâmetro fenomenológico):**
$$C_D(\alpha) = C_L(\alpha) \sin\alpha + C_{D_0}$$

O fator $C_{D_0}$ (parâmetro ajustável) representa simultaneamente:

- Arrasto do perfil aerodinâmico
- Ganho extremo de sustentação/arrasto induzido pelo vórtice biológico

### Estado Estacionário (Regime Terminal)

A autorrotação em regime de **estado estacionário** (equilíbrio passivo da queda) ocorre quando:

$$\ddot{\theta} = 0, \quad \ddot{\phi} = 0, \quad \dot{v}_0 = 0$$

Nesse ponto:

- Competição entre força gravitacional e integrações de $F_{z3}$ atinge **balanço exato**
- Veículo passa a descer com **velocidade terminal segura e constante**

---

## 3. Equações Completas em 6 Graus de Liberdade (6DOF)

### Sistema Newton-Euler Completo

Para expandir a arquitetura de simulação além do modelo simplificado de 4ª ordem, modelamos a dinâmica completa em seis graus de liberdade sem assumir que ângulo de rolagem ou inércia longitudinal sejam nulos.

#### Dinâmica Rotacional (Tensor de Equações)

A dinâmica rotacional completa do corpo do satélite, em referencial fixo no corpo da asa ($x_3, y_3, z_3$):

$$I_{x3x3} \dot{\omega}_{x3} + (I_{z3z3} - I_{y3y3})\omega_{y3}\omega_{z3} = M_{x3}$$

$$I_{y3y3} \dot{\omega}_{y3} + (I_{x3x3} - I_{z3z3})\omega_{x3}\omega_{z3} = M_{y3}$$

$$I_{z3z3} \dot{\omega}_{z3} + (I_{y3y3} - I_{x3x3})\omega_{x3}\omega_{y3} = M_{z3}$$

#### Movimento de Translação Completo

Equação que avalia balanço de aceleração no eixo vertical, não desprezando componentes de força causadas por rolagem ($\psi$) e vento ao longo da envergadura ($F_{x3}$):

$$m \dot{v}_0 = -mg + F_{x3} \sin\theta + F_{y3} \sin\psi \cos\theta + F_{z3} \cos\psi \cos\theta$$

#### Transformação de Ângulos de Euler

Para acoplar momentos e forças aerodinâmicas com taxas de rotação globais, sistema exige equação cinemática de transformação. **Velocidade angular vetorial resultante:**

$$\omega = (\dot{\psi} + \dot{\phi}\sin\theta)\hat{i} + (\dot{\phi}\cos\theta\sin\psi - \dot{\theta}\cos\psi)\hat{j} + (\dot{\phi}\cos\theta\cos\psi + \dot{\theta}\sin\psi)\hat{k}$$

#### Cinemática Aerodinâmica - Velocidade do Elemento de Pá

Para calcular sustentação no Elemento de Pá, precisamos da velocidade de translação absoluta de qualquer ponto $P$ no raio da asa:

$$v_P = v_O + (\omega \times r\hat{i})$$

Expandido:
$$v_P = v_o\sin\theta\hat{i} + [v_o\cos\theta\cos\psi - r(\dot{\phi}\cos\theta\sin\psi - \dot{\theta}\cos\psi)]\hat{k}$$
$$+ [v_o\cos\theta\sin\psi + r(\dot{\phi}\cos\theta\cos\psi + \dot{\theta}\sin\psi)]\hat{j}$$

Velocidade do vento relativo atinge o perfil como:
$$v_{w/P} = -v_P$$

**Nota de projeto:** Na nossa redução de modelo simplificado, forçamos $F_{x3} \approx 0$ e embutimos fator paramétrico $C_{D_0}$ para contabilizar anomalias desse vento.

#### Estado Estacionário com Rolagem Arbitrária (6DOF)

Se permitirmos otimizador explorar rolagem natural do material flexível impresso em 3D, acelerações de perturbação cessam:

$$\ddot{\theta} = \ddot{\phi} = \dot{v}_0 = 0$$

E o voo terminal passivo se ancora nas **raízes de estabilidade**:

$$\dot{\phi}^2 \sin\theta \cos\theta \cos\psi = -M_{y3}/I_{y3y3}$$

$$\dot{\phi}^2 \sin\theta \cos\theta \sin\psi = M_{z3}/I_{y3y3}$$

$$mg = F_{y3}\sin\psi\cos\theta + F_{z3}\cos\psi\cos\theta$$

### Extensão Futura

Essa cadeia de relações 3D compõe a infraestrutura analítica completa da mecânica de samaras. Se PocketQube necessitar futuramente prever efeitos de:

- Rajadas de ventos laterais
- Cisalhamento de asas flexíveis mudando ângulo $\psi$ gradualmente na queda de 1500m

Nossa proposta estenderá a classe `PocketQubeFlightDynamics` para resolver essas relações 6DOF explícitas no solver.

---

## 4. Revisão Integrada: Conceito Geral + Equações

### Síntese Executiva

A **autorrotação** é um fenômeno de voo aerodinâmico passivo onde:

1. **Geometria assimétrica** combina centro de massa deslocado com centro de sustentação distribuído
2. **Rotação contínua** ao redor do centro de massa desenha trajetória cônica
3. **Vórtice de Bordo de Ataque (LEV)** reduz pressão no extradorso, dobrando sustentação
4. **Estado terminal seguro** alcançado quando forças se equilibram

### Modelo Matemático Escolhido: 4ª Ordem

Por razões de **eficiência computacional vs. precisão**, escolhemos o modelo simplificado de **4ª ordem** com hipóteses:

- Rolagem negligenciável: $\psi \approx 0$
- Inércia longitudinal nula: $I_{x3x3} = 0$
- Inércia em guinada = inércia em arfagem: $I_{z3z3} = I_{y3y3}$

**Resultado**: Sistema compacto de 4 EDOs capturando dinâmica dominante sem overhead 6DOF.

### Equações Nucleares (4ª Ordem)

| Equação | Significado | Fórmula |
|---------|-----------|---------|
| Cinemática | Taxa de arfagem | $\dot{\theta} = d\theta/dt$ |
| Dinâmica Pitch | Aceleração de conicidade | $\ddot{\theta} = -M_{y3}/I_{y3y3} - \dot{\phi}^2\sin\theta\cos\theta$ |
| Dinâmica Yaw | Aceleração de rotação | $\ddot{\phi} = M_{z3}/(I_{y3y3}\cos\theta) + 2\dot{\phi}\dot{\theta}\tan\theta$ |
| Dinâmica Vertical | Aceleração de queda | $\dot{v}_0 = -g + F_{z3}\cos\theta/m$ |

### Extração de Forças: Blade Element Theory

Integração numérica de cargas aerodinâmicas do raio $r_0$ a $r_f$:

$$F = \int_{r_0}^{r_f} \frac{1}{2}\rho w(r)||U_\infty||^2 [C_L(\alpha), C_D(\alpha)] \, dr$$

Com modelagem de coeficientes:

- $C_L = 2\pi\sin\alpha$ (aerofólio fino)
- $C_D = C_L\sin\alpha + C_{D_0}$ (com ganho LEV implícito)

### Estabilidade e Condição Terminal

Autorrotação em estado estacionário quando:
$$\ddot{\theta} = \ddot{\phi} = \dot{v}_0 = 0$$

Nesse regime:

- Gravitação = Sustentação
- Torque pitch = 0
- Torque yaw = 0
- **Velocidade de descida constante e segura**

---

## 5. Referências Bibliográficas

Referencial teórico que embasa a proposta SRAB, formatado conforme normas ABNT para Mission Report e Launch Readiness Review (LRR):

### Referências Técnicas

EUROPEAN COMMISSION. Whirling maple seeds create vortex to fly high and far. **CORDIS - European Union**, 1 jul. 2009.

MCCONNELL, J.; DAS, T. Control Oriented Modeling, Experimentation, and Stability Analysis of an Autorotating Samara. **Journal of Dynamic Systems, Measurement, and Control**, v. 145, n. 6, p. 061004, 15 maio 2023. DOI: 10.1115/1.4062438.

PRISM. **Samara-Seed Aerodynamics**. Repositório institucional (acesso restrito).

RESEARCH INFORMATION. **Model for Sectional Leading-Edge Vortex Lift for the Prediction of Rotating Samara Seeds Performance**. University of Bristol.

VOGT, G. Maple Seeds. Edição de Roger Storm. **NASA Glenn Research Center**, 13 maio 2021.

### Referências de Competição e Padrões

LATIN AMERICAN SPACE CHALLENGE (LASC). **Satellite Challenge Standards Manual (SCSM)**. Edição 7, Revisão 1. 22 mar. 2026.

### Referências Aplicadas e Inspiração Bioinspirada

MODERN SCIENCES TEAM. Maple seed drone flies 26 minutes on a single rotor. **Modern Sciences**, 1 set. 2025.

SMITH, P. Bio-Inspired Drone Splits into Five Mini-Drones Mid-Air. **Drone Below**, 16 jul. 2019.

### Referências Conceituais

WIKIPEDIA. Samara (fruit). **Simple English Wikipedia, the free encyclopedia**, 8 mar. 2025.

WIKIPEDIA. Samara (fruit). **Wikipedia, The Free Encyclopedia**, 8 mar. 2026.

### Cobertura Referencial

Este acervo técnico cobre:

- ✓ Requisitos de competição (LASC SCSM)
- ✓ Validação empírica de LEV (University of Bristol, NASA)
- ✓ Literatura de sistemas dinâmicos e controle (Journal of Dynamic Systems)
- ✓ Referências de bioinspiração (maple seeds, drones)
- ✓ Repositórios institucionais (PRISM)

**Uso**: Em caso de questões da banca avaliadora sobre arrasto parasitário e fundamentação do modelo LEV, este portfólio oferece suporte técnico direto.

---

## 6. Estrutura do Projeto

### Arquivos Relacionados

- [[2026-04-17-helike-historico-testes]] - Histórico de testes com validação simulação
- [[2026-04-17-analise-simulacao-helike]] - Análise Samara PQ detalhada
- [[2026-04-17-plano-instrumentacao-helike-test3]] - Test #3 com eletrônica embarcada
- [[satellite]] - Projeto principal de satélite

### Pipeline de Documentação

```
NotebookLM (P&R capturados)
    ↓
Esta nota (SRAB - Conceitos Fundamentais)
    ↓
Nota de Revisão (a processar)
    ↓
Organização em pastas tematicas
    ↓
Linking Zettelkasten
```

---

## 7. Próximos Passos

- [ ] Revisar esta documentação com especialistas
- [ ] Preparar seção de Referências para LRR (Launch Readiness Review)
- [ ] Integrar com [[2026-04-17-plano-instrumentacao-helike-test3]] para validação experimental
- [ ] Expandir para 6DOF se necessário para testes com vento lateral
- [ ] Submeter como case study à LASC

---

**Versão**: 1.0  
**Data**: 2026-04-17  
**Status**: Revisão pendente  
**Próxima revisão**: Após apresentação ao team Helike
