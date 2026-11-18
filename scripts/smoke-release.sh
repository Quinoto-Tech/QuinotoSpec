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

# --- OpenCode (v2): install -> verify -> ownership manifest -> uninstall ---
TARGET_ROOT="$TEMP_ROOT/target"
mkdir -p "$TARGET_ROOT"
cd "$TARGET_ROOT"
QUINOTOSPEC_OPENCODE_MAJOR=2 bash "$TEMP_ROOT/install.sh" --opencode --yes >/dev/null
QUINOTOSPEC_OPENCODE_MAJOR=2 bash "$TEMP_ROOT/install.sh" --verify --opencode --yes >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

manifest = json.loads(Path(".opencode/.quinoto-spec/ownership.json").read_text(encoding="utf-8"))
assert manifest["schema_version"] == 1
assert manifest["owned"]
assert manifest["agents"]["managed"] is True
assert manifest.get("opencode_major") == 2, manifest.get("opencode_major")
assert Path(".opencode/.quinoto-spec/ownership.json").is_file()
PY

# Invariant VPAT: los .md instalados referencian rutas ejecutables, nunca agent-dist/
python3 - <<'PY'
import re
from pathlib import Path

installed = Path(".opencode")
broken = sorted(str(p.relative_to(installed)) for p in installed.rglob("*.md") if "agent-dist" in p.read_text(encoding="utf-8"))
assert not broken, "installed .md still reference agent-dist/: " + ", ".join(broken[:5])

bootstrap = (installed / "bootstrap/quinotospec-bootstrap.md").read_text(encoding="utf-8")
match = re.search(r"python3 (?:-B )?(\S*skills/quinotospec-contract/contract\.py)", bootstrap)
assert match, "bootstrap does not declare a contract.py preflight"
preflight = Path(match.group(1))
assert preflight.is_absolute(), "preflight path not resolved to install root: " + str(preflight)
assert preflight.is_file(), "preflight script missing: " + str(preflight)
PY

QUINOTOSPEC_OPENCODE_MAJOR=2 bash "$TEMP_ROOT/install.sh" --uninstall --opencode --yes >/dev/null
if [ -e ".opencode" ]; then
    printf 'ERROR: uninstall left an empty managed directory (opencode)\n' >&2
    exit 1
fi

# --- Resto de IDEs: install -> verify -> uninstall en un target aislado ---
roundtrip() {
    local ide="$1"
    local dir="$TEMP_ROOT/target-$ide"
    mkdir -p "$dir"
    cd "$dir"
    bash "$TEMP_ROOT/install.sh" "--$ide" --yes >/dev/null
    bash "$TEMP_ROOT/install.sh" --verify "--$ide" --yes >/dev/null
    bash "$TEMP_ROOT/install.sh" --uninstall "--$ide" --yes >/dev/null
    printf '  %s: install -> verify -> uninstall OK\n' "$ide"
}

for ide in cursor claude cline antigravity; do
    roundtrip "$ide"
done

printf 'Release smoke test passed: %s\n' "$ARCHIVE"
