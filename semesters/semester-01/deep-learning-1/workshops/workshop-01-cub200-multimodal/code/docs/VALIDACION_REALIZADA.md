# Validación realizada — ejecución con datos originales

**Estado verificado al 16/10/2026.** Este documento sustituye el estado inicial de prototipo y simulación sintética. La simulación fue un paso preliminar y **no representa la ejecución final**.

## 1. Fuentes e integridad

- Imágenes CUB-200-2011: **11.788 JPG**; verificación MD5 del archivo original documentada durante adquisición.
- Captions reales: **11.788 TXT**, cada uno con **diez líneas no vacías** y correspondencia por ruta; total **117.880 captions**.
- Anotaciones: 11.788 etiquetas, 11.788 cajas delimitadoras y 3.677.856 registros de atributos originales.
- Auditoría inicial: `logs/01_preflight.log`. Preparación real: `logs/03_prepare.log`.

## 2. Artefactos preparados

- `manifest.csv`: **11.788 IDs únicos**, todas las 200 clases; train **5.394**, val **600**, test oficial **5.794**.
- `tabular.npy`: `(11788, 318)`, primeras 312 binarias y últimas seis geometrías estandarizadas con train.
- `text_ids.npy`: `(11788, 10, 25)`; `text_lengths.npy`: `(11788, 10)`.
- `vocab.json`: **2.079 tokens**; `<pad>=0`, `<unk>=1`; máximo de secuencia 25.
- `bbox_clipping_audit.csv`: **30 casos** ajustados al tamaño de la imagen, manteniendo bbox original para trazabilidad. Figura en `artifacts/reports/bbox_top5.png`.

## 3. Frameworks y pruebas reales

Las validaciones se ejecutaron con Python 3.12.14 en **dos entornos independientes**. La validación rápida verificó un batch real por split para PyTorch y TensorFlow; seis flujos en total:

```bash
python scripts/validate.py --data-dir data --artifacts-dir artifacts --framework torch --batch-size 16
./.venv-tf/bin/python scripts/validate.py --data-dir data --artifacts-dir artifacts --framework tf --batch-size 16
```

Ambos informaron `Contrato multimodal: OK` en train, val y test. Evidencias: `logs/04_validate_pytorch.log` y `logs/05_validate_tensorflow.log`.

Pruebas unitarias: **8 passed y 1 skipped** por entorno, según las ejecuciones del usuario y `logs/02_pytest_torch.log`, `logs/13_pytest_tensorflow.log`. Para documentar con precisión el motivo del skip, ejecutar `python -m pytest -q -rs` y `./.venv-tf/bin/python -m pytest -q -rs`.

## 4. Comparación exhaustiva de los campos deterministas

Se exportaron **todas** las observaciones de val (**600**) y test (**5.794**) en cada framework. Los campos `image_id`, `label`, `input_ids` y `lengths` coinciden exactamente; las **318** columnas tabulares coinciden a tolerancia `atol=1e-6`, `rtol=0`.

Evidencias: `logs/09_export_torch_full.log`, `logs/10_export_tf_full.log`, `logs/11_compare_full.log`, y firmas en `artifacts/reports/signatures/`.

**Limitación explícita:** las imágenes se validaron por contrato, pero **no** se compararon píxel a píxel entre frameworks; tampoco se compararon aumentaciones aleatorias de train. Este resultado no es un ensayo independiente de ejecución en otra máquina.

## 5. Notebook y alcance académico

El notebook principal es `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb`: **11 celdas de código ejecutadas, sin errores guardados**. Muestra evidencia, metodología y validación separada por intérprete. El proyecto prepara datos; **no entrena modelos** ni informa exactitud predictiva.

Consultar también `docs/CIERRE_TAREA01.md`, `docs/DECISIONES_METODOLOGICAS.md` y `docs/Informe_Tecnico_CUB200_Deep_Learning_I.pdf`.
