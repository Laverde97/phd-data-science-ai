# Checklist de entrega — estado comprobado al 16/10/2026

Marcar solamente lo comprobado con el notebook, logs, código y artefactos disponibles.

## Datos e integridad
- [x] CUB original descargado, MD5 revisado y extraído.
- [x] 11.788 captions TXT emparejadas con JPG, 10 captions no vacías por archivo.
- [x] `manifest.csv`: 11.788 IDs únicos y 200 etiquetas 0..199.
- [x] Particiones: train 5.394, val 600, test oficial 5.794, sin solapamientos.
- [x] Correspondencia de rutas de JPG, captions y anotaciones auditada.

## Preprocesamiento
- [x] Bbox y margen 10 %, resize, crops, aumentación solo en train y normalización implementados y revisados; corrección de 30 bbox documentada.
- [x] Texto: normalización, vocabulario train-only, PAD/UNK, P95, padding y longitudes.
- [x] Tabular: 312 binarios + seis geometrías; scaler ajustado solo con train.
- [x] Captions: aleatoria en train y primera en val/test.

## Frameworks y evidencias
- [x] PyTorch: lote correcto en train/val/test.
- [x] TensorFlow: lote correcto en train/val/test.
- [x] Firmas completas de val y test por `image_id`, etiqueta, tokens, longitudes y tabular comparadas.
- [x] Tests: 8 aprobados y 1 omitido por entorno (consultar logs).
- [x] Integridad de dimensiones, clases, valores finitos y atributos binarios comprobada.
- [x] Notebook principal: 11 celdas de código ejecutadas, ninguna con error guardado.

## Presentación y límites
- [x] README actualizado con rutas y comandos por entorno, notebook canónico y limitaciones.
- [x] Informe técnico PDF/Word y descripción del contrato multimodal.
- [x] Decisiones geométricas, fuentes, metodología, discusión y bibliografía documentadas.
- [x] El ZIP ligero excluye `data/` y entornos virtuales; no se adjuntan imágenes originales de terceros.
- [ ] Prueba integral de instalación y reproducción desde cero en otro ordenador: **no realizada**.
- [ ] Revisión jurídica independiente de las licencias y permisos de redistribución: **no realizada**.
- [ ] Igualdad visual píxel a píxel de imágenes entre PyTorch y TensorFlow: **no realizada; no es requisito del contrato comparado**.

**Notebook para evaluar:** `notebooks/02_informe_ejecutable_CUB200_FINAL_PORTABLE.ipynb`.
