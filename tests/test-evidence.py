#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py"
DISPATCHER = ROOT / "agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py"
TASK_ID = "TSK-ABC-a1b2-001"


def timestamp(offset=0):
    return (datetime.now(timezone.utc) - timedelta(seconds=offset)).isoformat()


def run_record(command, status="passed", exit_code=0, output="observed output", justification=None):
    record = {"command": command, "status": status, "exit_code": exit_code, "output": output}
    if justification is not None:
        record["justification"] = justification
    return record


class EvidenceTests(unittest.TestCase):
    def write_evidence(self, root, kind, data):
        path = root / ".quinoto-spec/evidence" / TASK_ID / (kind + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def run_validator(self, root, kind, task_id=TASK_ID, max_age=86400):
        command = [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "validate",
            "--root",
            str(root),
            "--kind",
            kind,
            "--task-id",
            task_id,
            "--max-age",
            str(max_age),
            "--require",
            "--json",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return completed.returncode, json.loads(completed.stdout)

    def tdd_data(self, offset=0):
        return {
            "schema_version": 1,
            "kind": "tdd",
            "task_id": TASK_ID,
            "recorded_at": timestamp(offset),
            "expected_failure": "missing behavior",
            "observed_failure": "assertion failed",
            "red": run_record("pytest focused", "failed", 1, "expected assertion"),
            "green": run_record("pytest focused"),
            "suite": run_record("pytest"),
        }

    def debug_data(self, offset=0):
        return {
            "schema_version": 1,
            "kind": "debug",
            "task_id": TASK_ID,
            "recorded_at": timestamp(offset),
            "reproduction": run_record("pytest focused", "failed", 1, "reproduced"),
            "hypothesis": "If the boundary is wrong then the focused test changes.",
            "experiment": run_record("pytest focused", "observed", 0, "boundary confirmed"),
            "root_cause": "Boundary calculation discarded the final input.",
            "regression": run_record("pytest focused"),
        }

    def verify_data(self, offset=0):
        return {
            "schema_version": 1,
            "kind": "verify-before-done",
            "task_id": TASK_ID,
            "recorded_at": timestamp(offset),
            "checks": [{"criterion": "feature works", "run": run_record("pytest focused")}],
            "tests": run_record("pytest"),
            "lint": run_record("ruff check", "not_applicable", 0, "", "not configured"),
            "typecheck": run_record("mypy", "not_applicable", 0, "", "not configured"),
            "diff": run_record("git diff --check"),
        }

    def test_valid_tdd_debug_and_verify_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_evidence(root, "tdd", self.tdd_data())
            self.write_evidence(root, "debug", self.debug_data())
            self.write_evidence(root, "verify-before-done", self.verify_data())
            for kind in ("tdd", "debug", "verify-before-done"):
                code, result = self.run_validator(root, kind)
                self.assertEqual(code, 0, result)
                self.assertTrue(result["valid"])

    def test_stale_or_invalid_tdd_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_evidence(root, "tdd", self.tdd_data(offset=90000))
            code, result = self.run_validator(root, "tdd")
            self.assertEqual(code, 1)
            self.assertIn("stale", result["error"])
            data = self.tdd_data()
            data["red"]["exit_code"] = 0
            self.write_evidence(root, "tdd", data)
            code, result = self.run_validator(root, "tdd")
            self.assertEqual(code, 1)
            self.assertIn("non-zero", result["error"])

    def test_dispatcher_requires_evidence_only_when_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_evidence(root, "tdd", self.tdd_data())
            self.write_evidence(root, "verify-before-done", self.verify_data())
            command = [
                sys.executable,
                "-B",
                str(DISPATCHER),
                "--root",
                str(root),
                "--profile",
                "target",
                "--action",
                "apply",
                "--check",
                "tdd,verify-before-done",
                "--require-evidence",
                "--task-id",
                TASK_ID,
                "--json",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout)
            result = json.loads(completed.stdout)
            self.assertTrue(result["passed"])
            self.assertEqual({item["status"] for item in result["checks"]}, {"pass"})
            missing_command = list(command)
            missing_command[missing_command.index(TASK_ID)] = "TSK-ABC-a1b2-002"
            completed = subprocess.run(missing_command, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 1)
            self.assertIn(json.loads(completed.stdout)["violations"][0]["id"], {"tdd", "verify-before-done"})

    def test_package_preflight_keeps_evidence_deferred(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".quinoto-spec").mkdir()
            command = [
                sys.executable,
                "-B",
                str(DISPATCHER),
                "--root",
                str(root),
                "--profile",
                "package",
                "--action",
                "preflight",
                "--check",
                "tdd,verify-before-done",
                "--json",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout)
            deferred = {item["id"] for item in json.loads(completed.stdout)["deferred"]}
            self.assertIn("tdd", deferred)
            self.assertIn("verify-before-done", deferred)


if __name__ == "__main__":
    unittest.main()
