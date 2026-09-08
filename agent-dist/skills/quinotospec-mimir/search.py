#!/usr/bin/env python3
"""Mimir -- busqueda BM25 con citas exactas sobre el indice generado por index.py.

Uso:
    python3 search.py [--root PATH] "texto de busqueda" [--cite] [--limit N]
    python3 search.py [--root PATH] --trace PREFIX
    python3 search.py [--root PATH] --check

Solo stdlib. Offline. Sin dependencias externas.
"""
import collections
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from index import resolve_root, discover_files, sha1_of, tokenize  # noqa: E402


def bm25_search(index_data, query, limit=5):
    chunks = index_data.get("chunks", [])
    inv = index_data.get("inverted_index", {})
    n = len(chunks)
    avgdl = index_data.get("avgdl") or 0
    if n == 0:
        return []
    qterms = tokenize(query)
    scores = collections.Counter()
    k1, b = 1.5, 0.75
    dl_cache = {}
    for term in qterms:
        ids = inv.get(term)
        if not ids:
            continue
        df = len(ids)
        idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
        for cid in ids:
            ch = chunks[cid]
            if cid not in dl_cache:
                dl_cache[cid] = tokenize(ch["text"])
            toks = dl_cache[cid]
            tf = toks.count(term)
            dl = len(toks)
            denom = tf + k1 * (1 - b + b * dl / avgdl) if avgdl else tf + k1
            scores[cid] += idf * (tf * (k1 + 1) / denom)
    return scores.most_common(limit)


def format_result(chunks, cid, score, cite):
    ch = chunks[cid]
    loc = f"{ch['file']}:{ch['line_start']}"
    if ch["line_end"] != ch["line_start"]:
        loc += f"-{ch['line_end']}"
    meta = [m for m in (ch.get("prefix"), ch.get("fecha")) if m]
    meta_s = f" ({', '.join(meta)})" if meta else ""
    out = [f"[score {score:.2f}] {loc}{meta_s}"]
    if cite:
        for line in ch["text"].splitlines()[:6]:
            out.append(f"   > {line}")
    else:
        first_line = next((ln for ln in ch["text"].splitlines() if ln.strip()), "")
        out.append(f"   {first_line[:150]}")
    return "\n".join(out)


def find_proposal_dir(root: Path, prefix: str):
    props = root / ".quinoto-spec" / "proposals"
    if not props.exists():
        return None, False
    for p in props.glob("**/proposal.md"):
        text = p.read_text(errors="ignore")
        if re.search(r'\*\*Prefijo:?\*\*:?\s*' + re.escape(prefix) + r'\b', text):
            return p.parent, "_archived" in p.parts
    return None, False


def trace(root: Path, prefix: str):
    prop_dir, archived = find_proposal_dir(root, prefix)
    if not prop_dir:
        print(f"Mimir --trace: no se encontro ninguna propuesta con prefijo {prefix}")
        return 1

    slug = prop_dir.name
    print(f"Linaje de {prefix} (slug: {slug}){' [ARCHIVADA]' if archived else ''}:")

    proposal_md = prop_dir / "proposal.md"
    text = proposal_md.read_text(errors="ignore")
    m = re.search(r'\*\*Fecha de Creaci[oó]n\*\*:?\s*([0-9-]+)', text)
    fecha = m.group(1) if m else "0000-00-00"

    steps = [(fecha, str(proposal_md.relative_to(root)), "proposal creado")]

    delta_dir = prop_dir / "delta-specs"
    domains = []
    if delta_dir.exists():
        for spec in sorted(delta_dir.glob("*/spec.md")):
            domains.append(spec.parent.name)
            steps.append((fecha, str(spec.relative_to(root)), f"delta-spec: {spec.parent.name}"))

    us = prop_dir / "user-stories.md"
    if us.exists():
        steps.append((fecha, str(us.relative_to(root)), "user stories generadas"))

    changelog_dir = root / ".quinoto-spec" / "changelog"
    if changelog_dir.exists():
        for entry in sorted(changelog_dir.glob("*.md")):
            etext = entry.read_text(errors="ignore")
            if prefix in etext or slug in etext:
                date_guess = entry.stem[:10] if re.match(r'\d{4}-\d{2}-\d{2}', entry.stem) else fecha
                steps.append((date_guess, str(entry.relative_to(root)), "changelog entry"))

    legacy = root / ".quinoto-spec" / "quinoto-spec-changelog.md"
    if legacy.exists():
        ltext = legacy.read_text(errors="ignore")
        if prefix in ltext or slug in ltext:
            steps.append((fecha, str(legacy.relative_to(root)), "changelog entry (v1, orden no garantizado)"))

    for domain in domains:
        spec_merged = root / ".quinoto-spec" / "specs" / domain / "spec.md"
        if spec_merged.exists():
            steps.append(("9999-99-99", str(spec_merged.relative_to(root)), f"merged en specs/{domain}"))

    if archived:
        steps.append(("9999-99-99", str(prop_dir.relative_to(root)), "archivada (proposals/**/_archived/)"))

    steps.sort(key=lambda s: s[0])
    for i, (fecha_s, path_s, desc) in enumerate(steps, 1):
        print(f"  {i}. [{fecha_s}] {path_s} — {desc}")
    return 0


def check(root: Path):
    sources_path = root / ".quinoto-spec" / "mimir" / "mimir-sources.json"
    if not sources_path.exists():
        print("Mimir --check: no hay indice previo. Corre index.py primero.")
        return 1
    try:
        old_hashes = json.loads(sources_path.read_text())
    except (json.JSONDecodeError, OSError):
        print("Mimir --check: mimir-sources.json corrupto. Corre index.py --full.")
        return 1

    current_files = discover_files(root)
    current_hashes = {}
    for f in current_files:
        h = sha1_of(f)
        if h:
            current_hashes[str(f.relative_to(root))] = h

    stale = [f for f in current_hashes if old_hashes.get(f) != current_hashes[f]]
    removed = [f for f in old_hashes if f not in current_hashes]

    if not stale and not removed:
        print(f"Mimir --check: indice actualizado ({len(current_hashes)} archivos).")
        return 0

    if stale:
        print(f"STALE: {len(stale)} archivo(s) cambiaron desde el ultimo index:")
        for f in stale:
            print(f"  - {f}")
    if removed:
        print(f"REMOVED: {len(removed)} archivo(s) ya no existen:")
        for f in removed:
            print(f"  - {f}")
    print("-> corre index.py para reindexar")
    return 1


def main():
    root, rest = resolve_root(sys.argv[1:])

    cite = False
    do_check = False
    trace_prefix = None
    limit = 5
    query_parts = []

    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--cite":
            cite = True
        elif a == "--check":
            do_check = True
        elif a == "--trace":
            i += 1
            trace_prefix = rest[i] if i < len(rest) else None
        elif a == "--limit":
            i += 1
            limit = int(rest[i]) if i < len(rest) else limit
        else:
            query_parts.append(a)
        i += 1

    if do_check:
        sys.exit(check(root))

    if trace_prefix:
        sys.exit(trace(root, trace_prefix))

    index_path = root / ".quinoto-spec" / "mimir" / "index.json"
    if not index_path.exists():
        print(f"Mimir: no hay indice en {index_path}.")
        print(f"Corre: python3 index.py --root {root}")
        sys.exit(1)

    query = " ".join(query_parts).strip()
    if not query:
        print('Mimir: falta query. Uso: search.py [--root PATH] "texto de busqueda" [--cite] [--limit N]')
        sys.exit(1)

    try:
        index_data = json.loads(index_path.read_text())
    except (json.JSONDecodeError, OSError):
        print(f"Mimir: indice corrupto en {index_path}. Corre index.py --full.")
        sys.exit(1)

    results = bm25_search(index_data, query, limit=limit)
    print(f'query: "{query}"')
    if not results or results[0][1] <= 1.0:
        print("No encontrado en indice (reindex?)")
        sys.exit(0)

    chunks = index_data["chunks"]
    for rank, (cid, score) in enumerate(results, 1):
        print(f"{rank}. {format_result(chunks, cid, score, cite)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
