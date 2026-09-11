#!/bin/bash

# Test: checkers funcionales — Jormungandr (check.py), Huginn-Muninn (check.sh),
# y update-version.sh --dry-run

set -u

PASS=0
FAIL=0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass() { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

JORMUNDGANDR="$REPO_ROOT/agent-dist/skills/quinotospec-jormungandr/check.py"
HUGINN="$REPO_ROOT/agent-dist/skills/quinotospec-huginn-muninn/check.sh"
NORNS="$REPO_ROOT/scripts/update-version.sh"

# ─────────────────────────────────────────────────────────────
# Jormungandr: DAG aciclico del schema real → OK, exit 0
# ─────────────────────────────────────────────────────────────
if python3 "$JORMUNDGANDR" "$REPO_ROOT/agent-dist/templates/schema-template.yaml" >/dev/null 2>&1; then
    pass "jormungandr: schema-template.yaml acyclic (exit 0)"
else
    fail "jormungandr: real schema flagged as cyclic or errored"
fi

# ─────────────────────────────────────────────────────────────
# Jormungandr: DAG con ciclo → exit 1, reporta CYCLE
# ─────────────────────────────────────────────────────────────
cat > "$TMP/cyclic.yaml" <<'EOF'
artifacts:
  - id: a
    requires: [c]
  - id: b
    requires: [a]
  - id: c
    requires: [b]
EOF
OUT=$(python3 "$JORMUNDGANDR" "$TMP/cyclic.yaml" 2>&1)
RC=$?
if [ "$RC" -ne 0 ] && echo "$OUT" | grep -q "CYCLE"; then
    pass "jormungandr: cycle detected (exit $RC, CYCLE reported)"
else
    fail "jormungandr: cycle NOT detected (rc=$RC, out=$OUT)"
fi

# ─────────────────────────────────────────────────────────────
# Jormungandr: DAG lineal aciclico → OK
# ─────────────────────────────────────────────────────────────
cat > "$TMP/linear.yaml" <<'EOF'
artifacts:
  - id: a
    requires: []
  - id: b
    requires: [a]
  - id: c
    requires: [b]
EOF
if OUT=$(python3 "$JORMUNDGANDR" "$TMP/linear.yaml" 2>&1) && echo "$OUT" | grep -q "OK"; then
    pass "jormungandr: linear DAG passes ($OUT)"
else
    fail "jormungandr: linear DAG failed: $OUT"
fi

# ─────────────────────────────────────────────────────────────
# Huginn-Muninn: check.sh emite JSON valido con S_final
# ─────────────────────────────────────────────────────────────
if OUT=$(bash "$HUGINN" 2>&1) && echo "$OUT" | python3 -c "
import sys, json
data = json.loads(sys.stdin.read().strip().splitlines()[-1])
assert 'S_final' in data, 'missing S_final'
assert isinstance(data['S_final'], (int, float)), 'S_final not numeric'
" 2>/dev/null; then
    pass "huginn-muninn: valid JSON with numeric S_final"
else
    fail "huginn-muninn: invalid JSON output"
fi

# ─────────────────────────────────────────────────────────────
# update-version.sh --dry-run: no escribe nada, exit 0
# ─────────────────────────────────────────────────────────────
VERSION_BEFORE=$(cat "$REPO_ROOT/.version")
if OUT=$(bash "$NORNS" 9.9.9 --dry-run 2>&1) && echo "$OUT" | grep -q "DRY-RUN"; then
    pass "update-version: --dry-run reports dry-run mode"
else
    fail "update-version: --dry-run output unexpected: $OUT"
fi

VERSION_AFTER=$(cat "$REPO_ROOT/.version")
if [ "$VERSION_BEFORE" = "$VERSION_AFTER" ]; then
    pass "update-version: --dry-run did not modify .version ($VERSION_AFTER)"
else
    fail "update-version: --dry-run MUTATED .version ($VERSION_BEFORE -> $VERSION_AFTER)"
fi

# update-version.sh: version invalida → exit 1
if ! bash "$NORNS" "no-semver" --dry-run >/dev/null 2>&1; then
    pass "update-version: rejects non-semver version"
else
    fail "update-version: accepted non-semver version"
fi

# update-version.sh: sin args → exit 1
if ! bash "$NORNS" >/dev/null 2>&1; then
    pass "update-version: missing arg exits non-zero"
else
    fail "update-version: missing arg exited 0"
fi

echo ""
echo "test-checkers: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
