#!/usr/bin/env python3
"""Inventory the local scientific library and (re)build the catalog CSV.

READ-ONLY with respect to every source: the library, the thesis folder and the
anteproyecto PDF are only opened for reading. Nothing is moved, renamed or
rewritten there.

Usage (paths are passed as arguments; they are never stored in the repo):

    python3 research/literature/scripts/inventory_literature.py \
        --library   "/ruta/a/PAPER TUMORES GASTROINTESTINALES" \
        --thesis    "/ruta/a/TESIS DOCTORAL" \
        [--anteproyecto-pdf "/ruta/a/ANTEPROYECTO_DOCTORAL_GASTROINTESTINAL_V4.pdf"]

* ``--anteproyecto-pdf`` (optional, needs ``pypdf``) re-extracts the
  «Referencias» list (pp. 20–24 of V4) into ``data/anteproyecto_references_order.csv``.
  Without it the committed order file is reused.
* Existing rows of ``data/literature_catalog.csv`` are merged by
  ``article_id``; user-maintained columns (reading status/date, Latent
  Frontiers URL, translation, categories, notes) are never overwritten.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_common import (  # noqa: E402
    ANTEPROYECTO_ORDER_CSV, BLOCK_I, BLOCK_II, CATALOG_CSV, CATEGORY_RANK, LOCAL_DIR,
    REPORTS_DIR, USER_FIELDS, normalize_doi, normalize_title, read_catalog, write_catalog,
)

CATALOG_SRC = "00_CATALOGO_BIBLIOGRAFICO/CATALOGO_BIBLIOGRAFICO_v2.csv"
CATALOG_V1_SRC = "00_CATALOGO_BIBLIOGRAFICO/CATALOGO_BIBLIOGRAFICO.csv"
BIB_SRC = "00_CATALOGO_BIBLIOGRAFICO/REFERENCIAS_v2.bib"
GUIDE_SRC = "00_CATALOGO_BIBLIOGRAFICO/GUIA_DE_LECTURA_v2.md"
FASE4_BIB = "bibliografia_fase4.bib"
ANTE_BIB = "bibliografia.bib"

# Official proceedings pages for records registered with an arXiv DOI (taken from
# the anteproyecto V4 reference list / PMLR; verified online by validate --online).
PROCEEDINGS_URL = {
    "R085": "https://proceedings.mlr.press/v80/ilse18a.html",
    "R108": "https://proceedings.mlr.press/v97/tan19a.html",
}


# --------------------------------------------------------------------------- bib
def parse_bib(text: str) -> list[dict]:
    """Minimal, brace-aware BibTeX reader (enough for the library's files)."""
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key, pos = m.group(1).lower(), m.group(2), m.end()
        depth, i = 1, pos
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[pos:i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            j = fm.end()
            if j < len(body) and body[j] == "{":
                d, k = 0, j
                while k < len(body):
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                    if d == 0:
                        break
                val = body[j + 1:k - 1]
            else:
                val = re.match(r"[^,\n]*", body[j:]).group(0)
            fields.setdefault(fm.group(1).lower(), val.strip())
        clean = {k: re.sub(r"\s+", " ", v.replace("{", "").replace("}", "")).replace("\\&", "&").replace("\\_", "_").strip()
                 for k, v in fields.items()}
        entries.append({"type": etype, "key": key, **clean})
    return entries


def bib_authors(raw: str) -> str:
    """'A B and C D' or 'Surname, X. (Ed.)' -> semicolon list (kept as written)."""
    if " and " in raw:
        return "; ".join(a.strip() for a in raw.split(" and "))
    return raw


# ------------------------------------------------------------ anteproyecto (V4)
def extract_anteproyecto_order(pdf: Path) -> list[dict]:
    try:
        import pypdf  # type: ignore
    except ImportError:  # pragma: no cover
        sys.exit("pypdf no está instalado: instálalo en un entorno virtual o omite --anteproyecto-pdf")
    reader = pypdf.PdfReader(str(pdf))
    pages = [p.extract_text() or "" for p in reader.pages]
    text = "\n".join(f"=====PAGE {i + 1}\n{t}" for i, t in enumerate(pages))
    start = text.index("\nReferencias\n", text.index("=====PAGE 20"))
    end = text.index("\nAnexos\n", start)
    lines = [ln for ln in text[start + 13:end].split("\n")
             if ln.strip() and not ln.startswith("=====PAGE") and not re.fullmatch(r"\d{1,2}", ln.strip())]
    starts = re.compile(r"^(van der |de |von )?[A-ZÀ-Ž][\w'’\-À-ž]+( [A-ZÀ-Ž][\w'’\-À-ž]+)*, [A-ZÀ-Ž]")
    groups: list[list[str]] = []
    for ln in lines:
        if not groups or ("http" in " ".join(groups[-1]) and starts.match(ln)):
            groups.append([ln])
        else:
            groups[-1].append(ln)
    out = []
    for n, g in enumerate(groups, 1):
        s = " ".join(g)
        k = s.index("https:")
        url = s[k:].replace(" ", "")
        body = re.sub(r" ([,.;:])", r"\1", re.sub(r"\s+", " ", s[:k]).strip())
        m = re.search(r"doi\.org/(.+)$", url)
        out.append({"ref_no": n, "reference_apa": f"{body} {url}", "doi": normalize_doi(m.group(1)) if m else "",
                    "url": url, "article_id": ""})
    return out


def read_order_csv() -> list[dict]:
    with ANTEPROYECTO_ORDER_CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_order_csv(rows: list[dict]) -> None:
    ANTEPROYECTO_ORDER_CSV.parent.mkdir(parents=True, exist_ok=True)
    with ANTEPROYECTO_ORDER_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["ref_no", "article_id", "doi", "url", "reference_apa"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in w.fieldnames})


# ------------------------------------------------------------- classification
def pub_type(audited: str, base: str) -> str:
    a = audited.lower()
    if "metaanálisis" in a:
        return "Revisión sistemática y metaanálisis"
    if "revisión sistemática" in a:
        return "Revisión sistemática"
    if "revisión narrativa" in a:
        return "Revisión narrativa"
    if "guía de reporte" in a:
        return "Guía de reporte"
    if "declaración de posición" in a:
        return "Declaración de posición"
    if "conferencia" in a:
        return "Artículo de conferencia"
    if "dataset" in a:
        return "Artículo de datos"
    if "ensayo aleatorizado" in a:
        return "Artículo original (ensayo aleatorizado)"
    if "preprint" in (base or "").lower() and "revisado por pares" not in a:
        return "Preprint"
    if "ensayo aleatorizado" in a:
        return "Artículo original (ensayo aleatorizado)"
    return "Artículo original"


ROBUSTNESS_IDS = {"R010", "R012", "R019", "R111"}


def primary_category(rec: dict, src: dict) -> str:
    """Deterministic first-pass rule; reviewed manually afterwards."""
    ptype = rec["publication_type"]
    tumour = src.get("Tipo de tumor", "")
    focus = src.get("Enfoque", "")
    sid = rec["source_id"]
    title = rec["title_original"].lower()
    if ptype == "Libro":
        return "Libros y obras de referencia"
    if ptype in {"Guía de reporte", "Declaración de posición"} or sid in ROBUSTNESS_IDS \
            or re.search(r"domain shift|stain color|site-specific", title):
        return "Robustez, validación, explicabilidad y guías de reporte"
    if "Dataset" in focus or ptype == "Artículo de datos":
        return "Datasets y benchmarks públicos"
    if ptype.startswith("Revisión"):
        return "Revisiones sistemáticas, metaanálisis y síntesis"
    if focus in {"Foundation model", "Modelo visión-lenguaje"} \
            or re.search(r"self-supervised|joint-embedding|jepa|vicreg|rankme|effective rank|autonomous machine", title):
        if not tumour.startswith(("Colorrectal", "Gástrico", "Esofágico", "GIST")):
            return "Modelos fundacionales y aprendizaje autosupervisado"
    mapping = {
        "Colorrectal": "Cáncer colorrectal",
        "Gástrico": "Cáncer gástrico",
        "Esofágico": "Cáncer esofágico",
        "GIST": "Tumores del estroma gastrointestinal (GIST)",
        "Neuroendocrino": "Otros tumores digestivos",
        "Intestino delgado": "Otros tumores digestivos",
        "Páncreas": "Otros tumores digestivos",
        "Varios tumores GI": "Estudios pan-cáncer y multitumor gastrointestinal",
        "Pan-cáncer": "Estudios pan-cáncer y multitumor gastrointestinal",
        "Metodológico": "Arquitecturas y métodos de aprendizaje",
    }
    for prefix, cat in mapping.items():
        if tumour.startswith(prefix):
            return cat
    return "Pendiente de clasificación"


TAG_RULES = [
    (r"histopatolog", "modality", "Histopatología digital"),
    (r"endoscop|colonoscop|cápsula|ecoendoscop", "modality", "Endoscopia"),
    (r"tomograf|resonancia|pet/ct", "modality", "Radiología"),
    (r"^multimodal", "modality", "Multimodal"),
]
TITLE_TAGS = [
    (r"transformer|vision transformer|\bvit\b|16x16", "Vision Transformers"),
    (r"convolutional|\bcnn\b|densely connected|residual learning|efficientnet|u-net", "CNN"),
    (r"self-supervised|contrastive|joint-embedding|jepa|vicreg|rankme", "Aprendizaje autosupervisado"),
    (r"jepa|joint-embedding", "JEPA / I-JEPA"),
    (r"foundation model", "Modelos fundacionales"),
    (r"multiple instance|weakly", "MIL / supervisión débil"),
    (r"segmentation|segmented", "Segmentación"),
    (r"detection|detect", "Detección"),
    (r"classification|subtyping|diagnos", "Clasificación / diagnóstico"),
    (r"survival|prognos|outcome|recurrence", "Pronóstico"),
    (r"response|therapy|neoadjuvant", "Respuesta terapéutica"),
    (r"microsatellite|msi|mutation|biomarker|molecular|genomic|ebv|epstein|tumor mutational|hrd", "Biomarcadores"),
    (r"multicent|multi-cent|multi-institution|multicentric|international multicenter", "Validación multicéntrica"),
    (r"swarm|federated|decentralized", "Aprendizaje federado"),
    (r"explainab|interpretab|grad-cam|explanation", "Explicabilidad"),
    (r"domain shift|site-specific|stain", "Domain shift / tinción"),
    (r"radiomic", "Radiómica"),
    (r"multimodal|histology-genomic|vision.language|visual-language", "Aprendizaje multimodal"),
    (r"randomi[sz]ed", "Ensayo aleatorizado"),
    (r"benchmark", "Benchmark"),
]
FOCUS_TAGS = {
    "Deep Learning": ["Deep learning"],
    "Foundation model": ["Modelos fundacionales"],
    "Radiómica + ML tradicional": ["Radiómica", "Machine learning tradicional"],
    "Híbrido DL + ML": ["Deep learning", "Machine learning tradicional"],
    "Modelo visión-lenguaje": ["Modelos fundacionales", "Aprendizaje multimodal"],
    "ML tradicional": ["Machine learning tradicional"],
}


def secondary_tags(rec: dict, src: dict) -> str:
    tags: list[str] = []
    modality = src.get("Modalidad de imagen", "").lower()
    for pat, _, tag in TAG_RULES:
        if re.search(pat, modality):
            tags.append(tag)
    tags += FOCUS_TAGS.get(src.get("Enfoque", ""), [])
    title = rec["title_original"].lower()
    for pat, tag in TITLE_TAGS:
        if re.search(pat, title):
            tags.append(tag)
    if rec["publication_type"] == "Preprint":
        tags.append("Preprint")
    seen = []
    for t in tags:
        if t not in seen:
            seen.append(t)
    return "; ".join(seen)


# --------------------------------------------------------------- citations
PARTICLES = ("van der ", "van den ", "van ", "von ", "de ", "del ", "da ", "dos ", "le ")


def surname(full: str) -> str:
    full = re.sub(r"\(Eds?\.\)", "", full).strip()
    if "," in full:  # "Surname, X."
        return full.split(",")[0].strip()
    low = full.lower()
    for p in PARTICLES:
        idx = low.find(" " + p)
        if idx >= 0:
            return full[idx + 1:].strip()
    return full.split()[-1] if full.split() else full


def citation_short(authors: str, year: str, apa: str = "") -> str:
    if apa:  # Block I: take author surnames exactly as printed in the V4 list
        head = apa.split(f"({year}")[0] if year else apa
        names = re.findall(r"(?:^|, |& )((?:van der |van den |de |von )?[A-ZÀ-Ž][^,&()]*?), (?:[A-ZÀ-Ž]\.)", head)
        n_auth = head.count("., ") + 1 if names else 0
        if names:
            if len(names) == 1 and "&" not in head:
                return f"{names[0]} ({year})"
            if len(names) == 2 and n_auth <= 3:
                return f"{names[0]} y {names[1]} ({year})"
            return f"{names[0]} et al. ({year})"
    parts = [a for a in re.split(r";|, (?=[A-Z][a-z]+, )|, & |\\& | & ", authors) if a.strip()]
    if not parts:
        return f"s. a. ({year})"
    if len(parts) == 1:
        return f"{surname(parts[0])} ({year})"
    if len(parts) == 2:
        return f"{surname(parts[0])} y {surname(parts[1])} ({year})"
    return f"{surname(parts[0])} et al. ({year})"


# ------------------------------------------------------------------- guide
def guide_ranks(library: Path) -> dict[str, tuple[int, str]]:
    text = (library / GUIDE_SRC).read_text(encoding="utf-8")
    part_b = text.index("## Parte B")
    ranks: dict[str, tuple[int, str]] = {}
    for n, m in enumerate(re.finditer(r"\*\*\d+\. \[(R\d{3})\]", text[:part_b]), 1):
        ranks.setdefault(m.group(1), (n, "Guía de lectura v2 · Parte A"))
    for n, m in enumerate(re.finditer(r"^- \[(R\d{3})\]", text[part_b:], re.M), 1):
        ranks.setdefault(m.group(1), (100 + n, "Guía de lectura v2 · Parte B"))
    return ranks


# -------------------------------------------------------------------- main
def build(library: Path, thesis: Path, pdf: Path | None) -> None:
    src_rows = list(csv.DictReader((library / CATALOG_SRC).open(encoding="utf-8-sig")))
    bib = parse_bib((library / BIB_SRC).read_text(encoding="utf-8"))
    fase4 = parse_bib((thesis / FASE4_BIB).read_text(encoding="utf-8"))
    ante_bib = parse_bib((thesis / ANTE_BIB).read_text(encoding="utf-8"))
    ranks = guide_ranks(library)

    records: dict[str, dict] = {}
    src_by_id: dict[str, dict] = {}
    for r in src_rows:
        sid = r["ID"]
        doi = normalize_doi(r["DOI"])
        notes = []
        pub = r.get("Versión publicada del registro arXiv", "")
        m = re.search(r"doi\.org/(10\.\S+)", pub)
        if m:  # preprint registered in Phase 1; published version known
            notes.append(f"DOI del preprint registrado en el inventario: {doi}")
            doi = normalize_doi(m.group(1))
        url = PROCEEDINGS_URL.get(sid) or (f"https://doi.org/{doi}" if doi else r.get("URL oficial", ""))
        rec = {
            "article_id": f"lit-{sid.lower()}",
            "source_id": sid,
            "title_original": r["Título original"].strip(),
            "authors": r["Autores"].strip(),
            "publication_year": r["Año"].strip(),
            "venue": r["Revista o fuente"].strip(),
            "doi": doi,
            "pmid": r.get("PMID", "").strip(),
            "pmcid": r.get("PMCID", "").strip(),
            "original_url": url,
            "source_inventory": f"CATALOGO_BIBLIOGRAFICO_v2.csv#{sid}",
            "metadata_verification_status": "Inventario: DOI resuelto en OpenAlex/Crossref (Fases 1–2)",
            "notes": " | ".join(notes),
        }
        rec["publication_type"] = pub_type(r.get("Tipo de publicación (auditado)", ""), r.get("Tipo de publicación", ""))
        records[rec["article_id"]] = rec
        src_by_id[rec["article_id"]] = r

    for n, e in enumerate(fase4, 1):
        doi = normalize_doi(e.get("doi", ""))
        rec = {
            "article_id": f"lit-f4-{n:02d}",
            "source_id": e["key"],
            "title_original": e.get("title", ""),
            "authors": bib_authors(e.get("author", "")),
            "publication_year": e.get("year", ""),
            "venue": e.get("journal") or e.get("booktitle") or e.get("howpublished", ""),
            "doi": doi,
            "pmid": "", "pmcid": "",
            "original_url": f"https://doi.org/{doi}" if doi else e.get("url", ""),
            "source_inventory": f"bibliografia_fase4.bib#{e['key']}",
            "metadata_verification_status": "Inventario: verificada en fuente oficial (Fase 4)",
            "notes": e.get("note", ""),
            "publication_type": ("Preprint" if "preprint" in e.get("note", "").lower()
                                 else "Documento de posición" if e["type"] == "misc"
                                 else "Artículo de conferencia" if e["type"] == "inproceedings"
                                 else "Artículo original"),
        }
        records[rec["article_id"]] = rec
        src_by_id[rec["article_id"]] = {"Enfoque": "", "Tipo de tumor": "Metodológico", "Modalidad de imagen": ""}

    catalog_dois = {r["doi"] for r in records.values() if r["doi"]}
    dup_bib = []
    for e in bib:
        if e["type"] == "book":
            m = re.match(r"Libro(L\d+)", e["key"])
            sid = m.group(1) if m else e["key"]
            doi = normalize_doi(e.get("doi", ""))
            rec = {
                "article_id": f"lit-{sid.lower()}",
                "source_id": sid,
                "title_original": e.get("title", ""),
                "authors": e.get("author", ""),
                "publication_year": e.get("year", ""),
                "venue": e.get("publisher", ""),
                "doi": doi, "pmid": "", "pmcid": "",
                "original_url": f"https://doi.org/{doi}" if doi and "arxiv" not in doi else e.get("url", ""),
                "source_inventory": f"REFERENCIAS_v2.bib#{e['key']}",
                "metadata_verification_status": "Inventario: metadatos del registro de libros (Fase 1)",
                "notes": "",
                "publication_type": "Libro",
            }
            records[rec["article_id"]] = rec
            src_by_id[rec["article_id"]] = {"Enfoque": "", "Tipo de tumor": "", "Modalidad de imagen": ""}
        elif normalize_doi(e.get("doi", "")) not in {normalize_doi(r["DOI"]) for r in src_rows}:
            dup_bib.append(e)

    # ---------------------------------------------------------- Block I order
    if pdf:
        order = extract_anteproyecto_order(pdf)
    else:
        order = read_order_csv()
    by_doi = {r["doi"]: aid for aid, r in records.items() if r["doi"]}
    for r in records.values():  # preprint DOIs registered in notes also match
        m = re.search(r"preprint registrado en el inventario: (\S+)", r["notes"])
        if m:
            by_doi.setdefault(m.group(1), r["article_id"])
    by_title = {normalize_title(r["title_original"]): aid for aid, r in records.items()}
    unmatched = []
    for o in order:
        aid = o.get("article_id") or by_doi.get(normalize_doi(o.get("doi", "")))
        if not aid:
            apa_key = normalize_title(o["reference_apa"])
            aid = next((a for t, a in by_title.items() if len(t) > 25 and t in apa_key), "")
        o["article_id"] = aid
        if not aid:
            unmatched.append(o)
    write_order_csv(order)
    ante_pos = {o["article_id"]: int(o["ref_no"]) for o in order if o["article_id"]}
    apa_by_id = {o["article_id"]: o["reference_apa"] for o in order if o["article_id"]}

    # ---------------------------------------------------- merge with existing
    existing = {r["article_id"]: r for r in read_catalog()}
    out = []
    for aid, rec in records.items():
        src = src_by_id[aid]
        rec["block"] = BLOCK_I if aid in ante_pos else BLOCK_II
        rec["in_anteproyecto"] = "sí" if aid in ante_pos else "no"
        rec["anteproyecto_ref_no"] = str(ante_pos.get(aid, ""))
        g = ranks.get(rec["source_id"])
        rec["reading_guide"] = g[1] if g else ""
        rec["citation_short"] = citation_short(rec["authors"], rec["publication_year"], apa_by_id.get(aid, ""))
        rec["primary_category"] = primary_category(rec, src)
        rec["secondary_tags"] = secondary_tags(rec, src)
        rec["reading_status"] = "Pendiente"
        rec["reading_date"] = ""
        rec["latent_frontiers_url"] = ""
        rec["title_es"] = ""
        rec["translation_review"] = ""
        rec["_guide_rank"] = g[0] if g else 999
        rec["_priority"] = src.get("Prioridad de lectura", "Z")[:1] or "Z"
        old = existing.get(aid)
        if old:
            for f in USER_FIELDS:
                if old.get(f, "").strip():
                    rec[f] = old[f]
            # verified titles/metadata written by normalize_metadata.py are kept
            for f in ("title_original", "metadata_verification_status", "doi", "original_url"):
                if old.get(f, "").strip() and "verificad" in old.get("metadata_verification_status", "").lower():
                    rec[f] = old[f]
        out.append(rec)
    # rows added by hand (not produced by this import) are kept untouched
    for aid, old in existing.items():
        if aid not in records:
            keep = dict(old)
            keep.update({"_guide_rank": 999, "_priority": "Z"})
            out.append(keep)

    block1 =sorted((r for r in out if r["block"] == BLOCK_I), key=lambda r: int(r["anteproyecto_ref_no"]))
    block2 = sorted((r for r in out if r["block"] == BLOCK_II),
                    key=lambda r: (CATEGORY_RANK.get(r["primary_category"], 99), r["_guide_rank"], r["_priority"],
                                   -int(r["publication_year"] or 0), r["article_id"]))
    final = block1 + block2
    for n, r in enumerate(final, 1):
        r["reading_order"] = str(n)
    write_catalog(final)

    # ---------------------------------------------------------------- report
    write_inventory_report(library, thesis, pdf, src_rows, bib, fase4, ante_bib, records, order,
                           unmatched, dup_bib, final)
    print(f"Catálogo: {len(final)} registros ({len(block1)} en el Bloque I, {len(block2)} en el Bloque II) -> {CATALOG_CSV}")
    if unmatched:
        print(f"ATENCIÓN: {len(unmatched)} referencias del anteproyecto sin correspondencia; ver informe", file=sys.stderr)
        sys.exit(2)


def write_inventory_report(library, thesis, pdf, src_rows, bib, fase4, ante_bib, records, order,
                           unmatched, dup_bib, final) -> None:
    files = [p for p in library.rglob("*") if p.is_file()]
    ext = Counter(p.suffix.lower().lstrip(".") or "(sin extensión)" for p in files)
    pdfs = [p for p in files if p.suffix.lower() == ".pdf"]
    linked_paths = set()
    for r in src_rows:
        for col in ("Ruta local del archivo", "Ruta local (Fase 2)", "PDF versión publicada (Fase 2)"):
            v = (r.get(col) or "").strip()
            if v.lower().endswith(".pdf"):
                linked_paths.add(v.replace("\\", "/").split("PAPER TUMORES GASTROINTESTINALES/")[-1])
    rel = [p.relative_to(library).as_posix() for p in pdfs]
    groups = Counter()
    orphan_detail = []
    for r in rel:
        if r in linked_paths:
            groups["PDF asociado a un registro del inventario"] += 1
        elif r.startswith("14_LIBROS_ACADEMICOS/"):
            groups["Libro o capítulo (registros L01–L08)"] += 1
        elif r.startswith("18_ANTEPROYECTO_DOCTORAL/"):
            groups["Documento propio del anteproyecto (no es literatura)"] += 1
        elif r.startswith("19_FASE4_TEXTOS_COMPLETOS/"):
            groups["Manuscrito aceptado de un registro existente (Fase 4)"] += 1
        elif "/_scripts/" in "/" + r:
            groups["Archivo temporal de los scripts de descarga (no es literatura)"] += 1
        else:
            groups["PDF sin registro asociado (revisión manual)"] += 1
            orphan_detail.append(r)
    publicadas = sum(1 for r in rel if r.endswith("_PUBLICADA.pdf"))
    v1 = list(csv.DictReader((library / CATALOG_V1_SRC).open(encoding="utf-8-sig")))
    v1_ids = {r["ID"] for r in v1}
    in_ante_bib = sum(1 for e in ante_bib if normalize_doi(e.get("doi", "")) in {r["doi"] for r in records.values()}
                      or normalize_title(e.get("title", "")) in {normalize_title(r["title_original"]) for r in records.values()})
    cats = Counter(r["primary_category"] for r in final)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md = ["# Informe de inventario bibliográfico", "",
          "Generado por `scripts/inventory_literature.py`. Solo contiene recuentos e identificadores; "
          "no incluye rutas locales, textos completos ni PDF.", "",
          "## Fuentes consultadas (solo lectura)", "",
          "| Fuente | Registros | Uso |", "|---|---:|---|",
          f"| Inventario maestro `CATALOGO_BIBLIOGRAFICO_v2.csv` | {len(src_rows)} | Registros R001–R120 (DOI resuelto en OpenAlex/Crossref) |",
          f"| Inventario histórico `CATALOGO_BIBLIOGRAFICO.csv` (v1) | {len(v1)} | Control: mismos ID que la v2 ({len(v1_ids & {r['ID'] for r in src_rows})} coincidencias) |",
          f"| `REFERENCIAS_v2.bib` | {len(bib)} | 120 artículos + {sum(1 for e in bib if e['type']=='book')} libros (L01–L08) |",
          f"| `bibliografia.bib` del anteproyecto | {len(ante_bib)} | {in_ante_bib} ya presentes en el inventario |",
          f"| `bibliografia_fase4.bib` | {len(fase4)} | Referencias nuevas de la Fase 4 (JEPA, SSL, domain shift) |",
          f"| «Referencias» del anteproyecto V4 (PDF, pp. 20–24) | {len(order)} | Orden del Bloque I |",
          f"| `GUIA_DE_LECTURA_v2.md` | {sum(1 for r in final if r['reading_guide'])} registros citados | Orden de la literatura complementaria |",
          "", "## Archivos de la biblioteca", "",
          f"Total de archivos (recursivo): **{len(files)}**.", "",
          "| Extensión | Archivos |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in ext.most_common()]
    md += ["", f"PDF: **{len(pdfs)}**, de los cuales {publicadas} son la versión publicada de un preprint ya descargado "
           "(pares preprint/publicada: archivos duplicados, no registros duplicados).", "",
           "| Clasificación de los PDF | Archivos |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in groups.most_common()]
    md += ["", "## Deduplicación", "",
           f"- Registros únicos en el catálogo público: **{len(final)}** "
           f"({sum(1 for r in final if r['block']=='I')} del Bloque I y {sum(1 for r in final if r['block']=='II')} del Bloque II).",
           f"- Entradas de `REFERENCIAS_v2.bib` que no son libros ni coinciden por DOI con el inventario: {len(dup_bib)} "
           + (f"({', '.join(e['key'] for e in dup_bib)}: versión preprint de un registro existente, fusionada por título)" if dup_bib else ""),
           f"- Entradas de `bibliografia.bib` del anteproyecto: {len(ante_bib)}, todas fusionadas con su registro del inventario.",
           "- Los inventarios v1, `_respaldos/` y la búsqueda masiva cribada (`candidates_*.json`) son históricos: "
           "no se reutilizan como fuentes de registros nuevos.", "",
           "## Correspondencia con el anteproyecto (V4)", "",
           f"- Referencias de la lista V4: {len(order)}; vinculadas a un registro: {len(order) - len(unmatched)}; sin correspondencia: {len(unmatched)}.",
           "- La lista se extrajo del PDF V4 en modo lectura. Su texto y su orden coinciden con los de la V5 "
           "(comprobado durante la implementación), pero el orden publicado sigue a la V4.",
           "- No fue posible comparar byte a byte con la copia descargada «ANTEPROYECTO_DOCTORAL_GASTROINTESTINAL(4).pdf» "
           "porque esa copia no está en el equipo; se usó el PDF V4 de la biblioteca.", "",
           "## Clasificación (categoría principal)", "", "| Categoría | Registros |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in sorted(cats.items(), key=lambda kv: CATEGORY_RANK.get(kv[0], 99))]
    md += [f"| **Total** | **{sum(cats.values())}** |", ""]
    (REPORTS_DIR / "inventory_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    (LOCAL_DIR / "inventory_detail.json").write_text(json.dumps({
        "library": str(library), "thesis": str(thesis), "anteproyecto_pdf": str(pdf) if pdf else None,
        "orphan_pdfs": orphan_detail, "unmatched_anteproyecto": unmatched,
        "pdf_groups": dict(groups),
    }, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--thesis", required=True, type=Path)
    ap.add_argument("--anteproyecto-pdf", type=Path)
    a = ap.parse_args()
    for p in (a.library, a.thesis):
        if not p.is_dir():
            sys.exit(f"No existe o no es accesible: {p}")
    build(a.library, a.thesis, a.anteproyecto_pdf)


if __name__ == "__main__":
    main()
