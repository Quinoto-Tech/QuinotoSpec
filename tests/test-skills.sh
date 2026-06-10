#!/bin/bash

# Test: Validación de estructura de todas las skills
# Valida que todas las skills tengan SKILL.md con frontmatter correcto

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$PROJECT_ROOT/agent-dist/skills"

ERRORS=0
TESTED=0

echo "=========================================="
echo "Test: Validación de Skills"
echo "=========================================="
echo ""

if [ ! -d "$SKILLS_DIR" ]; then
    echo "❌ ERROR: Directorio de skills no encontrado: $SKILLS_DIR"
    exit 1
fi

for skill_dir in "$SKILLS_DIR"/*/; do
    if [ ! -d "$skill_dir" ]; then
        continue
    fi
    
    TESTED=$((TESTED + 1))
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"
    errors_in_skill=0
    
    # Check 1: Existe SKILL.md
    if [ ! -f "$skill_file" ]; then
        echo "❌ $skill_name: No tiene SKILL.md"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # Check 2: SKILL.md no está vacío
    if [ ! -s "$skill_file" ]; then
        echo "❌ $skill_name/SKILL.md: Archivo vacío"
        errors_in_skill=1
    fi
    
    # Check 3: Tiene frontmatter YAML
    first_line=$(head -n 1 "$skill_file")
    if [ "$first_line" != "---" ]; then
        echo "❌ $skill_name/SKILL.md: No tiene frontmatter YAML"
        errors_in_skill=1
    fi
    
    # Check 4: Tiene campo 'name' en el frontmatter
    if ! grep -q "^name:" "$skill_file"; then
        echo "❌ $skill_name/SKILL.md: No tiene campo 'name' en el frontmatter"
        errors_in_skill=1
    fi
    
    # Check 5: Tiene campo 'description' en el frontmatter
    if ! grep -q "^description:" "$skill_file"; then
        echo "❌ $skill_name/SKILL.md: No tiene campo 'description' en el frontmatter"
        errors_in_skill=1
    fi
    
    # Check 6: Tiene al menos un heading H1
    if ! grep -q "^# " "$skill_file"; then
        echo "❌ $skill_name/SKILL.md: No tiene heading H1"
        errors_in_skill=1
    fi
    
    # Check 7: Nombre del directorio sigue convención quinotospec-*
    if [[ ! "$skill_name" =~ ^quinotospec- ]]; then
        echo "⚠️  $skill_name: No sigue convención de nombrado quinotospec-<name>"
    fi
    
    # Check 8: El nombre en el frontmatter coincide con el directorio
    frontmatter_name=$(grep "^name:" "$skill_file" | head -1 | sed 's/^name: *//')
    if [ -n "$frontmatter_name" ] && [ "$frontmatter_name" != "$skill_name" ]; then
        echo "⚠️  $skill_name: Nombre en frontmatter ('$frontmatter_name') no coincide con directorio"
    fi
    
    if [ $errors_in_skill -eq 0 ]; then
        echo "✅ $skill_name"
    else
        ERRORS=$((ERRORS + errors_in_skill))
    fi
done

echo ""
echo "=========================================="
echo "Resultados: $TESTED skills testadas, $ERRORES errores"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

echo "✅ Todas las skills son válidas"
exit 0
