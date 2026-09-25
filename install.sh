#!/usr/bin/env bash

# QuinotoSpec Installer v3.2.0
# Instala QuinotoSpec en el IDE seleccionado con validación post-instalación

set -euo pipefail

INSTALLER_VERSION="3.2.0"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
TARGET_ROOT="$PROJECT_ROOT"
GLOBAL_INSTALL=false
ACTION="install"
VERIFY_ONLY=false
ASSUME_YES=false
TRANSACTION_DIR=""
FINAL_CONFIG_DIR=""
TRANSACTION_COMMITTED=false
CONFIG_CREATED=false
AGENTS_MANAGED=false
STAGED_AGENTS=""

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

# Titlecase portable (bash 3.2 en macOS no soporta ${var^})
titlecase() {
    echo "$1" | awk '{print toupper(substr($0,1,1)) substr($0,2)}'
}

restore_transaction() {
    if [ "$TRANSACTION_COMMITTED" = true ]; then
        return 0
    fi
    if [ -n "$TRANSACTION_DIR" ] && [ -e "$TRANSACTION_DIR/previous-live" ]; then
        rm -rf -- "$FINAL_CONFIG_DIR"
        if ! mv "$TRANSACTION_DIR/previous-live" "$FINAL_CONFIG_DIR"; then
            print_error "Could not restore previous installation at $FINAL_CONFIG_DIR"
            return 1
        fi
    elif [ "$CONFIG_CREATED" = true ] && [ -n "$FINAL_CONFIG_DIR" ] && [ -e "$FINAL_CONFIG_DIR" ]; then
        rm -rf -- "$FINAL_CONFIG_DIR"
    fi
    if [ -n "$TRANSACTION_DIR" ] && [ -e "$TRANSACTION_DIR/previous-agents" ]; then
        if [ -e "$TARGET_ROOT/AGENTS.md" ]; then
            rm -f -- "$TARGET_ROOT/AGENTS.md"
        fi
        if ! mv "$TRANSACTION_DIR/previous-agents" "$TARGET_ROOT/AGENTS.md"; then
            print_error "Could not restore previous AGENTS.md"
            return 1
        fi
    fi
    return 0
}

cleanup_transaction() {
    local status=$?
    trap - EXIT
    if [ "$TRANSACTION_COMMITTED" != true ]; then
        if ! restore_transaction; then
            status=1
        fi
    fi
    if [ -n "$TRANSACTION_DIR" ] && [ -d "$TRANSACTION_DIR" ]; then
        rm -rf -- "$TRANSACTION_DIR"
    fi
    exit "$status"
}

begin_transaction() {
    local final_config_dir="$1"
    FINAL_CONFIG_DIR="$final_config_dir"
    if [ -L "$FINAL_CONFIG_DIR" ] || { [ -e "$FINAL_CONFIG_DIR" ] && [ ! -d "$FINAL_CONFIG_DIR" ]; }; then
        print_error "Refusing to use a symlink or non-directory target: $FINAL_CONFIG_DIR"
        return 1
    fi
    local parent
    parent=$(dirname "$FINAL_CONFIG_DIR")
    mkdir -p "$parent"
    TRANSACTION_DIR=$(mktemp -d "${parent}/.quinotospec-install.XXXXXX")
    mkdir -p "$TRANSACTION_DIR/candidate" "$TRANSACTION_DIR/candidate-root"
    trap cleanup_transaction EXIT
    if [ -d "$FINAL_CONFIG_DIR" ]; then
        if ! cp -a "$FINAL_CONFIG_DIR/." "$TRANSACTION_DIR/candidate/"; then
            print_error "Could not stage existing configuration at $FINAL_CONFIG_DIR"
            return 1
        fi
        CONFIG_CREATED=false
    else
        CONFIG_CREATED=true
    fi
    return 0
}

prepare_candidate() {
    local previous_manifest="$FINAL_CONFIG_DIR/.quinoto-spec/ownership.json"
    if [ -f "$previous_manifest" ]; then
        if ! python3 - "$previous_manifest" "$TRANSACTION_DIR/candidate" <<'PY'
import hashlib
import json
import sys
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


manifest_path = Path(sys.argv[1])
candidate = Path(sys.argv[2])
try:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit("ownership manifest is invalid: " + str(error))
if not isinstance(data, dict) or data.get("schema_version") != 1:
    raise SystemExit("ownership manifest schema is unsupported")
for item in data.get("owned", []):
    if not isinstance(item, dict):
        raise SystemExit("ownership manifest contains an invalid entry")
    relative = item.get("path")
    expected = item.get("sha256")
    if not isinstance(relative, str) or not isinstance(expected, str) or not expected:
        raise SystemExit("ownership manifest entry is incomplete")
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts or relative == ".quinoto-spec/ownership.json":
        raise SystemExit("ownership manifest path is unsafe: " + relative)
    target = candidate / relative_path
    if target.is_symlink():
        raise SystemExit("managed path is a symlink: " + relative)
    if target.is_file():
        if digest(target) != expected:
            raise SystemExit("managed file was modified outside the installer: " + relative)
        target.unlink()
for directory in sorted((path for path in candidate.rglob("*") if path.is_dir()), key=lambda path: len(path.parts), reverse=True):
    try:
        directory.rmdir()
    except OSError:
        pass
PY
        then
            return 1
        fi
    fi
    return 0
}

reject_candidate_symlinks() {
    if ! python3 - "$TRANSACTION_DIR/candidate" <<'PY'
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
for path in candidate.rglob("*"):
    if path.is_symlink():
        raise SystemExit("staged configuration contains a symlink: " + str(path))
PY
    then
        return 1
    fi
    return 0
}

check_agents_conflict() {
    local target_agents="$TARGET_ROOT/AGENTS.md"
    if [ "$target_agents" = "$DIR/AGENTS.md" ] || [ ! -e "$target_agents" ]; then
        return 0
    fi
    if [ -L "$target_agents" ]; then
        print_error "Refusing to replace symlinked AGENTS.md: $target_agents"
        return 1
    fi
    local previous_manifest="$FINAL_CONFIG_DIR/.quinoto-spec/ownership.json"
    if [ -f "$previous_manifest" ]; then
        if ! python3 - "$previous_manifest" "$target_agents" <<'PY'
import hashlib
import json
import sys
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
target = Path(sys.argv[2])
agents = manifest.get("agents")
if isinstance(agents, dict) and agents.get("managed"):
    if not target.is_file() or digest(target) != agents.get("sha256"):
        raise SystemExit("AGENTS.md was modified outside the installer")
PY
        then
            return 1
        fi
        return 0
    fi
    if ! grep -q "Guía para Agentes QuinotoSpec\|QuinotoSpec Agent Guide" "$target_agents" 2>/dev/null; then
        print_error "Refusing to overwrite foreign AGENTS.md: $target_agents"
        return 1
    fi
    return 0
}

write_ownership_manifest() {
    local candidate="$1"
    local ide="$2"
    local target_root="$3"
    local final_config="$4"
    local agents_managed="$5"
    if ! python3 - "$DIR" "$candidate" "$ide" "$target_root" "$final_config" "$STAGED_AGENTS" "$agents_managed" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


source = Path(sys.argv[1])
candidate = Path(sys.argv[2])
ide = sys.argv[3]
target_root = Path(sys.argv[4])
final_config = Path(sys.argv[5])
staged_agents = Path(sys.argv[6])
agents_managed = sys.argv[7] == "true"
owned = set()


def add_tree(relative_source, relative_destination):
    directory = source / relative_source
    if not directory.is_dir():
        return
    for path in directory.rglob("*"):
        if path.is_file() or path.is_symlink():
            relative = path.relative_to(directory)
            owned.add((Path(relative_destination) / relative).as_posix())


add_tree("agent-dist/rules", "rules")
add_tree("agent-dist/skills", "skills")
add_tree("agent-dist/agents", "agents")
add_tree("agent-dist/templates", "templates")
add_tree("agent-dist/bootstrap", "bootstrap")
add_tree("agent-dist/hooks", "hooks")
add_tree("agent-dist/plugins", "plugins")
workflow_destination = "commands" if ide in {"cursor", "opencode", "claude"} else "workflows"
add_tree("agent-dist/workflows", workflow_destination)
if ide == "opencode":
    owned.add("plugins/quinotospec-plugin.js")
if ide == "cursor":
    add_tree("agent-dist/skills", "quinotospec-plugin/skills")
    add_tree("agent-dist/agents", "quinotospec-plugin/agents")
    add_tree("agent-dist/workflows", "quinotospec-plugin/commands")
    add_tree("agent-dist/rules", "quinotospec-plugin/rules")
    add_tree("agent-dist/hooks", "quinotospec-plugin/hooks")
    owned.add("quinotospec-plugin/.cursor-plugin/plugin.json")
records = []
for relative in sorted(owned):
    path = candidate / relative
    if path.is_symlink():
        raise SystemExit("managed path is a symlink: " + relative)
    if not path.is_file():
        continue
    records.append({"path": relative, "sha256": digest(path)})
external_config = []
hook_commands = []
if ide == "cursor":
    external_config.append({"path": "hooks.json", "managed": False})
    settings_path = candidate / "hooks.json"
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit("Cursor hooks configuration is invalid: " + str(error))
        for entry in settings.get("hooks", {}).get("sessionStart", []):
            if isinstance(entry, dict) and isinstance(entry.get("command"), str):
                hook_commands.append(entry["command"])
elif ide == "claude":
    external_config.append({"path": "settings.json", "managed": False})
    settings_path = candidate / "settings.json"
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit("Claude settings are invalid: " + str(error))
        for entries in settings.get("hooks", {}).values():
            for entry in entries if isinstance(entries, list) else []:
                for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                    if isinstance(hook, dict) and isinstance(hook.get("command"), str):
                        hook_commands.append(hook["command"])
agents = None
if agents_managed and staged_agents.is_file():
    agents = {"path": "AGENTS.md", "managed": True, "sha256": digest(staged_agents)}
manifest = {
    "schema_version": 1,
    "installer_version": "3.1.0",
    "ide": ide,
    "installed_at": datetime.now(timezone.utc).isoformat(),
    "owned": records,
    "external_config": external_config,
    "hook_commands": hook_commands,
    "agents": agents,
}
manifest_path = candidate / ".quinoto-spec/ownership.json"
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
    then
        return 1
    fi
    return 0
}

verify_ownership_manifest() {
    local config_dir="$1"
    local target_root="$2"
    if [ ! -f "$config_dir/.quinoto-spec/ownership.json" ]; then
        print_warning "Ownership manifest missing; legacy installation detected"
        return 0
    fi
    if ! python3 - "$config_dir" "$target_root" <<'PY'
import hashlib
import json
import sys
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


config = Path(sys.argv[1])
target_root = Path(sys.argv[2])
manifest_path = config / ".quinoto-spec/ownership.json"
try:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit("ownership manifest is invalid: " + str(error))
if not isinstance(data, dict) or data.get("schema_version") != 1:
    raise SystemExit("ownership manifest schema is unsupported")
for item in data.get("owned", []):
    if not isinstance(item, dict):
        raise SystemExit("ownership manifest contains an invalid entry")
    relative = Path(item.get("path", ""))
    if relative.is_absolute() or ".." in relative.parts or str(relative) == ".quinoto-spec/ownership.json":
        raise SystemExit("ownership manifest path is unsafe")
    path = config / relative
    if path.is_symlink() or not path.is_file() or digest(path) != item.get("sha256"):
        raise SystemExit("managed file is missing or modified: " + str(relative))
agents = data.get("agents")
if isinstance(agents, dict) and agents.get("managed"):
    path = target_root / agents.get("path", "AGENTS.md")
    if path.is_symlink() or not path.is_file() or digest(path) != agents.get("sha256"):
        raise SystemExit("managed AGENTS.md is missing or modified")
PY
    then
        return 1
    fi
    return 0
}

show_help() {
    echo "QuinotoSpec Installer v${INSTALLER_VERSION}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Installation Options:"
    echo "  --cursor          Install for Cursor"
    echo "  --opencode        Install for OpenCode"
    echo "  --claude          Install for Claude Code"
    echo "  --cline           Install for Cline"
    echo "  --antigravity     Install for Antigravity (AGY)"
    echo "  --generic         Install for Generic (.agent/)"
    echo "  --global, --root  Install globally in ~/.config/, ~/.cursor/, ~/.claude/ or ~/.gemini/config"
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
    echo "  $0 --claude                      # Install for Claude Code"
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

    if command -v python3 &>/dev/null; then
        local python_version
        python_version=$(python3 --version 2>&1 | awk '{print $2}')
        if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 8))'; then
            print_success "Python $python_version"
        else
            print_error "Python 3.8+ required (current: $python_version)"
            has_error=1
        fi
    else
        print_error "Python 3.8+ not found"
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
    local target_root="${3:-$TARGET_ROOT}"
    local errors=0

    print_info "Verifying $ide_name installation at $config_dir..."
    echo ""

    # Check config directory exists
    if [ ! -d "$config_dir" ]; then
        print_error "Configuration directory not found: $config_dir"
        return 1
    fi
    print_success "Configuration directory exists"

    if ! verify_ownership_manifest "$config_dir" "$target_root"; then
        errors=$((errors + 1))
    fi

    # Check critical directories
    local dirs_to_check=("rules" "skills" "templates" "bootstrap" "hooks")
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

    if [ -f "$config_dir/skills/quinotospec-contract/contract.py" ]; then
        print_success "Artifact contract helper exists"
    else
        print_error "Artifact contract helper missing: skills/quinotospec-contract/contract.py"
        errors=$((errors + 1))
    fi

    if [ -f "$config_dir/bootstrap/quinotospec-bootstrap.md" ]; then
        print_success "Session bootstrap exists"
    else
        print_error "Session bootstrap missing: bootstrap/quinotospec-bootstrap.md"
        errors=$((errors + 1))
    fi

    if [ -f "$config_dir/templates/constitution-template.md" ]; then
        print_success "Constitution template exists"
    else
        print_error "Constitution template missing: templates/constitution-template.md"
        errors=$((errors + 1))
    fi

    if [ -x "$config_dir/hooks/session-start.sh" ]; then
        print_success "Session-start hook is executable"
    else
        print_error "Session-start hook missing or not executable: hooks/session-start.sh"
        errors=$((errors + 1))
    fi

    case "$ide_name" in
        opencode)
            if [ -f "$config_dir/plugins/quinotospec-plugin.js" ]; then
                print_success "OpenCode bootstrap plugin exists"
            else
                print_error "OpenCode plugin missing: plugins/quinotospec-plugin.js"
                errors=$((errors + 1))
            fi
            ;;
        cursor)
            if [ -f "$config_dir/hooks.json" ] && [ -f "$config_dir/quinotospec-plugin/.cursor-plugin/plugin.json" ]; then
                print_success "Cursor session hook and plugin manifest exist"
            else
                print_error "Cursor hook or plugin manifest missing"
                errors=$((errors + 1))
            fi
            ;;
        claude)
            if [ -f "$config_dir/settings.json" ] && [ -f "$config_dir/hooks/hooks.json" ]; then
                print_success "Claude session hook settings exist"
            else
                print_error "Claude hook settings missing"
                errors=$((errors + 1))
            fi
            ;;
    esac

    # Check AGENTS.md in target root
    local agents_md="$target_root/AGENTS.md"
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
    if [ "$workflow_count" -lt 43 ]; then
        print_error "Installed workflow count is too low: $workflow_count"
        errors=$((errors + 1))
    fi
    if [ "$skill_count" -lt 86 ]; then
        print_error "Installed skill count is too low: $skill_count"
        errors=$((errors + 1))
    fi

    if [ $errors -gt 0 ]; then
        echo ""
        print_error "Verification failed with $errors errors"
        return 1
    fi

    echo ""
    print_success "Installation verified successfully"
    return 0
}

install_runtime_components() {
    local config_dir="$1"
    local ide="$2"
    local final_config_dir="${3:-$config_dir}"
    local hook_script="$config_dir/hooks/session-start.sh"
    local final_hook_script="$final_config_dir/hooks/session-start.sh"

    mkdir -p "$config_dir/bootstrap" "$config_dir/hooks"
    cp "$DIR/agent-dist/bootstrap/quinotospec-bootstrap.md" "$config_dir/bootstrap/quinotospec-bootstrap.md"
    cp -R "$DIR/agent-dist/hooks/." "$config_dir/hooks/"
    chmod +x "$hook_script" "$config_dir/hooks/run-hook.cmd"

    case "$ide" in
        opencode)
            mkdir -p "$config_dir/plugins"
            cp "$DIR/agent-dist/plugins/opencode/quinotospec-plugin.js" "$config_dir/plugins/quinotospec-plugin.js"
            cp "$DIR/agent-dist/hooks/hooks-opencode.json" "$config_dir/hooks/hooks-opencode.json"
            ;;
        cursor)
            python3 - "$config_dir/hooks.json" "$final_hook_script" <<'PY'
import json
import shlex
import sys
from pathlib import Path

settings = Path(sys.argv[1])
if settings.is_symlink():
    raise SystemExit(f"Cursor hooks configuration must not be a symlink: {settings}")
command = f"{shlex.quote(sys.argv[2])} --platform cursor"
try:
    payload = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit(f"Cursor hooks configuration is invalid: {error}")
payload.setdefault("version", 1)
entries = payload.setdefault("hooks", {}).setdefault("sessionStart", [])
if not any(entry.get("command") == command for entry in entries if isinstance(entry, dict)):
    entries.append({"command": command})
settings.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
            mkdir -p "$config_dir/quinotospec-plugin/.cursor-plugin" "$config_dir/quinotospec-plugin/skills" "$config_dir/quinotospec-plugin/agents" "$config_dir/quinotospec-plugin/commands" "$config_dir/quinotospec-plugin/rules" "$config_dir/quinotospec-plugin/hooks"
            cp -R "$config_dir/skills/." "$config_dir/quinotospec-plugin/skills/"
            cp -R "$config_dir/agents/." "$config_dir/quinotospec-plugin/agents/"
            cp -R "$config_dir/commands/." "$config_dir/quinotospec-plugin/commands/"
            cp -R "$config_dir/rules/." "$config_dir/quinotospec-plugin/rules/"
            cp -R "$config_dir/hooks/." "$config_dir/quinotospec-plugin/hooks/"
            cp "$DIR/.cursor-plugin/plugin.json" "$config_dir/quinotospec-plugin/.cursor-plugin/plugin.json"
            python3 - "$config_dir/quinotospec-plugin/hooks/hooks-cursor.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
for entries in payload.get("hooks", {}).values():
    for entry in entries:
        if isinstance(entry, dict) and "command" in entry:
            entry["command"] = "./hooks/session-start.sh --platform cursor"
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
            python3 - "$config_dir/quinotospec-plugin/.cursor-plugin/plugin.json" "$DIR/manifest.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
payload = {
    "name": "quinotospec",
    "version": manifest.get("version", "3.2.0"),
    "description": "QuinotoSpec methodology and agent configuration",
    "author": {"name": "QuinotoTech"},
    "agents": "agents",
    "skills": "skills",
    "commands": "commands",
    "rules": "rules",
    "hooks": "hooks/hooks-cursor.json",
}
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
            ;;
        claude)
            cp "$DIR/agent-dist/hooks/hooks.json" "$config_dir/hooks/hooks.json"
            python3 - "$config_dir/settings.json" "$final_hook_script" <<'PY'
import json
import shlex
import sys
from pathlib import Path

settings = Path(sys.argv[1])
if settings.is_symlink():
    raise SystemExit(f"Claude settings must not be a symlink: {settings}")
command = f"{shlex.quote(sys.argv[2])} --platform claude"
try:
    payload = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit(f"Claude settings are invalid: {error}")
entries = payload.setdefault("hooks", {}).setdefault("SessionStart", [])
for entry in entries:
    for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
        if isinstance(hook, dict) and hook.get("command") == command:
            break
    else:
        continue
    break
else:
    entries.append({"hooks": [{"type": "command", "command": command}]})
settings.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
            ;;
        *)
            cp "$DIR/agent-dist/hooks/hooks.json" "$config_dir/hooks/hooks.json"
            ;;
    esac
}

get_config_dir() {
    local ide="$1"
    local global="$2"

    case "$ide" in
        cursor)
            [ "$global" = true ] && echo "$HOME/.cursor" || echo "$TARGET_ROOT/.cursor"
            ;;
        opencode)
            [ "$global" = true ] && echo "$HOME/.config/opencode" || echo "$TARGET_ROOT/.opencode"
            ;;
        claude)
            [ "$global" = true ] && echo "$HOME/.claude" || echo "$TARGET_ROOT/.claude"
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

    if [ ! -f "$config_dir/.quinoto-spec/ownership.json" ]; then
        print_error "Refusing to remove $config_dir: ownership manifest not found"
        echo "  Resolve the installation manually or reinstall with the transactional installer."
        exit 1
    fi

    if [ "$ASSUME_YES" != "true" ]; then
        echo ""
        echo -n "Are you sure you want to remove managed QuinotoSpec files from $config_dir? [y/N]: "
        read -r confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            print_info "Uninstall cancelled"
            exit 0
        fi
    fi

    if ! python3 - "$config_dir" "$TARGET_ROOT" <<'PY'
import hashlib
import json
import sys
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def safe_relative(value):
    if not isinstance(value, str):
        raise ValueError("unsafe manifest path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe manifest path")
    return path


config = Path(sys.argv[1]).resolve()
target_root = Path(sys.argv[2]).resolve()
manifest_path = config / ".quinoto-spec/ownership.json"
try:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    raise SystemExit("ownership manifest is invalid: " + str(error))
if not isinstance(data, dict) or data.get("schema_version") != 1:
    raise SystemExit("ownership manifest schema is unsupported")
conflicts = []
removals = []
for item in data.get("owned", []):
    if not isinstance(item, dict):
        raise SystemExit("ownership manifest contains an invalid entry")
    try:
        relative = safe_relative(item.get("path", ""))
    except ValueError as error:
        raise SystemExit(str(error))
    if relative.as_posix() == ".quinoto-spec/ownership.json":
        continue
    path = config / relative
    if path.is_symlink():
        conflicts.append("managed symlink: " + relative.as_posix())
    elif path.is_file():
        if digest(path) != item.get("sha256"):
            conflicts.append("managed file was modified: " + relative.as_posix())
        else:
            removals.append(path)
    elif path.exists():
        conflicts.append("managed path is not a regular file: " + relative.as_posix())
agents = data.get("agents")
agents_path = None
if isinstance(agents, dict) and agents.get("managed"):
    try:
        relative_agents = safe_relative(agents.get("path", "AGENTS.md"))
    except ValueError as error:
        raise SystemExit(str(error))
    agents_path = target_root / relative_agents
    if agents_path.is_symlink():
        conflicts.append("managed AGENTS.md is a symlink")
    elif agents_path.is_file() and digest(agents_path) != agents.get("sha256"):
        conflicts.append("managed AGENTS.md was modified")
    elif agents_path.exists() and not agents_path.is_file():
        conflicts.append("managed AGENTS.md is not a regular file")
if conflicts:
    raise SystemExit("uninstall refused; resolve conflicts: " + "; ".join(conflicts))
pending_json = []
hook_commands = set(item for item in data.get("hook_commands", []) if isinstance(item, str))
if hook_commands and data.get("ide") == "cursor":
    hooks_path = config / "hooks.json"
    if hooks_path.is_symlink():
        raise SystemExit("Cursor hooks configuration is a symlink")
    if hooks_path.is_file():
        try:
            payload = json.loads(hooks_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit("Cursor hooks configuration is invalid: " + str(error))
        entries = payload.get("hooks", {}).get("sessionStart", [])
        payload["hooks"]["sessionStart"] = [entry for entry in entries if not (isinstance(entry, dict) and entry.get("command") in hook_commands)]
        pending_json.append((hooks_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n"))
if hook_commands and data.get("ide") == "claude":
    settings_path = config / "settings.json"
    if settings_path.is_symlink():
        raise SystemExit("Claude settings is a symlink")
    if settings_path.is_file():
        try:
            payload = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit("Claude settings are invalid: " + str(error))
        for key, entries in payload.get("hooks", {}).items():
            if not isinstance(entries, list):
                continue
            filtered = []
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("hooks"), list):
                    entry = dict(entry)
                    entry["hooks"] = [hook for hook in entry["hooks"] if not (isinstance(hook, dict) and hook.get("command") in hook_commands)]
                filtered.append(entry)
            payload["hooks"][key] = filtered
        pending_json.append((settings_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n"))
for path in removals:
    path.unlink()
for path, content in pending_json:
    path.write_text(content, encoding="utf-8")
if agents_path is not None and agents_path.is_file():
    agents_path.unlink()
try:
    manifest_path.unlink()
except FileNotFoundError:
    pass
for directory in sorted((path for path in config.rglob("*") if path.is_dir()), key=lambda path: len(path.parts), reverse=True):
    try:
        directory.rmdir()
    except OSError:
        pass
try:
    config.rmdir()
except OSError:
    pass
PY
    then
        print_error "Uninstall aborted without deleting managed files"
        exit 1
    fi
    print_success "Removed managed QuinotoSpec files from $config_dir"
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
        --claude) IDE_CHOICE="claude" ;;
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
        print_error "--uninstall requires an IDE flag (--opencode, --cursor, --claude, --cline, --antigravity)"
        exit 1
    fi
    uninstall "$IDE_CHOICE"
fi

# Check dependencies
check_dependencies

# Handle verify-only mode
if [ "$VERIFY_ONLY" = true ]; then
    if [ -z "$IDE_CHOICE" ]; then
        print_error "--verify requires an IDE flag (--opencode, --cursor, --claude, --cline, --antigravity)"
        exit 1
    fi
    config_dir=$(get_config_dir "$IDE_CHOICE" "$GLOBAL_INSTALL")
    verify_target_root="$PROJECT_ROOT"
    if [ "$GLOBAL_INSTALL" = true ]; then
        case "$IDE_CHOICE" in
            cursor) verify_target_root="$HOME" ;;
            claude) verify_target_root="$HOME/.claude" ;;
            antigravity) verify_target_root="$HOME/.gemini" ;;
            *) verify_target_root="$HOME/.config" ;;
        esac
    fi
    if verify_installation "$config_dir" "$IDE_CHOICE" "$verify_target_root"; then
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
    elif [ "$IDE_CHOICE" = "cursor" ]; then
        TARGET_ROOT="$HOME"
        print_info "Installing globally to ~/.cursor/"
    elif [ "$IDE_CHOICE" = "claude" ]; then
        TARGET_ROOT="$HOME/.claude"
        print_info "Installing globally to ~/.claude/"
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
    echo "  3) Claude Code"
    echo "  4) Cline"
    echo "  5) Antigravity"
    echo "  6) Generic (.agent/)"
    echo ""
    echo -n "Enter your choice [1-6] (default: 1): "
    read -r choice

    case "$choice" in
        1|"") IDE_CHOICE="opencode" ;;
        2) IDE_CHOICE="cursor" ;;
        3) IDE_CHOICE="claude" ;;
        4) IDE_CHOICE="cline" ;;
        5) IDE_CHOICE="antigravity" ;;
        6) IDE_CHOICE="generic" ;;
        *) IDE_CHOICE="opencode" ;;
    esac
fi

SOURCE_AGENT="$DIR/agent-dist"
FINAL_CONFIG_DIR=$(get_config_dir "$IDE_CHOICE" "$GLOBAL_INSTALL")
if [ "$TARGET_ROOT/AGENTS.md" != "$DIR/AGENTS.md" ] && ! check_agents_conflict; then
    exit 1
fi
if ! begin_transaction "$FINAL_CONFIG_DIR"; then
    exit 1
fi
config_dir="$TRANSACTION_DIR/candidate"
if ! prepare_candidate; then
    print_error "Installation aborted because existing managed files were modified"
    exit 1
fi
if ! reject_candidate_symlinks; then
    print_error "Installation aborted because staged configuration contains a symlink"
    exit 1
fi

case "$IDE_CHOICE" in
    cursor|opencode|claude|cline|antigravity)
        echo "Installing for $(titlecase "$IDE_CHOICE")..."
        cp -rf "$SOURCE_AGENT/." "$config_dir/"

        if [ "$IDE_CHOICE" = "cursor" ] || [ "$IDE_CHOICE" = "opencode" ] || [ "$IDE_CHOICE" = "claude" ]; then
            if [ -d "$config_dir/workflows" ]; then
                if [ -d "$config_dir/commands" ]; then
                    cp -R "$config_dir/workflows/." "$config_dir/commands/"
                    rm -rf "$config_dir/workflows"
                else
                    mv "$config_dir/workflows" "$config_dir/commands"
                fi
            fi
        fi

        install_runtime_components "$config_dir" "$IDE_CHOICE" "$FINAL_CONFIG_DIR"
        ;;

    *)
        echo "Installing for Generic (.agent/)..."
        cp -rf "$SOURCE_AGENT/." "$config_dir/"
        install_runtime_components "$config_dir" "generic" "$FINAL_CONFIG_DIR"
        ;;
esac

STAGED_AGENTS="$TRANSACTION_DIR/candidate-root/AGENTS.md"
INSTALL_CONFIG="$TARGET_ROOT/.quinoto-spec/config.yaml"
if [ -f "$INSTALL_CONFIG" ]; then
    CONFIG_SOURCE="$INSTALL_CONFIG"
else
    CONFIG_SOURCE="$DIR/agent-dist/templates/config-template.yml"
fi
if ! python3 -B "$DIR/agent-dist/skills/quinotospec-update-agents/update_agents.py" \
    --root "$TARGET_ROOT" \
    --inventory-root "$DIR" \
    --state-root "$TARGET_ROOT" \
    --config "$CONFIG_SOURCE" \
    --template "$DIR/agent-dist/templates/AGENTS-template.md" \
    --output "$STAGED_AGENTS" \
    --allow-external-output \
    --write; then
    print_error "Could not generate AGENTS.md from project configuration"
    exit 1
fi
if [ "$TARGET_ROOT/AGENTS.md" != "$DIR/AGENTS.md" ]; then
    AGENTS_MANAGED=true
else
    AGENTS_MANAGED=false
fi
if ! write_ownership_manifest "$config_dir" "$IDE_CHOICE" "$TARGET_ROOT" "$FINAL_CONFIG_DIR" "$AGENTS_MANAGED"; then
    print_error "Could not write the ownership manifest"
    exit 1
fi
if ! verify_installation "$config_dir" "$IDE_CHOICE" "$TRANSACTION_DIR/candidate-root"; then
    print_error "Staged installation verification failed; target was not changed"
    exit 1
fi

if [ -e "$FINAL_CONFIG_DIR" ]; then
    if ! mv "$FINAL_CONFIG_DIR" "$TRANSACTION_DIR/previous-live"; then
        print_error "Could not move the previous installation into transaction storage"
        exit 1
    fi
fi
if ! mv "$TRANSACTION_DIR/candidate" "$FINAL_CONFIG_DIR"; then
    print_error "Could not commit the staged installation"
    exit 1
fi
if [ "${QUINOTOSPEC_INSTALL_TEST_MODE:-false}" = "true" ] && [ "${QUINOTOSPEC_INSTALL_FAIL_STAGE:-}" = "after-config" ]; then
    print_error "Injected transaction failure after configuration commit"
    exit 1
fi
if [ "$AGENTS_MANAGED" = true ]; then
    if [ -e "$TARGET_ROOT/AGENTS.md" ]; then
        if ! mv "$TARGET_ROOT/AGENTS.md" "$TRANSACTION_DIR/previous-agents"; then
            print_error "Could not preserve the previous AGENTS.md"
            exit 1
        fi
    fi
    if ! mv "$STAGED_AGENTS" "$TARGET_ROOT/AGENTS.md"; then
        print_error "Could not commit AGENTS.md"
        exit 1
    fi
fi
config_dir="$FINAL_CONFIG_DIR"

echo ""
echo "======================================================================"
print_success "Installation complete for $(titlecase "$IDE_CHOICE")!"
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
        cursor)      echo "Installed to ~/.cursor/" ;;
        opencode)    echo "Installed to ~/.config/opencode/" ;;
        claude)      echo "Installed to ~/.claude/" ;;
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

if [ "$VERIFY_RESULT" -eq 0 ]; then
    TRANSACTION_COMMITTED=true
fi
exit $VERIFY_RESULT
