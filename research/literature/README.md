# Literatura científica

Catálogo bibliográfico de la investigación doctoral sobre inteligencia artificial aplicada a tumores
gastrointestinales. La página publicada (`index.qmd`) lee directamente `data/literature_catalog.csv`: **no hay
que editar HTML** para mantenerla.

## Estructura

```text
research/literature/
├── index.qmd                         # página (Quarto): encabezado, indicadores y tabla
├── literature.js / literature.css    # búsqueda, filtros, paginación y diseño (sin dependencias)
├── data/
│   ├── literature_catalog.csv        # FUENTE ÚNICA DE DATOS (se edita a mano)
│   ├── anteproyecto_references_order.csv  # orden de la lista «Referencias» del anteproyecto V4
│   └── references.bib                # generado desde el CSV (títulos oficiales)
├── scripts/
│   ├── catalog_common.py             # columnas, taxonomía y utilidades compartidas
│   ├── inventory_literature.py       # importación desde la biblioteca local (solo lectura)
│   ├── normalize_metadata.py         # verificación de títulos y DOI (Crossref, DataCite, PMLR)
│   ├── generate_catalog.py           # regenera references.bib y el resumen
│   └── validate_catalog.py           # comprobaciones de integridad (también en CI)
└── reports/                          # inventario, verificación de metadatos y resumen
```

Las fichas de lectura futuras pueden seguir la convención `autor-anio-tema.md` dentro de esta carpeta.

## Tareas habituales

Todas se hacen editando **una fila** de `data/literature_catalog.csv` (con VS Code, Excel o LibreOffice,
guardando en CSV UTF-8). Después:

```bash
python3 research/literature/scripts/validate_catalog.py   # debe terminar en «OK»
python3 research/literature/scripts/generate_catalog.py   # refresca references.bib y el resumen
git add research/literature && git commit -m "Literatura: …" && git push
```

Al llegar a `main`, el flujo de GitHub Actions vuelve a validar el catálogo y publica el sitio.

### Registrar una lectura

En la fila del artículo, cambie `reading_status` a `Realizado` y escriba `reading_date` en formato
`DD/MM/AAAA` (por ejemplo, `14/11/2026`). La validación rechaza una fecha sin estado *Realizado*, un estado
*Realizado* sin fecha y las fechas futuras.

### Añadir un análisis de Latent Frontiers

Pegue la URL pública definitiva de la entrada en `latent_frontiers_url`, por ejemplo
`https://laverde97.github.io/latent-frontiers/posts/<entrada>/`. Solo debe enlazarse una entrada que trate
explícitamente el artículo (un análisis, una reseña o un experimento con sus datos que cite su DOI). **Añadir el
enlace no cambia el estado de lectura.**

### Añadir una referencia nueva

Agregue una fila al final con:

- `article_id`: único y estable, por ejemplo `lit-n001`. No lo cambie después.
- `reading_order`: el siguiente número.
- `block`: `II`, con `in_anteproyecto` = `no`.
- `title_original`: el título exacto publicado, sin abreviar ni traducir.
- `title_es`: su traducción académica.
- `authors` (separados por `;`), `citation_short` (por ejemplo, `Pérez et al. (2026)`), `publication_year`,
  `venue`, `publication_type`, `doi` (sin `https://doi.org/`) y `original_url` (preferentemente
  `https://doi.org/<doi>`).
- `primary_category`: una de las categorías de `scripts/catalog_common.py`. Si aún no está clara, use
  `Pendiente de clasificación`.
- `reading_status` = `Pendiente` y `source_inventory` con el origen del dato.

Luego ejecute `normalize_metadata.py`, que verifica el título contra Crossref, y `validate_catalog.py`.
La numeración `reading_order` debe quedar consecutiva (1…N).

### Corregir una traducción o la categoría

Edite `title_es`, `primary_category` o `secondary_tags`. El `article_id` no cambia, así que los enlaces del tipo
`…/research/literature/#lit-r021` siguen funcionando.

## Reglas del catálogo

- **Bloque I:** referencias del anteproyecto doctoral, en el orden exacto de su lista «Referencias»
  (versión 4, pp. 20–24). **Bloque II:** literatura complementaria, agrupada por categoría y ordenada según la
  guía de lectura de la biblioteca.
- Tener el PDF descargado o haberlo procesado automáticamente **no** equivale a una lectura.
- La biblioteca local, el anteproyecto y los documentos de la tesis son **solo de lectura**: los scripts no
  los modifican y reciben sus rutas como argumentos, que nunca se guardan en el repositorio.
- Solo se publican metadatos y enlaces oficiales: ni PDF ni textos completos de terceros.

## Reimportar desde la biblioteca local (opcional)

```bash
python3 research/literature/scripts/inventory_literature.py \
    --library "<ruta>/PAPER TUMORES GASTROINTESTINALES" \
    --thesis  "<ruta>/TESIS DOCTORAL" \
    [--anteproyecto-pdf "<ruta>/ANTEPROYECTO_DOCTORAL_GASTROINTESTINAL_V4.pdf"]   # requiere pypdf
python3 research/literature/scripts/normalize_metadata.py
python3 research/literature/scripts/generate_catalog.py
python3 research/literature/scripts/validate_catalog.py
```

La reimportación conserva los campos editados a mano: estado y fecha de lectura, enlace de Latent Frontiers,
traducción, categorías y notas. El detalle con rutas locales se escribe en `_local/literature/`, que Git ignora.
