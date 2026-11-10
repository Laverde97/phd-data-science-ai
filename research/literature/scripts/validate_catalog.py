#!/usr/bin/env python3
"""Integrity checks for the literature catalog (stdlib only; runs in CI).

    python3 research/literature/scripts/validate_catalog.py           # offline checks
    python3 research/literature/scripts/validate_catalog.py --online  # + DOI / URL resolution

Exit code 0 = OK, 1 = errors. Network failures in ``--online`` mode are
reported as warnings, never as invalid URLs.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_common import (  # noqa: E402
    ANTEPROYECTO_ORDER_CSV, BLOCK_I, BLOCK_II, CATALOG_CSV, CATEGORY_LABELS, DATE_RE, DOI_RE, FIELDS, LF_PREFIX,
    LIT_DIR, STATUSES, normalize_doi, normalize_title, read_catalog,
)

CITATION_LIKE = re.compile(r"\bet al\.|^[\w\-’' ]+ \(\d{4}\)$|^[\w\-’' ]+,? \d{4}$")
SENSITIVE = [
    (re.compile(r"[A-Za-z]:\\\\?Users", re.I), "ruta de Windows"),
    (re.compile(r"/mnt/[a-z]/", re.I), "ruta WSL"),
    (re.compile(r"/home/[a-z0-9_-]+/", re.I), "ruta de usuario"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "correo electrónico"),
]


def check(online: bool) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    rows = read_catalog()
    if not rows:
        print("ERROR: catálogo vacío o inexistente:", CATALOG_CSV)
        return 1

    with CATALOG_CSV.open(encoding="utf-8", newline="") as fh:
        header = next(csv.reader(fh))
    if header != FIELDS:
        errors.append(f"Encabezado inesperado: {header}")

    ids = Counter(r["article_id"] for r in rows)
    errors += [f"article_id duplicado: {k}" for k, v in ids.items() if v > 1]
    dois = Counter(normalize_doi(r["doi"]) for r in rows if r["doi"])
    errors += [f"DOI duplicado: {k}" for k, v in dois.items() if v > 1]
    pmids = Counter(r["pmid"] for r in rows if r["pmid"])
    errors += [f"PMID duplicado: {k}" for k, v in pmids.items() if v > 1]
    titles = Counter(normalize_title(r["title_original"]) for r in rows)
    errors += [f"Título duplicado: {k[:60]}" for k, v in titles.items() if v > 1]

    orders = sorted(int(r["reading_order"]) for r in rows if r["reading_order"].isdigit())
    if orders != list(range(1, len(rows) + 1)):
        errors.append("reading_order debe ser consecutivo 1..N sin huecos ni repeticiones")
    ordered = sorted(rows, key=lambda r: int(r["reading_order"] or 0))
    blocks = [r["block"] for r in ordered]
    if blocks != sorted(blocks, key=lambda b: (b != BLOCK_I)):
        errors.append("El Bloque I (anteproyecto) debe preceder por completo al Bloque II")

    today = dt.date.today()
    for r in rows:
        rid = r["article_id"]
        t, es = r["title_original"].strip(), r["title_es"].strip()
        if not re.fullmatch(r"lit-[a-z0-9-]+", rid):
            errors.append(f"{rid}: article_id con formato no válido")
        if not t:
            errors.append(f"{rid}: falta el título original")
        elif CITATION_LIKE.search(t):
            errors.append(f"{rid}: el título original parece una cita abreviada («{t}»)")
        elif len(t.split()) < 3 and "título breve" not in r["notes"].lower():
            errors.append(f"{rid}: título original sospechosamente corto («{t}»)")
        if es and normalize_title(es) == normalize_title(t):
            errors.append(f"{rid}: la traducción repite el título original")
        if not es:
            warnings.append(f"{rid}: sin traducción al español")
        if r["block"] not in (BLOCK_I, BLOCK_II):
            errors.append(f"{rid}: bloque no válido «{r['block']}»")
        if (r["block"] == BLOCK_I) != (r["in_anteproyecto"] == "sí"):
            errors.append(f"{rid}: bloque e in_anteproyecto no coinciden")
        if r["primary_category"] not in CATEGORY_LABELS:
            errors.append(f"{rid}: categoría principal fuera de la taxonomía («{r['primary_category']}»)")
        if r["reading_status"] not in STATUSES:
            errors.append(f"{rid}: estado no permitido «{r['reading_status']}» (solo Pendiente/Realizado)")
        date = r["reading_date"].strip()
        if date:
            m = DATE_RE.match(date)
            try:
                d = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None
            except ValueError:
                d = None
            if not d:
                errors.append(f"{rid}: fecha de lectura no válida «{date}» (formato DD/MM/AAAA)")
            elif d > today:
                errors.append(f"{rid}: fecha de lectura en el futuro «{date}»")
            if r["reading_status"] != "Realizado":
                errors.append(f"{rid}: tiene fecha de lectura pero el estado no es Realizado")
        elif r["reading_status"] == "Realizado":
            errors.append(f"{rid}: estado Realizado sin fecha de lectura verificable")
        if r["doi"] and not DOI_RE.match(r["doi"]):
            errors.append(f"{rid}: DOI con formato no válido «{r['doi']}»")
        url = r["original_url"]
        if not url:
            warnings.append(f"{rid}: sin enlace original (se mostrará «No disponible»)")
        elif not url.startswith("https://"):
            errors.append(f"{rid}: el enlace original no es https «{url}»")
        lf = r["latent_frontiers_url"].strip()
        if lf and not (lf.startswith(LF_PREFIX) and len(lf) > len(LF_PREFIX)):
            errors.append(f"{rid}: el enlace de Latent Frontiers debe apuntar a una publicación ({LF_PREFIX}…)")
        if "verific" not in r["metadata_verification_status"].lower() and "inventario" not in r["metadata_verification_status"].lower():
            warnings.append(f"{rid}: estado de verificación de metadatos inesperado")
        if "pendiente de verificación" in r["metadata_verification_status"].lower():
            warnings.append(f"{rid}: metadatos pendientes de verificación automática")

    # Block I must follow the V4 «Referencias» order exactly
    with ANTEPROYECTO_ORDER_CSV.open(encoding="utf-8", newline="") as fh:
        order = list(csv.DictReader(fh))
    expected = [o["article_id"] for o in sorted(order, key=lambda o: int(o["ref_no"]))]
    got = [r["article_id"] for r in ordered if r["block"] == BLOCK_I]
    if expected != got:
        errors.append("El Bloque I no sigue exactamente el orden de la lista «Referencias» del anteproyecto V4")
    if "" in expected:
        errors.append("Hay referencias del anteproyecto sin registro asociado")

    # category totals == unique records
    cat_total = sum(Counter(r["primary_category"] for r in rows).values())
    if cat_total != len(rows):
        errors.append("La suma de categorías principales no coincide con el total de registros")

    # no sensitive strings or full texts in any published file of the section
    for p in LIT_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".pdf", ".docx", ".xlsx", ".txt", ".xml"}:
            errors.append(f"Archivo no permitido en la sección pública: {p.relative_to(LIT_DIR)}")
        if p.is_file() and p.suffix.lower() in {".csv", ".bib", ".md", ".qmd", ".json", ".css", ".js"}:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for rx, what in SENSITIVE:
                if rx.search(text):
                    errors.append(f"{p.relative_to(LIT_DIR)}: contiene {what}")

    if online:
        warnings += online_checks(rows)

    status = Counter(r["reading_status"] for r in rows)
    print(f"Registros: {len(rows)} · Bloque I: {sum(r['block']==BLOCK_I for r in rows)} · "
          f"Bloque II: {sum(r['block']==BLOCK_II for r in rows)} · Realizados: {status['Realizado']} · "
          f"Pendientes: {status['Pendiente']} · Con fecha: {sum(bool(r['reading_date']) for r in rows)} · "
          f"Latent Frontiers: {sum(bool(r['latent_frontiers_url']) for r in rows)} · "
          f"Con enlace original: {sum(bool(r['original_url']) for r in rows)}")
    for w in warnings:
        print("AVISO:", w)
    for e in errors:
        print("ERROR:", e)
    print("OK" if not errors else f"{len(errors)} error(es)")
    return 1 if errors else 0


def online_checks(rows: list[dict]) -> list[str]:
    out = []
    ua = {"User-Agent": "phd-literature-catalog/1.0 (link check)"}
    for r in rows:
        for label, url in (("original", r["original_url"]), ("Latent Frontiers", r["latent_frontiers_url"])):
            if not url:
                continue
            target = f"https://api.crossref.org/works/{r['doi']}" if label == "original" and r["doi"] and \
                not r["doi"].startswith("10.48550/") and url.startswith("https://doi.org/") else url
            req = urllib.request.Request(target, headers=ua, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    if resp.status >= 400:
                        out.append(f"{r['article_id']}: enlace {label} respondió {resp.status}")
            except urllib.error.HTTPError as e:
                if e.code in (401, 403, 429):
                    out.append(f"{r['article_id']}: enlace {label} no verificable automáticamente (HTTP {e.code})")
                else:
                    out.append(f"{r['article_id']}: enlace {label} respondió HTTP {e.code} — revisar")
            except Exception as e:  # network problem: not an invalid URL
                out.append(f"{r['article_id']}: no se pudo verificar el enlace {label} por un problema de red ({e.__class__.__name__})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--online", action="store_true")
    sys.exit(check(ap.parse_args().online))
