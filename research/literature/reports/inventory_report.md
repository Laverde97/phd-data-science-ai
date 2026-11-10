# Informe de inventario bibliográfico

Generado por `scripts/inventory_literature.py`. Solo contiene recuentos e identificadores; no incluye rutas locales, textos completos ni PDF.

## Fuentes consultadas (solo lectura)

| Fuente | Registros | Uso |
|---|---:|---|
| Inventario maestro `CATALOGO_BIBLIOGRAFICO_v2.csv` | 120 | Registros R001–R120 (DOI resuelto en OpenAlex/Crossref) |
| Inventario histórico `CATALOGO_BIBLIOGRAFICO.csv` (v1) | 120 | Control: mismos ID que la v2 (120 coincidencias) |
| `REFERENCIAS_v2.bib` | 128 | 120 artículos + 8 libros (L01–L08) |
| `bibliografia.bib` del anteproyecto | 40 | 40 ya presentes en el inventario |
| `bibliografia_fase4.bib` | 8 | Referencias nuevas de la Fase 4 (JEPA, SSL, domain shift) |
| «Referencias» del anteproyecto V4 (PDF, pp. 20–24) | 48 | Orden del Bloque I |
| `GUIA_DE_LECTURA_v2.md` | 28 registros citados | Orden de la literatura complementaria |

## Archivos de la biblioteca

Total de archivos (recursivo): **350**.

| Extensión | Archivos |
|---|---:|
| txt | 121 |
| pdf | 94 |
| md | 35 |
| py | 22 |
| docx | 19 |
| json | 17 |
| xlsx | 10 |
| pyc | 9 |
| qmd | 5 |
| html | 5 |
| log | 5 |
| csv | 3 |
| bib | 3 |
| xml | 2 |

PDF: **94**, de los cuales 10 son la versión publicada de un preprint ya descargado (pares preprint/publicada: archivos duplicados, no registros duplicados).

| Clasificación de los PDF | Archivos |
|---|---:|
| PDF asociado a un registro del inventario | 78 |
| Documento propio del anteproyecto (no es literatura) | 10 |
| Libro o capítulo (registros L01–L08) | 4 |
| Manuscrito aceptado de un registro existente (Fase 4) | 1 |
| Archivo temporal de los scripts de descarga (no es literatura) | 1 |

## Deduplicación

- Registros únicos en el catálogo público: **136** (48 del Bloque I y 88 del Bloque II).
- Entradas de `REFERENCIAS_v2.bib` que no son libros ni coinciden por DOI con el inventario: 1 (He2026Subspecialty: versión preprint de un registro existente, fusionada por título)
- Entradas de `bibliografia.bib` del anteproyecto: 40, todas fusionadas con su registro del inventario.
- Los inventarios v1, `_respaldos/` y la búsqueda masiva cribada (`candidates_*.json`) son históricos: no se reutilizan como fuentes de registros nuevos.

## Correspondencia con el anteproyecto (V4)

- Referencias de la lista V4: 48; vinculadas a un registro: 48; sin correspondencia: 0.
- La lista se extrajo del PDF V4 en modo lectura. Su texto y su orden coinciden con los de la V5 (comprobado durante la implementación), pero el orden publicado sigue a la V4.
- No fue posible comparar byte a byte con la copia descargada «ANTEPROYECTO_DOCTORAL_GASTROINTESTINAL(4).pdf» porque esa copia no está en el equipo; se usó el PDF V4 de la biblioteca.

## Clasificación (categoría principal)

| Categoría | Registros |
|---|---:|
| Revisiones sistemáticas, metaanálisis y síntesis | 12 |
| Cáncer colorrectal | 34 |
| Cáncer gástrico | 14 |
| Cáncer esofágico | 5 |
| Tumores del estroma gastrointestinal (GIST) | 7 |
| Otros tumores digestivos | 3 |
| Estudios pan-cáncer y multitumor gastrointestinal | 9 |
| Modelos fundacionales y aprendizaje autosupervisado | 18 |
| Arquitecturas y métodos de aprendizaje | 11 |
| Robustez, validación, explicabilidad y guías de reporte | 10 |
| Datasets y benchmarks públicos | 5 |
| Libros y obras de referencia | 8 |
| **Total** | **136** |

