---
title: Quick Reference - Helike Test #3 Checklist
date: 2026-04-17
tags: [helike, test-3, checklist, referência-rápida]
status: active
type: checklist
related:
  - "[[2026-04-17-plano-instrumentacao-helike-test3]]"
  - "[[2026-04-17-analise-simulacao-helike]]"
  - "[[2026-04-17-helike-historico-testes]]"
---

# ⚡ Quick Reference - Helike Test #3

## 🎯 Objetivo

Validar simulações Samara PQ com dados reais embarcados em Asa2.DXF.

---

## 📦 Hardware Requerido (budget de 15g)

- [ ] ESP32-C3 Microcontroller (4g)
- [ ] MPU-6050 IMU 6DOF (3g) - aceleração + rotação
- [ ] u-blox MAX-M8 GPS (2.5g) - altitude + trajetória
- [ ] LoRa32 915MHz transceiver (2g) - telemetria
- [ ] LiPo Battery 250mAh (1.5g)
- [ ] Suportes + cabeamento (4.5g)
- [ ] **Total da eletrônica: ~15g** ✓

---

## 🔌 Pinagem ESP32-C3

| Sensor | Pin | Protocolo |
|--------|-----|-----------|
| MPU-6050 | GPIO6, GPIO7 | I2C (0x68) |
| u-blox MAX-M8 | GPIO20, GPIO21 | UART 115200 |
| LoRa32 | GPIO3,4,5,10,6,7 | SPI |
| SD Card | GPIO2,4,5,6 | SPI backup |

---

## ✈️ Procedimento de Voo (Timeline)

```
T-00:30  Verificação pré-voo (hardware + sensores)
T-00:15  Aquecimento GPS (target: 5+ satélites)
T-00:10  Teste link LoRa com ground station
T-00:05  Armamento final
T-00:00  LANÇAMENTO
T+100s   IMPACTO esperado (detectar via a_z > 0.2g)
T+110s   COLETA de dados
```

---

## 📊 Validação vs Simulação

**Critérios de sucesso** (PASS se erro < 5%):

| Métrica | Simulação | Tolerância |
|---------|-----------|-----------|
| Vz impacto | 10.05 m/s | ±5% |
| Tempo voo | 100.02 s | ±3% |
| Taxa rotação | 439 rpm | ±5% |
| Energia | 12.62 J | ±10% |

---

## 📅 Deadlines

| Data | Milestone | Status |
|------|-----------|--------|
| 30/04 | Componentes procurados | ⏳ |
| 15/05 | Firmware pronto | ⏳ |
| 22/05 | Testes integração | ⏳ |
| **24/05** | **VOO TEST #3** | 🎯 |
| 31/05 | Análise completa | ⏳ |

---

## 🔴 CRÍTICO

✅ **Eletrônica é mandatória** - sem dados reais, a simulação não é validada experimentalmente
✅ **Asa2.DXF candidata** - aerodinâmica já validada
✅ **Margem existe** - 15g disponível no budget regulatório

---

## 📚 Documentação Relacionada

Ler em ordem:

1. [[2026-04-17-helike-historico-testes]] (visão geral)
2. [[2026-04-17-analise-simulacao-helike]] (técnico)
3. [[2026-04-17-plano-instrumentacao-helike-test3]] (detalhado)

## 🔗 Contexto do Projeto

- [[projeto-helike]]
- [[helike-hub]]

---

## 🚀 Ação Imediata

**HOJE**: Revisar plano de instrumentação
**ESTA SEMANA**: Iniciar sourcing de componentes
**PRÓXIMA SEMANA**: Preparar ambiente de firmware

> "Sem validação experimental, a simulação permanece hipótese técnica." - Equipe de Engenharia Helike
