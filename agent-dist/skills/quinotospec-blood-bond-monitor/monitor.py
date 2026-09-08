#!/usr/bin/env python3
"""Blood-Bond Monitor -- detecta inactividad y activa recordatorio proactivo.

Uso:
    python3 monitor.py [--root PATH] [--check-only] [--force] [--days N]

- Lee changelog v2/v1 para extraer última fecha.
- Calcula días desde última actividad.
- Estados: inactive >=14, warning 7-13, active <7
- Si inactive y no --check-only: ejecuta analyzer --force y predictor --force, genera reminder.md
- --check-only solo imprime JSON de estado
- --force fuerza recordatorio aunque esté activo
- --days N configura umbral (default 14)

Solo stdlib. Offline (salvo subprocesos para analyzer/predictor).
"""
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path


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


def parse_changelog_last_date(root: Path):
    dates = []
    last_proposal = None
    last_task = None

    changelog_dir = root / ".quinoto-spec" / "changelog"
    if changelog_dir.exists():
        for entry in sorted(changelog_dir.glob("*.md")):
            text = entry.read_text(errors="ignore")
            m = re.match(r"(\d{4}-\d{2}-\d{2})", entry.stem)
            date_str = m.group(1) if m else None
            m2 = re.search(r"##\s*\[Fecha:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\]", text)
            if m2:
                date_str = m2.group(1)
            if date_str:
                try:
                    dates.append(datetime.date.fromisoformat(date_str))
                except ValueError:
                    pass
                # Try to find proposal/task mentions
                if not last_proposal:
                    m_prop = re.search(r"propuesta\s*[`'\"]?([a-z0-9-]+)", text, re.I)
                    if m_prop:
                        last_proposal = m_prop.group(1)
                if not last_task:
                    m_task = re.search(r"TSK-[A-Za-z0-9]+-[0-9]+", text)
                    if m_task:
                        last_task = m_task.group(0)
            else:
                continue

    legacy = root / ".quinoto-spec" / "quinoto-spec-changelog.md"
    if legacy.exists():
        text = legacy.read_text(errors="ignore")
        for m in re.finditer(r"##\s*\[Fecha:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\]", text):
            date_str = m.group(1)
            try:
                dates.append(datetime.date.fromisoformat(date_str))
            except ValueError:
                continue
            snippet = text[m.start():m.start() + 1000]
            if not last_task:
                mt = re.search(r"TSK-[A-Za-z0-9]+-[0-9]+", snippet)
                if mt:
                    last_task = mt.group(0)
            if not last_proposal:
                mp = re.search(r"propuesta\s*[`'\"]?([a-z0-9-]+)", snippet, re.I)
                if mp:
                    last_proposal = mp.group(1)

    # Fallback to proposal fechas if no changelog dates
    if not dates:
        proposals_dir = root / ".quinoto-spec" / "proposals"
        if proposals_dir.exists():
            for proposal_md in proposals_dir.glob("*/proposal.md"):
                if "_archived" in proposal_md.parts:
                    continue
                text = proposal_md.read_text(errors="ignore")
                m = re.search(r"\*\*Fecha de Creaci[oó]n\*\*:?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text)
                if m:
                    try:
                        dates.append(datetime.date.fromisoformat(m.group(1)))
                        if not last_proposal:
                            last_proposal = proposal_md.parent.name
                    except ValueError:
                        pass

    if not dates:
        return None, last_proposal, last_task
    return max(dates), last_proposal, last_task


def main():
    root, rest = resolve_root(sys.argv[1:])

    check_only = "--check-only" in rest
    force = "--force" in rest
    threshold = 14
    if "--days" in rest:
        i = rest.index("--days")
        if i + 1 < len(rest):
            try:
                threshold = int(rest[i + 1])
            except ValueError:
                pass
    for arg in rest:
        if arg.startswith("--days="):
            try:
                threshold = int(arg.split("=", 1)[1])
            except ValueError:
                pass

    last_date, last_proposal, last_task = parse_changelog_last_date(root)

    if last_date is None:
        days_since = None
        status = "no_data"
        should_remind = False
    else:
        today = datetime.date.today()
        days_since = (today - last_date).days
        if days_since < 0:
            days_since = 0
        if days_since >= threshold:
            status = "inactive"
            should_remind = True
        elif days_since >= 7:
            status = "warning"
            should_remind = False
        else:
            status = "active"
            should_remind = False

    if force:
        should_remind = True
        if status != "inactive":
            status = "inactive_forced"

    result = {
        "status": status,
        "days_since_activity": days_since,
        "last_date": last_date.isoformat() if last_date else None,
        "last_proposal": last_proposal,
        "last_task": last_task,
        "should_remind": should_remind,
        "threshold_days": threshold,
    }

    if check_only:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if should_remind or force:
        # Ejecutar analyzer y predictor
        blood_dir = root / ".quinoto-spec" / "blood-bond"
        blood_dir.mkdir(parents=True, exist_ok=True)

        # Find companion scripts
        analyzer_path = Path(__file__).parent.parent / "quinotospec-blood-bond-analyzer" / "analyzer.py"
        predictor_path = Path(__file__).parent.parent / "quinotospec-blood-bond-predictor" / "predictor.py"
        # Fallback to same dir structure if deployed elsewhere
        if not analyzer_path.exists():
            analyzer_path = root / "agent-dist" / "skills" / "quinotospec-blood-bond-analyzer" / "analyzer.py"
        if not predictor_path.exists():
            predictor_path = root / "agent-dist" / "skills" / "quinotospec-blood-bond-predictor" / "predictor.py"

        # Try running analyzer
        if analyzer_path.exists():
            try:
                subprocess.run([sys.executable, str(analyzer_path), "--root", str(root), "--force"], timeout=15, capture_output=True)
            except Exception as e:
                print(f"Monitor: analyzer falló: {e}", file=sys.stderr)
        if predictor_path.exists():
            try:
                subprocess.run([sys.executable, str(predictor_path), "--root", str(root), "--force"], timeout=15, capture_output=True)
            except Exception as e:
                print(f"Monitor: predictor falló: {e}", file=sys.stderr)

        # Generate reminder.md
        suggestions_path = blood_dir / "suggestions.md"
        reminder_path = blood_dir / "reminder.md"

        # Try to read suggestions for embedding
        suggestions_preview = ""
        if suggestions_path.exists():
            try:
                text = suggestions_path.read_text(encoding="utf-8")
                # Take first 3 suggestion titles
                preview_lines = []
                for line in text.splitlines():
                    if line.startswith("### "):
                        preview_lines.append(line.strip())
                        if len(preview_lines) >= 3:
                            break
                if preview_lines:
                    suggestions_preview = "\n".join(preview_lines)
            except OSError:
                pass

        days_str = str(days_since) if days_since is not None else "desconocido"
        prop_str = last_proposal or "desconocida"
        reminder = []
        reminder.append(f"🩸 **Blood-Bond: Hey!** Hace {days_str} días que no hay actividad en el proyecto.")
        reminder.append("")
        reminder.append(f"Propuesta más reciente: `{prop_str}`")
        reminder.append("¿Querés que te sugiera qué hacer a continuación?")
        reminder.append("")
        if suggestions_preview:
            reminder.append(suggestions_preview)
            reminder.append("")
        reminder.append(f"Ejecutar: `@quinotospec.blood-bond --suggest` para ver detalles.")
        if last_task:
            reminder.append(f"Última task: `{last_task}`")
        reminder.append("")

        reminder_path.write_text("\n".join(reminder), encoding="utf-8")
        print(f"Blood-Bond Monitor: estado={status}, hace {days_str} días — recordatorio generado en {reminder_path}")
        # Also print reminder
        print("\n".join(reminder))
    else:
        print(f"Blood-Bond Monitor: estado={status}, hace {days_since} días — sin recordatorio (activo)")

    # If not check_only, also output json to stdout? The spec says check-only returns json; but we also want to return json when force?
    # For non-check_only, we already printed status; exit with 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
