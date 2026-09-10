# Reporte técnico de validación

Rama de trabajo: `feat/ml-linear-regression-workshop`. No se realizaron commit, push ni merge; los cambios quedan disponibles para revisión antes de un eventual commit.

## Fuente y requisitos

Se leyeron las cuatro páginas del PDF del profesor existente en `semesters/semester-01/machine-learning/workshops/Taller_Regresion_Lineal.pdf`. La ruta de Downloads indicada originalmente no estaba disponible en este entorno. Ese PDF ya estaba sin seguimiento al inicio y permanece intacto.

El PDF indica `bucket_doctorado_ueb_2026_2`; esa URL devolvió HTTP 404, `NoSuchBucket`. La URL corregida por el usuario, con **`backet_doctorado_ueb_2026_2`**, respondió **HTTP 200** y fue cargada con `pandas.read_csv`:

<https://storage.googleapis.com/backet_doctorado_ueb_2026_2/datos_viviendas_faltantes.csv>

Esta es la fuente utilizada en todo el análisis. La discrepancia se documenta aquí y no se comenta en el PDF académico. No se utilizaron datos simulados, no se reescalaron los precios y no se guardó el CSV en el repositorio.

## Datos y decisiones

- Dimensiones observadas: **100.000 filas y 2 columnas**, `tamano` y `precio`, ambas `float64`.
- Faltantes: `tamano` **10.000 (10 %)**; `precio` **5.000 (5 %)**. Total: **7,5 % de las celdas**; **14.499 filas (14,499 %)** con al menos un faltante.
- Se conservó `df` sin modificar. Se excluyeron únicamente del modelado las 5.000 filas sin precio observado; no se crearon etiquetas artificiales para entrenar o evaluar.
- Dataset de modelado: **95.000 filas**, dividido en **76.000 de entrenamiento y 19.000 de prueba** (80/20, `random_state=42`).
- Se imputó el tamaño con la **media aprendida exclusivamente en entrenamiento: 150,032139 m²**. La cercanía entre media y mediana y la asimetría pequeña respaldan la elección frente a la mediana. Se comparan conceptualmente ambas alternativas y la eliminación de filas en los entregables.
- La imputación usa `fit_transform` en entrenamiento y `transform` en prueba. El dataset de modelado tiene **cero NaN**, confirmado mediante recuentos y aserciones.
- No se eliminaron valores atípicos. Se usaron muestras de 3.000 observaciones exclusivamente para las figuras; no se redujo la muestra de entrenamiento para modelar.

## Resultados ejecutados

Los resultados siguientes proceden de `evidencias/validacion_notebook.json`; los coeficientes completos se conservaron en el modelo.

| Resultado | Valor |
|---|---:|
| Intercepto | 49.539,453922 COP |
| Pendiente | 2.504,472968 COP/m² |
| R² | 0,75308041 |
| Variabilidad explicada en prueba | 75,3080 % |
| RMSE | 60.812,91 COP |
| MAPE | 12,4216 % |
| Predicción para 150 m² | 425.210,40 COP |
| Correlación en pares completos | 0,914322 |

**Ecuación:** precio estimado (COP) = 49.539,453922 + 2.504,472968 × tamaño (m²).

El modelo explica aproximadamente el 75,31 % de la variabilidad en prueba. El RMSE resume errores en pesos y el MAPE el error absoluto relativo promedio. El grupo con tamaño imputado tiene mayor error que el grupo observado; se incluye el diagnóstico por grupo y se mantienen ambos en las métricas principales.

## Validación de los entregables

- **Notebook:** ejecución completa desde un kernel nuevo mediante `nbclient`; **28 celdas de código**, **3 figuras**, **0 errores** y ninguna salida `stderr` en las celdas. Se guardaron todas las salidas. La validación comprueba dimensiones, ausencia de NaN, partición, métricas finitas, predicción de 150 m² y actualización del widget a 160 y de regreso a 150 m².
- **Colab:** notebook autónomo, sin archivos auxiliares obligatorios ni `input()` bloqueante, con `ipywidgets` e integración condicional de Colab. La ejecución verificada fue en Jupyter local; no se abrió una sesión alojada de Google Colab. Se proporcionan instrucciones de carga manual y no se inventa un badge de un archivo todavía no publicado.
- **Quarto:** `quarto render Taller_Regresion_Lineal.qmd` terminó con código de salida **0**, ejecutando sus **28 celdas**. No se reutilizó caché de cómputo.
- **PDF:** generado directamente desde el QMD, **12 páginas**. Se revisaron visualmente todas las páginas mediante imágenes y se ampliaron las páginas de métricas, residuos y capturas. No se observaron contenidos recortados ni tablas fuera de los márgenes; código, figuras y fórmulas son legibles. Los bloques extensos pueden continuar en la página siguiente sin perder líneas.
- **Capturas:** se recortaron salidas efectivamente ejecutadas de una primera compilación del PDF y se incorporaron a la compilación final; no se dibujaron números de ejemplo.
- **Mensajes internos:** el PDF y las salidas del notebook no contienen warnings. Los logs de consola registran un aviso de arranque de `ipykernel` sobre su transporte local; no forma parte del documento académico.
- **Sitio:** se ejecutó `quarto render` completo en `/tmp/ml-workshop-site-check`, una copia aislada que excluyó `.git`, `.quarto` y `_site` originales. Finalizó con código **0**, procesando **28 fuentes QMD** y generando **27 páginas HTML más el PDF del taller**. Se verificaron **1.022 referencias locales** en HTML, sin destinos ausentes. PDF y notebook están disponibles en la salida del sitio. Esta comprobación verifica destinos de archivos, no todos los fragmentos de ancla ni enlaces externos.
- **Coherencia:** los 27 bloques compartidos de Python del QMD coinciden con los del notebook; la última celda difiere por diseño (capturas estáticas en PDF, widget en notebook). Las métricas del PDF coinciden con las del notebook.

Evidencias: `evidencias/validacion_notebook.json`, `evidencias/validacion_archivos.json`, capturas PNG y `evidencias/entorno-validado.txt`. El log local de Quarto es `evidencias/render-quarto.log` (ignorado por Git).

## Entorno

Se utilizó Quarto 1.9.38 y Python 3.14.4 en `/tmp/ml-workshop-venv`. TinyTeX 2026.09 se extrajo en `/tmp/ml-workshop-tools/.TinyTeX`; se usó LuaLaTeX mediante un `PATH` limitado a los comandos de render. Las dependencias y los paquetes LaTeX se instalaron en ubicaciones temporales, sin cambiar configuraciones globales. Las versiones exactas de Python están registradas en la evidencia del entorno.

La configuración local `_quarto.yml` permite renderizar el taller como documento PDF independiente. Quarto administra sus archivos internos de caché; no se almacenaron fuentes ni entregables del taller dentro de `.quarto`.

## Archivos y alcance Git

Todos los archivos nuevos del taller se encuentran en:

`semesters/semester-01/machine-learning/workshops/taller-regresion-lineal/`

Principales: `Taller_Regresion_Lineal.ipynb`, `Taller_Regresion_Lineal.qmd`, `Taller_Regresion_Lineal.pdf`, `README.md` y este reporte. Se añaden configuración local, dependencias, scripts de sincronización/validación/captura y evidencias. El único archivo previamente versionado modificado es `semesters/semester-01/machine-learning/workshops/index.qmd`: una fila nueva con enlaces relativos al PDF y al notebook. No se cambió la navegación global.

Ruta exacta del PDF en Windows:

`C:\Users\USUARIO\Documents\DOCTORADO\MODULOS\PRIMER SEMESTRE\phd-data-science-ai\semesters\semester-01\machine-learning\workshops\taller-regresion-lineal\Taller_Regresion_Lineal.pdf`

Estado de Git antes de cualquier commit:

```text
 M semesters/semester-01/machine-learning/workshops/index.qmd
?? semesters/semester-01/machine-learning/workshops/Taller_Regresion_Lineal.pdf
?? semesters/semester-01/machine-learning/workshops/taller-regresion-lineal/
```

El segundo renglón corresponde al PDF original que ya estaba sin seguimiento. `git diff --check` no detectó problemas de espacios. No se preparó el índice de Git ni se incluyó el PDF original en un commit.
