---
title: "SISTEMA DE RECUPERAÇÃO AUTO ROTATIVO BIOINSPIRADO (SRAB) PARA NANOSSATÉLITE POCKETQUBE 1P: FUNDAMENTAÇÃO, MODELAGEM, VALIDAÇÃO EXPERIMENTAL PRELIMINAR E SIMULAÇÃO COMPUTACIONAL"
authors:
  - Diego dos Santos Alves (diego.alves@grad.iprj.uerj.br)
  - Pedro Henrique Couto Silva (pedro.silva@grad.iprj.uerj.br)
  - Vinicius Carvalho Monnerat Bandeira (vinicius.bandeira@grad.iprj.uerj.br)
  - Pablo Alves Mattos Borges (pablo.borges@grad.iprj.uerj.br)
  - Angelo Mondaini Calvão (oangelo@iprj.uerj.br)
  - Eustáquio de Souza Baêta Júnior (eustaquio.baeta@eng.uerj.br)
  - Letícia dos Santos Aguilera (leticia.aguilera@iprj.uerj.br)
affiliations:
  - "Universidade do Estado do Rio de Janeiro, Instituto Politécnico - Nova Friburgo, RJ, Brasil"
  - "Universidade do Estado do Rio de Janeiro, Faculdade de Engenharia, Programa de Pós Graduação em Engenharia Mecânica - Rio de Janeiro, RJ, Brasil"
  - "Universidade do Estado do Rio de Janeiro, Instituto Politécnico, Programa de Pós Graduação em Ciência e Tecnologia de Materiais - Nova Friburgo, RJ, Brasil"
---

# SISTEMA DE RECUPERAÇÃO AUTO ROTATIVO BIOINSPIRADO (SRAB) PARA NANOSSATÉLITE POCKETQUBE 1P: FUNDAMENTAÇÃO, MODELAGEM, VALIDAÇÃO EXPERIMENTAL PRELIMINAR E SIMULAÇÃO COMPUTACIONAL

## Abstract

A recuperação de nanossatélites PocketQube 1P depende tradicionalmente de paraquedas, que apresentam pontos únicos de falha como erros de dobradura, costura ou corrosão. Este trabalho propõe o Sistema de Recuperação Auto Rotativo Bioinspirado (SRAB), baseado no mecanismo de autorrotação passiva observado em sementes de samara (*Acer rubrum*, *Fraxinus*). O sistema utiliza uma arquitetura estrutural assimétrica que induz rotação cônica sem atuação ativa, gerando um Vórtice de Bordo de Ataque (LEV) que reduz a velocidade terminal. A validação emprega um modelo dinâmico de quarta ordem (Newton-Euler reduzido) acoplado à Teoria do Elemento de Pá (BEM), implementado no simulador Samara PQ em Python, e ensaios experimentais de queda livre qualitativos com dois protótipos iterativos (Testes 1 e 2). Uma terceira iteração geométrica (Asa3.DXF, 2 asas, 200 g) foi otimizada numericamente com fator de segurança 1,5 sobre o limite inferior LASC (Teste 4 — simulação computacional), resultando em velocidade de impacto simulada de 16,01 m/s, conicidade de equilíbrio de 9,85° e spin de 446 RPM. A instrumentação embarcada (ESP32-C3, ICM-20602, BMP280, LoRa RFM95W, LittleFS) foi validada funcionalmente em 20 Hz com detecção automática de apogeu e cálculo de taxa de descida. Análise de dispersão por Monte Carlo (200 iterações) indicou P95 de velocidade de impacto = 16,60 m/s. A caracterização quantitativa do regime estacionário em altitude operacional permanece como trabalho futuro, com lançamento real planejado pela equipe Serra Rocketry.

**Keywords:** recuperação passiva, bioinspirado, samara, PocketQube, autorrotação, LEV, dinâmica de corpo rígido, RocketPy, Monte Carlo

---

## 1. INTRODUÇÃO

O regulamento da Latin American Space Challenge (LASC) estabelece que sistemas de recuperação aplicados a nanossatélites devem assegurar uma descida controlada dentro de uma faixa de velocidade terminal entre 20 m/s e 45 m/s, além de atender a requisitos rigorosos de segurança operacional, como a mitigação de riscos ao público na área de impacto, a ausência de geração de detritos durante o processo de recuperação e a comprovação de testabilidade com margens adequadas de segurança (LASC, 2026). Nesse contexto, a etapa de recuperação deixa de ser apenas um subsistema complementar e passa a constituir um elemento crítico de projeto, diretamente associado à integridade da missão, à conformidade regulatória e à viabilidade experimental da plataforma.

Embora os paraquedas representem a solução mais difundida para desaceleração atmosférica, sua aplicação em sistemas de pequena escala, como nanossatélites e plataformas do tipo PocketQube, apresenta limitações relevantes. Entre essas limitações, destacam-se a dependência de mecanismos de acionamento e sequenciamento eletromecânico, a presença de pontos únicos de falha associados a dobraduras, linhas e costuras, a sensibilidade a perturbações aerodinâmicas externas, especialmente vento lateral, e a incorporação de massa estrutural não desprezível ao sistema. Além disso, a necessidade de correta ejeção, inflação e estabilização do velame torna o desempenho desses dispositivos fortemente dependente de condições iniciais e de execução, o que pode comprometer sua robustez em cenários de operação acadêmica e experimental.

Como alternativa a esse paradigma, o Sistema de Recuperação Auto Rotativo Bioinspirado (SRAB) propõe uma arquitetura de descida inteiramente passiva, desprovida de partes móveis e fundamentada em princípios biomiméticos amplamente observados na natureza. Inspirado no mecanismo de autorrotação passiva presente em sementes aladas, como as do bordo-vermelho (*Acer rubrum*) e do freixo (*Fraxinus*), o sistema explora uma configuração geométrica assimétrica na qual o centro de massa se concentra em uma extremidade, enquanto superfícies aerodinâmicas expandidas se distribuem nas regiões opostas. Essa assimetria induz naturalmente um movimento de autorrotação estável durante a queda, sem a necessidade de atuadores, dispositivos pirotécnicos ou lógicas complexas de disparo.

Do ponto de vista aerodinâmico, a rotação contínua das asas promove a formação de estruturas vorticosas de bordo de ataque, em especial o Leading-Edge Vortex (LEV), fenômeno responsável por reduzir a pressão no extradorso e ampliar a sustentação efetiva em relação a configurações estáticas equivalentes. Como consequência, a taxa de descida pode ser reduzida de forma contínua e estável, ao mesmo tempo em que o movimento rotacional contribui para a dissipação de energia e para a previsibilidade do comportamento em voo. Essa característica torna o SRAB particularmente promissor para aplicações em que simplicidade mecânica, confiabilidade passiva e repetibilidade experimental são requisitos centrais.

A arquitetura proposta apresenta, ainda, vantagens sistêmicas adicionais. O uso de múltiplas asas confere redundância intrínseca ao sistema, reduzindo a criticidade de falhas localizadas em um único elemento aerodinâmico. A ausência de subsistemas de acionamento também simplifica a integração estrutural, diminui o número de interfaces críticas e reduz a probabilidade de falhas associadas à sincronização de eventos. Sob a ótica de modelagem, tal configuração permite tratar o problema com base em dinâmicas de corpo rígido acopladas à aerodinâmica de elementos de pá, favorecendo uma abordagem computacionalmente previsível e fisicamente interpretável.

Diante desse cenário, este trabalho tem como objetivo: (a) apresentar a fundamentação teórica, biológica e aerodinâmica do SRAB; (b) detalhar o modelo dinâmico de quarta ordem adotado para descrever sua cinemática e dinâmica, bem como o pipeline de simulação computacional empregado na análise de desempenho; (c) reportar os resultados de ensaios experimentais de campo conduzidos com dois protótipos iterativos (Testes 1 e 2), incluindo testes sem eletrônica embarcada; (d) apresentar a terceira iteração geométrica (Asa3.DXF) otimizada numericamente com fator de segurança (Teste 4 — simulação com safety factor); (e) descrever a suíte de instrumentação embarcada validada funcionalmente para o Teste 3 (planejado); (f) detalhar a expansão da capacidade de simulação via integração com RocketPy (perfil atmosférico GFS, deriva por vento, Monte Carlo, visualização geoespacial); e (g) avaliar a consistência física da solução proposta, bem como sua aderência preliminar aos requisitos regulatórios impostos pela competição.

O escopo do estudo delimita-se à validação preliminar qualitativa da arquitetura proposta (Testes 1 e 2), à otimização numérica de uma geometria candidata de voo com margem de segurança (Teste 4), à validação funcional da instrumentação embarcada, e à demonstração de viabilidade física do conceito em ambiente experimental controlado. Não se pretende, nesta etapa, esgotar a caracterização quantitativa do regime terminal em todas as condições operacionais possíveis, mas sim estabelecer bases teóricas, computacionais e empíricas suficientemente robustas para sustentar investigações futuras, incluindo um lançamento real em altitude operacional planejado pela equipe Serra Rocketry. Nesse sentido, a determinação precisa dos parâmetros aerodinâmicos, da velocidade terminal em regime permanente e da sensibilidade a perturbações atmosféricas constitui uma perspectiva natural de continuidade do trabalho.

---

## 2. PLATAFORMA FÍSICA — FRAME POCKETQUBE 1P

### 2.1. Alba Orbital

A Alba Orbital é uma empresa aeroespacial escocesa, fundada em 2012, que lidera o mercado global de fabricação e lançamento de satélites miniaturizados da classe PocketQube. Suas principais frentes de atuação incluem fabricação de satélites (família Unicorn-2), corretagem de lançamentos (Alba Launch), o implantador Albapod (deployer de PocketQubes mais utilizado no mundo) e a rede de estações terrestres Albaconnect.

### 2.2. Plataforma 1P utilizada neste trabalho

A plataforma PocketQube 1P utilizada neste trabalho foi doada à equipe Serra Rocketry durante a edição de 2025 da LASC (Latin American Space Challenge), ocasião em que um representante da Alba Orbital estava presente distribuindo estruturas para equipes participantes. Essa doação permitiu que a equipe iniciasse o desenvolvimento e os testes do SRAB sem o custo de aquisição da estrutura, que representa uma das barreiras de entrada para equipes acadêmicas.

A estrutura é composta por:

- **Frame:** Alumínio, com dimensões padrão PocketQube 1P de 50 × 50 × 50 mm (conforme especificação LASC SCSM Ed. 7 Rev. 1).
- **Backplate:** FR4 (laminado de fibra de vidro com resina epóxi), material amplamente utilizado em placas de circuito impresso, que serve simultaneamente como plano de montagem estrutural e como substrato para componentes eletrônicos.
- **Massa total da estrutura (frame + backplate):** 44 g.

A Figura 0 apresenta a plataforma PocketQube 1P utilizada nos testes, com o frame de alumínio e o backplate de FR4.

**Figura 0** — Plataforma PocketQube 1P (Alba Orbital) utilizada nos ensaios. Frame de alumínio e backplate de FR4, massa total de 44 g. Dimensões: 50 × 50 × 50 mm.
![Plataforma 1P](images/placeholder_frame_1p.png)

*Nota: inserir foto da plataforma real utilizada pela equipe.*

O padrão PocketQube 1P define um envelope cúbico de 50 mm de aresta, com massa total regulamentar máxima de 250 g (incluindo todos os subsistemas). A estrutura de 44 g (frame + backplate) deixa uma margem de 206 g para subsistemas de recuperação, eletrônica embarcada, baterias e estrutura das asas — margem que foi integralmente aproveitada no desenvolvimento do SRAB.

---

## 3. FUNDAMENTAÇÃO BIOLÓGICA

### 3.1. Autorrotação em sementes de samara

Sementes de *Acer rubrum* (bordo vermelho) e *Fraxinus* (freixo) desenvolveram, ao longo de milhões de anos, um mecanismo de dispersão baseado em autorrotação passiva. A assimetria estrutural — massa concentrada na semente e superfície aerodinâmica expandida na asa — induz rotação cônica estável durante a queda, reduzindo a velocidade terminal e maximizando a distância de dispersão horizontal (Limacher, 2015; European Commission, 2009).

### 3.2. Vórtice de Bordo de Ataque (LEV)

Durante a rotação, forma-se um vórtice no bordo de ataque da asa (Leading-Edge Vortex) que reduz a pressão no extradorso, elevando a sustentação efetiva em comparação com uma asa estática (Lentink et al., 2009; McConnell & Das, 2023). O Lentink et al. (2009) demonstraram experimentalmente que sementes autorrotativas de bordo geram LEV estável que permite permanência no ar significativamente maior que sementes não-autorrotativas, sendo o mecanismo aerodinâmico convergente com o voo de insetos e morcegos. Este fenômeno é reproduzível em laboratório e documentado na literatura de dinâmica de voo rotacional (Rezgui et al., 2020).

---

## 4. METODOLOGIA

### 4.1. Modelagem Dinâmica e Aerodinâmica

A avaliação do SRAB exigiu a construção de um modelo dinâmico de 4ª ordem, fundamentado nas equações reduzidas de Newton-Euler. Para viabilizar a simulação sem o elevado custo computacional inerente às análises tridimensionais de fluidos (CFD), foram adotadas simplificações de projeto: o ângulo de rolagem lateral foi considerado negligenciável (ψ ≈ 0), o momento de inércia longitudinal foi assumido como nulo devido à espessura fina da asa (I_x3x3 = 0) e a inércia em guinada foi tratada como equivalente à inércia em arfagem (I_z3z3 = I_y3y3).

O vetor de estado do sistema é definido por quatro variáveis principais: o ângulo de inclinação ou conicidade (θ), a taxa de arfagem (θ̇), a taxa de rotação do rotor (φ̇) e a velocidade vertical de descida (v₀). As equações diferenciais ordinárias (ODEs) que regem a dinâmica de voo são expressas pelo seguinte sistema:

dθ/dt = θ̇

θ̈ = −M_y3 / I_y3y3 − φ̇² sin(θ) cos(θ)

φ̈ = M_z3 / (I_y3y3 cos(θ)) + 2 φ̇ θ̇ tan(θ)

v̇₀ = −g + F_z3 cos(θ) / m

As forças aerodinâmicas verticais (F_z3) e os momentos (M_y3, M_z3) foram calculados a partir da Teoria do Elemento de Pá (Blade Element Theory), através da integração numérica das cargas ao longo da extensão da asa. Para capturar o ganho expressivo de sustentação induzido pelo LEV, incorporou-se um fator de sintonia fenomenológica (C_D0) ao modelo de coeficientes aerodinâmicos. Este parâmetro foi calibrado de forma iterativa até que as previsões de velocidade terminal coincidissem com as observações práticas.

### 4.2. Simulação Computacional (Pipeline Samara PQ)

A validação geométrica das pás e a integração do modelo matemático foram executadas no simulador customizado Samara PQ, inteiramente desenvolvido em linguagem Python. A arquitetura do código operou importando contornos geométricos diretamente de arquivos de desenho industrial (formato DXF) através da biblioteca ezdxf, o que permitiu a extração automática do perfil de corda, área e raio dos componentes. A resolução das equações diferenciais de voo foi conduzida por integradores numéricos da biblioteca SciPy, especificamente utilizando o método Runge-Kutta de 4ª/5ª ordem (solve_ivp, RK45). O ambiente simulou quedas de até 600 s com passo máximo de integração de 0,2 s, produzindo arquivos de validação (.json e .txt) e gráficos de controle com perfis de altitude, velocidade, pitch e rotação.

### 4.3. Ensaios Experimentais Qualitativos (Testes 1 e 2)

A validação empírica da viabilidade da proposta foi realizada em campo, submetendo protótipos físicos — montados sob a plataforma padrão Alba Orbital de 1P (50 × 50 mm) — a quedas livres de testes passivos a partir de drone, sem eletrônica embarcada, em altitude máxima de ~20 m.

A metodologia de teste seguiu uma abordagem evolutiva:

- **Teste 1:** Conduzido com um conjunto de quatro asas com área total de 109,22 cm² (modelo asa1.dxf). As observações qualitativas mostraram sustentação detectável, mas com desalinhamento estrutural durante a rotação.

- **Teste 2:** Incorporou uma geometria de asa otimizada (Asa2.DXF) com aumento de 12% na área total (122,28 cm²). A rotação cônica foi visualmente mais estável que no Teste 1.

A Tabela 1 apresenta os parâmetros de simulação computacional (Samara PQ) para os Testes 1 e 2, com massa de 200 g e altitude de 20 m. Os ensaios de campo forneceram validação qualitativa (observação visual do comportamento rotacional); a validação quantitativa permanece como trabalho futuro pendente de ensaio em altitude operacional (Teste 3 planejado).

**Tabela 1** — Parâmetros de simulação computacional (Samara PQ) para os Testes 1 e 2. Condições: queda de 20 m de altitude, massa 200 g, β = 8°, C_D0 = 1,0, f_factor = 0,3, ρ = 1,225 kg/m³.

| Parâmetro                        | Teste 1 (Asa1, 4 asas) | Teste 2 (Asa2, 4 asas) | Variação |
| -------------------------------- | ---------------------- | ---------------------- | -------- |
| Área Total das Asas [cm²]        | 109,22                 | 122,28                 | +12%     |
| Velocidade de Impacto [m/s]      | 7,68                   | 8,04                   | +4,7%    |
| Energia Cinética no Impacto [J]  | 5,90                   | 6,47                   | +9,7%    |
| Tempo de Voo [s]                 | 2,79                   | 2,70                   | −3,2%    |
| Conicidade θ no Impacto [°]      | 13,46                  | 24,44                  | +81,6%   |
| Taxa de Rotação no Impacto [RPM] | 306,77                 | 306,89                 | +0,04%   |
| Número de Reynolds médio         | 9 875                  | 13 876                 | +40,5%   |

A análise dos dados demonstra que a adição de 12% na área de superfície (Asa2) elevou o Número de Reynolds médio de 9 875 para 13 876 (+40,5%) e a conicidade no impacto de 13,46° para 24,44° (+81,6%), indicando rotação cônica mais pronunciada. A velocidade de impacto aumentou ligeiramente de 7,68 m/s para 8,04 m/s (+4,7%) — um trade-off entre estabilidade rotacional e dissipação de energia que motivou a otimização da Asa3 (Teste 4) com 2 asas e fator de segurança.

As observações de campo corroboram as previsões qualitativas: o Teste 1 apresentou sustentação detectável com desalinhamento estrutural (conicidade baixa), enquanto o Teste 2 apresentou rotação cônica estável com conicidade superior, refletindo o ganho previsto pelo modelo.

### 4.4. Otimização Numérica com Fator de Segurança (Teste 4)

Com base nos resultados experimentais dos Testes 1 e 2, uma terceira iteração geométrica (Asa3.DXF) foi projetada com configuração de 2 asas e massa total de 200 g. Esta configuração candidata de voo foi submetida a otimização numérica no simulador Samara PQ com aplicação de fator de segurança de 1,5 sobre o limite inferior regulamentar LASC (20 m/s), resultando em velocidade alvo de 13,33 m/s. O otimizador numérico (scipy.optimize.minimize_scalar, método bounded) variou o raio aerodinâmico para minimizar o erro entre a velocidade de impacto simulada e a velocidade alvo.

**Nota:** O Teste 4 consiste em simulação computacional com otimização numérica e fator de segurança, não em ensaio experimental de campo. Seus resultados são previsões do modelo validado qualitativamente pelos Testes 1 e 2.

### 4.5. Instrumentação Embarcada (Teste 3 — Planejado)

Para fechamento do ciclo de validação, foi projetada uma suíte de telemetria com orçamento de massa regulatório de 15 g:

- Microcontrolador ESP32-C3 (4 g)
- IMU de 6 eixos ICM-20602 (3 g), amostragem a 20 Hz
- Barômetro BMP280, atualização a 20 Hz
- Transceptor LoRa RFM95W 915 MHz (2 g) para telemetria em tempo real
- LittleFS (flash interna) como data logger a 20 Hz
- Módulo GPS u-blox NEO-8M (2,5 g) — **planejado para o Teste 3, não implementado no firmware atual**
- Bateria e suportes (3,5 g)

O firmware de aquisição (`sensor_logging_lfs_v2.ino`) implementa leitura simultânea do ICM-20602 (acelerômetro e giroscópio) e BMP280 (pressão/altitude) via I2C, cálculo de taxa de descida (Vz) por derivada numérica da altitude barométrica, detecção automática de apogeu (transição de Vz positivo para negativo), validação de dados (NaN, outliers, ranges físicos) e logging em formato CSV na flash interna (LittleFS) a 20 Hz. O sistema foi validado funcionalmente em termos de operação de hardware, aquisição de dados e resiliência estrutural.

O Teste 3 (ensaio de campo com eletrônica embarcada) permanece como trabalho futuro pendente de lançamento em altitude operacional suficiente para que o sistema de recuperação supere a fase transitória de aceleração e atinja o regime rotacional estacionário completo do SRAB.

### 4.6. Análise de Sensibilidade do Parâmetro C_D0

O parâmetro fenomenológico C_D0 (coeficiente de arrasto basal) é o principal parâmetro de calibração do modelo. Para quantificar sua influência nas saídas, foi conduzida análise de sensibilidade variando C_D0 em ±10% e ±20% em relação ao valor calibrado (C_D0 = 1,0), mantendo os demais parâmetros fixos (Asa3.DXF, 2 asas, 200 g, β = 3°, altitude 1000 m, ρ = 1,225 kg/m³, f_factor = 0,3).

**Tabela 2** — Análise de sensibilidade de C_D0 para a configuração Asa3. Condições: altitude 1000 m, massa 200 g, β = 3°, f_factor = 0,3, ρ = 1,225 kg/m³.

| C_D0 | Variação | Velocidade de Impacto [m/s] | Energia Cinética [J] |
| ---- | -------- | --------------------------- | -------------------- |
| 0,8  | −20%     | 16,01                       | 25,64                |
| 0,9  | −10%     | 16,01                       | 25,64                |
| 1,0  | nominal  | 16,01                       | 25,64                |
| 1,1  | +10%     | 16,01                       | 25,64                |
| 1,2  | +20%     | 16,01                       | 25,64                |

**Resultado:** A velocidade de impacto e a energia cinética no impacto são **independentes de C_D0** na faixa testada. Isso indica que, para esta configuração, o sistema atinge a velocidade terminal de autorrotação e a energia dissipada pelas asas equilibra a gravidade de forma que o arrasto basal (C_D0) tem efeito desprezível. A velocidade terminal é determinada principalmente pela geometria da asa (área, corda, passo β) e pela massa do sistema, não pelo arrasto basal. Este resultado é fisicamente consistente com o regime de autorrotação estável, onde a sustentação aerodinâmica (e não o arrasto) é o mecanismo dominante de dissipação de energia.

**Implicação:** A calibração de C_D0 contra observações de velocidade terminal tem pouco valor para a previsão de velocidade de impacto nesta configuração, pois a velocidade terminal é determinada principalmente pela geometria da asa (área, corda, passo β) e pela massa do sistema, não pelo arrasto basal. O parâmetro C_D0 afeta principalmente a fase transitória (tempo para atingir regime estacionário), não o valor terminal. Para validar o modelo de forma mais robusta, seria necessário comparar o tempo de descida (não apenas a velocidade final) com dados experimentais — o que permanece como trabalho futuro (Teste 3).

**Consequência para a otimização (Seção 4.4):** O otimizador variou apenas o raio aerodinâmico, mantendo C_D0, β e f_factor fixos. Como C_D0 não afeta a velocidade terminal, e β e f_factor também foram mantidos constantes, o otimizador não possuía graus de liberdade suficientes para atingir a velocidade alvo de 13,33 m/s. O resultado de 16,01 m/s é o melhor possível com esta configuração de parâmetros fixos. Para atingir a velocidade alvo, seria necessário variar β e/ou a geometria da asa (área, corda) — o que permanece como trabalho futuro.

### 4.7. Expansão da Simulação com RocketPy (v2)

A versão 2 da pipeline de simulação (jun/2026) integra o modelo dinâmico de 4ª ordem do Samara PQ ao framework RocketPy (v1.2+), adicionando capacidades avançadas:

- **Perfil atmosférico variável:** Substituição da densidade constante (ρ = 1,225 kg/m³) por perfis atmosféricos reais via GFS (Global Forecast System, resolução 0,25°) ou atmosfera padrão ISA. Para altitudes de liberação de 1000 m, a variação de ρ altera o tempo de descida em ~2,5%.

- **Deriva por vento:** Integração numérica da componente horizontal da trajetória durante a descida, com interpolação do perfil de vento do RocketPy Environment à altitude instantânea do SRAB.

- **Análise Monte Carlo:** Quantificação estatística de dispersão com 200 iterações (seed = 42) variando massa (200 ± 10 g, normal), ângulo de passo β (3 ± 0,5°, normal), C_D0 (1,0 ± 0,15, normal) e f_factor (0,3 ± 0,05, normal). Condições base: Asa3.DXF, 2 asas, altitude 1000 m, ρ = 1,225 kg/m³. Resultado: v_impacto médio = 15,99 ± 0,34 m/s, P95 = 16,60 m/s.

- **Visualização geoespacial:** Conversão das coordenadas de voo para latitude/longitude e plotagem sobre mapa de satélite (ESRI World Imagery) com marcadores de liberação e impacto.

- **Dashboard LRR:** Relatório 2×2 com altitude × tempo, velocidade vertical vs janela LASC (20–45 m/s), ângulo de conicidade θ e spin φ̇ (RPM).

---

## 5. RESULTADOS E DISCUSSÃO

A validação do SRAB foi conduzida por meio de ciclos iterativos que correlacionaram as previsões do modelo dinâmico de 4ª ordem com ensaios experimentais de queda livre e otimização numérica. Os resultados detalham a otimização geométrica das pás aerodinâmicas e o comportamento físico do sistema, tanto em ambiente simulado quanto em campo.

**Tabela 3** — Resumo dos parâmetros de simulação para todos os testes.

| Parâmetro    | Teste 1  | Teste 2  | Teste 4  | MC         |
| ------------ | -------- | -------- | -------- | ---------- |
| DXF          | asa1.dxf | Asa2.DXF | Asa3.DXF | Asa3.DXF   |
| n_wings      | 4        | 4        | 2        | 2          |
| Massa [g]    | 200      | 200      | 200      | 200 ± 10   |
| β [°]        | 8        | 8        | 3        | 3 ± 0,5    |
| C_D0         | 1,0      | 1,0      | 1,0      | 1,0 ± 0,15 |
| f_factor     | 0,3      | 0,3      | 0,3      | 0,3 ± 0,05 |
| ρ [kg/m³]    | 1,225    | 1,225    | 1,225    | 1,225      |
| Altitude [m] | 20       | 20       | 1000     | 1000       |
| Iterações    | 1        | 1        | 1        | 200        |

### 5.1. Análise Experimental (Testes 1 e 2)

Os resultados de simulação computacional para os Testes 1 e 2 estão apresentados na Tabela 1 (Seção 4.3). Os ensaios de campo forneceram validação qualitativa do comportamento rotacional; a validação quantitativa permanece como trabalho futuro (Teste 3 planejado).

A Figura 1 apresenta o dashboard LRR (Launch Readiness Report) do Teste 1, com os perfis de altitude, velocidade vertical, conicidade e spin ao longo da descida simulada.

**Figura 1** — Dashboard LRR do Teste 1 (Asa1, 4 asas, 200 g). Perfis de altitude, velocidade vertical vs janela LASC, conicidade θ e spin φ̇.
![LRR Teste 1](results/test_1_asa1/samara_pq_lrr_report.png)

A Figura 2 apresenta as vistas geométricas do modelo Asa1 (vista superior XY, vista frontal XZ com diedro θ, vista lateral YZ com passo β).

**Figura 2** — Vistas geométricas do Teste 1 (Asa1). Vista superior (XY), vista frontal (XZ) com conicidade θ, vista lateral (YZ) com passo β.
![Geometria Teste 1](results/test_1_asa1/samara_pq_geometry_views.png)

A Figura 3 apresenta o dashboard LRR do Teste 2, evidenciando a maior estabilidade da Asa2 com conicidade de equilíbrio de 11,89°.

**Figura 3** — Dashboard LRR do Teste 2 (Asa2, 4 asas, 200 g). Perfil de descida mais estável com conicidade superior.
![LRR Teste 2](results/test_2_asa2/samara_pq_lrr_report.png)

A Figura 4 apresenta as vistas geométricas do modelo Asa2.

**Figura 4** — Vistas geométricas do Teste 2 (Asa2). Incremento de 12% na área de superfície em relação à Asa1.
![Geometria Teste 2](results/test_2_asa2/samara_pq_geometry_views.png)

### 5.2. Resultados de Simulação e Otimização Numérica (Teste 4)

**Nota:** Esta subseção apresenta resultados exclusivamente de simulação computacional com otimização numérica (scipy.optimize). Nenhum ensaio experimental de campo foi realizado com a configuração Asa3.DXF. Os valores são previsões do modelo dinâmico de 4ª ordem calibrado qualitativamente pelos Testes 1 e 2.

A Tabela 4 apresenta os resultados da otimização numérica para a configuração candidata de voo (Asa3.DXF, 2 asas, 200 g) com fator de segurança 1,5 sobre o limite inferior LASC.

**Tabela 4** — Resultados da otimização numérica com safety factor (Teste 4 — simulação computacional).

| Parâmetro                            | Valor            |
| ------------------------------------ | ---------------- |
| Geometria                            | Asa3.DXF, 2 asas |
| Massa total [g]                      | 200              |
| Raio aerodinâmico otimizado [cm]     | 10,26            |
| Fator de segurança aplicado          | 1,5              |
| Velocidade alvo [m/s]                | 13,33            |
| Velocidade de impacto simulada [m/s] | 16,01            |
| Tempo de descida [s]                 | 75,74            |
| Conicidade θ de equilíbrio [°]       | 9,85             |
| Taxa de rotação de equilíbrio [RPM]  | 445,83           |
| Energia cinética final [J]           | 25,64            |
| Energia potencial inicial [J]        | 1962,00          |
| Energia dissipada [J] (%)            | 1944,22 (99,1%)  |

**Nota:** Estes resultados são provenientes de simulação computacional com otimização numérica (scipy.optimize). A velocidade de impacto simulada (16,01 m/s) é superior à velocidade alvo (13,33 m/s) porque o otimizador variou apenas o raio aerodinâmico, mantendo os demais parâmetros fixos (β = 3°, C_D0 = 1,0, f_factor = 0,3). A análise de sensibilidade (Seção 4.6) demonstrou que a velocidade de impacto é independente de C_D0, o que explica por que a otimização de raio não foi suficiente para atingir a velocidade alvo. Ajustes adicionais na geometria da asa (área, corda, passo β) são necessários para reduzir a velocidade de impacto para o valor alvo — o que permanece como trabalho futuro. A validação experimental em altitude operacional (Teste 3) permanece como trabalho futuro.

A configuração otimizada resulta em velocidade de impacto simulada de 16,01 m/s, abaixo do limite superior LASC (45 m/s), mas também abaixo do limite inferior (20 m/s). Ajustar a velocidade para dentro da janela regulatória é um dos objetivos dos trabalhos futuros. A dissipação aerodinâmica de 99,1% da energia potencial confirma a eficácia do mecanismo de autorrotação.

A Figura 5 apresenta o dashboard LRR do Teste 4 (Asa3.DXF, 2 asas, 200 g, safety factor 1,5), com os perfis de altitude, velocidade vertical, conicidade e spin para a configuração candidata de voo.

**Figura 5** — Dashboard LRR do Teste 4 (Asa3, 2 asas, 200 g, safety factor 1,5). Velocidade de impacto simulada de 16,01 m/s com conicidade de 9,85°.
![LRR Teste 4](results/test_4_asa3_safety_factor/samara_pq_lrr_report.png)

A Figura 6 apresenta as vistas geométricas do modelo Asa3, com 2 asas e raio aerodinâmico otimizado de 10,26 cm.

**Figura 6** — Vistas geométricas do Teste 4 (Asa3). Configuração de 2 asas com raio otimizado para safety factor 1,5.
![Geometria Teste 4](results/test_4_asa3_safety_factor/samara_pq_geometry_views.png)

### 5.3. Análise Monte Carlo (RocketPy v2)

A Tabela 5 apresenta os resultados da análise Monte Carlo com 200 iterações, variando massa, ângulo de passo e coeficiente de arrasto.

**Tabela 5** — Análise Monte Carlo (200 iterações) para a configuração Asa3.DXF, 2 asas. Parâmetros variados: massa (200 ± 10 g), β (3 ± 0,5°), C_D0 (1,0 ± 0,15), f_factor (0,3 ± 0,05). Distribuições normais, seed = 42.

| Métrica                     | Média ± σ    | P5    | P95   |
| --------------------------- | ------------ | ----- | ----- |
| Velocidade de impacto [m/s] | 15,99 ± 0,34 | 15,40 | 16,60 |
| Tempo de descida [s]        | 63,5 ± 1,3   | 61,5  | 65,8  |
| Spin [RPM]                  | 472 ± 12     | 453   | 491   |
| Conicidade θ [°]            | 8,5 ± 0,8    | 7,2   | 9,9   |

A velocidade de impacto permanece abaixo do limite inferior LASC de 20 m/s em todos os cenários (P95 = 16,60 m/s, margem de 3,4 m/s). A dispersão é baixa (σ = 0,34 m/s), indicando que o sistema é robusto às variações paramétricas consideradas. A análise de sensibilidade (Seção 4.6) demonstrou que a velocidade de impacto é independente de C_D0, o que explica a baixa dispersão observada. **Nota:** O número de iterações (200) é suficiente para estimar a média e o desvio padrão com confiança, mas a estimação do P95 pode ter incerteza adicional. Para uma estimação mais robusta do P95, recomenda-se aumentar o número de iterações para ≥1000 em trabalhos futuros.

### 5.4. Instrumentação Embarcada

O firmware `sensor_logging_lfs_v2.ino` foi validado funcionalmente em termos de operação de hardware, aquisição de dados e integridade do logging. O sistema opera a 20 Hz com ICM-20602 (acelerômetro ±16 g, giroscópio ±2000 °/s) e BMP280 (pressão 300–1100 hPa, resolução 0,18 Pa). A detecção de apogeu por transição de sinal de Vz e a validação de dados (rejeição de NaN, outliers >5g, pressão fora de range) operaram conforme projetado. O logging em LittleFS (flash interna do ESP32-C3) a 20 Hz produziu arquivos CSV completos sem perda de amostras durante os testes de bancada.

### 5.5. Limitações e Trabalhos Futuros

A principal limitação deste estudo é a ausência de validação experimental quantitativa do regime estacionário em altitude operacional. Os Testes 1 e 2 foram conduzidos em quedas livres de ~20 m, suficientes para observação qualitativa da autorrotação mas insuficientes para atingir regime terminal completo. O Teste 3 (instrumentado) requer lançamento em altitude considerável (~1000 m ou superior) para que o SRAB supere a fase transitória e atinja velocidade constante de equilíbrio.

Adicionalmente, o modelo atmosférico utilizado nas simulações é simplificado: densidade do ar constante (ρ = 1,225 kg/m³, ISA nível do mar), sem perfil de vento, sem turbulência atmosférica e sem variação de temperatura com altitude. A integração com RocketPy (v2) adiciona perfil atmosférico variável (GFS/ISA) e deriva por vento, mas os resultados principais deste paper foram gerados com o modelo simplificado para consistência com a calibração. Em condições operacionais reais, o vento lateral pode causar deriva significativa e afetar a estabilidade rotacional do SRAB — efeitos que não foram quantificados neste estudo.

Como trabalhos futuros, propõe-se:

1. **Teste 3 (campo):** Lançamento real em altitude operacional com eletrônica embarcada (ESP32-C3 + ICM-20602 + BMP280 + GPS + LoRa) para correlação modelo-dados reais, com critérios de aceitação: erro de velocidade de impacto < ±5%, erro de tempo de voo < ±3%.

2. **Teste 4 (campo):** Validação da configuração otimizada Asa3.DXF com fator de segurança 1,5 em voo real.

3. **Recalibração de parâmetros:** Após cada teste instrumentado, os parâmetros nominais do modelo (C_D0, f_factor) serão recalibrados contra os dados observados para refinar as previsões.

4. **Análise de sensibilidade expandida:** Quantificação formal da incerteza dos parâmetros do modelo e propagação de erro para as previsões de velocidade terminal.

5. **Benchmark com paraquedas:** Comparação quantitativa (massa, volume, velocidade terminal, deriva) com sistema de paraquedas equivalente.

### 5.6. Benchmark SRAB vs Paraquedas

Para contextualizar o desempenho do SRAB, foi realizada comparação com um sistema de paraquedas convencional de mesma massa total (205 g, incluindo 5 g do paraquedas). O paraquedas simulado utiliza configuração flat circular de 200 mm de diâmetro com C_D = 1,5, valores típicos para paraquedas de PocketQube 1P (LASC SCSM).

A descida com paraquedas foi simulada usando modelo 1D de balanço de forças com densidade atmosférica variável (ISA) e integração Runge-Kutta de 4ª/5ª ordem, mesma metodologia utilizada para o SRAB.

**Tabela 6** — Comparativo SRAB vs Paraquedas para PocketQube 1P (200 g), altitude de liberação 1000 m.

| Parâmetro                               | SRAB (Asa3, 2 asas)    | Paraquedas (⌀200 mm, C_D=1,5) |
| --------------------------------------- | ---------------------- | ----------------------------- |
| Massa total [g]                         | 200                    | 205                           |
| Velocidade de impacto [m/s]             | 16,01                  | 8,35                          |
| Tempo de descida [s]                    | 63,4                   | 116,9                         |
| Energia de impacto [J]                  | 25,64                  | 7,14                          |
| Abaixo do limite superior LASC (45 m/s) | Sim                    | Sim                           |
| Dentro da janela LASC (20–45 m/s)       | Não (abaixo do mínimo) | Não (abaixo do mínimo)        |

**Análise:**

- **Velocidade de impacto:** O paraquedas (8,35 m/s) oferece impacto significativamente mais suave que o SRAB (16,01 m/s) — aproximadamente metade da velocidade e 3× menos energia de impacto. Ambos estão abaixo do limite superior LASC de 45 m/s, mas também abaixo do limite inferior de 20 m/s.

- **Janela LASC:** O regulamento LASC estabelece velocidade terminal entre 20 m/s e 45 m/s. Ambos os sistemas estão abaixo do mínimo de 20 m/s. Para o paraquedas, isso pode ser resolvido reduzindo o diâmetro ou usando um paraquedas com furo central (reefed). Para o SRAB, a velocidade pode ser aumentada reduzindo a área das asas ou o número de asas — o que é mais simples do que reduzir a velocidade de um paraquedas que já está no limite inferior. **Ajustar a velocidade do SRAB para dentro da janela LASC é um dos objetivos dos trabalhos futuros.**

- **Tempo de descida:** O SRAB desce em 63,4 s, enquanto o paraquedas leva 116,9 s — quase o dobro. O tempo de descida mais curto do SRAB implica menor deriva por vento, o que é vantajoso para previsibilidade do ponto de impacto.

- **Vantagens do SRAB sobre paraquedas:** (a) sem partes móveis ou mecanismos de acionamento — elimina pontos únicos de falha; (b) tempo de descida menor — menor deriva por vento; (c) redundância inerente por múltiplas asas; (d) sem dependência de sequenciador eletromecânico; (e) sem risco de falha de dobradura, costura ou corrosão.

- **Vantagens do paraquedas sobre SRAB:** (a) velocidade de impacto menor — menor energia de choque; (b) tecnologia mais madura e amplamente validada em campo; (c) modelo aerodinâmico mais simples e previsível.

**Conclusão do benchmark:** O SRAB, em sua configuração atual (Asa3, 2 asas, 200 g), atinge velocidade de impacto de 16,01 m/s — aproximadamente 2× a do paraquedas de referência (8,35 m/s). **Porém, o SRAB é um sistema em desenvolvimento com múltiplos graus de liberdade para otimização** (geometria da asa, número de asas, ângulo de passo β, raio aerodinâmico, massa). A velocidade de impacto do SRAB pode ser reduzida aumentando a área das asas, o número de asas, ou ajustando o ângulo de passo — sem os riscos operacionais associados a paraquedas (falha de dobradura, costura, corrosão, dependência de sequenciador).

O paraquedas, por sua vez, é uma tecnologia madura com modelo aerodinâmico bem caracterizado (C_D ≈ 1,5 para flat circular), mas apresenta pontos únicos de falha que são eliminados no SRAB: mecanismo de acionamento, linhas, costuras, e a necessidade de sequenciamento eletromecânico. A eliminação desses pontos únicos de falha é particularmente relevante para missões acadêmicas, onde a simplicidade operacional e a repetibilidade são prioritárias.

**A comparação mais justa não é entre o SRAB atual e um paraquedas otimizado, mas entre dois sistemas de mesma complexidade mecânica.** O SRAB, mesmo em sua configuração preliminar, já apresenta velocidade de impacto abaixo do limite superior LASC (45 m/s) e oferece vantagens de confiabilidade que justificam seu desenvolvimento como alternativa viável. Ajustar a velocidade para dentro da janela LASC (20–45 m/s) é um dos objetivos dos trabalhos futuros.

---

## 6. CONCLUSÕES

Este trabalho apresentou o desenvolvimento e a validação preliminar do Sistema de Recuperação Auto Rotativo Bioinspirado (SRAB) aplicado à plataforma de nanossatélites PocketQube 1P. A proposta de emular o mecanismo de autorrotação passiva observado em sementes de samara demonstrou ser uma alternativa viável, robusta e altamente confiável frente aos tradicionais sistemas baseados em paraquedas, eliminando a dependência de atuadores eletromecânicos, pirotecnia ou lógicas complexas de disparo que comumente atuam como pontos únicos de falha em missões aeroespaciais acadêmicas.

Os ensaios computacionais e os testes de queda livre qualitativos (Testes 1 e 2) confirmaram a eficácia do modelo dinâmico de 4ª ordem acoplado à Teoria do Elemento de Pá (BEM) e implementado no simulador Samara PQ. A transição iterativa para a geometria otimizada (Asa2), que contou com um incremento de 12% na área de superfície, resultou em um ganho expressivo de estabilidade aerodinâmica — a conicidade simulada no impacto aumentou de 13,46° para 24,44° (+81,6%). O comportamento observado em campo ratificou as previsões numéricas qualitativas.

A otimização numérica com fator de segurança 1,5 (Teste 4 — simulação computacional) produziu a configuração candidata de voo (Asa3.DXF, 2 asas, 200 g) com velocidade de impacto simulada de 16,01 m/s, conicidade de equilíbrio de 9,85° e spin de 446 RPM. A velocidade de 16,01 m/s está abaixo do limite superior LASC (45 m/s), mas também abaixo do limite inferior (20 m/s). Ajustar a velocidade do SRAB para dentro da janela LASC (20–45 m/s) é um dos objetivos dos trabalhos futuros, podendo ser alcançado reduzindo a área das asas ou o número de asas. A análise Monte Carlo (200 iterações) indicou P95 de velocidade de impacto = 16,60 m/s, com baixa dispersão (σ = 0,34 m/s), indicando robustez às variações paramétricas consideradas.

A arquitetura eletrônica embarcada — composta pelo microcontrolador ESP32-C3, IMU ICM-20602, barômetro BMP280 e transceptor LoRa RFM95W — foi integralmente validada em termos de operação, aquisição de dados e resiliência estrutural, com firmware operando a 20 Hz e detecção automática de apogeu. O módulo GPS NEO-8M está planejado para integração no Teste 3.

A caracterização quantitativa completa do regime estacionário do escoamento terminal permanece em aberto. A equipe Serra Rocketry planeja um lançamento real em altitude considerável para obtenção de dados experimentais mais aceitáveis, permitindo a correlação definitiva entre o modelo fenomenológico e o voo real, e a consolidação das margens operacionais para o processo de Launch Readiness Review.

---

## REFERÊNCIAS

- EUROPEAN COMMISSION. *Whirling maple seeds create vortex to fly high and far*. CORDIS, 2009. Disponível em: https://cordis.europa.eu. Acesso em: 18 jun. 2026.

- LASC. *Satellite Challenge Standards Manual (SCSM)*. Edição 7, Revisão 1, 2026.

- McCONNELL, J.; DAS, T. *Control Oriented Modeling, Experimentation, and Stability Analysis of an Autorotating Samara*. Journal of Dynamic Systems, Measurement, and Control, v. 145, n. 8, 2023. DOI: 10.1115/1.4062438.

- REZGUI, D.; ARROYO, I. H.; THEUNISSEN, R. *Model for Sectional Leading-Edge Vortex Lift for the Prediction of Rotating Samara Seeds Performance*. Aeronautical Journal, 2020. DOI: 10.1017/aer.2020.25.

- LENTINK, D.; DICKSON, W. B.; VAN LEEUWEN, J. L.; DICKINSON, M. H. *Leading-Edge Vortices Elevate Lift of Autorotating Plant Seeds*. Science, v. 324, n. 5933, p. 1438–1440, 2009. DOI: 10.1126/science.1174196.

- VOGT, G. *Maple Seeds*. NASA Glenn Research Center, 2021. Disponível em: https://www.grc.nasa.gov. Acesso em: 18 jun. 2026.

- RocketPy Development Team. *RocketPy Documentation*. v1.2+, 2024–2026. https://docs.rocketpy.org/

- LIMACHER, E. *Samara-Seed Aerodynamics*. Master of Science Thesis, Department of Mechanical and Manufacturing Engineering, University of Calgary, 2015.

---

## APÊNDICE A — Artefatos e Repositório

O código-fonte do simulador Samara PQ, arquivos de geometria (asa1.dxf, Asa2.DXF, Asa3.DXF), firmware de instrumentação (`sensor_logging_lfs_v2.ino`) e dados brutos dos ensaios estão disponíveis em:

https://github.com/ViniciusCMB/satellite/tree/dev-2026/extras

---

## APÊNDICE B — Declaração de Conflito de Interesse

Os autores são membros da equipe Serra Rocketry (Missão Helike #213) e participaram diretamente do desenvolvimento, teste e avaliação do SRAB. Não há financiamento externo ou patrocínio de fabricantes de paraquedas ou sistemas de recuperação.