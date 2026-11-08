#!/bin/bash

# Test: check-skill-workflow-drift.py
# Verifica que el checker detecte drift funcional real y deje pasar el paquete intacto.

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
echo "Test: Skill <-> Workflow Drift"
echo "=========================================="
echo ""

[ -f "$CHECKER" ]
check "checker existe" "$?"

python3 -B "$CHECKER" --root "$PROJECT_ROOT" --warnings-as-errors >/dev/null 2>&1
check "el paquete no tiene drift funcional skill<->workflow" "$?"

FIXTURE="$(mktemp -d "$SCRIPT_DIR/temp_drift.XXXXXX")"
trap 'rm -rf "$FIXTURE"' EXIT INT TERM

mkdir -p "$FIXTURE/agent-dist/workflows" "$FIXTURE/agent-dist/skills/quinotospec-demo"

cat > "$FIXTURE/agent-dist/workflows/quinotospec.demo.md" <<'EOF'
---
description: Demo workflow
---

# Workflow: Demo

Ejecuta `scripts/validator.py` antes de continuar.
EOF

cat > "$FIXTURE/agent-dist/skills/quinotospec-demo/SKILL.md" <<'EOF'
---
name: quinotospec-demo
description: Demo skill
---

# Skill: Demo

Sin pasos de ejecucion.
EOF

RC=0
python3 -B "$CHECKER" --root "$FIXTURE" >/dev/null 2>&1 || RC=$?
[ "$RC" -eq 1 ]
check "detecta drift cuando la skill omite un script del workflow" "$?"

cat >> "$FIXTURE/agent-dist/skills/quinotospec-demo/SKILL.md" <<'EOF'

Ejecuta `scripts/validator.py`.
EOF

python3 -B "$CHECKER" --root "$FIXTURE" >/dev/null 2>&1
check "deja pasar el par cuando los scripts coinciden" "$?"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Drift checker funciona correctamente"
