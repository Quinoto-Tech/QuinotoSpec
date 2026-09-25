#!/bin/bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

for file in \
    "$ROOT/agent-dist/skills/quinotospec-tdd/SKILL.md" \
    "$ROOT/agent-dist/skills/quinotospec-tdd/testing-anti-patterns.md" \
    "$ROOT/agent-dist/skills/quinotospec-tdd/examples/tdd-typescript.md" \
    "$ROOT/agent-dist/skills/quinotospec-tdd/examples/tdd-python.md" \
    "$ROOT/agent-dist/skills/quinotospec-tdd/examples/tdd-rust.md" \
    "$ROOT/agent-dist/skills/quinotospec-debug/SKILL.md" \
    "$ROOT/agent-dist/skills/quinotospec-debug/root-cause-tracing.md" \
    "$ROOT/agent-dist/skills/quinotospec-debug/defense-in-depth.md" \
    "$ROOT/agent-dist/skills/quinotospec-debug/condition-based-waiting.md" \
    "$ROOT/agent-dist/skills/quinotospec-verify-before-done/SKILL.md"; do
    if [ -f "$file" ]; then
        pass "engineering artifact $(basename "$file")"
    else
        fail "missing engineering artifact: $file"
    fi
done

if grep -q "Iron Law" "$ROOT/agent-dist/skills/quinotospec-tdd/SKILL.md" && grep -q "RED.*GREEN.*REFACTOR" "$ROOT/agent-dist/skills/quinotospec-tdd/SKILL.md"; then
    pass "TDD Iron Law and cycle"
else
    fail "TDD Iron Law or cycle missing"
fi

if grep -q "cuatro fases" "$ROOT/agent-dist/skills/quinotospec-debug/SKILL.md" && grep -q "tres hipótesis" "$ROOT/agent-dist/skills/quinotospec-debug/SKILL.md"; then
    pass "debug four-phase method and escalation"
else
    fail "debug method incomplete"
fi

if grep -q "Gate de cinco pasos" "$ROOT/agent-dist/skills/quinotospec-verify-before-done/SKILL.md" && grep -q "evidencia fresca" "$ROOT/agent-dist/skills/quinotospec-verify-before-done/SKILL.md"; then
    pass "verify-before-done gate and evidence"
else
    fail "verify-before-done gate incomplete"
fi

for file in "$ROOT/agent-dist/rules/quinotospec-rules.md" "$ROOT/agent-dist/workflows/quinotospec.apply.md" "$ROOT/agent-dist/skills/quinotospec-apply/SKILL.md"; do
    if grep -q "quinotospec-tdd" "$file" && grep -q "quinotospec-debug" "$file" && grep -q "quinotospec-verify-before-done" "$file"; then
        pass "engineering gates referenced in $(basename "$(dirname "$file")")"
    else
        fail "engineering gates missing in $file"
    fi
done

if grep -q "Paso 0 — Verificar antes de modificar estados" "$ROOT/agent-dist/skills/quinotospec-mark-done/SKILL.md" && grep -q "verify-before-done" "$ROOT/agent-dist/skills/quinotospec-mark-done/SKILL.md"; then
    pass "mark-done verification gate is before state changes"
else
    fail "mark-done verification gate missing"
fi

if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["skills"] == 86; assert d["rules"] == 18; assert d["workflows"] == 43' "$ROOT/manifest.json"; then
    pass "manifest engineering counts"
else
    fail "manifest engineering counts"
fi

echo ""
echo "test-engineering-skills: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
