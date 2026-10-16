# Fuente del informe técnico (edición pública) — Tarea 01

Esta carpeta tiene la fuente Quarto de `../workshop-01-cub200-multimodal-informe.pdf`, la edición pública del informe
técnico de la Tarea 01 de Deep Learning I.

- El texto, las tablas y las cifras son los del informe entregado (`Informe_Tecnico_CUB200_Deep_Learning_I.pdf`).
- **Única diferencia:** la Figura 2 original muestra cinco fotografías de CUB-200-2011. Aquí se sustituye por una tabla con los
  mismos cinco casos (`image_id`, especie y pérdida relativa de área). Las fotografías tienen derechos de terceros y no se
  redistribuyen.
- `figures/fig-1-particiones.png` es la Figura 1 del informe original, el gráfico de barras generado por el notebook. Es trabajo propio y no contiene datos de terceros.

| Archivo | Uso |
|---------|-----|
| `workshop-01-cub200-multimodal-informe.qmd` | Texto del informe |
| `_quarto.yml` | Formato PDF (KOMA-Script, LuaLaTeX, TeX Gyre), mismo estilo que las guías de la Clase 02 |
| `report-style.tex` | Encabezados, pies y colores |
| `figures/fig-1-particiones.png` | Figura 1 |

## El sitio no compila esta carpeta

El `_quarto.yml` de la raíz del repositorio excluye esta carpeta del render. GitHub Pages publica el PDF ya generado.
El informe no ejecuta código.

## Cómo regenerar el PDF

```bash
# Copiar la carpeta fuera del repositorio, para que Quarto no la trate como parte del sitio
cp -r report-source /tmp/informe-cub200 && cd /tmp/informe-cub200
quarto render workshop-01-cub200-multimodal-informe.qmd     # requiere TinyTeX (quarto install tinytex)
cp _out/workshop-01-cub200-multimodal-informe.pdf <repo>/semesters/semester-01/deep-learning-1/workshops/workshop-01-cub200-multimodal/
```
