#!/bin/bash

# QuinotoSpec Installer

echo "Installing QuinotoSpec..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(pwd)"

echo "Installer location: $DIR"
echo "Target Project Root: $PROJECT_ROOT"

if [ -d "$DIR/agent-dist" ]; then
    SOURCE_AGENT="$DIR/agent-dist"
else
    echo "Error: agent-dist directory not found in $DIR"
    exit 1
fi

# 2. Ask for Target Directory
echo -n "Enter the installation path (default: current directory '$PROJECT_ROOT'): "
read USER_PATH

if [ -n "$USER_PATH" ]; then
    USER_PATH="${USER_PATH/\~/$HOME}"
    
    if [ ! -d "$USER_PATH" ]; then
        echo "Directory $USER_PATH does not exist. Creating it..."
        mkdir -p "$USER_PATH" || { echo "Error: Could not create directory $USER_PATH"; exit 1; }
    fi
    TARGET_ROOT="$USER_PATH"
else
    TARGET_ROOT="$PROJECT_ROOT"
fi

echo "Target Project Root: $TARGET_ROOT"

# IDE Selection
IDE_CHOICE=""

# Check for command line arguments first
for arg in "$@"; do
    if [ "$arg" == "--cursor" ]; then
        IDE_CHOICE="cursor"
    elif [ "$arg" == "--opencode" ]; then
        IDE_CHOICE="opencode"
    elif [ "$arg" == "--cline" ]; then
        IDE_CHOICE="cline"
    fi
done

# If no argument provided, show menu
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
        CONFIG_DIR_NAME=".cursor"
        
        if [ ! -d "$TARGET_ROOT/$CONFIG_DIR_NAME" ]; then
            mkdir -p "$TARGET_ROOT/$CONFIG_DIR_NAME"
        fi
        
        cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/$CONFIG_DIR_NAME/"
        
        if [ -d "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" ]; then
            rm -rf "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
            mv "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
        fi
        ;;
        
    opencode)
        echo "Installing for OpenCode..."
        CONFIG_DIR_NAME=".opencode"
        
        if [ ! -d "$TARGET_ROOT/$CONFIG_DIR_NAME" ]; then
            mkdir -p "$TARGET_ROOT/$CONFIG_DIR_NAME"
        fi
        
        cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/$CONFIG_DIR_NAME/"
        
        if [ -d "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" ]; then
            rm -rf "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
            mv "$TARGET_ROOT/$CONFIG_DIR_NAME/workflows" "$TARGET_ROOT/$CONFIG_DIR_NAME/commands"
        fi
        ;;
        
    cline)
        echo "Installing for Cline..."
        
        if [ ! -d "$TARGET_ROOT/.cline" ]; then
            mkdir -p "$TARGET_ROOT/.cline"
        fi
        
        if [ ! -d "$TARGET_ROOT/.clinerules" ]; then
            mkdir -p "$TARGET_ROOT/.clinerules"
        fi
        
        if [ -d "$SOURCE_AGENT/skills" ]; then
            mkdir -p "$TARGET_ROOT/.cline/skills"
            cp -rf "$SOURCE_AGENT/skills/." "$TARGET_ROOT/.cline/skills/"
        fi
        
        if [ -d "$SOURCE_AGENT/rules" ]; then
            cp -rf "$SOURCE_AGENT/rules/." "$TARGET_ROOT/.clinerules/"
        fi
        
        if [ -d "$SOURCE_AGENT/workflows" ]; then
            mkdir -p "$TARGET_ROOT/.clinerules/workflows"
            cp -rf "$SOURCE_AGENT/workflows/." "$TARGET_ROOT/.clinerules/workflows/"
        fi
        ;;
        
    *)
        echo "Installing for OpenAI (default)..."
        CONFIG_DIR_NAME=".agent"
        
        if [ ! -d "$TARGET_ROOT/$CONFIG_DIR_NAME" ]; then
            mkdir -p "$TARGET_ROOT/$CONFIG_DIR_NAME"
        fi
        
        cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/$CONFIG_DIR_NAME/"
        ;;
esac

echo ""
echo "======================================================================"
case "$IDE_CHOICE" in
    cursor)
        echo "Installation complete for Cursor!"
        echo "Use @quinotospec commands."
        ;;
    opencode)
        echo "Installation complete for OpenCode!"
        echo "Use @quinotospec commands."
        ;;
    cline)
        echo "Installation complete for Cline!"
        echo "Skills: .cline/skills/"
        echo "Rules: .clinerules/"
        echo "Workflows: .clinerules/workflows/"
        ;;
    *)
        echo "Installation complete!"
        echo "Use @quinotospec workflows."
        ;;
esac
echo "======================================================================"
