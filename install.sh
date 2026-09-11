#!/bin/bash

# QuinotoSpec Installer v2.6.0
# Instala QuinotoSpec en el IDE seleccionado con validación post-instalación

set -euo pipefail

INSTALLER_VERSION="2.7.0"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
TARGET_ROOT="$PROJECT_ROOT"
GLOBAL_INSTALL=false
ACTION="install"
VERIFY_ONLY=false
ASSUME_YES=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   QuinotoSpec Installer v${INSTALLER_VERSION}              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

show_help() {
    echo "QuinotoSpec Installer v${INSTALLER_VERSION}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Installation Options:"
    echo "  --cursor          Install for Cursor"
    echo "  --opencode        Install for OpenCode"
    echo "  --cline           Install for Cline"
    echo "  --antigravity     Install for Antigravity (AGY)"
    echo "  --generic         Install for Generic (.agent/)"
    echo "  --global, --root  Install globally in ~/.config/ or ~/.gemini/config"
    echo ""
    echo "Management Options:"
    echo "  --verify          Verify existing installation"
    echo "  --uninstall       Uninstall QuinotoSpec"
    echo "  --yes, -y         Non-interactive mode (accept all defaults and confirmations)"
    echo "  --version         Show installer version"
    echo "  -h, --help        Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --opencode                    # Install for OpenCode (interactive path)"
    echo "  $0 --cursor --global             # Install for Cursor globally"
    echo "  $0 --antigravity --global        # Install for Antigravity globally"
    echo "  $0 --opencode --global           # Install for OpenCode globally"
    echo "  $0 --verify --opencode --global  # Verify global OpenCode installation"
    echo "  $0 --verify --antigravity --global # Verify global Antigravity installation"
    echo "  $0 --uninstall --cursor          # Uninstall Cursor installation"
    exit 0
}

show_version() {
    echo "QuinotoSpec Installer v${INSTALLER_VERSION}"
    exit 0
}

check_dependencies() {
    local has_error=0

    print_info "Checking dependencies..."

    # Check bash version (>= 4.0)
    local bash_major="${BASH_VERSION%%.*}"
    if [ "$bash_major" -lt 4 ]; then
        print_error "Bash 4.0+ required (current: $BASH_VERSION)"
        echo "  Install with: sudo apt install bash (Linux) or brew install bash (macOS)"
        has_error=1
    else
        print_success "Bash $BASH_VERSION"
    fi

    # Check git
    if command -v git &>/dev/null; then
        local git_version
        git_version=$(git --version | awk '{print $3}')
        print_success "Git $git_version"
    else
        print_error "Git not found"
        echo "  Install with: sudo apt install git (Linux) or brew install git (macOS)"
        has_error=1
    fi

    # Check source directory
    if [ -d "$DIR/agent-dist" ]; then
        print_success "Source agent-dist found"
    else
        print_error "agent-dist directory not found in $DIR"
        has_error=1
    fi

    if [ $has_error -eq 1 ]; then
        print_error "Dependencies check failed. Install missing dependencies and retry."
        exit 1
    fi

    echo ""
}

verify_installation() {
    local config_dir="$1"
    local ide_name="$2"
    local errors=0

    print_info "Verifying $ide_name installation at $config_dir..."
    echo ""

    # Check config directory exists
    if [ ! -d "$config_dir" ]; then
        print_error "Configuration directory not found: $config_dir"
        return 1
    fi
    print_success "Configuration directory exists"

    # Check critical directories
    local dirs_to_check=("rules" "skills" "templates")
    for dir in "${dirs_to_check[@]}"; do
        if [ -d "$config_dir/$dir" ]; then
            print_success "Directory $dir/ exists"
        else
            print_error "Directory $dir/ missing"
            errors=$((errors + 1))
        fi
    done

    # Check workflows or commands directory
    if [ -d "$config_dir/workflows" ] || [ -d "$config_dir/commands" ]; then
        print_success "Workflows/commands directory exists"
    else
        print_error "Neither workflows/ nor commands/ directory found"
        errors=$((errors + 1))
    fi

    # Check critical files
    if [ -f "$config_dir/rules/quinotospec-rules.md" ]; then
        print_success "Rules file exists"
    else
        print_error "Rules file missing: rules/quinotospec-rules.md"
        errors=$((errors + 1))
    fi

    # Check AGENTS.md in target root
    local agents_md="$TARGET_ROOT/AGENTS.md"
    if [ -f "$agents_md" ]; then
        print_success "AGENTS.md exists"
    else
        print_warning "AGENTS.md not found at $agents_md"
    fi

    # Count installed components
    local workflow_count=0
    if [ -d "$config_dir/workflows" ]; then
        workflow_count=$(find "$config_dir/workflows" -name "*.md" 2>/dev/null | wc -l)
    elif [ -d "$config_dir/commands" ]; then
        workflow_count=$(find "$config_dir/commands" -name "*.md" 2>/dev/null | wc -l)
    fi
    local skill_count
    skill_count=$(find "$config_dir/skills" -name "SKILL.md" 2>/dev/null | wc -l)

    echo ""
    echo "  Components: $workflow_count workflows, $skill_count skills"

    if [ $errors -gt 0 ]; then
        echo ""
        print_error "Verification failed with $errors errors"
        return 1
    fi

    echo ""
    print_success "Installation verified successfully"
    return 0
}

get_config_dir() {
    local ide="$1"
    local global="$2"

    case "$ide" in
        cursor)
            [ "$global" = true ] && echo "$HOME/.config/cursor" || echo "$TARGET_ROOT/.cursor"
            ;;
        opencode)
            [ "$global" = true ] && echo "$HOME/.config/opencode" || echo "$TARGET_ROOT/.opencode"
            ;;
        cline)
            [ "$global" = true ] && echo "$HOME/.config/cline" || echo "$TARGET_ROOT/.cline"
            ;;
        antigravity)
            [ "$global" = true ] && echo "$HOME/.gemini/config" || echo "$TARGET_ROOT/.agents"
            ;;
        *)
            [ "$global" = true ] && echo "$HOME/.config/agent" || echo "$TARGET_ROOT/.agent"
            ;;
    esac
}

uninstall() {
    local ide="$1"
    local config_dir
    config_dir=$(get_config_dir "$ide" "$GLOBAL_INSTALL")

    print_info "Uninstalling QuinotoSpec from $config_dir..."

    if [ ! -d "$config_dir" ]; then
        print_warning "Directory not found: $config_dir (nothing to uninstall)"
        exit 0
    fi

    # Safety check: only delete if the directory actually contains QuinotoSpec files
    local is_quinoto=false
    if [ -f "$config_dir/rules/quinotospec-rules.md" ]; then
        is_quinoto=true
    elif find "$config_dir/skills" -maxdepth 2 -name "SKILL.md" -path "*quinotospec*" 2>/dev/null | grep -q .; then
        is_quinoto=true
    fi

    if [ "$is_quinoto" != "true" ]; then
        print_error "Refusing to delete $config_dir: no QuinotoSpec files detected (rules/quinotospec-rules.md or quinotospec skills not found)"
        echo "  If this is the correct directory, remove it manually."
        exit 1
    fi

    if [ "$ASSUME_YES" != "true" ]; then
        echo ""
        echo -n "Are you sure you want to remove $config_dir? [y/N]: "
        read -r confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            print_info "Uninstall cancelled"
            exit 0
        fi
    fi

    rm -rf "$config_dir"
    print_success "Removed $config_dir"

    # Remove AGENTS.md if it exists and was installed by us
    if [ -f "$TARGET_ROOT/AGENTS.md" ] && grep -q "Guía para Agentes QuinotoSpec\|QuinotoSpec Agent Guide" "$TARGET_ROOT/AGENTS.md" 2>/dev/null; then
        local remove_agents="n"
        if [ "$ASSUME_YES" = "true" ]; then
            remove_agents="y"
        else
            echo -n "Also remove AGENTS.md? [y/N]: "
            read -r remove_agents
        fi
        if [ "$remove_agents" = "y" ] || [ "$remove_agents" = "Y" ]; then
            rm -f "$TARGET_ROOT/AGENTS.md"
            print_success "Removed AGENTS.md"
        fi
    fi

    echo ""
    print_success "Uninstall complete"
    exit 0
}

# Parse arguments
IDE_CHOICE=""
for arg in "$@"; do
    case "$arg" in
        --cursor) IDE_CHOICE="cursor" ;;
        --opencode) IDE_CHOICE="opencode" ;;
        --cline) IDE_CHOICE="cline" ;;
        --antigravity) IDE_CHOICE="antigravity" ;;
        --generic) IDE_CHOICE="generic" ;;
        --global|--root) GLOBAL_INSTALL=true ;;
        --verify) VERIFY_ONLY=true ;;
        --uninstall) ACTION="uninstall" ;;
        --yes|-y) ASSUME_YES=true ;;
        --version) show_version ;;
        -h|--help) show_help ;;
        *)
            print_error "Unknown option: $arg"
            echo "Run $0 --help for usage"
            exit 1
            ;;
    esac
done

print_header

# Handle uninstall
if [ "$ACTION" = "uninstall" ]; then
    if [ -z "$IDE_CHOICE" ]; then
        print_error "--uninstall requires an IDE flag (--opencode, --cursor, --cline, --antigravity)"
        exit 1
    fi
    uninstall "$IDE_CHOICE"
fi

# Check dependencies
check_dependencies

# Handle verify-only mode
if [ "$VERIFY_ONLY" = true ]; then
    if [ -z "$IDE_CHOICE" ]; then
        print_error "--verify requires an IDE flag (--opencode, --cursor, --cline, --antigravity)"
        exit 1
    fi
    config_dir=$(get_config_dir "$IDE_CHOICE" "$GLOBAL_INSTALL")
    if verify_installation "$config_dir" "$IDE_CHOICE"; then
        exit 0
    else
        exit 1
    fi
fi

# Determine target directory
if [ "$GLOBAL_INSTALL" = true ]; then
    if [ "$IDE_CHOICE" = "antigravity" ]; then
        TARGET_ROOT="$HOME/.gemini"
        print_info "Installing globally to ~/.gemini/config/"
    else
        TARGET_ROOT="$HOME/.config"
        print_info "Installing globally to ~/.config/"
    fi
elif [ "$ASSUME_YES" = true ]; then
    print_info "Non-interactive mode: installing to current directory '$PROJECT_ROOT'"
else
    echo -n "Enter the installation path (default: current directory '$PROJECT_ROOT'): "
    read -r USER_PATH

    if [ -n "$USER_PATH" ]; then
        USER_PATH="${USER_PATH/\~/$HOME}"

        if [ ! -d "$USER_PATH" ]; then
            print_info "Directory $USER_PATH does not exist. Creating it..."
            mkdir -p "$USER_PATH" || { print_error "Could not create directory $USER_PATH"; exit 1; }
        fi
        TARGET_ROOT="$USER_PATH"
    fi
fi

echo "Target: $TARGET_ROOT"

# IDE Selection (interactive if not provided)
if [ -z "$IDE_CHOICE" ] && [ "$ASSUME_YES" = true ]; then
    print_info "Non-interactive mode: no IDE flag given, defaulting to opencode"
    IDE_CHOICE="opencode"
fi

if [ -z "$IDE_CHOICE" ]; then
    echo ""
    echo "Select your IDE/AI Assistant:"
    echo "  1) OpenCode"
    echo "  2) Cursor"
    echo "  3) Cline"
    echo "  4) Antigravity"
    echo "  5) Generic (.agent/)"
    echo ""
    echo -n "Enter your choice [1-5] (default: 1): "
    read -r choice

    case "$choice" in
        1|"") IDE_CHOICE="opencode" ;;
        2) IDE_CHOICE="cursor" ;;
        3) IDE_CHOICE="cline" ;;
        4) IDE_CHOICE="antigravity" ;;
        5) IDE_CHOICE="generic" ;;
        *) IDE_CHOICE="opencode" ;;
    esac
fi

SOURCE_AGENT="$DIR/agent-dist"

# Execute installation
case "$IDE_CHOICE" in
    cursor|opencode|cline|antigravity)
        echo "Installing for ${IDE_CHOICE^}..."
        config_dir=$(get_config_dir "$IDE_CHOICE" "$GLOBAL_INSTALL")

        mkdir -p "$config_dir"
        cp -rf "$SOURCE_AGENT/." "$config_dir/"

        # Rename workflows to commands for Cursor/OpenCode
        if [ "$IDE_CHOICE" = "cursor" ] || [ "$IDE_CHOICE" = "opencode" ]; then
            if [ -d "$config_dir/workflows" ]; then
                rm -rf "$config_dir/commands"
                mv "$config_dir/workflows" "$config_dir/commands"
            fi
        fi

        # Copy AGENTS.md unless target root is the source repo itself (same file)
        if [ "$TARGET_ROOT/AGENTS.md" != "$DIR/AGENTS.md" ]; then
            cp "$DIR/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
        fi
        ;;

    *)
        echo "Installing for Generic (.agent/)..."
        config_dir=$(get_config_dir "generic" "$GLOBAL_INSTALL")

        mkdir -p "$config_dir"
        cp -rf "$SOURCE_AGENT/." "$config_dir/"
        if [ "$TARGET_ROOT/AGENTS.md" != "$DIR/AGENTS.md" ]; then
            cp "$DIR/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
        fi
        ;;
esac

echo ""
echo "======================================================================"
print_success "Installation complete for ${IDE_CHOICE^}!"
echo ""

# Auto-verify installation
print_info "Running post-installation verification..."
echo ""
VERIFY_RESULT=0
if ! verify_installation "$config_dir" "$IDE_CHOICE"; then
    VERIFY_RESULT=1
fi

echo ""
echo "======================================================================"
if [ "$GLOBAL_INSTALL" = true ]; then
    case "$IDE_CHOICE" in
        cursor)      echo "Installed to ~/.config/cursor/" ;;
        opencode)    echo "Installed to ~/.config/opencode/" ;;
        cline)       echo "Installed to ~/.config/cline/" ;;
        antigravity) echo "Installed to ~/.gemini/config/" ;;
        *)           echo "Installed to ~/.config/agent/" ;;
    esac
else
    echo "Installed to $config_dir"
fi
echo ""
echo "Use @quinotospec commands in your IDE."
echo "======================================================================"

exit $VERIFY_RESULT
