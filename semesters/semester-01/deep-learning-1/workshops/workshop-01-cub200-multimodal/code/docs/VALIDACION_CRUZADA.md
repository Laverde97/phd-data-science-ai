# Validación cruzada PyTorch / TensorFlow

Complemento al proyecto CUB-200-2011. No sobrescribe scripts existentes.

## Instalar el complemento

Extraer este ZIP en la **raíz** de `CUB200_pipeline_profesional/`.

## Exportar una prueba de dos lotes por split

```bash
set -o pipefail
python scripts/export_eval_signatures.py --framework torch --max-batches 2 2>&1 | tee logs/06_export_torch.log
./.venv-tf/bin/python scripts/export_eval_signatures.py --framework tf --max-batches 2 2>&1 | tee logs/07_export_tf.log
python scripts/compare_eval_signatures.py 2>&1 | tee logs/08_compare.log
```

## Auditoría de anotaciones

```bash
python scripts/visualize_bbox_audit.py
```

Abre `artifacts/reports/bbox_top5.png` y verifica que el área visible del ave sigue siendo razonable.

## Comparación exhaustiva para evidencia final

Para comprobar **todas** las observaciones de validación y prueba, sobrescribir las firmas con:

```bash
python scripts/export_eval_signatures.py --framework torch --max-batches 0 2>&1 | tee logs/09_export_torch_full.log
./.venv-tf/bin/python scripts/export_eval_signatures.py --framework tf --max-batches 0 2>&1 | tee logs/10_export_tf_full.log
python scripts/compare_eval_signatures.py 2>&1 | tee logs/11_compare_full.log
```

Los archivos `.npz` se generan dentro de `artifacts/`. No se exportan imágenes crudas.
La comparación verifica `image_id`, `label`, `input_ids`, `lengths` y `tabular`. No exige igualdad exacta de imágenes, ya que los algoritmos de decodificación e interpolación pueden diferir; verifica que cada imagen es finita y cumple las dimensiones requeridas.

**Limitación:** el script `scripts/validate.py` comprueba un solo batch por split; no equivale a una inspección completa de las 11.788 imágenes. La comparación exhaustiva aquí recorre val y test, no train debido a sus aumentaciones aleatorias.
