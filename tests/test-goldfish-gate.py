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


def make_docs(root, offset=60):
    """Write proposal + tasks docs with an mtime older than the review."""
    proposals = root / ".quinoto-spec/proposals/demo"
    proposals.mkdir(parents=True, exist_ok=True)
    proposal = proposals / "proposal.md"
    tasks = proposals / "US-ABC-a1b2-001_tasks.md"
    proposal.write_text("# Proposal\n\nAlta de usuario.\n", encoding="utf-8")
    tasks.write_text("# Tasks\n\n- [ ] TSK-ABC-a1b2-001 alta\n", encoding="utf-8")
    stamp = (datetime.now(timezone.utc) - timedelta(seconds=offset)).timestamp()
    for path in (proposal, tasks):
        import os

        os.utime(path, (stamp, stamp))
    return {
        "proposal": ".quinoto-spec/proposals/demo/proposal.md",
        "tasks": ".quinoto-spec/proposals/demo/US-ABC-a1b2-001_tasks.md",
    }


class GoldfishGateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.docs = make_docs(self.root)

    def tearDown(self):
        self.directory.cleanup()

    def goldfish_data(self, offset=0, **overrides):
        data = {
            "schema_version": 1,
            "kind": "goldfish",
            "task_id": TASK_ID,
            "recorded_at": timestamp(offset),
            "fresh_context": True,
            "lenses": ["comprehension"],
            "inputs": [self.docs["proposal"], self.docs["tasks"]],
            "comprehension": {
                "explained_scope": True,
                "summary": "Alta de usuario con validacion de email; sin update ni delete.",
            },
            "verdict": "pass",
            "findings": [],
        }
        data.update(overrides)
        return data

    def write_evidence(self, data, kind="goldfish"):
        path = self.root / ".quinoto-spec/evidence" / TASK_ID / (kind + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def run_validator(self, max_age=86400):
        command = [
            sys.executable,
            "-B",
            str(VALIDATOR),
            "validate",
            "--root",
            str(self.root),
            "--kind",
            "goldfish",
            "--task-id",
            TASK_ID,
            "--max-age",
            str(max_age),
            "--require",
            "--json",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return completed.returncode, json.loads(completed.stdout)

    def assert_rejected(self, data, fragment, max_age=86400):
        self.write_evidence(data)
        code, result = self.run_validator(max_age=max_age)
        self.assertEqual(code, 1, result)
        self.assertFalse(result["valid"])
        self.assertIn(fragment, result["error"])

    def test_valid_goldfish_evidence_passes(self):
        self.write_evidence(self.goldfish_data())
        code, result = self.run_validator()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["valid"])
        self.assertEqual(result["kind"], "goldfish")
        self.assertEqual(result["task_id"], TASK_ID)

    def test_missing_evidence_fails_the_gate(self):
        code, result = self.run_validator()
        self.assertEqual(code, 1)
        self.assertFalse(result["valid"])
        self.assertIn("not found", result["error"])

    def test_reused_context_fails_the_gate(self):
        self.assert_rejected(self.goldfish_data(fresh_context=False), "fresh_context")

    def test_goldfish_that_cannot_explain_scope_fails(self):
        data = self.goldfish_data(
            comprehension={"explained_scope": False, "summary": "No pude determinar el alcance."}
        )
        self.assert_rejected(data, "explained_scope")

    def test_open_blocking_findings_fail_the_gate(self):
        data = self.goldfish_data(
            findings=[{"severity": "blocking", "status": "open", "detail": "Falta criterio de aceptacion"}]
        )
        self.assert_rejected(data, "blocking and unresolved")

    def test_non_pass_verdict_fails_the_gate(self):
        self.assert_rejected(self.goldfish_data(verdict="changes_required"), "verdict must be pass")

    def test_lenses_without_comprehension_fail_the_gate(self):
        self.assert_rejected(self.goldfish_data(lenses=["critic"]), "must include comprehension")

    def test_missing_input_document_fails_the_gate(self):
        data = self.goldfish_data(
            inputs=[self.docs["proposal"], ".quinoto-spec/proposals/demo/missing_tasks.md"]
        )
        self.assert_rejected(data, "does not reference a readable file")

    def test_input_changed_after_review_fails_the_gate(self):
        # Review recorded one hour ago, document touched now: the review is stale.
        self.write_evidence(self.goldfish_data(offset=3600))
        touched = self.root / self.docs["tasks"]
        touched.write_text("# Tasks\n\n- [ ] alcance cambiado\n", encoding="utf-8")
        code, result = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("changed after the goldfish review", result["error"])

    def test_stale_evidence_fails_the_gate(self):
        self.assert_rejected(self.goldfish_data(offset=90000), "stale")

    def test_manifest_declares_the_gate(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["features"]["goldfish_gate"])
        self.assertEqual(manifest["capability_maturity"]["goldfish_gate"], "beta")

    def test_dispatcher_blocks_without_evidence(self):
        command = [
            sys.executable,
            "-B",
            str(DISPATCHER),
            "--root",
            str(self.root),
            "--profile",
            "target",
            "--action",
            "apply",
            "--check",
            "goldfish",
            "--task-id",
            TASK_ID,
            "--require-evidence",
            "--json",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["blocking"])
        self.assertEqual(result["violations"][0]["code"], "evidence.invalid")

    def test_dispatcher_passes_with_valid_evidence(self):
        self.write_evidence(self.goldfish_data())
        command = [
            sys.executable,
            "-B",
            str(DISPATCHER),
            "--root",
            str(self.root),
            "--profile",
            "target",
            "--action",
            "apply",
            "--check",
            "goldfish",
            "--task-id",
            TASK_ID,
            "--require-evidence",
            "--json",
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual([item["id"] for item in result["checks"]], ["goldfish"])
        self.assertEqual(result["checks"][0]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
