"""Genera el notebook a partir del QMD y añade la interacción de Colab."""
from pathlib import Path
import re
import nbformat

BASE = Path(__file__).resolve().parent
texto = (BASE / 'Taller_Regresion_Lineal.qmd').read_text()
texto = texto.split('---', 2)[2].strip()
texto = texto.split('# Capturas de resultados clave')[0]
celdas = [nbformat.v4.new_markdown_cell(
    '# Taller práctico de regresión lineal\n\n'
    '## Predicción del precio de viviendas a partir de su tamaño\n\n'
    'Universidad El Bosque · Doctorado en Ciencia de Datos e Inteligencia Artificial\n\n'
    'En Google Colab: **Entorno de ejecución → Ejecutar todas**. '
    'El notebook carga directamente el CSV público y no necesita archivos locales. '
    'Al final hay un control interactivo. La URL de apertura directa se añadirá '
    'cuando este archivo esté publicado; por ahora use **Archivo → Subir notebook**.'
)]
for i, bloque in enumerate(re.split(r'```\{python\}\n(.*?)\n```', texto, flags=re.S)):
    if i % 2:
        bloque = re.sub(r'^#\|.*\n?', '', bloque, flags=re.M).strip()
        celdas.append(nbformat.v4.new_code_cell(bloque))
    elif bloque.strip():
        celdas.append(nbformat.v4.new_markdown_cell(bloque.strip()))
celdas.append(nbformat.v4.new_markdown_cell(
    '# Predicción interactiva en Colab\n\n'
    'El control reutiliza el modelo entrenado. Cambie el tamaño y el resultado '
    'se actualizará al soltar el deslizador. Se limita al rango observado de '
    'entrenamiento para evitar extrapolaciones evidentes. No se requiere '
    '`input()`, de modo que **Ejecutar todas** no queda esperando una respuesta. '
    'El control muestra inicialmente el ejemplo de 150 m². '
    'El PDF conserva una representación estática de esa predicción.'
))
celdas.append(nbformat.v4.new_code_cell('''import ipywidgets as widgets

try:
    from google.colab import output
except ImportError:
    pass  # En Jupyter local no se necesita la integración de Colab.
else:
    output.enable_custom_widget_manager()

control = widgets.FloatSlider(
    value=150.0, min=float(X_train.tamano.min()),
    max=float(X_train.tamano.max()), step=0.1,
    description="Tamaño (m²):", continuous_update=False,
    style={"description_width": "initial"},
    layout=widgets.Layout(width="90%"),
)
salida = widgets.HTML()

def actualizar_prediccion(change=None):
    estimado = predecir_vivienda(control.value)
    salida.value = (
        f"<p>Vivienda de {numero(control.value, 1)} m² "
        f"→ Precio estimado: <strong>${cop(estimado)}</strong></p>"
    )

control.observe(actualizar_prediccion, names="value")
display(widgets.VBox([control, salida]))
actualizar_prediccion()
'''))
celdas.append(nbformat.v4.new_markdown_cell(
    'La cifra cambia al variar el tamaño según la pendiente estimada. '
    'El control permite explorar la recta; no incorpora nuevas variables ni '
    'proporciona intervalos predictivos. La ejecución estática mantiene '
    'los resultados y gráficos del taller aunque el visor no soporte widgets.'
))
nb = nbformat.v4.new_notebook(cells=celdas, metadata={
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python'},
    'colab': {'name': 'Taller_Regresion_Lineal.ipynb', 'provenance': []},
})
nbformat.write(nb, BASE / 'Taller_Regresion_Lineal.ipynb')
print(f'Notebook generado: {len(celdas)} celdas')
