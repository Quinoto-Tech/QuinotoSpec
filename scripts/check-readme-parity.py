#!/usr/bin/env python3
"""check-readme-parity -- verifica que README.md y README_EN.md tengan la misma estructura.

Compara el numero de secciones H2, tablas y bloques de codigo. No traduce ni
compara prosa (eso sigue siendo trabajo humano); detecta drift estructural
(secciones que existen en un idioma y faltan en el otro).

Uso:
    check-readme-parity.py --root .
    check-readme-parity.py --root . --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def metrics(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "h2": len(re.findall(r"^## ", text, re.M)),
        "tables": len(re.findall(r"^\|[-: |]+\|\s*$", text, re.M)),
        "code_blocks": text.count("```") // 2,
        "images": len(re.findall(r"<img\s", text)),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compara la estructura de README.md y README_EN.md")
    parser.add_argument("--root", default=".", help="Raiz del paquete")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    docs = {"es": root / "README.md", "en": root / "README_EN.md"}
    missing = [str(p) for p in docs.values() if not p.is_file()]
    if missing:
        print("Faltan READMEs: " + ", ".join(missing))
        return 2

    values = {lang: metrics(path) for lang, path in docs.items()}
    diffs = {key: (values["es"][key], values["en"][key]) for key in values["es"] if values["es"][key] != values["en"][key]}

    report = {"schema_version": 1, "es": values["es"], "en": values["en"], "diffs": diffs}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("README parity (ES vs EN)")
        for key, (es, en) in diffs.items():
            print("  DRIFT %s: ES=%s EN=%s" % (key, es, en))
        if not diffs:
            print("  OK: estructura equivalente (%s)" % ", ".join("%s=%s" % (k, v) for k, v in values["es"].items()))

    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
