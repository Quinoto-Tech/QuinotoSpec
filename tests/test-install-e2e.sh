#!/bin/bash

# Test: Round-trip funcional de install.sh (instalar → verificar → desinstalar) en sandbox
# No requiere red ni dependencias externas. Corre 100% en $TMPDIR.

set -u

PASS=0
FAIL=0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="$REPO_ROOT/install.sh"

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

# Pre-flight: syntax check
if bash -n "$INSTALL" 2>/dev/null; then
    pass "install.sh syntax (bash -n)"
else
    fail "install.sh has syntax errors"
fi

# ─────────────────────────────────────────────────────────────
# Round-trip: --opencode --yes (non-interactive install + verify)
# ─────────────────────────────────────────────────────────────
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

echo "Testing install round-trip in sandbox: $SANDBOX"

# All installs run with cwd = sandbox (never pollutes the repo)
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --opencode --yes 2>&1); then
    pass "install.sh --opencode --yes exits 0 (cwd=sandbox)"
else
    fail "install.sh --opencode --yes failed (cwd=sandbox): $OUT"
fi

if [ -d "$SANDBOX/.opencode/commands" ]; then
    pass "workflows/ renamed to commands/ for opencode"
else
    fail "commands/ directory missing for opencode install"
fi

WF_COUNT=$(find "$SANDBOX/.opencode/commands" -name "*.md" 2>/dev/null | wc -l)
if [ "$WF_COUNT" -ge 43 ]; then
    pass "installed workflow count >= 43 ($WF_COUNT)"
else
    fail "installed workflow count too low: $WF_COUNT"
fi

if [ -f "$SANDBOX/.opencode/commands/quinotospec.constitution.md" ]; then
    pass "constitution workflow installed"
else
    fail "constitution workflow missing"
fi

SKILL_COUNT=$(find "$SANDBOX/.opencode/skills" -name "SKILL.md" 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -ge 86 ]; then
    pass "installed skill count >= 86 ($SKILL_COUNT)"
else
    fail "installed skill count too low: $SKILL_COUNT"
fi

for engineering_skill in quinotospec-tdd quinotospec-debug quinotospec-verify-before-done quinotospec-constitution quinotospec-receive-review quinotospec-worktree quinotospec-rules-enforce quinotospec-extension-manager quinotospec-template-resolver quinotospec-update-agents; do
    if [ -f "$SANDBOX/.opencode/skills/$engineering_skill/SKILL.md" ]; then
        pass "engineering skill installed: $engineering_skill"
    else
        fail "engineering skill missing: $engineering_skill"
    fi
done

for extension_helper in \
    "$SANDBOX/.opencode/skills/quinotospec-extension-manager/extension_manager.py" \
    "$SANDBOX/.opencode/skills/quinotospec-template-resolver/template_resolver.py" \
    "$SANDBOX/.opencode/skills/quinotospec-update-agents/update_agents.py"; do
    if [ -f "$extension_helper" ]; then
        pass "extension helper installed: $(basename "$extension_helper")"
    else
        fail "extension helper missing: $extension_helper"
    fi
done

if [ -f "$SANDBOX/.opencode/skills/quinotospec-rules-enforce/evidence_validate.py" ]; then
    pass "evidence validator installed"
else
    fail "evidence validator missing"
fi

if [ -f "$SANDBOX/.opencode/skills/quinotospec-rules-enforce/approval_validate.py" ]; then
    pass "approval validator installed"
else
    fail "approval validator missing"
fi

if [ -f "$SANDBOX/.opencode/skills/quinotospec-backup/backup.py" ]; then
    pass "backup engine installed"
else
    fail "backup engine missing"
fi

if [ -f "$SANDBOX/.opencode/rules/quinotospec-rules.md" ]; then
    pass "rules file installed"
else
    fail "rules/quinotospec-rules.md missing"
fi

if [ -f "$SANDBOX/.opencode/templates/constitution-template.md" ]; then
    pass "constitution template installed"
else
    fail "constitution template missing"
fi

if [ -f "$SANDBOX/.opencode/templates/AGENTS-template.md" ] && [ -f "$SANDBOX/.opencode/templates/config-template.yml" ]; then
    pass "dynamic AGENTS templates installed"
else
    fail "dynamic AGENTS templates missing"
fi

if [ -f "$SANDBOX/.opencode/skills/quinotospec-contract/contract.py" ]; then
    pass "artifact contract helper installed"
else
    fail "quinotospec-contract/contract.py missing"
fi

if [ -f "$SANDBOX/AGENTS.md" ] && grep -q "GENERATED:" "$SANDBOX/AGENTS.md"; then
    pass "dynamic AGENTS.md installed at target root"
else
    fail "dynamic AGENTS.md missing at target root"
fi

if [ -f "$SANDBOX/.opencode/bootstrap/quinotospec-bootstrap.md" ]; then
    pass "session bootstrap installed for opencode"
else
    fail "session bootstrap missing for opencode"
fi

if [ -x "$SANDBOX/.opencode/hooks/session-start.sh" ]; then
    pass "session-start hook installed executable for opencode"
else
    fail "session-start hook missing or not executable for opencode"
fi

if [ -f "$SANDBOX/.opencode/plugins/quinotospec-plugin.js" ]; then
    pass "OpenCode plugin flattened into plugins/"
else
    fail "OpenCode plugin missing from plugins/"
fi

if printf '{}' | PLUGIN_ROOT="$SANDBOX/.opencode" "$SANDBOX/.opencode/hooks/session-start.sh" --platform opencode | python3 -c 'import json,sys; assert "QuinotoSpec Session Bootstrap" in json.load(sys.stdin)["additionalContext"]'; then
    pass "installed session-start hook emits bootstrap"
else
    fail "installed session-start hook did not emit bootstrap"
fi

# Verify mode after install
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --verify --opencode --yes 2>&1); then
    pass "--verify passes after install"
else
    fail "--verify failed after install: $OUT"
fi

INSTALLER_VERSION_EXPECTED=$(grep -o 'INSTALLER_VERSION="[^"]*"' "$INSTALL" | head -1 | cut -d'"' -f2)
if python3 - "$SANDBOX/.opencode/.quinoto-spec/ownership.json" "$SANDBOX/AGENTS.md" "$INSTALLER_VERSION_EXPECTED" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert manifest["schema_version"] == 1
assert manifest["owned"]
assert manifest["agents"]["managed"] is True
assert manifest["installer_version"] == sys.argv[3], manifest["installer_version"]
assert Path(sys.argv[2]).is_file()
for item in manifest["owned"]:
    path = Path(sys.argv[1]).parent.parent / item["path"]
    assert path.is_file(), item["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["path"]
PY
then
    pass "ownership manifest records hashes, version and AGENTS.md"
else
    fail "ownership manifest is incomplete or invalid"
fi

if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --version --opencode 2>&1) && printf '%s' "$OUT" | grep -q "Installed QuinotoSpec v$INSTALLER_VERSION_EXPECTED"; then
    pass "--version reports the installed version"
else
    fail "--version did not report installed version: $OUT"
fi

ROLLBACK_TARGET="$SANDBOX/rollback-target"
mkdir -p "$ROLLBACK_TARGET/.opencode"
printf '%s\n' 'keep-me' > "$ROLLBACK_TARGET/.opencode/user.txt"
ROLLBACK_OUT=$(cd "$ROLLBACK_TARGET" && QUINOTOSPEC_INSTALL_TEST_MODE=true QUINOTOSPEC_INSTALL_FAIL_STAGE=after-config bash "$INSTALL" --opencode --yes 2>&1)
ROLLBACK_RC=$?
if [ "$ROLLBACK_RC" -ne 0 ] && [ -f "$ROLLBACK_TARGET/.opencode/user.txt" ] && [ ! -e "$ROLLBACK_TARGET/.opencode/skills" ] && [ ! -e "$ROLLBACK_TARGET/.opencode/.quinoto-spec/ownership.json" ]; then
    pass "failed transaction restores existing configuration"
else
    fail "transaction rollback failed (rc=$ROLLBACK_RC): $ROLLBACK_OUT"
fi

# Generic IDE install (explicit --generic flag, non-interactive)
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --generic --yes 2>&1) && [ -d "$SANDBOX/.agent/skills" ]; then
    pass "generic install creates .agent/ (with --generic --yes)"
else
    fail "generic install failed: $OUT"
fi

CURSOR_TARGET="$SANDBOX/cursor-target"
mkdir -p "$CURSOR_TARGET/.cursor"
printf '%s\n' '{"version":1,"hooks":{"sessionStart":[{"command":"existing-cursor-hook"}]}}' > "$CURSOR_TARGET/.cursor/hooks.json"
if OUT=$(cd "$CURSOR_TARGET" && bash "$INSTALL" --cursor --yes 2>&1) && [ -f "$CURSOR_TARGET/.cursor/hooks.json" ] && [ -f "$CURSOR_TARGET/.cursor/quinotospec-plugin/.cursor-plugin/plugin.json" ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert any(e.get("command") == "existing-cursor-hook" for e in d["hooks"]["sessionStart"])' "$CURSOR_TARGET/.cursor/hooks.json"; then
    pass "cursor install registers session hook and preserves existing hooks"
else
    fail "cursor install failed or did not preserve hooks: $OUT"
fi

if printf '{}' | PLUGIN_ROOT="$CURSOR_TARGET/.cursor" "$CURSOR_TARGET/.cursor/hooks/session-start.sh" --platform cursor | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["pluginPaths"][0].endswith("/quinotospec-plugin")'; then
    pass "cursor hook points to staged plugin root"
else
    fail "cursor hook did not point to staged plugin root"
fi

CLAUDE_TARGET="$SANDBOX/claude-target"
mkdir -p "$CLAUDE_TARGET/.claude"
printf '%s\n' '{"permissions":{"edit":"deny"}}' > "$CLAUDE_TARGET/.claude/settings.json"
if OUT=$(cd "$CLAUDE_TARGET" && bash "$INSTALL" --claude --yes 2>&1) && [ -f "$CLAUDE_TARGET/.claude/settings.json" ] && [ -x "$CLAUDE_TARGET/.claude/hooks/session-start.sh" ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["permissions"]["edit"] == "deny"; assert d["hooks"]["SessionStart"]' "$CLAUDE_TARGET/.claude/settings.json"; then
    pass "claude install registers SessionStart and preserves settings"
else
    fail "claude install failed or did not preserve settings: $OUT"
fi

GLOBAL_TARGET="$SANDBOX/global-target"
mkdir -p "$GLOBAL_TARGET/home" "$GLOBAL_TARGET/project"
if OUT=$(cd "$GLOBAL_TARGET/project" && HOME="$GLOBAL_TARGET/home" bash "$INSTALL" --cursor --global --yes 2>&1) && [ -f "$GLOBAL_TARGET/home/.cursor/hooks.json" ]; then
    pass "cursor global install uses ~/.cursor"
else
    fail "cursor global install failed: $OUT"
fi

if OUT=$(cd "$GLOBAL_TARGET/project" && HOME="$GLOBAL_TARGET/home" bash "$INSTALL" --verify --cursor --global --yes 2>&1); then
    pass "global verify uses the correct target root"
else
    fail "global verify failed: $OUT"
fi

CONFLICT_TARGET="$SANDBOX/conflict-target"
mkdir -p "$CONFLICT_TARGET"
if OUT=$(cd "$CONFLICT_TARGET" && bash "$INSTALL" --opencode --yes 2>&1); then
    printf '%s\n' 'local modification' >> "$CONFLICT_TARGET/.opencode/rules/quinotospec-rules.md"
    CONFLICT_OUT=$(cd "$CONFLICT_TARGET" && bash "$INSTALL" --opencode --yes 2>&1)
    CONFLICT_RC=$?
    if [ "$CONFLICT_RC" -ne 0 ] && grep -q 'local modification' "$CONFLICT_TARGET/.opencode/rules/quinotospec-rules.md" && [ -f "$CONFLICT_TARGET/.opencode/.quinoto-spec/ownership.json" ]; then
        pass "modified managed file blocks update before commit"
    else
        fail "update conflict protection failed (rc=$CONFLICT_RC): $CONFLICT_OUT"
    fi
else
    fail "could not prepare conflict fixture: $OUT"
fi

SYMLINK_TARGET="$SANDBOX/symlink-target"
mkdir -p "$SYMLINK_TARGET/.cursor"
printf '%s\n' 'external-secret' > "$SYMLINK_TARGET/hooks-external.json"
ln -s "$SYMLINK_TARGET/hooks-external.json" "$SYMLINK_TARGET/.cursor/hooks.json"
SYMLINK_OUT=$(cd "$SYMLINK_TARGET" && bash "$INSTALL" --cursor --yes 2>&1)
SYMLINK_RC=$?
if [ "$SYMLINK_RC" -ne 0 ] && [ "$(<"$SYMLINK_TARGET/hooks-external.json")" = "external-secret" ] && [ ! -e "$SYMLINK_TARGET/.cursor/.quinoto-spec/ownership.json" ]; then
    pass "installer refuses symlinked external configuration"
else
    fail "symlink protection failed (rc=$SYMLINK_RC): $SYMLINK_OUT"
fi

# Foreign symlinks outside managed paths (eg. opencode's own node_modules/.bin)
# must not block installation nor be modified.
FOREIGN_TARGET="$SANDBOX/foreign-symlink-target"
mkdir -p "$FOREIGN_TARGET/.opencode/node_modules/.bin"
ln -s ../pkg/cli.js "$FOREIGN_TARGET/.opencode/node_modules/.bin/opencode"
printf '{"custom":true}\n' > "$FOREIGN_TARGET/.opencode/opencode.jsonc"
if OUT=$(cd "$FOREIGN_TARGET" && bash "$INSTALL" --opencode --yes 2>&1); then
    if [ -L "$FOREIGN_TARGET/.opencode/node_modules/.bin/opencode" ] && [ -f "$FOREIGN_TARGET/.opencode/opencode.jsonc" ] && [ -f "$FOREIGN_TARGET/.opencode/skills/quinotospec-tdd/SKILL.md" ]; then
        pass "foreign symlinks are ignored and preserved during install"
    else
        fail "foreign symlink or config was not preserved"
    fi
else
    fail "installer rejected foreign symlink (rc=$?): $OUT"
fi

# ─────────────────────────────────────────────────────────────
# Uninstall: safe (marker present) and unsafe (no marker)
# ─────────────────────────────────────────────────────────────
printf '%s\n' 'foreign-config' > "$SANDBOX/.opencode/foreign.txt"
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --uninstall --opencode --yes 2>&1); then
    pass "uninstall with --yes exits 0"
else
    fail "uninstall failed: $OUT"
fi

if [ -f "$SANDBOX/.opencode/foreign.txt" ] && [ ! -e "$SANDBOX/.opencode/.quinoto-spec/ownership.json" ] && [ ! -e "$SANDBOX/.opencode/skills" ]; then
    pass "uninstall removes owned files and preserves foreign config"
else
    fail "uninstall was not ownership-safe"
fi

# Uninstall without markers must refuse (protect foreign dir)
mkdir -p "$SANDBOX/.opencode/rules"
echo "not quinoto" > "$SANDBOX/.opencode/rules/other.txt"
UNINSTALL_RC=0
(cd "$SANDBOX" && bash "$INSTALL" --uninstall --opencode --yes >/dev/null 2>&1) || UNINSTALL_RC=$?
if [ "$UNINSTALL_RC" -ne 0 ] && [ -f "$SANDBOX/.opencode/rules/other.txt" ]; then
    pass "uninstall refuses dir without QuinotoSpec markers (exit $UNINSTALL_RC, files intact)"
else
    fail "uninstall accepted a foreign .opencode dir (rc=$UNINSTALL_RC)"
fi

echo ""
echo "test-install-e2e: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
