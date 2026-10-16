# Distribución pública ligera — Tarea 01 · CUB-200-2011

Esta carpeta es la **edición pública** del paquete académico `ENTREGA_CUB200_TAREA01.zip` (64 archivos, 16/10/2026).
Contiene los **42 archivos** del paquete que se pueden redistribuir: código fuente, scripts, pruebas, documentación
metodológica, registros de ejecución, metadatos y listados de entorno. Todos se copiaron **sin modificar**.

La solución, el código y la documentación son trabajo académico propio de Juan Sebastián Laverde Chunza. El enunciado de la
tarea es del docente Héctor Javier Hortúa, PhD:
[`Tarea_multimodal_CUB-200-2011.md`](https://github.com/MAESTRiA-ESTADiS-CIENCIA-DATOS-Bosque/Deep_Learning_I_Fundamentos/blob/main/tareas/Tarea_multimodal_CUB-200-2011.md).

## Incluido

| Ruta | Contenido |
|------|-----------|
| `README.md` | Documento principal del proyecto: objetivo, contrato de salida, entorno, comandos y límites |
| `requirements.txt` | Dependencias compartidas (no fija una instalación GPU universal) |
| `src/cub200/` | `common`, `prepare`, `quality`, `pytorch_pipeline` y `tensorflow_pipeline` |
| `scripts/` | `preflight`, `prepare`, `validate`, exportación y comparación de firmas, y auditoría de *bounding boxes* |
| `tests/` | Pruebas unitarias y *smoke tests* (8 pasan y 1 se omite por entorno) |
| `docs/*.md` | Decisiones metodológicas, validación realizada, validación cruzada, corrección de *bounding boxes*, guía paso a paso, *checklist*, cierre y registro de correcciones |
| `logs/` | 13 registros de las ejecuciones en WSL |
| `artifacts/metadata.json` | Semilla, conteos, vocabulario, `max_len`, definición de la geometría y políticas |
| `artifacts/reports/environment/` | Paquetes efectivos de los entornos `.venv` (PyTorch) y `.venv-tf` (TensorFlow) |
| `preparar_entrega_CUB200.py` | Generador del paquete académico |

## No incluido, y por qué

| Archivo(s) | Motivo |
|------------|--------|
| `data/` (11.788 JPG, anotaciones y 11.788 TXT de *captions*) | Datos de terceros. Se descargan de Caltech y del repositorio de Reed et al. (ver `README.md`) |
| `artifacts/manifest.csv`, `tabular.npy`, `bbox_clipping_audit.csv`, `geometry_scaler.joblib` | Derivados de las anotaciones de CUB-200-2011 |
| `artifacts/text_ids.npy`, `text_lengths.npy`, `vocab.json` | Derivados de las *captions*; con el vocabulario se puede reconstruir el texto |
| `artifacts/reports/signatures/*.npz` | Firmas con *captions* codificadas y atributos anotados |
| `artifacts/reports/bbox_top5.png` | Cinco fotografías de CUB-200-2011 |
| `docs/Informe_Tecnico_CUB200_Deep_Learning_I.{pdf,docx}` | La Figura 2 tiene cinco fotografías. Se publica una edición pública (ver abajo) |
| `docs/GUIA_PROFESIONAL.pdf` | Guía de trabajo preliminar, reemplazada por la documentación final |
| `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb` | Sus salidas tienen fotografías, una *caption* y una ruta local. Se publica una edición pública (ver abajo) |
| `notebooks/01_*.ipynb`, `02_informe_ejecutable_CUB200.ipynb`, `02_*_revision_academica.ipynb` | Versiones históricas, no canónicas |
| `.gitignore`, `LEEME_ENTREGA.txt`, `MANIFEST_SHA256.txt` | Archivos de empaquetado del ZIP. El `.gitignore` ignora `artifacts/` |

Caltech indica que no posee los derechos de las fotografías de CUB-200-2011 y restringe su uso a la investigación y la
educación no comercial. Los términos de los datos de las *captions* no son explícitos. Por eso esta distribución no
incluye ningún archivo que contenga esos datos o derive de ellos. No se ha hecho una revisión jurídica.

Sin los artefactos excluidos, el notebook y `scripts/validate.py` **no se pueden ejecutar** solo con esta carpeta.
Hay que descargar los datos originales y ejecutar `scripts/prepare.py`, como describen `README.md` y
`docs/GUIA_PASO_A_PASO.md`.

## Ediciones públicas derivadas

| Original del paquete (SHA-256) | Edición pública | Cambios |
|--------------------------------|-----------------|---------|
| `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb` (`9d6f3525…08711`) | `../workshop-01-cub200-multimodal.ipynb` | Celda inicial de aviso con *badge* Colab. Salidas: ruta local reemplazada, fotografía y texto de la *caption* omitidos, figura de cinco fotografías omitida. Código, texto y contadores de ejecución intactos |
| `docs/Informe_Tecnico_CUB200_Deep_Learning_I.pdf` (`ccbc78ec…bdea8`) | `../workshop-01-cub200-multimodal-informe.pdf` | Recompuesto con Quarto (fuente en `../report-source/`). La Figura 2 (fotografías) se sustituye por una tabla de los mismos cinco casos |

Hashes completos:

```
9d6f352513b3ce343c5d0f17c2dcc575024c02934496d459d992f12afed08711  notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb
ccbc78ec1e29c4fab818b926db3769d12b0ce256ada654356a68c8ef322bdea8  docs/Informe_Tecnico_CUB200_Deep_Learning_I.pdf
339ddaae23a9377a076a412ecf858ab5ae167cc92bef34a7433cba2ab0716129  ENTREGA_CUB200_TAREA01.zip
```

## Licencia

Esta carpeta no tiene todavía un archivo de licencia propio. El código se publica para consulta académica.
