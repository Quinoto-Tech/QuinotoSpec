#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True

NAME_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")
KINDS = ("template", "command", "skill")


class ResolverError(Exception):
    pass


try:
    from extension_manager import load_document as _load_manifest_document
except ImportError:
    _load_manifest_document = None


def load_document(path: Path) -> Dict[str, Any]:
    if _load_manifest_document is not None:
        try:
            return _load_manifest_document(path)
        except Exception as error:
            raise ResolverError(str(error)) from error
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ResolverError("cannot read manifest: " + str(error)) from error
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ResolverError("JSON or PyYAML support is required to read this manifest") from error
    if not isinstance(data, dict):
        raise ResolverError("manifest must contain an object")
    return data


def safe_name(value: str) -> str:
    if not value or not NAME_PATTERN.fullmatch(value) or ".." in Path(value).parts or Path(value).is_absolute():
        raise ResolverError("name must be a safe relative identifier")
    return value


def priority_for(directory: Path, kind: str) -> int:
    manifest_name = "preset.yml" if kind == "preset" else "extension.yml"
    path = directory / manifest_name
    if not path.is_file() or path.is_symlink():
        return 100
    data = load_document(path)
    section = data.get(kind, {})
    priority = section.get("priority", data.get("priority", 100)) if isinstance(section, dict) else 100
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ResolverError("manifest priority must be an integer")
    return priority


def candidate_paths(root: Path, kind: str, name: str) -> List[Tuple[str, Path]]:
    candidates: List[Tuple[str, Path]] = []
    overrides = root / ".quinoto-spec/overrides"
    if kind == "template":
        candidates.append(("override", overrides / "templates" / name))
    elif kind == "command":
        candidates.extend([("override", overrides / "workflows" / name), ("override", overrides / "commands" / name)])
    else:
        candidates.extend([("override", overrides / "skills" / name / "SKILL.md"), ("override", overrides / "skills" / (name + ".md"))])
    preset_root = root / ".quinoto-spec/presets"
    if preset_root.is_dir():
        presets = sorted((path for path in preset_root.iterdir() if path.is_dir() and not path.is_symlink()), key=lambda path: (priority_for(path, "preset"), path.name))
        for preset in presets:
            if kind == "template":
                candidates.append(("preset", preset / "templates" / name))
            elif kind == "command":
                candidates.extend([("preset", preset / "workflows" / name), ("preset", preset / "commands" / name)])
            else:
                candidates.extend([("preset", preset / "skills" / name / "SKILL.md"), ("preset", preset / "skills" / (name + ".md"))])
    extension_root = root / ".quinoto-spec/extensions"
    if extension_root.is_dir():
        extensions = sorted((path for path in extension_root.iterdir() if path.is_dir() and not path.is_symlink()), key=lambda path: (priority_for(path, "extension"), path.name))
        for extension in extensions:
            if kind == "template":
                candidates.append(("extension", extension / "templates" / name))
            elif kind == "command":
                candidates.append(("extension", extension / "commands" / name))
            else:
                candidates.extend([("extension", extension / "skills" / name / "SKILL.md"), ("extension", extension / "skills" / (name + ".md"))])
    if kind == "template":
        candidates.append(("core", root / "agent-dist/templates" / name))
    elif kind == "command":
        candidates.append(("core", root / "agent-dist/workflows" / name))
    else:
        candidates.append(("core", root / "agent-dist/skills" / name / "SKILL.md"))
    return candidates


def resolve(root: Path, kind: str, name: str) -> Dict[str, Any]:
    checked: List[str] = []
    for layer, path in candidate_paths(root, kind, name):
        try:
            display_path = str(path.relative_to(root))
        except ValueError:
            display_path = str(path)
        checked.append(display_path)
        if path.is_symlink():
            raise ResolverError("resolver refuses symlinked candidate: " + str(path))
        if path.is_file():
            return {"resolved": True, "kind": kind, "name": name, "layer": layer, "path": str(path), "checked": checked}
    return {"resolved": False, "kind": kind, "name": name, "layer": None, "path": None, "checked": checked}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="QuinotoSpec four-layer template resolver")
    parser.add_argument("--root", default=".")
    parser.add_argument("--kind", choices=KINDS, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print("Resolver error: project root is not a directory", file=sys.stderr)
        return 2
    try:
        result = resolve(root, args.kind, safe_name(args.name))
    except ResolverError as error:
        if args.as_json:
            print(json.dumps({"resolved": False, "error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print("Resolver error: " + str(error), file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["resolved"]:
        print(result["layer"] + "\t" + result["path"])
    else:
        print("No candidate found")
    return 0 if result["resolved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
