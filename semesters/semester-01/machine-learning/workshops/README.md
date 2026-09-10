# Talleres — Machine Learning

Inventario de ejercicios prácticos reproducibles del módulo.

| Taller | Fecha | Notebook | Informe |
|---|---|---|---|
| 01 · Preparación de datos ICFES — CSV | 08/09/2026 | [Notebook](workshop-01-icfes-csv.ipynb) | — |
| 02 · Preparación de datos ICFES — JSON | 08/09/2026 | [Notebook](workshop-02-icfes-json.ipynb) | — |
| 03 · Regresión lineal para predicción de precios de viviendas | 10/09/2026 | [Notebook](workshop-03-regresion-lineal-viviendas.ipynb) | [PDF](workshop-03-regresion-lineal-viviendas.pdf) |

Los tres notebooks incluyen un badge **Open in Colab** en la primera celda Markdown.

## Taller 03

Desarrolla la exploración, comparación de métodos de imputación, selección de
`IterativeImputer + BayesianRidge` y regresión lineal sobre el dataset imputado
completo, con división 80/20, evaluación y visualización de residuos.

- [Ver notebook en GitHub](https://github.com/Laverde97/phd-data-science-ai/blob/main/semesters/semester-01/machine-learning/workshops/workshop-03-regresion-lineal-viviendas.ipynb).
- [Open in Colab](https://colab.research.google.com/github/Laverde97/phd-data-science-ai/blob/main/semesters/semester-01/machine-learning/workshops/workshop-03-regresion-lineal-viviendas.ipynb).
- [Descargar informe PDF](workshop-03-regresion-lineal-viviendas.pdf).

El notebook conserva sus resultados. El informe se genera externamente desde el
QMD definitivo y se incorpora como PDF estático; el sitio y GitHub Actions no
necesitan ejecutar el análisis ni compilar este informe. Los enlaces a `main`
corresponden a las rutas finales de publicación.

## Privacidad de los talleres ICFES 01 y 02

Sus salidas públicas se retiraron porque el conjunto contiene la variable
`documento`. El código de ambos ejercicios se conserva sin cambios. Esta
observación se refiere exclusivamente a los talleres ICFES.

Ver [el inventario del sitio](index.qmd) para consultar todos los talleres.
