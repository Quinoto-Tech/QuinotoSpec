#!/usr/bin/env python3
"""Mimir -- indexador BM25 con citas exactas (file:line) sobre .quinoto-spec/.

Uso:
    python3 index.py [--root PATH] [--full]

Resuelve la raiz del proyecto (el directorio que CONTIENE .quinoto-spec/) en este
orden de precedencia: --root PATH > variable de entorno QUINOTOSPEC_MIMIR_ROOT >
MIMIR_ROOT > directorio actual. Esto permite indexar fixtures de test o cualquier
proyecto objetivo sin hardcodear una ruta.

Por defecto el reindexado es incremental: solo se re-chunkean los archivos cuyo
SHA1 cambio desde la ultima corrida (segun mimir-sources.json). Usa --full para
forzar un rebuild completo.

Solo stdlib. Offline. Sin dependencias externas.
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

HEADING_RE = re.compile(r'^#{1,6}\s+\S')
YAML_KEY_RE = re.compile(r'^[A-Za-z_][\w-]*:')

STOPWORDS = {
    # Espanol
    "de", "la", "el", "en", "y", "a", "que", "un", "una", "los", "las", "por",
    "con", "para", "es", "se", "del", "al", "su", "sus", "lo", "como", "mas",
    "pero", "o", "si", "no", "ya", "este", "esta", "estos", "estas",
    # English
    "the", "a", "an", "of", "in", "on", "and", "or", "to", "for", "is", "are",
    "was", "were", "be", "been", "this", "that", "these", "those", "with",
    "as", "by", "it", "its",
}

# NOTA: la fuente declarada en SKILL.md no menciona explicitamente delta-specs,
# pero el ejemplo de --cite del propio SKILL.md cita un archivo delta-specs/*.md.
# Se incluye aqui a proposito para que ese ejemplo sea reproducible.
SOURCE_GLOBS = [
    ".quinoto-spec/discovery/*.md",
    ".quinoto-spec/specs/**/*.md",
    ".quinoto-spec/proposals/**/proposal.md",
    ".quinoto-spec/proposals/**/user-stories.md",
    ".quinoto-spec/proposals/**/delta-specs/**/*.md",
    ".quinoto-spec/proposals/**/_archived/**/*.md",
    "docs/ARCHITECTURE.md",
    "CHANGELOG.md",
    ".quinoto-spec/schema.yaml",
]


def resolve_root(argv):
    """Extrae --root de argv si esta presente; devuelve (root_path, argv_restante)."""
    args = list(argv)
    root = None
    if "--root" in args:
        i = args.index("--root")
        if i + 1 < len(args):
            root = args[i + 1]
            del args[i:i + 2]
        else:
            del args[i:i + 1]
    if root is None:
        root = os.environ.get("QUINOTOSPEC_MIMIR_ROOT") or os.environ.get("MIMIR_ROOT")
    if root is None:
        root = "."
    return Path(root).resolve(), args


def discover_files(root: Path):
    seen = set()
    files = []
    for pattern in SOURCE_GLOBS:
        try:
            matches = root.glob(pattern)
        except (ValueError, OSError):
            continue
        for p in matches:
            if p.is_file() and p not in seen:
                seen.add(p)
                files.append(p)
    return sorted(files)


def sha1_of(path: Path) -> str:
    try:
        return hashlib.sha1(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def tokenize(text: str):
    return [t for t in re.split(r"\W+", text.lower()) if t and t not in STOPWORDS]


def extract_meta(text: str):
    prefix = None
    fecha = None
    m = re.search(r'\*\*Prefijo:?\*\*:?\s*([A-Za-z0-9_-]+)', text)
    if m:
        prefix = m.group(1)
    m = re.search(r'\*\*Fecha(?: de Creaci[oó]n)?\*\*:?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', text)
    if m:
        fecha = m.group(1)
    return prefix, fecha


def chunk_bounds(lines, is_yaml: bool):
    pattern = YAML_KEY_RE if is_yaml else HEADING_RE
    bounds = []
    start = 0
    for i, line in enumerate(lines):
        if i > start and pattern.match(line):
            bounds.append((start, i - 1))
            start = i
    bounds.append((start, len(lines) - 1))
    return bounds


def build_chunks_for_file(path: Path, root: Path):
    text = path.read_text(errors="ignore")
    if not text.strip():
        return []
    prefix, fecha = extract_meta(text)
    lines = text.splitlines()
    bounds = chunk_bounds(lines, is_yaml=path.suffix in (".yaml", ".yml"))
    rel = str(path.relative_to(root))
    chunks = []
    for (s, e) in bounds:
        body = "\n".join(lines[s:e + 1]).strip()
        if not body:
            continue
        chunks.append({
            "file": rel,
            "line_start": s + 1,
            "line_end": e + 1,
            "heading": lines[s].strip(),
            "text": body[:4000],
            "prefix": prefix,
            "fecha": fecha,
        })
    return chunks


def main():
    root, rest = resolve_root(sys.argv[1:])
    full = "--full" in rest

    spec_dir = root / ".quinoto-spec"
    mimir_dir = spec_dir / "mimir"
    mimir_dir.mkdir(parents=True, exist_ok=True)
    index_path = mimir_dir / "index.json"
    sources_path = mimir_dir / "mimir-sources.json"

    files = discover_files(root)
    if not files:
        print(f"Mimir: no se encontraron archivos fuente bajo {root} (¿existe .quinoto-spec/?)")

    new_hashes = {}
    for f in files:
        h = sha1_of(f)
        if h:
            new_hashes[str(f.relative_to(root))] = h

    old_hashes = {}
    old_chunks_by_file = {}
    if not full and sources_path.exists() and index_path.exists():
        try:
            old_hashes = json.loads(sources_path.read_text())
        except (json.JSONDecodeError, OSError):
            old_hashes = {}
        try:
            old_index = json.loads(index_path.read_text())
            for ch in old_index.get("chunks", []):
                old_chunks_by_file.setdefault(ch["file"], []).append(ch)
        except (json.JSONDecodeError, OSError):
            old_chunks_by_file = {}

    all_chunks = []
    changed = 0
    reused = 0
    for rel, sha in new_hashes.items():
        if not full and old_hashes.get(rel) == sha and rel in old_chunks_by_file:
            all_chunks.extend(old_chunks_by_file[rel])
            reused += 1
        else:
            all_chunks.extend(build_chunks_for_file(root / rel, root))
            changed += 1

    for idx, ch in enumerate(all_chunks):
        ch["id"] = idx

    inv = {}
    for ch in all_chunks:
        for t in set(tokenize(ch["text"])):
            inv.setdefault(t, []).append(ch["id"])

    total_tokens = sum(len(tokenize(ch["text"])) for ch in all_chunks)
    avgdl = (total_tokens / len(all_chunks)) if all_chunks else 0.0

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "root": str(root),
        "files_indexed": len(new_hashes),
        "chunk_count": len(all_chunks),
        "avgdl": avgdl,
        "chunks": all_chunks,
        "inverted_index": inv,
    }
    index_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    sources_path.write_text(json.dumps(new_hashes, indent=2, ensure_ascii=False, sort_keys=True))

    removed = len(set(old_hashes) - set(new_hashes)) if old_hashes else 0
    print(
        f"Mimir: {len(all_chunks)} chunks de {len(new_hashes)} archivos "
        f"({changed} nuevos/modificados, {reused} reusados, {removed} eliminados) -> {index_path}"
    )


if __name__ == "__main__":
    main()
