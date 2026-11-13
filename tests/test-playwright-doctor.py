#!/usr/bin/env python3
"""Tests del doctor de Playwright."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
DOCTOR = ROOT / "agent-dist" / "skills" / "quinotospec-review" / "playwright_doctor.py"


def load_doctor():
    sys.path.insert(0, str(DOCTOR.parent))
    import playwright_doctor  # noqa: WPS433

    return playwright_doctor


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.doctor = load_doctor()

    def test_missing_everything(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.object(self.doctor.shutil, "which", return_value=None):
                env = self.doctor.check_environment(root, home=root / "home", module_dir=root / "module")
        self.assertFalse(env["node"]["available"])
        self.assertFalse(env["app"]["available"])
        self.assertFalse(env["mcp"]["configured"])
        self.assertEqual(env["recommended"], "skip")
        self.assertEqual({item["id"] for item in env["options"]}, {"install-app", "install-mcp", "skip"})

    def test_local_app_and_chromium(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            package = root / "agent-dist/skills/quinotospec-review/e2e/node_modules/@playwright/test/package.json"
            package.parent.mkdir(parents=True)
            package.write_text(json.dumps({"version": "1.52.0"}), encoding="utf-8")
            (home / ".cache/ms-playwright/chromium-1234").mkdir(parents=True)
            with mock.patch.object(self.doctor.shutil, "which", side_effect=lambda name: "/usr/bin/node" if name == "node" else None):
                with mock.patch.object(self.doctor, "run_command", return_value=(0, "v20.11.0", "")):
                    env = self.doctor.check_environment(root, home=home, module_dir=root / "module")
        self.assertTrue(env["node"]["available"])
        self.assertTrue(env["app"]["available"])
        self.assertTrue(env["app"]["chromium"])
        self.assertEqual(env["app"]["version"], "1.52.0")
        self.assertEqual(env["recommended"], "app")

    def test_mcp_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "opencode.json"
            config.write_text(json.dumps({"mcp": {"playwright": {"command": ["npx", "-y", "@playwright/mcp@latest"]}}}), encoding="utf-8")
            with mock.patch.object(self.doctor.shutil, "which", return_value=None):
                env = self.doctor.check_environment(root, home=root / "home", module_dir=root / "module")
        self.assertTrue(env["mcp"]["configured"])
        self.assertIn(str(config), env["mcp"]["detected_in"])
        self.assertEqual(env["recommended"], "mcp")

    def test_cli_json_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = subprocess.run(
                [sys.executable, "-B", str(DOCTOR), "--root", str(root), "--check", "--json"],
                capture_output=True,
                text=True,
                timeout=20,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["schema_version"], 1)
        for key in ("node", "app", "mcp", "options", "recommended"):
            self.assertIn(key, data)

    def test_node_18_is_not_enough(self):
        """@playwright/test 1.65 declara engines node>=20: el doctor no debe ofrecer instalar con 18."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.object(self.doctor.shutil, "which", side_effect=lambda name: "/usr/bin/node" if name == "node" else None):
                with mock.patch.object(self.doctor, "run_command", return_value=(0, "v18.20.0", "")):
                    env = self.doctor.check_environment(root, home=root / "home", module_dir=root / "module")
        self.assertTrue(env["node"]["available"])
        self.assertEqual(env["node"]["major"], 18)
        install_app = [item for item in env["options"] if item["id"] == "install-app"][0]
        self.assertFalse(install_app["available"], install_app)
        self.assertEqual(env["recommended"], "skip")
        self.assertTrue(any("20+" in blocker for blocker in env["blockers"]), env["blockers"])

    def test_force_missing_playwright_env_var(self):
        """QS_FORCE_MISSING_PLAYWRIGHT=1 permite probar el onboarding con Playwright instalado."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "agent-dist/skills/quinotospec-review/e2e/node_modules/@playwright/test/package.json"
            package.parent.mkdir(parents=True)
            package.write_text(json.dumps({"version": "1.65.0"}), encoding="utf-8")
            config = root / "opencode.json"
            config.write_text(json.dumps({"mcp": {"playwright": {"command": ["npx", "@playwright/mcp@latest"]}}}), encoding="utf-8")
            with mock.patch.object(self.doctor.shutil, "which", side_effect=lambda name: "/usr/bin/node" if name == "node" else None):
                with mock.patch.object(self.doctor, "run_command", return_value=(0, "v20.11.0", "")):
                    forced = self.doctor.check_environment(
                        root,
                        home=root / "home",
                        module_dir=root / "module",
                        env={"QS_FORCE_MISSING_PLAYWRIGHT": "1"},
                    )
                    real = self.doctor.check_environment(
                        root,
                        home=root / "home",
                        module_dir=root / "module",
                        env={},
                    )
        self.assertTrue(real["app"]["available"] and real["mcp"]["configured"])
        self.assertFalse(forced["app"]["available"])
        self.assertFalse(forced["mcp"]["configured"])
        self.assertTrue(forced.get("forced_missing_playwright"))


if __name__ == "__main__":
    unittest.main()
