#!/usr/bin/env python3
"""Valkyrie -- triage y scoring de propuestas activas.

Uso:
    python3 rank.py [--root PATH] [--json] [--suggest-next]

score = 0.30*impact + 0.25*urgency + 0.20*risk_inverse + 0.15*debt_relief + 0.10*deps_ready
(cada componente normalizada a [0,1]; el score mostrado es score_norm * 100)

- impact: # servicios afectados + # user stories P1 (de user-stories.md)
- urgency: prioridad declarada (P1/P2/P3) + antiguedad de la propuesta (mas reciente = mas urgente)
- risk_inverse: 1 - DREAD_avg/10 si existe dread.json/heimdallr.json en la propuesta, sino 0.5
- debt_relief: 1.0 si la propuesta menciona 07-findings-and-recommendations o un hallazgo de tiwaz-rune
- deps_ready: 0.0 si hay un ciclo en schema.yaml (Kahn, misma logica que quinotospec-jormungandr/check.py), sino 1.0

Solo stdlib. Offline.
"""
import datetime
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path


def load_contract():
    path = Path(__file__).resolve().parents[1] / "quinotospec-contract" / "contract.py"
    spec = importlib.util.spec_from_file_location("quinotospec_contract_shared", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = load_contract()
PRIORITY_WEIGHT = {"P1": 1.0, "P2": 0.5, "P3": 0.0}


def resolve_root(argv):
    args = list(argv)
    root = None
    if "--root" in args:
        i = args.index("--root")
        if i + 1 < len(args):
            root = args[i + 1]
            del args[i:i + 2]
        else:
            del args[i:i + 1]
    if root is None:
        root = os.environ.get("QUINOTOSPEC_VALKYRIE_ROOT") or os.environ.get("VALKYRIE_ROOT")
    if root is None:
        root = "."
    return Path(root).resolve(), args


def _field(text, pattern, default=None):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else default


def parse_proposal(path: Path):
    text = path.read_text(errors="ignore")
    root = path.parents[3] if len(path.parents) >= 3 else path.parent
    try:
        parsed = CONTRACT.parse_proposal(path, root).to_dict()
    except (OSError, ValueError):
        parsed = {
            "prefix": "SIN-PREFIJO",
            "date": "",
            "status": "unknown",
            "priority": "P3",
            "complexity": "Media",
            "services": [],
        }
    conflictos_raw = _field(text, r'\*\*?⚠️?\s*Conflictos Detectados:?\*\*?:?\s*(.+)')
    tiene_conflicto = bool(conflictos_raw) and "ninguno" not in conflictos_raw.lower()
    debt_relief = bool(re.search(r'07-findings|findings-and-recommendations|tiwaz-rune|hallazgo', text, re.I))
    return {
        "prefix": parsed["prefix"] or "SIN-PREFIJO",
        "fecha": parsed["date"],
        "estado": parsed["status"],
        "prioridad": parsed["priority"] if parsed["priority"] in PRIORITY_WEIGHT else "P3",
        "complejidad": parsed["complexity"] or "Media",
        "servicios": parsed["services"],
        "tiene_conflicto": tiene_conflicto,
        "conflicto_detalle": conflictos_raw,
        "debt_relief": debt_relief,
    }


def count_us_p1(prop_dir: Path):
    us_file = prop_dir / "user-stories.md"
    if not us_file.exists():
        return 0, 0
    try:
        stories = CONTRACT.parse_stories(us_file, prop_dir.parents[2])
    except (OSError, ValueError):
        return 0, 0
    p1 = sum(1 for story in stories if story.priority == "P1")
    return p1, len(stories)


def read_dread(prop_dir: Path):
    for name in ("dread.json", "heimdallr.json"):
        f = prop_dir / name
        if f.exists():
            try:
                data = json.loads(f.read_text())
                avg = data.get("dread_avg")
                if avg is not None:
                    return float(avg)
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                continue
    return None


def find_changelog_last_date(root: Path, prefix: str, slug: str):
    try:
        entries, _ = CONTRACT.parse_changelog(root)
    except (OSError, ValueError):
        return None
    dates = []
    for entry in entries:
        if prefix in (entry.prefix, entry.title, entry.path) or slug in entry.path:
            dates.append(entry.date)
    return max(dates) if dates else None


def find_entropy_delta(root: Path, servicios):
    tiwaz_dir = root / ".quinoto-spec" / "tiwaz-rune"
    if not tiwaz_dir.exists() or not servicios:
        return None
    reports = []
    for f in tiwaz_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        sp = str(data.get("service_path", ""))
        if any(s and s in sp for s in servicios) and "s_final" in data:
            reports.append((f.name, data["s_final"]))
    if len(reports) < 2:
        return None
    reports.sort(key=lambda r: r[0])
    delta = reports[-1][1] - reports[-2][1]
    return delta


def detect_schema_cycle(root: Path):
    """Misma logica Kahn que quinotospec-jormungandr/check.py, con parser robusto
    para el estilo de lista YAML usado en schema-template.yaml (`requires:` en
    bloque, no inline `[a, b]`)."""
    schema = root / ".quinoto-spec" / "schema.yaml"
    if not schema.exists():
        return False, []
    text = schema.read_text(errors="ignore")

    ids = []
    requires = {}
    cur = None
    in_requires = False
    for line in text.splitlines():
        m_id = re.match(r'\s*-\s+id:\s*(\S+)', line)
        if m_id:
            cur = m_id.group(1)
            ids.append(cur)
            requires[cur] = []
            in_requires = False
            continue
        if cur is None:
            continue
        if re.match(r'\s*requires:\s*\[\s*\]\s*$', line):
            in_requires = False
            continue
        m_inline = re.match(r'\s*requires:\s*\[(.*?)\]', line)
        if m_inline:
            requires[cur] = [r.strip() for r in m_inline.group(1).split(",") if r.strip()]
            in_requires = False
            continue
        if re.match(r'\s*requires:\s*$', line):
            in_requires = True
            continue
        if in_requires:
            m_req = re.match(r'\s*-\s+(\S+)', line)
            if m_req:
                requires[cur].append(m_req.group(1))
                continue
            in_requires = False

    indeg = defaultdict(int)
    g = defaultdict(list)
    for nid in ids:
        for r in requires.get(nid, []):
            g[r].append(nid)
            indeg[nid] += 1
            indeg.setdefault(r, 0)
    q = deque([n for n in ids if indeg[n] == 0])
    visited = []
    while q:
        n = q.popleft()
        visited.append(n)
        for nb in g[n]:
            indeg[nb] -= 1
            if indeg[nb] == 0:
                q.append(nb)
    if len(visited) == len(ids):
        return False, []
    cycle = [n for n in ids if n not in visited]
    return True, cycle


def compute_urgency(prioridad, fecha_str, today):
    priority_component = PRIORITY_WEIGHT.get(prioridad, 0.0)
    recency_component = 0.0
    if fecha_str:
        try:
            fecha = datetime.date.fromisoformat(fecha_str)
            days = (today - fecha).days
            recency_component = max(0.0, 1.0 - days / 180.0)
        except ValueError:
            pass
    return 0.6 * priority_component + 0.4 * recency_component


def suggest_next_task(prop_dir: Path):
    completed = set()
    candidates = []
    for tasks_file in sorted(prop_dir.glob("*_tasks.md")):
        if tasks_file.name == "all_tasks.md":
            continue
        try:
            tasks = CONTRACT.parse_tasks(tasks_file, prop_dir.parents[2])
        except (OSError, ValueError):
            continue
        for task in tasks:
            if task.status == "completed":
                completed.add(task.canonical_id)
            elif task.status == "pending":
                candidates.append(task)
    for task in candidates:
        if all(dependency in completed for dependency in task.dependencies):
            return task.path, task.canonical_id
    return None, None


def main():
    root, rest = resolve_root(sys.argv[1:])
    as_json = "--json" in rest
    suggest = "--suggest-next" in rest

    proposals_dir = root / ".quinoto-spec" / "proposals"
    if not proposals_dir.exists():
        if as_json:
            print(json.dumps({"error": f"no existe {proposals_dir}"}))
        else:
            print(f"Valkyrie: no existe {proposals_dir}")
        sys.exit(1)

    cycle_detected, cycle_nodes = detect_schema_cycle(root)
    today = datetime.date.today()
    rows = []

    for proposal_md in sorted(proposals_dir.glob("*/proposal.md")):
        prop_dir = proposal_md.parent
        if "_archived" in prop_dir.parts:
            continue

        meta = parse_proposal(proposal_md)
        slug = prop_dir.name
        n_servicios = len(meta["servicios"]) or 1
        us_p1, us_total = count_us_p1(prop_dir)

        impact = min(1.0, n_servicios * 0.15 + us_p1 * 0.25)
        urgency = compute_urgency(meta["prioridad"], meta["fecha"], today)
        dread = read_dread(prop_dir)
        risk_inverse = 1.0 - (dread / 10.0) if dread is not None else 0.5
        debt_relief = 1.0 if meta["debt_relief"] else 0.0
        deps_ready = 0.0 if cycle_detected else 1.0

        score_norm = (0.30 * impact + 0.25 * urgency + 0.20 * risk_inverse
                      + 0.15 * debt_relief + 0.10 * deps_ready)
        score = round(score_norm * 100)

        last_activity = find_changelog_last_date(root, meta["prefix"], slug) or meta["fecha"]
        days_since = None
        if last_activity:
            try:
                days_since = (today - datetime.date.fromisoformat(last_activity)).days
            except ValueError:
                days_since = None
        is_stale = days_since is not None and days_since > 60

        if cycle_detected:
            next_action = f"blocked (ciclo: {' -> '.join(cycle_nodes)})"
        elif meta["tiene_conflicto"]:
            next_action = "conflict -> ver conflict-detector"
        elif is_stale:
            next_action = f"stale {days_since}d -> candidate archive"
        else:
            next_action = "ready -> suggest-next"

        delta_s = find_entropy_delta(root, meta["servicios"])

        rows.append({
            "slug": slug,
            "prop_dir": str(prop_dir),
            "prefix": meta["prefix"],
            "score": score,
            "n_servicios": n_servicios,
            "us_p1": us_p1,
            "us_total": us_total,
            "delta_s": round(delta_s, 2) if delta_s is not None else None,
            "conflicto": meta["conflicto_detalle"] if meta["tiene_conflicto"] else "none",
            "next_action": next_action,
            "prioridad": meta["prioridad"],
            "estado": meta["estado"],
            "days_since_activity": days_since,
            "components": {
                "impact": round(impact, 2),
                "urgency": round(urgency, 2),
                "risk_inverse": round(risk_inverse, 2),
                "debt_relief": debt_relief,
                "deps_ready": deps_ready,
            },
        })

    rows.sort(key=lambda r: r["score"], reverse=True)

    if as_json:
        print(json.dumps({
            "cycle_detected": cycle_detected,
            "cycle": cycle_nodes,
            "ranking": rows,
        }, indent=2, ensure_ascii=False))
        return

    if cycle_detected:
        first = cycle_nodes[0] if cycle_nodes else "?"
        print(f"⚠️  BLOCKING: ciclo detectado en schema.yaml: {' -> '.join(cycle_nodes)} -> {first}")
        print()

    print("# | Propuesta | Score | Impact | ΔS | Conflictos | Next Action")
    for i, r in enumerate(rows, 1):
        propuesta = f"{r['slug']} ({r['prefix']})"
        impact_s = f"{r['n_servicios']} svcs"
        delta_s = f"{r['delta_s']:+.2f}" if r["delta_s"] is not None else "-"
        print(f"{i} | {propuesta} | {r['score']} | {impact_s} | {delta_s} | {r['conflicto']} | {r['next_action']}")

    if suggest and rows and rows[0]["next_action"].startswith("ready"):
        tasks_file, line = suggest_next_task(Path(rows[0]["prop_dir"]))
        print()
        if tasks_file:
            print(f"--suggest-next: siguiente tarea pendiente en {tasks_file}:\n  {line}")
        else:
            print(f"--suggest-next: '{rows[0]['slug']}' no tiene archivos *_tasks.md todavia "
                  f"(siguiente artefacto: delta-specs/user-stories/tasks segun corresponda).")


if __name__ == "__main__":
    main()
