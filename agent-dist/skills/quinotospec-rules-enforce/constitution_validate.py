#!/usr/bin/env python3
"""Constitution gate — valida .quinoto-spec/constitution.md (archivo, no ejecucion).

Uso:
    python3 constitution_validate.py --root . --json
    python3 constitution_validate.py --root . --require --json

Retorna valid:false si no existe o si el estado no es 'active'.
No prueba que el codigo cumpla principios; solo presencia y estado.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
try:
    from quinotospec_common import resolve_root as _resolve_root  # type: ignore

    def resolve_root(p):
        return _resolve_root(["--root", str(p)])[0]
except Exception:  # pragma: no cover
    def resolve_root(p):
        return Path(p).resolve()


def main(argv=None):
    parser = argparse.ArgumentParser(description="QuinotoSpec Constitution gate (validator)")
    parser.add_argument("--root", default=".")
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(Path(args.root))
    path = root / ".quinoto-spec" / "constitution.md"
    if not path.is_file():
        result = {"schema_version": 1, "valid": False, "gate": "constitution", "error": "constitution.md not found"}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Constitution gate: MISSING")
        return 1 if args.require else 0

    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Estado:\*\*\s*(.+)", text)
    raw = m.group(1).strip() if m else ""
    status = "active" if raw.lower().startswith("active") else ("draft" if "draft" in raw.lower() else "unknown")
    principles = re.findall(r"\*\*([A-Z]{2,}-\d{2,}):?\*\*:?\s*(.+)", text)
    result = {"schema_version": 1, "valid": status == "active", "gate": "constitution", "status": status, "status_raw": raw, "principles": len(principles), "path": str(path)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Constitution gate: %s (%s, %d principios)" % ("OK" if result["valid"] else "INACTIVE", status, len(principles)))
    return 0 if result["valid"] or not args.require else 1


if __name__ == "__main__":
    sys.exit(main())
