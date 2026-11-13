#!/usr/bin/env python3
"""Configuracion best-effort de Playwright MCP por IDE.

No instala nada. Solo escribe la entrada MCP cuando se le pide explicitamente.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

MCP_NAME = "playwright"
MCP_COMMAND = ["npx", "-y", "@playwright/mcp@latest"]


def snippet() -> Dict[str, Any]:
    return {
        "mcp": {
            MCP_NAME: {
                "type": "local",
                "command": list(MCP_COMMAND),
                "enabled": True,
            }
        }
    }


def _read(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _pick_target(root: Path, ide: Optional[str], home: Path) -> tuple:
    ide = (ide or "").lower()
    opencode_candidates = [
        root / "opencode.json",
        root / ".opencode" / "opencode.json",
        home / ".config" / "opencode" / "opencode.json",
    ]
    if ide in ("", "opencode", "auto"):
        for candidate in opencode_candidates:
            if candidate.is_file():
                return candidate, "opencode"
        if (root / ".opencode").is_dir() or ide == "opencode":
            return root / "opencode.json", "opencode"
    if ide == "cursor":
        for candidate in (root / ".cursor" / "mcp.json", home / ".cursor" / "mcp.json"):
            if candidate.is_file():
                return candidate, "cursor"
        return root / ".cursor" / "mcp.json", "cursor"
    if ide == "claude":
        for candidate in (root / ".mcp.json", home / ".claude" / "settings.json"):
            if candidate.is_file():
                return candidate, "claude"
        return root / ".mcp.json", "claude"
    if ide == "cline":
        for candidate in (root / ".cline" / "mcp.json", root / "cline_mcp_settings.json"):
            if candidate.is_file():
                return candidate, "cline"
        return root / ".cline" / "mcp.json", "cline"
    return root / "mcp.json", "generic"


def configure_mcp(
    root: Path,
    ide: Optional[str] = None,
    home: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    root = Path(root).resolve()
    if home is None and os.environ.get("QS_HOME"):
        home = Path(os.environ["QS_HOME"])
    home = home or Path.home()
    target, detected_ide = _pick_target(root, ide, home)
    data = _read(target)
    if detected_ide == "opencode":
        data.setdefault("mcp", {})
        data["mcp"][MCP_NAME] = {
            "type": "local",
            "command": list(MCP_COMMAND),
            "enabled": True,
        }
    else:
        data.setdefault("mcpServers", {})
        data["mcpServers"][MCP_NAME] = {
            "command": MCP_COMMAND[0],
            "args": list(MCP_COMMAND[1:]),
        }
    result = {
        "configured": True,
        "dry_run": bool(dry_run),
        "ide": detected_ide,
        "path": str(target),
        "requires_restart": True,
        "snippet": data,
    }
    if dry_run:
        return result
    if target.is_file():
        backup = target.with_suffix(target.suffix + ".quinotospec.bak")
        try:
            shutil.copy2(target, backup)
            result["backup"] = str(backup)
        except OSError:
            result["backup"] = None
    _write_atomic(target, data)
    return result
