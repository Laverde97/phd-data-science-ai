"""Ejecuta desde un kernel nuevo, valida resultados y conserva las salidas."""
import json
import os
from pathlib import Path
import time
import nbformat
from nbclient import NotebookClient

BASE = Path(__file__).resolve().parent
os.environ.setdefault('MPLCONFIGDIR', '/tmp/ml-workshop-matplotlib')
os.environ.setdefault('IPYTHONDIR', '/tmp/ml-workshop-ipython')
os.environ.setdefault('JUPYTER_RUNTIME_DIR', '/tmp/ml-workshop-jupyter')
nb = nbformat.read(BASE / 'Taller_Regresion_Lineal.ipynb', as_version=4)
for c in nb.cells:
    if c.cell_type == 'code':
        c.outputs = []
        c.execution_count = None
original_count = len(nb.cells)
nb.cells.append(nbformat.v4.new_code_cell('''import json
assert len(df) == 100000 and list(df.columns) == ["tamano", "precio"]
assert not df_modelado.isna().any().any()
assert len(X_train) == 76000 and len(X_test) == 19000
assert np.isfinite([intercepto, coeficiente, r2, rmse, mape, prediccion_150]).all()
assert np.isclose(prediccion_150, modelo.predict(pd.DataFrame({"tamano": [150]}))[0])
control.value = 160.0
assert numero(predecir_vivienda(160), 0) in salida.value
control.value = 150.0
assert numero(prediccion_150, 0) in salida.value
print(json.dumps({
    "observaciones": len(df), "columnas": list(df.columns),
    "faltantes": df.isna().sum().to_dict(),
    "porcentaje_faltantes": (df.isna().mean()*100).to_dict(),
    "porcentaje_celdas_faltantes": pct_celdas,
    "filas_afectadas": filas_afectadas,
    "filas_modelado": len(df_modelado),
    "entrenamiento": len(X_train), "prueba": len(X_test),
    "media_imputacion": media_entrenamiento,
    "intercepto": intercepto, "coeficiente": coeficiente,
    "r2": r2, "rmse_cop": rmse, "mape_porcentaje": mape,
    "prediccion_150_cop": prediccion_150,
    "correlacion_pares_completos": correlacion,
    "rmse_base": rmse_base,
    "metricas_por_grupo": metricas_grupo.to_dict(orient="records"),
    "residuo_medio": float(residuos.mean()),
    "huella_dataframe": huella,
    "widget_validado": True,
}, ensure_ascii=False))
'''))
inicio = time.monotonic()
NotebookClient(nb, timeout=240, kernel_name='python3', resources={
    'metadata': {'path': str(BASE)}
}).execute()
resultado = json.loads(''.join(
    o.get('text', '') for o in nb.cells[-1].outputs if o.output_type == 'stream'
))
nb.cells = nb.cells[:original_count]
codigo = [c for c in nb.cells if c.cell_type == 'code']
errores = [o for c in codigo for o in c.outputs if o.output_type == 'error']
figuras = sum('image/png' in o.get('data', {}) for c in codigo for o in c.outputs)
stderr = [o.get('text', '') for c in codigo for o in c.outputs
          if o.output_type == 'stream' and o.get('name') == 'stderr']
assert not errores
assert figuras >= 3
resultado.update(celdas_codigo=len(codigo), figuras=figuras,
                 errores=len(errores), stderr=stderr,
                 segundos=round(time.monotonic()-inicio, 2))
nbformat.validate(nb)
nbformat.write(nb, BASE / 'Taller_Regresion_Lineal.ipynb')
(BASE / 'evidencias' / 'validacion_notebook.json').write_text(
    json.dumps(resultado, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(resultado, ensure_ascii=False, indent=2))
