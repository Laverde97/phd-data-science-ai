#!/usr/bin/env python3
"""Genera un ZIP académico de CUB200 desde la raíz real del proyecto.

Uso:
    python preparar_entrega_CUB200.py
    python preparar_entrega_CUB200.py --include-data
    python preparar_entrega_CUB200.py --output /ruta/ENTREGA.zip

Por defecto NO incluye data/, .venv/, .venv-tf/, .git/ ni cachés. El
archivo conserva notebooks (con sus outputs), código, pruebas y artefactos.
"""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIRS = ("src", "scripts", "tests", "notebooks", "docs", "artifacts", "logs")
ROOT_PATTERNS = ("README*", "requirements*.txt", "pyproject.toml", "uv.lock", "setup.py", "setup.cfg", "pytest.ini", "LICENSE*", "CITATION.cff", "Makefile", ".gitignore", "environment.yml", "preparar_entrega_CUB200.py")
EXCLUDED_PARTS = {".git", ".venv", ".venv-tf", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", "__pycache__", "node_modules", ".DS_Store"}
EXCLUDED_GLOBS = ("*.pyc", "*.pyo", "*.swp", "*.tmp", "*.bak", "*.lock.tmp", "*.log~", ".env", ".env.*", "*.key", "*.pem", "id_rsa", "id_ed25519")


def eligible(rel: Path, include_data: bool) -> bool:
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if any(fnmatch.fnmatch(rel.name, g) for g in EXCLUDED_GLOBS):
        return False
    if rel.parts[0] in ROOT_DIRS or (include_data and rel.parts[0] == "data"):
        return True
    return len(rel.parts) == 1 and any(fnmatch.fnmatch(rel.name, pat) for pat in ROOT_PATTERNS)


def sha256_file(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            d.update(chunk)
    return d.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="Carpeta raíz del proyecto; por defecto la carpeta del script.")
    parser.add_argument("--output", type=Path, default=None, help="Ruta del ZIP que se generará.")
    parser.add_argument("--include-data", action="store_true", help="Incluye data/ completo; el ZIP puede superar 2 GB.")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not (root / "src" / "cub200").is_dir() or not (root / "notebooks").is_dir():
        parser.error(f"No es la raíz del proyecto CUB200: {root}")
    out = (args.output.expanduser() if args.output else root.parent / "ENTREGA_CUB200_TAREA01.zip").resolve()
    if out.is_dir():
        parser.error(f"La salida debe ser un archivo ZIP: {out}")
    if out == Path(__file__).resolve():
        parser.error("La salida no puede sobrescribir el script")
    out.parent.mkdir(parents=True, exist_ok=True)

    files = []
    for f in root.rglob("*"):
        if f.is_symlink() or not f.is_file() or f.resolve() == out:
            continue
        rel = f.relative_to(root)
        if eligible(rel, args.include_data):
            files.append((rel, f))
    files.sort(key=lambda x: x[0].as_posix())
    if not files:
        parser.error("No se seleccionaron archivos")
    nb = [r for r, _ in files if r.parts[0] == "notebooks" and r.suffix == ".ipynb"]
    if not nb:
        parser.error("No se encontró ningún notebook .ipynb")

    note = ("ENTREGA ACADÉMICA - CUB-200-2011 + captions\n"
            "Paquete generado desde el proyecto en WSL.\n\n"
            "Contiene código fuente, scripts, pruebas, notebooks con salidas,\n"
            "artefactos disponibles y documentación que existía en el proyecto.\n"
            f"Incluye fuentes de datos originales: {'SÍ' if args.include_data else 'NO'}\n\n"
            "Para ejecución completa se requieren los datos originales en data/,\n"
            "los entornos Python y la configuración compatible de GPU/CPU.\n"
            "Consulte el notebook y documentación para las fuentes de descarga.\n"
            "Las rutas absolutas locales no son transferibles: use ROOT dinámico.\n"
            "Los resultados guardados en notebooks no sustituyen ejecutar el pipeline.\n"
            "Una prueba pytest omitida debe documentarse con pytest -rs.\n")

    prefix = "CUB200_pipeline_profesional/"
    checksums = []
    print(f"Archivos seleccionados: {len(files):,}")
    print(f"Tamaño sin comprimir: {sum(f.stat().st_size for _, f in files) / (1024**2):.1f} MiB")
    print(f"Destino: {out}")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for k, (rel, f) in enumerate(files, 1):
            path = prefix + rel.as_posix()
            z.write(f, path)
            checksums.append((sha256_file(f), rel.as_posix()))
            if k % 1000 == 0:
                print(f"Incluidos {k:,}/{len(files):,} archivos...")
        z.writestr(prefix + "LEEME_ENTREGA.txt", note)
        z.writestr(prefix + "MANIFEST_SHA256.txt", "".join(f"{h}  {p}\n" for h, p in checksums))
    with zipfile.ZipFile(out, "r") as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"Archivo corrupto en el ZIP: {bad}")
    print(f"ZIP VERIFICADO: {out}\nTamaño ZIP: {out.stat().st_size/(1024**2):.1f} MiB")
    print("Nota: este ZIP no es una prueba de reproducción en otra máquina.")

if __name__ == "__main__":
    main()
