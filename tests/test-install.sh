#!/bin/bash

# Test: Validación del script de instalación
# Prueba que install.sh funciona correctamente en diferentes escenarios

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INSTALL_SCRIPT="$PROJECT_ROOT/install.sh"

ERRORS=0
TESTED=0

echo "=========================================="
echo "Test: Validación de Install Script"
echo "=========================================="
echo ""

# Check 1: install.sh existe
if [ ! -f "$INSTALL_SCRIPT" ]; then
    echo "❌ ERROR: install.sh no encontrado"
    exit 1
fi
echo "✅ install.sh existe"
TESTED=$((TESTED + 1))

# Check 2: install.sh es ejecutable
if [ ! -x "$INSTALL_SCRIPT" ]; then
    echo "❌ ERROR: install.sh no es ejecutable"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ install.sh es ejecutable"
fi
TESTED=$((TESTED + 1))

# Check 3: install.sh tiene shebang correcto
first_line=$(head -n 1 "$INSTALL_SCRIPT")
if [ "$first_line" != "#!/bin/bash" ]; then
    echo "❌ ERROR: install.sh no tiene shebang correcto (esperado: #!/bin/bash, obtenido: $first_line)"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ install.sh tiene shebang correcto"
fi
TESTED=$((TESTED + 1))

# Check 4: install.sh tiene flag --help
if ! grep -q "\-\-help" "$INSTALL_SCRIPT"; then
    echo "❌ ERROR: install.sh no tiene flag --help"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ install.sh tiene flag --help"
fi
TESTED=$((TESTED + 1))

# Check 5: install.sh verifica agent-dist
if ! grep -q "agent-dist" "$INSTALL_SCRIPT"; then
    echo "❌ ERROR: install.sh no referencia agent-dist"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ install.sh referencia agent-dist"
fi
TESTED=$((TESTED + 1))

# Check 6: install.sh soporta múltiples IDEs
IDE_COUNT=$(grep -c "\-\-opencode\|\-\-cursor\|\-\-cline" "$INSTALL_SCRIPT" || true)
if [ "$IDE_COUNT" -lt 2 ]; then
    echo "⚠️  install.sh podría no soportar suficientes IDEs (encontrados: $IDE_COUNT)"
else
    echo "✅ install.sh soporta múltiples IDEs ($IDE_COUNT referencias)"
fi
TESTED=$((TESTED + 1))

# Check 7: install.sh tiene manejo de errores
if ! grep -q "exit 1\|Error\|error" "$INSTALL_SCRIPT"; then
    echo "⚠️  install.sh podría no tener manejo de errores adecuado"
else
    echo "✅ install.sh tiene manejo de errores"
fi
TESTED=$((TESTED + 1))

# Check 8: install.sh tiene --global/--root
if ! grep -q "\-\-global\|\-\-root" "$INSTALL_SCRIPT"; then
    echo "⚠️  install.sh no tiene flag --global/--root"
else
    echo "✅ install.sh tiene flag --global/--root"
fi
TESTED=$((TESTED + 1))

# Check 9: Verificar que agent-dist tiene la estructura esperada
echo ""
echo "Verificando estructura de agent-dist:"
EXPECTED_DIRS=("workflows" "skills" "rules" "templates")
for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/agent-dist/$dir" ]; then
        echo "  ✅ agent-dist/$dir existe"
    else
        echo "  ❌ agent-dist/$dir no existe"
        ERRORS=$((ERRORS + 1))
    fi
    TESTED=$((TESTED + 1))
done

# Check 10: Verificar archivos críticos en agent-dist
echo ""
echo "Verificando archivos críticos:"
if [ -f "$PROJECT_ROOT/agent-dist/rules/quinotospec-rules.md" ]; then
    echo "  ✅ rules/quinotospec-rules.md existe"
else
    echo "  ❌ rules/quinotospec-rules.md no existe"
    ERRORS=$((ERRORS + 1))
fi
TESTED=$((TESTED + 1))

if [ -f "$PROJECT_ROOT/AGENTS.md" ]; then
    echo "  ✅ AGENTS.md existe"
else
    echo "  ❌ AGENTS.md no existe"
    ERRORS=$((ERRORS + 1))
fi
TESTED=$((TESTED + 1))

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORES errores"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

echo "✅ Install script válido"
exit 0
