#!/bin/bash
# Huginn & Muninn — check.sh (no LLM, solo metricas)
set -e
SERVICE_PATH="${1:-.}"
echo "Huginn: analizando $SERVICE_PATH"
# Placeholder: invoca entropy-calculator formulas
if [ -f "agent-dist/skills/quinotospec-entropy-calculator/SKILL.md" ]; then
  echo "  (usa quinotospec-entropy-calculator para H_total/S_proxy)"
fi
# Simula S_final para CI demo
echo '{"S_final": 0.42, "H_total": 0.38, "S_proxy": 0.48, "classification": "media"}'
