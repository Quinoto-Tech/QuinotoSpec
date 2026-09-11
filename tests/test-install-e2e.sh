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
if [ "$WF_COUNT" -ge 39 ]; then
    pass "installed workflow count >= 39 ($WF_COUNT)"
else
    fail "installed workflow count too low: $WF_COUNT"
fi

SKILL_COUNT=$(find "$SANDBOX/.opencode/skills" -name "SKILL.md" 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -ge 76 ]; then
    pass "installed skill count >= 76 ($SKILL_COUNT)"
else
    fail "installed skill count too low: $SKILL_COUNT"
fi

if [ -f "$SANDBOX/.opencode/rules/quinotospec-rules.md" ]; then
    pass "rules file installed"
else
    fail "rules/quinotospec-rules.md missing"
fi

if [ -f "$SANDBOX/AGENTS.md" ]; then
    pass "AGENTS.md installed at target root"
else
    fail "AGENTS.md missing at target root"
fi

# Verify mode after install
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --verify --opencode --yes 2>&1); then
    pass "--verify passes after install"
else
    fail "--verify failed after install: $OUT"
fi

# Generic IDE install (explicit --generic flag, non-interactive)
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --generic --yes 2>&1) && [ -d "$SANDBOX/.agent/skills" ]; then
    pass "generic install creates .agent/ (with --generic --yes)"
else
    fail "generic install failed: $OUT"
fi

# ─────────────────────────────────────────────────────────────
# Uninstall: safe (marker present) and unsafe (no marker)
# ─────────────────────────────────────────────────────────────
if OUT=$(cd "$SANDBOX" && bash "$INSTALL" --uninstall --opencode --yes 2>&1); then
    pass "uninstall with --yes exits 0"
else
    fail "uninstall failed: $OUT"
fi

if [ ! -d "$SANDBOX/.opencode" ]; then
    pass "config dir removed after uninstall"
else
    fail ".opencode still exists after uninstall"
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
