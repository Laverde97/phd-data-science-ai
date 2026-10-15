# Recursos — Semana 02 · Clase 02

Recursos y artefactos que usan o producen los notebooks de la clase. No se copiaron al repositorio:

- `clase2/resultados_regresion/` del repositorio del docente: `mejor_modelo.keras` y 12 registros
  de TensorBoard (6 `train` + 6 `validation`) generados por `01_Regresion.ipynb`. Se guardan como
  artefactos en almacenamiento privado:
  https://github.com/MAESTRiA-ESTADiS-CIENCIA-DATOS-Bosque/Deep_Learning_I_Fundamentos/tree/main/clase2/resultados_regresion
- `tensorflow_datasets`: `mnist`, que se descarga al ejecutar `Pipeline_TensorFlow.ipynb`.

## Material complementario propio

| Archivo | Descripción | SHA-256 |
|---------|-------------|---------|
| `Guia_Profesional_Redes_Neuronales.pdf` | Guía teórica y matemática de redes neuronales artificiales (33 páginas, español). Copia byte a byte del original. | `432289adde6984d1f4af4d1ad34192cd4f3ff57f17cee7bd853e7ca9ca639784` |

Elaborada por Juan Sebastián Laverde Chunza con apoyo de herramientas de inteligencia artificial
generativa (el PDF incluye metadatos de procedencia C2PA), tomando como referencia la presentación
*Artificial Neural Networks* del profesor Héctor Javier Hortúa, PhD. Sus diagramas están redibujados
y no reproduce las diapositivas. No es material oficial del docente ni de la Universidad El Bosque.

La presentación del docente, recopilada en Word (`Redes Neuronales.docx`), sigue en almacenamiento
privado y no se publica.

## Guías académicas de los notebooks (`guides/`)

Hay una guía por cada notebook de la clase, enlazada desde la columna «PDF» de la tabla de
notebooks en `../index.qmd`.

| Archivo | Notebook de referencia | Descripción | Páginas | SHA-256 |
|---------|------------------------|-------------|--------:|---------|
| `guides/01_Guia_Academica_Regresion_TensorFlow.pdf` | `01_Regresion.ipynb` | Regresión en TensorFlow: `GradientTape`, `tf.keras`, *callbacks*, guardado, regularización y normalización | 24 | `5dd7c95f3c6f7301517af0867b7575632f041a98e02318d3b54f483f4245d13f` |
| `guides/02_Guia_Academica_Clasificacion_PyTorch.pdf` | `02_Clasificacion.ipynb` | Clasificación binaria en PyTorch: BCE, *autograd*, `nn.Module`, bucle propio, Lightning y Keras sobre PyTorch | 22 | `aa50014b0df21f023c86b19fa9d1a4e6c40b0c57023fdf7cc6c0b2af988c48f2` |
| `guides/03_Guia_Academica_Pipeline_MNIST_TensorFlow.pdf` | `Pipeline_TensorFlow.ipynb` | *Pipeline* MNIST: TFDS, `tf.data`, pesos de clase, *callbacks*, matriz de confusión y F1 macro | 18 | `df75bc61aaf1dc3f70dc30b6d8be0f601dd6fd646ef9c4348ce568b49d1108ac` |
| `guides/04_Guia_Academica_Series_Temporales_Lightning_Keras_JAX.pdf` | `Pipeline__PyTorchL_KerasJAX.ipynb` | Series temporales: ventanas, división temporal, líneas base, Lightning y Keras 3 sobre JAX | 19 | `a7fc22d19bc61a4d346973588e9ea9da404cdf34ebb64845e3ee47ce524dea4c` |

**Procedencia y atribución.**

- Las guías las elaboró Juan Sebastián Laverde Chunza con apoyo de herramientas de inteligencia
  artificial generativa. La referencia conceptual son los notebooks de la Clase 02 del profesor
  Héctor Javier Hortúa, PhD, enlazados a su repositorio en GitHub y en Colab.
- Son **ediciones públicas**. Su código, sus datos (sintéticos, o MNIST, que es público) y sus
  explicaciones son propios. Una comparación automática contra los notebooks del docente (commit
  `c9cfeb5`) no encontró texto reproducido. Las únicas líneas de código coincidentes son firmas
  exigidas por las librerías, como `def training_step(self, batch, batch_idx):`.
- Todo el código de las guías se ejecutó al generarlas, así que las cifras y figuras que contienen
  son salidas reales.
- No son material oficial del docente ni de la Universidad El Bosque. Citar los notebooks como
  referencia no equivale a una licencia ni a una autorización sobre el material original.
- Las versiones anteriores de estas guías transcribían el código completo de los notebooks del
  docente. Se conservan solo en almacenamiento privado.
