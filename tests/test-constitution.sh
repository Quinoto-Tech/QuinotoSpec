#!/bin/bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

TEMPLATE="$ROOT/agent-dist/templates/constitution-template.md"
WORKFLOW="$ROOT/agent-dist/workflows/quinotospec.constitution.md"
SKILL="$ROOT/agent-dist/skills/quinotospec-constitution/SKILL.md"

for file in "$TEMPLATE" "$WORKFLOW" "$SKILL"; do
    if [ -f "$file" ]; then
        pass "constitution artifact $(basename "$file")"
    else
        fail "constitution artifact missing: $file"
    fi
done

if grep -q "Principios Fundamentales" "$TEMPLATE" && grep -q "Restricciones Adicionales" "$TEMPLATE" && grep -q "Quality Gates" "$TEMPLATE" && grep -q "Gobernanza" "$TEMPLATE"; then
    pass "constitution template sections"
else
    fail "constitution template sections incomplete"
fi

if ! grep -q '{{X}}' "$TEMPLATE" && grep -q '{{PROJECT_NAME}}' "$TEMPLATE" && grep -q '{{STACK}}' "$TEMPLATE"; then
    pass "constitution template placeholders"
else
    fail "constitution template placeholders invalid"
fi

if grep -q "discovery/01-stack-profile" "$WORKFLOW" && grep -Eq "reglas.*globales|globales.*reglas" "$WORKFLOW" && grep -q "aprobación explícita" "$WORKFLOW"; then
    pass "constitution workflow gates"
else
    fail "constitution workflow gates incomplete"
fi

for file in "$ROOT/agent-dist/workflows/quinotospec.apply.md" "$ROOT/agent-dist/skills/quinotospec-apply/SKILL.md" "$ROOT/agent-dist/workflows/quinotospec.review.md" "$ROOT/agent-dist/skills/quinotospec-review/SKILL.md" "$ROOT/agent-dist/workflows/quinotospec.archive.md" "$ROOT/agent-dist/skills/quinotospec-archive/SKILL.md"; do
    if grep -q "constitution" "$file"; then
        pass "constitution gate referenced in $(basename "$(dirname "$file")")"
    else
        fail "constitution gate missing in $file"
    fi
done

if grep -q "constitution-before-archive" "$ROOT/agent-dist/templates/schema-template.yaml" && grep -A2 "constitution-before-archive" "$ROOT/agent-dist/templates/schema-template.yaml" | grep -q "BLOCKING"; then
    pass "schema constitution archive rule"
else
    fail "schema constitution archive rule missing"
fi

if grep -q "quinotospec.constitution" "$ROOT/agent-dist/bootstrap/quinotospec-bootstrap.md" && grep -q "Constitutional Compliance" "$ROOT/agent-dist/rules/quinotospec-rules.md"; then
    pass "bootstrap and rule integration"
else
    fail "bootstrap or constitutional rule integration missing"
fi

if python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["workflows"] == 43; assert d["skills"] == 86; assert d["rules"] == 18; assert d["features"]["constitution"] is True' "$ROOT/manifest.json"; then
    pass "manifest constitution counts"
else
    fail "manifest constitution counts"
fi

if grep -Fq "rules:\$FS_RULES" "$ROOT/scripts/update-version.sh" && grep -Fq "templates:\$FS_TEMPLATES" "$ROOT/scripts/update-version.sh"; then
    pass "version sync preserves rules and templates"
else
    fail "version sync drops rules or templates"
fi

echo ""
echo "test-constitution: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
