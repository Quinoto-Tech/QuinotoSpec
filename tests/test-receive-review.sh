#!/bin/bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

SKILL="$ROOT/agent-dist/skills/quinotospec-receive-review/SKILL.md"
REVIEW_WORKFLOW="$ROOT/agent-dist/workflows/quinotospec.review.md"
REVIEW_SKILL="$ROOT/agent-dist/skills/quinotospec-review/SKILL.md"
APPLY_WORKFLOW="$ROOT/agent-dist/workflows/quinotospec.apply.md"
APPLY_SKILL="$ROOT/agent-dist/skills/quinotospec-apply/SKILL.md"

if [ -f "$SKILL" ]; then
    pass "receive-review skill exists"
else
    fail "receive-review skill missing"
fi
if [ -f "$REVIEW_WORKFLOW" ]; then
    pass "review workflow exists"
else
    fail "review workflow missing"
fi

if grep -qi "no.*acuerdo performativo\|acuerdo performativo" "$SKILL" && grep -qi "no aceptes comentarios sin verificarlos" "$SKILL"; then
    pass "forbidden performative responses"
else
    fail "forbidden performative responses missing"
fi

if grep -q "Source-Specific Handling" "$SKILL" && grep -q "Human partner" "$SKILL" && grep -q "Reviewer externo" "$SKILL"; then
    pass "source-specific feedback handling"
else
    fail "source-specific feedback handling missing"
fi

if grep -Fq 'If reviewer suggests “implementing properly”, grep codebase for actual usage first.' "$SKILL" && grep -q "YAGNI Check" "$SKILL"; then
    pass "YAGNI check"
else
    fail "YAGNI check missing"
fi

previous=0
for step in READ UNDERSTAND VERIFY EVALUATE RESPOND IMPLEMENT; do
    line=$(grep -n -m 1 -E "^[0-9]+\\. \\*\\*${step}\\*\\*:" "$SKILL" | cut -d: -f1)
    if [ -n "$line" ] && [ "$line" -gt "$previous" ]; then
        pass "response step ${step}"
        previous="$line"
    else
        fail "response step order: ${step}"
    fi
done

if grep -q "Fixed\\. \[Brief description\]" "$SKILL" && grep -q "No agregues agradecimientos" "$SKILL"; then
    pass "correct feedback acknowledgment"
else
    fail "correct feedback acknowledgment missing"
fi

if grep -q "quinotospec-receive-review" "$REVIEW_WORKFLOW" && grep -q "quinotospec-receive-review" "$REVIEW_SKILL"; then
    pass "review integration"
else
    fail "review integration missing"
fi

if grep -q "quinotospec-receive-review" "$APPLY_WORKFLOW" && grep -q "quinotospec-receive-review" "$APPLY_SKILL"; then
    pass "apply delegation"
else
    fail "apply delegation missing"
fi

if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["skills"] == 86; assert d["features"]["receive_review"] is True; assert d["capability_maturity"]["receive_review"] == "prompt-only"' "$ROOT/manifest.json"; then
    pass "manifest receive-review metadata"
else
    fail "manifest receive-review metadata"
fi

if grep -q '40 core' "$ROOT/scripts/update-version.sh"; then
    pass "architecture core count preserved"
else
    fail "architecture core count is stale"
fi

echo ""
echo "test-receive-review: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
