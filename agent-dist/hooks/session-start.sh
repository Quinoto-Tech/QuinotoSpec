#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PLATFORM="${QUINOTOSPEC_HOOK_PLATFORM:-generic}"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --platform)
            if [ "$#" -lt 2 ]; then
                printf '%s\n' 'QuinotoSpec hook: --platform requires a value' >&2
                exit 2
            fi
            PLATFORM="$2"
            shift 2
            ;;
        --platform=*)
            PLATFORM="${1#*=}"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

BOOTSTRAP_PATH="$PLUGIN_ROOT/bootstrap/quinotospec-bootstrap.md"
if [ ! -f "$BOOTSTRAP_PATH" ]; then
    printf 'QuinotoSpec hook: bootstrap not found: %s\n' "$BOOTSTRAP_PATH" >&2
    exit 1
fi

python3 - "$BOOTSTRAP_PATH" "$PLATFORM" "$PLUGIN_ROOT" <<'PY'
import json
import sys
from pathlib import Path

bootstrap_path = Path(sys.argv[1])
platform = sys.argv[2].lower()
plugin_root = Path(sys.argv[3]).resolve()
if platform == "cursor":
    staged_plugin = plugin_root / "quinotospec-plugin"
    if staged_plugin.is_dir():
        plugin_root = staged_plugin
text = bootstrap_path.read_text(encoding="utf-8")
if text.startswith("---"):
    end = text.find("\n---", 3)
    if end >= 0:
        newline = text.find("\n", end + 1)
        text = text[newline + 1:] if newline >= 0 else ""
context = text.strip()
if not context:
    raise SystemExit("QuinotoSpec hook: bootstrap is empty")
if platform == "claude":
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
elif platform == "cursor":
    payload = {
        "additional_context": context,
        "additionalContext": context,
        "pluginPaths": [str(plugin_root)],
    }
else:
    payload = {"additionalContext": context}
print(json.dumps(payload, ensure_ascii=False))
PY
