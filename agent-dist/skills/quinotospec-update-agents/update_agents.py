#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

sys.dont_write_bytecode = True

try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quinotospec-extension-manager"))
    from extension_manager import load_document  # type: ignore
except ImportError:
    load_document = None


class AgentsError(Exception):
    pass


def read_document(path: Path) -> Dict[str, Any]:
    if load_document is not None:
        try:
            return load_document(path)
        except Exception as error:
            raise AgentsError(str(error)) from error
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AgentsError("cannot read config: " + str(error)) from error
    if not isinstance(data, dict):
        raise AgentsError("config must contain an object")
    return data


def string_value(value: Any, default: str = "") -> str:
    if isinstance(value, str) and value.strip() and not value.strip().startswith("{{"):
        return value.strip()
    return default


def list_value(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip() and not item.strip().startswith("{{")]


def bullet_list(values: Sequence[str]) -> str:
    return "\n".join("- `" + value + "`" for value in values) if values else "- Ninguno configurado"


def installed_extensions(root: Path) -> List[str]:
    path = root / ".quinoto-spec/extensions/.registry"
    if not path.is_file() or path.is_symlink():
        return []
    try:
        data = read_document(path)
    except AgentsError:
        return []
    installed = data.get("installed", {}) if isinstance(data, dict) else {}
    if not isinstance(installed, dict):
        return []
    return sorted(identifier for identifier, entry in installed.items() if isinstance(entry, dict) and entry.get("kind") == "extension")


def core_workflows(root: Path) -> List[str]:
    directory = root / "agent-dist/workflows"
    if not directory.is_dir():
        return []
    aliases = {
        "create-proposal": "proposal",
        "create-user-stories": "user-stories",
        "create-tasks": "tasks",
    }
    values = []
    for path in directory.glob("quinotospec.*.md"):
        if not path.is_file():
            continue
        name = path.stem.replace("quinotospec.", "")
        values.append(aliases.get(name, name))
    return sorted(values)


def core_skills(root: Path) -> List[str]:
    directory = root / "agent-dist/skills"
    if not directory.is_dir():
        return []
    return sorted(path.name for path in directory.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())


def core_rules(root: Path) -> List[str]:
    path = root / "agent-dist/rules/quinotospec-rules.md"
    if not path.is_file() or path.is_symlink():
        return []
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            values.append(line[2:].strip())
    return values


def build_replacements(inventory_root: Path, state_root: Path, config: Dict[str, Any]) -> Dict[str, str]:
    project = config.get("project", {})
    context = config.get("context", {})
    workflows = config.get("workflows", {})
    rules = config.get("rules", {})
    if not isinstance(project, dict):
        project = {}
    if not isinstance(context, dict):
        context = {}
    if not isinstance(workflows, dict):
        workflows = {}
    if not isinstance(rules, dict):
        rules = {}
    active = list_value(workflows.get("active"))
    optional = list_value(workflows.get("optional"))
    available = set(core_workflows(inventory_root))
    active = [item for item in active if item in available] or [item for item in available if item in {"constitution", "discovery", "proposal", "user-stories", "tasks", "apply", "review", "archive"}]
    optional = [item for item in optional if item in available and item not in active]
    skills = core_skills(inventory_root)
    extensions = installed_extensions(state_root)
    return {
        "PROJECT_NAME": string_value(project.get("name"), state_root.name),
        "STACK": string_value(project.get("stack"), "not configured"),
        "LANGUAGE": string_value(project.get("language"), "not configured"),
        "TECH_STACK": string_value(context.get("tech_stack"), "not configured"),
        "CONVENTIONS": string_value(context.get("conventions"), "not configured"),
        "TESTING": string_value(context.get("testing"), "not configured"),
        "STRICTNESS": string_value(rules.get("strictness"), "standard"),
        "WORKFLOWS": bullet_list(["@quinotospec." + item for item in active]),
        "OPTIONAL_WORKFLOWS": bullet_list(["@quinotospec." + item for item in optional]),
        "SKILLS": bullet_list(["/" + item for item in skills]),
        "RULES": bullet_list(core_rules(inventory_root)),
        "EXTENSIONS": bullet_list(extensions),
    }


def render(template: str, replacements: Dict[str, str]) -> str:
    result = template
    for key, value in replacements.items():
        result = result.replace("{{" + key + "}}", value)
    unresolved = [token for token in result.split() if token.startswith("{{") and token.endswith("}}")]
    if unresolved:
        raise AgentsError("unresolved template placeholders: " + ", ".join(sorted(set(unresolved))))
    return result if result.endswith("\n") else result + "\n"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate AGENTS.md from project configuration")
    parser.add_argument("--root", default=".")
    parser.add_argument("--inventory-root")
    parser.add_argument("--state-root")
    parser.add_argument("--config")
    parser.add_argument("--template")
    parser.add_argument("--output", default="AGENTS.md")
    parser.add_argument("--allow-external-output", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if args.write == args.check:
        print("Choose exactly one of --write or --check", file=sys.stderr)
        return 2
    root = Path(args.root).resolve()
    inventory_root = Path(args.inventory_root).resolve() if args.inventory_root else root
    state_root = Path(args.state_root).resolve() if args.state_root else root
    try:
        if not root.is_dir() or not inventory_root.is_dir() or not state_root.is_dir():
            raise AgentsError("project, inventory, and state roots must be directories")
        config_path = Path(args.config) if args.config else root / ".quinoto-spec/config.yaml"
        if not config_path.is_absolute():
            config_path = root / config_path
        if not config_path.is_file() and args.config is None:
            config_path = root / "agent-dist/templates/config-template.yml"
        template_path = Path(args.template) if args.template else root / "agent-dist/templates/AGENTS-template.md"
        if not template_path.is_absolute():
            template_path = root / template_path
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = root / output_path
        if not args.allow_external_output:
            try:
                output_path.resolve().relative_to(root)
            except ValueError as error:
                raise AgentsError("output must stay within project root") from error
        content = render(template_path.read_text(encoding="utf-8"), build_replacements(inventory_root, state_root, read_document(config_path)))
        current = output_path.read_text(encoding="utf-8") if output_path.is_file() else None
        changed = current != content
        if args.write and changed:
            atomic_write(output_path, content)
        result = {
            "output": str(output_path),
            "config": str(config_path),
            "changed": changed,
            "written": bool(args.write and changed),
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        }
    except (AgentsError, OSError) as error:
        result = {"error": str(error)}
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("AGENTS generator error: " + str(error), file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("AGENTS.md " + ("updated" if result["written"] else "is current"))
    return 0 if not args.check or not result["changed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
