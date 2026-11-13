#!/bin/bash

# Test: higiene de la configuracion de CI
# GitHub depreca el runtime de Node de las actions cada tanto (Node 20 -> 24), y
# los snippets viejos se copian de docs/skills a los workflows. Esta suite falla
# si una action queda por debajo del major minimo o si un workflow no declara
# version explicita.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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
echo "Test: Higiene de CI (actions y runtimes)"
echo "=========================================="
echo ""

# Minimos vigentes. Subir aca cuando se bumpee el workflow (y en el snippet de
# la skill huginn-muninn, que es la plantilla que copian los usuarios).
WC_CHECKOUT="${WC_CHECKOUT:-7}"
WC_SETUP_PYTHON="${WC_SETUP_PYTHON:-7}"
WC_GH_RELEASE="${WC_GH_RELEASE:-3}"
WC_SETUP_NODE="${WC_SETUP_NODE:-7}"

scan_actions() {
    python3 -B - "$PROJECT_ROOT" "$WC_CHECKOUT" "$WC_SETUP_PYTHON" "$WC_GH_RELEASE" "$WC_SETUP_NODE" <<'PY'
import os
import re
import sys

root = sys.argv[1]
minimums = {
    "actions/checkout": int(sys.argv[2]),
    "actions/setup-python": int(sys.argv[3]),
    "softprops/action-gh-release": int(sys.argv[4]),
    "actions/setup-node": int(sys.argv[5]),
}

problems = []
scanned = 0

def scan_file(rel):
    global scanned
    path = os.path.join(root, rel)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return
    for number, line in enumerate(text.splitlines(), start=1):
        m = re.search(r"uses:\s*([\w.\-]+/[\w.\-]+)@(\S+)", line)
        if not m:
            continue
        action, ref = m.group(1), m.group(2).strip().rstrip(",")
        if action not in minimums:
            continue
        scanned += 1
        major_match = re.match(r"v(\d+)", ref)
        if not major_match:
            problems.append("%s:%d: %s@%s sin major (usa @vN)" % (rel, number, action, ref))
            continue
        major = int(major_match.group(1))
        if major < minimums[action]:
            problems.append(
                "%s:%d: %s@%s < minimo v%d (runtime Node deprecado)"
                % (rel, number, action, ref, minimums[action])
            )

workflows_dir = os.path.join(root, ".github", "workflows")
for name in sorted(os.listdir(workflows_dir)):
    if name.endswith((".yml", ".yaml")):
        scan_file(os.path.join(".github", "workflows", name))

# El snippet de la skill es una plantilla publica: mismo criterio.
scan_file(os.path.join("agent-dist", "skills", "quinotospec-huginn-muninn", "SKILL.md"))

for problem in problems:
    print("     " + problem)
print("     referencias de action verificadas: %d" % scanned)
sys.exit(1 if problems else 0)
PY
}

scan_actions
check "checkout, setup-python, setup-node y action-gh-release en majors sin Node deprecado" "$?"

# La suite completa tiene que cubrir el Python declarado como minimo y el actual.
RC=0
if ! grep -q '"3\.8"' "$PROJECT_ROOT/.github/workflows/ci.yml"; then
    RC=1
    echo "     el job compatibility no cubre Python 3.8 (minimo declarado en README)"
fi
check "compatibility cubre el Python minimo declarado (3.8)" "$RC"

RC=0
if ! grep -q '"3\.13"' "$PROJECT_ROOT/.github/workflows/ci.yml"; then
    RC=1
    echo "     el job compatibility no cubre Python 3.13"
fi
check "compatibility cubre un Python reciente (3.13)" "$RC"

# El job de macOS no debe instalar herramientas que no usa (punto de falla gratis).
RC=0
if grep -q 'brew install shellcheck' "$PROJECT_ROOT/.github/workflows/ci.yml"; then
    RC=1
    echo "     el job de macOS instala shellcheck, pero el lint es un job aparte"
fi
check "el job de macOS no instala shellcheck" "$RC"

# Cada workflow debe poder parsearse como YAML (python3+yaml, o ruby de fallback).
parse_workflows() {
    if python3 -c 'import yaml' >/dev/null 2>&1; then
        python3 -B - "$PROJECT_ROOT" <<'PY'
import os
import sys

import yaml

root = sys.argv[1]
workflows_dir = os.path.join(root, ".github", "workflows")
bad = []
for name in sorted(os.listdir(workflows_dir)):
    if not name.endswith((".yml", ".yaml")):
        continue
    try:
        yaml.safe_load(open(os.path.join(workflows_dir, name), encoding="utf-8"))
    except Exception as error:  # noqa: BLE001 - reportamos el parser tal cual
        bad.append("%s: %s" % (name, error))

for item in bad:
    print("     " + item)
sys.exit(1 if bad else 0)
PY
        return $?
    fi

    if command -v ruby >/dev/null 2>&1; then
        ruby -ryaml -e '
root = ARGV[0]
bad = []
Dir.children(File.join(root, ".github", "workflows")).sort.each do |name|
  next unless name.end_with?(".yml", ".yaml")
  begin
    YAML.load_file(File.join(root, ".github", "workflows", name))
  rescue StandardError => e
    bad << "#{name}: #{e.message}"
  end
end
bad.each { |item| puts "     #{item}" }
exit(bad.empty? ? 0 : 1)
' "$PROJECT_ROOT"
        return $?
    fi

    echo "     sin PyYAML ni ruby: se omite el parseo (GitHub lo valida al correr)"
    return 0
}

RC=0
parse_workflows || RC=$?
check "los workflows .yml parsean como YAML" "$RC"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Configuracion de CI sin actions deprecadas"
exit 0
