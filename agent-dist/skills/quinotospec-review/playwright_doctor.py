#!/usr/bin/env python3
"""playwright_doctor.py — detecta Playwright app/Chromium/MCP sin instalar nada.

Uso:
    python3 -B agent-dist/skills/quinotospec-review/playwright_doctor.py --root . --check --json
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.dont_write_bytecode = True

SCHEMA_VERSION = 1
MCP_PACKAGE = "@playwright/mcp"
E2E_RELATIVE = Path("agent-dist") / "skills" / "quinotospec-review" / "e2e"
MCP_CONFIG_CANDIDATES = (
    "opencode.json",
    ".opencode/opencode.json",
    ".cursor/mcp.json",
    ".mcp.json",
    ".cline/mcp.json",
    "cline_mcp_settings.json",
    "mcp.json",
    ".claude/settings.json",
)


def run_command(command: List[str], cwd: Optional[Path] = None, timeout: int = 5) -> tuple:
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except (OSError, subprocess.TimeoutExpired) as error:
        return 127, "", str(error)


def node_info(which=None, run=None) -> Dict[str, Any]:
    which = which or shutil.which
    run = run or run_command
    path = which("node")
    if not path:
        return {"available": False, "version": None, "path": None, "major": None, "error": "node not found"}
    code, out, err = run([path, "--version"])
    version = out.lstrip("v").strip() if code == 0 else None
    major = None
    if version:
        try:
            major = int(version.split(".")[0])
        except (TypeError, ValueError):
            major = None
    return {
        "available": code == 0,
        "version": version,
        "path": path,
        "major": major,
        "error": None if code == 0 else (err or "node --version failed"),
    }


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def local_playwright(root: Path, module_dir: Optional[Path] = None) -> Optional[str]:
    module_dir = module_dir or Path(__file__).resolve().parent
    candidates = [
        module_dir / "e2e" / "node_modules" / "@playwright" / "test" / "package.json",
        root / E2E_RELATIVE / "node_modules" / "@playwright" / "test" / "package.json",
        root / "tests" / "e2e" / "node_modules" / "@playwright" / "test" / "package.json",
    ]
    for package in candidates:
        data = _read_json(package)
        if data and isinstance(data.get("version"), str):
            return data["version"]
    return None


def playwright_app(root: Path, which=None, run=None, home=None, env=None, module_dir=None) -> Dict[str, Any]:
    which = which or shutil.which
    run = run or run_command
    version = local_playwright(root, module_dir=module_dir)
    source = "local" if version else None
    if not version:
        binary = which("playwright")
        if binary:
            code, out, _err = run([binary, "--version"])
            if code == 0:
                version = out.split()[-1] if out else None
                source = "binary"
    return {
        "available": bool(version),
        "version": version,
        "source": source,
        "chromium": chromium_installed(home=home, env=env),
    }


def chromium_installed(home: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> bool:
    env = env or os.environ
    candidates = []
    explicit = env.get("PLAYWRIGHT_BROWSERS_PATH")
    if explicit:
        candidates.append(Path(explicit))
    home = home or Path.home()
    candidates.extend(
        [
            home / ".cache" / "ms-playwright",
            home / "Library" / "Caches" / "ms-playwright",
        ]
    )
    local_app_data = env.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "ms-playwright")
    for base in candidates:
        if not base.is_dir():
            continue
        if any(base.glob("chromium-*")) or any(base.glob("chromium_headless_shell-*")):
            return True
    return False


def _mcp_like(data: Any) -> bool:
    text = json.dumps(data, ensure_ascii=False).lower()
    return "playwright" in text and ("@playwright/mcp" in text or "playwright-mcp" in text)


def detect_mcp(root: Path, home: Optional[Path] = None) -> Dict[str, Any]:
    home = home or Path.home()
    detected = []
    candidates = [root / item for item in MCP_CONFIG_CANDIDATES]
    candidates.extend(
        [
            home / ".config" / "opencode" / "opencode.json",
            home / ".cursor" / "mcp.json",
            home / ".claude" / "settings.json",
        ]
    )
    for path in candidates:
        data = _read_json(path)
        if data is not None and _mcp_like(data):
            detected.append(str(path))
    return {
        "configured": bool(detected),
        "detected_in": sorted(set(detected)),
        "package": MCP_PACKAGE,
    }


MIN_NODE_MAJOR = 20


def check_environment(root: Path, home: Optional[Path] = None, which=None, run=None, env=None, module_dir: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(root).resolve()
    env = env if env is not None else os.environ
    if home is None and os.environ.get("QS_HOME"):
        home = Path(os.environ["QS_HOME"])
    which = which or shutil.which
    run = run or run_command
    # Permite probar el onboarding aun con Playwright instalado.
    forced_missing = env.get("QS_FORCE_MISSING_PLAYWRIGHT") == "1"
    node = node_info(which=which, run=run)
    if forced_missing:
        app = {"available": False, "version": None, "source": None, "chromium": False}
        mcp = {"configured": False, "detected_in": [], "package": MCP_PACKAGE}
    else:
        app = playwright_app(root, which=which, run=run, home=home, env=env, module_dir=module_dir)
        mcp = detect_mcp(root, home=home)
    app_ready = bool(app["available"] and app["chromium"])
    node_ready = bool(node["available"] and (node.get("major") or 0) >= MIN_NODE_MAJOR)
    recommended = "skip"
    if app_ready:
        recommended = "app"
    elif mcp["configured"]:
        recommended = "mcp"
    elif node_ready:
        recommended = "install-app"
    options = [
        {
            "id": "install-app",
            "label": "Instalar Playwright app y Chromium",
            "recommended": recommended == "install-app",
            "available": node_ready,
            "requires": "Node.js 20+ y red",
            "size": "~150-300 MB",
        },
        {
            "id": "install-mcp",
            "label": "Configurar Playwright MCP",
            "recommended": recommended == "install-mcp",
            "available": node_ready,
            "requires": "Node.js 20+ y un IDE con soporte MCP",
            "size": "sin descarga de navegador",
        },
        {
            "id": "skip",
            "label": "Omitir el review visual",
            "recommended": recommended == "skip",
            "available": True,
            "requires": None,
            "size": None,
        },
    ]
    blockers = []
    if not node_ready:
        blockers.append("Node.js 20+ es requerido para instalar la app o el MCP (Playwright 1.65 declara engines node>=20)")
    result = {
        "schema_version": SCHEMA_VERSION,
        "node": node,
        "app": app,
        "mcp": mcp,
        "options": options,
        "recommended": recommended,
        "blockers": blockers,
        "root": str(root),
        "min_node_major": MIN_NODE_MAJOR,
    }
    if forced_missing:
        result["forced_missing_playwright"] = True
        result["forced_reason"] = "QS_FORCE_MISSING_PLAYWRIGHT=1"
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detecta Playwright app, Chromium y MCP sin instalar nada")
    parser.add_argument("--root", default=".", help="Raiz del proyecto")
    parser.add_argument("--check", action="store_true", help="Solo verificar (default)")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    data = check_environment(root)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        app = data["app"]
        mcp = data["mcp"]
        print("Playwright app: %s" % ("OK " + str(app["version"]) if app["available"] else "no disponible"))
        print("Chromium: %s" % ("OK" if app["chromium"] else "no disponible"))
        print("Playwright MCP: %s" % ("configurado" if mcp["configured"] else "no configurado"))
        print("Recomendado: %s" % data["recommended"])
        for item in data["options"]:
            print("  - %s: %s" % (item["id"], item["label"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
