#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "agent-dist/skills/quinotospec-rules-enforce/approval_validate.py"
DISPATCHER = ROOT / "agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py"
APPROVAL_ID = "APR-BASE-a1b2-001"
SUBJECT = ".quinoto-spec/sprints/base-config.yml"


def timestamp(offset=0):
    return (datetime.now(timezone.utc) - timedelta(seconds=offset)).isoformat()


class ApprovalTests(unittest.TestCase):
    def record(self, decision="approved", subject=SUBJECT, action="apply", offset=0):
        return {
            "schema_version": 1,
            "approval_id": APPROVAL_ID,
            "decision": decision,
            "subject": subject,
            "action": action,
            "requested_by": "developer",
            "decided_by": "owner",
            "decided_at": timestamp(offset),
            "rationale": "The change was reviewed and explicitly approved for this scope.",
            "scope": "single configuration change",
        }

    def write_approval(self, root, data):
        path = root / ".quinoto-spec/approvals" / (APPROVAL_ID + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def run_validator(self, root, subject=SUBJECT, action="apply", require=True, max_age=2592000, approval_id=APPROVAL_ID):
        command = [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "validate",
            "--root",
            str(root),
            "--approval-id",
            approval_id,
            "--subject",
            subject,
            "--action",
            action,
            "--max-age",
            str(max_age),
            "--json",
        ]
        if require:
            command.append("--require")
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return completed.returncode, json.loads(completed.stdout)

    def run_gate(self, root, *args):
        command = [sys.executable, "-B", str(DISPATCHER), "--root", str(root), "--json"]
        command.extend(args)
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return completed.returncode, json.loads(completed.stdout)

    def test_valid_approval_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_approval(root, self.record())
            code, result = self.run_validator(root)
            self.assertEqual(code, 0)
            self.assertTrue(result["valid"])
            self.assertTrue(result["approved"])
            self.assertEqual(result["decision"], "approved")

    def test_rejected_and_deferred_decisions_do_not_pass_required_gate(self):
        for decision in ("rejected", "deferred"):
            with self.subTest(decision=decision):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    self.write_approval(root, self.record(decision=decision))
                    code, result = self.run_validator(root)
                    self.assertEqual(code, 1)
                    self.assertTrue(result["valid"])
                    self.assertFalse(result["approved"])
                    self.assertIn(decision, result["error"])

    def test_stale_or_out_of_scope_approval_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_approval(root, self.record(offset=3000000))
            code, result = self.run_validator(root)
            self.assertEqual(code, 1)
            self.assertIn("stale", result["error"])
            self.write_approval(root, self.record(subject="src/other.py"))
            code, result = self.run_validator(root)
            self.assertEqual(code, 1)
            self.assertIn("subject", result["error"])
            self.write_approval(root, self.record(action="archive"))
            code, result = self.run_validator(root, action="apply")
            self.assertEqual(code, 1)
            self.assertIn("action", result["error"])

    def test_missing_or_malformed_record_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, result = self.run_validator(root)
            self.assertEqual(code, 1)
            self.assertFalse(result["valid"])
            path = self.write_approval(root, self.record())
            path.write_text("not json", encoding="utf-8")
            code, result = self.run_validator(root)
            self.assertEqual(code, 1)
            self.assertIn("JSON", result["error"])

    def test_dispatcher_requires_and_scopes_human_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / SUBJECT
            config.parent.mkdir(parents=True)
            config.write_text("enabled: true\n", encoding="utf-8")
            self.write_approval(root, self.record())
            arguments = (
                "--profile", "target",
                "--action", "apply",
                "--check", "critical-config,human-approval",
                "--path", str(config),
                "--require-approval",
                "--approval-id", APPROVAL_ID,
                "--approval-subject", "./" + SUBJECT,
            )
            code, result = self.run_gate(root, *arguments)
            self.assertEqual(code, 0, result)
            self.assertTrue(result["passed"])
            statuses = {item["id"]: item["status"] for item in result["checks"]}
            self.assertEqual(statuses["human-approval"], "pass")
            self.assertEqual(statuses["critical-config"], "pass")
            missing = list(arguments)
            missing[missing.index(APPROVAL_ID)] = "APR-BASE-a1b2-002"
            code, result = self.run_gate(root, *missing)
            self.assertEqual(code, 1)
            self.assertIn("approval.invalid", {item["code"] for item in result["violations"]})

    def test_approval_is_deferred_without_explicit_requirement_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            approval = self.write_approval(root, self.record())
            before = approval.read_bytes()
            code, result = self.run_gate(
                root,
                "--profile", "target",
                "--action", "apply",
                "--check", "human-approval",
                "--approval-id", APPROVAL_ID,
            )
            self.assertEqual(code, 0)
            self.assertEqual(result["checks"][0]["status"], "deferred")
            self.assertEqual(approval.read_bytes(), before)

    def test_package_preflight_keeps_human_approval_deferred(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".quinoto-spec").mkdir()
            code, result = self.run_gate(root, "--profile", "package", "--check", "human-approval")
            self.assertEqual(code, 0)
            self.assertIn("human-approval", {item["id"] for item in result["deferred"]})
    def test_manifest_registers_human_approval_gate(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["rules"], 18)
        self.assertTrue(manifest["features"]["human_approval_gate"])
        self.assertEqual(manifest["capability_maturity"]["human_approval_gate"], "beta")


if __name__ == "__main__":
    unittest.main()
