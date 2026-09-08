#!/usr/bin/env python3
"""Blood-Bond Analyzer -- recolecta patrones históricos del proyecto.

Uso:
    python3 analyzer.py [--root PATH] [--force] [--output PATH]

Lee:
  - changelog v2: .quinoto-spec/changelog/*.md
  - changelog v1: .quinoto-spec/quinoto-spec-changelog.md
  - prefix registry: .quinoto-spec/prefix-registry.md
  - proposals: .quinoto-spec/proposals/*/proposal.md
  - user stories: .quinoto-spec/proposals/*/user-stories.md
  - tasks: .quinoto-spec/proposals/*/*_tasks.md y **/*_tasks.md
  - discovery: .quinoto-spec/discovery/01-stack-profile.md (opcional)

Genera: .quinoto-spec/blood-bond/analysis.json

Solo stdlib. Offline.
"""
import datetime
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

SPANISH_DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


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
        root = os.environ.get("QUINOTOSPEC_BLOOD_BOND_ROOT") or os.environ.get("BLOOD_BOND_ROOT")
    if root is None:
        root = "."
    return Path(root).resolve(), args


def parse_changelog(root: Path):
    """Retorna lista de dicts {date_str, date_obj, title, task_ids, raw} ordenada por fecha."""
    entries = []

    # v2: .quinoto-spec/changelog/*.md
    changelog_dir = root / ".quinoto-spec" / "changelog"
    if changelog_dir.exists():
        for f in sorted(changelog_dir.glob("*.md")):
            text = f.read_text(errors="ignore")
            # Try to extract date from filename first
            m = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            date_str = m.group(1) if m else None
            # Also try header
            m2 = re.search(r"##\s*\[Fecha:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\]", text)
            if m2:
                date_str = m2.group(1)
            if not date_str:
                continue
            try:
                date_obj = datetime.date.fromisoformat(date_str)
            except ValueError:
                continue
            # Extract TASK_IDs
            task_ids = re.findall(r"TSK-[A-Za-z0-9]+-[0-9]+", text)
            # Title: first heading after date or filename
            title = f.stem
            m_title = re.search(r"##\s*\[Fecha:[^\]]*\]\s*-\s*(.+)", text)
            if m_title:
                title = m_title.group(1).strip()
            entries.append({"date_str": date_str, "date_obj": date_obj, "title": title, "task_ids": task_ids, "raw": text, "source": str(f)})

    # v1: .quinoto-spec/quinoto-spec-changelog.md
    legacy = root / ".quinoto-spec" / "quinoto-spec-changelog.md"
    if legacy.exists():
        text = legacy.read_text(errors="ignore")
        for m in re.finditer(r"##\s*\[Fecha:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\]\s*-?\s*([^\n]*)", text):
            date_str = m.group(1)
            title = m.group(2).strip() or "legacy-entry"
            try:
                date_obj = datetime.date.fromisoformat(date_str)
            except ValueError:
                continue
            # Snippet for task extraction
            start = m.start()
            snippet = text[start:start + 2000]
            task_ids = re.findall(r"TSK-[A-Za-z0-9]+-[0-9]+", snippet)
            entries.append({"date_str": date_str, "date_obj": date_obj, "title": title, "task_ids": task_ids, "raw": snippet, "source": str(legacy)})

    # Deduplicate by date+title maybe but keep all; sort by date
    entries.sort(key=lambda e: e["date_obj"])
    return entries


def parse_prefix_registry(root: Path):
    registry = root / ".quinoto-spec" / "prefix-registry.md"
    prefixes = []
    if not registry.exists():
        return prefixes
    text = registry.read_text(errors="ignore")
    # Table rows | PREFIX | ...
    for line in text.splitlines():
        # Look for | XXXX-xxxx | pattern
        m = re.match(r"\s*\|\s*([A-Z]{3,6}-[a-z0-9]{4})\s*\|", line)
        if m:
            # Extract prefix part before -
            full = m.group(1)
            prefix = full.split("-")[0]
            prefixes.append(prefix)
        else:
            # Alternative: | AUTH | ... (without suffix)
            m2 = re.match(r"\s*\|\s*([A-Z]{2,6})\s*\|", line)
            if m2:
                val = m2.group(1)
                if val not in ("Prefijo", "PREFIX", "Nombre"):
                    prefixes.append(val)
    return prefixes


def parse_proposals(root: Path):
    proposals_dir = root / ".quinoto-spec" / "proposals"
    proposals = []
    if not proposals_dir.exists():
        return proposals
    for proposal_md in sorted(proposals_dir.glob("*/proposal.md")):
        if "_archived" in proposal_md.parts:
            continue
        text = proposal_md.read_text(errors="ignore")
        prefix = None
        m = re.search(r"\*\*Prefijo:?\*\*:?\s*(\S+)", text)
        if m:
            raw_prefix = m.group(1).strip().rstrip(".,;:")
            # raw may be AUTH-a1b2 -> extract AUTH
            if "-" in raw_prefix:
                prefix = raw_prefix.split("-")[0].upper()
            else:
                prefix = raw_prefix.upper()
        fecha = None
        m2 = re.search(r"\*\*Fecha de Creaci[oó]n\*\*:?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
        if m2:
            fecha = m2.group(1)
        estado = None
        m3 = re.search(r"\*\*Estado\*\*:?\s*(.+)", text)
        if m3:
            estado = m3.group(1).strip()
        prioridad = None
        m4 = re.search(r"\*\*Prioridad\*\*:?\s*(P[123])", text)
        if m4:
            prioridad = m4.group(1)
        proposals.append({
            "path": proposal_md,
            "dir": proposal_md.parent,
            "slug": proposal_md.parent.name,
            "prefix": prefix,
            "fecha": fecha,
            "estado": estado,
            "prioridad": prioridad,
            "text": text,
        })
    return proposals


def scan_tasks(root: Path):
    proposals_dir = root / ".quinoto-spec" / "proposals"
    total = 0
    completed = 0
    pending = 0
    pending_tasks = []  # list of {id, line, file}
    completed_tasks = []
    if not proposals_dir.exists():
        return total, completed, pending, pending_tasks, completed_tasks
    for tasks_file in proposals_dir.rglob("*_tasks.md"):
        if "_archived" in tasks_file.parts:
            continue
        text = tasks_file.read_text(errors="ignore")
        for line in text.splitlines():
            # Count tasks with checkboxes
            if "[x]" in line or "[X]" in line:
                total += 1
                completed += 1
                # Extract TASK_ID
                m = re.search(r"TSK-[A-Za-z0-9]+-[0-9]+", line)
                if m:
                    completed_tasks.append({"id": m.group(0), "file": str(tasks_file.relative_to(root)), "line": line.strip()})
            elif "[ ]" in line:
                total += 1
                pending += 1
                m = re.search(r"TSK-[A-Za-z0-9]+-[0-9]+", line)
                tid = m.group(0) if m else None
                pending_tasks.append({"id": tid, "file": str(tasks_file.relative_to(root)), "line": line.strip()})
    return total, completed, pending, pending_tasks, completed_tasks


def analyze_temporal(entries):
    if not entries:
        return {
            "most_active_day": "desconocido",
            "typical_session_duration": "2-3 horas",
            "work_frequency": "esporádico",
            "days_since_last_activity": None,
        }
    # Most active day
    day_counter = Counter()
    for e in entries:
        wd = e["date_obj"].weekday()  # 0 monday
        day_counter[wd] += 1
    most_wd = day_counter.most_common(1)[0][0]
    most_active_day = SPANISH_DAYS[most_wd]

    # Days since last
    today = datetime.date.today()
    last = max(e["date_obj"] for e in entries)
    days_since = (today - last).days
    if days_since < 0:
        days_since = 0

    # Work frequency
    # Compute average gap
    if len(entries) >= 2:
        gaps = []
        sorted_dates = sorted(e["date_obj"] for e in entries)
        for i in range(1, len(sorted_dates)):
            gaps.append((sorted_dates[i] - sorted_dates[i-1]).days)
        avg_gap = sum(gaps) / len(gaps) if gaps else 999
        if avg_gap <= 2:
            freq = "diario"
        elif avg_gap <= 7:
            freq = "semanal"
        elif avg_gap <= 14:
            freq = "quincenal"
        else:
            freq = "esporádico"
    else:
        freq = "esporádico"

    # Session duration heuristic: based on tasks per day?
    return {
        "most_active_day": most_active_day,
        "typical_session_duration": "2-3 horas",
        "work_frequency": freq,
        "days_since_last_activity": days_since,
    }


def analyze_category(entries, proposals, registry_prefixes):
    # Extract prefixes from changelog TASK_IDs and proposal prefixes
    counter = Counter()
    for e in entries:
        for tid in e["task_ids"]:
            # TSK-AUTH-001 -> AUTH
            m = re.match(r"TSK-([A-Za-z0-9]+)-", tid)
            if m:
                counter[m.group(1).upper()] += 1
    for p in proposals:
        if p["prefix"]:
            counter[p["prefix"]] += 1

    # If registry has prefixes not counted, ensure they appear at least 0? but we prioritize counted
    # Also add registry prefixes with 0 if not present for completeness
    for rp in registry_prefixes:
        if rp not in counter:
            # Don't add zero counts to distribution; just keep for reference
            pass

    total = sum(counter.values())
    if total == 0:
        # fallback: use proposal prefixes or registry
        if proposals:
            for p in proposals:
                if p["prefix"]:
                    counter[p["prefix"]] += 1
            total = sum(counter.values())
        if total == 0 and registry_prefixes:
            for rp in registry_prefixes:
                counter[rp] += 1
            total = sum(counter.values())

    if total == 0:
        top = []
        dist = {}
        switch = "bajo"
    else:
        top = [k for k, _ in counter.most_common(3)]
        dist = {}
        other_sum = 0
        for k, v in counter.most_common():
            pct = round(v / total * 100)
            if k in top:
                dist[k] = pct
            else:
                other_sum += pct
        if other_sum > 0:
            dist["OTHER"] = other_sum
        # Adjust to 100% if rounding error
        s = sum(dist.values())
        if s != 100 and dist:
            # Adjust largest
            largest = max(dist, key=lambda k: dist[k])
            dist[largest] += 100 - s

        # Context switch rate: how many distinct prefixes vs total?
        distinct = len(counter)
        if total <= 1:
            switch = "bajo"
        elif distinct / total > 0.5:
            switch = "alto"
        elif distinct / total > 0.3:
            switch = "medio"
        else:
            switch = "bajo"

    return {
        "top_prefixes": top,
        "distribution": dist,
        "context_switch_rate": switch,
        "counter": counter,
        "total_mentions": total,
    }


def analyze_sequential(entries):
    # Build sequence from changelog order, extracting prefix per entry (first TASK_ID or proposal prefix)
    seq = []
    for e in entries:
        prefix = None
        if e["task_ids"]:
            m = re.match(r"TSK-([A-Za-z0-9]+)-", e["task_ids"][0])
            if m:
                prefix = m.group(1).upper()
        if prefix:
            seq.append(prefix)

    # Build bigrams
    bigrams = []
    for i in range(len(seq) - 1):
        if seq[i] != seq[i+1]:
            bigrams.append((seq[i], seq[i+1]))
    # Count
    bigram_counter = Counter(bigrams)
    common = [list(k) for k, _ in bigram_counter.most_common(3) if bigram_counter[k] >= 1]
    # If no bigrams from changelog, try to infer from proposals? else empty
    # Dependencies: map first -> list of seconds
    deps = {}
    for (a, b), cnt in bigram_counter.items():
        if cnt >= 1:
            deps.setdefault(a, []).append(b)
    # Deduplicate deps
    for k in deps:
        deps[k] = sorted(set(deps[k]))

    return {
        "sequence": seq,
        "common_sequences": common,
        "detected_dependencies": deps,
        "bigram_counter": bigram_counter,
    }


def analyze_progress(entries, proposals, total_tasks, completed_tasks_count, pending_tasks_count, pending_tasks):
    today = datetime.date.today()
    # Avg tasks per session: use distinct dates with entries
    if entries:
        distinct_dates = len(set(e["date_str"] for e in entries))
        avg_per_session = round(completed_tasks_count / distinct_dates, 1) if distinct_dates else 0
        if avg_per_session == 0 and completed_tasks_count > 0:
            avg_per_session = 1
        # If no completed but entries exist, estimate 1-3
        if completed_tasks_count == 0:
            avg_per_session = 1
    else:
        avg_per_session = 0

    completion_rate = round(completed_tasks_count / total_tasks * 100) if total_tasks else 0

    # Stagnant proposals: >14 days without advance
    # For each proposal, find last activity date from changelog mentioning its prefix or slug
    stagnant = []
    in_progress_us = []
    for p in proposals:
        last_date = None
        # Check changelog
        for e in entries:
            if (p["prefix"] and p["prefix"] in e["raw"]) or (p["slug"] in e["raw"]):
                if last_date is None or e["date_obj"] > last_date:
                    last_date = e["date_obj"]
        # Fallback to proposal fecha
        if last_date is None and p["fecha"]:
            try:
                last_date = datetime.date.fromisoformat(p["fecha"])
            except ValueError:
                last_date = None
        if last_date:
            days = (today - last_date).days
            if days >= 14:
                stagnant.append(p["slug"])
        # In progress: proposals with pending tasks >0 and not all done
        # Need to check tasks per proposal dir
        prop_tasks_total = 0
        prop_tasks_pending = 0
        for t in pending_tasks:
            if p["slug"] in t["file"]:
                prop_tasks_pending += 1
        # Also count completed in that slug
        # For simplicity, if pending >0 we consider in-progress
        if prop_tasks_pending > 0:
            # Find US file?
            us_file = p["dir"] / "user-stories.md"
            if us_file.exists():
                # Check if user-stories has been started (exists)
                in_progress_us.append(p["slug"])

    # Also check discovery for sprint pattern? Not needed
    return {
        "avg_tasks_per_session": avg_per_session,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks_count,
        "pending_tasks": pending_tasks_count,
        "completion_rate": completion_rate,
        "stagnant_proposals": sorted(set(stagnant)),
        "in_progress_us": sorted(set(in_progress_us)),
        "pending_task_details": pending_tasks,
    }


def analyze_sprint(total_tasks, avg_per_session, completion_rate):
    # Heuristics
    typical_duration_weeks = 2
    # Capacity: avg per session * sessions per sprint (approx 5)
    if avg_per_session and avg_per_session > 0:
        capacity = int(avg_per_session * 5)
        if capacity < 5:
            capacity = 5
        if capacity > 30:
            capacity = 30
    else:
        capacity = 15
    if completion_rate >= 70:
        velocity = "alta"
    elif completion_rate >= 40:
        velocity = "media"
    else:
        velocity = "baja"

    return {
        "typical_duration_weeks": typical_duration_weeks,
        "capacity_tasks_per_sprint": capacity,
        "current_velocity": velocity,
    }


def main():
    root, rest = resolve_root(sys.argv[1:])
    force = "--force" in rest
    output_path = None
    if "--output" in rest:
        i = rest.index("--output")
        if i + 1 < len(rest):
            output_path = Path(rest[i + 1])
            # If relative, resolve against root
            if not output_path.is_absolute():
                output_path = (Path.cwd() / output_path).resolve()
            rest = rest[:i] + rest[i+2:]

    # Also handle --output=PATH form?
    for arg in list(rest):
        if arg.startswith("--output="):
            output_path = Path(arg.split("=", 1)[1])
            if not output_path.is_absolute():
                output_path = (Path.cwd() / output_path).resolve()

    blood_dir = root / ".quinoto-spec" / "blood-bond"
    blood_dir.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = blood_dir / "analysis.json"

    if output_path.exists() and not force:
        # Still regenerate? spec says --force forces re-analysis
        # Without force, we still regenerate but could skip; spec says --force forces even if exists
        # So we always regenerate unless we want to skip; but we will regenerate anyway
        pass

    entries = parse_changelog(root)
    registry_prefixes = parse_prefix_registry(root)
    proposals = parse_proposals(root)
    total_tasks, completed, pending, pending_details, completed_details = scan_tasks(root)

    cold_start = len(entries) < 5

    temporal = analyze_temporal(entries)
    days_since = temporal.get("days_since_last_activity")
    # If no entries, days_since is None

    category = analyze_category(entries, proposals, registry_prefixes)
    sequential = analyze_sequential(entries)
    progress = analyze_progress(entries, proposals, total_tasks, completed, pending, pending_details)
    sprint = analyze_sprint(total_tasks, progress["avg_tasks_per_session"], progress["completion_rate"])

    # Build final json
    output = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cold_start": cold_start,
        "days_since_last_activity": days_since,
        "temporal_pattern": {
            "most_active_day": temporal["most_active_day"],
            "typical_session_duration": temporal["typical_session_duration"],
            "work_frequency": temporal["work_frequency"],
        },
        "category_pattern": {
            "top_prefixes": category["top_prefixes"],
            "distribution": category["distribution"],
            "context_switch_rate": category["context_switch_rate"],
        },
        "sequential_pattern": {
            "common_sequences": sequential["common_sequences"],
            "detected_dependencies": sequential["detected_dependencies"],
        },
        "progress_pattern": {
            "avg_tasks_per_session": progress["avg_tasks_per_session"],
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": progress["completion_rate"],
            "stagnant_proposals": progress["stagnant_proposals"],
            "in_progress_us": progress["in_progress_us"],
        },
        "sprint_pattern": {
            "typical_duration_weeks": sprint["typical_duration_weeks"],
            "capacity_tasks_per_sprint": sprint["capacity_tasks_per_sprint"],
            "current_velocity": sprint["current_velocity"],
        },
    }

    # Add extra debug maybe but keep spec fields
    # Also include raw counts for predictor
    output["_debug"] = {
        "entries_count": len(entries),
        "pending_task_details": pending_details[:10],  # limit
        "sequence": sequential["sequence"],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Blood-Bond Analyzer: {len(entries)} entradas, {total_tasks} tasks ({completed} done, {pending} pending) -> {output_path}")
    if cold_start:
        print("  Cold start: <5 entradas — sugerencias limitadas")
    if days_since is not None:
        print(f"  Última actividad: hace {days_since} días")
    else:
        print("  Sin actividad registrada")

    return 0


if __name__ == "__main__":
    sys.exit(main())
