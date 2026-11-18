#!/usr/bin/env bash
# Suite: Rutas de validadores resueltas tras instalar QuinotoSpec (VPAT-k4m7)
# RED esperado con la version actual: los .md instalados referencian agent-dist/
# y los entrypoints con dependencias de layout no encuentran su payload.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

FAILED_CHECKS=()
FAILURES=0

fail_check() {
    FAILURES=$((FAILURES + 1))
    FAILED_CHECKS+=("$1")
    printf '  \033[31m❌ %s\033[0m\n' "$1" >&2
}

pass_check() {
    printf '  \033[32m✅ %s\033[0m\n' "$1"
}

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/quinotospec-installed-paths.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

# ---------------------------------------------------------------------------
# Fixture: instalar el paquete en un directorio temporal (instalacion local
# de OpenCode, patron de scripts/smoke-release.sh: cwd = root de instalacion).
# ---------------------------------------------------------------------------
APP_DIR="$TMP_ROOT/app"
mkdir -p "$APP_DIR"
cp "$ROOT/install.sh" "$APP_DIR/install.sh"
cp -R "$ROOT/agent-dist" "$APP_DIR/agent-dist"

echo "▶ Instalando QuinotoSpec en $APP_DIR (instalacion local OpenCode)"
if ! (cd "$APP_DIR" && bash "$APP_DIR/install.sh" --opencode --yes >/dev/null 2>&1); then
    fail_check "install.sh --opencode --yes corre en temp dir"
fi

INSTALLED="$APP_DIR/.opencode"
if [ ! -d "$INSTALLED/skills/quinotospec-contract" ]; then
    fail_check "payload instalado contiene skills/quinotospec-contract"
    printf '\n\033[31mResumen: %s fallo(s)\033[0m\n' "$FAILURES"
    exit 1
fi

# Fixture: proyecto del usuario SIN agent-dist/ (el escenario real post-instalacion),
# inicializado con .quinoto-spec/ minimo para el contrato de artefactos.
FIXTURE="$TMP_ROOT/fixture"
mkdir -p "$FIXTURE/.quinoto-spec/changelog"
printf '# Registro de Prefijos\n\n| Prefijo | Nombre | Fecha |\n|---------|--------|-------|\n' > "$FIXTURE/.quinoto-spec/prefix-registry.md"
cat > "$FIXTURE/.quinoto-spec/changelog/2026-11-17-TEST-fixture.md" <<'EOF'
---
date: 2026-11-17
prefix: TEST-t000
slug: fixture
format: v2
type: change
---

## [2026-11-17] - Fixture Entry

### Resumen
- Entrada minima para el fixture del suite.

**Tiempo Ahorrado**: ~0h (IA: 0min vs Humano: 0h)
EOF

# ---------------------------------------------------------------------------
# Check A (RED): ningun .md instalado puede referenciar agent-dist/
# ---------------------------------------------------------------------------
echo "▶ Check A: referencias agent-dist/ en .md instalados"
BROKEN_COUNT=$({ grep -rl --include='*.md' 'agent-dist/' "$INSTALLED" 2>/dev/null || true; } | wc -l | tr -d ' ')
if [ "$BROKEN_COUNT" -eq 0 ]; then
    pass_check "ningun .md instalado referencia agent-dist/"
else
    fail_check "$BROKEN_COUNT archivo(s) .md instalados todavia referencian agent-dist/ (rutas rotas)"
    grep -rl --include='*.md' 'agent-dist/' "$INSTALLED" 2>/dev/null | awk 'NR<=5 {print "      " $0}' >&2
fi

# ---------------------------------------------------------------------------
# Check B (RED): el preflight del bootstrap instalado es ejecutable desde un
# proyecto sin agent-dist/
# ---------------------------------------------------------------------------
echo "▶ Check B: preflight del bootstrap instalado es ejecutable"
BOOT="$INSTALLED/bootstrap/quinotospec-bootstrap.md"
if [ ! -f "$BOOT" ]; then
    fail_check "bootstrap instalado existe en bootstrap/quinotospec-bootstrap.md"
else
    PREFLIGHT_SCRIPT=$(grep -oE 'python3 (-B )?[A-Za-z0-9._/~+-]*skills/quinotospec-contract/contract\.py' "$BOOT" | awk 'NR==1 {print; exit}' | sed 's/^python3 //; s/^-B //')
    if [ -z "$PREFLIGHT_SCRIPT" ]; then
        fail_check "bootstrap instalado declara comando de preflight de contract.py"
    elif (cd "$FIXTURE" && python3 -B "$PREFLIGHT_SCRIPT" validate --root . --strict >/dev/null 2>&1); then
        pass_check "preflight del bootstrap corre desde proyecto sin agent-dist/ ($PREFLIGHT_SCRIPT)"
    else
        fail_check "preflight del bootstrap corre desde proyecto sin agent-dist/ (script referenciado: $PREFLIGHT_SCRIPT)"
    fi
fi

# ---------------------------------------------------------------------------
# Check C (RED): update_agents.py regenera AGENTS.md desde un proyecto
# instalado usando la raiz del propio script cuando root/agent-dist no existe
# ---------------------------------------------------------------------------
echo "▶ Check C: update_agents.py con fallback a la raiz de instalacion"
UPDATE_AGENTS="$INSTALLED/skills/quinotospec-update-agents/update_agents.py"
if (cd "$FIXTURE" && python3 -B "$UPDATE_AGENTS" --root . --output AGENTS.md --write >/dev/null 2>&1) \
    && grep -q 'quinotospec-apply' "$FIXTURE/AGENTS.md" 2>/dev/null; then
    pass_check "update_agents.py genera AGENTS.md con inventario real desde proyecto instalado"
else
    fail_check "update_agents.py genera AGENTS.md con inventario real desde proyecto instalado (hoy: config/agent-dist ausentes)"
fi

# ---------------------------------------------------------------------------
# Check D (RED): template_resolver.py resuelve skills core desde un proyecto
# instalado
# ---------------------------------------------------------------------------
echo "▶ Check D: template_resolver.py con fallback a la raiz de instalacion"
RESOLVER="$INSTALLED/skills/quinotospec-template-resolver/template_resolver.py"
RESOLVED_PATH=$(cd "$FIXTURE" && python3 -B "$RESOLVER" --root . --kind skill --name quinotospec-contract --json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("path",""))' 2>/dev/null || true)
if [ -n "$RESOLVED_PATH" ] && [ -f "$RESOLVED_PATH" ]; then
    pass_check "template_resolver.py resuelve skill core desde proyecto instalado ($RESOLVED_PATH)"
else
    fail_check "template_resolver.py resuelve skill core desde proyecto instalado (hoy: root/agent-dist ausente)"
fi

# ---------------------------------------------------------------------------
# Check E (regresion cero): donde root/agent-dist SI existe, la resolucion por
# root sigue funcionando igual que hoy (semantica del repo fuente intacta)
# ---------------------------------------------------------------------------
echo "▶ Check E: regresion cero cuando root/agent-dist existe"
if python3 -B "$ROOT/agent-dist/skills/quinotospec-template-resolver/template_resolver.py" --root "$ROOT" --kind skill --name quinotospec-contract --json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("path") else 1)' >/dev/null 2>&1 \
    && (cd "$APP_DIR" && python3 -B "$INSTALLED/skills/quinotospec-update-agents/update_agents.py" --root . --output AGENTS.md --write >/dev/null 2>&1) \
    && grep -q 'quinotospec-apply' "$APP_DIR/AGENTS.md" 2>/dev/null; then
    pass_check "con root/agent-dist presente, update_agents y template_resolver siguen resolviendo por root (regresion cero)"
else
    fail_check "con root/agent-dist presente, update_agents y template_resolver siguen resolviendo por root (regresion cero)"
fi

# ---------------------------------------------------------------------------
# Check F: reinstall es idempotente (la normalizacion re-corrida es un no-op)
# ---------------------------------------------------------------------------
echo "▶ Check F: reinstall idempotente"
if (cd "$APP_DIR" && bash "$APP_DIR/install.sh" --opencode --yes >/dev/null 2>&1) \
    && [ "$({ grep -rl --include='*.md' 'agent-dist/' "$INSTALLED" 2>/dev/null || true; } | wc -l | tr -d ' ')" -eq 0 ]; then
    pass_check "reinstall sobre instalacion normalizada mantiene 0 referencias agent-dist/"
else
    fail_check "reinstall sobre instalacion normalizada mantiene 0 referencias agent-dist/"
fi

# ---------------------------------------------------------------------------
# Check G: ruta de instalacion con espacios y & no corrompe el rewrite
# ---------------------------------------------------------------------------
echo "▶ Check G: instalacion en ruta con espacios y &"
APP_SPACES="$TMP_ROOT/dir con espacio&tests"
mkdir -p "$APP_SPACES"
cp "$ROOT/install.sh" "$APP_SPACES/install.sh"
cp -R "$ROOT/agent-dist" "$APP_SPACES/agent-dist"
if (cd "$APP_SPACES" && bash "$APP_SPACES/install.sh" --opencode --yes >/dev/null 2>&1) \
    && [ -f "$APP_SPACES/.opencode/skills/quinotospec-contract/contract.py" ] \
    && [ "$({ grep -rl --include='*.md' 'agent-dist/' "$APP_SPACES/.opencode" 2>/dev/null || true; } | wc -l | tr -d ' ')" -eq 0 ]; then
    pass_check "rewrite correcto en ruta con espacio y &"
else
    fail_check "rewrite correcto en ruta con espacio y &"
fi

# ---------------------------------------------------------------------------
# Check H: el rewrite NO toca codigo (.py/.sh/.js/.json son byte-intactos)
# ---------------------------------------------------------------------------
echo "▶ Check H: codigo instalado byte-intacto"
CODE_DRIFT=0
while IFS= read -r -d '' installed_file; do
    relative="${installed_file#"$INSTALLED/"}"
    case "$relative" in
        *.py|*.sh|*.js|*.json) ;;
        *) continue ;;
    esac
    if ! cmp -s "$ROOT/agent-dist/$relative" "$installed_file" 2>/dev/null; then
        # los plugins/hooks pueden moverse en runtime; solo compara los que existen en source
        if [ -f "$ROOT/agent-dist/$relative" ]; then
            CODE_DRIFT=$((CODE_DRIFT + 1))
            printf '      drift: %s\n' "$relative" >&2
        fi
    fi
done < <(find "$INSTALLED" -type f -print0 2>/dev/null)
if [ "$CODE_DRIFT" -eq 0 ]; then
    pass_check "ningun .py/.sh/.js/.json instalado difiere del source"
else
    fail_check "$CODE_DRIFT archivo(s) de codigo instalado difieren del source (el rewrite no debe tocarlos)"
fi

# ---------------------------------------------------------------------------
# Check I: uninstall es coherente con el manifest post-rewrite
# ---------------------------------------------------------------------------
echo "▶ Check I: uninstall coherente"
if (cd "$APP_DIR" && bash "$APP_DIR/install.sh" --uninstall --opencode --yes >/dev/null 2>&1) \
    && [ ! -d "$INSTALLED/skills" ] && [ ! -d "$INSTALLED/rules" ]; then
    pass_check "uninstall remueve los archivos gestionados reescritos sin conflictos"
else
    fail_check "uninstall remueve los archivos gestionados reescritos sin conflictos"
fi

# ---------------------------------------------------------------------------
# Check J: el stub del comando resuelve su skill en instalacion local
# ---------------------------------------------------------------------------
echo "▶ Check J: stub -> skill en instalacion local"
LOCAL_CMD="$APP_SPACES/.opencode/commands/quinotospec.status.md"
LOCAL_SKILL="$APP_SPACES/.opencode/skills/quinotospec-status/SKILL.md"
if [ -f "$LOCAL_CMD" ] && [ -f "$LOCAL_SKILL" ] \
    && grep -q '[$]ARGUMENTS' "$LOCAL_CMD" \
    && grep -q 'skills/quinotospec-status/SKILL.md' "$LOCAL_CMD" \
    && ! grep -q '^# Workflow:' "$LOCAL_CMD"; then
    pass_check "comando instalado delega en SKILL.md local con \$ARGUMENTS"
else
    fail_check "comando instalado delega en SKILL.md local con \$ARGUMENTS"
fi

# ---------------------------------------------------------------------------
# Check K: lo mismo en instalacion GLOBAL (HOME aislado en temp dir)
# ---------------------------------------------------------------------------
echo "▶ Check K: stub -> skill en instalacion global"
HOME_DIR="$TMP_ROOT/home"
mkdir -p "$HOME_DIR"
if HOME="$HOME_DIR" bash "$APP_DIR/install.sh" --opencode --global --yes >/dev/null 2>&1 \
    && [ -f "$HOME_DIR/.config/opencode/commands/quinotospec.status.md" ] \
    && [ -f "$HOME_DIR/.config/opencode/skills/quinotospec-status/SKILL.md" ] \
    && grep -q '[$]ARGUMENTS' "$HOME_DIR/.config/opencode/commands/quinotospec.status.md" \
    && grep -q 'skills/quinotospec-status/SKILL.md' "$HOME_DIR/.config/opencode/commands/quinotospec.status.md"; then
    pass_check "comando global delega en SKILL.md global con \$ARGUMENTS"
else
    fail_check "comando global delega en SKILL.md global con \$ARGUMENTS"
fi

# ---------------------------------------------------------------------------
echo ""
if [ "$FAILURES" -eq 0 ]; then
    printf '\033[32m✅ installed-paths: todos los checks pasaron\033[0m\n'
    exit 0
fi
printf '\033[31m❌ installed-paths: %s check(s) fallaron:\033[0m\n' "$FAILURES" >&2
for item in "${FAILED_CHECKS[@]}"; do
    printf '   - %s\n' "$item" >&2
done
exit 1
