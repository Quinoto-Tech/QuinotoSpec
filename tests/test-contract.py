#!/usr/bin/env python3
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "agent-dist/skills/quinotospec-contract/contract.py"
SPEC = importlib.util.spec_from_file_location("quinotospec_contract", MODULE_PATH)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
FIXTURES = ROOT / "tests/fixtures/quinoto-contract"


class ContractTest(unittest.TestCase):
    def test_canonical_and_legacy_ids(self):
        canonical = CONTRACT.normalize_id("US-TEST-a1b2-001")
        self.assertEqual(canonical.canonical, "US-TEST-a1b2-001")
        self.assertEqual(canonical.source_format, "canonical")
        normalized = CONTRACT.normalize_id("TSK-TEST-001", "TEST-a1b2")
        self.assertEqual(normalized.canonical, "TSK-TEST-a1b2-001")
        self.assertEqual(normalized.source_format, "normalized-legacy")

    def test_modern_artifacts_parse_with_shared_contract(self):
        proposal = CONTRACT.parse_proposal(FIXTURES / "proposal-modern.md", ROOT)
        stories = CONTRACT.parse_stories(FIXTURES / "stories-modern.md", ROOT, proposal.prefix)
        tasks = CONTRACT.parse_tasks(FIXTURES / "tasks-modern.md", ROOT, proposal.prefix)
        self.assertEqual(proposal.status, "proposed")
        self.assertEqual(len(stories), 2)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(stories[0].canonical_id, "US-TEST-a1b2-001")
        self.assertEqual(tasks[0].story_id, "US-TEST-a1b2-001")
        self.assertEqual(tasks[0].status, "pending")
        self.assertTrue(all(not item.diagnostics for item in stories))
        self.assertTrue(all(not item.diagnostics for item in tasks))

    def test_legacy_blocks_are_accepted(self):
        stories = CONTRACT.parse_stories(FIXTURES / "stories-legacy.md", ROOT)
        tasks = CONTRACT.parse_tasks(FIXTURES / "tasks-legacy.md", ROOT, "TEST-a1b2")
        self.assertEqual(stories[0].canonical_id, "US-001")
        self.assertEqual(stories[0].status, "in_progress")
        self.assertEqual(tasks[0].canonical_id, "TSK-USR-001")
        self.assertEqual(tasks[0].status, "completed")
        self.assertEqual(tasks[0].story_id, "US-001")
        self.assertTrue(stories[0].diagnostics)
        self.assertTrue(tasks[0].diagnostics)

    def test_changelog_hybrid_prefers_v2(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changelog = root / ".quinoto-spec/changelog"
            changelog.mkdir(parents=True)
            (changelog / "2026-09-24-TEST-a1b2-contract.md").write_text(
                "---\ndate: 2026-09-24\nprefix: TEST-a1b2\nslug: contract\nformat: v2\n---\n\n## [2026-09-24] - Contract\n\n### Resumen\n- v2\n\n**Tiempo Ahorrado**: ~1h (IA: 5m vs Humano: 1h)\n",
                encoding="utf-8",
            )
            (root / ".quinoto-spec/quinoto-spec-changelog.md").write_text(
                "# QuinotoSpec Changelog\n\n## [Fecha: 2026-09-24] - Contract\n\n### Resumen\n- v1\n\n**Time Saved**: ~1h\n",
                encoding="utf-8",
            )
            entries, diagnostics = CONTRACT.parse_changelog(root)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].format, "v2")
            self.assertEqual(entries[0].summary, ["v2"])
            self.assertTrue(any(item.code == "changelog.duplicate" for item in diagnostics))

    def test_proposal_to_archive_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            qspec = root / ".quinoto-spec"
            proposal_dir = qspec / "proposals/2026-09-24-contract-fixture"
            proposal_dir.mkdir(parents=True)
            shutil.copy(FIXTURES / "proposal-modern.md", proposal_dir / "proposal.md")
            shutil.copy(FIXTURES / "stories-modern.md", proposal_dir / "user-stories.md")
            shutil.copy(FIXTURES / "tasks-modern.md", proposal_dir / "US-TEST-a1b2-001_tasks.md")
            (qspec / "prefix-registry.md").write_text("| Prefijo | Nombre | Fecha |\n|---|---|---|\n| TEST-a1b2 | Fixture | 2026-09-24 |\n", encoding="utf-8")
            (qspec / "changelog").mkdir()
            (qspec / "changelog/2026-09-24-TEST-a1b2-fixture.md").write_text(
                "## [2026-09-24] - Fixture\n\n### Resumen\n- Fixture\n\n**Tiempo Ahorrado**: ~1h\n",
                encoding="utf-8",
            )
            report = CONTRACT.validate_project(root)
            self.assertTrue(report["valid"], report)
            snapshot = CONTRACT.scan_project(root)
            self.assertEqual(snapshot["stories"][0]["status"], "pending")
            shutil.copy(proposal_dir / "US-TEST-a1b2-001_tasks.md", proposal_dir / "all_tasks.md")
            report = CONTRACT.validate_project(root)
            self.assertTrue(report["valid"], report)
            self.assertEqual(report["summary"]["derived_tasks"], 2)
            tasks_path = proposal_dir / "US-TEST-a1b2-001_tasks.md"
            tasks_path.write_text(tasks_path.read_text(encoding="utf-8").replace("| [ ] |", "| [x] |"), encoding="utf-8")
            report = CONTRACT.validate_project(root)
            self.assertTrue(report["valid"], report)
            snapshot = CONTRACT.scan_project(root)
            self.assertEqual(snapshot["stories"][0]["status"], "completed")
            archived = qspec / "proposals/_archived"
            archived.mkdir()
            shutil.move(str(proposal_dir), str(archived / proposal_dir.name))
            report = CONTRACT.validate_project(root)
            self.assertTrue(report["valid"], report)
            self.assertEqual(report["summary"]["proposals"], 0)


if __name__ == "__main__":
    unittest.main()
