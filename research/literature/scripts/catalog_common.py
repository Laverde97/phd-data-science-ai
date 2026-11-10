"""Shared definitions for the literature catalog scripts (stdlib only).

The single source of truth is ``data/literature_catalog.csv``. Every script in
this folder reads/writes it through the helpers below so that the column order,
the encoding (UTF-8, LF) and the controlled vocabularies stay consistent.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIT_DIR = HERE.parent
DATA_DIR = LIT_DIR / "data"
REPORTS_DIR = LIT_DIR / "reports"
CATALOG_CSV = DATA_DIR / "literature_catalog.csv"
ANTEPROYECTO_ORDER_CSV = DATA_DIR / "anteproyecto_references_order.csv"
REFERENCES_BIB = DATA_DIR / "references.bib"
REPO_ROOT = LIT_DIR.parent.parent
LOCAL_DIR = REPO_ROOT / "_local" / "literature"  # gitignored; never published

FIELDS = [
    "article_id",
    "reading_order",
    "block",
    "title_original",
    "title_es",
    "translation_review",
    "authors",
    "citation_short",
    "publication_year",
    "venue",
    "publication_type",
    "doi",
    "pmid",
    "pmcid",
    "original_url",
    "primary_category",
    "secondary_tags",
    "in_anteproyecto",
    "anteproyecto_ref_no",
    "reading_guide",
    "reading_date",
    "reading_status",
    "latent_frontiers_url",
    "source_inventory",
    "source_id",
    "metadata_verification_status",
    "notes",
]

# Columns that belong to the user: an import never overwrites a non-empty value.
USER_FIELDS = {
    "title_es",
    "translation_review",
    "primary_category",
    "secondary_tags",
    "reading_date",
    "reading_status",
    "latent_frontiers_url",
    "notes",
}

BLOCK_I = "I"   # referencias del anteproyecto doctoral (orden de la lista «Referencias», V4)
BLOCK_II = "II"  # literatura complementaria

STATUSES = ("Pendiente", "Realizado")

# Ordered taxonomy (primary categories). The order is the display order of
# Block II sections and of the thematic navigation.
CATEGORIES = [
    ("revisiones", "Revisiones sistemáticas, metaanálisis y síntesis"),
    ("colorrectal", "Cáncer colorrectal"),
    ("gastrico", "Cáncer gástrico"),
    ("esofagico", "Cáncer esofágico"),
    ("gist", "Tumores del estroma gastrointestinal (GIST)"),
    ("otros-digestivos", "Otros tumores digestivos"),
    ("pan-cancer", "Estudios pan-cáncer y multitumor gastrointestinal"),
    ("fundacionales-ssl", "Modelos fundacionales y aprendizaje autosupervisado"),
    ("arquitecturas", "Arquitecturas y métodos de aprendizaje"),
    ("robustez-validacion", "Robustez, validación, explicabilidad y guías de reporte"),
    ("datasets", "Datasets y benchmarks públicos"),
    ("libros", "Libros y obras de referencia"),
    ("pendiente", "Pendiente de clasificación"),
]
CATEGORY_LABELS = [label for _, label in CATEGORIES]
CATEGORY_RANK = {label: i for i, label in enumerate(CATEGORY_LABELS)}

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DATE_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
LF_PREFIX = "https://laverde97.github.io/latent-frontiers/posts/"


def normalize_title(text: str) -> str:
    """Lower-case, accent-free, alphanumeric-only key used for duplicate detection."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", text.lower())


def normalize_doi(doi: str) -> str:
    doi = (doi or "").strip()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi, flags=re.I)
    return doi.lower()


def read_catalog(path: Path = CATALOG_CSV) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def write_catalog(rows: list[dict], path: Path = CATALOG_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in FIELDS})


def sort_key(row: dict):
    return int(row.get("reading_order") or 10**6)
