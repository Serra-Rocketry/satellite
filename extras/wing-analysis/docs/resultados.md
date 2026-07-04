# SRAB — Resultados e Validacao

Resultados experimentais (Testes 1-2), simulacao computacional (Teste 3),
analise de sensibilidade e benchmark vs paraquedas.

---

## 1. Testes 1 e 2 (Quedas de ~20 m)

Prototipos em queda livre a partir de drone, massa 200 g, β=8°, CD0=1,0.

| Parametro | Teste 1 (asa1.dxf, 4 asas) | Teste 2 (Asa2.DXF, 4 asas) |
|---|---|---:|---:|
| Area total das asas | 109,22 cm² | 122,28 cm² |
| Velocidade de impacto | 7,68 m/s | 8,04 m/s |
| Conicidade θ no impacto | 13,46° | 24,44° |
| Rotacao no impacto | 306,77 RPM | 306,89 RPM |
| Reynolds medio | 9.875 | 13.876 |

O aumento de 81,6% na conicidade com +12% de area revela relacao nao linear
entre area aerodinamica e torque restaurador (My3 escala com quadrado da corda).
A rotacao de equilibrio e determinada principalmente por β e massa, nao pela
area total.

---

## 2. Teste 3 — Simulacao (Asa3, 1000 m)

Parametros: 200 g, β=3°, CD0=1,0, f_factor=0,3, ρ=1,225 kg/m³.

| Parametro | Valor |
|---|---|
| Velocidade de impacto | 12,90 m/s |
| Tempo de descida | 78,03 s |
| Conicidade θ de equilibrio | 17,22° |
| Rotacao | 372 RPM |
| Energia dissipada | 99,15% |

A velocidade de 12,90 m/s esta abaixo da janela LASC (20-45 m/s) — ajustes
geometricos (2 asas, β maior, mais massa) sao necessarios para conformidade.

---

## 3. Sensibilidade a CD0

CD0 variou ±10% e ±20% — velocidade de impacto permaneceu em 12,90 m/s em
todos os casos. Uma vez estabelecido o LEV, a sustentacao sobrepuja o arrasto
de forma. Tolerancias de impressao 3D no acabamento superficial nao
comprometem a velocidade terminal.

---

## 4. Monte Carlo (200 iteracoes)

Variacao: massa 200±10 g, β=3,0±0,5°, CD0=1,0±0,10, f_factor=0,3±0,03.

| Metrica | Media ± σ | P5 | P95 |
|---|---:|---:|---:|
| Velocidade de impacto | 12,89 ± 0,20 m/s | 12,54 | 13,19 |
| Tempo de descida | 78,23 ± 1,22 s | 76,46 | 80,38 |
| Conicidade θeq | 17,48 ± 1,19° | 15,71° | 19,50° |
| Spin de equilibrio | 371 ± 8 RPM | 358 | 384 |

CV < 2% na velocidade de impacto — o regime de autorrotacao atua como
controlador aerodinamico natural rejeitando perturbacoes parametricas.

---

## 5. Benchmark SRAB vs Paraquedas

SRAB (Asa3, 4 asas) vs paraquedas flat circular ∅200 mm (CD=1,5), ambos
200 g, 1000 m.

| Parametro | SRAB | Paraquedas |
|---|---|---:|---:|
| Velocidade de impacto | 12,90 m/s | 8,25 m/s |
| Tempo de descida | 78,03 s | 118,33 s |
| Energia de impacto | 16,65 J | 6,80 J |
| Dentro da janela LASC | Nao | Nao |

SRAB e 1,6× mais rapido, completa a descida em 34% menos tempo. Vantagens
estruturais: elimina mecanismos de acionamento, molas, pirotecnia, linhas e
costuras (pontos unicos de falha). Tempo de descida menor reduz deriva por
vento.

---

## 6. Conclusoes

1. **Modelo validado qualitativamente**: transicao Asa1→Asa2 com aumento de
   81,6% na conicidade.
2. **Instrumentacao funcional**: ESP32-C3 + ICM-20602 + BMP280 + LoRa RFM95W
   a 20 Hz.
3. **Simulacao Asa3**: 12,90 m/s, dissipacao de 99,15% da energia.
4. **CD0 nao influencia** velocidade terminal (±20%, sem efeito).
5. **MC**: CV < 2%, dispersao excepcionalmente baixa.

Abaixo da janela LASC — ajustes necessarios para conformidade, mas
parametricamente simples e energeticamente seguros.
