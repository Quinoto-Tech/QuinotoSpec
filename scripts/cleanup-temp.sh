#!/bin/bash

# Cleanup Temp: Limpia archivos temporales y backups antiguos
# Uso: ./scripts/cleanup-temp.sh [--days 7] [--dry-run]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DAYS=7
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --days) shift; DAYS="$1" ;;
        --dry-run) DRY_RUN=true ;;
        -h|--help)
            echo "Usage: $0 [--days N] [--dry-run]"
            echo "  --days N     Keep backups newer than N days (default: 7)"
            echo "  --dry-run    Show what would be deleted without deleting"
            exit 0
            ;;
    esac
done

echo "=========================================="
echo "  QuinotoSpec - Cleanup"
echo "=========================================="
echo ""

TOTAL_FREED=0
TOTAL_DELETED=0

# 1. Clean old backups in .quinoto-spec/backups/ (if in a project context)
echo "--- Backups ---"
if [ -d "$PROJECT_ROOT/.quinoto-spec/backups" ]; then
    OLD_BACKUPS=$(find "$PROJECT_ROOT/.quinoto-spec/backups" -maxdepth 1 -type d -mtime +$DAYS -name "backup-*" 2>/dev/null)
    if [ -n "$OLD_BACKUPS" ]; then
        while IFS= read -r backup; do
            SIZE=$(du -sh "$backup" 2>/dev/null | cut -f1)
            if [ "$DRY_RUN" = true ]; then
                echo "  [DRY RUN] Would delete: $(basename "$backup") ($SIZE)"
            else
                rm -rf "$backup"
                echo "  Deleted: $(basename "$backup") ($SIZE)"
            fi
            TOTAL_DELETED=$((TOTAL_DELETED + 1))
        done <<< "$OLD_BACKUPS"
    else
        echo "  No backups older than $DAYS days"
    fi
else
    echo "  No .quinoto-spec/backups/ directory found (not a project)"
fi
echo ""

# 2. Clean temp scripts
echo "--- Temp Scripts ---"
TEMP_SCRIPTS=$(find "$PROJECT_ROOT" -name "temp_*" -type f -mtime +$DAYS 2>/dev/null)
if [ -n "$TEMP_SCRIPTS" ]; then
    while IFS= read -r temp; do
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY RUN] Would delete: $temp"
        else
            rm -f "$temp"
            echo "  Deleted: $temp"
        fi
        TOTAL_DELETED=$((TOTAL_DELETED + 1))
    done <<< "$TEMP_SCRIPTS"
else
    echo "  No temp files older than $DAYS days"
fi
echo ""

# 3. Clean __pycache__ and .pyc files
echo "--- Python Cache ---"
PYCACHE=$(find "$PROJECT_ROOT" -type d -name "__pycache__" 2>/dev/null)
if [ -n "$PYCACHE" ]; then
    while IFS= read -r cache; do
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY RUN] Would delete: $cache"
        else
            rm -rf "$cache"
            echo "  Deleted: $cache"
        fi
        TOTAL_DELETED=$((TOTAL_DELETED + 1))
    done <<< "$PYCACHE"
else
    echo "  No __pycache__ directories found"
fi
echo ""

# 4. Clean node_modules in fixtures
echo "--- Node Modules in Fixtures ---"
NODE_MODS=$(find "$PROJECT_ROOT/tests/fixtures" -type d -name "node_modules" 2>/dev/null)
if [ -n "$NODE_MODS" ]; then
    while IFS= read -r nm; do
        SIZE=$(du -sh "$nm" 2>/dev/null | cut -f1)
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY RUN] Would delete: $nm ($SIZE)"
        else
            rm -rf "$nm"
            echo "  Deleted: $nm ($SIZE)"
        fi
        TOTAL_DELETED=$((TOTAL_DELETED + 1))
    done <<< "$NODE_MODS"
else
    echo "  No node_modules in fixtures"
fi
echo ""

# Summary
echo "=========================================="
if [ "$DRY_RUN" = true ]; then
    echo "  Dry run: $TOTAL_DELETED items would be deleted"
else
    echo "  Cleaned: $TOTAL_DELETED items"
fi
echo "=========================================="
