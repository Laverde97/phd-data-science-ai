"""Captura salidas reales del PDF compilado; requiere PyMuPDF."""
from pathlib import Path
import pymupdf

base = Path(__file__).resolve().parent
pdf = pymupdf.open(base / 'Taller_Regresion_Lineal.pdf')
busquedas = {
    'captura_metricas.png': ('R²: ', 'RMSE referencia (media de entrenamiento): '),
    'captura_prediccion.png': ('Vivienda de 150 m² →', 'Vivienda de 150 m² →'),
}
for nombre, (inicio, fin) in busquedas.items():
    encontrado = False
    for pagina in pdf:
        lineas = [linea for bloque in pagina.get_text('dict')['blocks']
                  if 'lines' in bloque for linea in bloque['lines']]
        textos = [''.join(s['text'] for s in l['spans']) for l in lineas]
        candidatos = [i for i,t in enumerate(textos) if t.startswith(inicio)]
        if not candidatos:
            continue
        i = candidatos[0]
        j = next(k for k in range(i,len(textos)) if textos[k].startswith(fin))
        caja = pymupdf.Rect(lineas[i]['bbox'])
        for linea in lineas[i:j+1]:
            caja |= pymupdf.Rect(linea['bbox'])
        caja = pymupdf.Rect(57, caja.y0-8, pagina.rect.width-57, caja.y1+8)
        pagina.get_pixmap(clip=caja, dpi=180).save(base / 'evidencias' / nombre)
        print(nombre, 'página fuente', pagina.number+1)
        encontrado = True
        break
    if not encontrado:
        raise RuntimeError(f'No se encontró la salida para {nombre}')
