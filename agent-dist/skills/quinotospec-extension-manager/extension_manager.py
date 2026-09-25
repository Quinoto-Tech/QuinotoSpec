#!/usr/bin/env python3
import argparse
import ast
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True

SCHEMA_VERSION = 1
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
HOOK_POINTS = {
    "before_proposal",
    "after_proposal",
    "before_delta_specs",
    "after_delta_specs",
    "before_user_stories",
    "after_user_stories",
    "before_design",
    "after_design",
    "before_tasks",
    "after_tasks",
    "before_apply",
    "after_apply",
    "before_review",
    "after_review",
    "before_archive",
    "after_archive",
    "before_constitution",
    "after_constitution",
}


class ExtensionError(Exception):
    pass


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value[:1] in {"\"", "'"} and value[-1:] == value[:1]:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as error:
            raise ExtensionError("invalid quoted scalar: " + value) from error
    if value[:1] in {"[", "{"}:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?(?:\d+\.\d*|\.\d+)", value):
        return float(value)
    return value


def strip_comment(value: str) -> str:
    quote = ""
    for index, character in enumerate(value):
        if character in {"\"", "'"}:
            if not quote:
                quote = character
            elif quote == character:
                quote = ""
        elif character == "#" and not quote and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def parse_simple_yaml(text: str) -> Any:
    entries: List[Tuple[int, str, int]] = []
    for number, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise ExtensionError("tabs are not supported in simple YAML at line " + str(number))
        content = strip_comment(raw.strip())
        if not content:
            continue
        entries.append((len(raw) - len(raw.lstrip()), content, number))
    if not entries:
        return {}
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Any]] = [(-1, root)]
    for index, (indent, content, number) in enumerate(entries):
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            raise ExtensionError("invalid indentation at line " + str(number))
        parent = stack[-1][1]
        if content.startswith("- ") or content == "-":
            if not isinstance(parent, list):
                raise ExtensionError("list item without list parent at line " + str(number))
            item_text = content[1:].strip()
            if not item_text:
                child: Any = {}
                parent.append(child)
                stack.append((indent, child))
            elif ":" in item_text and not item_text.startswith(("\"", "'")):
                key, raw_value = item_text.split(":", 1)
                item = {key.strip(): parse_scalar(raw_value)} if raw_value.strip() else {}
                parent.append(item)
                stack.append((indent, item))
            else:
                parent.append(parse_scalar(item_text))
            continue
        if not isinstance(parent, dict) or ":" not in content:
            raise ExtensionError("mapping entry expected at line " + str(number))
        key, raw_value = content.split(":", 1)
        key = key.strip()
        if not key:
            raise ExtensionError("empty mapping key at line " + str(number))
        if raw_value.strip():
            parent[key] = parse_scalar(raw_value)
            continue
        next_is_list = False
        if index + 1 < len(entries):
            next_indent, next_content, _ = entries[index + 1]
            next_is_list = next_indent > indent and (next_content.startswith("- ") or next_content == "-")
        child = [] if next_is_list else {}
        parent[key] = child
        stack.append((indent, child))
    return root


def load_document(path: Path) -> Dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ExtensionError("cannot read manifest: " + str(error)) from error
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError:
            data = parse_simple_yaml(text)
        else:
            try:
                data = yaml.safe_load(text)
            except Exception as error:
                raise ExtensionError("invalid YAML manifest: " + str(error)) from error
    if not isinstance(data, dict):
        raise ExtensionError("manifest must contain an object")
    return data


def nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExtensionError(field + " must be a non-empty string")
    return value.strip()


def validate_id(value: Any, field: str = "id") -> str:
    result = nonempty(value, field)
    if not ID_PATTERN.fullmatch(result):
        raise ExtensionError(field + " contains unsupported characters")
    return result


def validate_version(value: Any, field: str = "version") -> str:
    result = nonempty(value, field)
    if not VERSION_PATTERN.fullmatch(result):
        raise ExtensionError(field + " must be semantic versioning")
    return result


def safe_relative(value: Any, field: str) -> Path:
    text = nonempty(value, field)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ExtensionError(field + " must be a safe relative path")
    return path


def validate_hook_map(value: Any) -> Dict[str, List[Dict[str, Any]]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ExtensionError("hooks must be an object")
    result: Dict[str, List[Dict[str, Any]]] = {}
    for point, entries in value.items():
        if point not in HOOK_POINTS:
            raise ExtensionError("unsupported hook point: " + str(point))
        if not isinstance(entries, list):
            raise ExtensionError("hooks." + point + " must be a list")
        normalized: List[Dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ExtensionError("hooks." + point + " entries must be objects")
            command = nonempty(entry.get("command"), "hooks." + point + ".command")
            priority = entry.get("priority", 100)
            if not isinstance(priority, int) or isinstance(priority, bool):
                raise ExtensionError("hooks." + point + ".priority must be an integer")
            auto = entry.get("auto", False)
            if not isinstance(auto, bool):
                raise ExtensionError("hooks." + point + ".auto must be boolean")
            normalized.append({"command": command, "priority": priority, "auto": auto})
        normalized.sort(key=lambda item: (item["priority"], item["command"]))
        result[point] = normalized
    return result


def validate_manifest(data: Dict[str, Any], kind: str) -> Dict[str, Any]:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ExtensionError("unsupported manifest schema_version")
    section = data.get(kind)
    if not isinstance(section, dict):
        raise ExtensionError(kind + " metadata is required")
    identifier = validate_id(section.get("id"), kind + ".id")
    version = validate_version(section.get("version"), kind + ".version")
    name = nonempty(section.get("name"), kind + ".name")
    description = section.get("description", "")
    if description is not None and not isinstance(description, str):
        raise ExtensionError(kind + ".description must be a string")
    provides = data.get("provides", {})
    if provides is None:
        provides = {}
    if not isinstance(provides, dict):
        raise ExtensionError("provides must be an object")
    normalized_provides: Dict[str, List[str]] = {}
    for key in ("commands", "skills", "hooks"):
        values = provides.get(key, [])
        if not isinstance(values, list):
            raise ExtensionError("provides." + key + " must be a list")
        normalized = []
        for value in values:
            item = nonempty(value, "provides." + key)
            safe_relative(item, "provides." + key)
            normalized.append(item)
        normalized_provides[key] = normalized
    hooks = validate_hook_map(data.get("hooks", {}))
    priority = data.get("priority", 100)
    if not isinstance(priority, int) or isinstance(priority, bool):
        raise ExtensionError("priority must be an integer")
    return {
        "schema_version": SCHEMA_VERSION,
        kind: {
            "id": identifier,
            "name": name,
            "version": version,
            "description": description or "",
            "priority": priority,
        },
        "requires": data.get("requires", {}),
        "provides": normalized_provides,
        "hooks": hooks,
    }


def reject_symlinks(root: Path) -> None:
    if root.is_symlink():
        raise ExtensionError("extension source must not be a symlink")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ExtensionError("extension source contains a symlink: " + str(path))


def manifest_path(root: Path, kind: str) -> Path:
    return root / ("extension.yml" if kind == "extension" else "preset.yml")


def load_manifest(root: Path, kind: str) -> Dict[str, Any]:
    path = manifest_path(root, kind)
    if not path.is_file() or path.is_symlink():
        raise ExtensionError("missing " + kind + " manifest: " + str(path))
    return validate_manifest(load_document(path), kind)


def registry_path(root: Path) -> Path:
    return root / ".quinoto-spec/extensions/.registry"


def load_registry(root: Path) -> Dict[str, Any]:
    path = registry_path(root)
    if not path.is_file() or path.is_symlink():
        return {"schema_version": SCHEMA_VERSION, "installed": {}}
    data = load_document(path)
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION or not isinstance(data.get("installed"), dict):
        raise ExtensionError("extension registry is invalid")
    return data


def write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def catalog_entries(root: Path, catalog: Optional[str]) -> List[Dict[str, Any]]:
    paths = [Path(catalog)] if catalog else [Path("extensions/catalog.json"), Path("extensions/catalog.community.json")]
    entries: List[Dict[str, Any]] = []
    for raw in paths:
        path = raw if raw.is_absolute() else root / raw
        if not path.is_file():
            continue
        data = load_document(path)
        values = data.get("extensions", [])
        if not isinstance(values, list):
            raise ExtensionError("catalog extensions must be a list: " + str(path))
        for entry in values:
            if isinstance(entry, dict):
                item = dict(entry)
                item["_catalog"] = str(path)
                entries.append(item)
    return entries


def catalog_source(root: Path, identifier: str, catalog: Optional[str]) -> Path:
    for entry in catalog_entries(root, catalog):
        if entry.get("id") == identifier:
            value = entry.get("path")
            if not value:
                raise ExtensionError("catalog entry has no local path: " + identifier)
            path = Path(value)
            if not path.is_absolute():
                path = Path(entry["_catalog"]).parent / path
            return path.resolve()
    raise ExtensionError("extension not found in catalogs: " + identifier)


def source_path(root: Path, source: str, catalog: Optional[str]) -> Path:
    if source.startswith("catalog:"):
        return catalog_source(root, source.split(":", 1)[1], catalog)
    path = resolve_path(root, source)
    if not path.is_dir():
        raise ExtensionError("extension source directory not found: " + str(path))
    reject_symlinks(path)
    return path


def installed_path(root: Path, identifier: str, kind: str) -> Path:
    base = root / ".quinoto-spec" / ("extensions" if kind == "extension" else "presets")
    path = base / identifier
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise ExtensionError("installed path is unsafe: " + str(path))
    try:
        path.resolve().relative_to(base.resolve())
    except ValueError as error:
        raise ExtensionError("installed path escapes its root") from error
    return path


def copy_staged(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=str(destination.parent)))
    payload = staging / "payload"
    try:
        shutil.copytree(source, payload)
        reject_symlinks(payload)
        backup = None
        if destination.exists():
            backup = staging / "previous"
            os.replace(destination, backup)
        os.replace(payload, destination)
        shutil.rmtree(staging, ignore_errors=True)
    except Exception:
        if destination.exists() and not (staging / "payload").exists():
            pass
        if staging.exists():
            previous = staging / "previous"
            if previous.exists() and not destination.exists():
                os.replace(previous, destination)
        shutil.rmtree(staging, ignore_errors=True)
        raise


def update_registry(root: Path, kind: str, manifest: Dict[str, Any], source: str) -> None:
    registry = load_registry(root)
    identifier = manifest[kind]["id"]
    entry = registry["installed"].get(identifier)
    if entry is not None and entry.get("kind") != kind:
        raise ExtensionError("identifier is already registered with another kind: " + identifier)
    registry["installed"][identifier] = {
        "id": identifier,
        "kind": kind,
        "version": manifest[kind]["version"],
        "path": str(installed_path(root, identifier, kind).relative_to(root)),
        "source": source,
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json_atomic(registry_path(root), registry)


def command_install(root: Path, kind: str, source_value: str, catalog: Optional[str], replace: bool) -> Dict[str, Any]:
    source = source_path(root, source_value, catalog)
    manifest = load_manifest(source, kind)
    identifier = manifest[kind]["id"]
    destination = installed_path(root, identifier, kind)
    if destination.exists() and not replace:
        raise ExtensionError("already installed; use update or --replace: " + identifier)
    copy_staged(source, destination)
    try:
        update_registry(root, kind, manifest, source_value)
    except Exception:
        if destination.exists():
            shutil.rmtree(destination, ignore_errors=True)
        raise
    return {"action": "install", "kind": kind, "id": identifier, "version": manifest[kind]["version"], "path": str(destination)}


def command_remove(root: Path, kind: str, identifier: str, confirmed: bool) -> Dict[str, Any]:
    if not confirmed:
        raise ExtensionError("remove requires --yes")
    registry = load_registry(root)
    entry = registry["installed"].get(identifier)
    if entry is None or entry.get("kind") != kind:
        raise ExtensionError("extension is not registered: " + identifier)
    destination = installed_path(root, identifier, kind)
    if not destination.exists():
        raise ExtensionError("registered path is missing: " + str(destination))
    shutil.rmtree(destination)
    del registry["installed"][identifier]
    write_json_atomic(registry_path(root), registry)
    return {"action": "remove", "kind": kind, "id": identifier}


def command_list(root: Path, kind: Optional[str]) -> Dict[str, Any]:
    registry = load_registry(root)
    values = [entry for entry in registry["installed"].values() if kind is None or entry.get("kind") == kind]
    values.sort(key=lambda item: item.get("id", ""))
    return {"installed": values}


def command_search(root: Path, query: str, catalog: Optional[str]) -> Dict[str, Any]:
    query_lower = query.lower()
    values = []
    for entry in catalog_entries(root, catalog):
        haystack = " ".join(str(entry.get(key, "")) for key in ("id", "name", "description")).lower()
        if not query or query_lower in haystack:
            values.append({key: value for key, value in entry.items() if key != "_catalog"})
    return {"results": values}


def command_info(root: Path, kind: str, identifier: str) -> Dict[str, Any]:
    path = installed_path(root, identifier, kind)
    if not path.is_dir():
        raise ExtensionError("extension is not installed: " + identifier)
    return {"kind": kind, "id": identifier, "manifest": load_manifest(path, kind)}


def hook_entries(root: Path, point: Optional[str]) -> List[Dict[str, Any]]:
    if point is not None and point not in HOOK_POINTS:
        raise ExtensionError("unsupported hook point: " + point)
    registry = load_registry(root)
    result: List[Dict[str, Any]] = []
    for identifier, entry in sorted(registry["installed"].items()):
        if entry.get("kind") != "extension":
            continue
        manifest = load_manifest(installed_path(root, identifier, "extension"), "extension")
        for hook_point, entries in manifest["hooks"].items():
            if point is not None and hook_point != point:
                continue
            for hook in entries:
                result.append({"extension": identifier, "point": hook_point, **hook})
    result.sort(key=lambda item: (item["point"], item["priority"], item["extension"], item["command"]))
    return result


def command_hooks(root: Path, point: Optional[str], run: bool, confirmed: bool) -> Dict[str, Any]:
    entries = hook_entries(root, point)
    if not run:
        return {"hooks": entries}
    if not confirmed:
        raise ExtensionError("hook execution requires --yes")
    results = []
    for entry in entries:
        if not entry["auto"]:
            continue
        command = shlex.split(entry["command"])
        if not command:
            raise ExtensionError("hook command cannot be empty")
        completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True, check=False, timeout=30)
        results.append({**entry, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
        if completed.returncode != 0:
            raise ExtensionError("hook failed: " + entry["extension"] + " " + entry["command"])
    return {"hooks": entries, "results": results}


def print_result(result: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if "installed" in result:
        for item in result["installed"]:
            print(item.get("id"), item.get("kind"), item.get("version"))
    elif "results" in result:
        for item in result["results"]:
            print(item)
    elif "hooks" in result:
        for item in result["hooks"]:
            print(item)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QuinotoSpec extension and preset lifecycle manager")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    subparsers = parser.add_subparsers(dest="command", required=True)
    install = subparsers.add_parser("install")
    install.add_argument("--kind", choices=("extension", "preset"), default="extension")
    install.add_argument("--source", required=True)
    install.add_argument("--catalog")
    install.add_argument("--replace", action="store_true")
    update = subparsers.add_parser("update")
    update.add_argument("--kind", choices=("extension", "preset"), default="extension")
    update.add_argument("--source", required=True)
    update.add_argument("--catalog")
    remove = subparsers.add_parser("remove")
    remove.add_argument("--kind", choices=("extension", "preset"), default="extension")
    remove.add_argument("id")
    remove.add_argument("--yes", action="store_true")
    listing = subparsers.add_parser("list")
    listing.add_argument("--kind", choices=("extension", "preset"))
    search = subparsers.add_parser("search")
    search.add_argument("query")
    search.add_argument("--catalog")
    info = subparsers.add_parser("info")
    info.add_argument("--kind", choices=("extension", "preset"), default="extension")
    info.add_argument("id")
    hooks = subparsers.add_parser("hooks")
    hooks.add_argument("--point", choices=sorted(HOOK_POINTS))
    hooks.add_argument("--run", action="store_true")
    hooks.add_argument("--yes", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": "project root is not a directory"}, ensure_ascii=False), file=sys.stderr)
        return 2
    try:
        if args.command == "install":
            result = command_install(root, args.kind, args.source, args.catalog, args.replace)
        elif args.command == "update":
            result = command_install(root, args.kind, args.source, args.catalog, True)
        elif args.command == "remove":
            result = command_remove(root, args.kind, args.id, args.yes)
        elif args.command == "list":
            result = command_list(root, args.kind)
        elif args.command == "search":
            result = command_search(root, args.query, args.catalog)
        elif args.command == "info":
            result = command_info(root, args.kind, args.id)
        else:
            result = command_hooks(root, args.point, args.run, args.yes)
    except (ExtensionError, OSError, subprocess.SubprocessError) as error:
        result = {"error": str(error)}
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("Extension manager error: " + str(error), file=sys.stderr)
        return 1
    print_result(result, args.as_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
