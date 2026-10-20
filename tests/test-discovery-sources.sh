#!/bin/bash

# Test: create-proposal debe declarar las fuentes del discovery por sección
# Regresión: el workflow leía 01 y 08 pero no mapeaba 02-07 a las secciones
# técnicas de la propuesta, por lo que el agente omitía arquitectura, endpoints,
# datos, CI/seguridad y deuda técnica.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SKILL="$PROJECT_ROOT/agent-dist/skills/quinotospec-create-proposal/SKILL.md"
WORKFLOW="$PROJECT_ROOT/agent-dist/workflows/quinotospec.create-proposal.md"

REQUIRED_DISCOVERY_DOCS=(
    "02-overview"
    "03-architecture"
    "04-endpoints-and-openapi"
    "05-data-and-services"
    "06-devops-ci-security"
    "07-findings-and-recommendations"
)

ERRORS=0

echo "=========================================="
echo "Test: Fuentes de Discovery en create-proposal"
echo "=========================================="
echo ""

for target in "$SKILL" "$WORKFLOW"; do
    name="${target#"$PROJECT_ROOT"/}"

    if [ ! -f "$target" ]; then
        echo "❌ $name: archivo inexistente"
        ERRORS=$((ERRORS + 1))
        continue
    fi

    if ! grep -q "Lectura dirigida del Discovery" "$target"; then
        echo "❌ $name: falta el bloque 'Lectura dirigida del Discovery'"
        ERRORS=$((ERRORS + 1))
    fi

    for doc in "${REQUIRED_DISCOVERY_DOCS[@]}"; do
        if ! grep -q "$doc\.md" "$target"; then
            echo "❌ $name: no referencia $doc.md como fuente de una sección"
            ERRORS=$((ERRORS + 1))
        fi
    done

    if ! grep -q "no inventes endpoints" "$target"; then
        echo "❌ $name: falta la regla de no inventar datos faltantes del discovery"
        ERRORS=$((ERRORS + 1))
    fi

    if [ "$ERRORS" -eq 0 ]; then
        echo "✅ $name"
    fi
done

echo ""
echo "=========================================="
echo "Resultados: $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ create-proposal declara las fuentes del discovery por sección"
exit 0
