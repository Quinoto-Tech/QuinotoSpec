#!/usr/bin/env python3
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "agent-dist/skills/quinotospec-update-agents/update_agents.py"
TEMPLATE = ROOT / "agent-dist/templates/AGENTS-template.md"


class AgentsTests(unittest.TestCase):
    def run_generator(self, root, *args):
        command = [sys.executable, "-B", str(GENERATOR), "--root", str(root), "--inventory-root", str(ROOT), "--state-root", str(root), "--template", str(TEMPLATE), "--json"]
        command.extend(args)
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertIn(completed.returncode, (0, 1), completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def write_config(self, root, name="demo-project"):
        config = root / ".quinoto-spec/config.yaml"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(
            "schema_version: 1\n"
            "project:\n"
            "  name: " + name + "\n"
            "  stack: node-express\n"
            "  language: typescript\n"
            "context:\n"
            "  tech_stack: Node.js 20\n"
            "  conventions: Conventional commits\n"
            "  testing: Jest\n"
            "workflows:\n"
            "  active: [constitution, discovery, proposal]\n"
            "  optional: [review]\n"
            "rules:\n"
            "  strictness: strict\n"
            "extensions: []\n",
            encoding="utf-8",
        )
        return config

    def test_generates_and_checks_dynamic_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_config(root)
            code, result = self.run_generator(root, "--config", str(root / ".quinoto-spec/config.yaml"), "--write")
            self.assertEqual(code, 0, result)
            output = root / "AGENTS.md"
            self.assertTrue(output.is_file())
            content = output.read_text(encoding="utf-8")
            self.assertIn("demo-project", content)
            self.assertIn("@quinotospec.proposal", content)
            self.assertIn("Node.js 20", content)
            self.assertIn("GENERATED", content)
            code, result = self.run_generator(root, "--config", str(root / ".quinoto-spec/config.yaml"), "--check")
            self.assertEqual(code, 0, result)
            self.write_config(root, name="renamed-project")
            code, result = self.run_generator(root, "--config", str(root / ".quinoto-spec/config.yaml"), "--check")
            self.assertEqual(code, 1)
            self.assertTrue(result["changed"])

    def test_agent_personality_parity(self):
        """agent-defaults.toml es la fuente canonica; agents/*.md debe coincidir."""
        defaults = (ROOT / "agent-dist/config/agent-defaults.toml").read_text(encoding="utf-8")
        blocks = {}
        for match in re.finditer(r"^\[agents\.([a-z-]+)\]\n(.*?)(?=^\[|\Z)", defaults, re.M | re.S):
            personality = re.search(r'^personality = "(.*)"$', match.group(2), re.M)
            if personality:
                blocks[match.group(1)] = personality.group(1)
        self.assertEqual(len(blocks), 9, blocks)
        for key, personality in blocks.items():
            content = (ROOT / "agent-dist/agents" / (key + ".md")).read_text(encoding="utf-8")
            section = content.split("## Personalidad", 1)[1].split("\n## ", 1)[0].strip()
            self.assertEqual(section, personality, key)

    def test_registry_extensions_are_rendered(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_config(root)
            registry = root / ".quinoto-spec/extensions/.registry"
            registry.parent.mkdir(parents=True, exist_ok=True)
            registry.write_text(json.dumps({"schema_version": 1, "installed": {"example-extension": {"kind": "extension"}}}), encoding="utf-8")
            code, result = self.run_generator(root, "--config", str(root / ".quinoto-spec/config.yaml"), "--write")
            self.assertEqual(code, 0, result)
            self.assertIn("example-extension", (root / "AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
