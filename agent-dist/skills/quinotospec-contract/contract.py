#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

CONTRACT_VERSION = 1
PREFIX_PATTERN = re.compile(r"^([A-Za-z]{4})-([A-Za-z0-9]{4})$")
LEGACY_PREFIX_PATTERN = re.compile(r"^([A-Za-z]{3,4})-([A-Za-z0-9]{4})$")
CANONICAL_ID_PATTERN = re.compile(
    r"^(US|TSK)-([A-Za-z]{4})-(?:([A-Za-z0-9]{4})-)?(\d+)$",
    re.IGNORECASE,
)
SHORT_ID_PATTERN = re.compile(r"^(US|TSK)-([A-Za-z0-9]+)-(\d+)$", re.IGNORECASE)
LEGACY_ID_PATTERN = re.compile(r"^(US|TSK)-(\d+)$", re.IGNORECASE)


def key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "", normalized)


def clean_value(value: str) -> str:
    value = value or ""
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def metadata_from_lines(lines: Sequence[str], stop_at_heading: bool = True) -> Dict[str, str]:
    metadata: Dict[str, str] = {}
    for line in lines:
        if stop_at_heading and re.match(r"^##\s+", line):
            break
        candidate = re.sub(r"^\s*>\s?", "", line).strip()
        if not candidate or candidate.startswith("#") or candidate.startswith("|"):
            continue
        candidate = candidate.replace("**", "").replace("__", "")
        if ":" not in candidate:
            continue
        name, value = candidate.split(":", 1)
        name_key = key(name)
        if not name_key:
            continue
        metadata[name_key] = clean_value(value)
    return metadata


def meta_value(metadata: Dict[str, str], *names: str) -> str:
    for name in names:
        name_key = key(name)
        if name_key in metadata:
            return metadata[name_key]
    return ""


def split_list(value: str) -> List[str]:
    if not value:
        return []
    value = value.replace("•", ",").replace(";", ",")
    return [part.strip() for part in value.split(",") if part.strip()]


def normalize_status(value: str, default: str = "unknown") -> str:
    raw = (value or "").lower()
    normalized = key(value)
    if "[x]" in raw:
        return "completed"
    if "[ ]" in raw:
        return "pending"
    if "archiv" in normalized:
        return "archived"
    if any(token in normalized for token in ("complet", "done", "cerrad", "finaliz")):
        return "completed"
    if any(token in normalized for token in ("curso", "progreso", "progress", "wip")):
        return "in_progress"
    if any(token in normalized for token in ("propuesta", "planific", "planned", "draft", "todo")):
        return "proposed"
    if any(token in normalized for token in ("bloque", "block")):
        return "blocked"
    if any(token in normalized for token in ("cancel", "descart")):
        return "cancelled"
    if any(token in normalized for token in ("pend", "pending", "open")):
        return "pending"
    return default


def normalize_prefix(value: str) -> str:
    value = clean_value(value).strip("()[]{}.,;:")
    match = PREFIX_PATTERN.fullmatch(value) or LEGACY_PREFIX_PATTERN.fullmatch(value)
    if not match:
        return value
    return f"{match.group(1).upper()}-{match.group(2).lower()}"


@dataclass
class NormalizedId:
    raw: str
    canonical: str
    kind: str
    prefix: Optional[str]
    valid: bool
    source_format: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_id(raw_id: str, proposal_prefix: Optional[str] = None) -> NormalizedId:
    raw = clean_value(raw_id).strip("()[]{}.,;:")
    match = CANONICAL_ID_PATTERN.fullmatch(raw)
    if match:
        kind = match.group(1).upper()
        mnemonic = match.group(2).upper()
        suffix = match.group(3).lower() if match.group(3) else None
        number = match.group(4)
        prefix = f"{mnemonic}-{suffix}" if suffix else mnemonic
        normalized_legacy = False
        if suffix is None and proposal_prefix:
            candidate = normalize_prefix(proposal_prefix)
            if candidate.startswith(f"{mnemonic}-"):
                prefix = candidate
                suffix = candidate.split("-", 1)[1]
                normalized_legacy = True
        canonical = f"{kind}-{prefix}-{number}" if suffix else f"{kind}-{prefix}-{number}"
        return NormalizedId(
            raw=raw,
            canonical=canonical,
            kind=kind,
            prefix=prefix,
            valid=True,
            source_format="normalized-legacy" if normalized_legacy else ("canonical" if suffix else "legacy-short-id"),
        )
    match = SHORT_ID_PATTERN.fullmatch(raw)
    if match:
        kind = match.group(1).upper()
        mnemonic = match.group(2).upper()
        number = match.group(3)
        prefix = mnemonic
        if proposal_prefix:
            candidate = normalize_prefix(proposal_prefix)
            if candidate.startswith(f"{mnemonic}-"):
                prefix = candidate
                canonical = f"{kind}-{prefix}-{number}"
                return NormalizedId(raw, canonical, kind, prefix, True, "normalized-legacy")
        return NormalizedId(raw, raw, kind, prefix, True, "legacy-short-id")
    match = LEGACY_ID_PATTERN.fullmatch(raw)
    if match:
        kind = match.group(1).upper()
        number = match.group(2)
        return NormalizedId(raw, raw, kind, None, True, "legacy-id")
    return NormalizedId(raw, raw, "", None, False, "invalid")


@dataclass
class Diagnostic:
    severity: str
    code: str
    message: str
    path: str = ""
    line: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Proposal:
    path: str
    proposal_id: str
    prefix: str
    date: str
    status: str
    priority: str
    complexity: str
    services: List[str]
    source_format: str
    diagnostics: List[Diagnostic] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["diagnostics"] = [item.to_dict() for item in self.diagnostics]
        return result


@dataclass
class Story:
    path: str
    line: int
    raw_id: str
    canonical_id: str
    title: str
    description: str
    priority: str
    estimate: str
    service: str
    criteria: List[str]
    status: str
    diagnostics: List[Diagnostic] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["diagnostics"] = [item.to_dict() for item in self.diagnostics]
        return result


@dataclass
class Task:
    path: str
    line: int
    raw_id: str
    canonical_id: str
    title: str
    description: str
    story_raw_id: str
    story_id: str
    service: str
    files: List[str]
    estimate: str
    priority: str
    dependencies: List[str]
    status: str
    derived: bool = False
    diagnostics: List[Diagnostic] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["diagnostics"] = [item.to_dict() for item in self.diagnostics]
        return result


@dataclass
class ChangelogEntry:
    format: str
    date: str
    title: str
    summary: List[str]
    time_saved: str
    prefix: str
    slug: str
    path: str
    diagnostics: List[Diagnostic] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["diagnostics"] = [item.to_dict() for item in self.diagnostics]
        return result


def diagnostic(
    severity: str,
    code: str,
    message: str,
    path: Path,
    line: Optional[int] = None,
) -> Diagnostic:
    return Diagnostic(severity, code, message, str(path), line)


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_proposal(path: Path, root: Path) -> Proposal:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    metadata = metadata_from_lines(lines)
    proposal_id = meta_value(metadata, "id", "proposal id", "proposal")
    derived_id = path.parent.name
    prefix = normalize_prefix(meta_value(metadata, "prefix", "prefijo"))
    date = meta_value(metadata, "fecha de creacion", "fecha", "created")
    status = normalize_status(meta_value(metadata, "estado", "status"))
    priority = meta_value(metadata, "prioridad", "priority")
    complexity = meta_value(metadata, "complejidad", "complexity")
    services = split_list(meta_value(metadata, "servicios afectados", "services"))
    source_format = "canonical" if proposal_id and prefix and date else "legacy"
    diagnostics: List[Diagnostic] = []
    if not proposal_id:
        proposal_id = derived_id
        diagnostics.append(diagnostic("warning", "proposal.id.derived", "ID derivado de la carpeta", path, 1))
    if not prefix:
        diagnostics.append(diagnostic("error", "proposal.prefix.missing", "Falta el prefijo", path, 1))
    if not date:
        diagnostics.append(diagnostic("error", "proposal.date.missing", "Falta la fecha de creación", path, 1))
    if status == "unknown":
        diagnostics.append(diagnostic("error", "proposal.status.invalid", "Estado de propuesta no reconocido", path, 1))
    if "## Resumen Ejecutivo" not in text:
        diagnostics.append(diagnostic("warning", "proposal.summary.missing", "Falta la sección Resumen Ejecutivo", path))
    return Proposal(
        path=relative_path(path, root),
        proposal_id=proposal_id,
        prefix=prefix,
        date=date,
        status=status,
        priority=priority,
        complexity=complexity,
        services=services,
        source_format=source_format,
        diagnostics=diagnostics,
    )


def split_table_row(line: str) -> List[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: List[str] = []
    current: List[str] = []
    in_code = False
    for char in value:
        if char == "`":
            in_code = not in_code
            current.append(char)
        elif char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def is_separator_row(cells: Sequence[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def table_rows(text: str) -> List[Tuple[List[str], List[str], int]]:
    lines = text.splitlines()
    rows: List[Tuple[List[str], List[str], int]] = []
    index = 0
    while index < len(lines) - 1:
        if not lines[index].strip().startswith("|"):
            index += 1
            continue
        headers = split_table_row(lines[index])
        separator = split_table_row(lines[index + 1])
        if not is_separator_row(separator):
            index += 1
            continue
        row_index = index + 2
        while row_index < len(lines) and lines[row_index].strip().startswith("|"):
            cells = split_table_row(lines[row_index])
            if not is_separator_row(cells) and cells:
                rows.append((headers, cells, row_index + 1))
            row_index += 1
        index = row_index
    return rows


def column_value(headers: Sequence[str], cells: Sequence[str], *names: str) -> str:
    normalized_headers = [key(header) for header in headers]
    for name in names:
        name_key = key(name)
        for index, header in enumerate(normalized_headers):
            if header == name_key and index < len(cells):
                return clean_value(cells[index])
    return ""


def line_has_completion(line: str) -> Optional[str]:
    if re.search(r"\[[xX]\]", line):
        return "completed"
    if re.search(r"\[ \]", line):
        return "pending"
    return None


def parse_stories(path: Path, root: Path, proposal_prefix: Optional[str] = None) -> List[Story]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    stories: List[Story] = []
    found_table = False
    for headers, cells, line_number in table_rows(text):
        if key(headers[0] if headers else "") not in {"id", "userstoryid"} and "user story" not in " ".join(headers).lower():
            continue
        found_table = True
        raw_id = column_value(headers, cells, "id", "user story id")
        if not raw_id:
            continue
        normalized = normalize_id(raw_id, proposal_prefix)
        description = column_value(headers, cells, "user story", "story", "descripcion", "description")
        criteria = [line.strip() for line in re.split(r"\n|;", column_value(headers, cells, "criterios de aceptacion", "criterios", "acceptance criteria")) if line.strip()]
        status = normalize_status(column_value(headers, cells, "estado", "status"))
        diagnostics: List[Diagnostic] = []
        if not normalized.valid:
            diagnostics.append(diagnostic("error", "story.id.invalid", f"ID inválido: {raw_id}", path, line_number))
        if not description:
            diagnostics.append(diagnostic("error", "story.description.missing", "Falta la descripción de la story", path, line_number))
        stories.append(Story(
            path=relative_path(path, root),
            line=line_number,
            raw_id=raw_id,
            canonical_id=normalized.canonical,
            title=description,
            description=description,
            priority=column_value(headers, cells, "prioridad", "priority"),
            estimate=column_value(headers, cells, "estimacion", "estimate"),
            service=column_value(headers, cells, "servicio", "service"),
            criteria=criteria,
            status=status,
            diagnostics=diagnostics,
        ))
    if found_table:
        return stories
    block_story: Optional[str] = None
    block_title = ""
    block_lines: List[str] = []
    block_start = 0
    for index, line in enumerate(lines + [""]):
        match = re.match(r"^#{2,4}\s+(US-[A-Za-z0-9-]+)(?:\s*[-—:]\s*(.*))?$", line, re.IGNORECASE)
        if match:
            if block_story:
                stories.append(parse_story_block(path, root, block_story, block_title, block_lines, block_start, proposal_prefix))
            block_story = match.group(1)
            block_title = (match.group(2) or "").strip()
            block_lines = []
            block_start = index + 1
        elif block_story:
            block_lines.append(line)
    if block_story:
        stories.append(parse_story_block(path, root, block_story, block_title, block_lines, block_start, proposal_prefix))
    return stories


def parse_story_block(
    path: Path,
    root: Path,
    raw_id: str,
    title: str,
    lines: Sequence[str],
    line_number: int,
    proposal_prefix: Optional[str],
) -> Story:
    metadata = metadata_from_lines(lines, stop_at_heading=False)
    normalized = normalize_id(raw_id, proposal_prefix)
    description = meta_value(metadata, "descripcion", "description") or title
    criteria = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("- [x]") or stripped.startswith("- [X]"):
            criteria.append(stripped[6:].strip())
    status = normalize_status(meta_value(metadata, "estado", "status"))
    if status == "unknown":
        status = "completed" if all(not item.startswith("- [ ]") for item in lines) and criteria else "pending"
    return Story(
        path=relative_path(path, root),
        line=line_number,
        raw_id=raw_id,
        canonical_id=normalized.canonical,
        title=title,
        description=description,
        priority=meta_value(metadata, "prioridad", "priority"),
        estimate=meta_value(metadata, "estimacion", "estimate"),
        service=meta_value(metadata, "servicio", "service"),
        criteria=criteria,
        status=status,
        diagnostics=[diagnostic("warning", "story.block.legacy", "Story usa formato de bloques legacy", path, line_number)],
    )


def parse_tasks(
    path: Path,
    root: Path,
    proposal_prefix: Optional[str] = None,
    derived: bool = False,
) -> List[Task]:
    text = path.read_text(encoding="utf-8")
    tasks: List[Task] = []
    found_table = False
    for headers, cells, line_number in table_rows(text):
        if key(headers[0] if headers else "") not in {"id", "taskid"} and "task" not in " ".join(headers).lower():
            continue
        found_table = True
        raw_id = column_value(headers, cells, "id", "task id")
        if not raw_id:
            continue
        normalized = normalize_id(raw_id, proposal_prefix)
        row_text = " | ".join(cells)
        status = normalize_status(column_value(headers, cells, "estado", "status"))
        if status == "unknown":
            status = line_has_completion(row_text) or "pending"
        story_raw = column_value(headers, cells, "historia relacionada", "historia", "story", "user story")
        story_id = normalize_id(story_raw, proposal_prefix).canonical if story_raw else ""
        files = split_list(column_value(headers, cells, "archivos a modificar", "archivos", "files"))
        dependencies = [normalize_id(item, proposal_prefix).canonical for item in split_list(column_value(headers, cells, "dependencias", "dependencies")) if item.upper().startswith("TSK-")]
        tasks.append(Task(
            path=relative_path(path, root),
            line=line_number,
            raw_id=raw_id,
            canonical_id=normalized.canonical,
            title=column_value(headers, cells, "titulo", "title"),
            description=column_value(headers, cells, "descripcion", "description", "detalles"),
            story_raw_id=story_raw,
            story_id=story_id,
            service=column_value(headers, cells, "servicio", "service"),
            files=files,
            estimate=column_value(headers, cells, "estimacion", "estimate"),
            priority=column_value(headers, cells, "prioridad", "priority"),
            dependencies=dependencies,
            status=status,
            derived=derived,
            diagnostics=[diagnostic("error", "task.id.invalid", f"ID inválido: {raw_id}", path, line_number)] if not normalized.valid else [],
        ))
    if found_table:
        return tasks
    block_task: Optional[str] = None
    block_title = ""
    block_lines: List[str] = []
    block_start = 0
    for index, line in enumerate(text.splitlines() + [""]):
        match = re.match(r"^#{2,4}\s+(TSK-[A-Za-z0-9-]+)(?:\s*[-—:]\s*(.*))?$", line, re.IGNORECASE)
        if match:
            if block_task:
                tasks.append(parse_task_block(path, root, block_task, block_title, block_lines, block_start, proposal_prefix, derived))
            block_task = match.group(1)
            block_title = (match.group(2) or "").strip()
            block_lines = []
            block_start = index + 1
        elif block_task:
            block_lines.append(line)
    if block_task:
        tasks.append(parse_task_block(path, root, block_task, block_title, block_lines, block_start, proposal_prefix, derived))
    return tasks


def parse_task_block(
    path: Path,
    root: Path,
    raw_id: str,
    title: str,
    lines: Sequence[str],
    line_number: int,
    proposal_prefix: Optional[str],
    derived: bool,
) -> Task:
    metadata = metadata_from_lines(lines, stop_at_heading=False)
    normalized = normalize_id(raw_id, proposal_prefix)
    story_raw = meta_value(metadata, "story", "historia", "user story", "historia relacionada")
    story_id = normalize_id(story_raw, proposal_prefix).canonical if story_raw else ""
    status = normalize_status(meta_value(metadata, "estado", "status"))
    if status == "unknown":
        status = "completed" if any(re.search(r"\[[xX]\]", line) for line in lines) else "pending"
    return Task(
        path=relative_path(path, root),
        line=line_number,
        raw_id=raw_id,
        canonical_id=normalized.canonical,
        title=title or meta_value(metadata, "titulo", "title"),
        description=meta_value(metadata, "detalles", "descripcion", "description"),
        story_raw_id=story_raw,
        story_id=story_id,
        service=meta_value(metadata, "servicio", "service"),
        files=split_list(meta_value(metadata, "archivos", "files")),
        estimate=meta_value(metadata, "estimacion", "estimate"),
        priority=meta_value(metadata, "prioridad", "priority"),
        dependencies=[normalize_id(item, proposal_prefix).canonical for item in split_list(meta_value(metadata, "dependencias", "dependencies")) if item.upper().startswith("TSK-")],
        status=status,
        derived=derived,
        diagnostics=[diagnostic("warning", "task.block.legacy", "Task usa formato de bloques legacy", path, line_number)],
    )


def parse_frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    values: Dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        values[key(name)] = clean_value(value)
    return values


def parse_changelog_entry(path: Path, root: Path, format_name: str) -> ChangelogEntry:
    text = path.read_text(encoding="utf-8")
    metadata = parse_frontmatter(text)
    heading = re.search(
        r"^##\s+(?:\[Fecha:\s*)?\[?(\d{4}-\d{2}-\d{2})\]?\s*-\s*(.+?)\s*$",
        text,
        re.MULTILINE,
    )
    date_value = heading.group(1) if heading else meta_value(metadata, "date", "fecha")
    title = heading.group(2).strip() if heading else meta_value(metadata, "title", "titulo")
    summary: List[str] = []
    summary_match = re.search(r"^###\s+(?:Resumen|Summary)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if summary_match:
        tail = text[summary_match.end():]
        end_match = re.search(r"^\*\*(?:Tiempo Ahorrado|Time Saved)\*\*:", tail, re.MULTILINE)
        section = tail[:end_match.start()] if end_match else tail
        summary = [line.strip()[2:].strip() for line in section.splitlines() if line.strip().startswith("- ")]
    time_match = re.search(r"^\*\*(?:Tiempo Ahorrado|Time Saved)\*\*:\s*(.*)$", text, re.MULTILINE)
    prefix = meta_value(metadata, "prefix", "prefijo")
    slug = meta_value(metadata, "slug")
    if not prefix:
        name_match = re.match(r"^\d{4}-\d{2}-\d{2}-([A-Za-z0-9]+-[A-Za-z0-9]{4})-", path.name)
        if name_match:
            prefix = name_match.group(1)
    if not slug:
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-[A-Za-z0-9]+-[A-Za-z0-9]{4}-", "", path.stem)
    diagnostics = []
    if not heading:
        diagnostics.append(diagnostic("warning", "changelog.heading.missing", "Falta heading de fecha y título", path))
    if not summary:
        diagnostics.append(diagnostic("warning", "changelog.summary.missing", "Falta resumen con bullets", path))
    if not time_match:
        diagnostics.append(diagnostic("warning", "changelog.time.missing", "Falta Tiempo Ahorrado/Time Saved", path))
    return ChangelogEntry(
        format=format_name,
        date=date_value,
        title=title,
        summary=summary,
        time_saved=time_match.group(1).strip() if time_match else "",
        prefix=prefix,
        slug=slug,
        path=relative_path(path, root),
        diagnostics=diagnostics,
    )


def parse_changelog(root: Path) -> Tuple[List[ChangelogEntry], List[Diagnostic]]:
    qspec = root / ".quinoto-spec"
    entries: List[ChangelogEntry] = []
    diagnostics: List[Diagnostic] = []
    changelog_dir = qspec / "changelog"
    if changelog_dir.exists():
        for path in sorted(changelog_dir.glob("*.md")):
            if path.name == "INDEX.md":
                continue
            entries.append(parse_changelog_entry(path, root, "v2"))
    legacy = qspec / "quinoto-spec-changelog.md"
    if legacy.exists():
        text = legacy.read_text(encoding="utf-8")
        blocks = re.split(r"(?=^##\s+(?:\[Fecha:\s*)?\[?\d{4}-\d{2}-\d{2}\]?\s*-\s*)", text, flags=re.MULTILINE)
        for block in blocks:
            if not re.search(r"^##\s+", block, re.MULTILINE):
                continue
            heading = re.search(r"^##\s+(?:\[Fecha:\s*)?\[?(\d{4}-\d{2}-\d{2})\]?\s*-\s*(.+?)\s*$", block, re.MULTILINE)
            if not heading:
                continue
            title = heading.group(2).strip()
            summary_match = re.search(r"^###\s+(?:Resumen|Summary)\s*$", block, re.MULTILINE | re.IGNORECASE)
            summary = []
            if summary_match:
                tail = block[summary_match.end():]
                time_match = re.search(r"^\*\*(?:Tiempo Ahorrado|Time Saved)\*\*:", tail, re.MULTILINE)
                section = tail[:time_match.start()] if time_match else tail
                summary = [line.strip()[2:].strip() for line in section.splitlines() if line.strip().startswith("- ")]
            time_match = re.search(r"^\*\*(?:Tiempo Ahorrado|Time Saved)\*\*:\s*(.*)$", block, re.MULTILINE)
            entries.append(ChangelogEntry(
                format="v1",
                date=heading.group(1),
                title=title,
                summary=summary,
                time_saved=time_match.group(1).strip() if time_match else "",
                prefix="",
                slug="",
                path=relative_path(legacy, root),
                diagnostics=[] if summary else [diagnostic("warning", "changelog.summary.missing", "Falta resumen con bullets", legacy)],
            ))
    deduplicated: Dict[Tuple[str, str], ChangelogEntry] = {}
    for entry in entries:
        identity = (entry.date, key(entry.title))
        previous = deduplicated.get(identity)
        if previous is None:
            deduplicated[identity] = entry
        else:
            diagnostics.append(diagnostic("warning", "changelog.duplicate", f"Entrada duplicada: {entry.title}", Path(entry.path)))
            if entry.format == "v2":
                deduplicated[identity] = entry
    if not entries:
        diagnostics.append(diagnostic("warning", "changelog.missing", "No hay entradas de changelog", qspec))
    elif not any(entry.format == "v2" for entry in entries):
        diagnostics.append(diagnostic("warning", "changelog.v1_only", "El proyecto usa solo changelog v1", qspec))
    return sorted(deduplicated.values(), key=lambda item: (item.date, item.title), reverse=True), diagnostics


def parse_registry(path: Path) -> Tuple[List[str], List[Diagnostic]]:
    if not path.exists():
        return [], [diagnostic("warning", "registry.missing", "No existe prefix-registry.md", path)]
    prefixes: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*\|\s*([A-Za-z0-9-]+)\s*\|", line)
        if match and LEGACY_PREFIX_PATTERN.fullmatch(match.group(1)):
            prefixes.append(normalize_prefix(match.group(1)))
    diagnostics = []
    for prefix in sorted(set(prefixes)):
        if prefixes.count(prefix) > 1:
            diagnostics.append(diagnostic("error", "registry.duplicate", f"Prefijo duplicado: {prefix}", path))
    return prefixes, diagnostics


def scan_project(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    qspec = root / ".quinoto-spec"
    proposals: List[Proposal] = []
    stories: List[Story] = []
    tasks: List[Task] = []
    derived_tasks: List[Task] = []
    diagnostics: List[Diagnostic] = []
    proposal_root = qspec / "proposals"
    if proposal_root.exists():
        for proposal_dir in sorted(proposal_root.iterdir()):
            if not proposal_dir.is_dir() or proposal_dir.name == "_archived":
                continue
            proposal_path = proposal_dir / "proposal.md"
            if not proposal_path.exists():
                diagnostics.append(diagnostic("error", "proposal.file.missing", "La propuesta no contiene proposal.md", proposal_dir))
                continue
            proposal = parse_proposal(proposal_path, root)
            proposals.append(proposal)
            prefix = proposal.prefix or None
            proposal_stories: List[Story] = []
            proposal_tasks: List[Task] = []
            stories_path = proposal_dir / "user-stories.md"
            if stories_path.exists():
                proposal_stories = parse_stories(stories_path, root, prefix)
            for task_path in sorted(proposal_dir.glob("*_tasks.md")):
                parsed = parse_tasks(task_path, root, prefix, derived=task_path.name == "all_tasks.md")
                if task_path.name == "all_tasks.md":
                    derived_tasks.extend(parsed)
                else:
                    proposal_tasks.extend(parsed)
            for story in proposal_stories:
                related = [task for task in proposal_tasks if task.story_id == story.canonical_id]
                if related:
                    completed = sum(1 for task in related if task.status == "completed")
                    story.status = "completed" if completed == len(related) else ("in_progress" if completed else "pending")
            stories.extend(proposal_stories)
            tasks.extend(proposal_tasks)
    registry, registry_diagnostics = parse_registry(qspec / "prefix-registry.md")
    diagnostics.extend(registry_diagnostics)
    changelog, changelog_diagnostics = parse_changelog(root)
    diagnostics.extend(changelog_diagnostics)
    story_ids = {story.canonical_id for story in stories}
    for task in tasks:
        if task.story_id and task.story_id not in story_ids:
            diagnostics.append(diagnostic("error", "task.story.missing", f"La tarea {task.raw_id} referencia {task.story_id} inexistente", Path(task.path), task.line))
    return {
        "contract_version": CONTRACT_VERSION,
        "root": str(root),
        "proposals": [item.to_dict() for item in proposals],
        "stories": [item.to_dict() for item in stories],
        "tasks": [item.to_dict() for item in tasks],
        "derived_tasks": [item.to_dict() for item in derived_tasks],
        "registry": registry,
        "changelog": [item.to_dict() for item in changelog],
        "diagnostics": [item.to_dict() for item in diagnostics],
    }


def validate_project(root: Path) -> Dict[str, Any]:
    root = root.resolve()
    qspec = root / ".quinoto-spec"
    snapshot = scan_project(root)
    diagnostics: List[Diagnostic] = [Diagnostic(**item) for item in snapshot["diagnostics"]]
    if not qspec.exists():
        diagnostics.append(Diagnostic("error", "project.missing", "No existe .quinoto-spec/", str(qspec)))
    registry = set(snapshot["registry"])
    for proposal in snapshot["proposals"]:
        diagnostics.extend(Diagnostic(**item) for item in proposal["diagnostics"])
        prefix = proposal["prefix"]
        if prefix and prefix not in registry:
            severity = "error" if proposal["source_format"] == "canonical" else "warning"
            diagnostics.append(Diagnostic(severity, "proposal.prefix.unregistered", f"Prefijo no registrado: {prefix}", proposal["path"]))
    story_ids: Dict[str, str] = {}
    for story in snapshot["stories"]:
        diagnostics.extend(Diagnostic(**item) for item in story["diagnostics"])
        if story["canonical_id"] in story_ids:
            diagnostics.append(Diagnostic("error", "story.id.duplicate", f"Story duplicada: {story['raw_id']}", story["path"], story["line"]))
        story_ids[story["canonical_id"]] = story["raw_id"]
    task_ids: Dict[str, str] = {}
    for task in snapshot["tasks"]:
        diagnostics.extend(Diagnostic(**item) for item in task["diagnostics"])
        if task["canonical_id"] in task_ids:
            diagnostics.append(Diagnostic("error", "task.id.duplicate", f"Task duplicada: {task['raw_id']}", task["path"], task["line"]))
        task_ids[task["canonical_id"]] = task["raw_id"]
    errors = [item for item in diagnostics if item.severity == "error"]
    warnings = [item for item in diagnostics if item.severity == "warning"]
    return {
        "valid": not errors,
        "blocking": bool(errors),
        "contract_version": CONTRACT_VERSION,
        "root": str(root),
        "errors": [item.to_dict() for item in errors],
        "warnings": [item.to_dict() for item in warnings],
        "summary": {
            "proposals": len(snapshot["proposals"]),
            "stories": len(snapshot["stories"]),
            "tasks": len(snapshot["tasks"]),
            "derived_tasks": len(snapshot["derived_tasks"]),
            "changelog_entries": len(snapshot["changelog"]),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def print_json(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="QuinotoSpec artifact contract inspector and validator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "validate", "changelog"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--root", default=".", help="Project root")
        command_parser.add_argument("--json", action="store_true", dest="as_json")
        if command == "validate":
            command_parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if args.command == "inspect":
        data = scan_project(root)
        if args.as_json:
            print_json(data)
        else:
            print(f"QuinotoSpec contract v{CONTRACT_VERSION}")
            print(f"Proposals: {len(data['proposals'])}")
            print(f"Stories: {len(data['stories'])}")
            print(f"Tasks: {len(data['tasks'])}")
            print(f"Changelog entries: {len(data['changelog'])}")
            print(f"Diagnostics: {len(data['diagnostics'])}")
        return 0
    if args.command == "changelog":
        data = scan_project(root)["changelog"]
        if args.as_json:
            print_json({"entries": data})
        else:
            for entry in data:
                print(f"{entry['date']} | {entry['format']} | {entry['title']}")
        return 0
    report = validate_project(root)
    if args.as_json:
        print_json(report)
    else:
        print("QuinotoSpec artifact contract")
        print(f"Valid: {report['valid']}")
        print(f"Errors: {report['summary']['errors']}")
        print(f"Warnings: {report['summary']['warnings']}")
        for item in report["errors"]:
            print(f"ERROR {item['code']}: {item['message']} ({item['path']})")
        for item in report["warnings"]:
            print(f"WARN {item['code']}: {item['message']} ({item['path']})")
    if report["errors"]:
        return 1
    if args.strict and report["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"QuinotoSpec contract error: {error}", file=sys.stderr)
        raise SystemExit(2)
