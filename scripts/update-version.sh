#!/bin/bash

# Update Version: Actualiza version en todos los archivos relevantes (Norns — sync atomico)
# Uso: ./scripts/update-version.sh <new-version> [--dry-run]
# Ejemplo: ./scripts/update-version.sh 2.7.0

set -e

NEW_VERSION=""
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        -h|--help)
            echo "Usage: $0 <new-version> [--dry-run]"
            echo "Example: $0 2.7.0"
            echo ""
            echo "Updates version in (Norns — sync atomico):"
            echo "  - install.sh (INSTALLER_VERSION)"
            echo "  - manifest.json (version field)"
            echo "  - .version file"
            echo "  - README.md / README_EN.md (badges version/skills/rules + texto reglas)"
            echo "  - docs/ARCHITECTURE.md (diagrama + headings)"
            echo "  - V3_ROADMAP.md (Version actual)"
            echo "  - scripts/validate-all.sh (EXPECTED_COUNTS)"
            echo "  - CHANGELOG.md (adds new section)"
            exit 0
            ;;
        *) NEW_VERSION="$arg" ;;
    esac
done

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <new-version> [--dry-run]"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (X.Y.Z)"
    exit 1
fi

if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] would update to $NEW_VERSION (no writes)"
    exit 0
fi

echo "Updating version to $NEW_VERSION (Norns)..."

# FS counts for sync
FS_WORKFLOWS=$(find "$PROJECT_ROOT/agent-dist/workflows" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
FS_SKILLS=$(find "$PROJECT_ROOT/agent-dist/skills" -maxdepth 1 -type d 2>/dev/null | wc -l); FS_SKILLS=$((FS_SKILLS - 1))
FS_RULES=$(grep -c "^# " "$PROJECT_ROOT/agent-dist/rules/quinotospec-rules.md" 2>/dev/null || echo 13)

portable_sed() {
    # $1 = sed expr, $2 = file — portable macOS/Linux
    sed -i.bak "$1" "$2" 2>/dev/null || sed -i "$1" "$2"
    rm -f "$2.bak" 2>/dev/null || true
}

# 1. Update install.sh
INSTALL_SH="$PROJECT_ROOT/install.sh"
if [ -f "$INSTALL_SH" ]; then
    portable_sed "s/INSTALLER_VERSION=\"[^\"]*\"/INSTALLER_VERSION=\"$NEW_VERSION\"/" "$INSTALL_SH"
    echo "  Updated install.sh"
fi

# 2. Update manifest.json
MANIFEST="$PROJECT_ROOT/manifest.json"
if [ -f "$MANIFEST" ]; then
    portable_sed "s/\"version\": *\"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" "$MANIFEST"
    echo "  Updated manifest.json"
fi

# 3. Create/update .version file
echo "$NEW_VERSION" > "$PROJECT_ROOT/.version"
echo "  Created .version"

# 4. Sync README badges and rules text
for README in "$PROJECT_ROOT/README.md" "$PROJECT_ROOT/README_EN.md"; do
    if [ -f "$README" ]; then
        portable_sed "s/badge\/version-[0-9.]*-blue/badge\/version-$NEW_VERSION-blue/" "$README"
        portable_sed "s/badge\/skills-[0-9]*-purple/badge\/skills-$FS_SKILLS-purple/" "$README"
        portable_sed "s/badge\/rules-[0-9]*-red/badge\/rules-$FS_RULES-red/" "$README"
        portable_sed "s/badge\/workflows-[0-9]*-purple/badge\/workflows-$FS_WORKFLOWS-purple/" "$README"
        echo "  Synced $(basename "$README") badges ($FS_WORKFLOWS/$FS_SKILLS/$FS_RULES)"
    fi
done

# 5. Sync docs/ARCHITECTURE.md
ARCH="$PROJECT_ROOT/docs/ARCHITECTURE.md"
if [ -f "$ARCH" ]; then
    portable_sed "s/<-- [0-9]* workflows/<-- $FS_WORKFLOWS workflows/" "$ARCH"
    portable_sed "s/<-- [0-9]* skills.*/<-- $FS_SKILLS skills (39 core + $((FS_SKILLS - 39)) utilitarias)/" "$ARCH"
    portable_sed "s/<-- [0-9]* reglas/<-- $FS_RULES reglas/" "$ARCH"
    portable_sed "s/### Workflows ([0-9]*)/### Workflows ($FS_WORKFLOWS)/" "$ARCH"
    portable_sed "s/### Skills ([0-9]*)/### Skills ($FS_SKILLS)/" "$ARCH"
    portable_sed "s/### Reglas ([0-9]*)/### Reglas ($FS_RULES)/" "$ARCH"
    echo "  Synced docs/ARCHITECTURE.md"
fi

# 6. Sync V3_ROADMAP.md
ROADMAP="$PROJECT_ROOT/V3_ROADMAP.md"
if [ -f "$ROADMAP" ]; then
    portable_sed "s/\*\*Version actual:\*\* [0-9.]*/\*\*Version actual:\*\* $NEW_VERSION/" "$ROADMAP"
    echo "  Synced V3_ROADMAP.md"
fi

# 7. Sync validate-all.sh expected counts
VALIDATE="$PROJECT_ROOT/scripts/validate-all.sh"
if [ -f "$VALIDATE" ]; then
    portable_sed "s/EXPECTED_COUNTS=.*/EXPECTED_COUNTS=(\"workflows:$FS_WORKFLOWS\" \"skills:$FS_SKILLS\" \"agents:9\")/" "$VALIDATE"
    echo "  Synced scripts/validate-all.sh"
fi

# 8. Sync README rules count text (12->13 etc) — handle both languages
for README in "$PROJECT_ROOT/README.md" "$PROJECT_ROOT/README_EN.md"; do
    if [ -f "$README" ]; then
        # ES: "12 reglas estrictas" -> "13 reglas"
        portable_sed "s/[0-9]* reglas estrictas/$FS_RULES reglas estrictas/" "$README"
        portable_sed "s/[0-9]* strict rules/$FS_RULES strict rules/" "$README"
        # Governance system
        portable_sed "s/Sistema de gobernanza con [0-9]* reglas/Sistema de gobernanza con $FS_RULES reglas/" "$README"
        portable_sed "s/Governance system with [0-9]* rules/Governance system with $FS_RULES rules/" "$README"
    fi
done

# 9. Add CHANGELOG.md section
CHANGELOG="$PROJECT_ROOT/CHANGELOG.md"
if [ -f "$CHANGELOG" ]; then
    TODAY=$(date +%Y-%m-%d)
    EDITION_NAME="v$NEW_VERSION"

    MAJOR=$(echo "$NEW_VERSION" | cut -d. -f1)
    MINOR=$(echo "$NEW_VERSION" | cut -d. -f2)
    # (patch intentionally unused in edition naming)

    if [ "$MAJOR" -ge 3 ]; then
        EDITION_NAME="Warband: Hird Edition"
    elif [ "$MAJOR" -eq 2 ] && [ "$MINOR" -ge 6 ]; then
        EDITION_NAME="Yggdrasil — Tiwaz Rune"
    elif [ "$MAJOR" -ge 2 ] && [ "$MINOR" -ge 1 ]; then
        EDITION_NAME="Berserker Edition"
    fi

    # Portable insert after first "---" (header separator) — use ed-like via awk
    awk -v ver="$NEW_VERSION" -v today="$TODAY" -v edition="$EDITION_NAME" '
        NR==1 {print; next}
        /^---$/ && !done {print; print ""; print "## [" ver "] - " today " - " edition; print ""; print "### Summary"; print "- Release " ver; print ""; print "### Changed"; print "- See git log for details"; done=1; next}
        {print}
    ' "$CHANGELOG" > "$CHANGELOG.tmp" && mv "$CHANGELOG.tmp" "$CHANGELOG"
    echo "  Updated CHANGELOG.md ($EDITION_NAME)"
fi

echo ""
echo "Version updated to $NEW_VERSION (Norns sync: $FS_WORKFLOWS/$FS_SKILLS/$FS_RULES)"
echo ""
echo "Next steps:"
echo "  1. Review CHANGELOG.md and update release notes"
echo "  2. Run ./tests/run-all-tests.sh && ./scripts/validate-all.sh --strict"
echo "  3. Commit: git add -A && git commit -m 'chore: bump version to $NEW_VERSION (Norns)'"
echo "  4. Tag: git tag -a v$NEW_VERSION -m 'Release v$NEW_VERSION'"
