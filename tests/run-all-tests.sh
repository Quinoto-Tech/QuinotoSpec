#!/bin/bash

# Runner: Ejecuta todos los tests de QuinotoSpec
# Retorna exit code 0 si todos pasan, 1 si alguno falla

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0
FAILED_NAMES=()

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   QuinotoSpec - Test Suite                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

run_suite() {
    local suite_name="$1"
    local suite_script="$2"
    
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶ Ejecutando: $suite_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if bash "$suite_script"; then
        PASSED_SUITES=$((PASSED_SUITES + 1))
        echo ""
    else
        FAILED_SUITES=$((FAILED_SUITES + 1))
        FAILED_NAMES+=("$suite_name")
        echo ""
    fi
}

# Ejecutar cada suite de tests
run_suite "Workflows" "$SCRIPT_DIR/test-workflows.sh"
run_suite "Skills" "$SCRIPT_DIR/test-skills.sh"
run_suite "Rules" "$SCRIPT_DIR/test-rules.sh"
run_suite "Rules Enforce" "$SCRIPT_DIR/test-rules-enforce.sh"
run_suite "Evidence" "$SCRIPT_DIR/test-evidence.sh"
run_suite "Human Approval" "$SCRIPT_DIR/test-approval.sh"
run_suite "Extensions" "$SCRIPT_DIR/test-extensions.sh"
run_suite "Dynamic AGENTS" "$SCRIPT_DIR/test-agents.sh"
run_suite "Backup" "$SCRIPT_DIR/test-backup.sh"
run_suite "Install" "$SCRIPT_DIR/test-install.sh"
run_suite "Install E2E (sandbox)" "$SCRIPT_DIR/test-install-e2e.sh"
run_suite "Release Package" "$SCRIPT_DIR/test-release.sh"
run_suite "Session Bootstrap" "$SCRIPT_DIR/test-bootstrap.sh"
run_suite "Engineering Skills" "$SCRIPT_DIR/test-engineering-skills.sh"
run_suite "Constitution" "$SCRIPT_DIR/test-constitution.sh"
run_suite "Receive Review" "$SCRIPT_DIR/test-receive-review.sh"
run_suite "Worktree" "$SCRIPT_DIR/test-worktree.sh"
run_suite "Checkers funcionales" "$SCRIPT_DIR/test-checkers.sh"
run_suite "Artifact Contract" "$SCRIPT_DIR/test-contract.sh"
run_suite "Skills Nordic" "$SCRIPT_DIR/test-nordic-skills.sh"

# Resumen final
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   RESUMEN FINAL                              ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Total:  $TOTAL_SUITES suites                          ║"
echo "║  ✅ Pas: $PASSED_SUITES                                    ║"
echo "║  ❌ Fail: $FAILED_SUITES                                    ║"
echo "╚══════════════════════════════════════════════╝"

if [ $FAILED_SUITES -gt 0 ]; then
    echo ""
    echo "Suites fallidas:"
    for name in "${FAILED_NAMES[@]}"; do
        echo "  ❌ $name"
    done
    echo ""
    exit 1
fi

echo ""
echo "✅ Todos los tests pasaron correctamente"
exit 0
