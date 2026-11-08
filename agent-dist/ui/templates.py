#!/usr/bin/env python3
"""templates -- render HTML server-side para la UI (sin dependencias externas)."""

import html
import re

STATUS_LABELS = {
    "proposed": "Propuesta",
    "in_progress": "En curso",
    "completed": "Completada",
    "archived": "Archivada",
    "pending": "Pendiente",
    "blocked": "Bloqueada",
    "cancelled": "Cancelada",
    "unknown": "N/D",
}

NAV = (
    ("/", "Panel", "dashboard"),
    ("/projects", "Proyectos", "projects"),
    ("/proposals", "Propuestas", "proposals"),
    ("/tasks", "Tareas", "tasks"),
    ("/changelog", "Changelog", "changelog"),
    ("/discovery", "Discovery", "discovery"),
    ("/constitution", "Constitución", "constitution"),
    ("/specs", "Specs", "specs"),
    ("/evidence", "Evidencia", "evidence"),
    ("/gates", "Gates", "gates"),
)

STYLE = """
:root {
  --bg: #0f1419; --panel: #171d24; --panel2: #1e2630; --border: #2a3542;
  --text: #d7e0ea; --muted: #8b9bb0; --accent: #5cc8ff; --accent2: #7ee787;
  --warn: #e3b341; --danger: #f47067; --ok: #7ee787;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 14px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
header { display: flex; align-items: center; gap: 24px; padding: 14px 28px;
  background: var(--panel); border-bottom: 1px solid var(--border); position: sticky; top: 0; }
.brand { font-weight: 700; letter-spacing: .5px; color: #fff; }
.brand span { color: var(--accent); }
nav { display: flex; gap: 4px; flex-wrap: wrap; }
nav a { padding: 6px 12px; border-radius: 8px; color: var(--muted); }
nav a.active, nav a:hover { background: var(--panel2); color: var(--text); text-decoration: none; }
main { max-width: 1180px; margin: 0 auto; padding: 28px; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 16px; margin: 28px 0 12px; color: #fff; }
h3 { font-size: 14px; margin: 0 0 8px; }
.sub { color: var(--muted); margin: 0 0 18px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.card .num { font-size: 26px; font-weight: 700; color: #fff; }
.card .lbl { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .6px; }
table { width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }
th { background: var(--panel2); color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
tr:last-child td { border-bottom: none; }
.badge { display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 11px; font-weight: 600; border: 1px solid; white-space: nowrap; }
.s-proposed { color: var(--warn); border-color: var(--warn); background: rgba(227,179,65,.12); }
.s-in_progress { color: var(--accent); border-color: var(--accent); background: rgba(92,200,255,.12); }
.s-completed { color: var(--ok); border-color: var(--ok); background: rgba(126,231,135,.12); }
.s-archived { color: var(--muted); border-color: var(--muted); background: rgba(139,155,176,.12); }
.s-pending { color: var(--muted); border-color: var(--border); background: rgba(139,155,176,.08); }
.s-blocked, .s-cancelled { color: var(--danger); border-color: var(--danger); background: rgba(244,112,103,.12); }
.s-unknown { color: var(--muted); border-color: var(--border); }
.kanban { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.column { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 12px; min-height: 120px; }
.column h3 { display: flex; justify-content: space-between; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
.task { background: var(--panel2); border: 1px solid var(--border); border-radius: 8px; padding: 10px; margin-bottom: 8px; }
.task .id { color: var(--accent); font-size: 12px; font-weight: 600; }
.task .meta { color: var(--muted); font-size: 12px; margin-top: 4px; }
.empty { color: var(--muted); text-align: center; padding: 22px; }
.alert { border-radius: 10px; padding: 12px 14px; margin-bottom: 14px; border: 1px solid; }
.alert.warn { color: var(--warn); border-color: var(--warn); background: rgba(227,179,65,.08); }
.alert.ok { color: var(--ok); border-color: var(--ok); background: rgba(126,231,135,.08); }
.timeline { border-left: 2px solid var(--border); margin-left: 6px; padding-left: 18px; }
.entry { position: relative; padding: 0 0 18px; }
.entry::before { content: ""; position: absolute; left: -25px; top: 5px; width: 9px; height: 9px; border-radius: 50%; background: var(--accent); }
.entry .date { color: var(--muted); font-size: 12px; }
.entry ul { margin: 6px 0 0; padding-left: 18px; color: var(--muted); }
pre { background: var(--panel2); border: 1px solid var(--border); border-radius: 10px; padding: 14px; overflow: auto; white-space: pre-wrap; }
footer { color: var(--muted); font-size: 12px; text-align: center; padding: 24px; }
.two { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }
@media (max-width: 900px) { .kanban { grid-template-columns: 1fr 1fr; } .two { grid-template-columns: 1fr; } }
body.light {
  --bg: #f4f7fa; --panel: #ffffff; --panel2: #eef2f7; --border: #d5dde6;
  --text: #1a2330; --muted: #5a6b80; --accent: #0066cc; --accent2: #1f8a3a;
  --warn: #9a6700; --danger: #c0392b; --ok: #1f8a3a;
}
.theme-toggle { padding: 6px 10px; border-radius: 8px; border: 1px solid var(--border); background: var(--panel2); color: var(--text); cursor: pointer; font-size: 12px; }
.md-content { line-height: 1.6; }
.md-content h1, .md-content h2, .md-content h3, .md-content h4 { color: var(--text); margin: 18px 0 8px; }
.md-content h1 { font-size: 20px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
.md-content h2 { font-size: 17px; }
.md-content h3 { font-size: 15px; }
.md-content p { margin: 8px 0; }
.md-content ul, .md-content ol { margin: 8px 0; padding-left: 22px; }
.md-content li { margin: 4px 0; }
.md-content code { background: var(--panel2); padding: 1px 6px; border-radius: 4px; font-size: 12px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.md-content pre { background: var(--panel2); padding: 12px; border-radius: 8px; overflow-x: auto; }
.md-content pre code { background: none; padding: 0; }
.md-content blockquote { border-left: 3px solid var(--accent); padding-left: 12px; color: var(--muted); margin: 8px 0; }
.md-content hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
.md-content table { width: 100%; border-collapse: collapse; margin: 10px 0; }
.md-content th, .md-content td { padding: 8px 10px; border: 1px solid var(--border); }
.md-content th { background: var(--panel2); }
.md-content a { color: var(--accent); }
"""


def esc(value):
    return html.escape(str(value if value is not None else ""))


def badge(status, label=None):
    status = status or "unknown"
    return '<span class="badge s-%s">%s</span>' % (esc(status), esc(label or STATUS_LABELS.get(status, status)))


def layout(title, active, content, project_name="", projects=None, selected_project=""):
    links = []
    for href, label, key in NAV:
        cls = ' class="active"' if key == active else ""
        links.append('<a href="%s"%s>%s</a>' % (href, cls, esc(label)))
    selector = ""
    if projects and len(projects) > 1:
        options = ['<option value="">Todos los proyectos</option>']
        for project in projects:
            name = project["name"]
            selected = " selected" if name == selected_project else ""
            options.append('<option value="%s"%s>%s</option>' % (esc(name), selected, esc(name)))
        selector = (
            '<select onchange="var u=new URL(location.href);'
            'if(this.value) u.searchParams.set(\'project\',this.value);'
            'else u.searchParams.delete(\'project\'); location.href=u.toString();"'
            ' style="margin-right:8px;background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:4px 8px;">'
            '%s</select>' % "".join(options)
        )
    header_right = selector + esc(project_name)
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s · QuinotoSpec UI</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <div class="brand">Quinoto<span>Spec</span> UI</div>
  <nav>%s</nav>
  <div style="margin-left:auto;display:flex;align-items:center;gap:8px;color:var(--muted)">%s<button class="theme-toggle" onclick="toggleTheme()" id="theme-btn">Tema</button></div>
</header>
<main>
%s
</main>
<footer>Read-only · %s</footer>
<script>
(function(){var t=localStorage.getItem('qs-theme');if(t==='light')document.body.classList.add('light');})();
function toggleTheme(){var b=document.body;b.classList.toggle('light');localStorage.setItem('qs-theme',b.classList.contains('light')?'light':'dark');}
</script>
</body>
</html>""" % (
        esc(title),
        "".join(links),
        header_right,
        content,
        esc(project_name),
    )


def _cards(summary):
    counts = summary["counts"]
    by_status = counts["tasks_by_status"]
    cards = [
        ("Propuestas activas", counts["proposals_active"]),
        ("User stories", counts["stories"]),
        ("Tareas", counts["tasks"]),
        ("Completadas", by_status.get("completed", 0)),
        ("Entradas de changelog", counts["changelog"]),
        ("Con evidencia", counts["evidence"]),
    ]
    items = "".join(
        '<div class="card"><div class="num">%s</div><div class="lbl">%s</div></div>' % (esc(value), esc(label))
        for label, value in cards
    )
    return '<div class="grid">%s</div>' % items


def _alerts(summary):
    alerts = []
    discovery = summary["discovery"]
    if not discovery["present"]:
        alerts.append(('warn', "No hay discovery: ejecuta <code>@quinotospec.discovery</code>."))
    elif discovery["stale"]:
        alerts.append(('warn', "Discovery con %s días de antigüedad: considera <code>@quinotospec.refresh-discovery</code>." % discovery["age_days"]))
    if not summary["constitution"]["present"]:
        alerts.append(('warn', "Sin constitución activa: los gates constitucionales quedan en advertencia."))
    pending = summary["counts"]["tasks_by_status"].get("pending", 0)
    blocked = summary["counts"]["tasks_by_status"].get("blocked", 0)
    if blocked:
        alerts.append(('warn', "%s tarea(s) bloqueada(s)." % blocked))
    if not alerts:
        alerts.append(('ok', "Sin alertas: discovery fresco, constitución presente y sin tareas bloqueadas."))
    return "".join('<div class="alert %s">%s</div>' % (kind, text) for kind, text in alerts)


def dashboard(summary):
    show_project = bool(summary.get("multi") and not summary.get("selected_project"))
    rows = []
    for proposal in summary["proposals"]:
        counts = proposal["task_counts"]
        cells = []
        if show_project:
            cells.append("<td>%s</td>" % esc(proposal.get("project", "")))
        cells.append('<td><a href="/proposals/%s">%s</a></td>' % (esc(proposal["slug"]), esc(proposal["title"])))
        cells.append("<td>%s</td>" % badge(proposal["status"]))
        cells.append("<td>%s</td>" % esc(proposal["prefix"]))
        cells.append("<td>%s</td>" % esc(proposal["priority"]))
        cells.append("<td>%s</td>" % esc(proposal["complexity"]))
        cells.append("<td>%s/%s</td>" % (counts.get("completed", 0), len(proposal["tasks"])))
        rows.append("<tr>%s</tr>" % "".join(cells))
    header_cells = []
    if show_project:
        header_cells.append("<th>Proyecto</th>")
    header_cells += ["<th>Propuesta</th>", "<th>Estado</th>", "<th>Prefijo</th>", "<th>Prioridad</th>", "<th>Complejidad</th>", "<th>Tareas</th>"]
    table = (
        "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % ("".join(header_cells), "".join(rows))
        if rows
        else '<div class="card empty">No hay propuestas en este proyecto.</div>'
    )
    title = summary["name"] or "Proyecto"
    if summary.get("multi") and summary.get("selected_project"):
        title = "%s · %s" % (title, summary["selected_project"])
    return (
        "<h1>%s</h1><p class=\"sub\">Panel de estado · read-only</p>%s%s<h2>Propuestas</h2>%s"
        % (esc(title), _alerts(summary), _cards(summary), table)
    )


def proposals_page(summary, q=""):
    show_project = bool(summary.get("multi") and not summary.get("selected_project"))
    needle = (q or "").strip().lower()
    filtered = []
    for proposal in summary["proposals"]:
        haystack = " ".join(
            [
                proposal.get("title", ""),
                proposal.get("slug", ""),
                proposal.get("prefix", ""),
                proposal.get("priority", ""),
                " ".join(proposal.get("services", [])),
            ]
        ).lower()
        if needle and needle not in haystack:
            continue
        filtered.append(proposal)

    rows = []
    for proposal in filtered:
        cells = []
        if show_project:
            cells.append("<td>%s</td>" % esc(proposal.get("project", "")))
        cells.append('<td><a href="/proposals/%s">%s</a></td>' % (esc(proposal["slug"]), esc(proposal["title"])))
        cells.append("<td>%s</td>" % badge(proposal["status"]))
        cells.append("<td>%s</td>" % esc(proposal["prefix"]))
        cells.append("<td>%s</td>" % esc(proposal["date"]))
        cells.append("<td>%s</td>" % esc(proposal["priority"]))
        cells.append("<td>%s</td>" % esc(", ".join(proposal["services"])))
        cells.append("<td>%s</td>" % ("sí" if proposal["archived"] else "no"))
        rows.append("<tr>%s</tr>" % "".join(cells))
    header_cells = []
    if show_project:
        header_cells.append("<th>Proyecto</th>")
    header_cells += ["<th>Propuesta</th>", "<th>Estado</th>", "<th>Prefijo</th>", "<th>Fecha</th>", "<th>Prioridad</th>", "<th>Servicios</th>", "<th>Archivada</th>"]
    table = (
        "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % ("".join(header_cells), "".join(rows))
        if rows
        else '<div class="card empty">No hay propuestas.</div>'
    )
    search = (
        '<form method="get" style="margin-bottom:12px;display:flex;gap:8px;">'
        '<input name="q" value="%s" placeholder="Buscar propuestas..." style="flex:1;padding:8px;border-radius:8px;border:1px solid var(--border);background:var(--panel2);color:var(--text);">'
        '<button type="submit" style="padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:var(--panel2);color:var(--text);cursor:pointer;">Buscar</button>'
        '</form>' % esc(q)
    )
    return "<h1>Propuestas</h1><p class=\"sub\">%s propuesta(s)%s</p>%s%s" % (
        len(filtered),
        (" (filtro: %s)" % esc(q)) if q else "",
        search,
        table,
    )


def proposal_page(proposal):
    stories = []
    for story in proposal["stories"]:
        stories.append("<tr><td>%s</td><td>%s</td></tr>" % (esc(story["id"]), esc(story["title"])))
    stories_table = (
        "<table><thead><tr><th>Story</th><th>Título</th></tr></thead><tbody>%s</tbody></table>" % "".join(stories)
        if stories
        else '<div class="card empty">Sin user stories.</div>'
    )
    tasks = []
    for task in proposal["tasks"]:
        evidence = ", ".join(task["evidence"]) if task["evidence"] else "—"
        tasks.append(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(task["id"]), esc(task["title"]), badge(task["status"]), esc(task["story"]), esc(task["files"]), esc(evidence))
        )
    tasks_table = (
        "<table><thead><tr><th>ID</th><th>Título</th><th>Estado</th><th>Story</th><th>Archivos</th><th>Evidencia</th></tr></thead><tbody>%s</tbody></table>" % "".join(tasks)
        if tasks
        else '<div class="card empty">Sin tareas registradas (*_tasks.md).</div>'
    )
    services = ", ".join(proposal["services"]) or "—"
    meta = (
        '<div class="card"><h3>Metadatos</h3>'
        "<p><strong>Estado:</strong> %s</p>"
        "<p><strong>Prefijo:</strong> %s</p>"
        "<p><strong>Fecha:</strong> %s</p>"
        "<p><strong>Prioridad:</strong> %s</p>"
        "<p><strong>Complejidad:</strong> %s</p>"
        "<p><strong>Servicios:</strong> %s</p>"
        "<p><strong>Delta specs:</strong> %s</p>"
        "<p><strong>Ruta:</strong> <code>%s</code></p></div>"
    ) % (
        badge(proposal["status"]),
        esc(proposal["prefix"] or "—"),
        esc(proposal["date"] or "—"),
        esc(proposal["priority"] or "—"),
        esc(proposal["complexity"] or "—"),
        esc(services),
        "sí" if proposal["has_delta_specs"] else "no",
        esc(proposal["path"]),
    )
    return (
        '<h1>%s</h1><p class="sub"><a href="/proposals">← Propuestas</a> · %s</p>'
        '<div class="two"><div><h2>User stories</h2>%s<h2>Tareas</h2>%s</div><div>%s</div></div>'
        % (esc(proposal["title"]), esc(proposal["slug"]), stories_table, tasks_table, meta)
    )


def tasks_page(summary, q=""):
    columns = (
        ("pending", "Pendientes"),
        ("in_progress", "En curso"),
        ("blocked", "Bloqueadas"),
        ("completed", "Completadas"),
    )
    needle = (q or "").strip().lower()
    all_tasks = [(proposal, task) for proposal in summary["proposals"] for task in proposal["tasks"]]
    if needle:
        filtered = []
        for proposal, task in all_tasks:
            haystack = " ".join([task.get("id", ""), task.get("title", ""), task.get("story", ""), task.get("files", "")]).lower()
            if needle in haystack:
                filtered.append((proposal, task))
        all_tasks = filtered

    show_project = bool(summary.get("multi") and not summary.get("selected_project"))
    rendered = []
    for status, label in columns:
        items = []
        count = 0
        for proposal, task in all_tasks:
            if task["status"] != status:
                continue
            count += 1
            meta = esc(proposal["title"])
            if show_project:
                meta = "%s · %s" % (esc(proposal.get("project", "")), meta)
            meta = "%s · %s" % (meta, esc(task["story"] or "sin story"))
            items.append(
                '<div class="task"><div class="id"><a href="/tasks/%s">%s</a></div><div>%s</div>'
                '<div class="meta">%s</div></div>'
                % (esc(task["id"]), esc(task["id"]), esc(task["title"]), meta)
            )
        if not items:
            items.append('<div class="empty">Sin tareas</div>')
        rendered.append(
            '<div class="column"><h3><span>%s</span><span>%s</span></h3>%s</div>'
            % (esc(label), count, "".join(items))
        )
    search = (
        '<form method="get" style="margin-bottom:12px;display:flex;gap:8px;">'
        '<input name="q" value="%s" placeholder="Buscar tareas..." style="flex:1;padding:8px;border-radius:8px;border:1px solid var(--border);background:var(--panel2);color:var(--text);">'
        '<button type="submit" style="padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:var(--panel2);color:var(--text);cursor:pointer;">Buscar</button>'
        '</form>' % esc(q)
    )
    return "<h1>Tareas</h1><p class=\"sub\">Vista kanban multi-propuesta%s</p>%s<div class=\"kanban\">%s</div>" % (
        (" (filtro: %s)" % esc(q)) if q else "",
        search,
        "".join(rendered),
    )


def changelog_page(summary):
    entries = []
    show_project = bool(summary.get("multi") and not summary.get("selected_project"))
    for entry in summary["changelog"]:
        bullets = "".join("<li>%s</li>" % esc(line) for line in entry["summary"])
        meta_parts = []
        if show_project:
            meta_parts.append(entry.get("project", ""))
        meta_parts += [entry["prefix"], entry["type"], entry["format"]]
        meta = " · ".join(part for part in meta_parts if part)
        saved = "<div class=\"meta\">Tiempo ahorrado: %s</div>" % esc(entry["time_saved"]) if entry["time_saved"] else ""
        entries.append(
            '<div class="entry"><div class="date">%s · %s</div><h3>%s</h3><ul>%s</ul>%s</div>'
            % (esc(entry["date"]), esc(meta), esc(entry["title"]), bullets, saved)
        )
    body = '<div class="timeline">%s</div>' % "".join(entries) if entries else '<div class="card empty">Changelog vacío.</div>'
    return "<h1>Changelog</h1><p class=\"sub\">%s entrada(s)</p>%s" % (len(summary["changelog"]), body)


def discovery_page(summary):
    discovery = summary["discovery"]
    rows = []
    for item in discovery["files"]:
        rows.append(
            "<tr><td><a href=\"/discovery/%s\">%s</a></td><td>%s</td><td>%s bytes</td></tr>"
            % (esc(item["name"]), esc(item["name"]), esc(item["date"]), esc(item["size"]))
        )
    table = (
        "<table><thead><tr><th>Archivo</th><th>Fecha</th><th>Tamaño</th></tr></thead><tbody>%s</tbody></table>" % "".join(rows)
        if rows
        else '<div class="card empty">Sin discovery: ejecuta @quinotospec.discovery.</div>'
    )
    age = "desconocida"
    if discovery["age_days"] is not None:
        age = "%s días" % discovery["age_days"]
    alert = (
        '<div class="alert warn">Discovery obsoleto: %s (límite 30 días).</div>' % esc(age)
        if discovery["stale"]
        else '<div class="alert ok">Discovery fresco: %s.</div>' % esc(age)
    )
    return "<h1>Discovery</h1><p class=\"sub\">%s archivo(s) · fecha del proyecto: %s</p>%s%s" % (
        len(discovery["files"]),
        esc(discovery["project_date"] or "—"),
        alert,
        table,
    )


def task_page(task, proposal):
    evidence = task.get("evidence") or []
    evidence_items = "".join("<li>%s</li>" % esc(name) for name in evidence) if evidence else "<li>—</li>"
    meta = (
        '<div class="card"><h3>Metadatos</h3>'
        "<p><strong>ID:</strong> %s</p>"
        "<p><strong>Título:</strong> %s</p>"
        "<p><strong>Estado:</strong> %s</p>"
        "<p><strong>Story:</strong> %s</p>"
        "<p><strong>Archivos:</strong> %s</p>"
        "<p><strong>Dependencias:</strong> %s</p>"
        "<p><strong>Propuesta:</strong> <a href=\"/proposals/%s\">%s</a></p>"
        "<p><strong>Evidencia (%s):</strong></p><ul>%s</ul></div>"
    ) % (
        esc(task.get("id", "")),
        esc(task.get("title", "")),
        badge(task.get("status", "unknown")),
        esc(task.get("story", "") or "—"),
        esc(task.get("files", "") or "—"),
        esc(task.get("deps", "") or "—"),
        esc(proposal.get("slug", "")),
        esc(proposal.get("title", "")),
        len(evidence),
        evidence_items,
    )
    return '<h1>%s</h1><p class="sub"><a href="/tasks">← Tareas</a> · %s</p><div class="two"><div>%s</div></div>' % (
        esc(task.get("id", "")),
        esc(proposal.get("title", "")),
        meta,
    )


def projects_page(summary):
    if summary.get("multi"):
        projects = summary.get("projects", [])
    else:
        projects = [summary]
    rows = []
    for project in projects:
        counts = project["counts"]
        name = project["name"]
        link = "/?project=%s" % esc(name) if summary.get("multi") else "/"
        rows.append(
            "<tr><td><a href=\"%s\">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                link,
                esc(name),
                counts.get("proposals", 0),
                counts.get("tasks", 0),
                counts.get("tasks_by_status", {}).get("completed", 0),
                counts.get("changelog", 0),
                "sí" if project.get("initialized") else "no",
            )
        )
    table = (
        "<table><thead><tr><th>Proyecto</th><th>Propuestas</th><th>Tareas</th><th>Completadas</th><th>Changelog</th><th>Inicializado</th></tr></thead><tbody>%s</tbody></table>" % "".join(rows)
        if rows
        else '<div class="card empty">Sin proyectos.</div>'
    )
    return "<h1>Proyectos</h1><p class=\"sub\">%s proyecto(s) · read-only</p>%s" % (len(projects), table)


def _inline_markdown(text):
    # codigo inline
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # negrita
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # italica
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # enlaces
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text


def _is_block_start(stripped):
    if stripped == "":
        return True
    if stripped.startswith("```"):
        return True
    if re.match(r"^#{1,6}\s", stripped):
        return True
    if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
        return True
    if stripped.startswith(">"):
        return True
    if re.match(r"^[-*+]\s", stripped):
        return True
    if re.match(r"^\d+\.\s", stripped):
        return True
    return False


def render_markdown(text):
    lines = (text or "").splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        if stripped == "":
            i += 1
            continue
        if stripped.startswith("```"):
            lang = stripped[3:].strip().lower()
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code = "\n".join(code_lines)
            if lang == "mermaid":
                out.append('<div class="mermaid">%s</div>' % html.escape(code))
            else:
                out.append("<pre><code>%s</code></pre>" % html.escape(code))
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, _inline_markdown(html.escape(m.group(2))), level))
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            out.append("<hr>")
            i += 1
            continue
        if stripped.startswith(">"):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(_inline_markdown(html.escape(l)) for l in quote_lines))
            continue
        if re.match(r"^[-*+]\s", stripped):
            items = []
            while i < n and re.match(r"^[-*+]\s", lines[i].strip()):
                items.append(re.sub(r"^[-*+]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % _inline_markdown(html.escape(it)) for it in items))
            continue
        if re.match(r"^\d+\.\s", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % _inline_markdown(html.escape(it)) for it in items))
            continue
        # tabla simple (opcional)
        if "|" in stripped and i + 1 < n and re.match(r"^\|?[\s\-:|]+\|?$", lines[i + 1].strip()):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            head_html = "".join("<th>%s</th>" % _inline_markdown(html.escape(h)) for h in header)
            body_html = "".join(
                "<tr>%s</tr>" % "".join("<td>%s</td>" % _inline_markdown(html.escape(c)) for c in row) for row in rows
            )
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (head_html, body_html))
            continue
        para = []
        while i < n and lines[i].strip() != "" and not _is_block_start(lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        if para:
            out.append("<p>%s</p>" % _inline_markdown(html.escape(" ".join(para))))
            continue
        i += 1
    return "\n".join(out)


def _mermaid_lazy_script():
    return (
        '<script async src="/static/mermaid.min.js" onload="window.__mermaidReady=true;if(window.__mermaidInit)window.__mermaidInit();"></script>'
        '<script>var __mermaidLoaded=false;function __loadMermaid(){if(__mermaidLoaded||window.__mermaidReady)window.__mermaidInit&&window.__mermaidInit();else{var s=document.createElement("link");s.rel="preload";s.as="script";s.href="/static/mermaid.min.js";document.head.appendChild(s);setTimeout(function(){if(window.__mermaidReady)window.__mermaidInit&&window.__mermaidInit();},800);}}'
        'window.__mermaidInit=function(){try{if(!window.mermaid)return;mermaid.initialize({startOnLoad:false,theme:document.body.classList.contains("light")?"default":"dark"});document.querySelectorAll("div.mermaid").forEach(function(el){try{mermaid.run({nodes:[el]});}catch(e){}});}catch(e){}};'
        'window.addEventListener("load",function(){var blocks=document.querySelectorAll("div.mermaid");if(!blocks.length)return;if("IntersectionObserver"in window){var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){__loadMermaid();io.disconnect();}});});blocks.forEach(function(b){io.observe(b);});}else{__loadMermaid();}});</script>'
    )


def discovery_file_page(data):
    name = data["name"]
    content = data["content"]
    has_mermaid = 'class="mermaid"' in render_markdown(content)
    script = _mermaid_lazy_script() if has_mermaid else ""
    return (
        "<h1>Discovery · %s</h1><p class=\"sub\"><a href=\"/discovery\">← Discovery</a></p>"
        '<div class="card md-content">%s</div>%s'
        % (esc(name), render_markdown(content), script)
    )


def constitution_page(constitution):
    if not constitution["present"]:
        return '<h1>Constitución</h1><div class="alert warn">No existe <code>.quinoto-spec/constitution.md</code>. Ejecuta <code>@quinotospec.constitution</code>.</div>'
    principles = []
    for principle in constitution["principles"]:
        principles.append("<tr><td>%s</td><td>%s</td></tr>" % (esc(principle["id"]), esc(principle["text"])))
    table = (
        "<table><thead><tr><th>ID</th><th>Principio</th></tr></thead><tbody>%s</tbody></table>" % "".join(principles)
        if principles
        else '<div class="card empty">Sin principios detectados.</div>'
    )
    status = badge(constitution["status"]) if constitution["status"] in STATUS_LABELS else esc(constitution["status_raw"] or "—")
    return (
        "<h1>Constitución</h1><p class=\"sub\">Estado: %s</p>%s"
        '<details><summary>Ver documento completo</summary><div class="card md-content">%s</div></details>'
        % (status, table, render_markdown(constitution["content"]))
    )


def specs_page(summary):
    specs = summary.get("specs") or {"present": False, "domains": []}
    if not specs["present"]:
        return '<h1>Specs</h1><div class="alert warn">No existe <code>.quinoto-spec/specs/</code>. Ejecuta <code>@quinotospec.specs-init</code>.</div>'
    rows = []
    for d in specs["domains"]:
        rows.append(
            "<tr><td><a href=\"/specs/%s\">%s</a></td><td>%s</td><td>%s</td><td>%s bytes</td></tr>"
            % (esc(d["domain"]), esc(d["title"]), esc(d["domain"]), esc(d["req_count"]), esc(d["size"]))
        )
    table = (
        "<table><thead><tr><th>Spec</th><th>Dominio</th><th>Requirements</th><th>Tamaño</th></tr></thead><tbody>%s</tbody></table>" % "".join(rows)
        if rows
        else '<div class="card empty">Sin dominios de specs.</div>'
    )
    return "<h1>Specs consolidados</h1><p class=\"sub\">%s dominio(s)</p>%s" % (len(specs["domains"]), table)


def spec_file_page(data):
    return (
        "<h1>Spec · %s</h1><p class=\"sub\"><a href=\"/specs\">← Specs</a></p>"
        '<div class="card md-content">%s</div>%s' % (esc(data["domain"]), render_markdown(data["content"]), _mermaid_lazy_script() if "class=\"mermaid\"" in render_markdown(data["content"]) else "")
    )


def evidence_page(summary):
    ev = summary.get("evidence_all") or {"present": False, "items": []}
    if not ev["present"]:
        return '<h1>Evidencia</h1><div class="card empty">Sin evidencia (<code>.quinoto-spec/evidence/</code> vacío).</div>'
    steps = []
    for item in ev["items"]:
        files = []
        for f in item["files"]:
            files.append("<li>%s</li>" % esc(f["name"]))
        steps.append("<div class=\"card\"><h3>%s</h3><ul>%s</ul></div>" % (esc(item["task_id"]), "".join(files)))
    body = '<div class="grid">%s</div>' % "".join(steps) if steps else '<div class="card empty">Sin items.</div>'
    return "<h1>Evidencia</h1><p class=\"sub\">%s tarea(s) con evidencia</p>%s" % (len(ev["items"]), body)


def gates_page(summary):
    gates = summary.get("gates") or {"present": True, "tasks": []}
    rows = []
    for t in gates["tasks"]:
        cells = []
        for g in t["gates"]:
            cells.append("<td>%s</td>" % ("✅" if g["present"] else "⬜"))
        rows.append("<tr><td>%s</td><td>%s</td>%s</tr>" % (esc(t["task_id"]), esc(t["proposal"]), "".join(cells)))
    table = (
        "<table><thead><tr><th>Tarea</th><th>Propuesta</th><th>TDD</th><th>Debug</th><th>Verify</th></tr></thead><tbody>%s</tbody></table>" % "".join(rows)
        if rows
        else '<div class="card empty">Sin tareas para auditar gates.</div>'
    )
    return "<h1>Gates</h1><p class=\"sub\">Evidencia fresca por tarea (✅ presente / ⬜ ausente)</p>%s" % table
