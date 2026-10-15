# Fuentes de las guías académicas — Semana 02 · Clase 02

Fuentes Quarto de las cuatro guías PDF publicadas en `../resources/guides/`. Las guías son
**ediciones públicas** elaboradas por Juan Sebastián Laverde Chunza con apoyo de herramientas de
inteligencia artificial generativa, a partir de los notebooks de la Clase 02 del profesor Héctor
Javier Hortúa, PhD. Su código, sus datos y sus explicaciones son propios. No son material oficial del
docente ni de la Universidad El Bosque. Citar los notebooks como referencia no equivale a una
licencia sobre el material original.

| Fuente | PDF publicado |
|--------|---------------|
| `01_Guia_Academica_Regresion_TensorFlow.qmd` | `../resources/guides/01_Guia_Academica_Regresion_TensorFlow.pdf` |
| `02_Guia_Academica_Clasificacion_PyTorch.qmd` | `../resources/guides/02_Guia_Academica_Clasificacion_PyTorch.pdf` |
| `03_Guia_Academica_Pipeline_MNIST_TensorFlow.qmd` | `../resources/guides/03_Guia_Academica_Pipeline_MNIST_TensorFlow.pdf` |
| `04_Guia_Academica_Series_Temporales_Lightning_Keras_JAX.qmd` | `../resources/guides/04_Guia_Academica_Series_Temporales_Lightning_Keras_JAX.pdf` |

Archivos de apoyo:

- `_quarto.yml`: formato PDF (KOMA-Script, LuaLaTeX, TeX Gyre) y la opción de ejecutar el código.
- `guide-style.tex`: encabezados, pies, colores y ajuste de líneas largas de código.
- `requirements.txt`: versiones exactas del entorno con el que se generaron los PDF.

## El sitio no ejecuta estas fuentes

`_quarto.yml` (en la raíz del repositorio) excluye esta carpeta del render. GitHub Pages no ejecuta
ningún entrenamiento: publica los PDF ya generados de `../resources/guides/`.

## Cómo regenerar las guías

Las guías ejecutan su código al compilarse. Hacen entrenamientos cortos en CPU (unos cuatro minutos
en total), y la guía 03 descarga MNIST con `tensorflow_datasets` la primera vez.

```bash
# 1. Copiar esta carpeta fuera del repositorio, para que Quarto no la trate como parte del sitio
cp -r guides-source /tmp/guias && cd /tmp/guias

# 2. Crear el entorno
python3.12 -m venv .venv
.venv/bin/pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# 3. Compilar (requiere Quarto >= 1.4 y TinyTeX: `quarto install tinytex`)
QUARTO_PYTHON=.venv/bin/python quarto render 01_Guia_Academica_Regresion_TensorFlow.qmd
# ... o las cuatro: for f in 0*.qmd; do QUARTO_PYTHON=.venv/bin/python quarto render "$f"; done
```

Los PDF quedan en `_out/`.

## Reproducibilidad

- **Semillas.** Cada guía las fija en su código: `keras.utils.set_random_seed`, `torch.manual_seed`,
  `L.seed_everything` y generadores de NumPy y PyTorch con semilla explícita. Con este entorno, dos
  ejecuciones dieron cifras idénticas.
- **PDF regenerados.** No serán idénticos byte a byte a los publicados: cambian las marcas de tiempo,
  y otro *hardware* u otras versiones de las bibliotecas pueden variar algunas cifras en los últimos
  decimales. Las conclusiones se escriben con expresiones en línea de Quarto, así que siempre reflejan
  los valores de la ejecución en curso.
- **Archivos temporales.** La guía 04 escribe *checkpoints* de Lightning en la carpeta de trabajo y
  las demás usan directorios temporales del sistema. `.gitignore` evita versionar esos archivos.
