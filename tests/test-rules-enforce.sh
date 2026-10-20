#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
python3 "$SCRIPT_DIR/test-rules-enforce.py"

# Test de contrato JSON transversal en CLIs Python (M6)
python3 - "$PROJECT_ROOT" <<'PY'
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1]).resolve()


def run_json_cli(cmd):
    proc = subprocess.run([sys.executable, "-B", *cmd], capture_output=True, text=True, check=False)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as err:
        raise AssertionError(f"Invalid JSON from {cmd}: {err}\nstdout={proc.stdout}\nstderr={proc.stderr}") from err
    if not isinstance(payload, dict):
        raise AssertionError(f"Expected JSON object from {cmd}, got {type(payload)}")
    return proc.returncode, payload


with tempfile.TemporaryDirectory() as tmp:
    tmp_root = Path(tmp)
    (tmp_root / ".quinoto-spec").mkdir(parents=True, exist_ok=True)

    # 1. contract.py validate --json
    _, contract_data = run_json_cli([
        str(root / "agent-dist/skills/quinotospec-contract/contract.py"),
        "validate",
        "--root",
        str(root),
        "--json",
    ])
    assert "valid" in contract_data and "errors" in contract_data and "contract_version" in contract_data, contract_data

    # 2. rules_enforce.py --json
    _, rules_data = run_json_cli([
        str(root / "agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py"),
        "--root",
        str(root),
        "--profile",
        "package",
        "--check",
        "contract",
        "--json",
    ])
    assert "schema_version" in rules_data and "passed" in rules_data and "violations" in rules_data, rules_data

    # 3. evidence_validate.py validate --json
    _, evidence_data = run_json_cli([
        str(root / "agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py"),
        "validate",
        "--root",
        str(tmp_root),
        "--kind",
        "tdd",
        "--task-id",
        "TSK-TEST-a1b2-001",
        "--json",
    ])
    assert "schema_version" in evidence_data and "valid" in evidence_data and ("error" in evidence_data or "errors" in evidence_data or evidence_data["valid"]), evidence_data

    # 4. approval_validate.py validate --json
    _, approval_data = run_json_cli([
        str(root / "agent-dist/skills/quinotospec-rules-enforce/approval_validate.py"),
        "validate",
        "--root",
        str(tmp_root),
        "--approval-id",
        "APR-TEST-001",
        "--subject",
        ".quinoto-spec/sprints/base-config.yml",
        "--action",
        "modify",
        "--json",
    ])
    assert "schema_version" in approval_data and "valid" in approval_data and ("error" in approval_data or "errors" in approval_data or approval_data["valid"]), approval_data

    # 5. backup.py list --json
    _, backup_data = run_json_cli([
        str(root / "agent-dist/skills/quinotospec-backup/backup.py"),
        "list",
        "--root",
        str(tmp_root),
        "--json",
    ])
    assert "backups" in backup_data and isinstance(backup_data["backups"], list), backup_data

    # 6. extension_manager.py list --json
    _, ext_data = run_json_cli([
        str(root / "agent-dist/skills/quinotospec-extension-manager/extension_manager.py"),
        "list",
        "--root",
        str(tmp_root),
        "--json",
    ])
    assert "schema_version" in ext_data and "items" in ext_data and "installed" in ext_data, ext_data

print("Cross-CLI JSON contract checks: OK")
PY
