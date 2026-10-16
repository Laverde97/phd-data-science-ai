# Decisiones metodológicas, limitaciones y auditoría

## 1. Requerimientos originados en el documento docente
- 11.788 imágenes, 200 clases, 10 captions por imagen, 312 atributos, bounding boxes.
- Entrenamiento 5.394, validación 600, test 5.794; el split oficial del test se conserva.
- Imagen bbox+10%; 256x256 -> 224x224, aumentación exclusivamente en train y normalización ImageNet.
- Texto `[a-z]+` en minúsculas; vocabulario con frecuencia >=2 y P95 de longitud calculados solo sobre train; tokens PAD=0, UNK=1.
- Una caption aleatoria por lectura de train; primera en val/test.
- 312 binarios intactos; 6 geometrías con scaler ajustado solo en train.

## 2. Supuesto necesario (no especificado numéricamente)
El docente solicita seis variables geométricas (posición, tamaño, aspecto y área), **sin dar fórmulas explícitas**. Se propone:

1. `cx_over_W = (x + w/2) / W`
2. `cy_over_H = (y + h/2) / H`
3. `w_over_W = w / W`
4. `h_over_H = h / H`
5. `w_over_h = w / h`
6. `area_over_WH = w*h / (W*H)`

Son características normalizadas por dimensiones originales, excepto relación de aspecto. `StandardScaler` se ajusta al subconjunto train y se serializa. Cualquier definición distinta acordada con el docente debe cambiarse y documentarse antes de congelar los artefactos.

## 3. Riesgo de fuga de datos
- Nunca calcular vocabulario, percentil de longitud ni parámetros del scaler usando val/test.
- No usar rasgos anotados por clase como sustitutos de observaciones por imagen; podrían filtrar la etiqueta.
- El test oficial debe permanecer fuera de cualquier ajuste, y no se debe seleccionar hiperparámetros en función de test.

## 4. Importancia para la vida real
CUB es un benchmark de investigación, **no** un entorno de inferencia listo para aplicación.
- Los 312 atributos y los bounding boxes proceden de anotaciones humanas. En imágenes reales nuevas, hay que diseñar cómo obtenerlas; sin ello, el sistema no es directamente desplegable.
- Las captions pueden no existir en la entrada de una aplicación real; habrá que definir cómo las proporciona el usuario o un componente separado.
- Un `tf.data` y un `DataLoader` comparten estructura y datos, pero no se promete equivalencia numérica exacta en transformaciones estocásticas.
- Los datos tienen limitaciones de cobertura (especies presentes, contextos, variaciones); no se deben generalizar resultados a especies fuera del benchmark.
- Verificar términos de uso/redistribución de los datasets originales por separado del código.

## 5. Reproducibilidad y trazabilidad
`manifest.csv` contiene `image_id`, split, etiqueta y bbox; `metadata.json` registra longitudes, semilla y definiciones; vocabulario y scaler se serializan. Las imágenes y captions no se redistribuyen con el código. Se retiene `image_id` en cada batch para poder auditar errores.

## 6. Prueba de aceptación
Se aprueba técnicamente al ejecutar con datos originales **seis pipelines** (train/val/test en PyTorch y TensorFlow), pasar contrato de lotes y auditoría de consistencia. Pruebas sintéticas son útiles pero no sustituyen esta verificación.
