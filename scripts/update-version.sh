#!/bin/bash

# Update Version: Actualiza version en todos los archivos relevantes
# Uso: ./scripts/update-version.sh <new-version>
# Ejemplo: ./scripts/update-version.sh 2.1.0

set -e

if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 <new-version>"
    echo "Example: $0 2.1.0"
    echo ""
    echo "Updates version in:"
    echo "  - install.sh (INSTALLER_VERSION)"
    echo "  - manifest.json (version field)"
    echo "  - .version file"
    echo "  - CHANGELOG.md (adds new section)"
    exit 1
fi

NEW_VERSION="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (X.Y.Z)"
    exit 1
fi

echo "Updating version to $NEW_VERSION..."

# 1. Update install.sh
INSTALL_SH="$PROJECT_ROOT/install.sh"
if [ -f "$INSTALL_SH" ]; then
    sed -i "s/INSTALLER_VERSION=\"[^\"]*\"/INSTALLER_VERSION=\"$NEW_VERSION\"/" "$INSTALL_SH"
    echo "  Updated install.sh"
fi

# 2. Update manifest.json
MANIFEST="$PROJECT_ROOT/manifest.json"
if [ -f "$MANIFEST" ]; then
    sed -i "s/\"version\": *\"[^\"]*\"/\"version\": \"$NEW_VERSION\"/" "$MANIFEST"
    echo "  Updated manifest.json"
fi

# 3. Create/update .version file
echo "$NEW_VERSION" > "$PROJECT_ROOT/.version"
echo "  Created .version"

# 4. Add CHANGELOG.md section
CHANGELOG="$PROJECT_ROOT/CHANGELOG.md"
if [ -f "$CHANGELOG" ]; then
    TODAY=$(date +%Y-%m-%d)
    EDITION_NAME="v$NEW_VERSION"
    
    # Determine edition name based on version
    MAJOR=$(echo "$NEW_VERSION" | cut -d. -f1)
    MINOR=$(echo "$NEW_VERSION" | cut -d. -f2)
    
    if [ "$MAJOR" -ge 3 ]; then
        EDITION_NAME="Warband: Hird Edition"
    elif [ "$MAJOR" -ge 2 ] && [ "$MINOR" -ge 1 ]; then
        EDITION_NAME="Berserker Edition"
    fi
    
    # Insert new version section after the header
    sed -i "/^---$/a\\
\\
## [$NEW_VERSION] - $TODAY - $EDITION_NAME\\
\\
### Summary\\
- Release $NEW_VERSION\\
\\
### Changed\\
- See git log for details" "$CHANGELOG"
    echo "  Updated CHANGELOG.md"
fi

echo ""
echo "Version updated to $NEW_VERSION"
echo ""
echo "Next steps:"
echo "  1. Review CHANGELOG.md and update release notes"
echo "  2. Run ./tests/run-all-tests.sh to verify"
echo "  3. Commit changes: git add -A && git commit -m 'chore: bump version to $NEW_VERSION'"
echo "  4. Tag: git tag -a v$NEW_VERSION -m 'Release v$NEW_VERSION'"
