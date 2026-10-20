#!/bin/bash
# Skald — docs viva sin duplicacion.
# Uso:
#   sync-readme.sh [--check] [--root PATH]
#
# --check  Verifica que README.md y README_EN.md tengan la misma estructura de
#          tablas y que los badges version/workflows/skills/rules coincidan entre
#          si, con .version y con los conteos reales de agent-dist/.
#          Exit 0 si no hay drift; exit 1 si hay DRIFT.
# (sin flag) Sincroniza los badges en ambos READMEs y vuelve a verificar.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CHECK_ONLY=false

while [ "$#" -gt 0 ]; do
    case "$1" in
        --check) CHECK_ONLY=true ;;
        --root)
            shift
            if [ "$#" -eq 0 ]; then
                echo "ERROR: --root requires a path" >&2
                exit 2
            fi
            ROOT="$(cd "$1" && pwd)"
            ;;
        --root=*) ROOT="$(cd "${1#--root=}" && pwd)" ;;
        -h|--help)
            echo "Usage: $0 [--check] [--root PATH]"
            exit 0
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            exit 2
            ;;
    esac
    shift
done

README_ES="$ROOT/README.md"
README_EN="$ROOT/README_EN.md"
VERSION_FILE="$ROOT/.version"

for required in "$README_ES" "$README_EN" "$VERSION_FILE"; do
    if [ ! -f "$required" ]; then
        echo "ERROR: missing $required" >&2
        exit 2
    fi
done

VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"
WORKFLOWS=$(find "$ROOT/agent-dist/workflows" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
SKILLS=$(find "$ROOT/agent-dist/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
RULES=$(grep -c '^# ' "$ROOT/agent-dist/rules/quinotospec-rules.md" 2>/dev/null || echo 0)

badge_value() {
    # $1=file  $2=badge name (version|workflows|skills|rules)
    sed -n "s|.*badge/$2-\([0-9][0-9.]*\)-[a-z]*.*|\1|p" "$1" | head -1
}

rows() {
    grep -c '^| \*\*' "$1" 2>/dev/null || true
}

expected_value() {
    case "$1" in
        version) echo "$VERSION" ;;
        workflows) echo "$WORKFLOWS" ;;
        skills) echo "$SKILLS" ;;
        rules) echo "$RULES" ;;
    esac
}

DRIFT=0

report_drift() {
    echo "DRIFT: $1"
    DRIFT=$((DRIFT + 1))
}

verify_badges() {
    local badge file actual expected
    for file in "$README_ES" "$README_EN"; do
        for badge in version workflows skills rules; do
            expected="$(expected_value "$badge")"
            actual="$(badge_value "$file" "$badge")"
            if [ -z "$actual" ]; then
                report_drift "$(basename "$file") missing badge '$badge' (expected $expected)"
            elif [ "$actual" != "$expected" ]; then
                report_drift "$(basename "$file") badge '$badge'=$actual (expected $expected)"
            fi
        done
    done
}

verify_structure() {
    local es en
    es="$(rows "$README_ES")"
    en="$(rows "$README_EN")"
    if [ "$es" != "$en" ]; then
        report_drift "table row count mismatch: README.md=$es vs README_EN.md=$en"
    fi
}

sync_badges() {
    local file badge expected tmp
    for file in "$README_ES" "$README_EN"; do
        expected_version="$(expected_value version)"
        expected_workflows="$(expected_value workflows)"
        expected_skills="$(expected_value skills)"
        expected_rules="$(expected_value rules)"
        tmp="$(mktemp "${file}.XXXXXX")"
        sed \
            -e "s|badge/version-[0-9][0-9.]*-blue|badge/version-${expected_version}-blue|g" \
            -e "s|badge/workflows-[0-9][0-9.]*-purple|badge/workflows-${expected_workflows}-purple|g" \
            -e "s|badge/skills-[0-9][0-9.]*-purple|badge/skills-${expected_skills}-purple|g" \
            -e "s|badge/rules-[0-9][0-9.]*-red|badge/rules-${expected_rules}-red|g" \
            "$file" > "$tmp"
        mv "$tmp" "$file"
        echo "  Synced $(basename "$file") badges ($expected_version / $expected_workflows / $expected_skills / $expected_rules)"
    done
}

if [ "$CHECK_ONLY" = true ]; then
    echo "Skald --check: README.md vs README_EN.md vs filesystem"
    echo "  expected: version=$VERSION workflows=$WORKFLOWS skills=$SKILLS rules=$RULES"
    verify_badges
    verify_structure
    if [ "$DRIFT" -gt 0 ]; then
        echo "Skald: $DRIFT drift(s) detected"
        exit 1
    fi
    echo "OK: no drift"
    exit 0
fi

echo "Skald sync: README.md + README_EN.md badges from .version and agent-dist/"
sync_badges
verify_badges
verify_structure
if [ "$DRIFT" -gt 0 ]; then
    echo "Skald: $DRIFT drift(s) remain after sync (check table structure)"
    exit 1
fi
echo "OK: no drift"
exit 0
