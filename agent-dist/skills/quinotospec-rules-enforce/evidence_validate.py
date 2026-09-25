#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

sys.dont_write_bytecode = True

SCHEMA_VERSION = 1
TASK_PATTERN = re.compile(r"^(?:US|TSK)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
KINDS = ("tdd", "debug", "verify-before-done")


class EvidenceError(Exception):
    pass


def parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise EvidenceError("recorded_at must be an ISO-8601 timestamp")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise EvidenceError("recorded_at is not a valid ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise EvidenceError("recorded_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(field + " must be a non-empty string")
    return value.strip()


def validate_run(value: Any, field: str, expected_status: str, allow_not_applicable: bool = False) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError(field + " must be an object")
    status = value.get("status")
    if allow_not_applicable and status == "not_applicable":
        nonempty(value.get("justification"), field + ".justification")
        return value
    if status != expected_status:
        raise EvidenceError(field + ".status must be " + expected_status)
    nonempty(value.get("command"), field + ".command")
    exit_code = value.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        raise EvidenceError(field + ".exit_code must be an integer")
    if expected_status == "passed" and exit_code != 0:
        raise EvidenceError(field + ".exit_code must be 0")
    if expected_status == "failed" and exit_code == 0:
        raise EvidenceError(field + ".exit_code must be non-zero")
    nonempty(value.get("output"), field + ".output")
    return value


def validate_tdd(data: Dict[str, Any]) -> None:
    validate_run(data.get("red"), "red", "failed")
    nonempty(data.get("expected_failure"), "expected_failure")
    nonempty(data.get("observed_failure"), "observed_failure")
    validate_run(data.get("green"), "green", "passed")
    validate_run(data.get("suite"), "suite", "passed")
    if "refactor" in data and data["refactor"] is not None:
        validate_run(data["refactor"], "refactor", "passed")


def validate_debug(data: Dict[str, Any]) -> None:
    validate_run(data.get("reproduction"), "reproduction", "failed")
    nonempty(data.get("hypothesis"), "hypothesis")
    validate_run(data.get("experiment"), "experiment", "observed")
    nonempty(data.get("root_cause"), "root_cause")
    validate_run(data.get("regression"), "regression", "passed")


def validate_verify(data: Dict[str, Any]) -> None:
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        raise EvidenceError("checks must be a non-empty list")
    for index, item in enumerate(checks):
        if not isinstance(item, dict):
            raise EvidenceError("checks[" + str(index) + "] must be an object")
        nonempty(item.get("criterion"), "checks[" + str(index) + "].criterion")
        validate_run(item.get("run"), "checks[" + str(index) + "].run", "passed", allow_not_applicable=True)
    validate_run(data.get("tests"), "tests", "passed")
    validate_run(data.get("lint"), "lint", "passed", allow_not_applicable=True)
    validate_run(data.get("typecheck"), "typecheck", "passed", allow_not_applicable=True)
    validate_run(data.get("diff"), "diff", "passed")


def validate_evidence(path: Path, kind: str, task_id: str, max_age: int) -> Dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise EvidenceError("evidence file not found: " + str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceError("evidence JSON is invalid: " + str(error))
    if not isinstance(data, dict):
        raise EvidenceError("evidence must be a JSON object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise EvidenceError("unsupported evidence schema_version")
    if data.get("kind") != kind:
        raise EvidenceError("evidence kind does not match requested kind")
    if data.get("task_id") != task_id:
        raise EvidenceError("evidence task_id does not match requested task_id")
    recorded = parse_timestamp(data.get("recorded_at"))
    age = (datetime.now(timezone.utc) - recorded).total_seconds()
    if age > max_age:
        raise EvidenceError("evidence is stale: age exceeds " + str(max_age) + " seconds")
    if age < -300:
        raise EvidenceError("evidence timestamp is in the future")
    if kind == "tdd":
        validate_tdd(data)
    elif kind == "debug":
        validate_debug(data)
    else:
        validate_verify(data)
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": True,
        "kind": kind,
        "task_id": task_id,
        "path": str(path),
        "recorded_at": data["recorded_at"],
        "age_seconds": max(0, int(age)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QuinotoSpec read-only evidence validator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("--root", default=".")
    validate.add_argument("--evidence-dir", default=".quinoto-spec/evidence")
    validate.add_argument("--kind", required=True, choices=KINDS)
    validate.add_argument("--task-id", required=True)
    validate.add_argument("--max-age", type=int, default=86400)
    validate.add_argument("--require", action="store_true")
    validate.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.max_age < 1:
        print(json.dumps({"valid": False, "error": "max-age must be positive"}, ensure_ascii=False, indent=2))
        return 2
    task_id = args.task_id.strip()
    if not TASK_PATTERN.fullmatch(task_id):
        if args.as_json:
            print(json.dumps({"valid": False, "error": "task_id has an invalid format"}, ensure_ascii=False, indent=2))
        else:
            print("Evidence error: task_id has an invalid format", file=sys.stderr)
        return 2
    root = Path(args.root).resolve()
    evidence_dir = Path(args.evidence_dir)
    if not evidence_dir.is_absolute():
        evidence_dir = root / evidence_dir
    evidence_path = evidence_dir / task_id / (args.kind + ".json")
    try:
        result = validate_evidence(evidence_path, args.kind, task_id, args.max_age)
        code = 0
    except EvidenceError as error:
        result = {"schema_version": SCHEMA_VERSION, "valid": False, "kind": args.kind, "task_id": task_id, "path": str(evidence_path), "error": str(error)}
        code = 1 if args.require else 2
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
