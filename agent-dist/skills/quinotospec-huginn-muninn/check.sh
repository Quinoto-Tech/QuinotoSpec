#!/bin/bash
# Huginn & Muninn — check.sh (no LLM, solo metricas)
# Uso: check.sh [service-path] [--json]  (con --json emite SOLO el JSON para parsing en CI)
set -e
JSON_ONLY=false
SERVICE_PATH="."
for arg in "$@"; do
    case "$arg" in
        --json) JSON_ONLY=true ;;
        *) SERVICE_PATH="$arg" ;;
    esac
done

if [ "$JSON_ONLY" != "true" ]; then
  echo "Huginn: analizando $SERVICE_PATH"
  # Placeholder: invoca entropy-calculator formulas
  if [ -f "agent-dist/skills/quinotospec-entropy-calculator/SKILL.md" ]; then
    echo "  (usa quinotospec-entropy-calculator para H_total/S_proxy)"
  fi
fi
# Simula S_final para CI demo
echo '{"S_final": 0.42, "H_total": 0.38, "S_proxy": 0.48, "classification": "media"}'
