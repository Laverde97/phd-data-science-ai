# Guía operativa paso a paso — Tarea multimodal CUB-200-2011

## Antes de empezar: criterio de éxito
**Obligatorio (profesor):** dos frameworks, tres splits, cuatro tipos de salida (imagen, texto con longitud, tabular, etiqueta), preprocesamientos fijados por consigna, sin entrenamiento. **Valor adicional de ingeniería:** tests, fuentes verificables, control de leakage, artefactos persistidos, separación de responsabilidades, documentación y trazabilidad.

## Etapa 0. Preparar entorno (día 1)
1. Usar **Colab** para la primera corrida, o **VS Code** si hay disco/RAM suficientes.
2. Descomprimir el ZIP del proyecto. Abrir la carpeta raíz, no mover scripts sueltos.
3. Verificar Python, PyTorch y TensorFlow. Instalar dependencias según README. Ejecutar tests rápidos.
4. No guardar credenciales en notebooks ni subir archivos originales al repositorio Git.
**Evidencia:** captura/log de versiones y `pytest -q`.

## Etapa 1. Adquirir y catalogar fuentes (días 1–2)
1. Descargar archivo `CUB_200_2011.tgz` desde registro Caltech.
2. Descargar el paquete `birds` del repositorio Reed (enlace original), o alternativa contrastada.
3. Crear `data/CUB_200_2011` y `data/text_c10` como describe README.
4. Comprobar `images.txt`, `image_class_labels.txt`, `train_test_split.txt`, `bounding_boxes.txt` y `attributes/image_attribute_labels.txt`.
5. Inspeccionar `.txt`: se requieren 10 líneas útiles por cada JPG. Si el proveedor entrega otra estructura, primero reorganizar **sin inventar captions ni renombrar arbitrariamente**.
6. Registrar enlaces consultados, fechas de descarga y licencia/condiciones de uso cuando se disponga de ellas.
**Evidencia:** estructura de directorios y un par JPG/TXT emparejado.

## Etapa 2. Auditoría y tabla maestra (días 3–4)
1. Ejecutar `python scripts/prepare.py --data-dir data --artifacts-dir artifacts`.
2. Validar que hay 11.788 IDs únicos, 200 clases, 5.994/5.794 train/test oficiales.
3. Verificar que cada imagen tiene clase, bbox, 312 atributos, archivo físico y captions.
4. El script creará `manifest.csv`: `image_id`, ruta relativa, etiqueta 0..199, split y bbox.
**Evidencia:** conteos y primeras filas de manifest.

## Etapa 3. Particiones y anti-leakage (día 5)
1. Respetar test original; no usar `train_test_split` sobre las 11.788 observaciones.
2. Reservar 600 de train oficial como validación, **estratificando por especie** con `seed=42`.
3. Comprobar train=5394, val=600, test=5794 y que los IDs no se cruzan.
4. Conservar las particiones como columnas del manifest para reutilizarlas en ambos frameworks.
**Evidencia:** tabla de conteos por clase y por split.

## Etapa 4. Procesamiento de las tres modalidades (días 6–8)
**Imagen**
- `bbox` + 10% de margen, recorte dentro del tamaño de la imagen.
- Resize 256x256; train crop aleatorio 224x224 y aumento; evaluación crop central 224x224.
- Escalado a [0,1] y normalización ImageNet. Los aumentos solo ocurren en train.

**Texto**
- Convertir a minúsculas; letras a-z; suprimir puntuación y números.
- Construir vocabulario con **todas las captions de las imágenes de train**, mínimo dos ocurrencias.
- `<pad>=0`, `<unk>=1`, `max_len=ceil(percentil95)` calculado solo en train.
- Vectorizar y guardar `text_ids.npy` (N,10,L) y `text_lengths.npy` (N,10).

**Tabular**
- Conservar los 312 binarios originales intactos.
- Definir seis variables geométricas sobre bbox/dimensiones originales, explícitas en el informe.
- Ajustar `StandardScaler` solo con train, aplicar con `transform` a val/test.
- Guardar `tabular.npy` (N,318) y `geometry_scaler.joblib`.

**Evidencia:** tamaños, min/max, valores NaN/Inf y comparación de 3 ejemplos.

## Etapa 5. Implementar PyTorch (días 9–10)
1. Abrir `src/cub200/pytorch_pipeline.py` y estudiar `CUBMultimodalTorch(Dataset)`.
2. Revisar `__len__`, `__getitem__`, lectura bajo demanda y transformación de imagen.
3. Crear `train_loader`, `val_loader`, `test_loader` con `make_torch_loaders`.
4. Verificar shapes y dtypes de una muestra y un batch por partición.
5. Inspeccionar que train se baraja y val/test conservan la primera caption.
**Evidencia:** stdout de `validate.py --framework torch`.

## Etapa 6. Implementar TensorFlow (días 11–12)
1. Abrir `src/cub200/tensorflow_pipeline.py`, usando `from_tensor_slices`, `map`, `batch`, `prefetch`.
2. Confirmar que las imágenes se cargan mediante `tf.io` y aumentan con `tf.image`.
3. Crear `train_ds`, `val_ds`, `test_ds` con `make_tf_datasets`.
4. Comprobar que las estructuras son compatibles con PyTorch aunque orden de ejes difiera.
5. Controlar cardinalidad y tipos de cada dataset.
**Evidencia:** stdout de `validate.py --framework tf`.

## Etapa 7. Pruebas y comparación (días 13–14)
1. Ejecutar `python -m pytest -q -rs` en PyTorch, `./.venv-tf/bin/python -m pytest -q -rs` en TensorFlow y `scripts/validate.py` por separado en cada entorno.
2. Verificar 200 clases en cada partición, sin solapamientos ni fuga de información.
3. Comparar por `image_id`: `label`, `tabular`, tokens y lengths de val/test deben coincidir entre frameworks.
4. Para val/test, comprobar estabilidad al repetir la carga; **no exigir igualdad exacta pixel a pixel entre librerías**.
5. Mostrar imágenes antes/después, una caption real, un vector parcial de atributos y su especie.
6. Documentar errores y correcciones realizadas, RAM, tiempo de preparación y ambiente.
**Evidencia:** notebook ejecutado + registro de comandos.

## Etapa 8. Presentación y entrega (día 15)
1. Introducción al problema; descripción de dataset y distribución.
2. Diseño de pipeline, decisiones de preprocesamiento, reproducibilidad.
3. Comparación de PyTorch/TensorFlow, tabla de shapes y ejemplos gráficos.
4. Limitaciones: anotaciones disponibles solo como ground truth, links antiguos y ausencia de modelo entrenado.
5. Bibliografía Wah et al. (2011), Reed et al. (2016), documentación oficial de frameworks.
6. Entregar notebook ejecutado, código fuente, README, evidencia de pruebas y **sin adjuntar dataset gigante salvo solicitud**.

## Comandos base (entornos separados, ejecución comprobada en WSL)
```bash
python -m pytest -q
python scripts/preflight.py --data-dir data
python scripts/prepare.py --data-dir data --artifacts-dir artifacts
python scripts/validate.py --data-dir data --artifacts-dir artifacts --framework torch --batch-size 16
./.venv-tf/bin/python scripts/validate.py --data-dir data --artifacts-dir artifacts --framework tf --batch-size 16
python scripts/export_eval_signatures.py --framework torch --max-batches 0
./.venv-tf/bin/python scripts/export_eval_signatures.py --framework tf --max-batches 0
python scripts/compare_eval_signatures.py
```

## Problemas frecuentes
- **Faltan captions:** probablemente el archivo descargado no es el paquete de texto correcto o está en carpeta anidada.
- **Falla el split:** verificar IDs/clases oficiales, no crear splits aleatorios globales.
- **Demora en Colab:** copiar y extraer en `/content`; usar Drive principalmente para respaldos.
- **TensorFlow no importa:** verificar versión Python/Colab e instalación compatible; no cambiar la implementación a PyTorch para sustituirlo.
- **Out of memory:** `batch_size=8`, menos paralelismo y no cargar todas las imágenes en un arreglo.
- **Diferencia entre imágenes TF/Torch:** redimensionamiento/interpolación y aleatoriedad pueden diferir, pero el contrato debe respetarse.

> **Estado final:** las fuentes originales y los pipelines ya se procesaron y verificaron en la máquina de desarrollo. El notebook principal ejecutado es `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb`. Una validación rápida por split no equivale a examinar todos los píxeles. No se ejecutó una instalación desde cero en otra máquina.
