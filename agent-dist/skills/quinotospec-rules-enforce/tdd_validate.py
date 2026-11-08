#!/usr/bin/env python3
"""TDD gate — valida que exista evidencia RED-GREEN (vector archivo, no ejecucion).

Uso:
    python3 tdd_validate.py validate --task-id TSK-X --root . --json
    python3 tdd_validate.py validate --task-id TSK-X --root . --require --json
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
try:
    from quinotospec_common import resolve_root as _resolve_root  # type: ignore

    def resolve_root(p):
        return _resolve_root(["--root", str(p)])[0]
except Exception:  # pragma: no cover
    def resolve_root(p):
        return Path(p).resolve()

try:
    from evidence_validate import validate_evidence  # type: ignore
except Exception:
    validate_evidence = None


def main(argv=None):
    parser = argparse.ArgumentParser(description="QuinotoSpec TDD gate (validator)")
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(Path(args.root))
    evidence_path = root / ".quinoto-spec" / "evidence" / args.task_id / "tdd.json"
    if validate_evidence is not None:
        try:
            result = validate_evidence(evidence_path, "tdd", args.task_id, 86400 * 7)
            result["gate"] = "tdd"
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("TDD gate: OK" if result.get("valid") else "TDD gate: FAIL")
            return 0 if (result.get("valid") or not args.require) else 1
        except Exception as error:  # noqa: BLE001
            result = {"schema_version": 1, "valid": False, "gate": "tdd", "task_id": args.task_id, "error": str(error)}
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("TDD gate: FAIL — %s" % error)
            return 1 if args.require else 0

    present = evidence_path.is_file()
    result = {"schema_version": 1, "valid": present, "gate": "tdd", "task_id": args.task_id, "path": str(evidence_path)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("TDD gate: OK" if present else "TDD gate: MISSING (solo presencia)")
    return 0 if present or not args.require else 1


if __name__ == "__main__":
    sys.exit(main())
