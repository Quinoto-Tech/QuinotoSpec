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
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def load_contract():
    path = Path(__file__).resolve().parents[1] / "quinotospec-contract" / "contract.py"
    spec = importlib.util.spec_from_file_location("quinotospec_contract_shared", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = load_contract()


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
    try:
        entries, _ = CONTRACT.parse_changelog(root)
    except (OSError, ValueError):
        entries = []
    dates = []
    last_proposal = None
    last_task = None
    for entry in entries:
        try:
            dates.append(datetime.date.fromisoformat(entry.date))
        except ValueError:
            continue
        if last_proposal is None:
            last_proposal = entry.path.split("/")[-1] if entry.path else None
        if last_task is None:
            raw = Path(entry.path)
            if not raw.is_absolute():
                raw = root / raw
            text = raw.read_text(errors="ignore") if raw.exists() else ""
            match = re.search(r"TSK-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-\d+", text)
            if match:
                last_task = match.group(0)
    if not dates:
        try:
            proposals = CONTRACT.scan_project(root)["proposals"]
        except (OSError, ValueError):
            proposals = []
        for proposal in proposals:
            try:
                dates.append(datetime.date.fromisoformat(proposal["date"]))
                last_proposal = last_proposal or Path(proposal["path"]).parent.name
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
