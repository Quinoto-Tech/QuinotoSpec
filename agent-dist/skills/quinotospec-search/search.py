#!/usr/bin/env python3
"""quinotospec-search -- busqueda filtrada sobre el indice BM25 de Mimir.

Delega el scoring en `quinotospec-mimir/search.py` (BM25) y agrega los filtros
que el indice no aplica por si solo: tipo, prefijo, fecha y estado.

Uso:
    python3 search.py --root . --query "login" [--type task] [--prefix AUTH] [--since 2026-01-01] [--status en-curso] [--limit 5] [--json] [--cite]

Solo stdlib. Offline.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from quinotospec_common import load_module_from_path, resolve_root  # noqa: E402

MIMIR_DIR = Path(__file__).resolve().parents[1] / "quinotospec-mimir"
INDEX_PY = MIMIR_DIR / "index.py"
SEARCH_PY = MIMIR_DIR / "search.py"

TYPE_PATTERNS = {
    "proposal": re.compile(r"proposals/[^/]+/proposal\.md$"),
    "task": re.compile(r"_tasks\.md$"),
    "story": re.compile(r"user-stories\.md$"),
    "discovery": re.compile(r"discovery/[^/]+\.md$"),
    "spec": re.compile(r"specs/[^/]+/spec\.md$"),
}

USAGE = (
    'Uso: search.py [--root PATH] --query "texto" [--type all|proposal|task|story|discovery|spec] '
    "[--prefix PREFIX] [--since YYYY-MM-DD] [--status ESTADO] [--limit N] [--json] [--cite]"
)


def parse_args(argv):
    options = {"query": "", "type": "all", "prefix": None, "since": None, "status": None, "limit": 10, "json": False, "cite": False}
    i = 0
    parts = []
    while i < len(argv):
        arg = argv[i]
        if arg in ("--query", "--type", "--prefix", "--since", "--status", "--limit"):
            i += 1
            if i >= len(argv):
                raise SystemExit("Falta valor para " + arg + "\n" + USAGE)
            value = argv[i]
            key = arg[2:]
            if key == "limit":
                options[key] = int(value)
            else:
                options[key] = value
        elif arg == "--json":
            options["json"] = True
        elif arg == "--cite":
            options["cite"] = True
        elif arg in ("-h", "--help"):
            print(USAGE)
            raise SystemExit(0)
        elif arg.startswith("--"):
            raise SystemExit("Flag desconocido: " + arg + "\n" + USAGE)
        else:
            parts.append(arg)
        i += 1
    if not options["query"]:
        options["query"] = " ".join(parts).strip()
    return options


def ensure_index(root):
    index_path = root / ".quinoto-spec" / "mimir" / "index.json"
    if index_path.exists():
        return
    completed = subprocess.run(
        [sys.executable, "-B", str(INDEX_PY), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not index_path.exists():
        print("Search: no se pudo construir el indice de Mimir.")
        if completed.stderr:
            print(completed.stderr.strip())
        raise SystemExit(1)


def chunk_status(root, chunk_file):
    path = root / chunk_file
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    match = re.search(r"\*\*Estado:?\*\*:?\s*(.+)", text)
    return match.group(1).strip().lower() if match else ""


def matches_type(chunk, wanted):
    if wanted == "all":
        return True
    pattern = TYPE_PATTERNS.get(wanted)
    return bool(pattern and pattern.search(chunk.get("file", "")))


def matches_filters(root, chunk, options):
    if not matches_type(chunk, options["type"]):
        return False
    if options["prefix"] and options["prefix"].lower() not in (chunk.get("prefix") or "").lower():
        return False
    if options["since"]:
        fecha = chunk.get("fecha") or ""
        if not fecha:
            name = Path(chunk.get("file", "")).name
            fecha = name[:10] if re.match(r"\d{4}-\d{2}-\d{2}", name) else ""
        if not fecha or fecha < options["since"]:
            return False
    if options["status"]:
        wanted = options["status"].lower().replace("-", " ")
        status = chunk_status(root, chunk.get("file", ""))
        if wanted not in status:
            return False
    return True


def main():
    argv = sys.argv[1:]
    root, rest = resolve_root(argv, ("QUINOTOSPEC_SEARCH_ROOT", "SEARCH_ROOT"))
    options = parse_args(rest)

    if not options["query"]:
        print(USAGE)
        return 2
    if options["type"] not in set(TYPE_PATTERNS) | {"all"}:
        print("Tipo invalido: %s (valores: all, %s)" % (options["type"], ", ".join(TYPE_PATTERNS)))
        return 2

    ensure_index(root)
    mimir_search = load_module_from_path(SEARCH_PY, "quinotospec_mimir_search")
    index_data = json.loads((root / ".quinoto-spec" / "mimir" / "index.json").read_text(encoding="utf-8"))
    chunks = index_data.get("chunks", [])

    # Scoring BM25 sobre todo el corpus; los filtros se aplican a los resultados.
    ranked = mimir_search.bm25_search(index_data, options["query"], limit=len(chunks) or 1)
    filtered = []
    for cid, score in ranked:
        chunk = chunks[cid]
        if matches_filters(root, chunk, options):
            filtered.append((chunk, score))
        if len(filtered) >= options["limit"]:
            break

    if options["json"]:
        payload = {
            "schema_version": 1,
            "query": options["query"],
            "filters": {k: options[k] for k in ("type", "prefix", "since", "status")},
            "count": len(filtered),
            "results": [
                {
                    "file": chunk.get("file"),
                    "line_start": chunk.get("line_start"),
                    "line_end": chunk.get("line_end"),
                    "prefix": chunk.get("prefix"),
                    "fecha": chunk.get("fecha"),
                    "score": round(score, 4),
                    "snippet": chunk.get("text", "").strip().splitlines()[:3],
                }
                for chunk, score in filtered
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not filtered:
        print('Sin resultados para "%s" con los filtros aplicados (reindex con index.py --full?)' % options["query"])
        return 0

    print('query: "%s"' % options["query"])
    for rank, (chunk, score) in enumerate(filtered, 1):
        loc = "%s:%s" % (chunk.get("file"), chunk.get("line_start"))
        if chunk.get("line_end") != chunk.get("line_start"):
            loc += "-%s" % chunk.get("line_end")
        meta = [m for m in (chunk.get("prefix"), chunk.get("fecha")) if m]
        suffix = " (%s)" % ", ".join(meta) if meta else ""
        print("%d. [score %.2f] %s%s" % (rank, score, loc, suffix))
        if options["cite"]:
            for line in chunk.get("text", "").splitlines()[:6]:
                print("   > " + line)
        else:
            first = next((ln for ln in chunk.get("text", "").splitlines() if ln.strip()), "")
            print("   " + first[:150])
    return 0


if __name__ == "__main__":
    sys.exit(main())
