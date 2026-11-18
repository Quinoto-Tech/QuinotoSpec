#!/usr/bin/env python3
"""check-skill-workflow-drift — valida la delegación comando → skill.

Tras SKDP-m2q8, la skill es la única fuente del prompt y el comando debe ser
el stub canónico generado por `scripts/generate-command-stubs.py`. El checker
verifica, para cada par:

1. el workflow es exactamente el stub esperado (sin prompt duplicado);
2. la skill pareada existe y no está vacía;
3. la skill conserva los headings H2 y las referencias a scripts que el
   workflow original tenía en HEAD (pre-conversión), para detectar pérdida
   de capacidad durante la consolidación.

Pares diferidos (conflicto PWRE-9f2c) se reportan como INFO, silenciosos para
el gate. Las skills sin workflow pareado siguen siendo válidas (INFO).

Uso:
    check-skill-workflow-drift.py --root .
    check-skill-workflow-drift.py --root . --json
    check-skill-workflow-drift.py --root . --warnings-as-errors
"""

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPT_RE = re.compile(r"[\w][\w./-]*\.(?:py|sh|js)\b")
H2_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)

# (pair, razón): convertido al cierre de PWRE-9f2c — ver
# .quinoto-spec/reviews/SKDP-m2q8-review-pair-debt.md
DEFERRED = {"review": "PWRE-9f2c En Curso — deuda registrada"}

ALLOWLIST = {}


def load_generator(root):
    path = root / "scripts/generate-command-stubs.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("generate_command_stubs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refs(text):
    return {Path(m.group(0)).name for m in SCRIPT_RE.finditer(text)}


def headings(text):
    return {m.group(1).strip() for m in H2_RE.finditer(text)}


def original_workflow(root, wf):
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:" + str(wf.relative_to(root))],
            capture_output=True, text=True, check=False,
        )
        return result.stdout if result.returncode == 0 else None
    except (OSError, ValueError):
        return None


def paired_files(root):
    for wf in sorted((root / "agent-dist/workflows").glob("quinotospec.*.md")):
        name = wf.name[len("quinotospec."):-len(".md")]
        yield name, wf


def check(root):
    generator = load_generator(root)
    report = {
        "schema_version": 1,
        "pairs": [],
        "errors": 0,
        "warnings": 0,
        "deferred": [],
    }
    for name, wf in paired_files(root):
        skill = root / "agent-dist/skills" / ("quinotospec-" + name.replace(".", "-")) / "SKILL.md"
        if not skill.is_file():
            report["errors"] += 1
            report["pairs"].append({"pair": name, "workflow": str(wf.relative_to(root)),
                                    "skill": None, "delegates": False,
                                    "missing_in_skill": ["SKILL.md"],
                                    "missing_in_workflow": [], "deferred": False})
            continue
        if name in DEFERRED:
            report["deferred"].append(name)
            continue
        expected = generator.render(root, name) if generator else None
        actual = wf.read_text(encoding="utf-8", errors="replace")
        delegates = bool(expected) and actual == expected
        skill_text = skill.read_text(encoding="utf-8", errors="replace")

        lost = []
        original = original_workflow(root, wf)
        if original and not delegates:
            # workflow aún sin convertir: no exigimos nada hasta la migración
            original = None
        if original:
            lost = sorted(headings(original) - headings(skill_text))
            lost += sorted(h for h in refs(original) - refs(skill_text) if h not in ALLOWLIST.get(name, {}))

        errors = []
        if not delegates:
            errors.append("workflow no es el stub canónico (prompt duplicado o desviado)")
        if not skill_text.strip():
            errors.append("SKILL.md vacío")
        errors.extend("contenido original perdido: " + item for item in lost)

        report["errors"] += len(errors)
        report["pairs"].append({
            "pair": name,
            "workflow": str(wf.relative_to(root)),
            "skill": str(skill.relative_to(root)),
            "delegates": delegates,
            "missing_in_skill": errors,
            "missing_in_workflow": [],
            "deferred": False,
        })
    return report


def render(report):
    lines = ["Skill <-> Workflow Drift (delegación comando → skill)", ""]
    clean = True
    for entry in report["pairs"]:
        for error in entry.get("missing_in_skill", []):
            clean = False
            lines.append("ERROR %s: %s" % (entry["pair"], error))
    if report["deferred"]:
        lines.append("INFO diferidos: " + ", ".join(report["deferred"]) + " (ver deuda registrada)")
    if clean:
        lines.append("OK: %d pares delegan correctamente" % len([p for p in report["pairs"] if p.get("delegates")]))
    lines.append("")
    lines.append("Pares analizados: %d | Errores: %d | Warnings: %d" % (
        len(report["pairs"]), report["errors"], report["warnings"]
    ))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Valida delegación skill<->workflow")
    parser.add_argument("--root", default=".", help="Raiz del paquete QuinotoSpec")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    parser.add_argument("--warnings-as-errors", action="store_true", help="Falla tambien con warnings")
    args = parser.parse_args(argv)

    report = check(Path(args.root).resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    if report["errors"] > 0:
        return 1
    if args.warnings_as_errors and report["warnings"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
