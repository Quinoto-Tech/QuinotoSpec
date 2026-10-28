#!/usr/bin/env python3
"""quinotospec-help — navegacion contextual global.

Inspecciona `.quinoto-spec/` desde cero y recomienda el siguiente comando
exacto. No escribe nada.

Uso:
    help.py [--root PATH] [--json] [--stale-days N]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

TASK_ID_RE = re.compile(r"(TSK-[A-Z0-9]+-[a-z0-9]{4}-\d{3}|TSK-[A-Z0-9-]+-\d{3})")
CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[([ xX])\]\s*(.*)$")
TABLE_CHECKBOX_RE = re.compile(r"\|\s*\[([ xX])\]\s*\|")
IN_PROGRESS_RE = re.compile(r"in[_ ]progress|en[_ ]progreso|🔄", re.IGNORECASE)


def newest_mtime(paths):
    newest = None
    for path in paths:
        try:
            stamp = path.stat().st_mtime
        except OSError:
            continue
        if newest is None or stamp > newest:
            newest = stamp
    return newest


def inspect_discovery(state_dir, stale_days):
    discovery = state_dir / "discovery"
    files = sorted(discovery.glob("*.md")) if discovery.is_dir() else []
    if not files:
        return {"present": False, "files": 0, "age_days": None, "stale": False}
    newest = newest_mtime(files)
    age_days = None
    if newest is not None:
        age_days = int((time.time() - newest) // 86400)
    return {
        "present": True,
        "files": len(files),
        "age_days": age_days,
        "stale": age_days is not None and age_days > stale_days,
    }


def parse_task_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    pending = []
    completed = 0
    in_progress = 0
    for line in text.splitlines():
        match = CHECKBOX_RE.match(line) or TABLE_CHECKBOX_RE.search(line)
        if not match:
            continue
        marker = match.group(1)
        id_match = TASK_ID_RE.search(line)
        if marker.lower() == "x":
            completed += 1
            continue
        if IN_PROGRESS_RE.search(line):
            in_progress += 1
        pending.append(id_match.group(1) if id_match else None)
    return {
        "completed": completed,
        "pending": len(pending),
        "in_progress": in_progress,
        "next_task": next((task for task in pending if task), None),
    }


def inspect_proposals(state_dir):
    proposals_dir = state_dir / "proposals"
    items = []
    archived = 0
    if not proposals_dir.is_dir():
        return {"active": 0, "archived": 0, "items": []}
    for entry in sorted(proposals_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("_") or entry.name.startswith("."):
            archived += 1
            continue
        has_proposal = (entry / "proposal.md").is_file()
        has_user_stories = (entry / "user-stories.md").is_file()
        task_files = sorted(entry.glob("*_tasks.md"))
        totals = {"completed": 0, "pending": 0, "in_progress": 0, "next_task": None}
        for task_file in task_files:
            parsed = parse_task_file(task_file)
            totals["completed"] += parsed["completed"]
            totals["pending"] += parsed["pending"]
            totals["in_progress"] += parsed["in_progress"]
            if totals["next_task"] is None:
                totals["next_task"] = parsed["next_task"]
        items.append(
            {
                "slug": entry.name,
                "has_proposal": has_proposal,
                "has_user_stories": has_user_stories,
                "task_files": [path.name for path in task_files],
                "tasks": totals,
            }
        )
    return {"active": len(items), "archived": archived, "items": items}


def build_report(root, stale_days):
    state_dir = root / ".quinoto-spec"
    initialized = state_dir.is_dir()
    discovery = inspect_discovery(state_dir, stale_days)
    proposals = inspect_proposals(state_dir) if initialized else {
        "active": 0,
        "archived": 0,
        "items": [],
    }
    constitution = (state_dir / "constitution.md").is_file()
    specs = (state_dir / "specs").is_dir()

    recommendations = []

    def recommend(command, reason, priority):
        recommendations.append(
            {"command": command, "reason": reason, "priority": priority}
        )

    if not initialized:
        recommend("/quinotospec.init", "No existe .quinoto-spec/ en la raiz del proyecto.", "high")
        recommend("/quinotospec.discovery", "Tras inicializar, documentar el stack y el contexto.", "medium")
    elif not discovery["present"]:
        recommend("/quinotospec.discovery", "No hay archivos de discovery del proyecto.", "high")
    elif discovery["stale"]:
        recommend(
            "/quinotospec.refresh-discovery",
            "El discovery tiene {} dias (umbral {}).".format(
                discovery["age_days"], stale_days
            ),
            "high",
        )

    if initialized and proposals["active"] == 0:
        recommend(
            "/quinotospec.create-proposal",
            "No hay propuestas activas: el siguiente paso es definir la solucion tecnica.",
            "high",
        )

    for item in proposals["items"]:
        slug = item["slug"]
        if not item["has_proposal"]:
            recommend(
                "/quinotospec.create-proposal {}".format(slug),
                "La propuesta {} no tiene proposal.md.".format(slug),
                "high",
            )
            continue
        if not item["has_user_stories"]:
            recommend(
                "/quinotospec.create-user-stories {}".format(slug),
                "La propuesta {} no tiene user-stories.md.".format(slug),
                "high",
            )
            continue
        if not item["task_files"]:
            recommend(
                "/quinotospec.create-tasks {}".format(slug),
                "La propuesta {} no tiene archivo de tareas.".format(slug),
                "high",
            )
            continue
        tasks = item["tasks"]
        if tasks["pending"] > 0:
            if tasks["next_task"]:
                recommend(
                    "/quinotospec.apply {}".format(tasks["next_task"]),
                    "Siguiente tarea pendiente de {} ({} pendientes, {} completadas).".format(
                        slug, tasks["pending"], tasks["completed"]
                    ),
                    "high",
                )
            else:
                recommend(
                    "/quinotospec.suggest-next {}".format(slug),
                    "Hay {} tareas pendientes sin ID canonico reconocible.".format(
                        tasks["pending"]
                    ),
                    "high",
                )
        elif tasks["completed"] > 0:
            recommend(
                "/quinotospec-mark-done {}".format(slug),
                "Todas las tareas de {} estan completadas.".format(slug),
                "high",
            )
            recommend(
                "/quinotospec.review-handoff {}".format(slug),
                "Generar la guia de code review para el revisor humano antes de archivar.",
                "medium",
            )
            recommend(
                "/quinotospec.archive {}".format(slug),
                "Tras el code review humano, archivar la propuesta y mergear delta specs.",
                "medium",
            )

    if not recommendations:
        recommend(
            "/quinotospec.status",
            "No hay acciones pendientes detectadas; revisar el dashboard del proyecto.",
            "low",
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda item: priority_order.get(item["priority"], 3))

    return {
        "schema_version": 1,
        "root": str(root),
        "initialized": initialized,
        "constitution": constitution,
        "specs": specs,
        "discovery": discovery,
        "proposals": proposals,
        "recommendations": recommendations,
        "next_command": recommendations[0]["command"] if recommendations else None,
    }


def render(report):
    lines = ["QuinotoSpec Help — estado del proyecto", ""]
    lines.append("Raiz: {}".format(report["root"]))
    lines.append(
        "Inicializado: {} | Constitucion: {} | Specs: {}".format(
            "si" if report["initialized"] else "no",
            "si" if report["constitution"] else "no",
            "si" if report["specs"] else "no",
        )
    )
    discovery = report["discovery"]
    if discovery["present"]:
        lines.append(
            "Discovery: {} archivos, {} dias ({})".format(
                discovery["files"],
                discovery["age_days"] if discovery["age_days"] is not None else "?",
                "OBSOLETO" if discovery["stale"] else "vigente",
            )
        )
    else:
        lines.append("Discovery: ausente")
    lines.append(
        "Propuestas: {} activas, {} archivadas".format(
            report["proposals"]["active"], report["proposals"]["archived"]
        )
    )
    for item in report["proposals"]["items"]:
        tasks = item["tasks"]
        lines.append(
            "  - {}: stories={} tasks={} pending={} completed={}".format(
                item["slug"],
                "si" if item["has_user_stories"] else "no",
                len(item["task_files"]),
                tasks["pending"],
                tasks["completed"],
            )
        )
    lines.append("")
    lines.append("Siguiente comando recomendado:")
    lines.append("  {}".format(report["next_command"]))
    lines.append("")
    lines.append("Recomendaciones:")
    for item in report["recommendations"]:
        lines.append("  [{}] {} — {}".format(item["priority"], item["command"], item["reason"]))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="quinotospec-help — recomendador contextual de workflows"
    )
    parser.add_argument("--root", default=".", help="Raiz del proyecto")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="Dias tras los cuales el discovery se considera obsoleto",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print("ERROR: root not found: " + str(root), file=sys.stderr)
        return 2

    report = build_report(root, args.stale_days)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
