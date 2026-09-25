#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "agent-dist/skills/quinotospec-backup/backup.py"


class BackupTests(unittest.TestCase):
    def make_project(self, root):
        qspec = root / ".quinoto-spec"
        (qspec / "discovery").mkdir(parents=True)
        (qspec / "proposals/demo").mkdir(parents=True)
        (qspec / "backups").mkdir(parents=True)
        (qspec / "discovery/01-stack-profile.md").write_text("Stack: Python\n", encoding="utf-8")
        (qspec / "discovery/08-product-and-agreements.md").write_text("DoR and DoD are explicit.\n", encoding="utf-8")
        (qspec / "proposals/demo/proposal.md").write_text("Proposal stable\n", encoding="utf-8")
        (qspec / ".env").write_text("TOKEN=do-not-backup\n", encoding="utf-8")
        (qspec / "backups/old.txt").write_text("recursive\n", encoding="utf-8")
        return root

    def run_engine(self, root, store, command, *args):
        invocation = [sys.executable, "-B", str(SCRIPT), command, "--root", str(root), "--store", str(store), "--json"]
        invocation.extend(args)
        completed = subprocess.run(invocation, capture_output=True, text=True, check=False)
        self.assertIn(completed.returncode, (0, 1, 2), completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def test_create_verify_list_and_secret_exclusion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            store = Path(directory) / "store"
            code, created = self.run_engine(root, store, "create", "--type", "full")
            self.assertEqual(code, 0)
            backup_id = created["backup"]["backup_id"]
            self.assertEqual(created["backup"]["algorithm"], "sha256")
            self.assertNotIn(".env", [item["path"] for item in created["backup"]["files"]])
            self.assertNotIn("backups/old.txt", [item["path"] for item in created["backup"]["files"]])
            code, verified = self.run_engine(root, store, "verify", "--backup", backup_id)
            self.assertEqual(code, 0)
            self.assertTrue(verified["valid"])
            code, listed = self.run_engine(root, store, "list")
            self.assertEqual(code, 0)
            self.assertEqual(listed["count"], 1)

    def test_tampered_payload_fails_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            store = Path(directory) / "store"
            _, created = self.run_engine(root, store, "create", "--type", "full")
            backup = Path(created["path"])
            payload = backup / "payload/discovery/01-stack-profile.md"
            payload.write_text("tampered", encoding="utf-8")
            code, result = self.run_engine(root, store, "verify", "--backup", created["backup"]["backup_id"])
            self.assertEqual(code, 1)
            self.assertEqual(result["error_type"], "verification")

    def test_restore_requires_confirmation_and_preserves_safety_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            store = Path(directory) / "store"
            _, created = self.run_engine(root, store, "create", "--type", "full")
            target = root / ".quinoto-spec/discovery/01-stack-profile.md"
            target.write_text("changed after backup\n", encoding="utf-8")
            code, refused = self.run_engine(root, store, "restore", "--backup", created["backup"]["backup_id"])
            self.assertEqual(code, 2)
            self.assertIn("--yes", refused["error"])
            self.assertIn("changed after backup", target.read_text(encoding="utf-8"))
            code, restored = self.run_engine(root, store, "restore", "--backup", created["backup"]["backup_id"], "--yes")
            self.assertEqual(code, 0)
            self.assertTrue(restored["restored"])
            self.assertIn("Stack: Python", target.read_text(encoding="utf-8"))
            self.assertTrue(Path(restored["safety_backup"]).is_dir())

    def test_incremental_records_changes_and_deletions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            store = Path(directory) / "store"
            old = root / ".quinoto-spec/proposals/demo/old.md"
            old.write_text("old\n", encoding="utf-8")
            _, full = self.run_engine(root, store, "create", "--type", "full")
            old.unlink()
            changed = root / ".quinoto-spec/proposals/demo/proposal.md"
            changed.write_text("changed\n", encoding="utf-8")
            new_file = root / ".quinoto-spec/proposals/demo/new.md"
            new_file.write_text("new\n", encoding="utf-8")
            code, incremental = self.run_engine(root, store, "create", "--type", "incremental")
            self.assertEqual(code, 0)
            self.assertEqual(incremental["backup"]["base_backup"], full["backup"]["backup_id"])
            paths = {item["path"] for item in incremental["backup"]["files"]}
            self.assertIn("proposals/demo/proposal.md", paths)
            self.assertIn("proposals/demo/new.md", paths)
            self.assertIn("proposals/demo/old.md", set(incremental["backup"]["deleted"]))

    def test_store_inside_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            store = root / ".quinoto-spec/backups"
            code, result = self.run_engine(root, store, "create", "--type", "full")
            self.assertEqual(code, 2)
            self.assertIn("outside", result["error"])

    def test_source_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            outside = Path(directory) / "outside.txt"
            outside.write_text("secret", encoding="utf-8")
            link = root / ".quinoto-spec/discovery/link.md"
            link.symlink_to(outside)
            code, result = self.run_engine(root, Path(directory) / "store", "create", "--type", "full")
            self.assertEqual(code, 2)
            self.assertIn("symlink", result["error"])

    def test_cleanup_is_dry_run_first(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_project(Path(directory))
            store = Path(directory) / "store"
            ids = []
            for _ in range(3):
                _, result = self.run_engine(root, store, "create", "--type", "full")
                ids.append(result["backup"]["backup_id"])
            code, preview = self.run_engine(root, store, "cleanup", "--keep", "1", "--dry-run")
            self.assertEqual(code, 0)
            self.assertEqual(len(preview["removed"]), 2)
            self.assertTrue(all(Path(item).is_dir() for item in preview["removed"]))
            code, removed = self.run_engine(root, store, "cleanup", "--keep", "1", "--yes")
            self.assertEqual(code, 0)
            self.assertEqual(len(removed["removed"]), 2)
            _, listed = self.run_engine(root, store, "list")
            self.assertEqual(listed["count"], 1)


if __name__ == "__main__":
    unittest.main()
