#!/usr/bin/env bash
set -euo pipefail

ARCHIVE="${1:?usage: smoke-release.sh ARCHIVE}"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEMP_ROOT"' EXIT

tar -xzf "$ARCHIVE" -C "$TEMP_ROOT"
if [ ! -x "$TEMP_ROOT/install.sh" ] || [ ! -d "$TEMP_ROOT/agent-dist" ]; then
    printf 'ERROR: archive is missing install.sh or agent-dist\n' >&2
    exit 1
fi

if tar -tzf "$ARCHIVE" | grep -Eq '(^|/)__pycache__/|(^|/)[^/]+\.pyc$|(^|/)(\.pytest_cache|\.mypy_cache|node_modules)(/|$)'; then
    printf 'ERROR: archive contains generated Python cache files\n' >&2
    exit 1
fi

TARGET_ROOT="$TEMP_ROOT/target"
mkdir -p "$TARGET_ROOT"
cd "$TARGET_ROOT"
bash "$TEMP_ROOT/install.sh" --opencode --yes >/dev/null
bash "$TEMP_ROOT/install.sh" --verify --opencode --yes >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

manifest = json.loads(Path(".opencode/.quinoto-spec/ownership.json").read_text(encoding="utf-8"))
assert manifest["schema_version"] == 1
assert manifest["owned"]
assert manifest["agents"]["managed"] is True
assert Path(".opencode/.quinoto-spec/ownership.json").is_file()
PY

bash "$TEMP_ROOT/install.sh" --uninstall --opencode --yes >/dev/null
if [ -e ".opencode" ]; then
    printf 'ERROR: uninstall left an empty managed directory\n' >&2
    exit 1
fi
printf 'Release smoke test passed: %s\n' "$ARCHIVE"
