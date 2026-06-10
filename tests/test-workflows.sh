#!/bin/bash

# Test: Validación de sintaxis de todos los workflows
# Valida que todos los archivos .md en agent-dist/workflows/ tengan estructura correcta

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WORKFLOWS_DIR="$PROJECT_ROOT/agent-dist/workflows"

ERRORS=0
TESTED=0

echo "=========================================="
echo "Test: Validación de Workflows"
echo "=========================================="
echo ""

if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "❌ ERROR: Directorio de workflows no encontrado: $WORKFLOWS_DIR"
    exit 1
fi

for workflow in "$WORKFLOWS_DIR"/*.md; do
    if [ ! -f "$workflow" ]; then
        continue
    fi
    
    TESTED=$((TESTED + 1))
    filename=$(basename "$workflow")
    errors_in_file=0
    
    # Check 1: El archivo no está vacío
    if [ ! -s "$workflow" ]; then
        echo "❌ $filename: Archivo vacío"
        errors_in_file=1
    fi
    
    # Check 2: Tiene frontmatter YAML (--- al inicio)
    first_line=$(head -n 1 "$workflow")
    if [ "$first_line" != "---" ]; then
        echo "❌ $filename: No tiene frontmatter YAML (debe empezar con ---)"
        errors_in_file=1
    fi
    
    # Check 3: El frontmatter se cierra correctamente
    if ! grep -q "^---$" "$workflow"; then
        echo "❌ $filename: Frontmatter no se cierra (falta --- de cierre)"
        errors_in_file=1
    fi
    
    # Check 4: Tiene campo 'description' en el frontmatter
    if ! grep -q "^description:" "$workflow"; then
        echo "❌ $filename: No tiene campo 'description' en el frontmatter"
        errors_in_file=1
    fi
    
    # Check 5: Tiene al menos un heading H1
    if ! grep -q "^# " "$workflow"; then
        echo "❌ $filename: No tiene heading H1"
        errors_in_file=1
    fi
    
    # Check 6: Nombre sigue convención quinotospec.*.md
    if [[ ! "$filename" =~ ^quinotospec\..+\.md$ ]]; then
        echo "⚠️  $filename: No sigue convención de nombrado quinotospec.<name>.md"
    fi
    
    # Check 7: No tiene caracteres de control no imprimibles
    if grep -Pq '[\x00-\x08\x0B\x0C\x0E-\x1F]' "$workflow" 2>/dev/null; then
        echo "❌ $filename: Contiene caracteres de control no imprimibles"
        errors_in_file=1
    fi
    
    if [ $errors_in_file -eq 0 ]; then
        echo "✅ $filename"
    else
        ERRORS=$((ERRORS + errors_in_file))
    fi
done

echo ""
echo "=========================================="
echo "Resultados: $TESTED workflows testados, $ERRORES errores"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

echo "✅ Todos los workflows son válidos"
exit 0
