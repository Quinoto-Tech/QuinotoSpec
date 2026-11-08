#!/bin/bash

# Test: QuinotoSpec UI (Fase 1, read-only)
# Valida readers sobre la fixture/ejemplos y ejercita todos los endpoints con
# un servidor efimero. Sin dependencias externas (urllib).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
UI_DIR="$PROJECT_ROOT/agent-dist/ui"
FIXTURE="$SCRIPT_DIR/fixtures/quinoto-spec-sample"
EXAMPLE="$PROJECT_ROOT/examples/python-fastapi"

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
echo "Test: QuinotoSpec UI (read-only)"
echo "=========================================="
echo ""

for artifact in "$UI_DIR/server.py" "$UI_DIR/readers.py" "$UI_DIR/templates.py" \
    "$PROJECT_ROOT/agent-dist/skills/quinotospec-ui/SKILL.md" \
    "$PROJECT_ROOT/agent-dist/workflows/quinotospec.ui.md"; do
    [ -f "$artifact" ]
    check "existe $(basename "$artifact")" "$?"
done

# --- Readers sobre la fixture ---
python3 -B "$UI_DIR/server.py" --root "$FIXTURE" --json >/dev/null 2>&1
check "server.py --json ejecuta sobre la fixture" "$?"

RC=0
python3 -B "$UI_DIR/server.py" --root "$FIXTURE" --json | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["initialized"] is True
assert len(data["proposals"]) == 2
assert len(data["proposals"][1]["stories"]) == 3
assert len(data["discovery"]["files"]) == 2
assert len(data["prefixes"]) == 2
assert data["constitution"]["present"] is False
' || RC=$?
check "readers parsean propuestas, stories, discovery y prefijos" "$RC"

# --- Formato de tareas por heading (ejemplo) ---
RC=0
python3 -B "$UI_DIR/server.py" --root "$EXAMPLE" --json | python3 -c '
import json, sys
data = json.load(sys.stdin)
tasks = [t for p in data["proposals"] for t in p["tasks"]]
assert len(tasks) == 4, tasks
assert all(t["status"] == "completed" for t in tasks), tasks
assert any(t["story"] for t in tasks)
' || RC=$?
check "readers parsean tareas en formato heading (ejemplo python-fastapi)" "$RC"

# --- Roundtrip HTTP + read-only ---
BEFORE=$(find "$FIXTURE" -type f | wc -l)
RC=0
UI_ROOT="$FIXTURE" UI_DIR="$UI_DIR" python3 - <<'PY' || RC=$?
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ui_dir = os.environ["UI_DIR"]
root = os.environ["UI_ROOT"]

sock = socket.socket()
sock.bind(("127.0.0.1", 0))
port = sock.getsockname()[1]
sock.close()

proc = subprocess.Popen(
    [sys.executable, "-B", os.path.join(ui_dir, "server.py"), "--root", root, "--port", str(port), "--no-browser"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
try:
    base = "http://127.0.0.1:%d" % port
    for _ in range(60):
        try:
            urllib.request.urlopen(base + "/health", timeout=0.3)
            break
        except Exception:
            time.sleep(0.1)
    else:
        raise SystemExit("servidor no respondio a /health")

    expectations = {
        "/": b"Panel de estado",
        "/proposals": b"Sample Auth JWT",
        "/proposals/2026-01-10-sample-auth": b"User stories",
        "/tasks": b"kanban",
        "/changelog": b"Changelog",
        "/discovery": b"Discovery",
        "/constitution": b"constituc",
        "/static/style.css": b"--accent",
    }
    for route, marker in expectations.items():
        body = urllib.request.urlopen(base + route, timeout=3).read()
        assert marker.lower() in body.lower(), (route, marker)

    summary = json.loads(urllib.request.urlopen(base + "/api/summary", timeout=3).read())
    assert summary["name"]
    assert summary["counts"]["proposals"] == 2

    try:
        urllib.request.urlopen(base + "/noexiste", timeout=3)
    except urllib.error.HTTPError as error:
        assert error.code == 404, error.code
    else:
        raise AssertionError("ruta inexistente devolvio 200")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
PY
check "endpoints HTTP responden y 404 funciona" "$RC"

AFTER=$(find "$FIXTURE" -type f | wc -l)
[ "$BEFORE" = "$AFTER" ]
check "la UI no crea archivos en el proyecto (read-only)" "$?"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ QuinotoSpec UI funciona correctamente"
