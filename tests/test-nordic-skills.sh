#!/bin/bash

# Test: Validación end-to-end de las skills nordicas con lógica real
# (Mimir, Valkyrie, Bifrost). A diferencia de las otras suites, estos scripts
# ejecutan código Python real contra fixtures/repos efímeros, y varios de los
# comandos devuelven exit code != 0 a propósito (BLOCKING, drift, warnings).
# Por eso esta suite NO usa `set -e`: cada check captura su propio resultado
# y lo contabiliza en ERRORS, en vez de abortar el script al primer comando
# que "falla" intencionalmente.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FIXTURE_SRC="$SCRIPT_DIR/fixtures/quinoto-spec-sample"
MIMIR_DIR="$PROJECT_ROOT/agent-dist/skills/quinotospec-mimir"
VALKYRIE_DIR="$PROJECT_ROOT/agent-dist/skills/quinotospec-valkyrie"
BIFROST_DIR="$PROJECT_ROOT/agent-dist/skills/quinotospec-bifrost"

ERRORS=0
TESTED=0

# Directorio de trabajo efímero DENTRO del workspace (no en /tmp) para que
# funcione bajo sandboxes que solo permiten escritura dentro del proyecto.
# El prefijo "temp_" ya está cubierto por .gitignore.
WORKDIR="$(mktemp -d "$SCRIPT_DIR/temp_nordic_test.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT INT TERM

echo ""
echo "=========================================="
echo "Test: Skills Nordicas (Mimir, Valkyrie, Bifrost)"
echo "=========================================="
echo ""

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

if [ ! -d "$FIXTURE_SRC" ]; then
    echo "❌ ERROR: fixture no encontrada en $FIXTURE_SRC"
    exit 1
fi

# ==========================================================================
# Mimir -- índice BM25 con citas exactas (file:line)
# ==========================================================================
echo "--- Mimir (índice BM25) ---"

MIMIR_WORK="$WORKDIR/mimir-fixture"
cp -R "$FIXTURE_SRC" "$MIMIR_WORK"

INDEX_OUT=$(python3 "$MIMIR_DIR/index.py" --root "$MIMIR_WORK" 2>&1)
RC=0
echo "$INDEX_OUT" | grep -q "chunks de" || RC=$?
check "index.py genera chunks desde la fixture" "$RC"

if [ -f "$MIMIR_WORK/.quinoto-spec/mimir/index.json" ]; then
    check "index.json fue generado" 0
else
    check "index.json fue generado" 1
fi

if [ -f "$MIMIR_WORK/.quinoto-spec/mimir/mimir-sources.json" ]; then
    check "mimir-sources.json fue generado (para reindex incremental)" 0
else
    check "mimir-sources.json fue generado (para reindex incremental)" 1
fi

SEARCH_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" "TOTP 2FA" --cite 2>&1)
RC=0
echo "$SEARCH_OUT" | grep -q "delta-specs/auth/spec.md" || RC=$?
check "search.py 'TOTP 2FA' devuelve el delta-spec de auth (file:line)" "$RC"

RC=0
echo "$SEARCH_OUT" | grep -qi "TOTP" || RC=$?
check "search.py --cite incluye texto citado verbatim con 'TOTP'" "$RC"

TRACE_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" --trace AUTH-a1b2 2>&1)
RC=0
echo "$TRACE_OUT" | grep -q "proposal creado" || RC=$?
check "search.py --trace AUTH-a1b2 muestra el linaje de la propuesta" "$RC"
RC=0
echo "$TRACE_OUT" | grep -q "delta-spec: auth" || RC=$?
check "search.py --trace incluye el delta-spec de auth en el linaje" "$RC"

CHECK_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" --check 2>&1)
CHECK_RC=$?
RC=0
echo "$CHECK_OUT" | grep -q "indice actualizado" || RC=$?
check "search.py --check confirma índice fresco tras reindex" "$RC"
if [ "$CHECK_RC" -eq 0 ]; then
    check "search.py --check devuelve exit 0 cuando el índice está fresco" 0
else
    check "search.py --check devuelve exit 0 cuando el índice está fresco" 1
fi

# Modificar un archivo fuente y confirmar que --check detecta el drift (STALE)
sleep 1
echo "" >> "$MIMIR_WORK/.quinoto-spec/discovery/02-overview.md"
STALE_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" --check 2>&1)
STALE_RC=$?
RC=0
echo "$STALE_OUT" | grep -q "STALE" || RC=$?
check "search.py --check detecta archivo modificado (STALE)" "$RC"
if [ "$STALE_RC" -eq 1 ]; then
    check "search.py --check devuelve exit 1 cuando hay drift" 0
else
    check "search.py --check devuelve exit 1 cuando hay drift" 1
fi

echo ""

# ==========================================================================
# Valkyrie -- triage y scoring de propuestas
# ==========================================================================
echo "--- Valkyrie (triage/scoring) ---"

VALKYRIE_JSON=$(python3 "$VALKYRIE_DIR/rank.py" --root "$FIXTURE_SRC" --json 2>&1)

AUTH_SCORE=$(echo "$VALKYRIE_JSON" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for r in data.get('ranking', []):
        if 'sample-auth' in r['slug']:
            print(r['score'])
            break
except (json.JSONDecodeError, KeyError):
    pass
" 2>/dev/null)
LEGACY_SCORE=$(echo "$VALKYRIE_JSON" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for r in data.get('ranking', []):
        if 'sample-legacy' in r['slug']:
            print(r['score'])
            break
except (json.JSONDecodeError, KeyError):
    pass
" 2>/dev/null)

if [ -n "$AUTH_SCORE" ] && [ -n "$LEGACY_SCORE" ]; then
    check "rank.py --json produce scores numéricos para ambas propuestas" 0
else
    check "rank.py --json produce scores numéricos para ambas propuestas" 1
fi

if [ -n "$AUTH_SCORE" ] && [ -n "$LEGACY_SCORE" ]; then
    if [ "$AUTH_SCORE" -gt "$LEGACY_SCORE" ]; then
        check "sample-auth (score $AUTH_SCORE) rankea por encima de sample-legacy (score $LEGACY_SCORE)" 0
    else
        check "sample-auth (score $AUTH_SCORE) rankea por encima de sample-legacy (score $LEGACY_SCORE)" 1
    fi
else
    check "sample-auth rankea por encima de sample-legacy (scores no disponibles, ver JSON arriba)" 1
fi

TABLE_OUT=$(python3 "$VALKYRIE_DIR/rank.py" --root "$FIXTURE_SRC" 2>&1)
RC=0
echo "$TABLE_OUT" | grep -q "sample-auth" || RC=$?
check "rank.py (tabla) lista sample-auth" "$RC"
RC=0
echo "$TABLE_OUT" | grep -q "sample-legacy" || RC=$?
check "rank.py (tabla) lista sample-legacy" "$RC"
RC=0
echo "$TABLE_OUT" | grep -q "candidate archive" || RC=$?
check "rank.py detecta al menos una propuesta stale -> candidate archive" "$RC"

echo ""

# --- Valkyrie: detección de ciclos en el DAG de schema.yaml (Kahn) ---
echo "--- Valkyrie (detección de ciclos DAG) ---"

CYCLE_WORK="$WORKDIR/valkyrie-cycle"
cp -R "$FIXTURE_SRC" "$CYCLE_WORK"
cat > "$CYCLE_WORK/.quinoto-spec/schema.yaml" <<'EOF'
name: cycle-fixture
version: 1
artifacts:
  - id: a
    requires:
      - b
  - id: b
    requires:
      - a
EOF

CYCLE_OUT=$(python3 "$VALKYRIE_DIR/rank.py" --root "$CYCLE_WORK" 2>&1)
echo "$CYCLE_OUT" | grep -q "BLOCKING"
check "rank.py detecta ciclo sintético a -> b -> a (BLOCKING)" $?
echo "$CYCLE_OUT" | grep -q "blocked (ciclo"
check "rank.py marca next_action='blocked (ciclo...)' cuando hay ciclo" $?

echo ""

# ==========================================================================
# Bifrost -- federación multi-repo (2 repos git efímeros + origin bare local)
# ==========================================================================
echo "--- Bifrost (federación multi-repo) ---"

BIFROST_WORK="$WORKDIR/bifrost"
mkdir -p "$BIFROST_WORK"

git init --bare -q "$BIFROST_WORK/origin.git"

setup_repo() {
    local name="$1"
    local dir="$BIFROST_WORK/$name"
    mkdir -p "$dir"
    git -C "$dir" init -q
    git -C "$dir" config user.email "test@quinotospec.local"
    git -C "$dir" config user.name "QuinotoSpec Test"
    git -C "$dir" remote add origin "$BIFROST_WORK/origin.git"
    echo "# $name" > "$dir/README.md"
    git -C "$dir" add README.md
    git -C "$dir" commit -q -m "init $name"
    git -C "$dir" push -q origin HEAD:refs/heads/main
}

setup_repo "auth"
setup_repo "payments"

# "auth" tiene schema + una propuesta activa En Curso (para --status: OK/en curso)
mkdir -p "$BIFROST_WORK/auth/.quinoto-spec/proposals/sample-x"
cp "$FIXTURE_SRC/.quinoto-spec/schema.yaml" "$BIFROST_WORK/auth/.quinoto-spec/schema.yaml"
cat > "$BIFROST_WORK/auth/.quinoto-spec/proposals/sample-x/proposal.md" <<'EOF'
# Propuesta: Sample X

**Prefijo:** SAMP-x1x1
**Estado**: En Curso
**Prioridad**: P1
EOF
# "payments" se deja sin .quinoto-spec/ a propósito (para probar MISSING schema)

INIT_OUT=$(python3 "$BIFROST_DIR/bifrost.py" --init --root "$BIFROST_WORK" --repos "auth:auth,payments:payments" --name "test-falange" 2>&1)
INIT_RC=$?
RC=0
echo "$INIT_OUT" | grep -q "federation.yaml creado" || RC=$?
check "bifrost.py --init crea federation.yaml" "$RC"
if [ "$INIT_RC" -eq 0 ]; then
    check "bifrost.py --init devuelve exit 0" 0
else
    check "bifrost.py --init devuelve exit 0" 1
fi
if [ -f "$BIFROST_WORK/.quinoto-spec/federation.yaml" ]; then
    check "federation.yaml existe en disco" 0
else
    check "federation.yaml existe en disco" 1
fi

STATUS_OUT=$(python3 "$BIFROST_DIR/bifrost.py" --status --root "$BIFROST_WORK" 2>&1)
RC=0
echo "$STATUS_OUT" | grep -q "^auth " || RC=$?
check "bifrost.py --status lista el repo 'auth'" "$RC"
RC=0
echo "$STATUS_OUT" | grep -q "1 activas" || RC=$?
check "bifrost.py --status cuenta la propuesta activa de 'auth'" "$RC"
RC=0
echo "$STATUS_OUT" | grep -q "^payments " || RC=$?
check "bifrost.py --status lista el repo 'payments'" "$RC"
RC=0
echo "$STATUS_OUT" | grep -q "MISSING schema" || RC=$?
check "bifrost.py --status detecta schema faltante en 'payments'" "$RC"

# --sync: agregar una nota en 'auth' (sin pushear a mano) y verificar que
# bifrost.py --sync la propague a origin y de ahi a 'payments'.
git -C "$BIFROST_WORK/auth" notes --ref=quinotospec-events add -m "evento de test desde auth" HEAD

SYNC_OUT=$(python3 "$BIFROST_DIR/bifrost.py" --sync --root "$BIFROST_WORK" 2>&1)
SYNC_RC=$?
RC=0
echo "$SYNC_OUT" | grep -q "auth | push: OK | fetch: OK" || RC=$?
check "bifrost.py --sync hace push+fetch OK para 'auth'" "$RC"
RC=0
echo "$SYNC_OUT" | grep -q "payments | push:.*| fetch: OK" || RC=$?
check "bifrost.py --sync hace fetch OK para 'payments' (recibe la nota via origin)" "$RC"
if [ "$SYNC_RC" -eq 0 ]; then
    check "bifrost.py --sync devuelve exit 0 (sin errores reales)" 0
else
    check "bifrost.py --sync devuelve exit 0 (sin errores reales)" 1
fi

AUTH_HEAD=$(git -C "$BIFROST_WORK/auth" rev-parse HEAD)
git -C "$BIFROST_WORK/payments" notes --ref=quinotospec-events show "$AUTH_HEAD" > /dev/null 2>&1
check "'payments' recibió efectivamente la nota de 'auth' via origin (git notes show)" $?

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

echo "✅ Mimir, Valkyrie y Bifrost funcionan correctamente end-to-end"
exit 0
