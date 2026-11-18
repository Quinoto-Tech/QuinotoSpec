#!/bin/bash

# Test: check-skill-workflow-drift.py (contrato SKDP-m2q8: delegación comando→skill)
# Verifica que el checker acepte stubs canónicos, detecte prompts duplicados
# y reporte skills huérfanas como INFO sin romper el gate.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHECKER="$PROJECT_ROOT/scripts/check-skill-workflow-drift.py"

ERRORS=0
TESTED=0

check() {
    local desc="$1"
    local rc="$2"
    TESTED=$((TESTED + 1))
    if [ "$rc" -eq 0 ]; then
        echo "  ✅ $desc"
    else
        echo "  ❌ $desc"
        ERRORS=$((ERRORS + 1))
    fi
}

echo ""
echo "=========================================="
echo "Test: Skill <-> Workflow Drift (delegación)"
echo "=========================================="
echo ""

RC=0
if [ ! -f "$CHECKER" ]; then RC=1; fi
check "checker existe" "$RC"

RC=0
python3 -B "$CHECKER" --root "$PROJECT_ROOT" --warnings-as-errors >/dev/null 2>&1 || RC=$?
check "el paquete delega 48/49 pares sin drift (review diferido)" "$RC"

RC=0
python3 -B "$PROJECT_ROOT/scripts/generate-command-stubs.py" --root "$PROJECT_ROOT" --check >/dev/null 2>&1 || RC=$?
check "los 48 comandos son el stub canónico generado" "$RC"

FIXTURE="$(mktemp -d "$SCRIPT_DIR/temp_drift.XXXXXX")"
trap 'rm -rf "$FIXTURE"' EXIT INT TERM
mkdir -p "$FIXTURE/agent-dist/workflows" "$FIXTURE/agent-dist/skills/quinotospec-demo" "$FIXTURE/scripts"
cp "$PROJECT_ROOT/scripts/generate-command-stubs.py" "$FIXTURE/scripts/"

STUB="$FIXTURE/agent-dist/workflows/quinotospec.demo.md"
SKILL="$FIXTURE/agent-dist/skills/quinotospec-demo/SKILL.md"

cat > "$SKILL" <<'EOF'
---
name: quinotospec-demo
description: Demo skill
---

# Skill: Demo

Ejecuta `scripts/validator.py` antes de continuar.
EOF

python3 -B "$PROJECT_ROOT/scripts/generate-command-stubs.py" --root "$FIXTURE" --render demo > "$STUB"
cp "$STUB" "$FIXTURE/stub.good.md"

RC=0
python3 -B "$CHECKER" --root "$FIXTURE" >/dev/null 2>&1 || RC=$?
check "deja pasar un stub correcto con su skill" "$RC"

# Regresión: prompt duplicado dentro del comando
cat > "$STUB" <<'EOF'
---
description: Demo workflow
---

# Skill: Demo

Ejecuta `scripts/validator.py` antes de continuar.
EOF
RC=0
python3 -B "$CHECKER" --root "$FIXTURE" >/dev/null 2>&1 || RC=$?
if [ "$RC" -ne 0 ]; then check "detecta prompt duplicado en el workflow" 0; else check "detecta prompt duplicado en el workflow" 1; fi

# Skill sin workflow pareado: INFO, no error
cp "$FIXTURE/stub.good.md" "$STUB"
mkdir -p "$FIXTURE/agent-dist/skills/quinotospec-orphan"
printf '%s\n' '---' 'name: quinotospec-orphan' 'description: huérfana' '---' '# Skill huérfana' > "$FIXTURE/agent-dist/skills/quinotospec-orphan/SKILL.md"
RC=0
python3 -B "$CHECKER" --root "$FIXTURE" >/dev/null 2>&1 || RC=$?
check "skill sin workflow pareado no rompe el gate" "$RC"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Drift checker funciona correctamente"
