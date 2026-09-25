#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True

SCHEMA_VERSION = 1
CONTRACT_PATH = Path(__file__).resolve().parents[1] / "quinotospec-contract" / "contract.py"
EVIDENCE_VALIDATOR_PATH = Path(__file__).resolve().parent / "evidence_validate.py"
APPROVAL_VALIDATOR_PATH = Path(__file__).resolve().parent / "approval_validate.py"
ALL_CHECKS = (
    "contract",
    "changelog",
    "prefix",
    "product-agreement",
    "branch",
    "protected-paths",
    "critical-config",
    "no-overwrite",
    "archive-state",
    "archive-convention",
    "tdd",
    "debug",
    "verify-before-done",
    "human-approval",
)
ACTIONS = {"preflight", "create-proposal", "apply", "archive", "review", "refactor", "constitution", "mjolnir-refactor"}
BRANCH_PATTERN = re.compile(
    r"^(?:feature|bugfix)/(?:US|TSK)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-[a-z0-9]+(?:-[a-z0-9]+)+$"
)
PLACEHOLDER_PATTERN = re.compile(
    r"(?:\{\{[^}]+\}\}|<[^>]+>|\b(?:todo|tbd|placeholder|pendiente|por definir)\b)",
    re.IGNORECASE,
)


class OperationError(Exception):
    pass


def make_check(
    rule: Optional[int],
    check_id: str,
    status: str,
    severity: str,
    message: str = "",
    path: str = "",
) -> Dict[str, Any]:
    return {
        "rule": rule,
        "id": check_id,
        "status": status,
        "severity": severity,
        "message": message,
        "path": path,
    }


def make_violation(
    check_id: str,
    severity: str,
    message: str,
    path: str = "",
    code: str = "",
) -> Dict[str, Any]:
    return {
        "id": check_id,
        "severity": severity,
        "message": message,
        "path": path,
        "code": code,
    }


def expand_checks(values: Sequence[str]) -> List[str]:
    selected: List[str] = []
    for value in values:
        for item in value.split(","):
            item = item.strip().lower()
            if not item:
                continue
            if item == "all":
                selected.extend(ALL_CHECKS)
            else:
                selected.append(item)
    unknown = [item for item in selected if item not in ALL_CHECKS]
    if unknown:
        raise OperationError("unknown checks: " + ", ".join(sorted(set(unknown))))
    result: List[str] = []
    for item in selected:
        if item not in result:
            result.append(item)
    return result or list(ALL_CHECKS)


def run_contract(root: Path) -> Dict[str, Any]:
    if not CONTRACT_PATH.is_file():
        raise OperationError("contract helper not found: " + str(CONTRACT_PATH))
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [
        sys.executable,
        "-B",
        str(CONTRACT_PATH),
        "validate",
        "--root",
        str(root),
        "--json",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise OperationError("contract helper could not be executed: " + str(error))
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise OperationError("contract helper returned invalid JSON: " + detail[:200])
    if not isinstance(report, dict) or "errors" not in report or "warnings" not in report:
        raise OperationError("contract helper returned an invalid report")
    return report


def contract_diagnostics(report: Dict[str, Any], check_id: str) -> List[Dict[str, Any]]:
    diagnostics: List[Dict[str, Any]] = []
    for item in list(report.get("errors", [])) + list(report.get("warnings", [])):
        code = str(item.get("code", ""))
        matches = (
            (check_id == "changelog" and code.startswith("changelog."))
            or (check_id == "prefix" and (code.startswith("registry.") or code.startswith("proposal.prefix.")))
            or (
                check_id == "contract"
                and not code.startswith("changelog.")
                and not code.startswith("registry.")
                and not code.startswith("proposal.prefix.")
            )
        )
        if matches:
            diagnostics.append(item)
    return diagnostics


def add_contract_checks(
    checks: List[Dict[str, Any]],
    violations: List[Dict[str, Any]],
    report: Dict[str, Any],
    selected: Sequence[str],
    mode: str,
) -> None:
    for check_id in ("contract", "changelog", "prefix"):
        if check_id not in selected:
            continue
        diagnostics = contract_diagnostics(report, check_id)
        errors = [item for item in diagnostics if item.get("severity") == "error"]
        warnings = [item for item in diagnostics if item.get("severity") == "warning"]
        if errors:
            checks.append(make_check(None, check_id, "fail", "blocking", "Contract diagnostics contain errors"))
            for item in errors:
                violations.append(
                    make_violation(
                        check_id,
                        "blocking",
                        str(item.get("message", "contract error")),
                        str(item.get("path", "")),
                        str(item.get("code", "contract.error")),
                    )
                )
        elif warnings and mode == "strict":
            checks.append(make_check(None, check_id, "fail", "warning", "Contract diagnostics contain warnings"))
            for item in warnings:
                violations.append(
                    make_violation(
                        check_id,
                        "warning",
                        str(item.get("message", "contract warning")),
                        str(item.get("path", "")),
                        str(item.get("code", "contract.warning")),
                    )
                )
        elif warnings:
            checks.append(make_check(None, check_id, "warning", "warning", "Contract diagnostics contain warnings"))
        else:
            checks.append(make_check(None, check_id, "pass", "blocking"))


def meaningful_content(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    meaningful = 0
    in_frontmatter = False
    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if index == 0 and line == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if not line or line in {"#", "##", "###", "---", "___"} or line.startswith("#"):
            continue
        if re.fullmatch(r"\|?\s*:?-{3,}:?\s*\|?", line):
            continue
        content = re.sub(r"^[-*+]\s+", "", line)
        if PLACEHOLDER_PATTERN.search(content):
            continue
        if content.lower() in {"n/a", "na", "-", "—", "pendiente", "sin definir"}:
            continue
        meaningful += 1
    return meaningful >= 1


def add_product_agreement(
    checks: List[Dict[str, Any]],
    violations: List[Dict[str, Any]],
    root: Path,
    profile: str,
    action: str,
) -> None:
    check_id = "product-agreement"
    if profile != "target" or action != "create-proposal":
        checks.append(make_check(3, check_id, "not_applicable", "blocking"))
        return
    relative = ".quinoto-spec/discovery/08-product-and-agreements.md"
    path = root / relative
    if meaningful_content(path):
        checks.append(make_check(3, check_id, "pass", "blocking"))
        return
    checks.append(make_check(3, check_id, "fail", "blocking", "Product agreements are missing or placeholders only", relative))
    violations.append(
        make_violation(
            check_id,
            "blocking",
            "No puedo validar la propuesta porque DoR/DoD no están definidos en 08-product-and-agreements.md",
            relative,
            "product_agreement.missing",
        )
    )


def add_branch_check(
    checks: List[Dict[str, Any]],
    violations: List[Dict[str, Any]],
    branch: Optional[str],
    action: str,
) -> None:
    check_id = "branch"
    required = action in {"apply", "review"}
    if not branch and not required:
        checks.append(make_check(7, check_id, "not_applicable", "blocking"))
        return
    if not branch:
        checks.append(make_check(7, check_id, "fail", "blocking", "A branch is required for this action"))
        violations.append(make_violation(check_id, "blocking", "A branch is required for apply/review", code="branch.missing"))
        return
    if BRANCH_PATTERN.fullmatch(branch):
        checks.append(make_check(7, check_id, "pass", "blocking"))
        return
    checks.append(make_check(7, check_id, "fail", "blocking", "Branch does not follow the task branch convention"))
    violations.append(
        make_violation(
            check_id,
            "blocking",
            "Branch must start with feature/ or bugfix/ and include a canonical task ID plus kebab-case description",
            code="branch.invalid",
        )
    )


def resolve_paths(root: Path, raw_paths: Sequence[str]) -> List[Tuple[str, Path, Optional[str]]]:
    resolved: List[Tuple[str, Path, Optional[str]]] = []
    for raw in raw_paths:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            relative = candidate.resolve(strict=False).relative_to(root.resolve()).as_posix()
        except ValueError:
            resolved.append((raw, candidate, None))
            continue
        resolved.append((raw, candidate, relative))
    return resolved


def add_path_checks(
    checks: List[Dict[str, Any]],
    violations: List[Dict[str, Any]],
    root: Path,
    raw_paths: Sequence[str],
    selected: Sequence[str],
    approved_critical: bool,
    approved_subject: Optional[str],
    write_mode: str,
) -> None:
    selected_paths = resolve_paths(root, raw_paths)
    if "protected-paths" in selected:
        if not selected_paths:
            checks.append(make_check(12, "protected-paths", "not_applicable", "blocking"))
        else:
            protected_violations: List[Dict[str, Any]] = []
            for raw, candidate, relative in selected_paths:
                if relative is None:
                    protected_violations.append(
                        make_violation("protected-paths", "blocking", "Path escapes the project root", raw, "path.outside_root")
                    )
                    continue
                if candidate.is_symlink() or candidate.exists() and candidate.is_symlink():
                    protected_violations.append(
                        make_violation("protected-paths", "blocking", "Symbolic-link paths are not accepted by the gate", relative, "path.symlink")
                    )
                if "_archived" in candidate.resolve(strict=False).parts:
                    protected_violations.append(
                        make_violation("protected-paths", "blocking", "Writes inside _archived/ require an explicit recovery workflow", relative, "path.archived")
                    )
            if protected_violations:
                checks.append(make_check(12, "protected-paths", "fail", "blocking", "A guarded path violates protection rules"))
                violations.extend(protected_violations)
            else:
                checks.append(make_check(12, "protected-paths", "pass", "blocking"))

    if "critical-config" in selected:
        if not selected_paths:
            checks.append(make_check(8, "critical-config", "not_applicable", "blocking"))
        else:
            critical_violations: List[Dict[str, Any]] = []
            critical_paths: List[str] = []
            for _, _, relative in selected_paths:
                if relative is None:
                    continue
                path = Path(relative)
                is_critical = (
                    path.as_posix() == ".quinoto-spec/sprints/base-config.yml"
                    or (len(path.parts) >= 3 and path.parts[:2] == (".quinoto-spec", "sprints") and path.name == "sprint-config.yml")
                    or re.fullmatch(r"\.quinoto-spec/[^/]+/mjolnir-refactor\.yml", relative) is not None
                )
                if is_critical:
                    critical_paths.append(relative)
                    if not approved_critical and approved_subject != relative:
                        critical_violations.append(
                            make_violation("critical-config", "blocking", "Critical configuration requires explicit approval", relative, "config.critical")
                        )
            if critical_paths and (approved_critical or approved_subject in critical_paths):
                checks.append(make_check(8, "critical-config", "pass", "blocking", "Critical configuration explicitly approved"))
            elif critical_violations:
                checks.append(make_check(8, "critical-config", "fail", "blocking", "Critical configuration requires approval"))
                violations.extend(critical_violations)
            else:
                checks.append(make_check(8, "critical-config", "pass", "blocking"))

    if "no-overwrite" in selected:
        if not selected_paths:
            checks.append(make_check(4, "no-overwrite", "not_applicable", "blocking"))
        else:
            overwrite_violations: List[Dict[str, Any]] = []
            for _, candidate, relative in selected_paths:
                if relative is None:
                    continue
                name = candidate.name
                if (name == "user-stories.md" or name.endswith("_tasks.md")) and candidate.exists() and write_mode != "merge":
                    overwrite_violations.append(
                        make_violation(
                            "no-overwrite",
                            "blocking",
                            "Existing specification files require write-mode=merge",
                            relative,
                            "spec.overwrite",
                        )
                    )
            if overwrite_violations:
                checks.append(make_check(4, "no-overwrite", "fail", "blocking", "An existing specification file would be overwritten"))
                violations.extend(overwrite_violations)
            else:
                checks.append(make_check(4, "no-overwrite", "pass", "blocking"))


def run_evidence_validator(
    root: Path,
    evidence_dir: str,
    kind: str,
    task_id: Optional[str],
) -> Tuple[bool, str]:
    if not EVIDENCE_VALIDATOR_PATH.is_file():
        return False, "evidence validator not found"
    if not task_id:
        return False, "task_id is required for evidence validation"
    command = [
        sys.executable,
        "-B",
        str(EVIDENCE_VALIDATOR_PATH),
        "validate",
        "--root",
        str(root),
        "--evidence-dir",
        evidence_dir,
        "--kind",
        kind,
        "--task-id",
        task_id,
        "--require",
        "--json",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True,
            text=True,
            check=False,
        )
        result = json.loads(completed.stdout)
    except (OSError, json.JSONDecodeError) as error:
        return False, "evidence validator could not be read: " + str(error)
    if completed.returncode == 0 and result.get("valid") is True:
        return True, ""
    return False, str(result.get("error", "evidence validation failed"))


def run_approval_validator(
    root: Path,
    approval_dir: str,
    approval_id: Optional[str],
    subject: str,
    action: str,
    max_age: int,
) -> Tuple[bool, str]:
    if not APPROVAL_VALIDATOR_PATH.is_file():
        return False, "approval validator not found"
    if not approval_id:
        return False, "approval_id is required for human approval validation"
    command = [
        sys.executable,
        "-B",
        str(APPROVAL_VALIDATOR_PATH),
        "validate",
        "--root",
        str(root),
        "--approval-dir",
        approval_dir,
        "--approval-id",
        approval_id,
        "--subject",
        subject,
        "--action",
        action,
        "--max-age",
        str(max_age),
        "--require",
        "--json",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True,
            text=True,
            check=False,
        )
        result = json.loads(completed.stdout)
    except (OSError, json.JSONDecodeError) as error:
        return False, "approval validator could not be read: " + str(error)
    if completed.returncode == 0 and result.get("valid") is True and result.get("approved") is True:
        return True, ""
    return False, str(result.get("error", "human decision is not approved"))


def add_human_approval_check(
    checks: List[Dict[str, Any]],
    violations: List[Dict[str, Any]],
    deferred: List[Dict[str, Any]],
    selected: Sequence[str],
    root: Path,
    profile: str,
    action: str,
    raw_paths: Sequence[str],
    approval_dir: str,
    approval_id: Optional[str],
    approval_subject: Optional[str],
    approval_action: Optional[str],
    require_approval: bool,
    max_age: int,
) -> Optional[str]:
    check_id = "human-approval"
    if check_id not in selected:
        return None
    reason = "Human decisions require a fresh, scoped approval record"
    if profile != "target":
        if require_approval:
            checks.append(make_check(18, check_id, "not_applicable", "advisory"))
        else:
            checks.append(make_check(18, check_id, "deferred", "advisory", reason))
            deferred.append({"id": check_id, "rule": 18, "reason": reason})
        return None
    if not require_approval:
        checks.append(make_check(18, check_id, "deferred", "advisory", reason))
        deferred.append({"id": check_id, "rule": 18, "reason": reason})
        return None
    expected_action = approval_action or action
    expected_subject = approval_subject
    resolved_paths = resolve_paths(root, raw_paths)
    if not expected_subject and len(resolved_paths) == 1:
        _, _, relative = resolved_paths[0]
        expected_subject = relative
    if not approval_id:
        message = "approval_id is required when human approval is enforced"
        checks.append(make_check(18, check_id, "fail", "blocking", message))
        violations.append(make_violation(check_id, "blocking", message, code="approval.id_missing"))
        return None
    if not expected_subject:
        message = "approval subject is required; pass --approval-subject or exactly one --path"
        checks.append(make_check(18, check_id, "fail", "blocking", message))
        violations.append(make_violation(check_id, "blocking", message, code="approval.subject_missing"))
        return None
    expected_subject = Path(expected_subject).as_posix()
    expected_action = expected_action.strip()
    valid, message = run_approval_validator(root, approval_dir, approval_id, expected_subject, expected_action, max_age)
    if valid:
        checks.append(make_check(18, check_id, "pass", "blocking", "Human approval validated"))
        return expected_subject
    checks.append(make_check(18, check_id, "fail", "blocking", message))
    violations.append(make_violation(check_id, "blocking", message, code="approval.invalid"))
    return None


def add_evidence_checks(
    checks: List[Dict[str, Any]],
    violations: List[Dict[str, Any]],
    deferred: List[Dict[str, Any]],
    selected: Sequence[str],
    root: Path,
    profile: str,
    action: str,
    evidence_dir: str,
    task_id: Optional[str],
    require_evidence: bool,
) -> None:
    definitions = {
        "tdd": (14, "TDD evidence requires a fresh structured record"),
        "debug": (15, "Debug evidence requires reproduction, hypothesis, root cause and regression"),
        "verify-before-done": (16, "Verify evidence requires fresh tests, quality commands and DoD checks"),
    }
    applicable_actions = {"apply", "review", "refactor"}
    for kind, (rule, reason) in definitions.items():
        if kind not in selected:
            continue
        if profile != "target" or action not in applicable_actions:
            if not require_evidence:
                checks.append(make_check(rule, kind, "deferred", "advisory", reason))
                deferred.append({"id": kind, "rule": rule, "reason": reason})
            else:
                checks.append(make_check(rule, kind, "not_applicable", "advisory"))
            continue
        if not require_evidence:
            checks.append(make_check(rule, kind, "deferred", "advisory", reason))
            deferred.append({"id": kind, "rule": rule, "reason": reason})
            continue
        valid, message = run_evidence_validator(root, evidence_dir, kind, task_id)
        if valid:
            checks.append(make_check(rule, kind, "pass", "blocking", "Evidence validated"))
        else:
            checks.append(make_check(rule, kind, "fail", "blocking", message))
            violations.append(make_violation(kind, "blocking", message, code="evidence.invalid"))


def add_deferred(checks: List[Dict[str, Any]], deferred: List[Dict[str, Any]], selected: Sequence[str]) -> None:
    deferred_specs = {
        "archive-state": (5, "Archive completion state requires artifact identity and workflow context"),
        "archive-convention": (6, "Archive movement semantics are not inferred from a path-only check"),
    }
    for check_id, (rule, reason) in deferred_specs.items():
        if check_id in selected:
            checks.append(make_check(rule, check_id, "deferred", "advisory", reason))
            deferred.append({"id": check_id, "rule": rule, "reason": reason})
    for rule, check_id, reason in (
        (10, "backup-pre-refactor", "Backup pre-refactor requires explicit backup.py verification and user confirmation"),
        (17, "constitution", "Constitutional compliance requires human-approved evidence"),
    ):
        if "contract" in selected and check_id in {"backup-pre-refactor", "constitution"}:
            checks.append(make_check(rule, check_id, "deferred", "advisory", reason))
            deferred.append({"id": check_id, "rule": rule, "reason": reason})


def enforce(
    root: Path,
    profile: str,
    action: str,
    mode: str,
    selected: Sequence[str],
    raw_paths: Sequence[str],
    branch: Optional[str],
    approved_critical: bool,
    write_mode: str,
    evidence_dir: str,
    task_id: Optional[str],
    require_evidence: bool,
    approval_dir: str,
    approval_id: Optional[str],
    approval_subject: Optional[str],
    approval_action: Optional[str],
    require_approval: bool,
    approval_max_age: int,
) -> Dict[str, Any]:
    if profile not in {"package", "target"}:
        raise OperationError("profile must be package or target")
    if action not in ACTIONS:
        raise OperationError("unsupported action: " + action)
    if mode not in {"strict", "warning"}:
        raise OperationError("mode must be strict or warning")
    if write_mode not in {"write", "merge", "create"}:
        raise OperationError("write-mode must be write, merge, or create")
    root = root.resolve()
    if not root.is_dir():
        raise OperationError("project root is not a directory: " + str(root))
    checks: List[Dict[str, Any]] = []
    violations: List[Dict[str, Any]] = []
    deferred: List[Dict[str, Any]] = []
    if "contract" in selected or "changelog" in selected or "prefix" in selected:
        report = run_contract(root)
        add_contract_checks(checks, violations, report, selected, mode)
    if "product-agreement" in selected:
        add_product_agreement(checks, violations, root, profile, action)
    if "branch" in selected:
        add_branch_check(checks, violations, branch, action)
    approved_subject = add_human_approval_check(
        checks,
        violations,
        deferred,
        selected,
        root,
        profile,
        action,
        raw_paths,
        approval_dir,
        approval_id,
        approval_subject,
        approval_action,
        require_approval,
        approval_max_age,
    )
    if "protected-paths" in selected or "critical-config" in selected or "no-overwrite" in selected:
        add_path_checks(checks, violations, root, raw_paths, selected, approved_critical, approved_subject, write_mode)
    add_evidence_checks(
        checks,
        violations,
        deferred,
        selected,
        root,
        profile,
        action,
        evidence_dir,
        task_id,
        require_evidence,
    )
    add_deferred(checks, deferred, selected)
    blocking = any(item["severity"] == "blocking" for item in violations)
    passed = not violations
    return {
        "schema_version": SCHEMA_VERSION,
        "passed": passed,
        "blocking": blocking,
        "mode": mode,
        "profile": profile,
        "action": action,
        "checks": checks,
        "violations": violations,
        "deferred": deferred,
    }


def print_human(result: Dict[str, Any]) -> None:
    print("QuinotoSpec Rules Enforce")
    print("Profile: {} | Action: {} | Mode: {}".format(result["profile"], result["action"], result["mode"]))
    for check in result["checks"]:
        print("  [{}] {} {}".format(check["status"].upper(), check["id"], check["message"]))
    for item in result["deferred"]:
        print("  [DEFERRED] {}: {}".format(item["id"], item["reason"]))
    print("Passed: {} | Blocking: {}".format(result["passed"], result["blocking"]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only QuinotoSpec governance gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--profile", default="package", choices=("package", "target"))
    parser.add_argument("--action", default="preflight", choices=tuple(sorted(ACTIONS)))
    parser.add_argument("--mode", default="strict", choices=("strict", "warning"))
    parser.add_argument("--check", action="append", default=None)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--branch")
    parser.add_argument("--approved-critical", action="store_true")
    parser.add_argument("--write-mode", default="write", choices=("write", "merge", "create"))
    parser.add_argument("--evidence-dir", default=".quinoto-spec/evidence")
    parser.add_argument("--task-id")
    parser.add_argument("--require-evidence", action="store_true")
    parser.add_argument("--approval-dir", default=".quinoto-spec/approvals")
    parser.add_argument("--approval-id")
    parser.add_argument("--approval-subject")
    parser.add_argument("--approval-action")
    parser.add_argument("--require-approval", action="store_true")
    parser.add_argument("--approval-max-age", type=int, default=2592000)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        selected = expand_checks(args.check or ["all"])
        result = enforce(
            Path(args.root),
            args.profile,
            args.action,
            args.mode,
            selected,
            args.path,
            args.branch,
            args.approved_critical,
            args.write_mode,
            args.evidence_dir,
            args.task_id,
            args.require_evidence,
            args.approval_dir,
            args.approval_id,
            args.approval_subject,
            args.approval_action,
            args.require_approval,
            args.approval_max_age,
        )
    except OperationError as error:
        result = {
            "schema_version": SCHEMA_VERSION,
            "passed": False,
            "blocking": True,
            "mode": args.mode,
            "profile": args.profile,
            "action": args.action,
            "checks": [],
            "violations": [make_violation("operation", "blocking", str(error), code="operation.error")],
            "deferred": [],
        }
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("QuinotoSpec Rules Enforce error: " + str(error), file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result)
    return 1 if result["violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
