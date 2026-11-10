#!/usr/bin/env python3
"""Generate derived files from the single source of truth (literature_catalog.csv).

* ``data/references.bib``      – BibTeX with the official (untranslated) titles.
* ``reports/catalog_summary.md`` – counts per block, category and reading status.

The web page reads the CSV directly, so after editing the CSV this script is
only needed to refresh the BibTeX and the summary.

    python3 research/literature/scripts/generate_catalog.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_common import (  # noqa: E402
    BLOCK_I, CATEGORY_LABELS, REFERENCES_BIB, REPORTS_DIR, read_catalog, sort_key,
)

ENTRY_TYPE = {
    "Libro": "book",
    "Artículo de conferencia": "inproceedings",
    "Preprint": "misc",
    "Documento de posición": "misc",
}


def bib_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def to_bib(r: dict) -> str:
    etype = ENTRY_TYPE.get(r["publication_type"], "article")
    authors = " and ".join(a.strip() for a in r["authors"].split(";") if a.strip())
    venue_field = {"article": "journal", "inproceedings": "booktitle", "book": "publisher"}.get(etype, "howpublished")
    fields = [
        ("title", "{" + bib_escape(r["title_original"]) + "}"),
        ("author", bib_escape(authors)),
        ("year", r["publication_year"]),
        (venue_field, bib_escape(r["venue"])),
        ("doi", r["doi"]),
        ("url", r["original_url"]),
        ("pmid", r["pmid"]),
        ("pmcid", r["pmcid"]),
    ]
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
    return f"@{etype}{{{r['article_id']},\n{body}\n}}"


def main() -> None:
    rows = sorted(read_catalog(), key=sort_key)
    header = ("% references.bib — generado por scripts/generate_catalog.py a partir de data/literature_catalog.csv.\n"
              "% Títulos originales oficiales (sin traducir). No editar a mano: edite el CSV y regenere.\n\n")
    REFERENCES_BIB.write_text(header + "\n\n".join(to_bib(r) for r in rows) + "\n", encoding="utf-8")

    cats = Counter(r["primary_category"] for r in rows)
    status = Counter(r["reading_status"] for r in rows)
    md = ["# Resumen del catálogo", "",
          "Generado por `scripts/generate_catalog.py` a partir de `data/literature_catalog.csv`.", "",
          "| Indicador | Valor |", "|---|---:|",
          f"| Referencias únicas | {len(rows)} |",
          f"| Bloque I · referencias del anteproyecto (orden V4) | {sum(r['block'] == BLOCK_I for r in rows)} |",
          f"| Bloque II · literatura complementaria | {sum(r['block'] != BLOCK_I for r in rows)} |",
          f"| Lecturas realizadas | {status['Realizado']} |",
          f"| Lecturas pendientes | {status['Pendiente']} |",
          f"| Fechas de lectura registradas | {sum(bool(r['reading_date']) for r in rows)} |",
          f"| Con enlace al artículo original | {sum(bool(r['original_url']) for r in rows)} |",
          f"| Con DOI | {sum(bool(r['doi']) for r in rows)} |",
          f"| Análisis vinculados en Latent Frontiers | {sum(bool(r['latent_frontiers_url']) for r in rows)} |",
          f"| Traducciones marcadas para revisión | {sum(r['translation_review'] == 'sí' for r in rows)} |",
          "", "## Categorías principales", "", "| Categoría | Bloque I | Bloque II | Total |", "|---|---:|---:|---:|"]
    for c in CATEGORY_LABELS:
        b1 = sum(1 for r in rows if r["primary_category"] == c and r["block"] == BLOCK_I)
        tot = cats.get(c, 0)
        md.append(f"| {c} | {b1} | {tot - b1} | {tot} |")
    md.append(f"| **Total** | **{sum(r['block'] == BLOCK_I for r in rows)}** | "
              f"**{sum(r['block'] != BLOCK_I for r in rows)}** | **{len(rows)}** |")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "catalog_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"references.bib: {len(rows)} entradas · resumen actualizado")


if __name__ == "__main__":
    main()
