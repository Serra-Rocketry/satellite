# Considerações Finais — Samara PQ Simulation

## 1) Estado atual do pipeline

O script `extras/wing-analisys/samara_pq_simulation.py` está consolidado em um pipeline único com:

- leitura geométrica via DXF (perfil de asa);
- dinâmica reduzida com foco em autorrotação (pitch, rotação e descida vertical);
- otimização opcional de raio para velocidade de impacto alvo;
- geração automática de relatórios (`.json` e `.txt`) e gráficos (`LRR` e área frontal);
- diagnósticos adicionais de Reynolds médio e consistência energética.

Isso mantém baixo custo computacional, preservando boa previsibilidade para estudos comparativos de geometria.

## 2) Modelo físico e fidelidade

O modelo é intencionalmente reduzido (não é 6DOF completo), mas já inclui mecanismos para evitar resultados excessivamente otimistas:

- saturação suave de `Cl` em alto ângulo de ataque;
- perdas aerodinâmicas simplificadas (eficiência, ponta de asa, arrasto induzido/perfil/rotação);
- projeção vertical com fator de desalinhamento simplificado;
- amortecimento rotacional para conter crescimento de `phi_dot`.

Mesmo assim, os resultados continuam dependentes dos parâmetros de calibração e da qualidade do DXF de entrada.

## 3) Diagnósticos de confiança

Os principais indicadores para validar plausibilidade em cada rodada são:

- `Impact speed` e `Vertical speed vz` (devem ser coerentes em magnitude);
- `Angular speed` (rad/s e rpm) em faixa crível para o envelope do sistema;
- `Mean Reynolds number` na faixa esperada para baixa escala;
- balanço de energia (`potencial inicial`, `cinética final`, `dissipada`) sem violação física.

Se houver divergência grande entre otimização e relatório final, verificar **consistência de `max_step` e `t_span`** entre as duas etapas.

## 4) Interpretação dos resultados

- Redução de `n_wings` tende a reduzir área aerodinâmica total e aumentar taxa de queda.
- Aumento de `radius_scale` tende a aumentar sustentação/arrasto total e reduzir taxa de descida.
- Geometrias DXF diferentes (ex.: `asa1.dxf` vs `Asa2.DXF`) alteram fortemente estabilidade, rpm e velocidade terminal.

O uso do pipeline para comparação relativa entre configurações é robusto, desde que as condições numéricas sejam mantidas iguais.

## 5) Limitações conhecidas

- não há acoplamento translacional lateral completo (modelo focado em descida vertical);
- termo de desalinhamento/roll é simplificado (equivalente de baixa ordem);
- inflow induzido é simplificado (parâmetro tunável);
- otimização de impacto é sensível ao intervalo de busca e aos parâmetros fixos de perdas.

## 6) Recomendações práticas de uso

1. Sempre registrar: DXF, `n_wings`, `radius_scale`, `t_span`, `max_step`.
2. Comparar cenários mantendo os mesmos parâmetros numéricos.
3. Calibrar primeiro por tendência (ordem de grandeza), depois por refinamento fino.
4. Usar o relatório de energia como sanity check em toda iteração.

## 7) Próximos passos sugeridos

- criar presets de calibração (ex.: conservador, nominal, agressivo);
- incluir sweep automatizado de `radius_scale` e `n_wings` com tabela de resultados;
- opcionalmente adicionar export CSV consolidado para análise estatística.
