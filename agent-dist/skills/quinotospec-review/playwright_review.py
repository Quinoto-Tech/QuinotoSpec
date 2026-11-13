#!/usr/bin/env python3
"""playwright_review.py — review visual de propuestas con Playwright.

Uso:
    python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
      --root . --proposal 2026-11-13-mi-propuesta --json

El modo es opcional y degrada de forma segura: si falta Playwright ofrece
instalar la app, configurar MCP u omitir. Nunca instala sin consentimiento.
"""

import argparse
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import mcp_config  # noqa: E402
import playwright_doctor  # noqa: E402

SCHEMA_VERSION = 1
VIEWPORTS = ("1440x900", "768x1024", "390x844")
EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_ACTION_REQUIRED = 3


class ReviewError(Exception):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def contract_script() -> Path:
    return HERE.parent / "quinotospec-contract" / "contract.py"


def validate_contract(root: Path) -> Dict[str, Any]:
    script = contract_script()
    if not script.is_file():
        return {"ok": True, "skipped": True, "reason": "contract.py no encontrado"}
    proc = subprocess.run(
        [sys.executable, "-B", str(script), "validate", "--root", str(root), "--strict"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "output": (proc.stdout or "").strip(),
        "error": (proc.stderr or "").strip(),
    }


def resolve_proposal(root: Path, slug: str) -> Path:
    if not slug or slug.strip() != slug:
        raise ReviewError("proposal slug vacio o con espacios")
    if "/" in slug or "\\" in slug or slug in (".", "..") or slug.startswith(".."):
        raise ReviewError("proposal slug invalido: " + slug)
    base = (root / ".quinoto-spec" / "proposals").resolve()
    raw_target = base / slug
    if raw_target.is_symlink():
        raise ReviewError("proposal no puede ser un symlink: " + slug)
    target = raw_target.resolve()
    if base not in target.parents:
        raise ReviewError("proposal fuera de .quinoto-spec/proposals: " + slug)
    if not (target / "proposal.md").is_file():
        raise ReviewError("proposal.md no encontrado: " + slug)
    return target


def find_free_port() -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
    finally:
        sock.close()


def start_ui(root: Path, port: int, timeout: int = 10, log_dir: Optional[Path] = None) -> tuple:
    server = HERE.parents[1] / "ui" / "server.py"
    if not server.is_file():
        raise ReviewError("UI server.py no encontrado: " + str(server))
    # El log va a un archivo: heredar PIPE sin drenar puede bloquear el server
    # cuando el buffer se llena. `start_new_session` permite matar el grupo.
    log_path = None
    log_handle = subprocess.DEVNULL
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "ui-server.log"
        log_handle = open(log_path, "w", encoding="utf-8")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-B", str(server), "--root", str(root), "--host", "127.0.0.1", "--port", str(port), "--no-browser"],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
    finally:
        if log_path is not None and hasattr(log_handle, "close"):
            log_handle.close()
    base_url = "http://127.0.0.1:%d" % port
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            tail = ""
            if log_path is not None and log_path.is_file():
                tail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
            raise ReviewError("UI termino antes de /health (exit %s): %s" % (proc.returncode, tail.strip()))
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=0.5) as response:
                if response.status == 200:
                    return proc, base_url
        except (urllib.error.URLError, OSError):
            time.sleep(0.1)
    stop_ui(proc)
    raise ReviewError("timeout esperando /health de la UI")


def stop_ui(proc: Optional[subprocess.Popen]) -> None:
    if proc is None or proc.poll() is not None:
        return
    # El server corre en su propio grupo (start_new_session): matarlo entero
    # evita hijos huerfanos cuando el proceso principal ya no existe.
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            proc.kill()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass


def locate_e2e(root: Path, explicit: Optional[str] = None) -> Path:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.is_dir():
            return candidate.resolve()
        raise ReviewError("directorio E2E no encontrado: " + str(candidate))
    for candidate in (HERE / "e2e", root / "agent-dist" / "skills" / "quinotospec-review" / "e2e", root / "tests" / "e2e"):
        if candidate.is_dir():
            return candidate.resolve()
    raise ReviewError("harness E2E no encontrado; se esperaba agent-dist/skills/quinotospec-review/e2e")


def build_install_commands() -> List[List[str]]:
    return [
        ["npm", "ci"],
        ["npx", "playwright", "install", "chromium"],
    ]


def install_playwright_app(root: Path, e2e_dir: Optional[str] = None) -> Dict[str, Any]:
    e2e = locate_e2e(root, e2e_dir)
    npm = shutil.which("npm")
    npx = shutil.which("npx")
    if not npm or not npx:
        raise ReviewError("npm y npx son necesarios para instalar Playwright app")
    steps = []
    for command in build_install_commands():
        executable = npm if command[0] == "npm" else npx
        proc = subprocess.run(
            [executable] + command[1:],
            cwd=str(e2e),
            capture_output=True,
            text=True,
            timeout=600,
        )
        steps.append(
            {
                "command": " ".join(command),
                "exit_code": proc.returncode,
                "output": ((proc.stdout or "") + (proc.stderr or "")).strip()[-4000:],
            }
        )
        if proc.returncode != 0:
            raise ReviewError("fallo instalando Playwright: " + " ".join(command))
    return {"installed": True, "e2e_dir": str(e2e), "steps": steps, "sudo": False}


def select_backend(requested: str, environment: Dict[str, Any]) -> Optional[str]:
    app_ready = bool(environment["app"]["available"] and environment["app"]["chromium"])
    mcp_ready = bool(environment["mcp"]["configured"])
    if requested == "app":
        return "app" if app_ready else None
    if requested == "mcp":
        return "mcp" if mcp_ready else None
    if app_ready:
        return "app"
    if mcp_ready:
        return "mcp"
    return None


def dependency_block(environment: Dict[str, Any], backend: Optional[str], action: str, consent: str) -> Dict[str, Any]:
    return {
        "app": environment["app"],
        "mcp": environment["mcp"],
        "selected_backend": backend,
        "install_action": action,
        "consent": consent,
    }


def base_evidence(root: Path, slug: str, task_id: Optional[str], environment: Dict[str, Any], backend: Optional[str], action: str, consent: str) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": "playwright",
        "browser": "chromium",
        "base_url": None,
        "proposal": slug,
        "task_id": task_id,
        "dependency": dependency_block(environment, backend, action, consent),
        "viewports": list(VIEWPORTS),
        "checks": [],
        "console_errors": [],
        "page_errors": [],
        "failed_requests": [],
        "screenshots": [],
        "result": "error",
        "generated_at": now_iso(),
    }


def safe_slug(slug: str) -> str:
    """Nombre de archivo seguro derivado del slug.

    El slug llega del usuario y en el camino de error (`resolve_proposal` falla)
    todavia no fue validado: sin sanitizar, `reviews / (slug + ".json")` escribe
    fuera de `.quinoto-spec/reviews/` (path traversal).
    """
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", slug or "")
    cleaned = cleaned.strip(".-")
    return cleaned or "proposal"


def display_path(path: Any, root: Path) -> Any:
    """Ruta apta para evidencia versionable: relativa al repo o con `~`."""
    if not isinstance(path, str) or not path:
        return path
    candidate = Path(path)
    if candidate.is_absolute():
        # En macOS /var es symlink a /private/var: comparar sin resolver deja la
        # ruta absoluta (y filtra el home) aunque este dentro del repo.
        resolved_root = Path(root).resolve()
        try:
            return str(candidate.resolve().relative_to(resolved_root))
        except (ValueError, OSError):
            try:
                return "~/" + str(candidate.resolve().relative_to(Path.home()))
            except (ValueError, OSError):
                return path
    return path


def sanitize_paths(data: Dict[str, Any], root: Path) -> Dict[str, Any]:
    data["screenshots"] = [display_path(item, root) for item in data.get("screenshots", [])]
    dependency = data.get("dependency") or {}
    mcp = dependency.get("mcp") or {}
    if mcp.get("detected_in"):
        mcp["detected_in"] = [display_path(item, root) for item in mcp["detected_in"]]
        dependency["mcp"] = mcp
        data["dependency"] = dependency
    playwright = data.get("playwright")
    if isinstance(playwright, dict):
        for key in ("e2e_dir", "raw"):
            if playwright.get(key):
                playwright[key] = display_path(playwright[key], root)
    for key in ("evidence", "mcp"):
        block = data.get(key)
        if isinstance(block, dict):
            for field in ("json", "markdown", "artifacts", "path", "backup"):
                if block.get(field):
                    block[field] = display_path(block[field], root)
    return data


def write_evidence(root: Path, slug: str, data: Dict[str, Any]) -> Dict[str, str]:
    reviews = root / ".quinoto-spec" / "reviews"
    artifacts = reviews / ".artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    safe = safe_slug(slug)
    json_path = reviews / (safe + "-playwright.json")
    md_path = reviews / (safe + "-playwright.md")
    data = sanitize_paths(data, root)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_report(data), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "artifacts": str(artifacts)}


def render_report(data: Dict[str, Any]) -> str:
    dep = data.get("dependency", {})
    lines = [
        "# Playwright Review — %s" % data.get("proposal", ""),
        "",
        "- **Resultado:** `%s`" % data.get("result", ""),
        "- **Backend:** `%s`" % (dep.get("selected_backend") or "—"),
        "- **Acción de instalación:** `%s`" % (dep.get("install_action") or "—"),
        "- **Consentimiento:** `%s`" % (dep.get("consent") or "—"),
        "- **Generado:** %s" % data.get("generated_at", ""),
        "",
        "## Checks",
        "",
    ]
    checks = data.get("checks") or []
    if checks:
        lines += ["| Check | Estado | Detalle |", "|---|---|---|"]
        for check in checks:
            lines.append("| %s | %s | %s |" % (check.get("id", ""), check.get("status", ""), str(check.get("detail", "")).replace("|", "\\|")))
    else:
        lines.append("Sin checks ejecutados.")
    lines += ["", "## Errores de consola", ""]
    lines += ["- %s" % item for item in (data.get("console_errors") or [])] or ["- Ninguno"]
    lines += ["", "## Screenshots", ""]
    lines += ["- `%s`" % item for item in (data.get("screenshots") or [])] or ["- Ninguno"]
    if data.get("message"):
        lines += ["", "## Mensaje", "", str(data["message"])]
    return "\n".join(lines) + "\n"


def _print_or_json(args: argparse.Namespace, data: Dict[str, Any], code: int) -> int:
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("Playwright review: %s" % data.get("result"))
        if data.get("message"):
            print(data["message"])
        print("Evidencia: %s" % data.get("evidence", {}).get("json", "—"))
    return code


def prompt_for_action(environment: Dict[str, Any]) -> str:
    print("Playwright no esta disponible.\n")
    print("  1) Instalar Playwright app (recomendado para CI y resultados reproducibles)")
    print("     - requiere Node.js 20+ y ~150-300 MB para Chromium")
    print("     - comando: cd agent-dist/skills/quinotospec-review/e2e && npm install && npx playwright install chromium")
    print("  2) Configurar Playwright MCP (recomendado para revision interactiva en el IDE)")
    print("     - el agente usa herramientas MCP; puede requerir reiniciar el IDE")
    print("     - comando base: npx -y @playwright/mcp@latest")
    print("  3) Omitir el review visual y continuar con el review estandar")
    print("")
    for _ in range(3):
        try:
            choice = input("Elegi una opcion [1/2/3]: ").strip()
        except EOFError:
            return "skip"
        if choice in ("1", "2", "3"):
            return {"1": "install-app", "2": "install-mcp", "3": "skip"}[choice]
    return "skip"


def run_playwright(
    root: Path,
    base_url: str,
    slug: str,
    task_id: Optional[str],
    output_dir: Path,
    e2e_dir: Optional[str],
    timeout: int,
) -> Dict[str, Any]:
    e2e = locate_e2e(root, e2e_dir)
    npx = shutil.which("npx")
    if not npx:
        raise ReviewError("npx no encontrado")
    env = os.environ.copy()
    env.update(
        {
            "QS_BASE_URL": base_url,
            "QS_PROPOSAL_SLUG": slug,
            "QS_TASK_ID": task_id or "",
            "QS_OUTPUT_DIR": str(output_dir),
        }
    )
    proc = subprocess.run(
        [npx, "playwright", "test", "--project=chromium"],
        cwd=str(e2e),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    raw_path = output_dir / "playwright-raw.json"
    raw = {}
    if raw_path.is_file():
        try:
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = {}
    return {
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "")[-8000:],
        "stderr": (proc.stderr or "")[-8000:],
        "raw": raw,
        "raw_path": str(raw_path) if raw_path.is_file() else None,
        "e2e_dir": str(e2e),
    }


def run_review_app(
    root: Path,
    slug: str,
    task_id: Optional[str],
    environment: Dict[str, Any],
    args: argparse.Namespace,
    install_action: str,
    consent: str,
) -> Dict[str, Any]:
    data = base_evidence(root, slug, task_id, environment, "app", install_action, consent)
    reviews = root / ".quinoto-spec" / "reviews"
    artifacts = reviews / ".artifacts" / (safe_slug(slug) + "-playwright")
    artifacts.mkdir(parents=True, exist_ok=True)
    port = find_free_port()
    proc = None
    try:
        proc, base_url = start_ui(root, port, log_dir=artifacts)
        data["base_url"] = base_url
        result = run_playwright(root, base_url, slug, task_id, artifacts, args.e2e_dir, args.timeout)
        raw = result.get("raw") or {}
        data["checks"] = raw.get("checks", [])
        data["console_errors"] = raw.get("console_errors", [])
        data["page_errors"] = raw.get("page_errors", [])
        data["failed_requests"] = raw.get("failed_requests", [])
        data["screenshots"] = raw.get("screenshots", [])
        data["result"] = raw.get("result") or ("pass" if result["exit_code"] == 0 else "fail")
        data["playwright"] = {
            "exit_code": result["exit_code"],
            "e2e_dir": result["e2e_dir"],
            "raw": result.get("raw_path"),
            "stdout_tail": result.get("stdout", "")[-2000:],
            "stderr_tail": result.get("stderr", "")[-2000:],
        }
    except Exception as error:  # noqa: BLE001
        data["result"] = "error"
        data["message"] = str(error)
    finally:
        stop_ui(proc)
    return data


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Review visual de propuestas con Playwright")
    parser.add_argument("--root", default=".")
    parser.add_argument("--proposal", required=False, help="Slug de la propuesta")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--playwright-backend", choices=["auto", "app", "mcp"], default="auto")
    parser.add_argument("--install-playwright", action="store_true")
    parser.add_argument("--install-playwright-mcp", action="store_true")
    parser.add_argument("--no-install-prompt", action="store_true")
    parser.add_argument("--require-playwright", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--skip-contract", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--e2e-dir", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    environment = playwright_doctor.check_environment(root)
    if args.check_only:
        print(json.dumps(environment, ensure_ascii=False, indent=2))
        return EXIT_OK

    if not args.proposal:
        print("ERROR: falta --proposal", file=sys.stderr)
        return EXIT_USAGE

    try:
        proposal_dir = resolve_proposal(root, args.proposal)
    except ReviewError as error:
        data = base_evidence(root, args.proposal, args.task_id, environment, None, "none", "none")
        data["result"] = "error"
        data["message"] = str(error)
        data["evidence"] = {}
        if (root / ".quinoto-spec").is_dir():
            try:
                data["evidence"] = write_evidence(root, args.proposal, data)
            except OSError as write_error:
                data["evidence_error"] = str(write_error)
        return _print_or_json(args, data, EXIT_USAGE)

    if not args.skip_contract:
        contract = validate_contract(root)
        if not contract["ok"]:
            data = base_evidence(root, args.proposal, args.task_id, environment, None, "none", "none")
            data["result"] = "error"
            data["message"] = "contract.py validate fallo: " + contract.get("output", "") + contract.get("error", "")
            data["evidence"] = write_evidence(root, args.proposal, data)
            return _print_or_json(args, data, EXIT_FAIL)

    backend = select_backend(args.playwright_backend, environment)
    install_action = "none"
    consent = "none"

    if backend is None:
        if args.no_install_prompt:
            data = base_evidence(root, args.proposal, args.task_id, environment, None, "skip", "explicit-flag")
            data["result"] = "skipped"
            data["message"] = "Playwright no disponible; se omite el review visual."
            data["evidence"] = write_evidence(root, args.proposal, data)
            return _print_or_json(args, data, EXIT_OK)

        if args.install_playwright:
            try:
                install = install_playwright_app(root, args.e2e_dir)
                environment = playwright_doctor.check_environment(root)
                backend = select_backend("app", environment)
                install_action = "install-app"
                consent = "explicit-flag"
                if backend is None:
                    raise ReviewError("Playwright app se instalo pero Chromium no esta disponible")
            except ReviewError as error:
                data = base_evidence(root, args.proposal, args.task_id, environment, None, "install-app", "explicit-flag")
                data["result"] = "error"
                data["message"] = str(error)
                data["evidence"] = write_evidence(root, args.proposal, data)
                return _print_or_json(args, data, EXIT_FAIL)

        elif args.install_playwright_mcp:
            try:
                config = mcp_config.configure_mcp(root, dry_run=False)
                environment = playwright_doctor.check_environment(root)
                install_action = "configure-mcp"
                consent = "explicit-flag"
                data = base_evidence(root, args.proposal, args.task_id, environment, "mcp", install_action, consent)
                data["result"] = "action_required"
                data["message"] = "MCP configurado en %s. Reinicia el IDE y volve a ejecutar el review con --playwright-backend mcp." % config["path"]
                data["mcp"] = config
                data["evidence"] = write_evidence(root, args.proposal, data)
                return _print_or_json(args, data, EXIT_ACTION_REQUIRED)
            except Exception as error:  # noqa: BLE001
                data = base_evidence(root, args.proposal, args.task_id, environment, None, "configure-mcp", "explicit-flag")
                data["result"] = "error"
                data["message"] = "No se pudo configurar MCP: " + str(error)
                data["evidence"] = write_evidence(root, args.proposal, data)
                return _print_or_json(args, data, EXIT_FAIL)

        elif not sys.stdin.isatty() or args.yes:
            data = base_evidence(root, args.proposal, args.task_id, environment, None, "none", "none")
            data["result"] = "action_required"
            data["message"] = "Falta Playwright. Elegi --install-playwright, --install-playwright-mcp o --no-install-prompt."
            data["options"] = environment["options"]
            data["evidence"] = write_evidence(root, args.proposal, data)
            code = EXIT_FAIL if args.require_playwright else EXIT_ACTION_REQUIRED
            return _print_or_json(args, data, code)

        else:
            choice = prompt_for_action(environment)
            if choice == "skip":
                data = base_evidence(root, args.proposal, args.task_id, environment, None, "skip", "interactive")
                data["result"] = "skipped"
                data["message"] = "El usuario omitio el review visual."
                data["evidence"] = write_evidence(root, args.proposal, data)
                return _print_or_json(args, data, EXIT_OK)
            if choice == "install-app":
                try:
                    install_playwright_app(root, args.e2e_dir)
                    environment = playwright_doctor.check_environment(root)
                    backend = select_backend("app", environment)
                    install_action = "install-app"
                    consent = "interactive"
                    if backend is None:
                        raise ReviewError("Chromium no disponible despues de instalar")
                except ReviewError as error:
                    data = base_evidence(root, args.proposal, args.task_id, environment, None, "install-app", "interactive")
                    data["result"] = "error"
                    data["message"] = str(error)
                    data["evidence"] = write_evidence(root, args.proposal, data)
                    return _print_or_json(args, data, EXIT_FAIL)
            else:
                try:
                    config = mcp_config.configure_mcp(root, dry_run=False)
                    environment = playwright_doctor.check_environment(root)
                    install_action = "configure-mcp"
                    consent = "interactive"
                    data = base_evidence(root, args.proposal, args.task_id, environment, "mcp", install_action, consent)
                    data["result"] = "action_required"
                    data["message"] = "MCP configurado en %s. Reinicia el IDE y volve a ejecutar." % config["path"]
                    data["mcp"] = config
                    data["evidence"] = write_evidence(root, args.proposal, data)
                    return _print_or_json(args, data, EXIT_ACTION_REQUIRED)
                except Exception as error:  # noqa: BLE001
                    data = base_evidence(root, args.proposal, args.task_id, environment, None, "configure-mcp", "interactive")
                    data["result"] = "error"
                    data["message"] = "No se pudo configurar MCP: " + str(error)
                    data["evidence"] = write_evidence(root, args.proposal, data)
                    return _print_or_json(args, data, EXIT_FAIL)

    if backend == "mcp":
        data = base_evidence(root, args.proposal, args.task_id, environment, "mcp", install_action, consent)
        data["result"] = "action_required"
        data["message"] = "Backend MCP seleccionado. El agente debe ejecutar los checks con las herramientas MCP y guardar la evidencia."
        data["requires_agent"] = True
        data["evidence"] = write_evidence(root, args.proposal, data)
        return _print_or_json(args, data, EXIT_ACTION_REQUIRED)

    data = run_review_app(root, args.proposal, args.task_id, environment, args, install_action, consent)
    data["evidence"] = write_evidence(root, args.proposal, data)
    code = EXIT_OK if data["result"] in ("pass", "warn") else EXIT_FAIL
    if data["result"] == "action_required":
        code = EXIT_ACTION_REQUIRED
    return _print_or_json(args, data, code)


if __name__ == "__main__":
    raise SystemExit(main())
