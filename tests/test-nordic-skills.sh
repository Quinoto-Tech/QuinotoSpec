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
# Jormungandr -- check.py directo (Kahn sobre YAML inline y multilínea)
# ==========================================================================
echo "--- Jormungandr (check.py directo) ---"

JORM_CHECK="$PROJECT_ROOT/agent-dist/skills/quinotospec-jormungandr/check.py"
JORM_TEMPLATE_OUT=$(python3 "$JORM_CHECK" "$PROJECT_ROOT/agent-dist/templates/schema-template.yaml" 2>&1)
JORM_TEMPLATE_RC=$?
if [ "$JORM_TEMPLATE_RC" -eq 0 ] && echo "$JORM_TEMPLATE_OUT" | grep -q "OK: DAG aciclico"; then
    check "check.py valida schema-template.yaml con Kahn real (exit 0)" 0
else
    check "check.py valida schema-template.yaml con Kahn real (exit 0)" 1
fi
if ! echo "$JORM_TEMPLATE_OUT" | grep -q "demo fallback"; then
    check "check.py sobre schema-template.yaml no usa demo fallback" 0
else
    check "check.py sobre schema-template.yaml no usa demo fallback" 1
fi

JORM_MULTI_CYCLE="$WORKDIR/jorm-multi-cycle.yaml"
cat > "$JORM_MULTI_CYCLE" <<'EOF'
artifacts:
  - id: a
    requires:
      - b
  - id: b
    requires:
      - a
EOF
JORM_MULTI_OUT=$(python3 "$JORM_CHECK" "$JORM_MULTI_CYCLE" 2>&1)
JORM_MULTI_RC=$?
if [ "$JORM_MULTI_RC" -eq 1 ] && echo "$JORM_MULTI_OUT" | grep -q "CYCLE:"; then
    check "check.py detecta ciclo en formato multilínea (exit 1, CYCLE:)" 0
else
    check "check.py detecta ciclo en formato multilínea (exit 1, CYCLE:)" 1
fi

JORM_INLINE_CYCLE="$WORKDIR/jorm-inline-cycle.yaml"
cat > "$JORM_INLINE_CYCLE" <<'EOF'
artifacts:
  - id: a
    requires: [b]
  - id: b
    requires: [a]
EOF
JORM_INLINE_OUT=$(python3 "$JORM_CHECK" "$JORM_INLINE_CYCLE" 2>&1)
JORM_INLINE_RC=$?
if [ "$JORM_INLINE_RC" -eq 1 ] && echo "$JORM_INLINE_OUT" | grep -q "CYCLE:"; then
    check "check.py detecta ciclo en formato inline (exit 1, CYCLE:)" 0
else
    check "check.py detecta ciclo en formato inline (exit 1, CYCLE:)" 1
fi

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

# ==========================================================================
# Huginn & Muninn -- metricas reales de entropia (no demo)
# ==========================================================================
echo "--- Huginn & Muninn (entropia real) ---"

HUGINN_DIR="$PROJECT_ROOT/agent-dist/skills/quinotospec-huginn-muninn"

HUGINN_ONE=$(bash "$HUGINN_DIR/check.sh" "$PROJECT_ROOT/agent-dist/skills/quinotospec-mimir" --json 2>&1)
RC=0
echo "$HUGINN_ONE" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["files_analyzed"] > 0, "files_analyzed must be > 0"
for key in ("S_final", "H_total", "S_proxy", "H_size", "H_testing"):
    assert 0.0 <= data[key] <= 1.0, key + " out of range"
assert data["status"] in ("HEALTHY", "WARNING", "CRITICAL")
assert data["classification"] in ("baja", "media", "alta")
' || RC=$?
check "check.sh --json calcula metricas reales con claves y rangos validos" "$RC"

HUGINN_TWO=$(bash "$HUGINN_DIR/check.sh" "$PROJECT_ROOT/agent-dist/skills/quinotospec-contract" --json 2>&1)
RC=0
python3 - "$HUGINN_ONE" "$HUGINN_TWO" <<'PY' || RC=$?
import json
import sys

first = json.loads(sys.argv[1])
second = json.loads(sys.argv[2])
assert first["target"] != second["target"], "targets must differ"
assert (
    first["files_analyzed"] != second["files_analyzed"]
    or first["S_final"] != second["S_final"]
    or first["H_total"] != second["H_total"]
), "distinct directories must not share cached/demo metrics"
PY
check "check.sh produce metricas distintas para directorios distintos (sin cache global)" "$RC"

# ==========================================================================
# Norns -- deteccion de drift de version
# ==========================================================================
echo "--- Norns (drift de version) ---"

NORNS_SCRIPT="$PROJECT_ROOT/agent-dist/skills/quinotospec-norns/norns.py"

NORNS_CHECK=$(python3 -B "$NORNS_SCRIPT" --check --root "$PROJECT_ROOT" 2>&1)
RC=$?
check "norns.py --check sobre el repo real no detecta drift" "$RC"

NORNS_WORK="$WORKDIR/norns-fixture"
mkdir -p "$NORNS_WORK/docs" "$NORNS_WORK/scripts" "$NORNS_WORK/.cursor-plugin"
cp "$PROJECT_ROOT/.version" "$NORNS_WORK/.version"
cp "$PROJECT_ROOT/manifest.json" "$NORNS_WORK/manifest.json"
cp "$PROJECT_ROOT/install.sh" "$NORNS_WORK/install.sh"
cp "$PROJECT_ROOT/.cursor-plugin/plugin.json" "$NORNS_WORK/.cursor-plugin/plugin.json"
cp "$PROJECT_ROOT/README.md" "$NORNS_WORK/README.md"
cp "$PROJECT_ROOT/README_EN.md" "$NORNS_WORK/README_EN.md"
cp "$PROJECT_ROOT/CHANGELOG.md" "$NORNS_WORK/CHANGELOG.md"
cp "$PROJECT_ROOT/V3_ROADMAP.md" "$NORNS_WORK/V3_ROADMAP.md"
cp "$PROJECT_ROOT/docs/ARCHITECTURE.md" "$NORNS_WORK/docs/ARCHITECTURE.md"
cp "$PROJECT_ROOT/scripts/validate-all.sh" "$NORNS_WORK/scripts/validate-all.sh"
cp -R "$PROJECT_ROOT/agent-dist" "$NORNS_WORK/agent-dist"
printf '3.9.9\n' > "$NORNS_WORK/.version"

NORNS_DRIFT=$(python3 -B "$NORNS_SCRIPT" --check --root "$NORNS_WORK" 2>&1)
NORNS_DRIFT_RC=$?
RC=0
if [ "$NORNS_DRIFT_RC" -ne 0 ] && echo "$NORNS_DRIFT" | grep -q "DRIFT:"; then
    RC=0
else
    RC=1
fi
check "norns.py --check detecta drift cuando .version difiere" "$RC"

VERSION_BEFORE=$(tr -d '[:space:]' < "$PROJECT_ROOT/.version")
NORNS_DRY=$(python3 -B "$NORNS_SCRIPT" --to 3.9.0 --dry-run --root "$PROJECT_ROOT" 2>&1)
RC=0
echo "$NORNS_DRY" | grep -q "\[DRY-RUN\]" || RC=$?
check "norns.py --to 3.9.0 --dry-run lista cambios" "$RC"
VERSION_AFTER=$(tr -d '[:space:]' < "$PROJECT_ROOT/.version")
if [ "$VERSION_BEFORE" = "$VERSION_AFTER" ]; then
    RC=0
else
    RC=1
fi
check "norns.py --dry-run no modifica .version" "$RC"

# ==========================================================================
# Skald -- paridad de badges y estructura README
# ==========================================================================
echo "--- Skald (paridad README) ---"

SKALD_SCRIPT="$PROJECT_ROOT/agent-dist/skills/quinotospec-skald/sync-readme.sh"

SKALD_CHECK=$(bash "$SKALD_SCRIPT" --check --root "$PROJECT_ROOT" 2>&1)
RC=$?
check "sync-readme.sh --check sobre el repo real no detecta drift" "$RC"

SKALD_WORK="$WORKDIR/skald-fixture"
mkdir -p "$SKALD_WORK"
cp "$PROJECT_ROOT/.version" "$SKALD_WORK/.version"
cp "$PROJECT_ROOT/README.md" "$SKALD_WORK/README.md"
cp "$PROJECT_ROOT/README_EN.md" "$SKALD_WORK/README_EN.md"
cp -R "$PROJECT_ROOT/agent-dist" "$SKALD_WORK/agent-dist"
sed -i.bak 's|badge/version-3\.3\.0-blue|badge/version-9.9.9-blue|' "$SKALD_WORK/README_EN.md"
rm -f "$SKALD_WORK/README_EN.md.bak"

SKALD_DRIFT=$(bash "$SKALD_SCRIPT" --check --root "$SKALD_WORK" 2>&1)
SKALD_DRIFT_RC=$?
RC=0
if [ "$SKALD_DRIFT_RC" -ne 0 ] && echo "$SKALD_DRIFT" | grep -q "DRIFT:"; then
    RC=0
else
    RC=1
fi
check "sync-readme.sh --check detecta badge desincronizado" "$RC"

SKALD_SYNC=$(bash "$SKALD_SCRIPT" --root "$SKALD_WORK" 2>&1)
RC=$?
check "sync-readme.sh sin --check sincroniza badges y queda sin drift" "$RC"
RC=0
grep -q "badge/version-3.3.0-blue" "$SKALD_WORK/README_EN.md" || RC=$?
check "sync-readme.sh restaura el badge de version correcto" "$RC"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ $ERRORS -gt 0 ]; then
    exit 1
fi

echo "✅ Mimir, Valkyrie, Bifrost, Huginn & Muninn, Norns y Skald funcionan correctamente end-to-end"
exit 0
