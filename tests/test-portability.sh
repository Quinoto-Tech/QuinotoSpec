#!/bin/bash

# Test: Portabilidad de scripts (GNU/Linux <-> macOS BSD)
# El CI corre en ubuntu-latest y macos-latest; un comando GNU-only que pasa en
# Linux rompe el job de macOS y la experiencia de un dev con Mac. Esta suite
# detecta esos patrones en Linux para no enterarnos recien en macOS.

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
echo "Test: Portabilidad GNU/Linux <-> macOS"
echo "=========================================="
echo ""

# scan_gnu_only <json de reglas>  -> imprime hallazgos, exit 1 si hay alguno.
# Las reglas viven en python para ignorar comentarios y este mismo archivo.
scan_gnu_only() {
    python3 -B - "$PROJECT_ROOT" <<'PY'
import os
import re
import sys

root = sys.argv[1]
SELF = os.path.join("tests", "test-portability.sh")

RULES = [
    (r"(?<![A-Za-z0-9_])touch\s+-d\s", "touch -d (GNU): usar python3 os.utime"),
    (r"grep\s+-[A-Za-z]*P", "grep -P (PCRE no existe en macOS/BSD)"),
    (r"sed\s+-i\s", "sed -i sin sufijo (BSD exige 'sed -i.bak')"),
    (r"(?<![A-Za-z0-9_])(mapfile|readarray)\s", "mapfile/readarray (bash 4+; macOS trae 3.2)"),
    (r"stat\s+-c\s", "stat -c (GNU): usar python3"),
    (r"date\s+(-d|-u\s+-d)\s", "date -d (GNU): usar python3"),
]

TARGETS = ["install.sh", "scripts", os.path.join("tests"), os.path.join("agent-dist", "hooks")]

def is_shell(path):
    if path.endswith(".sh"):
        return True
    if path == "install.sh":
        return True
    return path.startswith(os.path.join(".githooks", ""))

def collect():
    files = []
    for target in TARGETS:
        full = os.path.join(root, target)
        if os.path.isfile(full):
            files.append(target)
            continue
        for dirpath, _, filenames in os.walk(full):
            for name in filenames:
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                if is_shell(rel):
                    files.append(rel)
    # Los skills pueden traer scripts ejecutables (bash) propios.
    skills = os.path.join(root, "agent-dist", "skills")
    for dirpath, _, filenames in os.walk(skills):
        for name in filenames:
            if name.endswith(".sh"):
                files.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(set(files))

def strip_comment(line):
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return ""
    return line

findings = []
checked = 0
for rel in collect():
    if rel == SELF:
        continue
    path = os.path.join(root, rel)
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()
    except OSError:
        continue
    checked += 1
    for number, line in enumerate(lines, start=1):
        if not strip_comment(line):
            continue
        for pattern, label in RULES:
            if re.search(pattern, line):
                findings.append("%s:%d: %s -> %s" % (rel, number, label, line.strip()))

# Las suites de tests deben generarse con contenido: si no, el scan no sirve.
if checked < 20:
    print("     AVISO: solo %d archivos auditados" % checked)
    sys.exit(1)

for finding in findings:
    print("     " + finding)

print("     archivos auditados: %d" % checked)
sys.exit(1 if findings else 0)
PY
}

scan_gnu_only
check "sin comandos GNU-only en scripts shell (touch -d, grep -P, sed -i, mapfile, stat -c, date -d)" "$?"

# install.sh debe avisar antes de fallar por bash viejo (UX del Dia 1 en macOS).
RC=0
if ! grep -q 'Bash 4.0+ required' "$PROJECT_ROOT/install.sh"; then
    RC=1
    echo "     install.sh no valida la version de bash"
fi
check "install.sh avisa cuando bash < 4.0" "$RC"

# El CI debe cubrir ambas plataformas.
RC=0
if ! grep -q 'macos-latest' "$PROJECT_ROOT/.github/workflows/ci.yml"; then
    RC=1
    echo "     ci.yml no incluye macos-latest en la matriz de test"
fi
check "ci.yml corre la suite en macOS" "$RC"

# Lint con version fijada (el set de checks cambia entre releases de shellcheck).
RC=0
if [ ! -f "$PROJECT_ROOT/.shellcheck-version" ] || [ ! -f "$PROJECT_ROOT/scripts/lint-shell.sh" ]; then
    RC=1
    echo "     falta .shellcheck-version o scripts/lint-shell.sh"
fi
check "shellcheck corre con version fijada (.shellcheck-version)" "$RC"

# validate-all.sh debe seguir siendo compatible con bash 3.2 (mapfile ya no se usa).
RC=0
if grep -qE '(^|[^A-Za-z0-9_])(mapfile|readarray)[[:space:]]' "$PROJECT_ROOT/scripts/validate-all.sh"; then
    RC=1
    echo "     validate-all.sh usa mapfile/readarray (bash 4+)"
fi
check "validate-all.sh corre en bash 3.2 (sin mapfile)" "$RC"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Portabilidad GNU/Linux <-> macOS sin patrones bloqueantes"
exit 0
