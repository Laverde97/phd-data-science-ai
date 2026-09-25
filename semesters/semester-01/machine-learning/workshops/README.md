# Talleres — Machine Learning

Inventario de ejercicios prácticos reproducibles del módulo.

| Taller | Fecha | Enunciado | Notebook | Fuente (QMD) | Solución |
|---|---|---|---|---|---|
| 01 · Preparación de datos ICFES — CSV | 08/09/2026 | — | [Notebook](workshop-01-icfes-csv.ipynb) | — | — |
| 02 · Preparación de datos ICFES — JSON | 08/09/2026 | — | [Notebook](workshop-02-icfes-json.ipynb) | — | — |
| 03 · Regresión lineal para predicción de precios de viviendas | 10/09/2026 | Privado | [Notebook](workshop-03-regresion-lineal-viviendas.ipynb) | [QMD](workshop-03-regresion-lineal-viviendas.qmd) | [PDF](workshop-03-regresion-lineal-viviendas.pdf) |
| 04 · Regresión lineal múltiple: selección de variables con OLS | 14/09/2026 | — | [Notebook](workshop-04-regresion-multiple-seleccion-variables.ipynb) | — | — |
| 05 · Árboles de Decisión para Regresión — California Housing | 16/09/2026 | Privado | [Notebook](workshop-05-arbol-decision-california-housing.ipynb) | — | [PDF](workshop-05-arbol-decision-california-housing.pdf) |
| 06 · Random Forest vs. Árbol de Decisión para Regresión | 17/09/2026 | — | [Notebook](workshop-06-random-forest-vs-arbol-decision-regresion.ipynb) | — | — |
| 07 · Árbol de Decisión para Clasificación — Cáncer de Mama (Entropía) | 20/09/2026 | — | [Notebook](workshop-07-arbol-decision-clasificacion-cancer-mama.ipynb) | — | — |

Los siete notebooks incluyen un badge **Open in Colab** en la primera celda Markdown.

## Taller Final

Segmentación inteligente de servicios clínicos mediante PCA y K-Means (25/09/2026).
Los resultados provienen de una base de datos MySQL de solo lectura; el notebook
público no contiene la contraseña (usa Colab Secrets o `getpass`).

- [SQL](taller-final/Taller_Final_Clinica_ML.sql) — consultas de solo lectura.
- [Colab](https://colab.research.google.com/github/Laverde97/phd-data-science-ai/blob/main/semesters/semester-01/machine-learning/workshops/taller-final/Taller_Clinica_Machine_Learning_LAVERDE.ipynb) — [notebook](taller-final/Taller_Clinica_Machine_Learning_LAVERDE.ipynb) con sus salidas.
- [PDF](taller-final/Taller_Final_Segmentacion_Clinica_PCA_KMeans.pdf) — informe generado con Quarto.

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
