#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:?usage: package-release.sh VERSION [OUTPUT_DIR]}"
OUTPUT_DIR="${2:-$ROOT/dist}"
MANIFEST_VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/manifest.json")"

if [ "$VERSION" != "$MANIFEST_VERSION" ]; then
    printf 'ERROR: requested version %s does not match manifest %s\n' "$VERSION" "$MANIFEST_VERSION" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
ARCHIVE="$OUTPUT_DIR/quinotospec-$VERSION.tar.gz"
CHECKSUM="$ARCHIVE.sha256"

# Preflight rapido (no recursivo: no ejecuta la suite de tests).
# SKIP_PREFLIGHT=1 para omitirlo; REQUIRE_CLEAN=1 para exigir git limpio.
if [ "${SKIP_PREFLIGHT:-0}" != "1" ]; then
    if [ -n "$(git -C "$ROOT" status --porcelain 2>/dev/null || true)" ]; then
        if [ "${REQUIRE_CLEAN:-0}" = "1" ]; then
            printf 'ERROR: working tree is dirty; commit or set REQUIRE_CLEAN=0\n' >&2
            exit 1
        fi
        printf 'WARNING: working tree is dirty; the archive is not reproducible from the commit\n' >&2
    fi
    python3 -B "$ROOT/scripts/check-skill-workflow-drift.py" --root "$ROOT" >/dev/null || {
        printf 'ERROR: skill/workflow drift detected\n' >&2
        exit 1
    }
    bash "$ROOT/scripts/check-links.sh" --internal-only >/dev/null || {
        printf 'ERROR: broken internal links detected\n' >&2
        exit 1
    }
fi

rm -f "$ARCHIVE" "$CHECKSUM"

(cd "$ROOT" && tar -czf "$ARCHIVE" \
    --exclude='__pycache__' \
    --exclude='*/__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='*/.pytest_cache' \
    --exclude='.mypy_cache' \
    --exclude='*/.mypy_cache' \
    --exclude='node_modules' \
    --exclude='*/node_modules' \
    --exclude='.DS_Store' \
    --exclude='*/.DS_Store' \
    --exclude='docs/assets/YGGDRASIL.png' \
    --exclude='docs/assets/Mimir.png' \
    --exclude='docs/assets/possessed.png' \
    --exclude='docs/assets/amok.png' \
    --exclude='docs/assets/berserker.jpg' \
    agent-dist/ \
    .cursor-plugin/ \
    extensions/ \
    docs/ \
    examples/ \
    scripts/ \
    tests/ \
    install.sh \
    manifest.json \
    .version \
    AGENTS.md \
    README.md \
    README_EN.md \
    V3_ROADMAP.md \
    LICENSE \
    CHANGELOG.md)

if command -v sha256sum >/dev/null 2>&1; then
    (cd "$OUTPUT_DIR" && sha256sum "$(basename "$ARCHIVE")" > "$(basename "$CHECKSUM")" && sha256sum -c "$(basename "$CHECKSUM")")
elif command -v shasum >/dev/null 2>&1; then
    (cd "$OUTPUT_DIR" && shasum -a 256 "$(basename "$ARCHIVE")" > "$(basename "$CHECKSUM")" && shasum -a 256 -c "$(basename "$CHECKSUM")")
else
    printf 'ERROR: no SHA-256 utility found\n' >&2
    exit 1
fi

printf 'Archive: %s\nChecksum: %s\n' "$ARCHIVE" "$CHECKSUM"
