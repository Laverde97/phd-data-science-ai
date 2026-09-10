# Talleres — Machine Learning

Inventario de ejercicios prácticos reproducibles del módulo.

| Taller | Fecha | Enunciado | Notebook | Fuente (QMD) | Solución |
|---|---|---|---|---|---|
| 01 · Preparación de datos ICFES — CSV | 08/09/2026 | — | [Notebook](workshop-01-icfes-csv.ipynb) | — | — |
| 02 · Preparación de datos ICFES — JSON | 08/09/2026 | — | [Notebook](workshop-02-icfes-json.ipynb) | — | — |
| 03 · Regresión lineal para predicción de precios de viviendas | 10/09/2026 | Privado | [Notebook](workshop-03-regresion-lineal-viviendas.ipynb) | [QMD](workshop-03-regresion-lineal-viviendas.qmd) | [PDF](workshop-03-regresion-lineal-viviendas.pdf) |

Los tres notebooks incluyen un badge **Open in Colab** en la primera celda Markdown.

## Taller 03

Desarrolla la exploración, comparación de métodos de imputación, selección de
`IterativeImputer + BayesianRidge` y regresión lineal sobre el dataset imputado
completo, con división 80/20, evaluación y visualización de residuos.

- [Ver notebook en GitHub](https://github.com/Laverde97/phd-data-science-ai/blob/main/semesters/semester-01/machine-learning/workshops/workshop-03-regresion-lineal-viviendas.ipynb).
- [Open in Colab](https://colab.research.google.com/github/Laverde97/phd-data-science-ai/blob/main/semesters/semester-01/machine-learning/workshops/workshop-03-regresion-lineal-viviendas.ipynb).
- [Descargar fuente Quarto (.qmd)](workshop-03-regresion-lineal-viviendas.qmd).
- [Descargar solución en PDF](workshop-03-regresion-lineal-viviendas.pdf).

El Taller 03 reúne cuatro recursos: el **enunciado** original —material de clase que se conserva de forma privada y no se distribuye en este repositorio público—, el **notebook** con sus salidas, la **fuente Quarto** y la **solución en PDF**, generada desde el `.qmd`. El PDF se incorpora como archivo estático; el sitio y GitHub Actions no ejecutan el análisis ni compilan este informe. Los enlaces a `main` corresponden a las rutas finales de publicación.

## Privacidad de los talleres ICFES 01 y 02

Sus salidas públicas se retiraron porque el conjunto contiene la variable
`documento`. El código de ambos ejercicios se conserva sin cambios. Esta
observación se refiere exclusivamente a los talleres ICFES.

Ver [el inventario del sitio](index.qmd) para consultar todos los talleres.
