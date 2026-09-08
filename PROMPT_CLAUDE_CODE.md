# Prompt maestro para Claude Code

Quiero que trabajes como **Senior Software Engineer + Research Software Engineer + diseñador de sitios académicos con Quarto**.

Tu misión es crear y mantener un repositorio GitHub llamado **`phd-data-science-ai`** para documentar profesionalmente mi **Doctorado en Ciencia de Datos e Inteligencia Artificial**.

El repositorio debe funcionar simultáneamente como:

1. repositorio académico organizado;
2. bitácora técnica del doctorado;
3. portafolio público de aprendizaje e investigación;
4. sitio web profesional publicado con **Quarto + GitHub Pages**.

## Identidad del proyecto

- GitHub owner: `Laverde97`
- Repository: `phd-data-science-ai`
- Idioma principal de navegación/contenido: español.
- Nombres técnicos de carpetas: inglés, `kebab-case`.
- Estética: académica, moderna, minimalista, elegante, profesional y orientada a Data Science/AI.
- Debe soportar light mode y dark mode.
- Evita una estética infantil, excesivamente colorida o llena de efectos.

## Estructura académica inicial

Actualmente solo debes crear:

- **Semestre 1**
  - **Módulo 1: Machine Learning**

NO inventes los nombres de módulos futuros. La arquitectura sí debe quedar preparada para agregarlos después.

Dentro de cada módulo deben existir estas categorías:

- `assignments/` → Tareas
- `quizzes/` → Quiz
- `data/` → Data
- `workshops/` → Talleres
- `notebooks/` → Notebooks Google Colab
- `presentations/` → Presentaciones
- `notes/` → Notas de estudio

Además debe existir una sección separada:

- `research/` → investigación doctoral, literatura, experimentos y avances.

## Website

Construye un sitio Quarto con:

- portada tipo academic/research dashboard;
- navbar fija;
- hero elegante;
- tarjetas para semestre, módulo y recursos;
- navegación Semestre 1 -> Machine Learning;
- página de Research Track;
- diseño responsive;
- excelente tipografía y whitespace;
- enlaces al repositorio GitHub;
- footer profesional;
- CSS personalizado;
- accesibilidad razonable;
- sin dependencias innecesarias.

La portada debe transmitir que no es solo almacenamiento de archivos sino una **doctoral learning hub / research learning journal**.

## Machine Learning

La página del módulo debe mostrar visualmente tarjetas para:

- Tareas
- Quiz
- Data
- Talleres
- Notebooks / Colab
- Presentaciones
- Notas

Incluye una tabla de progreso editable, pero marca cualquier contenido no confirmado como provisional. No inventes calificaciones ni resultados.

## Google Colab

Cada notebook `.ipynb` que se agregue debe incluir un badge "Open in Colab" que apunte a:

`https://colab.research.google.com/github/Laverde97/phd-data-science-ai/blob/main/<ruta-del-notebook>`

Si encuentras notebooks existentes, agrega el badge sin modificar innecesariamente su contenido científico.

## Seguridad y datos

- Nunca subas `.env`, tokens, claves o credenciales.
- Nunca publiques datos sensibles o privados.
- Si un dataset no debe hacerse público, crea un README con la fuente, esquema esperado y forma de obtenerlo, pero no copies los datos.
- Revisa licencias antes de redistribuir datasets o diapositivas de terceros.

## GitHub Pages

Configura publicación automática con GitHub Actions y Quarto.

Usa una estrategia mantenible con:

- `actions/checkout@v7`
- `quarto-dev/quarto-actions/setup@v2`
- `quarto-dev/quarto-actions/publish@v2`
- target `gh-pages`
- `GITHUB_TOKEN`

Mantén `main` como rama principal de trabajo y `gh-pages` para la publicación generada.

## Archivos mínimos

Crea como mínimo:

- `README.md`
- `_quarto.yml`
- `index.qmd`
- `styles.css`
- `CLAUDE.md`
- `.gitignore`
- `.github/workflows/publish.yml`
- `semesters/semester-01/index.qmd`
- `semesters/semester-01/machine-learning/index.qmd`
- todas las carpetas de recursos del módulo con sus README
- `research/index.qmd`

## Convenciones

Usa prefijos numéricos cuando el contenido tenga orden:

- `01-data-preparation.ipynb`
- `02-train-test-split.ipynb`
- `assignment-01-...`
- `quiz-01-...`
- `workshop-01-...`
- `presentation-01-...`

## Flujo de trabajo

1. Antes de cambiar nada, inspecciona el directorio actual.
2. Si el repositorio GitHub todavía no existe y `gh` está autenticado, créalo público con:
   `gh repo create Laverde97/phd-data-science-ai --public --source=. --remote=origin`
3. Crea la arquitectura.
4. Implementa la web.
5. Ejecuta `quarto render`.
6. Corrige todos los errores de renderizado y enlaces internos.
7. Revisa `git diff` y evita archivos basura.
8. Realiza un commit limpio.
9. Haz push a `main` únicamente si el entorno está autenticado y tengo permisos.
10. Comprueba GitHub Actions y reporta cualquier ajuste manual requerido para habilitar Pages.

## Restricciones importantes

- No borres materiales existentes sin necesidad.
- No inventes contenido académico.
- No alteres notebooks científicos si no es necesario.
- No hagas commits de secretos.
- No publiques datasets restringidos.
- No uses lorem ipsum.
- No dejes enlaces rotos.
- No uses emojis de forma excesiva; como máximo úsalos discretamente en tarjetas de recursos.

## Entrega final

Al terminar, dame:

1. árbol final del repositorio;
2. archivos creados/modificados;
3. resultado de `quarto render`;
4. estado de `git status`;
5. commit creado;
6. URL del repositorio;
7. URL esperada de GitHub Pages;
8. cualquier paso manual que falte.

Empieza trabajando directamente sobre el proyecto y completa todo lo que puedas sin detenerte a preguntarme por decisiones menores.
