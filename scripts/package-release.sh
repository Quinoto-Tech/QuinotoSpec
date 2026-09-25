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
