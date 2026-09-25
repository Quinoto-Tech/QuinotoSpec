#!/bin/bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

SKILL="$ROOT/agent-dist/skills/quinotospec-worktree/SKILL.md"
APPLY_WORKFLOW="$ROOT/agent-dist/workflows/quinotospec.apply.md"
APPLY_SKILL="$ROOT/agent-dist/skills/quinotospec-apply/SKILL.md"
BOOTSTRAP="$ROOT/agent-dist/bootstrap/quinotospec-bootstrap.md"

if [ -f "$SKILL" ]; then
    pass "worktree skill exists"
else
    fail "worktree skill missing"
fi

if grep -q '^name: quinotospec-worktree$' "$SKILL" && grep -q '^description:' "$SKILL" && grep -q '^# ' "$SKILL"; then
    pass "worktree skill metadata"
else
    fail "worktree skill metadata incomplete"
fi

for step in "Step 0" "Step 1" "Step 2"; do
    if grep -q "$step" "$SKILL"; then
        pass "$step documented"
    else
        fail "$step missing"
    fi
done

if grep -q 'GIT_DIR' "$SKILL" && grep -q 'GIT_COMMON' "$SKILL" && grep -q 'GIT_DIR != GIT_COMMON' "$SKILL"; then
    pass "existing isolation detection"
else
    fail "existing isolation detection missing"
fi

for directory in '.worktrees/' 'worktrees/' 'config/quinotospec/worktrees/'; do
    if grep -Fq "$directory" "$SKILL"; then
        pass "directory priority $directory"
    else
        fail "directory priority missing: $directory"
    fi
done

if grep -q 'git check-ignore' "$SKILL" && grep -q 'No uses.*--force' "$SKILL"; then
    pass "path safety and ignore verification"
else
    fail "path safety verification missing"
fi

if grep -q 'quinotospec-stack-detect' "$SKILL" && grep -q '01-stack-profile.md' "$SKILL" && grep -q 'Tras la confirmación' "$SKILL" && grep -q 'npm ci' "$SKILL"; then
    pass "stack detection and project setup"
else
    fail "stack detection or project setup missing"
fi

if grep -q 'Baseline limpia' "$SKILL" && grep -q 'baseline fallida no es un RED TDD' "$SKILL"; then
    pass "clean baseline gate"
else
    fail "clean baseline gate missing"
fi

if grep -q 'mktemp -d' "$SKILL" && grep -q '700' "$SKILL" && grep -q 'sandbox' "$SKILL"; then
    pass "permission fallback sandbox"
else
    fail "permission fallback sandbox missing"
fi

if grep -q 'git push' "$SKILL" && grep -q 'git branch -D' "$SKILL" && grep -q 'rm -rf' "$SKILL"; then
    pass "destructive operation safeguards"
else
    fail "destructive operation safeguards missing"
fi

if grep -q 'quinotospec-worktree' "$APPLY_WORKFLOW" && grep -q 'USE_WORKTREE=true' "$APPLY_WORKFLOW" && grep -q 'quinotospec-worktree' "$APPLY_SKILL" && grep -q 'USE_WORKTREE=true' "$APPLY_SKILL"; then
    pass "Apply integration"
else
    fail "Apply integration missing"
fi

if grep -q 'quinotospec-tdd' "$APPLY_WORKFLOW" && grep -q 'quinotospec-mark-done' "$APPLY_WORKFLOW" && grep -q 'No implementes en el checkout original' "$APPLY_WORKFLOW"; then
    pass "Apply context and lifecycle safeguards"
else
    fail "Apply context safeguards missing"
fi

if grep -q 'quinotospec-worktree' "$BOOTSTRAP" && grep -q 'git check-ignore' "$BOOTSTRAP"; then
    pass "bootstrap integration"
else
    fail "bootstrap integration missing"
fi

if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["skills"] == 86; assert d["features"]["worktree"] is True; assert d["capability_maturity"]["worktree"] == "prompt-only"' "$ROOT/manifest.json"; then
    pass "manifest worktree metadata"
else
    fail "manifest worktree metadata"
fi

if grep -q 'skills:86' "$ROOT/scripts/validate-all.sh" && grep -q 'skill_count" -lt 86' "$ROOT/install.sh"; then
    pass "inventory thresholds synchronized"
else
    fail "inventory thresholds not synchronized"
fi

echo ""
echo "test-worktree: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
