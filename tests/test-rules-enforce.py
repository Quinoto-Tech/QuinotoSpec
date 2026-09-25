#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py"


class RulesEnforceTests(unittest.TestCase):
    def run_gate(self, root, *args):
        command = [sys.executable, "-B", str(SCRIPT), "--root", str(root), "--json"]
        command.extend(args)
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertIn(completed.returncode, (0, 1, 2), completed.stderr)
        payload = json.loads(completed.stdout)
        return completed.returncode, payload

    def make_target(self, root, agreement="# Product Agreements\n\nThe release contract is explicit.\nThe user flow has a measurable outcome.\n"):
        path = root / ".quinoto-spec/discovery/08-product-and-agreements.md"
        path.parent.mkdir(parents=True)
        path.write_text(agreement, encoding="utf-8")
        return path

    def test_product_agreement_passes_and_is_filterable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_target(root)
            code, result = self.run_gate(root, "--profile", "target", "--action", "create-proposal", "--check", "product-agreement")
            self.assertEqual(code, 0)
            self.assertTrue(result["passed"])
            self.assertEqual([item["id"] for item in result["checks"]], ["product-agreement"])

    def test_product_agreement_missing_is_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, result = self.run_gate(root, "--profile", "target", "--action", "create-proposal", "--check", "product-agreement")
            self.assertEqual(code, 1)
            self.assertTrue(result["blocking"])
            self.assertEqual(result["violations"][0]["code"], "product_agreement.missing")

    def test_product_agreement_placeholders_are_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_target(root, "# Product Agreements\n\n{{VISION}}\nTBD\n")
            code, result = self.run_gate(root, "--profile", "target", "--action", "create-proposal", "--check", "product-agreement")
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "product_agreement.missing")

    def test_branch_validation_and_requirement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, result = self.run_gate(root, "--action", "apply", "--check", "branch")
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "branch.missing")
            code, result = self.run_gate(root, "--action", "apply", "--branch", "feature/US-ABC-001-add-login", "--check", "branch")
            self.assertEqual(code, 0)
            code, result = self.run_gate(root, "--action", "review", "--branch", "main", "--check", "branch")
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "branch.invalid")

    def test_archived_and_outside_paths_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archived = root / ".quinoto-spec/proposals/demo/_archived/old.md"
            archived.parent.mkdir(parents=True)
            archived.write_text("old", encoding="utf-8")
            code, result = self.run_gate(root, "--check", "protected-paths", "--path", str(archived))
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "path.archived")
            code, result = self.run_gate(root, "--check", "protected-paths", "--path", str(Path(directory).parent / "outside.md"))
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "path.outside_root")

    def test_critical_configuration_requires_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / ".quinoto-spec/sprints/base-config.yml"
            config.parent.mkdir(parents=True)
            config.write_text("enabled: true\n", encoding="utf-8")
            code, result = self.run_gate(root, "--check", "critical-config", "--path", str(config))
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "config.critical")
            code, result = self.run_gate(root, "--check", "critical-config", "--path", str(config), "--approved-critical")
            self.assertEqual(code, 0)

    def test_existing_spec_requires_merge_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stories = root / ".quinoto-spec/proposals/demo/user-stories.md"
            stories.parent.mkdir(parents=True)
            stories.write_text("existing", encoding="utf-8")
            code, result = self.run_gate(root, "--check", "no-overwrite", "--path", str(stories))
            self.assertEqual(code, 1)
            self.assertEqual(result["violations"][0]["code"], "spec.overwrite")
            code, result = self.run_gate(root, "--check", "no-overwrite", "--path", str(stories), "--write-mode", "merge")
            self.assertEqual(code, 0)

    def test_contract_delegation_and_deferred_checks(self):
        code, result = self.run_gate(ROOT, "--profile", "package", "--check", "contract")
        self.assertEqual(code, 0)
        self.assertEqual(result["checks"][0]["id"], "contract")
        code, result = self.run_gate(ROOT, "--profile", "package", "--check", "all")
        self.assertEqual(code, 0)
        deferred_ids = {item["id"] for item in result["deferred"]}
        self.assertIn("tdd", deferred_ids)
        self.assertIn("verify-before-done", deferred_ids)

    def test_gate_is_read_only_and_operation_errors_are_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "value.txt"
            target.write_text("stable", encoding="utf-8")
            before = target.read_bytes()
            code, result = self.run_gate(root, "--check", "protected-paths", "--path", str(target))
            self.assertEqual(code, 0)
            self.assertEqual(target.read_bytes(), before)
            code, result = self.run_gate(root, "--check", "not-a-check")
            self.assertEqual(code, 2)
            self.assertEqual(result["violations"][0]["code"], "operation.error")


if __name__ == "__main__":
    unittest.main()
