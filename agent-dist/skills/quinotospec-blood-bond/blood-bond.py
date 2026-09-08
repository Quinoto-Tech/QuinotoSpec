#!/usr/bin/env python3
"""Blood-Bond Orchestrator -- CLI principal para @quinotospec.blood-bond.

Uso:
    python3 blood-bond.py [--root PATH] [--suggest] [--profile] [--alerts] [--force] [--limit N]

- Sin flags: análisis completo + sugerencias (analyzer -> predictor -> mostra suggestions.md)
- --suggest: solo generar sugerencias (analyzer + predictor)
- --profile: solo mostrar perfil (lee analysis.json)
- --alerts: solo mostrar alertas de estancamiento (lee analysis.json o genera si falta)

Flujo genérico:
  1. Invocar analyzer (genera analysis.json)
  2. Invocar predictor (genera suggestions.md)
  3. Mostrar resultados según flag

Solo stdlib. Offline.
"""
import json
import os
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


def find_scripts():
    base = Path(__file__).parent
    # Expected layout: agent-dist/skills/quinotospec-blood-bond/blood-bond.py
    # siblings: ../quinotospec-blood-bond-analyzer/analyzer.py etc.
    analyzer = base.parent / "quinotospec-blood-bond-analyzer" / "analyzer.py"
    predictor = base.parent / "quinotospec-blood-bond-predictor" / "predictor.py"
    monitor = base.parent / "quinotospec-blood-bond-monitor" / "monitor.py"
    return analyzer, predictor, monitor


def run_analyzer(root: Path, force: bool):
    analyzer, _, _ = find_scripts()
    if not analyzer.exists():
        print(f"Blood-Bond: analyzer no encontrado en {analyzer}", file=sys.stderr)
        return 1
    args = [sys.executable, str(analyzer), "--root", str(root)]
    if force:
        args.append("--force")
    result = subprocess.run(args, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


def run_predictor(root: Path, force: bool, limit: int = 3):
    _, predictor, _ = find_scripts()
    if not predictor.exists():
        print(f"Blood-Bond: predictor no encontrado en {predictor}", file=sys.stderr)
        return 1
    args = [sys.executable, str(predictor), "--root", str(root), "--limit", str(limit)]
    if force:
        args.append("--force")
    result = subprocess.run(args, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


def show_profile(root: Path):
    analysis_path = root / ".quinoto-spec" / "blood-bond" / "analysis.json"
    if not analysis_path.exists():
        print("Blood-Bond: no hay analysis.json — ejecuta primero `@quinotospec.blood-bond` sin flags")
        return 1
    data = json.loads(analysis_path.read_text(encoding="utf-8"))
    days = data.get("days_since_last_activity")
    last_str = f"hace {days} días" if days is not None else "sin registro"
    top = data.get("category_pattern", {}).get("top_prefixes", [])
    area = top[0] if top else "N/D"
    pct = data.get("category_pattern", {}).get("distribution", {}).get(area, "?")
    velocity = f"{data.get('progress_pattern', {}).get('avg_tasks_per_session', '?')} tasks/sesión"
    total = data.get("progress_pattern", {}).get("total_tasks", 0)
    completed = data.get("progress_pattern", {}).get("completed_tasks", 0)
    pending = data.get("progress_pattern", {}).get("pending_tasks", 0)
    switch = data.get("category_pattern", {}).get("context_switch_rate", "?")
    temporal = data.get("temporal_pattern", {})
    cold = data.get("cold_start", False)

    print("🩸 **Blood-Bond: Tu Perfil**")
    print("")
    print(f"📊 **Métricas**")
    print(f"- Última actividad: {last_str}")
    print(f"- Área principal: {area} ({pct}% del trabajo)" if area != "N/D" else "- Área principal: N/D")
    print(f"- Velocidad típica: {velocity}")
    print(f"- Context switch rate: {switch}")
    print(f"- Total completado: {completed} / {total} (pendientes: {pending})")
    print(f"- Día más activo: {temporal.get('most_active_day', 'N/D')}")
    print(f"- Frecuencia: {temporal.get('work_frequency', 'N/D')}")
    print(f"- Duración típica sprint: {data.get('sprint_pattern', {}).get('typical_duration_weeks', '?')} semanas")
    print(f"- Capacidad por sprint: {data.get('sprint_pattern', {}).get('capacity_tasks_per_sprint', '?')} tasks")
    if cold:
        print("")
        print("> ⚠️ Cold Start: <5 entradas — datos limitados. Necesito más historial para predicciones precisas.")
    print("")
    return 0


def show_alerts(root: Path):
    analysis_path = root / ".quinoto-spec" / "blood-bond" / "analysis.json"
    if not analysis_path.exists():
        print("Blood-Bond: no hay analysis.json — ejecuta analyzer primero")
        return 1
    data = json.loads(analysis_path.read_text(encoding="utf-8"))
    stagnant = data.get("progress_pattern", {}).get("stagnant_proposals", [])
    pending = data.get("progress_pattern", {}).get("pending_tasks", 0)
    in_progress = data.get("progress_pattern", {}).get("in_progress_us", [])
    completion = data.get("progress_pattern", {}).get("completion_rate", 0)
    days = data.get("days_since_last_activity")

    print("🩸 **Blood-Bond: Alertas**")
    print("")
    if not stagnant:
        print("⚠️ Ninguna propuesta estancada (proyecto activo)")
        print(f"- Días desde última actividad: {days if days is not None else 'N/D'}")
        print(f"- Completion rate: {completion}%")
        print("")
        return 0

    for slug in stagnant:
        print(f"⚠️ `{slug}` sin avance en >=14 días")
        # Try to find pending task for suggestion
        # Look at _debug pending_task_details
        pending_details = data.get("_debug", {}).get("pending_task_details", [])
        related = [t for t in pending_details if slug in t.get("file", "")]
        if related:
            tid = related[0].get("id", "TSK-???")
            print(f"   {pending} tasks pendientes — siguiente: `{tid}`")
            print(f"   💡 Sugerencia: `@quinotospec.apply {tid}` para continuar")
        else:
            print(f"   💡 Sugerencia: revisar `{slug}` — ¿Bloqueada o abandonada? Considera `@quinotospec.archive`")
        print("")

    if in_progress:
        print(f"📋 Historias en progreso: {', '.join(in_progress)}")
        print("")

    print(f"📊 Total pendientes: {pending}")
    print("")
    return 0


def show_full(root: Path):
    suggestions_path = root / ".quinoto-spec" / "blood-bond" / "suggestions.md"
    analysis_path = root / ".quinoto-spec" / "blood-bond" / "analysis.json"
    if not suggestions_path.exists():
        print(f"Blood-Bond: no existe {suggestions_path}")
        return 1

    # If analysis indicates cold_start, mention
    if analysis_path.exists():
        data = json.loads(analysis_path.read_text(encoding="utf-8"))
        days = data.get("days_since_last_activity")
        area = (data.get("category_pattern", {}).get("top_prefixes", []) or ["N/D"])[0]
        velocity = data.get("progress_pattern", {}).get("avg_tasks_per_session", "?")

        print("🩸 **Blood-Bond: Análisis Completo**")
        print("")
        print("📊 **Tu Perfil**")
        print(f"- Última actividad: hace {days} días" if days is not None else "- Última actividad: sin registro")
        print(f"- Área principal: {area}")
        print(f"- Velocidad: {velocity} tasks/sesión")
        print("")
        print("---")
        print("")

    # Print suggestions.md content
    print(suggestions_path.read_text(encoding="utf-8"))
    return 0


def main():
    root, rest = resolve_root(sys.argv[1:])

    is_suggest = "--suggest" in rest
    is_profile = "--profile" in rest
    is_alerts = "--alerts" in rest
    force = "--force" in rest
    limit = 3
    if "--limit" in rest:
        i = rest.index("--limit")
        if i + 1 < len(rest):
            try:
                limit = int(rest[i + 1])
            except ValueError:
                pass
    for arg in rest:
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=", 1)[1])
            except ValueError:
                pass

    # --profile only
    if is_profile:
        # Ensure analysis exists, if not run analyzer
        analysis_path = root / ".quinoto-spec" / "blood-bond" / "analysis.json"
        if not analysis_path.exists() or force:
            run_analyzer(root, force=True)
        return show_profile(root)

    if is_alerts:
        analysis_path = root / ".quinoto-spec" / "blood-bond" / "analysis.json"
        if not analysis_path.exists() or force:
            run_analyzer(root, force=True)
        return show_alerts(root)

    if is_suggest:
        rc = run_analyzer(root, force=force)
        if rc != 0:
            return rc
        rc = run_predictor(root, force=force, limit=limit)
        if rc != 0:
            return rc
        # Show suggestions
        suggestions_path = root / ".quinoto-spec" / "blood-bond" / "suggestions.md"
        if suggestions_path.exists():
            print(suggestions_path.read_text(encoding="utf-8"))
        return 0

    # Default: full analysis + suggestions
    rc = run_analyzer(root, force=force)
    if rc != 0:
        return rc
    rc = run_predictor(root, force=force, limit=limit)
    if rc != 0:
        return rc
    return show_full(root)


if __name__ == "__main__":
    sys.exit(main())
