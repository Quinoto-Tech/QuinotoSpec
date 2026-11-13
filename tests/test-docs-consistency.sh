#!/bin/bash

# Test: check-readme-commands.py
# Verifica que la documentacion no cite comandos inexistentes y que el checker
# realmente detecte una referencia muerta (no que pase por vacio).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHECKER="$PROJECT_ROOT/scripts/check-readme-commands.py"

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
echo "Test: Comandos citados en la documentacion"
echo "=========================================="
echo ""

RC=0
[ -f "$CHECKER" ] || RC=1
check "existe scripts/check-readme-commands.py" "$RC"

RC=0
python3 -B "$CHECKER" --root "$PROJECT_ROOT" --include docs >/dev/null 2>&1 || RC=$?
check "README + docs no citan comandos inexistentes" "$RC"

# El checker debe usar contextos de comando: una ruta de archivo no es un comando.
FIXTURE="$(mktemp -d "$SCRIPT_DIR/temp_docs.XXXXXX")"
trap 'rm -rf "$FIXTURE"' EXIT INT TERM

mkdir -p "$FIXTURE/docs" "$FIXTURE/agent-dist/skills/quinotospec-real" "$FIXTURE/agent-dist/workflows"
printf -- '---\nname: quinotospec-real\n---\n\n# Skill\n' > "$FIXTURE/agent-dist/skills/quinotospec-real/SKILL.md"
printf -- '---\ndescription: demo\n---\n\n# Workflow\n' > "$FIXTURE/agent-dist/workflows/quinotospec.real.md"

cat > "$FIXTURE/README.md" <<'EOF'
# Demo

| Skill | Comando |
|-------|---------|
| Real | `/quinotospec-real` |

Ver `agent-dist/skills/quinotospec-real/SKILL.md` y el paquete `quinotospec-package`.

```bash
@quinotospec.real
```
EOF

RC=0
python3 -B "$CHECKER" --root "$FIXTURE" --file README.md >/dev/null 2>&1 || RC=$?
check "acepta comandos existentes y no confunde rutas de archivo" "$RC"

cat > "$FIXTURE/README.md" <<'EOF'
# Demo

| Skill | Comando |
|-------|---------|
| Fantasma | `/quinotospec-fantasma` |

```bash
@quinotospec.workflow-fantasma
```
EOF

OUTPUT="$(python3 -B "$CHECKER" --root "$FIXTURE" --file README.md 2>&1)"
RC=$?
FAIL_OK=0
[ "$RC" -ne 0 ] || FAIL_OK=1
check "detecta una skill inexistente (exit != 0)" "$FAIL_OK"

RC=0
echo "$OUTPUT" | grep -q "quinotospec-fantasma" || RC=1
check "el error nombra la skill inexistente" "$RC"

RC=0
echo "$OUTPUT" | grep -q "quinotospec.workflow-fantasma" || RC=1
check "el error nombra el workflow inexistente" "$RC"

# JSON estable para otros consumidores (status de ayuda, dashboards).
cat > "$FIXTURE/README.md" <<'EOF'
# Demo

`/quinotospec-real`
EOF
JSON_OK=0
python3 -B "$CHECKER" --root "$FIXTURE" --file README.md --json 2>/dev/null | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["schema_version"] == 1
assert data["problems"] == []
assert data["files"]["README.md"] == 1
' || JSON_OK=1
check "salida --json con schema_version, files y problems" "$JSON_OK"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ check-readme-commands funciona y detecta referencias muertas"
exit 0
