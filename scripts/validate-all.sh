#!/bin/bash

# Validate All: Ejecuta todas las validaciones del paquete QuinotoSpec
# Uso: ./scripts/validate-all.sh [--strict]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STRICT=false

for arg in "$@"; do
    case "$arg" in
        --strict) STRICT=true ;;
        -h|--help)
            echo "Usage: $0 [--strict]"
            echo "  --strict  Fail on warnings too"
            exit 0
            ;;
    esac
done

echo "=========================================="
echo "  QuinotoSpec - Full Validation"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# 1. Ejecutar test suite
echo "--- Test Suite ---"
if bash "$SCRIPT_DIR/../tests/run-all-tests.sh"; then
    echo ""
else
    ERRORS=$((ERRORS + 1))
    echo ""
fi

# 2. Ejecutar dispatcher de gobernanza read-only
echo "--- Governance Gate / Artifact Contract ---"
if PYTHONDONTWRITEBYTECODE=1 python3 -B "$PROJECT_ROOT/agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py" \
    --root "$PROJECT_ROOT" \
    --profile package \
    --action preflight \
    --mode strict \
    --check all \
    --json; then
    echo ""
else
    ERRORS=$((ERRORS + 1))
    echo ""
fi

# 3. Validar links en documentacion (delegado a check-links.sh — fuente única de lógica)
# HTTP link checking disponible manualmente: ./scripts/check-links.sh (sin flags)
echo "--- Link Validation (internal) ---"
if bash "$SCRIPT_DIR/check-links.sh" --internal-only; then
    echo ""
else
    if [ "$STRICT" = true ]; then
        ERRORS=$((ERRORS + 1))
    else
        WARNINGS=$((WARNINGS + 1))
    fi
    echo ""
fi

# 4. Validar consistencia de versiones
echo "--- Version Consistency ---"
if [ -f "$PROJECT_ROOT/manifest.json" ]; then
    MANIFEST_VERSION=$(grep -o '"version": *"[^"]*"' "$PROJECT_ROOT/manifest.json" | head -1 | cut -d'"' -f4)
    INSTALLER_VERSION=$(grep "INSTALLER_VERSION=" "$PROJECT_ROOT/install.sh" | head -1 | cut -d'"' -f2)
    VERSION_FILE=$(tr -d '[:space:]' < "$PROJECT_ROOT/.version")
    PLUGIN_VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$PROJECT_ROOT/.cursor-plugin/plugin.json")
    if [ "$MANIFEST_VERSION" = "$INSTALLER_VERSION" ] && [ "$VERSION_FILE" = "$MANIFEST_VERSION" ] && [ "$PLUGIN_VERSION" = "$MANIFEST_VERSION" ]; then
        echo "  Versions consistent: $MANIFEST_VERSION"
    else
        echo "  MISMATCH: manifest=$MANIFEST_VERSION, installer=$INSTALLER_VERSION, .version=$VERSION_FILE, cursor-plugin=$PLUGIN_VERSION"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  manifest.json not found (run scripts/update-version.sh first)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 5. Validar estructura de agent-dist
echo "--- Structure Validation ---"
EXPECTED_COUNTS=("workflows:43" "skills:86" "rules:18" "agents:9" "templates:13")
for expected in "${EXPECTED_COUNTS[@]}"; do
    dir="${expected%%:*}"
    count="${expected##*:}"
    case "$dir" in
        skills)
            actual=$(find "$PROJECT_ROOT/agent-dist/$dir" -type f -name "SKILL.md" 2>/dev/null | wc -l)
            ;;
        rules)
            actual=$(grep -c '^# ' "$PROJECT_ROOT/agent-dist/rules/quinotospec-rules.md" 2>/dev/null || true)
            ;;
        templates)
            actual=$(find "$PROJECT_ROOT/agent-dist/$dir" -maxdepth 1 -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | wc -l)
            ;;
        *)
            actual=$(find "$PROJECT_ROOT/agent-dist/$dir" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l)
            ;;
    esac
    if [ "$actual" -ge "$count" ]; then
        echo "  $dir: $actual files (expected >= $count)"
    else
        echo "  $dir: $actual files (expected >= $count) - MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# 6. Validar runtime de bootstrap
RUNTIME_FILES=(
    "agent-dist/bootstrap/quinotospec-bootstrap.md"
    "agent-dist/hooks/session-start.sh"
    "agent-dist/hooks/hooks.json"
    "agent-dist/hooks/hooks-cursor.json"
    "agent-dist/hooks/hooks-opencode.json"
    "agent-dist/plugins/opencode/quinotospec-plugin.js"
    ".cursor-plugin/plugin.json"
)
for file in "${RUNTIME_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "  $file: present"
    else
        echo "  $file: MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done
if bash -n "$PROJECT_ROOT/agent-dist/hooks/session-start.sh"; then
    echo "  session-start.sh: syntax OK"
else
    echo "  session-start.sh: syntax ERROR"
    ERRORS=$((ERRORS + 1))
fi
for file in "$PROJECT_ROOT"/agent-dist/hooks/*.json "$PROJECT_ROOT/.cursor-plugin/plugin.json"; do
    if python3 -m json.tool "$file" >/dev/null; then
        echo "  $(basename "$file"): JSON OK"
    else
        echo "  $(basename "$file"): JSON ERROR"
        ERRORS=$((ERRORS + 1))
    fi
done
if command -v node >/dev/null 2>&1; then
    if node --check "$PROJECT_ROOT/agent-dist/plugins/opencode/quinotospec-plugin.js"; then
        echo "  quinotospec-plugin.js: syntax OK"
    else
        echo "  quinotospec-plugin.js: syntax ERROR"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  quinotospec-plugin.js: Node.js unavailable, syntax check skipped"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 7. Jormungandr — detectar ciclos en DAG (strict BLOCKING, no-strict warn)
echo "--- Jormungandr (DAG Cycle Check) ---"
JORMUNGANDR_SCHEMA="$PROJECT_ROOT/agent-dist/templates/schema-template.yaml"
if [ -f "$JORMUNGANDR_SCHEMA" ]; then
    if python3 "$PROJECT_ROOT/agent-dist/skills/quinotospec-jormungandr/check.py" "$JORMUNGANDR_SCHEMA" 2>&1; then
        echo "  Jormungandr: DAG OK"
    else
        if [ "$STRICT" = true ]; then
            echo "  Jormungandr: CYCLE detected (BLOCKING in --strict)"
            ERRORS=$((ERRORS + 1))
        else
            echo "  Jormungandr: CYCLE detected (WARNING)"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi
else
    echo "  Jormungandr: schema not found, skip"
fi
echo ""

# Summary
echo "=========================================="
echo "  Results: $ERRORS errors, $WARNINGS warnings"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

if [ "$STRICT" = true ] && [ $WARNINGS -gt 0 ]; then
    exit 1
fi

echo "All validations passed"
exit 0
