#!/bin/bash

# Test: review visual con Playwright (doctor, onboarding, harness)
# No requiere Playwright instalado; el E2E real es opt-in con QS_RUN_PLAYWRIGHT=1.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REVIEW_DIR="$PROJECT_ROOT/agent-dist/skills/quinotospec-review"
FIXTURE="$SCRIPT_DIR/fixtures/quinoto-spec-playwright"
TMP="$(mktemp -d)"
PYTHON_BIN="$(command -v python3)"
ERRORS=0
TESTED=0

cleanup() {
    rm -rf "$TMP"
}
trap cleanup EXIT

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
echo "Test: Playwright review"
echo "=========================================="
echo ""

for artifact in \
    "$REVIEW_DIR/playwright_doctor.py" \
    "$REVIEW_DIR/playwright_review.py" \
    "$REVIEW_DIR/mcp_config.py" \
    "$REVIEW_DIR/e2e/package.json" \
    "$REVIEW_DIR/e2e/playwright.config.js" \
    "$REVIEW_DIR/e2e/proposal-review.spec.js" \
    "$REVIEW_DIR/e2e/reporter.js" \
    "$FIXTURE/.quinoto-spec/proposals/demo/proposal.md"; do
    [ -f "$artifact" ]
    check "existe $(basename "$artifact")" "$?"
done

python3 -B "$SCRIPT_DIR/test-playwright-doctor.py" >/dev/null 2>&1
check "tests del doctor" "$?"

python3 -B "$SCRIPT_DIR/test-review-playwright.py" >/dev/null 2>&1
check "tests del orquestador" "$?"

if command -v node >/dev/null 2>&1; then
    (
        cd "$REVIEW_DIR/e2e" && node --check proposal-review.spec.js >/dev/null 2>&1
    )
    check "spec de Playwright tiene sintaxis valida" "$?"

    (
        cd "$REVIEW_DIR/e2e" && node --check reporter.js >/dev/null 2>&1
    )
    check "reporter de Playwright tiene sintaxis valida" "$?"
else
    echo "  ⏭️  Node no instalado; se omiten los checks de sintaxis JS"
fi

cp -R "$FIXTURE" "$TMP/project"
mkdir -p "$TMP/home" "$TMP/empty-bin"
BEFORE=$(find "$TMP/project/.quinoto-spec/proposals" -type f -exec sha256sum {} + | sort | sha256sum)

QS_HOME="$TMP/home" PATH="$TMP/empty-bin" "$PYTHON_BIN" -B "$REVIEW_DIR/playwright_review.py" \
    --root "$TMP/project" --proposal demo --no-install-prompt --skip-contract --json \
    >"$TMP/skip.json" 2>"$TMP/skip.err"
RC=$?
check "skip path devuelve exit 0" "$RC"
python3 - "$TMP/skip.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["result"] == "skipped", data
assert data["dependency"]["install_action"] == "skip", data
PY
check "skip path produce evidencia skipped" "$?"

QS_HOME="$TMP/home" PATH="$TMP/empty-bin" "$PYTHON_BIN" -B "$REVIEW_DIR/playwright_review.py" \
    --root "$TMP/project" --proposal demo --yes --skip-contract --json \
    >"$TMP/action.json" 2>"$TMP/action.err"
RC=$?
RC_EXIT=0
[ "$RC" -eq 3 ] || RC_EXIT=1
check "no-TTY sin decision devuelve action_required (exit 3)" "$RC_EXIT"
python3 - "$TMP/action.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["result"] == "action_required", data
assert len(data["options"]) == 3, data
PY
check "action_required ofrece app, MCP y omitir" "$?"

AFTER=$(find "$TMP/project/.quinoto-spec/proposals" -type f -exec sha256sum {} + | sort | sha256sum)
[ "$BEFORE" = "$AFTER" ]
check "el review no modifica proposal, stories ni tasks" "$?"

QS_HOME="$TMP/home" PATH="$TMP/empty-bin" "$PYTHON_BIN" -B "$REVIEW_DIR/playwright_review.py" \
    --root "$TMP/project" --proposal demo --install-playwright-mcp --skip-contract --json \
    >"$TMP/mcp.json" 2>"$TMP/mcp.err"
RC=$?
[ "$RC" -eq 3 ]
check "configurar MCP devuelve action_required (exit 3)" "$?"
python3 - "$TMP/mcp.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
assert data["result"] == "action_required", data
assert data["dependency"]["mcp"]["configured"] is True, data
PY
check "configuracion MCP queda registrada" "$?"

if [ "${QS_RUN_PLAYWRIGHT:-0}" = "1" ]; then
    if command -v npx >/dev/null 2>&1 && npx playwright --version >/dev/null 2>&1; then
        PORT=$("$PYTHON_BIN" - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
)
        "$PYTHON_BIN" -B "$PROJECT_ROOT/agent-dist/ui/server.py" --root "$TMP/project" --port "$PORT" --no-browser >"$TMP/ui.log" 2>&1 &
        UI_PID=$!
        for _ in $(seq 1 50); do
            curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break
            sleep 0.1
        done
        (
            cd "$REVIEW_DIR/e2e" && \
            QS_BASE_URL="http://127.0.0.1:$PORT" \
            QS_PROPOSAL_SLUG="demo" \
            QS_OUTPUT_DIR="$TMP/e2e-out" \
            npx playwright test --project=chromium >/dev/null 2>&1
        )
        check "E2E de Playwright sobre el fixture" "$?"
        kill "$UI_PID" 2>/dev/null || true
    else
        echo "  ⏭️  Playwright no instalado; se omite el E2E real"
    fi
fi

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Review con Playwright funciona correctamente"
