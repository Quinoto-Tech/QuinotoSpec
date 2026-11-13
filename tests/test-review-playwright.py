#!/usr/bin/env python3
"""Tests del orquestador de review con Playwright."""

import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "agent-dist" / "skills" / "quinotospec-review" / "playwright_review.py"


def load_review():
    sys.path.insert(0, str(REVIEW.parent))
    import playwright_review  # noqa: WPS433

    return playwright_review


def clean_env(root: Path) -> dict:
    home = root / "home"
    home.mkdir(exist_ok=True)
    return {
        "PATH": str(root / "empty-bin"),
        "QS_HOME": str(home),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    }


def make_project(root: Path) -> Path:
    proposal = root / ".quinoto-spec" / "proposals" / "demo"
    proposal.mkdir(parents=True)
    (proposal / "proposal.md").write_text(
        "# Propuesta Técnica: Demo\n\n**ID:** 2026-11-13-demo\n**Prefijo:** DEMO-1a2b\n**Fecha de Creación:** 2026-11-13\n**Estado:** 🟡 Propuesta\n",
        encoding="utf-8",
    )
    return proposal


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.review = load_review()

    def test_resolve_proposal_valid_and_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            self.assertTrue(self.review.resolve_proposal(root, "demo").is_dir())
            for slug in ("../demo", "demo/../demo", "/tmp", ".."):
                with self.assertRaises(self.review.ReviewError):
                    self.review.resolve_proposal(root, slug)

    def test_select_backend(self):
        app = {"app": {"available": True, "chromium": True}, "mcp": {"configured": False}}
        mcp = {"app": {"available": False, "chromium": False}, "mcp": {"configured": True}}
        none = {"app": {"available": False, "chromium": False}, "mcp": {"configured": False}}
        self.assertEqual(self.review.select_backend("auto", app), "app")
        self.assertEqual(self.review.select_backend("auto", mcp), "mcp")
        self.assertIsNone(self.review.select_backend("auto", none))
        self.assertIsNone(self.review.select_backend("app", mcp))
        self.assertEqual(self.review.select_backend("mcp", mcp), "mcp")

    def test_install_commands_do_not_use_sudo(self):
        commands = self.review.build_install_commands()
        self.assertEqual(commands[0][:2], ["npm", "ci"])
        self.assertEqual(commands[1][:3], ["npx", "playwright", "install"])
        self.assertFalse(any(command and command[0] == "sudo" for command in commands))

    def test_skip_path_writes_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            env = clean_env(root)
            proc = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(REVIEW),
                    "--root",
                    str(root),
                    "--proposal",
                    "demo",
                    "--no-install-prompt",
                    "--skip-contract",
                    "--json",
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            data = json.loads(proc.stdout)
            self.assertEqual(data["result"], "skipped")
            self.assertTrue((root / ".quinoto-spec/reviews/demo-playwright.json").is_file())
            self.assertTrue((root / ".quinoto-spec/reviews/demo-playwright.md").is_file())

    def test_non_tty_without_decision_returns_action_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            env = clean_env(root)
            proc = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(REVIEW),
                    "--root",
                    str(root),
                    "--proposal",
                    "demo",
                    "--yes",
                    "--skip-contract",
                    "--json",
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 3, proc.stderr + proc.stdout)
            data = json.loads(proc.stdout)
            self.assertEqual(data["result"], "action_required")
            self.assertEqual({item["id"] for item in data["options"]}, {"install-app", "install-mcp", "skip"})

    def test_install_mcp_writes_config_and_requests_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            env = clean_env(root)
            proc = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(REVIEW),
                    "--root",
                    str(root),
                    "--proposal",
                    "demo",
                    "--install-playwright-mcp",
                    "--skip-contract",
                    "--json",
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 3, proc.stderr + proc.stdout)
            data = json.loads(proc.stdout)
            self.assertEqual(data["result"], "action_required")
            self.assertTrue(data["dependency"]["mcp"]["configured"])
            config_path = Path(data["mcp"]["path"])
            if not config_path.is_absolute():
                config_path = root / config_path
            self.assertTrue(config_path.is_file(), data["mcp"])

    def test_invalid_slug_does_not_write_outside_reviews(self):
        """Un slug invalido se rechaza y NO debe escribir evidencia fuera de reviews/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            before = {path for path in (root / ".quinoto-spec").rglob("*") if path.is_file()}
            proc = subprocess.run(
                [
                    sys.executable, "-B", str(REVIEW),
                    "--root", str(root),
                    "--proposal", "../escape",
                    "--skip-contract", "--json",
                ],
                capture_output=True, text=True, env=clean_env(root), timeout=30,
            )
            self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
            data = json.loads(proc.stdout)
            self.assertEqual(data["result"], "error")
            self.assertFalse((root / ".quinoto-spec" / "escape-playwright.json").exists())
            self.assertFalse((root / ".quinoto-spec" / "escape-playwright.md").exists())
            created = [path for path in (root / ".quinoto-spec").rglob("*") if path.is_file()] 
            created = [path for path in created if path not in before]
            reviews = root / ".quinoto-spec" / "reviews"
            for path in created:
                self.assertEqual(path.parent, reviews, "escritura fuera de reviews: %s" % path)

    def test_deep_traversal_returns_json_not_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            proc = subprocess.run(
                [
                    sys.executable, "-B", str(REVIEW),
                    "--root", str(root),
                    "--proposal", "../../../../tmp/quinotospec-should-not-exist",
                    "--skip-contract", "--json",
                ],
                capture_output=True, text=True, env=clean_env(root), timeout=30,
            )
            self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
            self.assertNotIn("Traceback", proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["result"], "error")
            self.assertFalse(Path("/tmp/quinotospec-should-not-exist-playwright.json").exists())

    def test_install_playwright_app_runs_pinned_commands_without_sudo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            e2e = root / "e2e"
            e2e.mkdir()
            calls = []

            class Result:
                returncode = 0
                stdout = "ok"
                stderr = ""

            def fake_run(command, **kwargs):
                calls.append((command, kwargs.get("cwd")))
                return Result()

            with mock.patch.object(self.review.shutil, "which", side_effect=lambda name: "/usr/bin/" + name if name in ("npm", "npx") else None):
                with mock.patch.object(self.review.subprocess, "run", side_effect=fake_run):
                    result = self.review.install_playwright_app(root, str(e2e))
        self.assertTrue(result["installed"])
        self.assertFalse(result["sudo"])
        self.assertEqual([call[0][0] for call in calls], ["/usr/bin/npm", "/usr/bin/npx"])
        self.assertNotIn("sudo", [part for call in calls for part in call[0]])
        self.assertTrue(all(call[1] == str(e2e) for call in calls))

    def test_install_playwright_app_failure_is_actionable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            e2e = root / "e2e"
            e2e.mkdir()

            class Result:
                returncode = 1
                stdout = ""
                stderr = "network error"

            with mock.patch.object(self.review.shutil, "which", side_effect=lambda name: "/usr/bin/" + name):
                with mock.patch.object(self.review.subprocess, "run", return_value=Result()):
                    with self.assertRaises(self.review.ReviewError) as raised:
                        self.review.install_playwright_app(root, str(e2e))
        self.assertIn("fallo instalando Playwright", str(raised.exception))

    def _args(self, **overrides):
        base = {"e2e_dir": None, "timeout": 5}
        base.update(overrides)
        return types.SimpleNamespace(**base)

    def test_run_review_app_passes_evidence_and_stops_ui(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            stopped = []
            environment = {"app": {"available": True, "chromium": True}, "mcp": {"configured": False}}

            def fake_playwright(*_args, **_kwargs):
                return {
                    "exit_code": 0,
                    "e2e_dir": "e2e",
                    "raw": {
                        "checks": [{"id": "http-status", "status": "pass", "detail": "200"}],
                        "console_errors": [], "page_errors": [], "failed_requests": [],
                        "screenshots": ["/abs/desktop.png"], "result": "pass",
                    },
                    "raw_path": "raw.json",
                    "stdout": "", "stderr": "",
                }

            with mock.patch.object(self.review, "start_ui", return_value=(object(), "http://127.0.0.1:1234")):
                with mock.patch.object(self.review, "run_playwright", side_effect=fake_playwright):
                    with mock.patch.object(self.review, "stop_ui", side_effect=lambda proc: stopped.append(proc)):
                        data = self.review.run_review_app(root, "demo", None, environment, self._args(), "none", "none")
        self.assertEqual(data["result"], "pass")
        self.assertEqual(data["base_url"], "http://127.0.0.1:1234")
        self.assertEqual(len(data["checks"]), 1)
        self.assertEqual(len(stopped), 1, "stop_ui debe ejecutarse siempre")

    def test_run_review_app_playwright_failure_and_timeout_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_project(root)
            environment = {"app": {"available": True, "chromium": True}, "mcp": {"configured": False}}
            for error in (RuntimeError("boom"), subprocess.TimeoutExpired("npx", 1)):
                stopped = []
                with mock.patch.object(self.review, "start_ui", return_value=(object(), "http://127.0.0.1:1234")):
                    with mock.patch.object(self.review, "run_playwright", side_effect=error):
                        with mock.patch.object(self.review, "stop_ui", side_effect=lambda proc: stopped.append(proc)):
                            data = self.review.run_review_app(root, "demo", None, environment, self._args(), "none", "none")
                self.assertEqual(data["result"], "error")
                self.assertTrue(data["message"])
                self.assertEqual(len(stopped), 1)

    def test_evidence_paths_are_relative_for_versioning(self):
        """La evidencia se versiona: no debe filtrar /home/<usuario> ni rutas absolutas del repo."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reviews").mkdir()
            home_config = Path.home() / ".cache" / "quinotospec-test-config.json"
            data = {
                "screenshots": [str(root / "reviews" / "desktop.png"), "/opt/otro/lugar.png"],
                "dependency": {"mcp": {"configured": True, "detected_in": [str(home_config)]}},
                "playwright": {"e2e_dir": str(root / "agent-dist" / "e2e"), "raw": str(root / "reviews" / "raw.json")},
            }
            clean = self.review.sanitize_paths(data, root)
        self.assertIn("reviews/desktop.png", clean["screenshots"])
        self.assertNotIn(str(root), " ".join(clean["screenshots"]))
        self.assertEqual(clean["dependency"]["mcp"]["detected_in"][0][:1], "~")
        self.assertEqual(clean["playwright"]["e2e_dir"], "agent-dist/e2e")

    def test_evidence_paths_work_under_symlinked_root(self):
        """macOS resuelve /var -> /private/var: root sin resolver no debe romper la sanitizacion."""
        with tempfile.TemporaryDirectory() as tmp:
            real = Path(tmp) / "real-root"
            real.mkdir()
            link = Path(tmp) / "link-root"
            link.symlink_to(real, target_is_directory=True)
            data = {"screenshots": [str(real / "reviews" / "desktop.png")], "dependency": {"mcp": {"detected_in": []}}}
            clean = self.review.sanitize_paths(data, link)
        self.assertEqual(clean["screenshots"], ["reviews/desktop.png"])


if __name__ == "__main__":
    unittest.main()
