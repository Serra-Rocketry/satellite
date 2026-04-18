---
title: Histórico de Testes Helike (Campo + Simulação)
date: 2026-04-17
captured: 2026-04-17 14:30
type: reference
status: active
project: helike
tags: [helike, testes, simulação, aerodinâmica]
related: []
---

# Histórico de Testes - Projeto Helike (com Simulação Computacional)

## Visão Geral

Registro completo do histórico de testes de protótipos do projeto Helike utilizando estrutura básica 1P da Alba Orbital, com validação via simulação aeronáutica (Samara PQ).

---

## Teste #1 - 01/04/2026 (asa1.dxf)

**Data**: 01 de abril de 2026  
**Estrutura**: Alba Orbital 1P básica  
**Asas utilizadas**: 4 asas (asa1.dxf)
**Modelo DXF processado**: `asa1.dxf`

### Observações de Campo

- Modelo apresenta sustentação detectável
- Estrutura com limitações aerodinâmicas
- Asa não está paralela ao backplate (desalinhamento)
- Status: Sem eletrônica embarcada

### Dados de Simulação (Samara PQ)

| Métrica | Valor |
|---------|-------|
| **Tempo de voo** | 97.33 s |
| **Velocidade de impacto** | 10.33 m/s |
| **Energia cinética de impacto** | 13.33 J |
| **Taxa de rotação** | 444.86 rpm |
| **Ângulo de pitch (impacto)** | 6.14° |
| **Área total de asas** | 109.22 cm² |
| **Área frontal total** | 134.22 cm² |
| **Número de Reynolds médio** | 13,246 |
| **Energia dissipada** | 2,439.17 J (99.5%) |

### Conclusões

Protótipo viável em termos aerodinâmicos, mas com limitações estruturais. Dissipação de energia confirmada. Design com potencial para otimização.

---

## Teste #2 - 08/04/2026 (Asa2.DXF)

**Data**: 08 de abril de 2026  
**Estrutura**: Alba Orbital 1P (reposicionada)  
**Asas utilizadas**: 4 asas (Asa2.DXF - novo modelo)
**Modelo DXF processado**: `Asa2.DXF`

### Observações de Campo

- Melhoria significativa em relação ao Teste #1 ✓
- Reposicionamento das asas bem-sucedido ✓
- Novo modelo de asa com melhor desempenho ✓
- Bom comportamento rotacional durante queda ✓
- Afetado por carregamento de vento (esperado)
- Status: Sem eletrônica embarcada

### Dados de Simulação (Samara PQ)

| Métrica | Valor |
|---------|-------|
| **Tempo de voo** | 100.02 s |
| **Velocidade de impacto** | 10.05 m/s |
| **Energia cinética de impacto** | 12.62 J |
| **Taxa de rotação** | 439.08 rpm |
| **Ângulo de pitch (impacto)** | 11.89° |
| **Área total de asas** | 122.28 cm² |
| **Área frontal total** | 147.28 cm² |
| **Número de Reynolds médio** | 18,270 |
| **Energia dissipada** | 2,439.88 J (99.5%) |

---

## Análise Comparativa: Test 1 vs Test 2

### Melhorias Confirmadas em Asa2.DXF

| Parâmetro | Test 1 | Test 2 | Melhoria |
|-----------|--------|--------|----------|
| Velocidade de impacto | 10.33 m/s | 10.05 m/s | **-2.7%** ✓ |
| Energia de impacto | 13.33 J | 12.62 J | **-5.4%** ✓ |
| Tempo de voo | 97.33 s | 100.02 s | **+2.8%** ✓ |
| Área de asa | 109.22 cm² | 122.28 cm² | **+12.0%** ✓ |
| Área frontal | 134.22 cm² | 147.28 cm² | **+9.7%** ✓ |
| Taxa de rotação | 444.86 rpm | 439.08 rpm | -1.3% (estável) |
| Reynolds médio | 13,246 | 18,270 | +37.9% (fluxo melhor) |

### Conclusão da Análise

✓ **Asa2.DXF apresenta melhoria mensurável:**

- **Pouso mais suave**: velocidade de impacto reduzida em 2.7%
- **Menor energia de choque**: 5.4% de redução em impacto
- **Voo mais longo**: 2.8% de aumento no tempo de descida
- **Aerodinâmica superior**: +12% em área de asa, +9.7% em área frontal
- **Equilíbrio giroscópico mantido**: taxa de rotação estável
- **Número de Reynolds aumentado**: indicação de regime de escoamento mais favorável

**Os dados simulados corroboram as observações de campo do teste de 08/04.**

---

## Próximos Passos

### Críticos (para Teste #3)

- [x] Analisar dados simulados dos dois testes comparativamente ✓
- [ ] **Integração de Eletrônica Embarcada (MANDATÓRIO para Test #3)**
  - GPS para validação de altitude/trajetória
  - Acelerômetro IMU para validação de g-force de impacto
  - Dados LoRa para telemetria em tempo real
  - Justificativa: **Necessário validar predições de simulação com dados reais**
  - Margem de massa disponível: ~15g (250g regulatório - 235g estrutura)
  - Candidato: Asa2.DXF (aerodinâmica validada, área suficiente)

### Secundários

- [ ] Executar Teste #3 com Asa3.dxf (otimizada) + eletrônica
- [ ] Comparar dados simulados vs reais (aceleração, velocidade, trajetória)
- [ ] Documentar lições aprendidas em [[design-otimizacao-samara]]
- [ ] Considerar escalonamento para protótipo com 2 asas vs 6 asas
- [ ] Publicar resultados comparativos (sim vs real) em relatório LASC

---

## Artefatos Técnicos

### Scripts de Simulação

- **Localização**: `/satellite/extras/wing-analisys/`
- **Script principal**: `samara_pq_simulation.py`
- **Manual de uso**: `samara_pq_usage_manual.md`
- **Quickstart**: `samara_pq_quickstart.md`

### Modelos DXF Utilizados

- `asa1.dxf` - Primeiro design (Test #1)
- `Asa2.DXF` - Design otimizado (Test #2)
- `Asa3.dxf` - Próximo candidato para Test #3

### Relatórios Salvos

- `test_1_asa1/samara_pq_impact_report.json`
- `test_2_asa2/samara_pq_impact_report.json`
- Visualizações PNG (LRR reports, frontal area)

---

## Referências e Links

- [[satellite]] - Projeto satélite principal
- [[Alba-Orbital-1P]] - Padrão estrutural Alba Orbital
- `samara_pq_simulation.py` - Pipeline de simulação
- `/satellite/extras/wing-analisys/` - Diretório de análise
