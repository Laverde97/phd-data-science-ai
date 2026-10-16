# Corrección de bounding boxes fuera de los límites de imagen

## Problema observado
La anotación `(2,69,457,311)` sobre una imagen `(500,375)` presenta 5 píxeles de exceso vertical. El código anterior abortaba al exigir un máximo de 2 píxeles fuera del lienzo. Se mantiene la anotación cruda como dato original.

## Política documentada
Las seis variables geométricas se calculan sobre la **intersección visible** entre la anotación y el lienzo. Si la caja no intersecta la imagen, si posee tamaños no positivos o coordenadas no finitas, se interrumpe la preparación con una excepción. El margen del 10% para recortar imágenes se sigue aplicando en los pipelines, y sus resultados se limitan al lienzo.

## Trazabilidad
- `manifest.csv` conserva `x,y,w,h` originales.
- `bbox_clipping_audit.csv` contiene `image_id`, dimensiones originales y bbox recortada para todos los casos detectados (puede estar vacío).
- `metadata.json` registra `bbox_clipping_count` y la política utilizada.
- No se modifica ningún archivo de `data/`.

## Criterio de calidad
Revisar cuántas anotaciones requieren clipping y revisar manualmente una muestra, especialmente excesos grandes. Esta política no legitima anotaciones arbitrarias; simplemente evita que un pequeño exceso de anotación impida generar características físicamente interpretables.
