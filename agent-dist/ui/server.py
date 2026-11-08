#!/usr/bin/env python3
"""QuinotoSpec UI -- dashboard web local read-only sobre .quinoto-spec/.

Uso:
    python3 -B agent-dist/ui/server.py --root . --port 8765
    python3 -B agent-dist/ui/server.py --root . --port 0 --no-browser

Solo stdlib (http.server + urllib). No modifica archivos del proyecto.
"""

import argparse
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True

sys.path.insert(0, str(Path(__file__).resolve().parent))

import readers  # noqa: E402
import templates  # noqa: E402


class State:
    roots = []
    root = Path(".")
    summaries = []
    summary = None

    @classmethod
    def refresh(cls, project=None):
        if not cls.roots:
            cls.roots = [cls.root]
        cls.summaries = [readers.build_summary(r) for r in cls.roots]
        if len(cls.roots) == 1:
            cls.root = cls.roots[0]
            cls.summary = dict(cls.summaries[0])
            cls.summary["multi"] = False
            cls.summary["projects"] = None
            cls.summary["roots"] = [str(cls.roots[0])]
            cls.summary["selected_project"] = None
            return cls.summary

        ms = readers.build_multi_summary(cls.roots)
        selected = None
        if project:
            for index, summary in enumerate(cls.summaries):
                if summary["name"] == project:
                    selected = (index, summary)
                    break
        if selected is not None:
            index, selected_summary = selected
            cls.root = cls.roots[index]
            view = dict(selected_summary)
            view["multi"] = True
            view["projects"] = ms["projects"]
            view["roots"] = ms["roots"]
            view["selected_project"] = project
            for proposal in view.get("proposals", []):
                proposal.setdefault("project", project)
            cls.summary = view
        else:
            cls.root = cls.roots[0]
            ms["selected_project"] = None
            cls.summary = ms
        return cls.summary


class Handler(BaseHTTPRequestHandler):
    server_version = "QuinotoSpecUI/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s %s\n" % (self.address_string(), fmt % args))

    def _send(self, status, body, content_type="text/html; charset=utf-8"):
        payload = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _page(self, title, active, content):
        summary = State.refresh(self._project)
        projects = summary.get("projects") if summary.get("multi") else None
        body = templates.layout(title, active, content, project_name=summary.get("name", ""), projects=projects, selected_project=summary.get("selected_project"))
        self._send(200, body)

    def do_GET(self):
        parsed = urlparse(self.path)
        route = unquote(parsed.path)
        from urllib.parse import parse_qs

        self._project = (parse_qs(parsed.query).get("project") or [None])[0]

        try:
            if route == "/health":
                self._send(200, json.dumps({"status": "ok", "root": str(State.root)}), "application/json; charset=utf-8")
                return
            if route == "/api/summary":
                self._send(200, json.dumps(State.refresh(self._project), ensure_ascii=False, indent=2), "application/json; charset=utf-8")
                return
            if route == "/static/style.css":
                self._send(200, templates.STYLE, "text/css; charset=utf-8")
                return

            summary = State.refresh(self._project)
            q = (parse_qs(parsed.query).get("q") or [""])[0]
            if route == "/":
                self._page("Panel", "dashboard", templates.dashboard(summary))
                return
            if route == "/projects":
                self._page("Proyectos", "projects", templates.projects_page(summary))
                return
            if route == "/proposals":
                self._page("Propuestas", "proposals", templates.proposals_page(summary, q=q))
                return
            if route.startswith("/proposals/"):
                slug = route[len("/proposals/"):].strip("/")
                proposal = next((p for p in summary["proposals"] if p["slug"] == slug), None)
                if proposal is None:
                    self._send(404, templates.layout("No encontrada", "", '<div class="card empty">Propuesta no encontrada: %s</div>' % templates.esc(slug)))
                    return
                self._page(proposal["title"], "proposals", templates.proposal_page(proposal))
                return
            if route.startswith("/tasks/"):
                task_id = route[len("/tasks/"):].strip("/")
                task = None
                parent = None
                for proposal in summary["proposals"]:
                    for candidate in proposal["tasks"]:
                        if candidate["id"] == task_id:
                            task = candidate
                            parent = proposal
                            break
                    if task:
                        break
                if task is None:
                    self._send(404, templates.layout("No encontrada", "", '<div class="card empty">Tarea no encontrada: %s</div>' % templates.esc(task_id)))
                    return
                self._page(task["id"], "tasks", templates.task_page(task, parent))
                return
            if route == "/tasks":
                self._page("Tareas", "tasks", templates.tasks_page(summary, q=q))
                return
            if route == "/changelog":
                self._page("Changelog", "changelog", templates.changelog_page(summary))
                return
            if route == "/discovery":
                self._page("Discovery", "discovery", templates.discovery_page(summary))
                return
            if route == "/constitution":
                self._page("Constitución", "constitution", templates.constitution_page(readers.read_constitution(State.root)))
                return

            self._send(404, templates.layout("No encontrado", "", '<div class="card empty">Ruta no encontrada.</div>'))
        except Exception as error:  # noqa: BLE001 - la UI no debe caerse por un archivo mal formado
            self._send(500, templates.layout("Error", "", '<div class="alert warn">Error leyendo el proyecto: %s</div>' % templates.esc(error)))


def main(argv=None):
    parser = argparse.ArgumentParser(description="QuinotoSpec UI -- dashboard web local read-only")
    parser.add_argument("--root", default=".", help="Raiz del proyecto con .quinoto-spec/")
    parser.add_argument("--roots", default="", help="Lista de raices separadas por coma (panel multi-proyecto)")
    parser.add_argument("--host", default="127.0.0.1", help="Host de escucha (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Puerto (0 = efimero)")
    parser.add_argument("--no-browser", action="store_true", help="No abrir el navegador")
    parser.add_argument("--json", action="store_true", help="Imprimir el resumen JSON y salir")
    args = parser.parse_args(argv)

    roots = [p.strip() for p in args.roots.split(",") if p.strip()] if args.roots else [args.root]
    resolved = [Path(r).resolve() for r in roots]
    if not (resolved[0] / ".quinoto-spec").is_dir():
        print("Aviso: %s no contiene .quinoto-spec/ (la UI mostrara un proyecto vacio)." % resolved[0], file=sys.stderr)

    State.roots = resolved
    State.root = resolved[0]
    if args.json:
        if len(resolved) == 1:
            print(readers.to_json(resolved[0]))
        else:
            print(json.dumps(readers.build_multi_summary(resolved), ensure_ascii=False, indent=2))
        return 0

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    host, port = server.server_address[0], server.server_address[1]
    url = "http://%s:%s" % (host, port)
    print("QuinotoSpec UI: %s (root: %s)" % (url, resolved[0]))
    print("Ctrl+C para detener.")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001 - sin navegador disponible, seguir sirviendo
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
