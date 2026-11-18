#!/usr/bin/env python3
"""generate-command-stubs — genera/verifica los comandos delegados a skills.

Cada `agent-dist/workflows/quinotospec.<name>.md` se convierte en un stub
que indica al agente leer la skill `SKILL.md` pareada por ruta de archivo
(repo fuente → instalación local → instalación global) y aplicarla con
`$ARGUMENTS`. La skill es la única fuente del prompt.

Uso:
    python3 -B scripts/generate-command-stubs.py --root . --check
    python3 -B scripts/generate-command-stubs.py --root . --write
    python3 -B scripts/generate-command-stubs.py --root . --render status
"""

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

# Par en conflicto con PWRE-9f2c (En Curso): se migra al cierre de esa propuesta
# o se registra deuda. No se genera stub para él hasta entonces (TSK-008).
EXCLUDED = {"review"}

BODY = """# Command: {name}

Lee la skill `{skill_id}` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/{skill_id}/SKILL.md` (repo fuente), `.opencode/skills/{skill_id}/SKILL.md`, `.cursor/skills/{skill_id}/SKILL.md`, `.claude/skills/{skill_id}/SKILL.md`, `.agent/skills/{skill_id}/SKILL.md` (instalación local), `~/.config/opencode/skills/{skill_id}/SKILL.md`, `~/.cursor/skills/{skill_id}/SKILL.md`, `~/.claude/skills/{skill_id}/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
"""


def workflow_name(path):
    return path.name[len("quinotospec."):-len(".md")]


def skill_id(name):
    return "quinotospec-" + name.replace(".", "-")


def frontmatter(text):
    match = re.match(r"\A(---\n.*?\n---\n)", text, re.DOTALL)
    return match.group(1) if match else "---\ndescription: Comando QuinotoSpec\n---\n"


def render(root, name):
    wf = root / "agent-dist/workflows" / ("quinotospec." + name + ".md")
    header = frontmatter(wf.read_text(encoding="utf-8")) if wf.is_file() else "---\ndescription: Comando QuinotoSpec\n---\n"
    return header + "\n" + BODY.format(skill_id=skill_id(name), name=name)


def pairs(root):
    for wf in sorted((root / "agent-dist/workflows").glob("quinotospec.*.md")):
        name = workflow_name(wf)
        skill = root / "agent-dist/skills" / skill_id(name) / "SKILL.md"
        if skill.is_file():
            yield name, wf, skill


def main(argv=None):
    parser = argparse.ArgumentParser(description="Genera/verifica stubs comando→skill")
    parser.add_argument("--root", default=".")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="verifica que los comandos sean los stubs esperados")
    action.add_argument("--write", action="store_true", help="escribe los stubs en agent-dist/workflows")
    action.add_argument("--render", metavar="NAME", help="imprime el stub de un comando por stdout")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.render:
        sys.stdout.write(render(root, args.render))
        return 0

    generated = 0
    mismatches = []
    for name, wf, _skill in pairs(root):
        if name in EXCLUDED:
            continue
        expected = render(root, name)
        generated += 1
        if args.write:
            wf.write_text(expected, encoding="utf-8")
        elif not wf.is_file() or wf.read_text(encoding="utf-8") != expected:
            mismatches.append(name)

    if args.check:
        if mismatches:
            print("ERROR: stubs desviados: " + ", ".join(mismatches), file=sys.stderr)
            return 1
        print("OK: %d comandos son el stub canónico (excluidos: %s)" % (generated, ", ".join(sorted(EXCLUDED))))
    else:
        print("OK: %d stubs escritos (excluidos: %s)" % (generated, ", ".join(sorted(EXCLUDED))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
