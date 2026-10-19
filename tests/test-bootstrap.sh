#!/bin/bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$ROOT/agent-dist/hooks/session-start.sh"
PLUGIN="$ROOT/agent-dist/plugins/opencode/quinotospec-plugin.js"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

if bash -n "$HOOK"; then
    pass "session-start.sh syntax"
else
    fail "session-start.sh syntax"
fi

for file in \
    "$ROOT/agent-dist/bootstrap/quinotospec-bootstrap.md" \
    "$ROOT/agent-dist/hooks/hooks.json" \
    "$ROOT/agent-dist/hooks/hooks-cursor.json" \
    "$ROOT/agent-dist/hooks/hooks-opencode.json" \
    "$ROOT/agent-dist/hooks/run-hook.cmd" \
    "$ROOT/.cursor-plugin/plugin.json" \
    "$PLUGIN" \
    "$ROOT/agent-dist/plugins/opencode-v2/index.js" \
    "$ROOT/agent-dist/plugins/opencode-v2/package.json"; do
    if [ -f "$file" ]; then
        pass "runtime artifact $(basename "$file")"
    else
        fail "runtime artifact missing: $file"
    fi
done

if python3 - "$ROOT/agent-dist/bootstrap/quinotospec-bootstrap.md" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
assert "/quinotospec.party-mode" in text
assert "--subagents" in text
PY
then
    pass "Party Mode bootstrap integration"
else
    fail "Party Mode bootstrap integration"
fi

for json_file in "$ROOT/agent-dist/hooks/hooks.json" "$ROOT/agent-dist/hooks/hooks-cursor.json" "$ROOT/agent-dist/hooks/hooks-opencode.json" "$ROOT/.cursor-plugin/plugin.json"; do
    if python3 -m json.tool "$json_file" >/dev/null; then
        pass "valid JSON $(basename "$json_file")"
    else
        fail "invalid JSON $json_file"
    fi
done

if printf '{}' | PLUGIN_ROOT="$ROOT/agent-dist" "$HOOK" --platform claude | python3 -c 'import json,sys; d=json.load(sys.stdin); h=d["hookSpecificOutput"]; assert h["hookEventName"] == "SessionStart"; assert "QuinotoSpec Session Bootstrap" in h["additionalContext"]; assert not h["additionalContext"].startswith("---")'; then
    pass "Claude SessionStart payload"
else
    fail "Claude SessionStart payload"
fi

if printf '{}' | PLUGIN_ROOT="$ROOT/agent-dist" "$HOOK" --platform cursor | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["pluginPaths"]; assert "QuinotoSpec Session Bootstrap" in d["additional_context"]'; then
    pass "Cursor sessionStart payload"
else
    fail "Cursor sessionStart payload"
fi

if printf '{}' | PLUGIN_ROOT="$ROOT/agent-dist" sh "$ROOT/agent-dist/hooks/run-hook.cmd" --platform claude | python3 -c 'import json,sys; assert json.load(sys.stdin)["hookSpecificOutput"]["hookEventName"] == "SessionStart"'; then
    pass "run-hook.cmd shell entrypoint"
else
    fail "run-hook.cmd shell entrypoint"
fi

SPACE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/quinotospec bootstrap.XXXXXX")"
mkdir -p "$SPACE_ROOT/bootstrap"
cp "$ROOT/agent-dist/bootstrap/quinotospec-bootstrap.md" "$SPACE_ROOT/bootstrap/quinotospec-bootstrap.md"
if printf '{}' | PLUGIN_ROOT="$SPACE_ROOT" "$HOOK" --platform generic | python3 -c 'import json,sys; assert "QuinotoSpec Session Bootstrap" in json.load(sys.stdin)["additionalContext"]'; then
    pass "PLUGIN_ROOT path with spaces"
else
    fail "PLUGIN_ROOT path with spaces"
fi
rm -rf "$SPACE_ROOT"

if command -v node >/dev/null 2>&1; then
    if node --check "$PLUGIN"; then
        pass "OpenCode plugin syntax"
    else
        fail "OpenCode plugin syntax"
    fi
    if node - "$PLUGIN" "$ROOT/agent-dist" <<'NODE'
const path = require("node:path");
const plugin = require(process.argv[2]);
(async () => {
  const hooks = await plugin({ configDir: process.argv[3] });
  const config = {};
  hooks.config(config);
  if (hooks.toolAliases.TodoWrite !== "todowrite" || hooks.toolAliases.Task !== "task") process.exit(1);
  if (!config.skills.paths.some((item) => item.endsWith("/skills"))) process.exit(1);
  if (!config.instructions.some((item) => item.endsWith("/commands") || item.endsWith("/workflows"))) process.exit(1);
  const messages = [{ role: "user", content: "hello" }];
  await hooks["experimental.chat.messages.transform"]({}, { messages });
  if (!messages[0].content.includes("<quinotospec-bootstrap>")) process.exit(1);
  const before = messages[0].content;
  await hooks["experimental.chat.messages.transform"]({}, { messages });
  if (messages[0].content !== before) process.exit(1);
})();
NODE
    then
        pass "OpenCode plugin config and injection"
    else
        fail "OpenCode plugin config and injection"
    fi
else
    echo "  [SKIP] Node.js not available; plugin runtime test skipped"
fi

# OpenCode v2 plugin test (ESM, zero-dep)
V2_PLUGIN="$ROOT/agent-dist/plugins/opencode-v2/index.js"
if command -v node >/dev/null 2>&1; then
    if node --input-type=module --check "$V2_PLUGIN" 2>/dev/null; then
        pass "OpenCode v2 plugin syntax (ESM)"
    else
        # Fallback: node --check with .mjs extension
        if node --check "$V2_PLUGIN" 2>/dev/null; then
            pass "OpenCode v2 plugin syntax (ESM)"
        else
            fail "OpenCode v2 plugin syntax (ESM)"
        fi
    fi

    # Runtime test with dynamic import (requires ESM)
    # Create a temp dir with proper OpenCode v2 structure: .opencode/plugins/quinotospec/ + .opencode/bootstrap/
    V2_TEST_DIR=$(mktemp -d "${TMPDIR:-/tmp}/quinotospec-v2-test.XXXXXX")
    mkdir -p "$V2_TEST_DIR/.opencode/plugins/quinotospec"
    mkdir -p "$V2_TEST_DIR/.opencode/bootstrap"
    cp "$ROOT/agent-dist/bootstrap/quinotospec-bootstrap.md" "$V2_TEST_DIR/.opencode/bootstrap/quinotospec-bootstrap.md"
    cp "$V2_PLUGIN" "$V2_TEST_DIR/.opencode/plugins/quinotospec/index.js"
    cp "$ROOT/agent-dist/plugins/opencode-v2/package.json" "$V2_TEST_DIR/.opencode/plugins/quinotospec/package.json"

    V2_TEST_SCRIPT=$(cat <<'V2NODE'
import fs from "node:fs";
import path from "node:path";

const pluginPath = process.argv[1];
const root = process.argv[2];

const mod = await import("file://" + path.resolve(pluginPath));
const plugin = mod.default;

let registeredHooks = [];
let capturedEvent = null;

const fakeCtx = {
    location: { directory: root },
    app: { version: "2.0.6" },
    options: { verbose: true },
    session: {
        hook: async (name, callback) => {
            registeredHooks.push(name);
            if (name === "context") {
                const event = { system: [] };
                await callback(event);
                capturedEvent = event;
            }
        },
    },
};

await plugin.setup(fakeCtx);

if (!registeredHooks.includes("context")) process.exit(1);
if (!registeredHooks.includes("compaction")) process.exit(1);
if (!capturedEvent || !capturedEvent.system) process.exit(1);
if (!capturedEvent.system.some(p => p.type === "text" && p.text && p.text.includes("<quinotospec-bootstrap>"))) process.exit(1);
if (capturedEvent.system.some(p => p.type === "text" && p.text && p.text.startsWith("---"))) process.exit(1);

console.log("v2 plugin hooks:", registeredHooks);
V2NODE
)
    if node --input-type=module -e "$V2_TEST_SCRIPT" "$V2_TEST_DIR/.opencode/plugins/quinotospec/index.js" "$V2_TEST_DIR/.opencode" 2>/dev/null; then
        pass "OpenCode v2 plugin context/compaction hooks and bootstrap injection"
    else
        fail "OpenCode v2 plugin context/compaction hooks and bootstrap injection"
    fi
    rm -rf "$V2_TEST_DIR"
else
    echo "  [SKIP] Node.js not available; v2 plugin runtime test skipped"
fi

echo ""
echo "test-bootstrap: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
