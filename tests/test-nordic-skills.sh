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
echo "$INDEX_OUT" | grep -q "chunks de"
check "index.py genera chunks desde la fixture" $?

[ -f "$MIMIR_WORK/.quinoto-spec/mimir/index.json" ]
check "index.json fue generado" $?

[ -f "$MIMIR_WORK/.quinoto-spec/mimir/mimir-sources.json" ]
check "mimir-sources.json fue generado (para reindex incremental)" $?

SEARCH_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" "TOTP 2FA" --cite 2>&1)
echo "$SEARCH_OUT" | grep -q "delta-specs/auth/spec.md"
check "search.py 'TOTP 2FA' devuelve el delta-spec de auth (file:line)" $?

echo "$SEARCH_OUT" | grep -qi "TOTP"
check "search.py --cite incluye texto citado verbatim con 'TOTP'" $?

TRACE_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" --trace AUTH-a1b2 2>&1)
echo "$TRACE_OUT" | grep -q "proposal creado"
check "search.py --trace AUTH-a1b2 muestra el linaje de la propuesta" $?
echo "$TRACE_OUT" | grep -q "delta-spec: auth"
check "search.py --trace incluye el delta-spec de auth en el linaje" $?

CHECK_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" --check 2>&1)
CHECK_RC=$?
echo "$CHECK_OUT" | grep -q "índice actualizado"
check "search.py --check confirma índice fresco tras reindex" $?
[ "$CHECK_RC" -eq 0 ]
check "search.py --check devuelve exit 0 cuando el índice está fresco" $?

# Modificar un archivo fuente y confirmar que --check detecta el drift (STALE)
sleep 1
echo "" >> "$MIMIR_WORK/.quinoto-spec/discovery/02-overview.md"
STALE_OUT=$(python3 "$MIMIR_DIR/search.py" --root "$MIMIR_WORK" --check 2>&1)
STALE_RC=$?
echo "$STALE_OUT" | grep -q "STALE"
check "search.py --check detecta archivo modificado (STALE)" $?
[ "$STALE_RC" -eq 1 ]
check "search.py --check devuelve exit 1 cuando hay drift" $?

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

[ -n "$AUTH_SCORE" ] && [ -n "$LEGACY_SCORE" ]
check "rank.py --json produce scores numéricos para ambas propuestas" $?

if [ -n "$AUTH_SCORE" ] && [ -n "$LEGACY_SCORE" ]; then
    [ "$AUTH_SCORE" -gt "$LEGACY_SCORE" ]
    check "sample-auth (score $AUTH_SCORE) rankea por encima de sample-legacy (score $LEGACY_SCORE)" $?
else
    check "sample-auth rankea por encima de sample-legacy (scores no disponibles, ver JSON arriba)" 1
fi

TABLE_OUT=$(python3 "$VALKYRIE_DIR/rank.py" --root "$FIXTURE_SRC" 2>&1)
echo "$TABLE_OUT" | grep -q "sample-auth"
check "rank.py (tabla) lista sample-auth" $?
echo "$TABLE_OUT" | grep -q "sample-legacy"
check "rank.py (tabla) lista sample-legacy" $?
echo "$TABLE_OUT" | grep -q "candidate archive"
check "rank.py detecta al menos una propuesta stale -> candidate archive" $?

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
echo "$INIT_OUT" | grep -q "federation.yaml creado"
check "bifrost.py --init crea federation.yaml" $?
[ "$INIT_RC" -eq 0 ]
check "bifrost.py --init devuelve exit 0" $?
[ -f "$BIFROST_WORK/.quinoto-spec/federation.yaml" ]
check "federation.yaml existe en disco" $?

STATUS_OUT=$(python3 "$BIFROST_DIR/bifrost.py" --status --root "$BIFROST_WORK" 2>&1)
echo "$STATUS_OUT" | grep -q "^auth "
check "bifrost.py --status lista el repo 'auth'" $?
echo "$STATUS_OUT" | grep -q "1 activas"
check "bifrost.py --status cuenta la propuesta activa de 'auth'" $?
echo "$STATUS_OUT" | grep -q "^payments "
check "bifrost.py --status lista el repo 'payments'" $?
echo "$STATUS_OUT" | grep -q "MISSING schema"
check "bifrost.py --status detecta schema faltante en 'payments'" $?

# --sync: agregar una nota en 'auth' (sin pushear a mano) y verificar que
# bifrost.py --sync la propague a origin y de ahi a 'payments'.
git -C "$BIFROST_WORK/auth" notes --ref=quinotospec-events add -m "evento de test desde auth" HEAD

SYNC_OUT=$(python3 "$BIFROST_DIR/bifrost.py" --sync --root "$BIFROST_WORK" 2>&1)
SYNC_RC=$?
echo "$SYNC_OUT" | grep -q "auth | push: OK | fetch: OK"
check "bifrost.py --sync hace push+fetch OK para 'auth'" $?
echo "$SYNC_OUT" | grep -q "payments | push:.*| fetch: OK"
check "bifrost.py --sync hace fetch OK para 'payments' (recibe la nota via origin)" $?
[ "$SYNC_RC" -eq 0 ]
check "bifrost.py --sync devuelve exit 0 (sin errores reales)" $?

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
