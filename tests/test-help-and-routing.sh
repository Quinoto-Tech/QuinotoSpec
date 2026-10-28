#!/bin/bash

# Test: Help contextual (F3.5), Complexity Router (F4.2) y Agent Config 3-layer (F3.1)
# Sin `set -e`: cada check captura su propio resultado para reportar todos los fallos.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HELP="$PROJECT_ROOT/agent-dist/skills/quinotospec-help/help.py"
ROUTER="$PROJECT_ROOT/agent-dist/skills/quinotospec-complexity-router/router.py"
AGENT_CONFIG="$PROJECT_ROOT/agent-dist/skills/quinotospec-agent-config/agent_config.py"
DEFAULTS="$PROJECT_ROOT/agent-dist/config/agent-defaults.toml"

ERRORS=0
TESTED=0

WORKDIR="$(mktemp -d "$SCRIPT_DIR/temp_help_routing.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT INT TERM

echo ""
echo "=========================================="
echo "Test: Help, Complexity Router y Agent Config"
echo "=========================================="
echo ""

check() {
    local desc="$1"
    local rc="$2"
    TESTED=$((TESTED + 1))
    if [ "$rc" -eq 0 ]; then
        echo "  ✅ $desc"
    else
        echo "  ❌ $desc"
        ERRORS=$((ERRORS + 1))
    fi
}

for artifact in "$HELP" "$ROUTER" "$AGENT_CONFIG" "$DEFAULTS" \
    "$PROJECT_ROOT/agent-dist/skills/quinotospec-help/SKILL.md" \
    "$PROJECT_ROOT/agent-dist/skills/quinotospec-complexity-router/SKILL.md" \
    "$PROJECT_ROOT/agent-dist/skills/quinotospec-agent-config/SKILL.md" \
    "$PROJECT_ROOT/agent-dist/workflows/quinotospec.help.md" \
    "$PROJECT_ROOT/agent-dist/workflows/quinotospec.quick-dev.md" \
    "$PROJECT_ROOT/agent-dist/workflows/quinotospec.agent-config.md" \
    "$PROJECT_ROOT/agent-dist/workflows/quinotospec.review-handoff.md" \
    "$PROJECT_ROOT/agent-dist/skills/quinotospec-review-handoff/SKILL.md"; do
    [ -f "$artifact" ]
    check "existe $(basename "$(dirname "$artifact")")/$(basename "$artifact")" "$?"
done

# ==========================================================================
# Help contextual
# ==========================================================================
echo "--- Help contextual ---"

HELP_JSON=$(python3 -B "$HELP" --root "$PROJECT_ROOT" --json 2>&1)
RC=0
echo "$HELP_JSON" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["schema_version"] == 1
assert "initialized" in data and "discovery" in data and "proposals" in data
assert isinstance(data["recommendations"], list) and data["recommendations"]
assert data["next_command"]
' || RC=$?
check "help.py --json devuelve estado y recomendaciones" "$RC"

EMPTY_PROJECT="$WORKDIR/empty-project"
mkdir -p "$EMPTY_PROJECT"
HELP_EMPTY=$(python3 -B "$HELP" --root "$EMPTY_PROJECT" --json 2>&1)
RC=0
echo "$HELP_EMPTY" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["initialized"] is False
assert data["next_command"] == "/quinotospec.init"
' || RC=$?
check "help.py recomienda init en un proyecto vacio" "$RC"

STALE_PROJECT="$WORKDIR/stale-project"
mkdir -p "$STALE_PROJECT/.quinoto-spec/discovery"
printf '# stack\n' > "$STALE_PROJECT/.quinoto-spec/discovery/01-stack-profile.md"
touch -d "90 days ago" "$STALE_PROJECT/.quinoto-spec/discovery/01-stack-profile.md"
HELP_STALE=$(python3 -B "$HELP" --root "$STALE_PROJECT" --json 2>&1)
RC=0
echo "$HELP_STALE" | python3 -c '
import json, sys
data = json.load(sys.stdin)
commands = [item["command"] for item in data["recommendations"]]
assert data["discovery"]["stale"] is True
assert "/quinotospec.refresh-discovery" in commands
' || RC=$?
check "help.py detecta discovery obsoleto (>30 dias)" "$RC"

TASK_PROJECT="$WORKDIR/task-project"
mkdir -p "$TASK_PROJECT/.quinoto-spec/discovery" "$TASK_PROJECT/.quinoto-spec/proposals/demo-abcd"
printf '# stack\n' > "$TASK_PROJECT/.quinoto-spec/discovery/01-stack-profile.md"
printf '# Proposal\n' > "$TASK_PROJECT/.quinoto-spec/proposals/demo-abcd/proposal.md"
printf '# User stories\n' > "$TASK_PROJECT/.quinoto-spec/proposals/demo-abcd/user-stories.md"
printf -- '- [x] TSK-DEMO-abcd-001 completada\n- [ ] TSK-DEMO-abcd-002 pendiente\n' \
    > "$TASK_PROJECT/.quinoto-spec/proposals/demo-abcd/US-DEMO-abcd-001_tasks.md"
HELP_TASK=$(python3 -B "$HELP" --root "$TASK_PROJECT" --json 2>&1)
RC=0
echo "$HELP_TASK" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["next_command"] == "/quinotospec.apply TSK-DEMO-abcd-002"
assert data["proposals"]["items"][0]["tasks"]["pending"] == 1
assert data["proposals"]["items"][0]["tasks"]["completed"] == 1
' || RC=$?
check "help.py recomienda la tarea pendiente concreta" "$RC"

DONE_PROJECT="$WORKDIR/done-project"
mkdir -p "$DONE_PROJECT/.quinoto-spec/discovery" "$DONE_PROJECT/.quinoto-spec/proposals/demo-abcd"
printf '# stack\n' > "$DONE_PROJECT/.quinoto-spec/discovery/01-stack-profile.md"
printf '# Proposal\n' > "$DONE_PROJECT/.quinoto-spec/proposals/demo-abcd/proposal.md"
printf '# User stories\n' > "$DONE_PROJECT/.quinoto-spec/proposals/demo-abcd/user-stories.md"
printf -- '- [x] TSK-DEMO-abcd-001 completada\n- [x] TSK-DEMO-abcd-002 completada\n' \
    > "$DONE_PROJECT/.quinoto-spec/proposals/demo-abcd/US-DEMO-abcd-001_tasks.md"
HELP_DONE=$(python3 -B "$HELP" --root "$DONE_PROJECT" --json 2>&1)
RC=0
echo "$HELP_DONE" | python3 -c '
import json, sys
data = json.load(sys.stdin)
commands = [item["command"] for item in data["recommendations"]]
assert "/quinotospec.review-handoff demo-abcd" in commands, commands
assert "/quinotospec.archive demo-abcd" in commands, commands
assert commands.index("/quinotospec.review-handoff demo-abcd") < commands.index("/quinotospec.archive demo-abcd"), commands
' || RC=$?
check "help.py recomienda review-handoff antes de archive con todo completado" "$RC"

# ==========================================================================
# Complexity Router
# ==========================================================================
echo "--- Complexity Router ---"

router_track() {
    python3 -B "$ROUTER" "$@" --json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["track"])'
}

for case in \
    "--files 1|quick_fix" \
    "--files 2|simple" \
    "--files 8|complex" \
    "--files 30|enterprise"; do
    args="${case%%|*}"
    expected="${case##*|}"
    # shellcheck disable=SC2086
    actual=$(router_track $args)
    [ "$actual" = "$expected" ]
    check "router $args -> $expected" "$?"
done

[ "$(router_track --files 1 --auth)" = "complex" ]
check "router escala a complex ante --auth" "$?"

[ "$(router_track --files 1 --db)" = "complex" ]
check "router escala a complex ante --db" "$?"

[ "$(router_track --files 1 --public-api)" = "complex" ]
check "router escala a complex ante --public-api" "$?"

[ "$(router_track --files 2 --regulated)" = "enterprise" ]
check "router escala a enterprise ante --regulated" "$?"

[ "$(router_track --files 1 --services 3)" = "enterprise" ]
check "router escala a enterprise con >2 servicios" "$?"

[ "$(router_track --files 1 --override enterprise)" = "enterprise" ]
check "router respeta --override enterprise" "$?"

ROUTER_JSON=$(python3 -B "$ROUTER" --files 2 --services 1 --json 2>&1)
RC=0
echo "$ROUTER_JSON" | python3 -c '
import json, sys
data = json.load(sys.stdin)
assert data["schema_version"] == 1
assert data["recommended_workflow"] == "/quinotospec.quick-dev"
assert data["needs_proposal"] is False
assert data["rationale"]
' || RC=$?
check "router --json expone workflow y rationale" "$RC"

# ==========================================================================
# Agent Config 3-layer
# ==========================================================================
echo "--- Agent Config 3-layer ---"

LIST_JSON=$(python3 -B "$AGENT_CONFIG" --root "$PROJECT_ROOT" --list --json 2>&1)
RC=0
echo "$LIST_JSON" | python3 -c '
import json, sys
data = json.load(sys.stdin)
agents = {item["agent"]: item for item in data["agents"]}
assert len(agents) == 9
assert agents["architect"]["display_name"] == "Alba"
assert agents["code-reviewer"]["display_name"] == "Lucas"
assert data["layers"][0]["layer"] == "defaults"
' || RC=$?
check "agent_config.py --list expone los 9 agentes con nombres" "$RC"

ARCH_JSON=$(python3 -B "$AGENT_CONFIG" --root "$PROJECT_ROOT" --agent architect --json 2>&1)
RC=0
echo "$ARCH_JSON" | python3 -c '
import json, sys
data = json.load(sys.stdin)
config = data["config"]
assert config["display_name"] == "Alba"
assert config["communication_style"]["language"] == "espanol"
assert config["principles"]
' || RC=$?
check "agent_config.py resuelve la configuracion efectiva de un agente" "$RC"

LAYER_PROJECT="$WORKDIR/agent-layers"
mkdir -p "$LAYER_PROJECT/agent-dist/config" "$LAYER_PROJECT/.quinoto-spec"
cp "$DEFAULTS" "$LAYER_PROJECT/agent-dist/config/agent-defaults.toml"
printf '[agents.architect]\nprinciples = ["Regla de equipo"]\n\n[agents.architect.communication_style]\nverbosity = "bajo"\n' \
    > "$LAYER_PROJECT/.quinoto-spec/agent-team.toml"
printf '[agents.architect]\ndisplay_name = "Alba Local"\n' \
    > "$LAYER_PROJECT/.quinoto-spec/agent-personal.toml"
LAYER_JSON=$(python3 -B "$AGENT_CONFIG" --root "$LAYER_PROJECT" --agent architect --json 2>&1)
RC=0
echo "$LAYER_JSON" | python3 -c '
import json, sys
data = json.load(sys.stdin)
config = data["config"]
assert config["display_name"] == "Alba Local", config["display_name"]
assert config["principles"] == ["Regla de equipo"]
assert config["communication_style"]["verbosity"] == "bajo"
assert config["communication_style"]["language"] == "espanol"
assert [layer["layer"] for layer in data["layers"]] == ["defaults", "team", "personal"]
' || RC=$?
check "agent_config.py aplica merge defaults -> team -> personal" "$RC"

printf '[agents.architect\nbroken = "toml"\n' > "$LAYER_PROJECT/.quinoto-spec/agent-personal.toml"
python3 -B "$AGENT_CONFIG" --root "$LAYER_PROJECT" --agent architect >/dev/null 2>&1
RC=$?
if [ "$RC" -ne 0 ]; then RC=0; else RC=1; fi
check "agent_config.py falla con TOML invalido en vez de aplicar config parcial" "$RC"

echo ""
echo "=========================================="
echo "Resultados: $TESTED checks, $ERRORS errores"
echo "=========================================="

if [ "$ERRORS" -gt 0 ]; then
    exit 1
fi

echo "✅ Help, Complexity Router y Agent Config funcionan correctamente"
exit 0
