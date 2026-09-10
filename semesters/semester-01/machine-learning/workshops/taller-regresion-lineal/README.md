# Taller de regresión lineal: precios de viviendas

Construir e interpretar una regresión lineal simple del precio (COP) sobre el tamaño (m²), con manejo de faltantes y evaluación independiente.

Datos: [CSV público](https://storage.googleapis.com/backet_doctorado_ueb_2026_2/datos_viviendas_faltantes.csv), cargado directamente con `pandas.read_csv`. No se guarda el dataset en el repositorio.

## Archivos

- [Notebook ejecutado](Taller_Regresion_Lineal.ipynb): análisis completo y predicción interactiva.
- [Fuente Quarto](Taller_Regresion_Lineal.qmd): código, resultados e interpretación académica.
- [PDF final](Taller_Regresion_Lineal.pdf): documento generado desde Quarto.
- [Reporte técnico](REPORTE_TECNICO.md): validación, decisiones y detalles del entorno.
- `requirements.txt`: dependencias para ejecución local.
- `sincronizar_notebook.py`: genera el notebook desde el QMD y añade el control interactivo. Al ejecutarlo se borran las salidas del notebook generado; después debe validarse de nuevo.
- `validar_notebook.py`: ejecuta un kernel nuevo, comprueba resultados e interacción y guarda el notebook ejecutado y evidencia JSON.
- `capturar_resultados.py`: recorta las salidas reales de métricas y predicción del PDF para el apéndice; requiere `requirements-validacion.txt`.
- `evidencias/`: versiones verificadas, resultados de validación y capturas.
- `_quarto.yml`: aísla el documento del formato y la navegación del sitio principal.

## Google Colab

Descargue `Taller_Regresion_Lineal.ipynb`, abra [Google Colab](https://colab.research.google.com/) y seleccione **Archivo → Subir notebook**. Ejecute **Entorno de ejecución → Ejecutar todas**. El control final actualiza el precio al cambiar el tamaño. Requiere conexión a Internet para cargar el CSV.

No se incluye badge hasta que la ruta del notebook esté publicada y verificada en GitHub. No se ha realizado push.

## Ejecución local y PDF

Desde esta carpeta, con Python, Quarto y LaTeX/TinyTeX disponibles:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python validar_notebook.py
quarto render Taller_Regresion_Lineal.qmd
```

En Windows, active el entorno con `.venv\Scripts\Activate.ps1` en PowerShell. El PDF se genera en esta misma carpeta. Si Quarto no selecciona el entorno activo, establezca `QUARTO_PYTHON` a la ruta de su intérprete. No es necesario regenerar el notebook para abrirlo o ejecutarlo.

La validación usó TinyTeX aislado en `/tmp`, sin cambiar configuraciones globales. Las versiones exactas están en `evidencias/entorno-validado.txt`; los rangos de `requirements.txt` permiten entornos de Colab y Python anteriores.

Para renovar las capturas después de cambiar el análisis, instale `requirements-validacion.txt`, renderice el QMD, ejecute `python capturar_resultados.py` y vuelva a renderizar. El PDF final ya contiene las capturas de los resultados verificados.
