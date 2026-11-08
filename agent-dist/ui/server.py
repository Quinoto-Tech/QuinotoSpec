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
            if route.startswith("/static/"):
                name = route[len("/static/"):].strip("/")
                static_dir = Path(__file__).resolve().parent / "static"
                if name == "style.css":
                    self._send(200, templates.STYLE, "text/css; charset=utf-8")
                    return
                target = (static_dir / name).resolve()
                if static_dir.resolve() not in target.parents and target != static_dir.resolve():
                    self._send(404, "not found")
                    return
                if target.is_file():
                    import mimetypes

                    mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
                    self._send(200, target.read_bytes(), mime)
                    return
                self._send(404, "not found")
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
            if route.startswith("/discovery/"):
                name = route[len("/discovery/"):].strip("/")
                data = readers.read_discovery_file(State.root, name)
                if not data["exists"]:
                    self._send(404, templates.layout("No encontrada", "", '<div class="card empty">Archivo no encontrado: %s</div>' % templates.esc(name)))
                    return
                self._page(name, "discovery", templates.discovery_file_page(data))
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
    parser.add_argument("--stop", action="store_true", help="Detener instancias en ejecucion del servidor UI y salir")
    args = parser.parse_args(argv)

    if args.stop:
        stopped = 0
        import os as _os

        try:
            import subprocess as _sp

            result = _sp.run(["pgrep", "-f", "agent-dist/ui/server.py"], capture_output=True, text=True)
            for pid in result.stdout.split():
                if pid == str(_os.getpid()):
                    continue
                try:
                    _os.kill(int(pid), 15)
                    stopped += 1
                except (ProcessLookupError, ValueError):
                    pass
        except FileNotFoundError:
            for entry in _os.listdir("/proc"):
                if not entry.isdigit():
                    continue
                try:
                    with open(_os.path.join("/proc", entry, "cmdline"), "rb") as fh:
                        cmdline = fh.read()
                except OSError:
                    continue
                if b"agent-dist/ui/server.py" in cmdline and entry != str(_os.getpid()):
                    try:
                        _os.kill(int(entry), 15)
                        stopped += 1
                    except (ProcessLookupError, ValueError):
                        pass
        print("Servidores UI detenidos: %d" % stopped)
        return 0

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
