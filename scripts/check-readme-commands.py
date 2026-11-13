#!/usr/bin/env python3
"""Verifica que los comandos citados en la documentacion existan de verdad.

`check-readme-parity.py` compara estructura (h2, tablas, code blocks) y
`check-links.sh` valida URLs relativas, pero ninguno detecta que el README
prometa `/quinotospec-foo` cuando la skill se renombro o nunca existio. Ese
hueco deja instrucciones muertas en la cara del usuario.

Reglas de resolucion:
  - `/quinotospec-<name>` o `@quinotospec-<name>`  -> agent-dist/skills/quinotospec-<name>/SKILL.md
  - `/quinotospec.<name>` o `@quinotospec.<name>`  -> agent-dist/workflows/quinotospec.<name>.md

Solo se consideran contextos de comando (code fences y spans inline), para no
confundir rutas de archivo ni URLs con comandos.

Uso:
  python3 scripts/check-readme-commands.py [--root .] [--include docs] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

WORKFLOW_PREFIX = "quinotospec."
SKILL_PREFIX = "quinotospec-"

INLINE_CODE = re.compile(r"`([^`\n]+)`")
COMMAND_START = re.compile(r"^(@|/)(quinotospec[.\-][A-Za-z0-9._\-]*)")


def iter_command_tokens(text: str):
    """Devuelve (linea, token) para comandos en code fences y spans inline."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue

        if in_fence:
            match = COMMAND_START.match(stripped)
            if match:
                yield number, match.group(1) + match.group(2)

        for span in INLINE_CODE.findall(line):
            span = span.strip()
            match = COMMAND_START.match(span)
            if match:
                yield number, match.group(1) + match.group(2)


def resolve(token: str, root: str):
    """Devuelve None si el comando existe, o el motivo del fallo."""
    body = token[1:]  # sin @ o /
    if body.startswith(SKILL_PREFIX):
        name = body[len(SKILL_PREFIX):]
        skill_file = os.path.join(root, "agent-dist", "skills", SKILL_PREFIX + name, "SKILL.md")
        if os.path.isfile(skill_file):
            return None
        # Un workflow tambien puede citarse en forma dash (p.ej. quick-dev).
        workflow_file = os.path.join(root, "agent-dist", "workflows", "quinotospec." + name + ".md")
        if os.path.isfile(workflow_file):
            return None
        return "no existe la skill agent-dist/skills/%s%s/SKILL.md" % (SKILL_PREFIX, name)

    if body.startswith(WORKFLOW_PREFIX):
        name = body[len(WORKFLOW_PREFIX):]
        workflow_file = os.path.join(root, "agent-dist", "workflows", "quinotospec." + name + ".md")
        if os.path.isfile(workflow_file):
            return None
        return "no existe el workflow agent-dist/workflows/quinotospec.%s.md" % name

    return "prefijo no reconocido: %s" % token


def check_file(path: str, root: str):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    seen = {}
    problems = []
    for number, token in iter_command_tokens(text):
        reason = resolve(token, root)
        if reason is None:
            continue
        problems.append({"file": os.path.relpath(path, root), "line": number, "command": token, "reason": reason})
        seen.setdefault(token, number)

    commands = {token for _, token in iter_command_tokens(text)}
    return commands, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="raiz del repo QuinotoSpec")
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        help="archivo markdown a revisar (default: README.md y README_EN.md)",
    )
    parser.add_argument("--include", action="append", default=[], help="directorio extra de markdown a revisar")
    parser.add_argument("--json", action="store_true", help="salida JSON")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    files = args.file or ["README.md", "README_EN.md"]

    for extra in args.include:
        directory = os.path.join(root, extra)
        for dirpath, _, filenames in os.walk(directory):
            for name in sorted(filenames):
                if name.endswith(".md"):
                    rel = os.path.relpath(os.path.join(dirpath, name), root)
                    if rel not in files:
                        files.append(rel)

    problems = []
    per_file = {}
    for rel in files:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            problems.append({"file": rel, "line": 0, "command": "", "reason": "archivo no encontrado"})
            continue
        commands, file_problems = check_file(path, root)
        per_file[rel] = len(commands)
        problems.extend(file_problems)

    if args.json:
        print(json.dumps({"schema_version": 1, "files": per_file, "problems": problems}, indent=2, ensure_ascii=False))
        return 1 if problems else 0

    print("README/documentation commands check")
    for rel, count in per_file.items():
        print("  %s: %d comandos citados" % (rel, count))

    if problems:
        print("")
        print("  Comandos citados que no existen:")
        for problem in problems:
            print("    %s:%d: %s — %s" % (problem["file"], problem["line"], problem["command"], problem["reason"]))
        print("")
        print("  DEAD COMMANDS: %d" % len(problems))
        return 1

    print("  OK: todos los comandos citados existen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
