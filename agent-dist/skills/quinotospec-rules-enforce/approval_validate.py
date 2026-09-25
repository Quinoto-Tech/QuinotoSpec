#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

sys.dont_write_bytecode = True

SCHEMA_VERSION = 1
DECISIONS = ("approved", "rejected", "deferred")
APPROVAL_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Za-z0-9]+)+$")


class ApprovalError(Exception):
    pass


def parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ApprovalError("decided_at must be an ISO-8601 timestamp")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ApprovalError("decided_at is not a valid ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ApprovalError("decided_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ApprovalError(field + " must be a non-empty string")
    return value.strip()


def normalize_subject(value: Any, field: str = "subject") -> str:
    subject = nonempty(value, field)
    if "\\" in subject or "\x00" in subject:
        raise ApprovalError(field + " must be a relative POSIX path")
    candidate = Path(subject)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ApprovalError(field + " must stay within the project root")
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        raise ApprovalError(field + " must identify a concrete target")
    return normalized


def validate_approval(
    path: Path,
    approval_id: str,
    subject: str,
    action: str,
    max_age: int,
) -> Dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ApprovalError("approval file not found: " + str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ApprovalError("approval JSON is invalid: " + str(error))
    if not isinstance(data, dict):
        raise ApprovalError("approval must be a JSON object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ApprovalError("unsupported approval schema_version")
    if data.get("approval_id") != approval_id:
        raise ApprovalError("approval_id does not match the requested approval")
    record_subject = normalize_subject(data.get("subject"))
    if record_subject != normalize_subject(subject, "requested_subject"):
        raise ApprovalError("approval subject does not match the requested subject")
    record_action = nonempty(data.get("action"), "action")
    if record_action != action:
        raise ApprovalError("approval action does not match the requested action")
    decision = data.get("decision")
    if decision not in DECISIONS:
        raise ApprovalError("decision must be approved, rejected, or deferred")
    nonempty(data.get("requested_by"), "requested_by")
    nonempty(data.get("decided_by"), "decided_by")
    rationale = nonempty(data.get("rationale"), "rationale")
    if len(rationale) < 10:
        raise ApprovalError("rationale must contain at least 10 characters")
    nonempty(data.get("scope"), "scope")
    decided = parse_timestamp(data.get("decided_at"))
    age = (datetime.now(timezone.utc) - decided).total_seconds()
    if age > max_age:
        raise ApprovalError("approval is stale: age exceeds " + str(max_age) + " seconds")
    if age < -300:
        raise ApprovalError("approval timestamp is in the future")
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "approved": decision == "approved",
        "approval_id": approval_id,
        "decision": decision,
        "subject": record_subject,
        "action": record_action,
        "path": str(path),
        "decided_at": data["decided_at"],
        "age_seconds": max(0, int(age)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QuinotoSpec read-only human approval validator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--root", default=".")
    validate.add_argument("--approval-dir", default=".quinoto-spec/approvals")
    validate.add_argument("--approval-id", required=True)
    validate.add_argument("--subject", required=True)
    validate.add_argument("--action", required=True)
    validate.add_argument("--max-age", type=int, default=2592000)
    validate.add_argument("--require", action="store_true")
    validate.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.max_age < 1:
        print(json.dumps({"valid": False, "error": "max-age must be positive"}, ensure_ascii=False, indent=2))
        return 2
    approval_id = args.approval_id.strip()
    if not APPROVAL_ID_PATTERN.fullmatch(approval_id):
        print(json.dumps({"valid": False, "error": "approval_id has an invalid format"}, ensure_ascii=False, indent=2))
        return 2
    try:
        subject = normalize_subject(args.subject, "requested_subject")
        action = nonempty(args.action, "requested_action")
        root = Path(args.root).resolve()
        if not root.is_dir():
            raise ApprovalError("project root is not a directory: " + str(root))
        approval_dir = Path(args.approval_dir)
        if not approval_dir.is_absolute():
            approval_dir = root / approval_dir
        approval_dir = approval_dir.resolve(strict=False)
        try:
            approval_dir.relative_to(root)
        except ValueError as error:
            raise ApprovalError("approval directory must stay within the project root") from error
        approval_path = approval_dir / (approval_id + ".json")
        result = validate_approval(approval_path, approval_id, subject, action, args.max_age)
        code = 0
        if not result["approved"]:
            result["error"] = "human decision is " + result["decision"] + ", not approved"
            code = 1 if args.require else 0
    except ApprovalError as error:
        result = {
            "schema_version": SCHEMA_VERSION,
            "valid": False,
            "approved": False,
            "approval_id": approval_id,
            "error": str(error),
        }
        code = 1 if args.require else 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
