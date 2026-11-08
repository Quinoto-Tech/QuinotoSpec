#!/usr/bin/env python3
"""Skald — paridad README + diccionario ES->EN para conceptos (sin LLM).

Uso:
    skald.py --check [--root PATH] [--json]
    skald.py --check-i18n [--root PATH] [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

# Diccionario de conceptos clave ES->EN (verificacion de paridad, no traduccion completa)
GLOSSARY = {
    "propuestas": "proposals",
    "tareas": "tasks",
    "changelog": "changelog",
    "constitución": "constitution",
    "descubrimiento": "discovery",
    "trabajo": "workflow",
    "habilidad": "skill",
    "reglas": "rules",
    "agentes": "agents",
    "plantillas": "templates",
    "historia": "story",
    "especificación": "spec",
    "evidencia": "evidence",
}

REQUIRED_TABLES = ["workflows", "skills", "rules", "agents", "templates"]


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def main(argv=None):
    parser = argparse.ArgumentParser(description="Skald — paridad docs ES/EN")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-i18n", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root)
    readme_es = read(root / "README.md")
    readme_en = read(root / "README_EN.md")
    missing = []
    for key in REQUIRED_TABLES:
        if not readme_es.lower().find(key) >= 0 or not readme_en.lower().find(key) >= 0:
            missing.append(key)
    i18n_report = {"glossary": GLOSSARY, "missing_tables": missing, "ok": not missing}
    if args.check_i18n or args.check:
        if args.json:
            print(json.dumps(i18n_report, ensure_ascii=False, indent=2))
        else:
            print("Skald i18n: %s (%d entradas)" % ("OK" if i18n_report["ok"] else "DRIFT", len(GLOSSARY)))
            if missing:
                print("  faltan tablas: %s" % ", ".join(missing))
        return 0 if i18n_report["ok"] else 1
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
