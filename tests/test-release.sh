#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/manifest.json")"
OUTPUT_DIR="$(mktemp -d)"
trap 'rm -rf "$OUTPUT_DIR"' EXIT

bash "$ROOT/scripts/package-release.sh" "$VERSION" "$OUTPUT_DIR"
bash "$ROOT/scripts/smoke-release.sh" "$OUTPUT_DIR/quinotospec-$VERSION.tar.gz"
