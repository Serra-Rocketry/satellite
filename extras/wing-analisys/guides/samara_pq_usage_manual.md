# Manual de Uso — Samara PQ Simulation

Este manual descreve como usar o pipeline de simulação de autorrotação em:

- `extras/wing-analisys/src/samara_pq_simulation.py`

## 1) Pré-requisitos

No diretório raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy scipy matplotlib ezdxf black pylint
```

## 2) Execução automática (pipeline completo)

Roda otimização (impacto alvo), simulação, relatório e gráficos:

```bash
source .venv/bin/activate
python extras/wing-analisys/src/samara_pq_simulation.py
```

Saídas padrão em `extras/wing-analisys/`:

- `samara_pq_impact_report.json`
- `samara_pq_impact_report.txt`
- `samara_pq_lrr_report.png`
- `samara_pq_frontal_area.png`

## 3) Como analisar outros arquivos DXF

### 3.1 Analise geometrica isolada (sem script auxiliar)

Atualmente nao existe `analisar_dxf.py` no repositorio.
Para inspecionar apenas geometria e area, use a classe `DxfWingProfile` diretamente:

```bash
source .venv/bin/activate
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); prof=m.DxfWingProfile('extras/wing-analisys/geometry/Asa2.DXF'); print('r0_m=', round(prof.r0_m,6)); print('rf_m=', round(prof.rf_m,6)); print('area_one_wing_m2=', round(prof.area_one_wing_m2,8))"
```

### 3.2 Rodar simulação com outro DXF sem alterar o código-fonte

Exemplo com `asa1.dxf`:

```bash
source .venv/bin/activate
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/asa1.dxf', n_wings=4); d=m.PocketQubeFlightDynamics(w); sol=d.simulate_drop(t_span=(0.0,600.0), max_step=0.2); r=m.PocketQubeMissionReporter(w, sol); summ=r.build_summary(); r.print_summary(summ); r.save_report_files(summ); m.plot_frontal_area_system(w); v=m.PocketQubeLRRVisualizer(sol); v.generate_lrr_report()"
```

## 4) Rodar com `radius_scale` fixo

Para usar escala fixa sem otimização:

```bash
source .venv/bin/activate
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); scale=1.3; w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/Asa2.DXF', n_wings=4); radius=w.base_rf*scale; w.update_geometry(radius, w.f_factor, w.cd0, n_wings=4); d=m.PocketQubeFlightDynamics(w); sol=d.simulate_drop(t_span=(0.0,600.0), max_step=0.2); r=m.PocketQubeMissionReporter(w, sol); summ=r.build_summary(); r.print_summary(summ); r.save_report_files(summ); m.plot_frontal_area_system(w); v=m.PocketQubeLRRVisualizer(sol); v.generate_lrr_report(); print(f'radius_scale={w.radius_scale:.3f}, radius_m={radius:.6f}')"
```

Para o caso solicitado de escala original:

- use `scale=1.0`

## 5) Como mudar `n_wings`

No mesmo comando inline, altere:

- `n_wings=4` para `n_wings=2` (ou outro valor inteiro desejado)

Exemplo (`n_wings=2`, `radius_scale=1.0`):

```bash
source .venv/bin/activate
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/Asa2.DXF', n_wings=2); radius=w.base_rf*1.0; w.update_geometry(radius, w.f_factor, w.cd0, n_wings=2); d=m.PocketQubeFlightDynamics(w); sol=d.simulate_drop(t_span=(0.0,600.0), max_step=0.2); r=m.PocketQubeMissionReporter(w, sol); summ=r.build_summary(); r.print_summary(summ)"
```

## 6) Otimização para velocidade de impacto alvo

O fluxo automático já usa:

- `optimize_radius_for_impact(...)`

Se quiser executar manualmente:

```bash
source .venv/bin/activate
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/Asa2.DXF', n_wings=4); d=m.PocketQubeFlightDynamics(w); o=m.PocketQubeSamaraOptimizer(d, target_vf=-25.0); r=o.optimize_radius_for_impact(n_wings=4, target_impact_vf=-25.0, sim_t_span=(0.0,600.0), sim_max_step=0.2); print('optimal_radius_m=', r)"
```

## 7) Boas práticas para comparar cenários

Para comparações justas, mantenha constantes:

- `t_span`
- `max_step`
- arquivo DXF
- parâmetros aerodinâmicos internos

Mude apenas um fator por vez (`radius_scale`, `n_wings`, ou geometria).

## 8) Solucao de problemas comum

1. **Erro de arquivo DXF não encontrado**
   - Verifique maiúsculas/minúsculas (Linux diferencia `extras/wing-analisys/geometry/Asa2.DXF` de `asa2.dxf`).

2. **Resultados divergentes entre otimização e relatório final**
   - Use os mesmos `t_span` e `max_step` em ambas etapas.

3. **Dependência ausente (`ezdxf`)**
   - Instale no `.venv`:

     ```bash
     .venv/bin/pip install ezdxf
     ```

## 9) Qualidade de código

Para verificar formatação e lint:

```bash
source .venv/bin/activate
black extras/wing-analisys/src/samara_pq_simulation.py
pylint extras/wing-analisys/src/samara_pq_simulation.py
```
