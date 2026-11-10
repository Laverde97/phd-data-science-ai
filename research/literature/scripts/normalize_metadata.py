#!/usr/bin/env python3
"""Verify titles/DOIs of the catalog against official sources (stdlib only).

* DOI ``10.48550/*`` (arXiv)  -> DataCite REST API
* any other DOI               -> Crossref REST API
* PMLR / OpenReview pages     -> the official page/API title
* anything else               -> left as «pendiente de verificación»

Title policy (the published title is never abbreviated or translated):
* If the official title equals the inventory title after removing case,
  accents and punctuation, the official spelling is adopted.
* If they differ in substance, the inventory title is kept and the record is
  flagged in ``reports/metadata_verification.md`` for manual review.

Network failures never invalidate a record: they are reported as such.
Responses are cached in ``_local/literature/`` (gitignored).

    python3 research/literature/scripts/normalize_metadata.py [--offline]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_common import LOCAL_DIR, REPORTS_DIR, normalize_title, read_catalog, write_catalog  # noqa: E402

UA = "phd-literature-catalog/1.0 (metadata verification; stdlib urllib)"
CACHE = LOCAL_DIR / "metadata_cache.json"


def fetch(url: str, cache: dict, accept: str = "application/json") -> tuple[int, str]:
    if url in cache:
        return cache[url]["status"], cache[url]["body"]
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, body = r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, body = e.code, ""
    except Exception as e:  # network problem: do not cache
        return -1, str(e)
    cache[url] = {"status": status, "body": body}
    time.sleep(0.15)
    return status, body


def clean(t: str) -> str:
    t = html.unescape(re.sub(r"<[^>]+>", "", t or ""))
    return re.sub(r"\s+", " ", t).strip()


# Sources that cannot be queried through an API. Each value was checked by hand
# on the official page/document (see reports/metadata_verification.md).
MANUAL_OFFICIAL = {
    "lit-f4-06": ("The effective rank: A measure of effective dimensionality",
                  "PDF oficial de EURASIP (EUSIPCO 2007; el título se imprime en mayúsculas)"),
    "lit-l07": ("Interpretable Machine Learning: A Guide for Making Black Box Models Explainable",
                "sitio oficial del libro (3.ª edición)"),
}
# Alternative DOI that identifies the same work when the official page blocks automated access.
ALT_DOI = {
    "lit-f4-03": "10.48550/arxiv.2105.04906",  # VICReg, arXiv record «Accepted at ICLR 2022»
}


def official_title(row: dict, cache: dict) -> tuple[str, str, str]:
    """Return (title, source, error)."""
    if row["article_id"] in MANUAL_OFFICIAL:
        t, src = MANUAL_OFFICIAL[row["article_id"]]
        return t, src, ""
    doi = row["doi"] or ALT_DOI.get(row["article_id"], "")
    if doi.startswith("10.48550/"):
        st, body = fetch(f"https://api.datacite.org/dois/{urllib.parse.quote(doi)}", cache)
        if st == 200:
            titles = json.loads(body)["data"]["attributes"].get("titles") or []
            return clean(titles[0]["title"]) if titles else "", "DataCite", ""
        return "", "DataCite", f"HTTP {st}"
    if doi:
        st, body = fetch(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}", cache)
        if st == 200:
            msg = json.loads(body)["message"]
            title = clean((msg.get("title") or [""])[0])
            sub = clean((msg.get("subtitle") or [""])[0]) if msg.get("subtitle") else ""
            if sub and normalize_title(sub) not in normalize_title(title):
                title = f"{title}: {sub[0].upper()}{sub[1:]}" if msg.get("type", "").startswith("book") else title
            return title, "Crossref", ""
        return "", "Crossref", f"HTTP {st}"
    url = row["original_url"]
    if "proceedings.mlr.press" in url:
        st, body = fetch(url, cache, accept="text/html")
        m = re.search(r'<meta name="citation_title" content="([^"]+)"', body)
        return (clean(m.group(1)) if m else ""), "PMLR", "" if st == 200 else f"HTTP {st}"
    if "openreview.net/forum?id=" in url:
        fid = url.split("id=")[1]
        st, body = fetch(f"https://api2.openreview.net/notes?id={fid}", cache)
        if st == 200:
            notes = json.loads(body).get("notes") or []
            if notes:
                t = notes[0]["content"].get("title")
                return clean(t["value"] if isinstance(t, dict) else t), "OpenReview", ""
        st, body = fetch(f"https://api.openreview.net/notes?id={fid}", cache)
        if st == 200:
            notes = json.loads(body).get("notes") or []
            if notes:
                return clean(notes[0]["content"].get("title", "")), "OpenReview", ""
        return "", "OpenReview", f"HTTP {st}"
    return "", "", "sin DOI ni fuente consultable automáticamente"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="solo usa la caché local")
    args = ap.parse_args()
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    rows = read_catalog()
    report = {"adopted": [], "same": [], "differs": [], "failed": [], "manual": []}
    for row in rows:
        if args.offline and row["doi"] and not any(row["doi"] in k for k in cache):
            report["failed"].append((row, "modo sin conexión"))
            continue
        title, source, err = official_title(row, cache)
        if not title:
            kind = "manual" if source == "" else "failed"
            report[kind].append((row, err or source))
            if "verificad" not in row["metadata_verification_status"].lower():
                row["metadata_verification_status"] = ("Pendiente de verificación automática; metadatos del inventario"
                                                       if kind == "failed" else row["metadata_verification_status"])
            continue
        inv = row["title_original"]
        if normalize_title(title) == normalize_title(inv):
            if title != inv:
                report["adopted"].append((row, inv, title))
                row["title_original"] = title
                note = f"Grafía oficial adoptada; el inventario registraba «{inv}»"
                if note not in row["notes"]:
                    row["notes"] = " | ".join(x for x in (row["notes"], note) if x)
            else:
                report["same"].append(row)
            row["metadata_verification_status"] = f"Título verificado en {source}"
        elif (ann := re.search(r"\s*\(([^)]*)\)\s*$", inv)) and \
                normalize_title(title).startswith(normalize_title(inv[:ann.start()])):
            # the inventory appended a cataloguing note, e.g. «(3rd ed.)», to the title
            report["adopted"].append((row, inv, title))
            row["title_original"] = title
            note = f"Anotación del inventario retirada del título: «{ann.group(1)}»"
            if note not in row["notes"]:
                row["notes"] = " | ".join(x for x in (row["notes"], note) if x)
            row["metadata_verification_status"] = f"Título verificado en {source}"
        else:
            report["differs"].append((row, inv, title, source))
            row["metadata_verification_status"] = f"Título difiere de {source}: revisar"
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    write_catalog(rows)

    md = ["# Verificación de metadatos", "",
          "Generado por `scripts/normalize_metadata.py` (Crossref, DataCite, PMLR y OpenReview). "
          "Un fallo de red no invalida un registro; solo deja la verificación pendiente.", "",
          "| Resultado | Registros |", "|---|---:|",
          f"| Título idéntico al oficial | {len(report['same'])} |",
          f"| Grafía oficial adoptada en esta ejecución (mayúsculas, guiones, puntuación o anotación del inventario) | {len(report['adopted'])} |",
          f"| Título sustancialmente distinto: revisión manual | {len(report['differs'])} |",
          f"| Fuente consultable pero sin respuesta (red o API) | {len(report['failed'])} |",
          f"| Sin DOI ni fuente consultable automáticamente | {len(report['manual'])} |", ""]
    changed = [r for r in rows if "Grafía oficial adoptada" in r["notes"] or "Anotación del inventario" in r["notes"]]
    if changed:
        md += ["## Títulos ajustados a la grafía oficial (acumulado)", "", "| ID | Título publicado | Nota |", "|---|---|---|"]
        md += [f"| `{r['article_id']}` | {r['title_original']} | {r['notes']} |" for r in changed]
        md.append("")
    if report["differs"]:
        md += ["## Títulos que requieren revisión manual", "", "| ID | Inventario (se conserva) | Fuente oficial |", "|---|---|---|"]
        md += [f"| `{r['article_id']}` | {a} | {b} ({s}) |" for r, a, b, s in report["differs"]]
        md.append("")
    if report["failed"] or report["manual"]:
        md += ["## Pendientes de verificación", "", "| ID | Motivo |", "|---|---|"]
        md += [f"| `{r['article_id']}` | {e} |" for r, e in report["failed"] + report["manual"]]
        md.append("")
    (REPORTS_DIR / "metadata_verification.md").write_text("\n".join(md), encoding="utf-8")
    print({k: len(v) for k, v in report.items()})


if __name__ == "__main__":
    main()
