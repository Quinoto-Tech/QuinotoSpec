#!/usr/bin/env python3
"""Blood-Bond Predictor -- genera sugerencias accionables desde analysis.json.

Uso:
    python3 predictor.py [--root PATH] [--force] [--limit N]

Input: .quinoto-spec/blood-bond/analysis.json
Output: .quinoto-spec/blood-bond/suggestions.md

Reglas de predicción:
  1. Siguiente en Secuencia
  2. Área Caliente (Hot Path >40%)
  3. Desbloqueo
  4. Estancamiento >=14 días
  5. Prioridad + Velocidad

Solo stdlib.
"""
import datetime
import json
import os
import re
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


def parse_args(rest):
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
    return force, limit


def load_analysis(root: Path):
    p = root / ".quinoto-spec" / "blood-bond" / "analysis.json"
    if not p.exists():
        return None, f"no existe {p} — ejecuta analyzer primero"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data, None
    except (json.JSONDecodeError, OSError) as e:
        return None, str(e)


def find_pending_tasks(root: Path):
    proposals_dir = root / ".quinoto-spec" / "proposals"
    pending_by_prefix = {}  # prefix -> list of task lines
    all_pending = []
    if not proposals_dir.exists():
        return pending_by_prefix, all_pending
    for tasks_file in proposals_dir.rglob("*_tasks.md"):
        if "_archived" in tasks_file.parts:
            continue
        text = tasks_file.read_text(errors="ignore")
        for line in text.splitlines():
            if "[ ]" in line:
                m = re.search(r"TSK-([A-Za-z0-9]+)-[0-9]+", line)
                prefix = m.group(1).upper() if m else "UNKNOWN"
                # Extract TASK_ID
                tid_m = re.search(r"TSK-[A-Za-z0-9]+-[0-9]+", line)
                tid = tid_m.group(0) if tid_m else None
                entry = {"id": tid, "prefix": prefix, "file": str(tasks_file.relative_to(root)), "line": line.strip()}
                all_pending.append(entry)
                pending_by_prefix.setdefault(prefix, []).append(entry)
    return pending_by_prefix, all_pending


def find_proposal_priorities(root: Path):
    proposals_dir = root / ".quinoto-spec" / "proposals"
    prio_map = {}  # slug -> P1/P2/P3
    if not proposals_dir.exists():
        return prio_map
    for proposal_md in sorted(proposals_dir.glob("*/proposal.md")):
        if "_archived" in proposal_md.parts:
            continue
        slug = proposal_md.parent.name
        text = proposal_md.read_text(errors="ignore")
        m = re.search(r"\*\*Prioridad\*\*:?\s*(P[123])", text)
        if m:
            prio_map[slug] = m.group(1)
        else:
            prio_map[slug] = "P3"
    return prio_map


def confidence_bars(level: str) -> str:
    if level == "Alta":
        return "████░░ Alta"
    elif level == "Media":
        return "███░░░ Media"
    else:
        return "██░░░░ Baja"


def generate_suggestions(analysis, pending_by_prefix, all_pending, prio_map):
    suggestions = []
    alerts = []

    cold_start = analysis.get("cold_start", False)
    days_since = analysis.get("days_since_last_activity")
    temporal = analysis.get("temporal_pattern", {})
    category = analysis.get("category_pattern", {})
    sequential = analysis.get("sequential_pattern", {})
    progress = analysis.get("progress_pattern", {})
    sprint = analysis.get("sprint_pattern", {})

    top_prefixes = category.get("top_prefixes", [])
    distribution = category.get("distribution", {})
    common_seqs = sequential.get("common_sequences", [])
    deps = sequential.get("detected_dependencies", {})
    stagnant = progress.get("stagnant_proposals", [])
    pending_count = progress.get("pending_tasks", 0)
    velocity = sprint.get("current_velocity", "media")

    # REGLA 4: Estancamiento (crítico) - first alerts
    for slug in stagnant:
        prio = prio_map.get(slug, "P3")
        # Find days? approximate from analysis? Use days_since + maybe
        alerts.append({
            "type": "stagnation",
            "proposal": slug,
            "priority": prio,
            "reason": f"Sin avance en >=14 días",
            "action": f"Revisar `{slug}` — ¿Bloqueada o abandonada? Ejecutar `@quinotospec.apply` para continuar o `@quinotospec.archive` si ya no aplica",
            "confidence": "Alta" if prio == "P1" else "Media",
        })

    # Also from analysis pending task details, we have _debug pending_task_details
    # Build suggestions

    # REGLA 2: Hot Path
    for prefix, pct in distribution.items():
        if prefix == "OTHER":
            continue
        if pct is None:
            continue
        try:
            pct_val = int(pct)
        except:
            continue
        if pct_val > 40 and prefix in pending_by_prefix:
            count = len(pending_by_prefix[prefix])
            # Find first pending task id
            first = pending_by_prefix[prefix][0]
            tid = first["id"] or f"TSK-{prefix}-???"
            conf = "Alta" if pct_val >= 60 else "Media"
            suggestions.append({
                "title": f"Continuar con {prefix}",
                "reason": f"Hace {pct_val}% de tu trabajo en {prefix}. Tenés {count} tasks pendientes. Evitar context switch.",
                "action": f"@quinotospec.apply {tid}",
                "confidence": conf,
                "priority_order": 3,
            })
            # Only first hot path
            break

    # REGLA 1: Siguiente en Secuencia
    for seq in common_seqs:
        if len(seq) < 2:
            continue
        a, b = seq[0], seq[1]
        # If last work was in a (check top_prefixes or sequence), suggest b
        # For simplicity, if a is in top_prefixes and b has pending
        if b in pending_by_prefix:
            # Check if sequence is relevant: a is top or last in _debug sequence
            seq_list = analysis.get("_debug", {}).get("sequence", [])
            last_prefix = seq_list[-1] if seq_list else (top_prefixes[0] if top_prefixes else None)
            if last_prefix == a or a in top_prefixes:
                first = pending_by_prefix[b][0]
                tid = first["id"] or f"TSK-{b}-???"
                suggestions.append({
                    "title": f"Preparar {b} (siguiente en secuencia {a} → {b})",
                    "reason": f"Secuencia típica: {a} → {b}. Ya completaste trabajo en {a}.",
                    "action": f"@quinotospec.apply {tid}",
                    "confidence": "Media",
                    "priority_order": 4,
                })
                break

    # REGLA 3: Desbloqueo (if deps and completed)
    for src, dst_list in deps.items():
        for dst in dst_list:
            if dst in pending_by_prefix:
                # Check if src has no pending (i.e., completed)
                src_pending = pending_by_prefix.get(src, [])
                if not src_pending:
                    # src completed, dst pending -> suggest dst
                    first = pending_by_prefix[dst][0]
                    tid = first["id"] or f"TSK-{dst}-???"
                    suggestions.append({
                        "title": f"Desbloqueo: {dst} listo tras {src}",
                        "reason": f"{src} se completó y desbloquea {dst}.",
                        "action": f"@quinotospec.apply {tid}",
                        "confidence": "Alta",
                        "priority_order": 2,
                    })

    # REGLA 5: Prioridad + Velocidad
    # Find pending proposals with P1
    p1_slugs = [s for s, p in prio_map.items() if p == "P1"]
    p1_pending = []
    for slug in p1_slugs:
        # Check if any pending task file belongs to this slug
        for entry in all_pending:
            if slug in entry["file"]:
                p1_pending.append(entry)
                break
    if p1_pending:
        if velocity in ("alta", "media"):
            first = p1_pending[0]
            tid = first["id"] or "TSK-???-001"
            suggestions.append({
                "title": f"Avanzar P1: {first['file'].split('/')[2] if '/' in first['file'] else first['prefix']}",
                "reason": f"Hay tareas P1 pendientes y tu velocidad es {velocity}. Priorizar lo crítico.",
                "action": f"@quinotospec.apply {tid}",
                "confidence": "Alta" if velocity == "alta" else "Media",
                "priority_order": 2,
            })
        else:
            suggestions.append({
                "title": f"Dividir P1 pendiente (velocidad baja)",
                "reason": f"Velocidad actual {velocity}. Considera dividir tareas P1 en chunks más pequeños.",
                "action": "@quinotospec.create-tasks --help",
                "confidence": "Media",
                "priority_order": 5,
            })

    # If still no suggestions and we have pending tasks, add generic
    if not suggestions and all_pending:
        # Use first pending
        first = all_pending[0]
        tid = first["id"] or "TSK-???-001"
        prefix = first["prefix"]
        suggestions.append({
            "title": f"Continuar con {prefix}",
            "reason": f"Tienes {len(all_pending)} tasks pendientes.",
            "action": f"@quinotospec.apply {tid}",
            "confidence": "Media",
            "priority_order": 10,
        })

    # If still none and no pending but proposals exist, suggest create proposal
    if not suggestions and not all_pending:
        suggestions.append({
            "title": "Proyecto sin tasks pendientes",
            "reason": "No se encontraron tareas pendientes. ¿Nuevo feature?",
            "action": "@quinotospec.create-proposal nueva-feature",
            "confidence": "Baja",
            "priority_order": 10,
        })

    # Sort by priority_order then confidence
    def conf_rank(c):
        return {"Alta": 0, "Media": 1, "Baja": 2}.get(c, 2)
    suggestions.sort(key=lambda s: (s["priority_order"], conf_rank(s["confidence"])))

    return suggestions, alerts


def generate_markdown(analysis, suggestions, alerts, limit):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    days_since = analysis.get("days_since_last_activity")
    last_activity_str = f"hace {days_since} días" if days_since is not None else "sin registro"
    cold_start = analysis.get("cold_start", False)

    category = analysis.get("category_pattern", {})
    progress = analysis.get("progress_pattern", {})
    sprint = analysis.get("sprint_pattern", {})
    temporal = analysis.get("temporal_pattern", {})

    top_prefix = category.get("top_prefixes", [])
    area_principal = top_prefix[0] if top_prefix else "N/D"
    avg_tasks = progress.get("avg_tasks_per_session", 0)
    completed = progress.get("completed_tasks", 0)
    total = progress.get("total_tasks", 0)
    context_switch = category.get("context_switch_rate", "bajo")

    md = []
    md.append("# 🩸 Blood-Bond: Sugerencias Proactivas")
    md.append("")
    md.append(f"**Generado**: {now}")
    md.append(f"**Última actividad**: {last_activity_str}")
    md.append("")
    if cold_start:
        md.append("> ⚠️ **Cold Start**: Menos de 5 entradas en el changelog. Necesito más historial para predicciones precisas. Sugerencias limitadas.")
        md.append("")
    md.append("---")
    md.append("")
    md.append("## 🔥 Sugerencias Inmediatas")
    md.append("")

    if not suggestions:
        md.append("No hay sugerencias por ahora. ¡Proyecto al día!")
        md.append("")
    else:
        for i, s in enumerate(suggestions[:limit], 1):
            conf_str = confidence_bars(s["confidence"])
            md.append(f"### {i}. {s['title']} (Confianza: {conf_str})")
            md.append("")
            md.append(f"**Razón**: {s['reason']}")
            md.append("")
            md.append(f"**Acción sugerida**:")
            md.append("```")
            md.append(s["action"])
            md.append("```")
            md.append("")

    md.append("---")
    md.append("")
    md.append("## ⚠️ Alertas")
    md.append("")
    if not alerts and not progress.get("stagnant_proposals"):
        md.append("Ninguna (proyecto activo)")
        md.append("")
    else:
        if alerts:
            md.append("### 🚨 Estancamiento Detectado")
            for a in alerts:
                md.append(f"**Propuesta**: `{a['proposal']}`")
                md.append(f"- {a['reason']}")
                md.append(f"- **Prioridad**: {a['priority']}")
                md.append(f"- **Recomendación**: {a['action']}")
                md.append("")
        # Also list stagnant from analysis if not already in alerts
        stagnant = progress.get("stagnant_proposals", [])
        if stagnant:
            for slug in stagnant:
                if not any(a["proposal"] == slug for a in alerts):
                    md.append(f"**Propuesta**: `{slug}`")
                    md.append(f"- Sin avance en **>=14 días**")
                    md.append(f"- **Recomendación**: Completar o archivar")
                    md.append("")

    md.append("---")
    md.append("")
    md.append("## 📊 Tu Perfil de Trabajo")
    md.append("")
    md.append("| Métrica | Valor |")
    md.append("|---------|-------|")
    md.append(f"| Última actividad | {last_activity_str} |")
    md.append(f"| Área principal | {area_principal} |")
    md.append(f"| Velocidad típica | {avg_tasks} tasks/sesión |")
    md.append(f"| Context switch | {context_switch} |")
    md.append(f"| Total completado | {completed} / {total} tasks |")
    md.append(f"| Día más activo | {temporal.get('most_active_day', 'N/D')} |")
    md.append(f"| Frecuencia | {temporal.get('work_frequency', 'N/D')} |")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 🧠 Insights")
    md.append("")
    if top_prefix:
        md.append(f"- **Patrón**: Tu área principal es **{area_principal}** ({category.get('distribution', {}).get(area_principal, '?')}%).")
    if progress.get("stagnant_proposals"):
        md.append(f"- **Estancamiento**: {len(progress['stagnant_proposals'])} propuesta(s) sin avance >=14 días.")
    if progress.get("completion_rate", 0) > 0:
        md.append(f"- **Progreso**: {progress['completion_rate']}% completado.")
    if not top_prefix and not progress.get("stagnant_proposals"):
        md.append("- **Patrón**: Historial limitado — seguí trabajando para que Blood-Bond aprenda tu ritmo.")
    md.append("- **Recomendación**: Usa `@quinotospec.apply` para continuar con la siguiente task sugerida.")
    md.append("")

    md.append("---")
    md.append("")
    md.append("*💡 Blood-Bond analiza tu historial para predecir qué necesitas a continuación.*")
    md.append("*Para re-generar: `@quinotospec.blood-bond --suggest`*")
    md.append("")

    return "\n".join(md)


def main():
    root, rest = resolve_root(sys.argv[1:])
    force, limit = parse_args(rest)

    blood_dir = root / ".quinoto-spec" / "blood-bond"
    analysis_path = blood_dir / "analysis.json"
    suggestions_path = blood_dir / "suggestions.md"

    if not analysis_path.exists():
        print(f"Blood-Bond Predictor: no existe {analysis_path} — ejecuta analyzer primero (quinotospec-blood-bond-analyzer)")
        sys.exit(1)

    if suggestions_path.exists() and not force:
        # Overwrite anyway but note
        pass

    analysis, err = load_analysis(root)
    if err:
        print(f"Error leyendo analysis.json: {err}")
        sys.exit(1)

    pending_by_prefix, all_pending = find_pending_tasks(root)
    prio_map = find_proposal_priorities(root)

    suggestions, alerts = generate_suggestions(analysis, pending_by_prefix, all_pending, prio_map)

    # Limit handling for cold start: if cold_start, limit to 1-2?
    if analysis.get("cold_start"):
        # Still respect limit but ensure at least basic suggestion
        pass

    md_content = generate_markdown(analysis, suggestions, alerts, limit)

    blood_dir.mkdir(parents=True, exist_ok=True)
    suggestions_path.write_text(md_content, encoding="utf-8")

    print(f"Blood-Bond Predictor: {len(suggestions)} sugerencias, {len(alerts)} alertas -> {suggestions_path}")
    if analysis.get("cold_start"):
        print("  Cold start: sugerencias básicas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
