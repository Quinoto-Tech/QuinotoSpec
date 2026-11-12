#!/usr/bin/env bash

# Lint: shellcheck sobre todos los scripts del paquete con una version fija.
#
# Por que existe: el set de checks de shellcheck cambia entre releases (SC2317
# aparecio y cambio de heuristica entre 0.9 y 0.11). Si CI usa la version del
# runner y el dev usa la de su package manager, el mismo commit puede pasar en
# una maquina y fallar en la otra. `.shellcheck-version` es la fuente unica.
#
# Uso: ./scripts/lint-shell.sh [--allow-version-mismatch] [--quiet]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PIN_FILE="$PROJECT_ROOT/.shellcheck-version"
ALLOW_MISMATCH=false
QUIET=false

for arg in "$@"; do
    case "$arg" in
        --allow-version-mismatch) ALLOW_MISMATCH=true ;;
        --quiet) QUIET=true ;;
        -h|--help)
            echo "Usage: $0 [--allow-version-mismatch] [--quiet]"
            echo "  --allow-version-mismatch  Correr aunque la version local no coincida con .shellcheck-version"
            echo "  --quiet                   Solo imprimir hallazgos y el resumen"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            exit 2
            ;;
    esac
done

if [ ! -f "$PIN_FILE" ]; then
    echo "ERROR: .shellcheck-version not found at $PIN_FILE" >&2
    exit 1
fi
EXPECTED_VERSION="$(tr -d '[:space:]' < "$PIN_FILE")"

if ! command -v shellcheck >/dev/null 2>&1; then
    echo "ERROR: shellcheck not installed (required: $EXPECTED_VERSION)" >&2
    echo "  macOS: brew install shellcheck" >&2
    echo "  Linux: https://github.com/koalaman/shellcheck/releases/tag/v$EXPECTED_VERSION" >&2
    exit 1
fi

ACTUAL_VERSION="$(shellcheck --version | awk '/^version:/ {print $2}')"
if [ "$ACTUAL_VERSION" != "$EXPECTED_VERSION" ]; then
    if [ "$ALLOW_MISMATCH" != true ]; then
        echo "ERROR: shellcheck $ACTUAL_VERSION found, $EXPECTED_VERSION pinned in .shellcheck-version" >&2
        echo "  Instala la version fijada, o corre con --allow-version-mismatch." >&2
        exit 1
    fi
    echo "WARNING: shellcheck $ACTUAL_VERSION != pinned $EXPECTED_VERSION (mismatch allowed)" >&2
fi

if [ "$QUIET" != true ]; then
    echo "shellcheck $ACTUAL_VERSION (pinned: $EXPECTED_VERSION)"
fi

FAILED=0
CHECKED=0
while IFS= read -r file; do
    CHECKED=$((CHECKED + 1))
    if ! shellcheck -e SC2329 -x "$file"; then
        FAILED=$((FAILED + 1))
    fi
done < <(
    cd "$PROJECT_ROOT" || exit 1
    for f in install.sh agent-dist/hooks/*.sh scripts/*.sh tests/*.sh .githooks/*; do
        [ -f "$f" ] && printf '%s\n' "$f"
    done
)

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "shellcheck: $FAILED of $CHECKED scripts failed (version $ACTUAL_VERSION)" >&2
    exit 1
fi

if [ "$QUIET" != true ]; then
    echo "shellcheck: $CHECKED scripts clean"
fi
exit 0
