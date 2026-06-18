# Quickstart — Samara PQ

Guia rápido com comandos prontos para os fluxos mais comuns.

## 1) Ativar ambiente

```bash
cd /home/viniciusmonnerat/Documentos/Projetos/satellite
source .venv/bin/activate
```

## 2) Rodar pipeline automático completo

```bash
python extras/wing-analisys/src/samara_pq_simulation.py
```

Gera:

- `extras/wing-analisys/samara_pq_impact_report.json`
- `extras/wing-analisys/samara_pq_impact_report.txt`
- `extras/wing-analisys/samara_pq_lrr_report.png`
- `extras/wing-analisys/samara_pq_frontal_area.png`

## 3) Rodar com `radius_scale` fixo (exemplo 1.0)

```bash
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/Asa2.DXF', n_wings=4); scale=1.0; radius=w.base_rf*scale; w.update_geometry(radius, w.f_factor, w.cd0, n_wings=4); d=m.PocketQubeFlightDynamics(w); sol=d.simulate_drop(t_span=(0.0,600.0), max_step=0.2); r=m.PocketQubeMissionReporter(w, sol); summ=r.build_summary(); r.print_summary(summ); r.save_report_files(summ); m.plot_frontal_area_system(w); v=m.PocketQubeLRRVisualizer(sol); v.generate_lrr_report(); print(f'radius_scale={w.radius_scale:.3f}, radius_m={radius:.6f}')"
```

## 4) Mudar `n_wings` (exemplo `n_wings=2`, `radius_scale=1.0`)

```bash
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/Asa2.DXF', n_wings=2); radius=w.base_rf*1.0; w.update_geometry(radius, w.f_factor, w.cd0, n_wings=2); d=m.PocketQubeFlightDynamics(w); sol=d.simulate_drop(t_span=(0.0,600.0), max_step=0.2); r=m.PocketQubeMissionReporter(w, sol); summ=r.build_summary(); r.print_summary(summ)"
```

## 5) Trocar arquivo DXF (exemplo `asa1.dxf`)

```bash
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/asa1.dxf', n_wings=4); d=m.PocketQubeFlightDynamics(w); sol=d.simulate_drop(t_span=(0.0,600.0), max_step=0.2); r=m.PocketQubeMissionReporter(w, sol); summ=r.build_summary(); r.print_summary(summ)"
```

## 6) Otimizar raio para `vf_impact` alvo

```bash
python -c "import importlib.util; p='extras/wing-analisys/src/samara_pq_simulation.py'; s=importlib.util.spec_from_file_location('m', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.PocketQubeSamaraWing(dxf_path='extras/wing-analisys/geometry/Asa2.DXF', n_wings=4); d=m.PocketQubeFlightDynamics(w); o=m.PocketQubeSamaraOptimizer(d, target_vf=-25.0); r=o.optimize_radius_for_impact(n_wings=4, target_impact_vf=-25.0, sim_t_span=(0.0,600.0), sim_max_step=0.2); print('optimal_radius_m=', r)"
```

## 7) Validar formatação/lint

```bash
black extras/wing-analisys/src/samara_pq_simulation.py
pylint extras/wing-analisys/src/samara_pq_simulation.py
```

## 8) Diagnóstico rápido

- `extras/wing-analisys/geometry/Asa2.DXF` e `asa2.dxf` são diferentes no Linux.
- Para comparar cenários, mantenha fixos `t_span` e `max_step`.
- Se faltar dependência:

```bash
.venv/bin/pip install ezdxf numpy scipy matplotlib
```
