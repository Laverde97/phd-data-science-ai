# Cierre de la Tarea 01 — CUB-200-2011

## Estado respaldado por resultados reales compartidos

- PyTorch `2.11.0+cu128`: GPU NVIDIA RTX 4060 detectada, producto de matrices validado.
- TensorFlow `2.21.0`: GPU detectada, producto de matrices validado. Corregida búsqueda de `libcusolver.so.11` mediante enlace simbólico dentro de `.venv-tf`.
- Imágenes: 11.788, archivo original con MD5 verificado.
- Captions: 11.788 archivos válidos, con diez líneas no vacías por archivo.
- Anotaciones: 11.788 etiquetas y bounding boxes; 3.677.856 registros originales de atributos.
- Particiones: train 5.394, val 600, test 5.794.
- Vocabulario: 2.079 tokens; `max_len=25`; tabular 318 variables.
- Bounding boxes: 30 recortadas a la imagen; 5 casos extremos inspeccionados visualmente. Máxima área anotada perdida: 7,98 %.
- Validación: los seis pipelines superaron su contrato básico; `pytest` reportó 8 passed / 1 skipped en cada entorno.
- Comparación completa: 600 val y 5.794 test, coincidencia en IDs, labels, texto y equivalencia numérica tabular a `atol=1e-6`.

**Estos resultados no significan** que se haya entrenado un modelo ni que las imágenes sean idénticas píxel a píxel. Tampoco sustituyen pruebas adicionales de aumentación y rendimiento de train.

## Notebook oficial y uso en WSL

La versión vigente de evaluación se encuentra **dentro del proyecto**:

```text
notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb
```

Para abrirla desde la raíz del proyecto:

```bash
source .venv/bin/activate
code notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb
```

Seleccionar el kernel `.venv/bin/python`, ejecutar **Restart Kernel and Run All** y guardar. El notebook utiliza `ROOT` calculado dinámicamente a partir del directorio del proyecto. La validación de TensorFlow se lanza en `.venv-tf` mediante un proceso separado con `MPLBACKEND=Agg`, evitando incompatibilidades con el backend inline de Jupyter. Los artefactos preparados se consumen desde `artifacts/`; no hace falta repetir `prepare.py` si ya existen los datos procesados.

**Versiones anteriores del notebook son históricas** y no forman parte de la evaluación principal. Los documentos e informes se conservan en `docs/`.

## Verificaciones necesarias antes de entregar

1. [Verificado] Notebook final ejecutado: 11 celdas de código con salidas guardadas y sin errores.
2. Compruebe que `artifacts/reports/signatures/{torch,tf}_{val,test}.npz` sean las firmas **completas** (600 y 5.794 observaciones). No sustituir por resultados de 32 casos.
3. Revise si `logs/` y `artifacts/reports/` están ignorados por `.gitignore`. Decida qué resúmenes y figuras pequeñas sí conviene publicar; evite subir artefactos pesados o innecesarios.
4. [Actualizado] `README.md` y `docs/VALIDACION_REALIZADA.md` describen los datos originales y las verificaciones realmente ejecutadas.
5. Documente el clipping (30 casos), la fuente de captions (AttnGAN/Reed), la diferencia entre DataLoaders y la selección aleatoria de caption en train.
6. Explique en el informe que las pruebas unitarias saltadas corresponden al otro framework no instalado en el respectivo entorno, y conserve ambas ejecuciones.
7. No subir `.venv`, `.venv-tf`, el dataset completo ni los archivos `.tgz`/`.zip` de datos a un repositorio público. Mantenga referencias a las fuentes y licencias.
8. Realice commit del código, notebook ejecutado y la documentación (no de los datos originales). **No hacer push/merge sin revisar antes el diff.**

## Lista de entrega propuesta

- Código modular en `src/cub200/` y `scripts/`.
- **Notebook canónico ejecutado** `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb`.
- Documentación técnica y metodología, con fuentes, supuestos y limitaciones.
- Evidencia resumida de tests, validaciones y auditoría gráfica (no necesariamente todos los artefactos `.npz`).

## Observaciones metodológicas importantes

- Estar en condiciones de leer todo val/test no implica validar imagen vs. imagen a igualdad exacta: los sistemas tienen reglas e interpoladores distintos.
- El test oficial de CUB se conserva, y val surge de train oficial mediante split estratificado.
- El uso de anotaciones tabulares manuales limita las aplicaciones a datos donde estos atributos sean observables o puedan inferirse.
- Se requiere al menos una comprobación controlada de la lógica aleatoria de train si se desea afirmar reproducibilidad completa bajo múltiples workers.
