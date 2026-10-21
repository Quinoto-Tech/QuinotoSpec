#!/bin/bash

# Test: agent-dist no debe contener caracteres CJK
# Regresión: el skill y el workflow de create-prd tenían fragmentos en chino
# (陈述, 功能) por un copy/paste desde una plantilla traducida.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

TARGET_DIRS=("$PROJECT_ROOT/agent-dist" "$PROJECT_ROOT/docs")

ERRORS=0

echo "=========================================="
echo "Test: Caracteres CJK en documentación"
echo "=========================================="
echo ""

for dir in "${TARGET_DIRS[@]}"; do
    [ -d "$dir" ] || continue

    matches=$(python3 - "$dir" <<'PY'
import pathlib
import re
import sys

# Han (ideogramas), kana (japonés), fullwidth forms y puntuación CJK
pattern = re.compile(r'[\u3000-\u303f\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]')
exts = {".md", ".sh", ".py", ".js", ".json", ".yml", ".yaml", ".toml"}

for path in sorted(pathlib.Path(sys.argv[1]).rglob("*")):
    if not path.is_file() or path.suffix not in exts:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for lineno, line in enumerate(text.splitlines(), 1):
        if pattern.search(line):
            print(f"{path}:{lineno}: {line.strip()}")
PY
)

    if [ -n "$matches" ]; then
        while IFS= read -r line; do
            echo "❌ Carácter CJK inesperado — $line"
            ERRORS=$((ERRORS + 1))
        done <<< "$matches"
    fi
done

echo ""
echo "=========================================="
echo "Resultados: $ERRORS ocurrencias"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Sin caracteres CJK en la documentación"
exit 0
