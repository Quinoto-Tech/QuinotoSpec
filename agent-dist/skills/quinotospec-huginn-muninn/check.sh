#!/bin/bash
# Huginn & Muninn — check.sh
# Uso: check.sh [service-path] [--json]
# Delega el calculo real de entropia a check.py (Python 3 stdlib).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$SCRIPT_DIR/check.py" "$@"
