# PhD · Data Science & Artificial Intelligence

Repositorio académico y sitio web para organizar el **Doctorado en Ciencia de Datos e
Inteligencia Artificial**: cursos, notebooks, talleres, quizzes, datasets, presentaciones,
notas y material de investigación.

Funciona a la vez como repositorio académico, bitácora técnica, portafolio público, sitio web
académico (Quarto + GitHub Pages) y repositorio reproducible de notebooks y experimentos.

**Sitio publicado:** <https://laverde97.github.io/phd-data-science-ai/>

## Estructura actual

- **Semestre 01**
  - **Módulo 01 · Machine Learning**
    - `assignments/` — Tareas
    - `quizzes/` — Quiz
    - `data/` — Data
    - `workshops/` — Talleres
    - `notebooks/` — Notebooks (Google Colab)
    - `presentations/` — Presentaciones
    - `notes/` — Notas
- **research/** — Trabajo de investigación doctoral
  - `literature/`, `research-questions/`, `experiments/`, `results/`,
    `meetings/`, `progress/`, `manuscripts/`, `presentations/`

Los semestres y módulos siguientes se agregarán conservando esta misma arquitectura. No se
anticipan sus nombres.

## Sitio web (Quarto)

```bash
quarto preview   # desarrollo local con recarga
quarto render    # build estático en _site/
```

La publicación es automática: cada push a `main` dispara el workflow
`.github/workflows/publish.yml`, que renderiza con Quarto y publica en la rama `gh-pages`,
servida por GitHub Pages.

## Árbol del repositorio

```text
phd-data-science-ai/
├── _quarto.yml
├── index.qmd
├── styles.css
├── assets/
│   ├── favicon.svg
│   └── logo.svg
├── research/
│   ├── index.qmd
│   ├── literature/            (index.qmd + README.md)
│   ├── research-questions/
│   ├── experiments/
│   ├── results/
│   ├── meetings/
│   ├── progress/
│   ├── manuscripts/
│   └── presentations/
├── semesters/
│   ├── index.qmd
│   └── semester-01/
│       ├── index.qmd
│       └── machine-learning/
│           ├── index.qmd
│           ├── assignments/   (index.qmd + README.md)
│           ├── quizzes/
│           ├── data/
│           ├── workshops/
│           ├── notebooks/     (index.qmd + README.md + 00-template.ipynb)
│           ├── presentations/
│           └── notes/
└── .github/workflows/publish.yml
```

## Convenciones

- Carpetas en inglés y `kebab-case`; interfaz de usuario en español.
- Numeración cronológica de dos dígitos: `01-data-preparation.ipynb`,
  `02-train-test-split.ipynb`, `assignment-01-...`, `quiz-01-...`, `workshop-01-...`,
  `presentation-01-...`.
- Cada `.ipynb` incluye un badge **Open in Colab**.

## Google Colab

```text
https://colab.research.google.com/github/Laverde97/phd-data-science-ai/blob/main/<ruta-del-notebook>
```

## Seguridad

Nunca se publican `.env`, claves de API, tokens, contraseñas, credenciales, información
personal sensible ni datasets restringidos. Cuando un dataset no puede hacerse público, se
documenta únicamente su origen, descripción, variables, esquema y procedimiento de acceso
(ver `semesters/semester-01/machine-learning/data/`).
