#!/bin/bash

# Test: Validación de reglas
# Valida que el archivo de reglas tenga estructura correcta y las reglas esperadas

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RULES_FILE="$PROJECT_ROOT/agent-dist/rules/quinotospec-rules.md"

ERRORS=0

echo "=========================================="
echo "Test: Validación de Reglas"
echo "=========================================="
echo ""

# Check 1: El archivo existe
if [ ! -f "$RULES_FILE" ]; then
    echo "❌ ERROR: Archivo de reglas no encontrado: $RULES_FILE"
    exit 1
fi

echo "✅ Archivo de reglas existe"

# Check 2: No está vacío
if [ ! -s "$RULES_FILE" ]; then
    echo "❌ ERROR: Archivo de reglas vacío"
    exit 1
fi

echo "✅ Archivo de reglas no está vacío"

# Check 3: Tiene frontmatter con trigger
if ! grep -q "^trigger:" "$RULES_FILE"; then
    echo "❌ ERROR: No tiene campo 'trigger' en el frontmatter"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Tiene campo 'trigger' en frontmatter"
fi

# Check 4: Tiene heading H1
if ! grep -q "^# " "$RULES_FILE"; then
    echo "❌ ERROR: No tiene heading H1"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Tiene heading H1"
fi

# Check 5: Contiene las reglas esperadas
EXPECTED_RULES=(
    "Gestión del Changelog"
    "Gestión de Prefijos"
    "Product Agreement"
    "No Sobreescribir"
    "Validación de Estado"
    "Convención de Archivado"
    "Nombrado de Branches"
    "Aprobación de Configuración"
    "Validación Pre-Workflow"
    "Backup Pre-Refactor"
    "Validación de Sintaxis Pre-Apply"
    "Protección de Archivos Archivados"
)

echo ""
echo "Verificando reglas esperadas:"
for rule in "${EXPECTED_RULES[@]}"; do
    if grep -qi "$rule" "$RULES_FILE"; then
        echo "  ✅ Regla encontrada: $rule"
    else
        echo "  ❌ Regla faltante: $rule"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 6: Cada regla tiene formato consistente (- **Regla** o - **SEVERIDAD**)
echo ""
echo "Verificando formato de reglas:"
rule_count=$(grep -c "^# " "$RULES_FILE" || true)
bold_count=$(grep -c "\*\*" "$RULES_FILE" || true)

if [ "$bold_count" -lt 8 ]; then
    echo "⚠️  Las reglas podrían no tener formato consistente (se esperan al menos 8 bloques con **bold**)"
else
    echo "✅ Formato de reglas consistente ($bold_count bloques con formato)"
fi

echo ""
echo "=========================================="
echo "Resultados: $ERRORES errores encontrados"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

echo "✅ Todas las reglas son válidas"
exit 0
