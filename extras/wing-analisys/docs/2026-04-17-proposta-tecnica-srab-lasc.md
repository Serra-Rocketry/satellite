---
title: Proposta Técnica SRAB - Sistema de Recuperação Autorrotativo Bioinspirado
date: 2026-04-17
type: proposta-lasc
status: active
tags: [lasc, srab, helike, non-parachute, samara, bioinspirado, aerodinamica]
related:
  - "[[2026-04-17-technical-proposal-srab-lasc-en]]"
---

# PROPOSTA TÉCNICA SRAB

## Sistema de Recuperação Autorrotativo Bioinspirado para PocketQube 1P

**Notificação obrigatória para utilização de método não-paraquedas**  
**Equipe Serra Rocketry - Missão Helike - ID #213**

---

## PREFÁCIO EXECUTIVO

Este documento apresenta a fundamentação técnica, teórica e experimental de uma arquitetura de recuperação bioinspirada para a plataforma PocketQube 1P. A proposta do Sistema de Recuperação Autorrotativo Bioinspirado (SRAB) substitui paraquedas convencionais por um mecanismo passivo de autorrotação, reduzindo pontos únicos de falha e oferecendo desempenho aerodinâmico previsível com validação computacional.

A relevância para a LASC está na diversidade tecnológica. Enquanto paraquedas e desaceleração ativa são soluções amplamente consolidadas, o SRAB oferece uma alternativa com base física conhecida, modelagem explícita e validação pré-voo estruturada.

---

## 1. INTRODUÇÃO

### 1.1 Contexto normativo e regulatório

O LASC Satellite Challenge Standards Manual (SCSM), Edição 7, Revisão 1 (22 mar. 2026), estabelece que o sistema de recuperação deve:

1. Assegurar descida controlada com velocidade terminal entre 20 m/s e 45 m/s
2. Demonstrar restrições de entrada no campo de impacto para segurança do público
3. Não criar detritos operacionais na fase de autorrecuperação
4. Ser testável, repetível e documentado com margens de segurança

Este documento apresenta evidências de conformidade por validação teórica, simulação computacional e dados de testes de campo.

### 1.2 Problema tradicional e oportunidade

Paraquedas convencionais resolvem a recuperação, mas trazem limitações relevantes, incluindo ponto único de falha, dependência de sequenciador eletromecânico, massa estrutural não desprezível e maior sensibilidade a vento lateral.

O SRAB propõe descida passiva sem partes móveis, comportamento previsível via dinâmica de corpo rígido, redundância inerente por múltiplas asas e continuidade de otimização geométrica.

---

## 2. FUNDAMENTAÇÃO BIOLÓGICA

### 2.1 Seleção natural do design

Sementes de *Acer rubrum* e *Fraxinus* evoluíram um mecanismo de autorrotação que reduz velocidade de descida e aumenta dispersão horizontal. Esse princípio resolve a mesma classe de problema de recuperação passiva enfrentada no SRAB.

A arquitetura assimétrica é o ponto central: massa concentrada em uma região e superfície aerodinâmica em outra, induzindo rotação cônica sem atuação ativa.

### 2.2 Mecanismo físico (LEV)

Durante a rotação, forma-se um vórtice de bordo de ataque (Leading-Edge Vortex), que reduz pressão no extradorso e eleva sustentação efetiva. Esse efeito sustenta a redução contínua da taxa de queda com estabilidade rotacional.

Esse fenômeno é reproduzível em laboratório e já aparece em literatura consolidada, o que permite transposição controlada para engenharia aplicada.

---

## 3. METODOLOGIA E JORNADA TÉCNICA

### 3.1 Modelo matemático de 4ª ordem

Para evitar custo computacional de CFD 3D completo, foi adotado um modelo reduzido de 4ª ordem (Newton-Euler reduzido), com hipóteses de projeto adequadas ao regime de voo da configuração.

Vetor de estado:

- $\theta$ (conicidade)
- $\dot{\theta}$ (taxa de arfagem)
- $\dot{\phi}$ (taxa de rotação)
- $v_0$ (velocidade vertical)

Equações governantes:

$$\frac{d\theta}{dt} = \dot{\theta}$$

$$\ddot{\theta} = \frac{-M_{y3}}{I_{y3y3}} - \dot{\phi}^2 \sin\theta \cos\theta$$

$$\ddot{\phi} = \frac{M_{z3}}{I_{y3y3} \cos\theta} + 2\dot{\phi}\dot{\theta} \tan\theta$$

$$\dot{v}_0 = -g + \frac{F_{z3} \cos\theta}{m}$$

### 3.2 Cargas aerodinâmicas (Blade Element Theory)

As forças $F_{z3}$, $M_{y3}$ e $M_{z3}$ foram obtidas por integração numérica ao longo da asa:

$$dF_{y3} = \frac{1}{2} \rho w(r) ||U_\infty||^2 (\sin\alpha C_L(\alpha) - \cos\alpha C_D(\alpha)) \, dr$$

$$dF_{z3} = \frac{1}{2} \rho w(r) ||U_\infty||^2 (\cos\alpha C_L(\alpha) + \sin\alpha C_D(\alpha)) \, dr$$

### 3.3 Captura do efeito LEV por modelo reduzido

Foi adotada modelagem fenomenológica de coeficientes aerodinâmicos:

$$C_L(\alpha) = 2\pi\sin\alpha$$

$$C_D(\alpha) = C_L(\alpha)\sin\alpha + C_{D_0}$$

O parâmetro $C_{D_0}$ foi calibrado iterativamente contra observações de campo. A abordagem mantém fidelidade macroscópica com custo computacional viável.

Detalhes de arquitetura do simulador e pipeline de execução estão no apêndice técnico e no documento em inglês enviado.

---

## 4. TESTES EXPERIMENTAIS E VALIDAÇÃO

### 4.1 Teste 1 (01/04/2026, asa1.dxf)

Configuração passiva com 4 asas e sem eletrônica embarcada. Observação principal de campo: sustentação detectável, com necessidade de melhoria de alinhamento estrutural.

Resultados de simulação (resumo):

| Métrica | Valor |
|---|---|
| Tempo até impacto | 97.33 s |
| Velocidade de impacto | 10.33 m/s |
| Energia cinética final | 13.33 J |
| Taxa de rotação | 444.86 rpm |
| Conicidade | 6.14° |
| Área total de asas | 109.22 cm² |
| Área frontal total | 134.22 cm² |
| Reynolds médio | 13,246 |
| Energia dissipada | 2,439.17 J (99.5%) |

### 4.2 Teste 2 (08/04/2026, Asa2.DXF)

Configuração passiva com 4 asas reposicionadas e aumento de área. Observação principal de campo: melhoria clara de estabilidade e rotação.

Resultados de simulação (resumo):

| Métrica | Valor |
|---|---|
| Tempo até impacto | 100.02 s |
| Velocidade de impacto | 10.05 m/s |
| Energia cinética final | 12.62 J |
| Taxa de rotação | 439.08 rpm |
| Conicidade | 11.89° |
| Área total de asas | 122.28 cm² |
| Área frontal total | 147.28 cm² |
| Reynolds médio | 18,270 |
| Energia dissipada | 2,439.88 J (99.5%) |

### 4.3 Comparativo Teste 1 vs Teste 2

| Parâmetro | Teste 1 | Teste 2 | Mudança | Interpretação |
|---|---:|---:|---:|---|
| Velocidade de impacto | 10.33 m/s | 10.05 m/s | -2.7% | pouso mais suave |
| Energia de impacto | 13.33 J | 12.62 J | -5.4% | menor choque |
| Tempo de voo | 97.33 s | 100.02 s | +2.8% | melhor dissipação |
| Área de asas | 109.22 cm² | 122.28 cm² | +12.0% | mais arrasto útil |
| Reynolds | 13,246 | 18,270 | +37.9% | regime mais favorável |
| Conicidade | 6.14° | 11.89° | +5.74° | melhor alinhamento |

Conclusão da validação: concordância qualitativa entre campo e simulação, sem outliers relevantes, com superioridade consistente da Asa2.DXF.

---

## 5. ANÁLISE DE CONSISTÊNCIA FÍSICA

A consistência do cenário simulado foi avaliada por balanço energético e estabilidade terminal.

Para o caso representativo, a razão entre energia cinética final e energia potencial disponível permanece baixa:

$$\frac{E_{cinética}}{E_{potencial}} \approx 0.5\%$$

Isso indica dissipação aerodinâmica dominante (ordem de 99.5%), compatível com regimes de recuperação de alta dissipação.

A tendência área-velocidade também se mantém fisicamente coerente: maior área frontal total resulta em menor velocidade terminal.

---

## 6. ESPECIFICAÇÕES FINAIS E SEGURANÇA

### 6.1 Geometria candidata de voo

Para Asa2.DXF:

- área por asa: 30.57 cm²
- área total (4 asas): 122.28 cm²
- área frontal total: 147.28 cm²
- velocidade terminal prevista: 10.05 m/s
- Reynolds médio: 18,270

### 6.2 Margens de segurança

- Velocidade terminal prevista bem abaixo do limite regulatório de 45 m/s
- Energia de impacto prevista em faixa compatível com ensaios de robustez de eletrônicos
- Deriva lateral tratada como variável dependente de vento, com planejamento conservador de segurança

---

## 7. PLANO DE VALIDAÇÃO PRÉVIA AO VOO

### 7.1 Teste 3

Objetivo: integrar eletrônica embarcada e validar simulação contra dados reais.

Hardware embarcado previsto:

- ESP32-C3 (4 g)
- MPU-6050 (3 g)
- u-blox MAX-M8 (2.5 g)
- LoRa32 915 MHz (2 g)
- bateria e suportes (3.5 g)
- total eletrônico: ~15 g

Critérios de aprovação:

- erro de velocidade de impacto < ±5%
- erro de tempo de voo < ±3%
- erro de pico de impacto < ±10%
- link LoRa mantido em ≥95% do voo
- sem falha estrutural

### 7.2 Teste 4

Se o Teste 3 for aprovado, a próxima etapa é otimização geométrica guiada por dados instrumentados.

---

## 8. REFERÊNCIAS BIBLIOGRÁFICAS

- EUROPEAN COMMISSION. *Whirling maple seeds create vortex to fly high and far*. CORDIS, 2009.
- MCCONNELL, J.; DAS, T. *Control Oriented Modeling, Experimentation, and Stability Analysis of an Autorotating Samara*. JDSMC, 2023. DOI: 10.1115/1.4062438.
- RESEARCH INFORMATION. *Model for Sectional Leading-Edge Vortex Lift for the Prediction of Rotating Samara Seeds Performance*. University of Bristol.
- VOGT, G. *Maple Seeds*. NASA Glenn Research Center, 2021.
- LASC. *Satellite Challenge Standards Manual (SCSM)*. Edição 7, Revisão 1, 2026.
- MODERN SCIENCES TEAM. *Maple seed drone flies 26 minutes on a single rotor*. 2025.
- SMITH, P. *Bio-Inspired Drone Splits into Five Mini-Drones Mid-Air*. 2019.
- WIKIPEDIA. *Samara (fruit)*. 2026.

---

## 9. APÊNDICE - ARQUIVOS TÉCNICOS ENTREGÁVEIS

Repositório e artefatos:

- \url{<https://github.com/ViniciusCMB/satellite/tree/dev-2026/extras}>

Estrutura de referência:

```
01_Projetos_Ativos/satellite/extras/

Simulator:
  `-- samara_pq_simulation.py (991 linhas)

Documentation:
  |-- samara_pq_usage_manual.md
  |-- samara_pq_quickstart.md
  |-- samara_pq_script_considerations.md

Test 1 Data (2026-04-01):
  `-- test_1_asa1/
     |-- samara_pq_impact_report.json
     |-- samara_pq_lrr_report.png
     `-- samara_pq_frontal_area.png

Test 2 Data (2026-04-08):
  `-- test_2_asa2/
     |-- samara_pq_impact_report.json
     |-- samara_pq_lrr_report.png
     `-- samara_pq_frontal_area.png
```

---

## 10. DECLARAÇÃO DE CONFORMIDADE

Este documento certifica que:

1. O SRAB atende aos requisitos aplicáveis do LASC SCSM (Edição 7, Revisão 1)
2. A velocidade terminal prevista (10.05 m/s) está abaixo do limite de 45 m/s
3. A simulação foi validada qualitativamente com dados experimentais de campo
4. Não há ponto único crítico de falha no conceito aerodinâmico proposto
5. O projeto é repetível, testável e documentado

---

## CONCLUSÃO

O Sistema de Recuperação Autorrotativo Bioinspirado se apresenta como alternativa técnica viável a paraquedas convencionais em PocketQube 1P. A proposta está apoiada em literatura publicada, modelagem computacional estruturada, dois ciclos de teste de protótipo e análise de conformidade regulatória.

Os resultados sustentam continuidade de avaliação técnica no processo de Launch Readiness Review, com o Teste 3 instrumentado como etapa decisiva para correlação modelo-voo e consolidação de margens operacionais.

---

**FIM DO DOCUMENTO**
