#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.dont_write_bytecode = True

SCHEMA_VERSION = 1
BACKUP_TYPES = ("full", "incremental", "proposals", "discovery")
INTERNAL_TYPES = ("pre-restore",)
EXCLUDED_NAMES = {"backups", "mimir", "__pycache__", ".git"}
SECRET_NAMES = {".env", "credentials", "id_rsa", "id_ed25519"}


class BackupError(Exception):
    pass


class VerificationError(BackupError):
    pass


def now_values() -> Tuple[str, float]:
    current = datetime.now(timezone.utc)
    return current.isoformat(), current.timestamp()


def default_store(root: Path) -> Path:
    return root / ".quinoto-spec-backups"


def resolve_store(root: Path, value: Optional[str]) -> Path:
    store = Path(value) if value else default_store(root)
    if not store.is_absolute():
        store = root / store
    if store.exists() and store.is_symlink():
        raise BackupError("backup store cannot be a symlink: " + str(store))
    return store.resolve()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def ensure_store_outside_source(root: Path, store: Path) -> None:
    source = (root / ".quinoto-spec").resolve()
    try:
        store.relative_to(source)
    except ValueError:
        return
    raise BackupError("backup store must be outside .quinoto-spec/")


def safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise BackupError("unsafe path in manifest: " + value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise BackupError("unsafe path in manifest: " + value)
    return path


def is_excluded(relative: Path) -> bool:
    return any(part in EXCLUDED_NAMES for part in relative.parts) or any(part in SECRET_NAMES for part in relative.parts) or relative.name.startswith(".last-backup") or relative.suffix.lower() in {".pem", ".key"}


def source_files(root: Path, scope: str) -> List[Path]:
    source = root / ".quinoto-spec"
    if source.is_symlink():
        raise BackupError(".quinoto-spec/ cannot be a symlink")
    if not source.is_dir():
        raise BackupError(".quinoto-spec/ does not exist")
    if scope not in {"full", "proposals", "discovery"}:
        raise BackupError("unsupported backup scope: " + scope)
    files: List[Path] = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise BackupError("symlinks are not supported in backup source: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if is_excluded(relative):
            continue
        if scope in {"proposals", "discovery"} and (not relative.parts or relative.parts[0] != scope):
            continue
        files.append(path)
    return files


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(source: Path, relative: Path) -> Dict[str, Any]:
    stat = source.stat()
    return {
        "path": relative.as_posix(),
        "size": stat.st_size,
        "sha256": sha256_file(source),
    }


def read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BackupError("cannot read " + str(path) + ": " + str(error))
    if not isinstance(value, dict):
        raise BackupError("JSON document is not an object: " + str(path))
    return value


def write_json_atomic(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


def latest_full_backup(store: Path) -> Optional[Path]:
    candidates: List[Tuple[float, Path]] = []
    if not store.is_dir():
        return None
    for manifest in store.glob("backup-*/manifest.json"):
        try:
            data = read_json(manifest)
            if data.get("scope") != "full" or data.get("type") not in {"full", "pre-restore"}:
                continue
            created = float(data.get("created_epoch", 0))
        except BackupError:
            continue
        candidates.append((created, manifest.parent))
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (item[0], item[1].name))[-1][1]


def make_backup_id(kind: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return "backup-{}-{}".format(kind, stamp)


def unique_backup_path(store: Path, backup_id: str) -> Path:
    candidate = store / backup_id
    suffix = 2
    while candidate.exists():
        candidate = store / (backup_id + "-" + str(suffix))
        suffix += 1
    return candidate


def create_backup(root: Path, store: Path, kind: str) -> Dict[str, Any]:
    if kind not in BACKUP_TYPES + INTERNAL_TYPES:
        raise BackupError("unsupported backup type: " + kind)
    store = store.resolve()
    ensure_store_outside_source(root, store)
    store.mkdir(parents=True, exist_ok=True)
    source = root / ".quinoto-spec"
    previous_dir = latest_full_backup(store) if kind == "incremental" else None
    previous_manifest: Optional[Dict[str, Any]] = None
    previous_files: Dict[str, Dict[str, Any]] = {}
    if previous_dir is not None:
        previous_manifest = read_json(previous_dir / "manifest.json")
        for item in previous_manifest.get("files", []):
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                previous_files[item["path"]] = item
    scope = "full" if kind in {"full", "incremental", "pre-restore"} else kind
    all_files = source_files(root, scope)
    current_paths = {path.relative_to(source).as_posix() for path in all_files}
    if kind == "incremental" and previous_manifest is not None:
        previous_epoch = float(previous_manifest.get("created_epoch", 0))
        selected = [
            path
            for path in all_files
            if path.relative_to(source).as_posix() not in previous_files
            or path.stat().st_mtime > previous_epoch
        ]
        deleted = sorted(set(previous_files) - current_paths)
        base_backup = previous_manifest.get("backup_id", previous_dir.name)
    else:
        selected = all_files
        deleted = []
        base_backup = None
    staging = Path(tempfile.mkdtemp(prefix=".backup-staging-", dir=str(store.parent)))
    payload = staging / "payload"
    payload.mkdir()
    try:
        for path in selected:
            relative = path.relative_to(source)
            destination = payload / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(path), str(destination))
        created_at, created_epoch = now_values()
        records = []
        for path in selected:
            relative = path.relative_to(source)
            records.append(file_record(payload / relative, relative))
        records.sort(key=lambda item: item["path"])
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "backup_id": "",
            "created_at": created_at,
            "created_epoch": created_epoch,
            "type": kind,
            "scope": scope,
            "source_root": str(root.resolve()),
            "store": str(store),
            "base_backup": base_backup,
            "algorithm": "sha256",
            "files": records,
            "deleted": deleted,
            "file_count": len(records),
            "total_size": sum(item["size"] for item in records),
        }
        backup_id = make_backup_id(kind)
        manifest["backup_id"] = backup_id
        write_json_atomic(staging / "manifest.json", manifest)
        destination = unique_backup_path(store, backup_id)
        manifest["backup_id"] = destination.name
        write_json_atomic(staging / "manifest.json", manifest)
        os.replace(str(staging), str(destination))
    except Exception:
        shutil.rmtree(str(staging), ignore_errors=True)
        raise
    try:
        verify_backup(destination)
    except Exception:
        shutil.rmtree(str(destination), ignore_errors=True)
        raise
    write_json_atomic(store / ".last-backup.json", {"backup_id": manifest["backup_id"], "created_at": manifest["created_at"]})
    return {"backup": manifest, "path": str(destination)}


def resolve_backup(store: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_dir() and (candidate / "manifest.json").is_file():
        path = candidate.resolve()
    else:
        if Path(value).name != value:
            raise BackupError("backup must be an id or a directory path")
        path = (store / value).resolve()
    if path.is_symlink() or not path.is_dir() or not (path / "manifest.json").is_file():
        raise BackupError("backup not found: " + str(path))
    return path


def verify_backup(backup: Path) -> Dict[str, Any]:
    manifest = read_json(backup / "manifest.json")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise VerificationError("unsupported backup manifest version")
    if manifest.get("algorithm") != "sha256":
        raise VerificationError("unsupported backup checksum algorithm")
    payload = backup / "payload"
    if not payload.is_dir() or payload.is_symlink():
        raise VerificationError("backup payload directory is missing or invalid")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise VerificationError("backup manifest files must be a list")
    verified: List[str] = []
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise VerificationError("invalid file record in manifest")
        relative = safe_relative_path(item["path"])
        target = payload / relative
        if target.is_symlink() or not target.is_file() or not is_within(target.resolve(), payload.resolve()):
            raise VerificationError("missing or unsafe payload file: " + relative.as_posix())
        if target.stat().st_size != item.get("size"):
            raise VerificationError("size mismatch: " + relative.as_posix())
        if sha256_file(target) != item.get("sha256"):
            raise VerificationError("sha256 mismatch: " + relative.as_posix())
        verified.append(relative.as_posix())
    if any(path.is_symlink() for path in payload.rglob("*")):
        raise VerificationError("backup payload contains a symlink")
    actual_files = {
        path.relative_to(payload).as_posix()
        for path in payload.rglob("*")
        if path.is_file()
    }
    if actual_files != set(verified):
        raise VerificationError("payload contains files not declared in the manifest")
    if manifest.get("file_count") != len(verified):
        raise VerificationError("manifest file count does not match payload")
    for value in manifest.get("deleted", []):
        safe_relative_path(value)
    return {
        "valid": True,
        "backup_id": manifest.get("backup_id", backup.name),
        "type": manifest.get("type", ""),
        "scope": manifest.get("scope", ""),
        "created_at": manifest.get("created_at", ""),
        "file_count": len(verified),
        "total_size": sum(item.get("size", 0) for item in files),
        "algorithm": "sha256",
        "verified_files": verified,
    }


def list_backups(store: Path) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    if store.is_dir():
        for manifest in sorted(store.glob("backup-*/manifest.json")):
            try:
                data = read_json(manifest)
                entries.append({
                    "backup_id": data.get("backup_id", manifest.parent.name),
                    "type": data.get("type", ""),
                    "scope": data.get("scope", ""),
                    "created_at": data.get("created_at", ""),
                    "file_count": data.get("file_count", len(data.get("files", []))),
                    "total_size": data.get("total_size", 0),
                    "path": str(manifest.parent),
                })
            except BackupError as error:
                entries.append({"backup_id": manifest.parent.name, "valid": False, "error": str(error)})
    entries.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return {"store": str(store), "backups": entries, "count": len(entries)}


def copy_current_to_staging(current: Path, staged: Path) -> None:
    if not current.is_dir():
        staged.mkdir(parents=True)
        return
    if any(path.is_symlink() for path in current.rglob("*")):
        raise BackupError("current .quinoto-spec contains a symlink")
    shutil.copytree(str(current), str(staged), ignore=shutil.ignore_patterns(*EXCLUDED_NAMES, ".last-backup"))


def stage_restore(root: Path, backup: Path, manifest: Dict[str, Any]) -> Path:
    source = root / ".quinoto-spec"
    payload = backup / "payload"
    temporary = Path(tempfile.mkdtemp(prefix="quinotospec-restore-", dir=str(root.parent)))
    staged = temporary / "qspec"
    try:
        if manifest.get("scope") == "full" and not manifest.get("base_backup"):
            copy_current_to_staging(payload, staged)
        else:
            copy_current_to_staging(source, staged)
            for item in manifest.get("files", []):
                relative = safe_relative_path(item["path"])
                destination = staged / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(payload / relative), str(destination))
        for value in manifest.get("deleted", []):
            relative = safe_relative_path(value)
            target = staged / relative
            if target.is_file() or target.is_symlink():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(str(target))
        return temporary
    except Exception:
        shutil.rmtree(str(temporary), ignore_errors=True)
        raise


def swap_restore(root: Path, staged_parent: Path) -> str:
    staged = staged_parent / "qspec"
    current = root / ".quinoto-spec"
    rollback = staged_parent / "rollback"
    if current.is_symlink():
        raise BackupError(".quinoto-spec/ cannot be a symlink during restore")
    try:
        if current.exists() or current.is_symlink():
            os.replace(str(current), str(rollback))
        os.replace(str(staged), str(current))
    except Exception:
        if rollback.exists() and not current.exists():
            os.replace(str(rollback), str(current))
        raise
    shutil.rmtree(str(staged_parent), ignore_errors=True)
    return str(current)


def restore_backup(root: Path, store: Path, value: str, confirmed: bool) -> Dict[str, Any]:
    if not confirmed:
        raise BackupError("restore requires --yes")
    store = store.resolve()
    ensure_store_outside_source(root, store)
    backup = resolve_backup(store, value)
    verification = verify_backup(backup)
    manifest = read_json(backup / "manifest.json")
    safety = create_backup(root, store, "pre-restore")
    staged_parent = stage_restore(root, backup, manifest)
    try:
        restored_path = swap_restore(root, staged_parent)
    except Exception:
        shutil.rmtree(str(staged_parent), ignore_errors=True)
        raise
    return {
        "restored": True,
        "backup_id": verification["backup_id"],
        "path": restored_path,
        "safety_backup": safety["path"],
        "verified": verification,
    }


def cleanup_backups(store: Path, keep: int, dry_run: bool, confirmed: bool) -> Dict[str, Any]:
    if keep < 1:
        raise BackupError("keep must be at least 1")
    if not dry_run and not confirmed:
        raise BackupError("cleanup requires --yes or --dry-run")
    listed = list_backups(store)["backups"]
    removable = [item for item in listed[keep:] if item.get("path")]
    removed: List[str] = []
    for item in removable:
        path = Path(item["path"])
        if path.is_symlink() or not path.is_dir():
            continue
        if dry_run:
            removed.append(str(path))
        else:
            shutil.rmtree(str(path))
            removed.append(str(path))
    return {"dry_run": dry_run, "keep": keep, "removed": removed, "remaining": len(listed) - len(removed)}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QuinotoSpec verifiable backup engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify", "list", "restore", "cleanup"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--root", default=".")
        sub.add_argument("--json", action="store_true", dest="as_json")
        sub.add_argument("--store")
        if command == "create":
            sub.add_argument("--type", default="full", choices=BACKUP_TYPES)
        if command in {"verify", "restore"}:
            sub.add_argument("--backup", required=True)
        if command == "restore":
            sub.add_argument("--yes", action="store_true")
        if command == "cleanup":
            sub.add_argument("--keep", type=int, default=5)
            sub.add_argument("--dry-run", action="store_true")
            sub.add_argument("--yes", action="store_true")
    return parser.parse_args(argv)


def output_human(command: str, result: Dict[str, Any]) -> None:
    print("QuinotoSpec Backup: " + command)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    store = resolve_store(root, args.store)
    try:
        if args.command == "create":
            result = create_backup(root, store, args.type)
        elif args.command == "verify":
            result = verify_backup(resolve_backup(store, args.backup))
        elif args.command == "list":
            result = list_backups(store)
        elif args.command == "restore":
            result = restore_backup(root, store, args.backup, args.yes)
        else:
            result = cleanup_backups(store, args.keep, args.dry_run, args.yes)
        code = 0
    except VerificationError as error:
        result = {"ok": False, "error": str(error), "error_type": "verification"}
        code = 1
    except BackupError as error:
        result = {"ok": False, "error": str(error), "error_type": "operational"}
        code = 2
    except (OSError, ValueError) as error:
        result = {"ok": False, "error": str(error), "error_type": "operational"}
        code = 2
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        output_human(args.command, result)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
