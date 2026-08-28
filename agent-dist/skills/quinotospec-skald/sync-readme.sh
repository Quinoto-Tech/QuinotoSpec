#!/bin/bash
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SRC="$PROJECT_ROOT/README.md"
DST="$PROJECT_ROOT/README_EN.md"
if [ "$1" = "--check" ]; then
  echo "Skald --check: comparando estructura README.md vs README_EN.md"
  # simple drift: conteo de workflows listados
  SRC_W=$(grep -c "^\| \*\*" "$SRC" || true)
  DST_W=$(grep -c "^\| \*\*" "$DST" || true)
  echo "  workflows rows: README $SRC_W vs README_EN $DST_W"
  if [ "$SRC_W" != "$DST_W" ]; then echo "DRIFT: row count mismatch"; exit 1; fi
  echo "OK: no drift"
  exit 0
fi
echo "Skald sync: README.md -> README_EN.md (estructura only, no traduce)"
echo "  (placeholder — sync real requiere mapeo manual de bloques)"
