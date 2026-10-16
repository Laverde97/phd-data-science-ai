# CUB-200-2011 — Pipeline multimodal reproducible
**Deep Learning I · Tarea 01 · PyTorch y TensorFlow**

> **Estado al 16/10/2026:** pipeline construido y validado con datos originales de CUB-200-2011 y captions asociados; seis flujos de datos comprobados (train/val/test por framework), pruebas automatizadas y comparación exhaustiva de los campos deterministas de val/test. **No se entrenó ningún modelo.** El ZIP de entrega excluye `data/` y los entornos virtuales.

## 1. Objetivo y salidas

Combinar 11.788 fotografías de 200 especies, 10 captions por fotografía y un vector de 318 atributos (312 binarios + seis geométricos), manteniendo la partición oficial de prueba. Los artefactos aprendidos se ajustan **exclusivamente con train**.

Cada muestra/lote contiene `image`, `input_ids`, `lengths`, `tabular`, `label` e `image_id` (trazabilidad).

| Campo | PyTorch | TensorFlow |
|---|---|---|
| `image` | `(B, 3, 224, 224)` float32 | `(B, 224, 224, 3)` float32 |
| `input_ids` | `(B, 25)` entero | `(B, 25)` entero |
| `lengths` | `(B,)` entero | `(B,)` entero |
| `tabular` | `(B, 318)` float32 | `(B, 318)` float32 |
| `label` | `(B,)` entero | `(B,)` entero |
| `image_id` | `(B,)` entero | `(B,)` entero |

## 2. Estructura y notebook que se debe evaluar

```text
CUB200_pipeline_profesional/
├── README.md
├── requirements.txt
├── data/                     # no incluida en el ZIP; fuentes originales
│   ├── CUB_200_2011/
│   └── text_c10/
├── artifacts/                # metadatos, arrays, scaler y firmas val/test
├── src/cub200/               # common, prepare, quality, pytorch_pipeline y tensorflow_pipeline
├── scripts/                  # preflight, prepare, validate, export y compare
├── tests/                    # pruebas unitarias y smoke tests
├── notebooks/
│   ├── 02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb    # PRINCIPAL
│   └── ...                    # variantes históricas / auxiliares
├── docs/                     # informe PDF/Word, metodología y evidencias
├── logs/                     # registros de ejecuciones realizadas
└── preparar_entrega_CUB200.py
```

**Notebook canónico para el docente:** `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb`, guardado con las 11 celdas de código ejecutadas y sin errores. Los demás notebooks quedan como antecedentes y no sustituyen al principal.

## 3. Fuentes de datos y alcance de distribución

- **CUB-200-2011 (imágenes, clases, anotaciones):** https://data.caltech.edu/records/20098 . El árbol extraído debe localizarse en `data/CUB_200_2011/`.
- **Captions Reed et al. (2016):** https://github.com/reedscot/cvpr2016 ; se usó la distribución `birds`/AttnGAN https://github.com/taoxugit/AttnGAN . Se extrajeron 11.788 `.txt` en `data/text_c10/`, cada uno con diez captions no vacías, alineadas con los JPG.
- Antes de redistribuir fotografías o captions originales deben revisarse las licencias y condiciones de las respectivas fuentes. **El paquete académico ligero no redistribuye esos datos.**

Ejemplo de correspondencia de archivos:

```text
data/CUB_200_2011/images/001.Black_footed_Albatross/Black_Footed_Albatross_0001_796111.jpg
data/text_c10/001.Black_footed_Albatross/Black_Footed_Albatross_0001_796111.txt
```

**Nota:** el ZIP sí incluye `artifacts/` ya procesados y firmas numéricas. Para volver a **leer imágenes o reconstruir artefactos** desde cero se requieren JPG, anotaciones y captions originales.

## 4. Entorno usado y cómo ejecutar en WSL

La ejecución documentada utilizó **Python 3.12.14**, PyTorch **2.11.0+cu128** con torchvision **0.26.0+cu128** y TensorFlow **2.21.0**, en dos entornos independientes: `.venv` y `.venv-tf`. Ambos detectaron GPU en la máquina original. **No son entornos portables a Windows**, por lo que no deben copiarse como instaladores.

Los listados de paquetes efectivos están en:

```text
artifacts/reports/environment/pytorch_packages.txt
artifacts/reports/environment/tensorflow_packages.txt
```

`requirements.txt` enumera dependencias compartidas y no fija una instalación universal de GPU. Reconstruir entornos en otra máquina exige elegir versiones CUDA/CPU compatibles con esa plataforma según documentación oficial. La reproducción desde cero fuera del WSL original **no fue ensayada**.

Desde la raíz del proyecto ya preparado en WSL:

```bash
source .venv/bin/activate
python -m pytest -q -rs
./.venv-tf/bin/python -m pytest -q -rs

python scripts/preflight.py --data-dir data
# prepare.py solo si se necesitan volver a generar los artefactos:
python scripts/prepare.py --data-dir data --artifacts-dir artifacts

python scripts/validate.py --data-dir data --artifacts-dir artifacts --framework torch --batch-size 16
./.venv-tf/bin/python scripts/validate.py --data-dir data --artifacts-dir artifacts --framework tf --batch-size 16
```

**Comparación completa de val/test** (las exportaciones pueden tardar):

```bash
python scripts/export_eval_signatures.py --framework torch --max-batches 0
./.venv-tf/bin/python scripts/export_eval_signatures.py --framework tf --max-batches 0
python scripts/compare_eval_signatures.py
```

No utilizar `--framework both` desde un solo intérprete en esta configuración de dos entornos. Para inspeccionar resultados, abrir en VS Code el notebook canónico con el kernel `.venv/bin/python`, ejecutar **Restart Kernel and Run All** y guardar.

## 5. Preprocesamiento implementado

- **Particiones:** test oficial de 5.794; train oficial 5.994, subdividido estratificadamente en train 5.394 / val 600, semilla 42.
- **Imagen:** recorte en torno a bounding box (+10 % de margen y clipping si sale del lienzo), resize 256×256, crop final de 224×224, normalización ImageNet; aumentaciones (crop aleatorio, flip, brillo y contraste) exclusivamente en train. Se auditaron **30 bounding boxes** con intersección correctiva.
- **Texto:** limpieza a minúsculas y letras inglesas, `<pad>=0`, `<unk>=1`; vocabulario de **2.079 tokens** con frecuencia mínima 2 y longitud máxima **25** basada en el P95 de train. Caption aleatoria entre diez para train; primera caption para val/test.
- **Tabular:** 312 atributos binarios sin escalado y seis características geométricas con `StandardScaler` aprendido solo de train.
- **Implementaciones:** PyTorch usa `Dataset` y `DataLoader`; TensorFlow usa un flujo nativo `tf.data` con `tf.io`, `tf.image`, batching y prefetch.

## 6. Evidencias obtenidas y límites de las afirmaciones

| Evidencia | Resultado documentado |
|---|---|
| Identificadores | 11.788 distintos; 200 especies |
| Splits | train 5.394, val 600, test 5.794 |
| Arrays persistidos | tabular `(11788,318)`; texto `(11788,10,25)` |
| Validación por framework | train/val/test superaron contrato de lote |
| Pruebas unitarias | 8 passed, 1 skipped **en cada entorno** (ver logs y `pytest -rs` para motivo de omisión) |
| Firmas deterministas val/test | 600 + 5.794 registros; igualdad exacta en `image_id`, `label`, `input_ids`, `lengths`; `tabular` equivalente con `atol=1e-6`, `rtol=0` |
| Notebook principal | 11/11 celdas de código ejecutadas y 0 errores guardados |

**Límites:** las firmas no comparan píxeles de imagen entre frameworks ni prueban igualdad de aumentaciones aleatorias en train. La validación rápida (`scripts/validate.py`) inspecciona un lote de cada split, no todas las imágenes. No hubo entrenamiento, accuracy ni F1; tampoco benchmarking de rendimiento. Las bounding boxes y atributos proceden de anotaciones y no están garantizados para fotografías futuras. Reproducir en otro equipo requiere las fuentes originales y reconstruir dependencias.

## 7. Entrega y documentación

- **Notebook oficial:** `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb`.
- **Informe académico:** `docs/Informe_Tecnico_CUB200_Deep_Learning_I.pdf` (Word editable disponible).
- **Guía de cierre:** `docs/CIERRE_TAREA01.md`.
- **Pruebas y salidas:** `logs/`, `artifacts/reports/signatures/`, `docs/VALIDACION_REALIZADA.md`.
- **Criterios y limitaciones:** `docs/DECISIONES_METODOLOGICAS.md` y `docs/CHECKLIST_ENTREGA.md`.

Regenerar el paquete ligero desde la raíz:

```bash
python preparar_entrega_CUB200.py
```

El ZIP generado tiene un manifiesto SHA-256 e incluye los artefactos existentes pero **no `data/` ni los entornos virtuales**. La verificación del ZIP acredita integridad de los archivos incluidos, **no** reproducción de extremo a extremo en otra máquina.

## Referencias principales

- Wah et al. (2011), *The Caltech-UCSD Birds-200-2011 Dataset*: https://data.caltech.edu/records/20098
- Reed et al. (2016), *Learning Deep Representations of Fine-Grained Visual Descriptions*: https://arxiv.org/abs/1605.05395
- PyTorch, Dataset/DataLoader: https://pytorch.org/docs/stable/data.html
- TensorFlow, tf.data: https://www.tensorflow.org/guide/data
