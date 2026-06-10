#!/bin/bash

# Install Git Hooks: Symlinks hooks from .githooks/ to .git/hooks/
# Usage: ./scripts/install-hooks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.githooks"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "Error: Not a git repository"
    exit 1
fi

echo "Installing git hooks..."

for hook in "$HOOKS_DIR"/*; do
    if [ ! -f "$hook" ]; then continue; fi
    
    hook_name=$(basename "$hook")
    target="$GIT_HOOKS_DIR/$hook_name"
    
    # Remove existing hook if present
    if [ -f "$target" ] || [ -L "$target" ]; then
        rm -f "$target"
    fi
    
    # Create symlink
    ln -s "$hook" "$target"
    chmod +x "$hook"
    echo "  Installed: $hook_name"
done

echo ""
echo "Git hooks installed successfully"
echo "Hooks: $(ls "$HOOKS_DIR" | tr '\n' ', ' | sed 's/,$//')"
