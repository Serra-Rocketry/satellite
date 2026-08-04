# AGENTS.md

## What this is

Mission Report (LASC 2026, 7th Latin American Space Challenge) for the Helike #213 PocketQube (1P, 50×50×50 mm) from Serra Rocketry (IPRJ-UERJ). Language is English (required by LASC/AIAA style). Built from the official LASC Mission Report template, broken into one `.tex` file per section.

## Build

```bash
latexmk -pdf main.tex
```

Output: `main.pdf` in this folder. `latexmk` handles all passes automatically (no bibliography tool needed — references are hand-formatted per AIAA style, no `.bib`).

## File layout

| Path | Role |
|---|---|
| `main.tex` | Document entry point. Preamble (pandoc/AIAA style), title, `\input`s for every section, appendices. |
| `sec-frontmatter.tex` | Abstract + Authors + Nomenclature. |
| `sec-introduction.tex` | §1 Introduction. |
| `sec-architecture.tex` | §2 System Architecture and Concept of Operations (subsections: Architecture, Subsystems, ConOps). |
| `sec-weights-measures.tex` | §3 Weights, Measures, and Performance Data. |
| `sec-computational-simulation.tex` | §4 Computational Simulation (Theory, Methodology, Results). |
| `sec-conclusions.tex` | §5 Conclusions and Lessons Learned. |
| `sec-references.tex` | §6 References (AIAA format examples from template). |
| `sec-appendix-hazard.tex` | Appendix A: Hazard Analysis. |
| `sec-appendix-risk.tex` | Appendix B: Risk Assessment. |
| `sec-appendix-drawings.tex` | Appendix C: Engineering Drawings and Optional. |
| `sec-procedure.tex`, `sec-guidelines.tex`, `sec-formatting.tex` | Template guidance sections. NOT included in `main.tex` (commented out) — reference while writing, delete before submission. |
| `main_backup.tex` | Pristine copy of the original LASC template. Do not edit. |
| `figures/` | Images for the report (empty until figures are added). |

## Conventions agents must follow

- **Section numbering is manual**: each section file opens with `\begin{enumerate}` + `\def\labelenumi{\arabic{enumi}.}` + `\setcounter{enumi}{N}` + `\item \textbf{Title}`. The counters are: Introduction=0 (auto), Architecture=1, Weights/Measures=2, Simulation=3, Conclusions=4, References=5. Keep them in sync.
- **Subsections use `\subsection` / `\subsubsection`** with `\setcounter{secnumdepth}{-\maxdimen}` active (no auto numbering — titles appear bold, unnumbered). Matches AIAA style.
- **English only** in the report body. Comments/TODOs may be in Portuguese (team's working language).
- **Content source**: `Second-brain/01_Projetos_Ativos/helike-mission-report.md` holds the full mission context (architecture, SRAB recovery data, test results, FMECA). Each section file has `% TODO:` comments mapping to that source.
- **Unit formatting**: use `~` for non-breaking spaces before units (e.g. `10.05~m/s`, `122.28~cm²`). Decimal separator is dot (English).
- **References follow AIAA style** exactly as the template examples in `sec-references.tex` (author, title, source, Vol./No., year, pages, doi).
- **Do not include** `sec-procedure.tex`, `sec-guidelines.tex`, `sec-formatting.tex` in the final document — they are template instructions, not report content.
- **Do not touch `main_backup.tex`** — it is the pristine template reference.

## Style quirks to know

- The preamble comes from pandoc's AIAA-ish template: `\setcounter{secnumdepth}{-\maxdimen}` removes auto numbering; `microtype` is loaded with `expansion=false` (required — the default causes a pdfTeX error with `lmex10` fonts); `soul`/`lua-ul` provide `\hl`.
- `\hl{...}` was used in the original template to mark placeholders (e.g. team name). Filled values should drop the `\hl` wrapper.
- `\pandocbounded` (defined in preamble) is the safe way to include figures scaled to the page. Figures live in `figures/`; reference with relative path `figures/name.png` or set `\graphicspath`.
