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

# 2. Validar links en documentacion (delegado a check-links.sh — fuente única de lógica)
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

# 3. Validar consistencia de versiones
echo "--- Version Consistency ---"
if [ -f "$PROJECT_ROOT/manifest.json" ]; then
    MANIFEST_VERSION=$(grep -o '"version": *"[^"]*"' "$PROJECT_ROOT/manifest.json" | head -1 | cut -d'"' -f4)
    INSTALLER_VERSION=$(grep "INSTALLER_VERSION=" "$PROJECT_ROOT/install.sh" | head -1 | cut -d'"' -f2)
    if [ "$MANIFEST_VERSION" = "$INSTALLER_VERSION" ]; then
        echo "  Versions consistent: $MANIFEST_VERSION"
    else
        echo "  MISMATCH: manifest=$MANIFEST_VERSION, installer=$INSTALLER_VERSION"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  manifest.json not found (run scripts/update-version.sh first)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 4. Validar estructura de agent-dist
echo "--- Structure Validation ---"
EXPECTED_COUNTS=("workflows:39" "skills:76" "agents:9")
for expected in "${EXPECTED_COUNTS[@]}"; do
    dir="${expected%%:*}"
    count="${expected##*:}"
    actual=$(find "$PROJECT_ROOT/agent-dist/$dir" -name "*.md" 2>/dev/null | wc -l)
    if [ "$actual" -ge "$count" ]; then
        echo "  $dir: $actual files (expected >= $count)"
    else
        echo "  $dir: $actual files (expected >= $count) - MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# 5. Jormungandr — detectar ciclos en DAG (strict BLOCKING, no-strict warn)
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
