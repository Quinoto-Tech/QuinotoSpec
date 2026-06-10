#!/bin/bash

# Check Links: Valida que todos los links en la documentacion funcionen
# Uso: ./scripts/check-links.sh [--internal-only]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INTERNAL_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --internal-only) INTERNAL_ONLY=true ;;
        -h|--help)
            echo "Usage: $0 [--internal-only]"
            echo "  --internal-only  Only check relative links (no HTTP)"
            exit 0
            ;;
    esac
done

echo "=========================================="
echo "  QuinotoSpec - Link Checker"
echo "=========================================="
echo ""

BROKEN=0
CHECKED=0
WARNINGS=0

check_internal_link() {
    local link="$1"
    local source_file="$2"
    local source_dir
    source_dir=$(dirname "$source_file")
    
    # Remove anchor from link
    link="${link%%#*}"
    
    # Skip empty links and anchors-only
    if [ -z "$link" ]; then return; fi
    
    # Resolve relative path
    local target="$source_dir/$link"
    
    if [ ! -e "$target" ]; then
        echo "  BROKEN: $link (in $(basename "$source_file"))"
        BROKEN=$((BROKEN + 1))
    fi
    CHECKED=$((CHECKED + 1))
}

check_external_link() {
    local link="$1"
    local source_file="$2"
    
    if ! curl -sf --max-time 10 -o /dev/null "$link" 2>/dev/null; then
        echo "  BROKEN: $link (in $(basename "$source_file"))"
        BROKEN=$((BROKEN + 1))
    fi
    CHECKED=$((CHECKED + 1))
}

echo "Scanning markdown files..."
echo ""

for md_file in "$PROJECT_ROOT"/*.md "$PROJECT_ROOT"/agent-dist/**/*.md; do
    if [ ! -f "$md_file" ]; then continue; fi
    
    while IFS= read -r link; do
        if [[ "$link" =~ ^https?:// ]]; then
            if [ "$INTERNAL_ONLY" = false ]; then
                check_external_link "$link" "$md_file"
            fi
        elif [[ ! "$link" =~ ^# ]]; then
            check_internal_link "$link" "$md_file"
        fi
    done < <(grep -oP '\[.*?\]\(\K[^)]+' "$md_file" 2>/dev/null || true)
done

echo ""
echo "=========================================="
echo "  Results: $CHECKED checked, $BROKEN broken"
echo "=========================================="

if [ $BROKEN -gt 0 ]; then
    exit 1
fi

echo "All links valid"
exit 0
