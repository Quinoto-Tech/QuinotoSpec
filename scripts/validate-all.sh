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

# 2. Validar links en documentacion
echo "--- Link Validation ---"
BROKEN_LINKS=0
for md_file in "$PROJECT_ROOT"/*.md "$PROJECT_ROOT"/agent-dist/**/*.md; do
    if [ ! -f "$md_file" ]; then continue; fi
    while IFS= read -r link; do
        if [[ "$link" =~ ^https?:// ]]; then
            if ! curl -sf --max-time 5 "$link" > /dev/null 2>&1; then
                echo "  BROKEN: $link (in $(basename "$md_file"))"
                BROKEN_LINKS=$((BROKEN_LINKS + 1))
            fi
        fi
    done < <(grep -oP '\[.*?\]\(\K[^)]+' "$md_file" 2>/dev/null || true)
done
if [ $BROKEN_LINKS -eq 0 ]; then
    echo "  All links valid"
else
    WARNINGS=$((WARNINGS + BROKEN_LINKS))
    echo "  $BROKEN_LINKS potentially broken links"
fi
echo ""

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
EXPECTED_COUNTS=("workflows:38" "skills:31" "agents:9")
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
