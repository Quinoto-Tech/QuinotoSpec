#!/bin/bash

# QuinotoSpec Installer

echo "Installing QuinotoSpec..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(pwd)"

echo "Installer location: $DIR"
TARGET_ROOT="$PROJECT_ROOT"
GLOBAL_INSTALL=false

if [ -d "$DIR/agent-dist" ]; then
    SOURCE_AGENT="$DIR/agent-dist"
else
    echo "Error: agent-dist directory not found in $DIR"
    exit 1
fi

for arg in "$@"; do
    case "$arg" in
        --cursor) IDE_CHOICE="cursor" ;;
        --opencode) IDE_CHOICE="opencode" ;;
        
        --global|--root) GLOBAL_INSTALL=true ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --cursor    Install for Cursor"
            echo "  --opencode  Install for OpenCode"
            
            echo "  --global, --root  Install globally in ~/.config/, ignoring project directory"
            echo "  -h, --help  Show this help"
            exit 0
            ;;
    esac
done

if [ "$GLOBAL_INSTALL" = true ]; then
    TARGET_ROOT="$HOME/.config"
    echo "Installing globally to ~/.config/"
else
    echo -n "Enter the installation path (default: current directory '$PROJECT_ROOT'): "
    read USER_PATH

    if [ -n "$USER_PATH" ]; then
        USER_PATH="${USER_PATH/\~/$HOME}"

        if [ ! -d "$USER_PATH" ]; then
            echo "Directory $USER_PATH does not exist. Creating it..."
            mkdir -p "$USER_PATH" || { echo "Error: Could not create directory $USER_PATH"; exit 1; }
        fi
        TARGET_ROOT="$USER_PATH"
    fi
fi

echo "Target Project Root: $TARGET_ROOT"

# IDE Selection
if [ -z "$IDE_CHOICE" ]; then
    echo ""
    echo "Select your IDE/AI Assistant:"
    echo "  1) OpenAI (default)"
    echo "  2) Cursor"
    echo "  3) OpenCode"
    echo "  4) Cline"
    echo ""
    echo -n "Enter your choice [1-4]: "
    read IDE_CHOICE

    case "$IDE_CHOICE" in
        1) IDE_CHOICE="openai" ;;
        2) IDE_CHOICE="cursor" ;;
        3) IDE_CHOICE="opencode" ;;
        4) IDE_CHOICE="cline" ;;
        *) IDE_CHOICE="openai" ;;
    esac
fi

# Execute installation based on IDE choice
case "$IDE_CHOICE" in
    cursor)
        echo "Installing for Cursor..."
        if [ "$GLOBAL_INSTALL" = true ]; then
            CONFIG_DIR_NAME="cursor"
        else
            CONFIG_DIR_NAME=".cursor"
        fi

        if [ ! -d "$TARGET_ROOT/$CONFIG_DIR_NAME" ]; then
            mkdir -p "$TARGET_ROOT/$CONFIG_DIR_NAME"
        fi

        cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/$CONFIG_DIR_NAME/"

        if [ -d "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" ]; then
            rm -rf "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
            mv "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
        fi

        cp "$DIR/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
        ;;
        
    opencode)
        echo "Installing for OpenCode..."
        if [ "$GLOBAL_INSTALL" = true ]; then
            CONFIG_DIR_NAME="opencode"
        else
            CONFIG_DIR_NAME=".opencode"
        fi

        if [ ! -d "$TARGET_ROOT/$CONFIG_DIR_NAME" ]; then
            mkdir -p "$TARGET_ROOT/$CONFIG_DIR_NAME"
        fi

        cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/$CONFIG_DIR_NAME/"

        if [ -d "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" ]; then
            rm -rf "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
            mv "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
        fi

        cp "$DIR/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
        ;;

    *)
        echo "Installing for OpenAI (default)..."
        CONFIG_DIR_NAME=".agent"
        
        if [ ! -d "$TARGET_ROOT/$CONFIG_DIR_NAME" ]; then
            mkdir -p "$TARGET_ROOT/$CONFIG_DIR_NAME"
        fi
        
        cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/$CONFIG_DIR_NAME/"

        cp "$DIR/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
        ;;
esac

echo ""
echo "======================================================================"
case "$IDE_CHOICE" in
    cursor)
        echo "Installation complete for Cursor!"
        if [ "$GLOBAL_INSTALL" = true ]; then
            echo "Installed to ~/.config/cursor/"
        else
            echo "Use @quinotospec commands."
        fi
        ;;
    opencode)
        echo "Installation complete for OpenCode!"
        if [ "$GLOBAL_INSTALL" = true ]; then
            echo "Installed to ~/.config/opencode/"
        else
            echo "Use @quinotospec commands."
        fi
        ;;
    *)
        echo "Installation complete!"
        echo "Use @quinotospec workflows."
        ;;
esac
echo "======================================================================"
