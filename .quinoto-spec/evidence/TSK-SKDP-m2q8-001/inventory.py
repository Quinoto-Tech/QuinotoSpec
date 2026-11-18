#!/usr/bin/env python3
"""SKDP TSK-001: inventario de paridad workflow<->skill y evidencia pre-conversion."""
import difflib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
flows = root / "agent-dist/workflows"
skills = root / "agent-dist/skills"
script_re = re.compile(r"[\w][\w./-]*\.(?:py|sh|js)\b")
h2_re = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def body(text):
    return text.split("---", 2)[-1] if text.startswith("---") else text


def refs(text):
    return {Path(m.group(0)).name for m in script_re.finditer(text)}


def headings(text):
    return {m.group(1).strip() for m in h2_re.finditer(text)}


pairs = []
for wf in sorted(flows.glob("quinotospec.*.md")):
    name = wf.name[len("quinotospec."):-3]
    sk = skills / ("quinotospec-" + name.replace(".", "-")) / "SKILL.md"
    if not sk.is_file():
        pairs.append({"pair": name, "skill": None})
        continue
    a = body(wf.read_text(encoding="utf-8"))
    b = body(sk.read_text(encoding="utf-8"))
    only_h2 = sorted(headings(a) - headings(b))
    only_scripts = sorted(refs(a) - refs(b))
    pairs.append({
        "pair": name,
        "skill": str(sk.relative_to(root)),
        "similarity": round(difflib.SequenceMatcher(a=a.splitlines(), b=b.splitlines()).ratio(), 2),
        "workflow_only_h2": only_h2,
        "workflow_only_scripts": only_scripts,
        "needs_consolidation": bool(only_h2 or only_scripts),
    })

report = {
    "schema_version": 1,
    "task_id": "TSK-SKDP-m2q8-001",
    "pairs": pairs,
    "totals": {
        "pairs": len(pairs),
        "duplicates_similarity_ge_07": sum(1 for p in pairs if p.get("similarity", 0) >= 0.7),
        "needs_consolidation": sum(1 for p in pairs if p.get("needs_consolidation")),
    },
    "excluded": {"review": "PWRE-9f2c activa (En Curso) — TSK-008 la migra al cierre o registra deuda"},
}
print(json.dumps(report, ensure_ascii=False, indent=2))
