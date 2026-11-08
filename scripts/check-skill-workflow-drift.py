#!/usr/bin/env python3
"""check-skill-workflow-drift — detecta drift funcional entre skills y workflows.

Para cada par `agent-dist/workflows/quinotospec.<name>.md` +
`agent-dist/skills/quinotospec-<name>/SKILL.md`, compara las referencias a
scripts ejecutables (`*.py`, `*.sh`, `*.js`) que cada documento menciona.

Una skill es la superficie que carga el agente; si el workflow invoca un
script que la skill no menciona, la skill perdió una capacidad real. Ese caso
es ERROR. La inversa (skill menciona algo que el workflow no) es WARNING.

Uso:
    check-skill-workflow-drift.py --root .
    check-skill-workflow-drift.py --root . --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPT_RE = re.compile(r"[\w][\w./-]*\.(?:py|sh|js)\b")

# Pares con diferencia intencional documentada: script -> razón.
ALLOWLIST = {
    # (workflow_name, script_basename): "razon"
}


def script_refs(text):
    return {Path(m.group(0)).name for m in SCRIPT_RE.finditer(text)}


def paired_files(root):
    workflows_dir = root / "agent-dist" / "workflows"
    skills_dir = root / "agent-dist" / "skills"
    if not workflows_dir.is_dir() or not skills_dir.is_dir():
        return []

    pairs = []
    for wf in sorted(workflows_dir.glob("quinotospec.*.md")):
        name = wf.name[len("quinotospec."):-len(".md")]
        skill = skills_dir / ("quinotospec-" + name.replace(".", "-")) / "SKILL.md"
        if skill.is_file():
            pairs.append((name, wf, skill))
    return pairs


def check(root):
    report = {"schema_version": 1, "pairs": [], "errors": 0, "warnings": 0}
    for name, wf, skill in paired_files(root):
        wf_refs = script_refs(wf.read_text(encoding="utf-8", errors="replace"))
        sk_refs = script_refs(skill.read_text(encoding="utf-8", errors="replace"))
        missing_in_skill = sorted(
            ref for ref in wf_refs - sk_refs if (name, ref) not in ALLOWLIST
        )
        missing_in_workflow = sorted(sk_refs - wf_refs)
        entry = {
            "pair": name,
            "workflow": str(wf.relative_to(root)),
            "skill": str(skill.relative_to(root)),
            "missing_in_skill": missing_in_skill,
            "missing_in_workflow": missing_in_workflow,
        }
        report["pairs"].append(entry)
        report["errors"] += len(missing_in_skill)
        report["warnings"] += len(missing_in_workflow)
    return report


def render(report):
    lines = ["Skill <-> Workflow Drift", ""]
    clean = True
    for entry in report["pairs"]:
        if entry["missing_in_skill"]:
            clean = False
            lines.append("ERROR %s: la skill no menciona %s" % (
                entry["pair"], ", ".join(entry["missing_in_skill"])
            ))
        if entry["missing_in_workflow"]:
            clean = False
            lines.append("WARN  %s: el workflow no menciona %s" % (
                entry["pair"], ", ".join(entry["missing_in_workflow"])
            ))
    if clean:
        lines.append("OK: %d pares skill<->workflow sin drift funcional" % len(report["pairs"]))
    lines.append("")
    lines.append("Pares analizados: %d | Errores: %d | Warnings: %d" % (
        len(report["pairs"]), report["errors"], report["warnings"]
    ))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Detecta drift funcional entre skills y workflows")
    parser.add_argument("--root", default=".", help="Raiz del paquete QuinotoSpec")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Falla tambien con warnings")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    report = check(root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report))

    if report["errors"] > 0:
        return 1
    if args.warnings_as_errors and report["warnings"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
