#!/usr/bin/env python3
"""readers -- lectores read-only del estado .quinoto-spec/ para la UI.

Solo stdlib. Cada funcion devuelve estructuras JSON-serializables y no
modifica archivos.
"""

import json
import re
from datetime import date, datetime
from pathlib import Path

FIELD_RE = re.compile(r"^[\s>\-*]*\*\*(?P<key>[^*]+?)\*\*:?\s*(?P<value>.*)$", re.M)
TASK_HEADING_RE = re.compile(r"^##\s+(TSK-[A-Za-z0-9-]+)\s*[—-]\s*(.+)$", re.M)
STORY_ROW_RE = re.compile(r"^\|\s*(US-[A-Za-z0-9-]+)\s*\|", re.M)

STATUS_MAP = (
    ("🟡", "proposed"),
    ("🟢", "in_progress"),
    ("✅", "completed"),
    ("🔴", "archived"),
    ("propuesta", "proposed"),
    ("proposed", "proposed"),
    ("en curso", "in_progress"),
    ("in_progress", "in_progress"),
    ("in progress", "in_progress"),
    ("completada", "completed"),
    ("completed", "completed"),
    ("archivada", "archived"),
    ("archived", "archived"),
    ("bloqueada", "blocked"),
    ("blocked", "blocked"),
    ("cancelada", "cancelled"),
    ("cancelled", "cancelled"),
    ("pendiente", "pending"),
    ("pending", "pending"),
    ("proposed", "proposed"),
)

TASK_STATUS_MAP = (
    ("[x]", "completed"),
    ("[X]", "completed"),
    ("[ ]", "pending"),
    ("completada", "completed"),
    ("completed", "completed"),
    ("en curso", "in_progress"),
    ("in_progress", "in_progress"),
    ("bloqueada", "blocked"),
    ("blocked", "blocked"),
    ("cancelada", "cancelled"),
    ("cancelled", "cancelled"),
    ("pendiente", "pending"),
    ("pending", "pending"),
    ("proposed", "pending"),
)


def _read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def normalize_status(raw):
    low = (raw or "").strip().lower()
    if not low:
        return "unknown"
    for token, value in STATUS_MAP:
        if token in low:
            return value
    return "unknown"


def normalize_task_status(raw):
    low = (raw or "").strip().lower()
    if not low:
        return "pending"
    for token, value in TASK_STATUS_MAP:
        if token.lower() in low:
            return value
    return "unknown"


def parse_fields(text):
    fields = {}
    for match in FIELD_RE.finditer(text):
        key = match.group("key").strip().rstrip(":").lower()
        value = match.group("value").strip()
        if key and key not in fields:
            fields[key] = value
    return fields


def first_heading(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _split_table_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_tasks_file(path):
    """Parsea tareas desde un archivo `*_tasks.md` (tabla o formato heading)."""
    text = _read(path)
    tasks = []
    lines = text.splitlines()
    header = None
    for index, line in enumerate(lines):
        if line.startswith("|") and "ID" in line and ("Estado" in line or "Status" in line):
            header = [cell.lower() for cell in _split_table_row(line)]
            break
    if header:
        id_idx = header.index("id") if "id" in header else 0

        def col(*names):
            for name in names:
                if name in header:
                    return header.index(name)
            return None

        title_idx = col("título", "titulo", "title")
        files_idx = col("archivos a modificar", "archivos", "files")
        deps_idx = col("dependencias", "deps", "dependencies")
        status_idx = col("estado", "status")
        story_idx = col("historia relacionada", "story", "historia")
        for line in lines[index + 1:]:
            if not line.strip().startswith("|"):
                if tasks:
                    break
                continue
            cells = _split_table_row(line)
            if len(cells) <= id_idx or not re.match(r"^TSK-", cells[id_idx]):
                continue
            tasks.append(
                {
                    "id": cells[id_idx],
                    "title": cells[title_idx] if title_idx is not None and title_idx < len(cells) else "",
                    "story": cells[story_idx] if story_idx is not None and story_idx < len(cells) else "",
                    "files": cells[files_idx] if files_idx is not None and files_idx < len(cells) else "",
                    "deps": cells[deps_idx] if deps_idx is not None and deps_idx < len(cells) else "",
                    "status": normalize_task_status(cells[status_idx]) if status_idx is not None and status_idx < len(cells) else "pending",
                    "source": path.name,
                }
            )
        return tasks

    # Formato heading: "## TSK-XXX — Titulo" + bullets "**Estado**: ..."
    matches = list(TASK_HEADING_RE.finditer(text))
    for pos, match in enumerate(matches):
        end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
        block = text[match.start():end]
        fields = parse_fields(block)
        tasks.append(
            {
                "id": match.group(1),
                "title": match.group(2).strip(),
                "story": fields.get("story", ""),
                "files": fields.get("archivos", fields.get("files", "")),
                "deps": fields.get("dependencias", fields.get("deps", "")),
                "status": normalize_task_status(fields.get("estado", fields.get("status", ""))),
                "source": path.name,
            }
        )
    return tasks


def read_evidence(root, task_id):
    directory = Path(root) / ".quinoto-spec" / "evidence" / task_id
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_file())


def read_stories(proposal_dir):
    text = _read(Path(proposal_dir) / "user-stories.md")
    stories = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _split_table_row(line)
        if cells and re.match(r"^US-", cells[0]):
            stories.append({"id": cells[0], "title": cells[1] if len(cells) > 1 else ""})
    return stories


def read_proposal(root, proposal_dir, archived=False):
    proposal_dir = Path(proposal_dir)
    text = _read(proposal_dir / "proposal.md")
    fields = parse_fields(text)
    tasks = []
    for tasks_file in sorted(proposal_dir.glob("*_tasks.md")):
        tasks.extend(read_tasks_file(tasks_file))
    for task in tasks:
        task["evidence"] = read_evidence(root, task["id"])
    stories = read_stories(proposal_dir)
    title = first_heading(text) or proposal_dir.name
    title = re.sub(r"^Propuesta T[eé]cnica:\s*", "", title)
    for task in tasks:
        task["evidence_count"] = len(task["evidence"])
    return {
        "slug": proposal_dir.name,
        "title": title,
        "prefix": fields.get("prefijo", ""),
        "date": fields.get("fecha de creación", fields.get("fecha de creacion", "")),
        "status": normalize_status(fields.get("estado", "")),
        "status_raw": fields.get("estado", ""),
        "priority": fields.get("prioridad", ""),
        "complexity": fields.get("complejidad", ""),
        "services": [s.strip() for s in fields.get("servicios afectados", "").split(",") if s.strip()],
        "archived": archived,
        "path": str(proposal_dir),
        "stories": stories,
        "tasks": tasks,
        "task_counts": _count_by_status(task["status"] for task in tasks),
        "has_delta_specs": (proposal_dir / "delta-specs").is_dir(),
    }


def _count_by_status(statuses):
    counts = {"pending": 0, "in_progress": 0, "completed": 0, "blocked": 0, "cancelled": 0, "unknown": 0}
    for status in statuses:
        counts[status] = counts.get(status, 0) + 1
    return counts


def read_proposals(root):
    root = Path(root)
    base = root / ".quinoto-spec" / "proposals"
    proposals = []
    if not base.is_dir():
        return proposals
    for directory in sorted(base.iterdir()):
        if not directory.is_dir() or directory.name.startswith("_"):
            continue
        if (directory / "proposal.md").is_file():
            proposals.append(read_proposal(root, directory))
    archived_base = base / "_archived"
    if archived_base.is_dir():
        for directory in sorted(archived_base.iterdir()):
            if directory.is_dir() and (directory / "proposal.md").is_file():
                proposals.append(read_proposal(root, directory, archived=True))
    return proposals


def read_changelog(root):
    root = Path(root)
    entries = []
    changelog_dir = root / ".quinoto-spec" / "changelog"
    if changelog_dir.is_dir():
        for path in sorted(changelog_dir.glob("*.md")):
            if path.name == "INDEX.md":
                continue
            text = _read(path)
            meta = {}
            for key in ("date", "prefix", "slug", "type"):
                match = re.search(r"^%s:\s*(.+)$" % key, text, re.M)
                if match:
                    meta[key] = match.group(1).strip()
            heading = re.search(r"^##\s+\[([^\]]+)\]\s*-\s*(.+)$", text, re.M)
            summary = []
            block = re.search(r"###\s+Resumen\s*\n(.*?)(?:\n\*\*|\n###|\Z)", text, re.S)
            if block:
                for line in block.group(1).splitlines():
                    if line.strip().startswith("- "):
                        summary.append(line.strip()[2:])
            time_saved = re.search(r"\*\*Tiempo Ahorrado\*\*:\s*(.+)", text)
            entries.append(
                {
                    "date": meta.get("date") or (heading.group(1) if heading else ""),
                    "title": heading.group(2).strip() if heading else path.stem,
                    "prefix": meta.get("prefix", ""),
                    "type": meta.get("type", "change"),
                    "summary": summary,
                    "time_saved": time_saved.group(1).strip() if time_saved else "",
                    "file": path.name,
                    "format": "v2",
                }
            )
    legacy = root / ".quinoto-spec" / "quinoto-spec-changelog.md"
    if legacy.is_file():
        text = _read(legacy)
        matches = list(re.finditer(r"^##\s+\[(?:Fecha:\s*)?([0-9-]+)\]\s*-\s*(.+)$", text, re.M))
        for pos, match in enumerate(matches):
            end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
            block = text[match.start():end]
            summary = [line.strip()[2:] for line in block.splitlines() if line.strip().startswith("- ")]
            entries.append(
                {
                    "date": match.group(1),
                    "title": match.group(2).strip(),
                    "prefix": "",
                    "type": "legacy",
                    "summary": summary[:5],
                    "time_saved": "",
                    "file": legacy.name,
                    "format": "v1",
                }
            )
    entries.sort(key=lambda item: (item["date"], item["file"]), reverse=True)
    return entries


def read_discovery_file(root, name):
    root = Path(root)
    directory = (root / ".quinoto-spec" / "discovery").resolve()
    target = (directory / name).resolve()
    if directory not in target.parents and target != directory:
        return {"name": name, "exists": False, "content": ""}
    if not target.is_file():
        return {"name": name, "exists": False, "content": ""}
    return {"name": name, "exists": True, "content": _read(target)}


def read_discovery(root):
    root = Path(root)
    directory = root / ".quinoto-spec" / "discovery"
    files = []
    project_date = ""
    age_days = None
    if directory.is_dir():
        for path in sorted(directory.glob("*.md")):
            text = _read(path)
            match = re.search(r"\*\*Discovery Date:\*\*\s*([0-9-]+)", text)
            file_date = match.group(1) if match else ""
            if path.name.startswith("01-") and file_date:
                project_date = file_date
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
            except OSError:
                mtime = ""
            files.append({"name": path.name, "date": file_date or mtime, "size": path.stat().st_size if path.exists() else 0})
    if project_date:
        try:
            age_days = (date.today() - date.fromisoformat(project_date)).days
        except ValueError:
            age_days = None
    return {
        "present": directory.is_dir(),
        "files": files,
        "project_date": project_date,
        "age_days": age_days,
        "stale": age_days is not None and age_days > 30,
    }


def read_constitution(root):
    root = Path(root)
    path = root / ".quinoto-spec" / "constitution.md"
    if not path.is_file():
        return {"present": False, "status": "", "content": "", "principles": []}
    text = _read(path)
    match = re.search(r"\*\*Estado:\*\*\s*(.+)", text)
    raw = match.group(1).strip() if match else ""
    status = "active" if raw.lower().startswith("active") else ("draft" if "draft" in raw.lower() else "unknown")
    principles = re.findall(r"\*\*([A-Z]{2,}-\d{2,})\*\*:\s*(.+)", text)
    return {
        "present": True,
        "status": status,
        "status_raw": raw,
        "content": text,
        "principles": [{"id": pid, "text": ptext} for pid, ptext in principles],
    }


def read_prefix_registry(root):
    root = Path(root)
    path = root / ".quinoto-spec" / "prefix-registry.md"
    entries = []
    if not path.is_file():
        return entries
    for line in _read(path).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _split_table_row(line)
        if not cells or cells[0].lower() in ("prefijo", "prefix") or set(cells[0]) <= set("-: "):
            continue
        entries.append({"prefix": cells[0], "name": cells[1] if len(cells) > 1 else "", "date": cells[2] if len(cells) > 2 else ""})
    return entries


def build_summary(root):
    root = Path(root)
    spec = root / ".quinoto-spec"
    proposals = read_proposals(root)
    tasks = [task for proposal in proposals for task in proposal["tasks"]]
    stories = [story for proposal in proposals for story in proposal["stories"]]
    discovery = read_discovery(root)
    constitution = read_constitution(root)
    changelog = read_changelog(root)
    total_tasks = _count_by_status(task["status"] for task in tasks)
    return {
        "root": str(root),
        "name": root.name,
        "initialized": spec.is_dir(),
        "discovery": discovery,
        "constitution": {"present": constitution["present"], "status": constitution["status"], "principles": len(constitution["principles"])},
        "proposals": proposals,
        "changelog": changelog,
        "prefixes": read_prefix_registry(root),
        "counts": {
            "proposals": len(proposals),
            "proposals_active": len([p for p in proposals if not p["archived"]]),
            "stories": len(stories),
            "tasks": len(tasks),
            "tasks_by_status": total_tasks,
            "changelog": len(changelog),
            "evidence": len([task for task in tasks if task["evidence_count"] > 0]),
        },
    }


def to_json(root):
    return json.dumps(build_summary(root), ensure_ascii=False, indent=2)


def build_multi_summary(roots):
    """Agrega el estado de varios roots (panel central multi-proyecto)."""
    roots = [Path(r) for r in roots]
    summaries = [build_summary(r) for r in roots]

    all_proposals = []
    for summary in summaries:
        for proposal in summary["proposals"]:
            tagged = dict(proposal)
            tagged["project"] = summary["name"]
            all_proposals.append(tagged)

    all_changelog = []
    for summary in summaries:
        for entry in summary["changelog"]:
            tagged = dict(entry)
            tagged["project"] = summary["name"]
            all_changelog.append(tagged)
    all_changelog.sort(key=lambda item: (item.get("date", ""), item.get("file", "")), reverse=True)

    all_tasks = [task for proposal in all_proposals for task in proposal["tasks"]]

    return {
        "multi": True,
        "root": str(roots[0]) if roots else "",
        "roots": [str(r) for r in roots],
        "name": "Multi-proyecto (%d)" % len(roots),
        "initialized": all(s["initialized"] for s in summaries),
        "projects": summaries,
        "selected_project": None,
        "discovery": summaries[0]["discovery"] if summaries else {"present": False, "files": [], "project_date": "", "age_days": None, "stale": False},
        "constitution": summaries[0]["constitution"] if summaries else {"present": False, "status": "", "principles": 0},
        "proposals": all_proposals,
        "changelog": all_changelog,
        "prefixes": [prefix for summary in summaries for prefix in summary["prefixes"]],
        "counts": {
            "proposals": len(all_proposals),
            "proposals_active": len([p for p in all_proposals if not p.get("archived")]),
            "stories": sum(s["counts"]["stories"] for s in summaries),
            "tasks": len(all_tasks),
            "tasks_by_status": _count_by_status(task["status"] for task in all_tasks),
            "changelog": len(all_changelog),
            "evidence": len([task for task in all_tasks if task.get("evidence_count", 0) > 0]),
            "projects": len(summaries),
        },
    }
