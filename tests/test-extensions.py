#!/usr/bin/env python3
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "agent-dist/skills/quinotospec-extension-manager/extension_manager.py"
RESOLVER = ROOT / "agent-dist/skills/quinotospec-template-resolver/template_resolver.py"
EXTENSION_ID = "example-extension"


class ExtensionTests(unittest.TestCase):
    def write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def make_source(self, root, identifier=EXTENSION_ID, version="0.1.0", hook=True):
        source = root / "source" / identifier
        manifest = {
            "schema_version": 1,
            "extension": {
                "id": identifier,
                "name": "Example Extension",
                "version": version,
                "description": "A local test extension",
                "priority": 100,
            },
            "requires": {"quinotospec_version": ">=3.1.0"},
            "provides": {"commands": ["example-sync"], "skills": ["quinotospec-example"], "hooks": []},
            "hooks": {
                "before_apply": [
                    {
                        "command": "python3 -c " + shlex.quote("from pathlib import Path; Path('hook-ran').write_text('ok')"),
                        "priority": 10,
                        "auto": hook,
                    }
                ]
            },
        }
        self.write_json(source / "extension.yml", manifest)
        (source / "commands").mkdir(parents=True, exist_ok=True)
        (source / "commands" / "example-sync.md").write_text("# Example\n", encoding="utf-8")
        (source / "skills" / "quinotospec-example").mkdir(parents=True, exist_ok=True)
        (source / "skills" / "quinotospec-example" / "SKILL.md").write_text("# Example Skill\n", encoding="utf-8")
        (source / "templates").mkdir(parents=True, exist_ok=True)
        (source / "templates" / "example-template.md").write_text("example\n", encoding="utf-8")
        return source

    def run_manager(self, root, *args):
        command = [sys.executable, "-B", str(MANAGER), "--root", str(root), "--json"]
        command.extend(args)
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertIn(completed.returncode, (0, 1), completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def run_resolver(self, root, kind, name):
        command = [sys.executable, "-B", str(RESOLVER), "--root", str(root), "--kind", kind, "--name", name, "--json"]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        return completed.returncode, json.loads(completed.stdout)

    def test_install_list_info_update_and_remove(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root)
            code, result = self.run_manager(root, "install", "--kind", "extension", "--source", str(source))
            self.assertEqual(code, 0, result)
            registry = root / ".quinoto-spec/extensions/.registry"
            self.assertTrue(registry.is_file())
            code, result = self.run_manager(root, "list")
            self.assertEqual(code, 0)
            self.assertEqual(result["installed"][0]["id"], EXTENSION_ID)
            code, result = self.run_manager(root, "info", "--kind", "extension", EXTENSION_ID)
            self.assertEqual(code, 0)
            self.assertEqual(result["manifest"]["extension"]["version"], "0.1.0")
            self.make_source(root, version="0.2.0")
            code, result = self.run_manager(root, "update", "--kind", "extension", "--source", str(source))
            self.assertEqual(code, 0, result)
            code, result = self.run_manager(root, "info", "--kind", "extension", EXTENSION_ID)
            self.assertEqual(result["manifest"]["extension"]["version"], "0.2.0")
            code, result = self.run_manager(root, "remove", "--kind", "extension", EXTENSION_ID, "--yes")
            self.assertEqual(code, 0, result)
            self.assertFalse((root / ".quinoto-spec/extensions" / EXTENSION_ID).exists())

    def test_catalog_search_and_hooks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root)
            self.write_json(root / "catalog.json", {"schema_version": 1, "extensions": [{"id": EXTENSION_ID, "name": "Example", "description": "local", "path": "source/example-extension"}]})
            code, result = self.run_manager(root, "search", "example", "--catalog", "catalog.json")
            self.assertEqual(code, 0)
            self.assertEqual(result["results"][0]["id"], EXTENSION_ID)
            code, result = self.run_manager(root, "install", "--kind", "extension", "--source", "catalog:" + EXTENSION_ID, "--catalog", "catalog.json")
            self.assertEqual(code, 0, result)
            code, result = self.run_manager(root, "hooks", "--point", "before_apply")
            self.assertEqual(code, 0)
            self.assertEqual(len(result["hooks"]), 1)
            code, result = self.run_manager(root, "hooks", "--point", "before_apply", "--run", "--yes")
            self.assertEqual(code, 0, result)
            self.assertEqual((root / "hook-ran").read_text(encoding="utf-8"), "ok")

    def test_invalid_manifest_is_not_installed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_source(root)
            manifest = json.loads((source / "extension.yml").read_text(encoding="utf-8"))
            manifest["provides"]["commands"] = ["../escape"]
            self.write_json(source / "extension.yml", manifest)
            code, result = self.run_manager(root, "install", "--kind", "extension", "--source", str(source))
            self.assertEqual(code, 1)
            self.assertIn("safe relative path", result["error"])
            self.assertFalse((root / ".quinoto-spec/extensions" / EXTENSION_ID).exists())

    def test_four_layer_resolution_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core = root / "agent-dist/templates/example.md"
            core.parent.mkdir(parents=True)
            core.write_text("core\n", encoding="utf-8")
            code, result = self.run_resolver(root, "template", "example.md")
            self.assertEqual(code, 0)
            self.assertEqual(result["layer"], "core")
            override = root / ".quinoto-spec/overrides/templates/example.md"
            override.parent.mkdir(parents=True)
            override.write_text("override\n", encoding="utf-8")
            code, result = self.run_resolver(root, "template", "example.md")
            self.assertEqual(result["layer"], "override")
            override.unlink()
            preset = root / ".quinoto-spec/presets/example-preset"
            self.write_json(preset / "preset.yml", {"schema_version": 1, "preset": {"id": "example-preset", "name": "Preset", "version": "0.1.0", "priority": 20}})
            (preset / "templates").mkdir(parents=True)
            (preset / "templates" / "example.md").write_text("preset\n", encoding="utf-8")
            code, result = self.run_resolver(root, "template", "example.md")
            self.assertEqual(result["layer"], "preset")
            import shutil
            shutil.rmtree(preset)
            extension = root / ".quinoto-spec/extensions/example-extension"
            self.write_json(extension / "extension.yml", {"schema_version": 1, "extension": {"id": EXTENSION_ID, "name": "Extension", "version": "0.1.0", "priority": 10}})
            (extension / "templates").mkdir(parents=True)
            (extension / "templates" / "example.md").write_text("extension\n", encoding="utf-8")
            code, result = self.run_resolver(root, "template", "example.md")
            self.assertEqual(result["layer"], "extension")

    def test_resolver_rejects_unsafe_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, result = self.run_resolver(root, "template", "../secret.md")
            self.assertEqual(code, 1)
            self.assertIn("safe relative identifier", result["error"])


if __name__ == "__main__":
    unittest.main()
