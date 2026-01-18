#!/bin/bash

# QuinotoSpec Installer

echo "Installing QuinotoSpec..."

# 1. Location Check
# We assume the user is running this from inside the package directory, 
# or copying the files to their root.
# Let's try to copy things to the current directory's parent if we are inside the package folder,
# OR to the current directory if we are at root.

# Simple approach: The user should copy the contents of this folder to their project root 
# OR run this script from the package folder and it installs to relative paths.

# Let's assume the user runs `./quinotospec-package/install.sh` FROM the project root
# OR runs `./install.sh` FROM inside `quinotospec-package`.

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
    # Resolve relative paths relative to where the script is run (which might be confusing)
    # or just treat it as absolute/relative. Ideally we want absolute.
    # Let's simple check if directory exists or try to create it.
    
    # Expand tilde if present (basic handling)
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

# 3. Copy .agent folder
echo "Copying .agent configuration..."

# Create .agent directory if it doesn't exist
if [ ! -d "$TARGET_ROOT/.agent" ]; then
    mkdir -p "$TARGET_ROOT/.agent"
fi

# Copy contents of agent-dist into .agent, overwriting existing files
# We use cp -rf to force overwrite and recursive copy.
# The 'slash-dot' notation "$SOURCE_AGENT/." ensures we copy contents, not the directory itself.
cp -rf "$SOURCE_AGENT/." "$TARGET_ROOT/.agent/"


echo "Installation complete!"
echo "----------------------------------------------------------------"
echo "You can now use @quinotospec workflows."
echo "Read the guide at docs/quinotospec-guide.md to get started."
echo "----------------------------------------------------------------"
