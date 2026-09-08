#!/usr/bin/env python3
"""Bifrost -- federacion multi-repo (alcance acotado, sin GitHub real).

Uso:
    python3 bifrost.py --init   [--root PATH] [--repos path1:role1,path2:role2,...] [--name NOMBRE]
    python3 bifrost.py --status [--root PATH]
    python3 bifrost.py --sync   [--root PATH]

Alcance: --sync usa `git notes` (push/fetch de refs/notes/quinotospec-events)
contra el remoto `origin` de cada repo listado en federation.yaml. No requiere
GitHub real -- funciona igual contra un remoto local (bare repo) o cualquier
remoto git configurado. Ver tests/test-nordic-skills.sh para un ejemplo
end-to-end con repos efimeros (git init locales, sin red).

Solo stdlib. Unicas llamadas de red posibles son los `git push/fetch` explicitos
de --sync (heredan la configuracion de remotos de cada repo).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

NOTES_REF = "refs/notes/quinotospec-events"


def resolve_root(argv):
    args = list(argv)
    root = None
    if "--root" in args:
        i = args.index("--root")
        if i + 1 < len(args):
            root = args[i + 1]
            del args[i:i + 2]
        else:
            del args[i:i + 1]
    if root is None:
        root = os.environ.get("QUINOTOSPEC_BIFROST_ROOT") or os.environ.get("BIFROST_ROOT")
    if root is None:
        root = "."
    return Path(root).resolve(), args


def sha1_of(path: Path):
    try:
        return hashlib.sha1(path.read_bytes()).hexdigest()
    except OSError:
        return None


def federation_path(root: Path) -> Path:
    return root / ".quinoto-spec" / "federation.yaml"


def parse_federation(root: Path):
    """Parser minimo (sin pyyaml) para el formato fijo que genera --init."""
    fpath = federation_path(root)
    if not fpath.exists():
        return None
    data = {"repos": []}
    cur = None
    section = None
    for raw in fpath.read_text().splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if not raw.startswith(" "):
            m = re.match(r'^(\w+):\s*(.*)$', raw)
            if m:
                key, val = m.groups()
                section = key
                if key != "repos":
                    data[key] = val if val else {}
            continue
        if section == "repos":
            m_item = re.match(r'^\s*-\s*path:\s*(.+)$', raw)
            if m_item:
                if cur:
                    data["repos"].append(cur)
                cur = {"path": m_item.group(1).strip()}
                continue
            m_field = re.match(r'^\s+(\w+):\s*(.+)$', raw)
            if m_field and cur is not None:
                cur[m_field.group(1)] = m_field.group(2).strip()
        elif section == "bridge":
            m_field = re.match(r'^\s+(\w+):\s*(.+)$', raw)
            if m_field:
                if not isinstance(data.get("bridge"), dict):
                    data["bridge"] = {}
                data["bridge"][m_field.group(1)] = m_field.group(2).strip()
    if cur:
        data["repos"].append(cur)
    return data


def build_federation_yaml(name, repos):
    lines = [
        "# .quinoto-spec/federation.yaml",
        f"federation: {name}",
        "version: 1",
        "repos:",
    ]
    for r in repos:
        lines.append(f"  - path: {r['path']}")
        lines.append(f"    role: {r['role']}")
        lines.append(f"    schema: {r.get('schema', '.quinoto-spec/schema.yaml')}")
        if r.get("schema_sha1"):
            lines.append(f"    schema_sha1: {r['schema_sha1']}")
    lines += [
        "bridge:",
        "  discovery: stack-discovery  # consolida 01-stack-profile.md de cada repo",
        "  specs: federated            # specs/<domain>/spec.md por repo, indice federado",
        "  changelog: aggregated       # changelog-view --federated",
    ]
    return "\n".join(lines) + "\n"


def cmd_init(root: Path, rest):
    repos_arg = None
    if "--repos" in rest:
        i = rest.index("--repos")
        if i + 1 < len(rest):
            repos_arg = rest[i + 1]
    name = "quinoto-falange"
    if "--name" in rest:
        i = rest.index("--name")
        if i + 1 < len(rest):
            name = rest[i + 1]

    repos = []
    if repos_arg:
        for item in repos_arg.split(","):
            parts = item.split(":")
            path = parts[0].strip()
            role = parts[1].strip() if len(parts) > 1 else Path(path).name
            repo_root = (root / path).resolve()
            schema_file = repo_root / ".quinoto-spec" / "schema.yaml"
            repos.append({
                "path": path,
                "role": role,
                "schema": ".quinoto-spec/schema.yaml",
                "schema_sha1": sha1_of(schema_file) if schema_file.exists() else None,
            })
    else:
        repos.append({"path": "../peer-repo", "role": "peer", "schema": ".quinoto-spec/schema.yaml", "schema_sha1": None})

    content = build_federation_yaml(name, repos)
    fpath = federation_path(root)
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(content)
    print(f"Bifrost --init: {fpath} creado con {len(repos)} repo(s).")
    if not repos_arg:
        print("  (placeholder generado -- edita 'path'/'role' o corre con --repos path1:role1,path2:role2)")
    return 0


def count_proposals(repo_root: Path):
    props_dir = repo_root / ".quinoto-spec" / "proposals"
    if not props_dir.exists():
        return None, None
    total = 0
    en_curso = 0
    for p in props_dir.glob("*/proposal.md"):
        if "_archived" in p.parts:
            continue
        total += 1
        text = p.read_text(errors="ignore")
        if re.search(r'\*\*Estado\*\*:?\s*.*En Curso', text):
            en_curso += 1
    return total, en_curso


def latest_s_final(repo_root: Path):
    tiwaz_dir = repo_root / ".quinoto-spec" / "tiwaz-rune"
    if not tiwaz_dir.exists():
        return None
    reports = sorted(tiwaz_dir.glob("*.json"))
    if not reports:
        return None
    try:
        data = json.loads(reports[-1].read_text())
        return data.get("s_final")
    except (json.JSONDecodeError, OSError):
        return None


def notes_last_sync(repo_root: Path):
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%cr", NOTES_REF],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def cmd_status(root: Path, rest):
    fed = parse_federation(root)
    if not fed:
        print(f"Bifrost --status: no existe {federation_path(root)}. Corre --init primero.")
        return 1

    print(f"Federacion: {fed.get('federation', '?')} (v{fed.get('version', '?')})")
    print("Repo | S_final | Propuestas | Drift | Bridge")
    any_warn = False
    for r in fed.get("repos", []):
        repo_root = (root / r["path"]).resolve()
        role = r.get("role", r["path"])

        if not repo_root.exists():
            print(f"{role} | N/D | N/D | MISSING ({r['path']} no existe) | -")
            any_warn = True
            continue

        s_final = latest_s_final(repo_root)
        s_final_s = f"{s_final:.2f}" if isinstance(s_final, (int, float)) else "N/D"

        total, en_curso = count_proposals(repo_root)
        if total is None:
            props_s = "sin .quinoto-spec/proposals/"
        elif en_curso:
            props_s = f"{total} activas ({en_curso} en curso)"
        else:
            props_s = f"{total} activas"

        schema_file = repo_root / r.get("schema", ".quinoto-spec/schema.yaml")
        recorded_sha1 = r.get("schema_sha1")
        if not schema_file.exists():
            drift = "MISSING schema"
            any_warn = True
        elif recorded_sha1 and sha1_of(schema_file) != recorded_sha1:
            drift = "WARN contract drift"
            any_warn = True
        else:
            drift = "OK"

        sync_info = notes_last_sync(repo_root)
        bridge_s = f"synced {sync_info}" if sync_info else "sync needed"
        if not sync_info:
            any_warn = True

        print(f"{role} | {s_final_s} | {props_s} | {drift} | {bridge_s}")

    if any_warn:
        print("\n⚠️  Hay repos con drift, schema faltante o sin sincronizar -- revisar antes de mergear cambios cross-repo.")
    return 1 if any_warn else 0


def git_run(repo_root: Path, args):
    try:
        return subprocess.run(["git", "-C", str(repo_root)] + args, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as e:
        return subprocess.CompletedProcess(args, 1, stdout="", stderr=str(e))


def _last_line(text: str) -> str:
    lines = [ln for ln in (text or "").strip().splitlines() if ln.strip()]
    return lines[-1] if lines else "error desconocido"


def classify_push(result):
    if result.returncode == 0:
        return "OK"
    err = result.stderr or result.stdout or ""
    if "does not match any" in err or "src refspec" in err:
        return "SKIP (sin notes locales para enviar)"
    return f"ERR: {_last_line(err)}"


def classify_fetch(result):
    if result.returncode == 0:
        return "OK"
    return f"ERR: {_last_line(result.stderr or result.stdout or '')}"


def sync_one(repo_root: Path, label: str):
    if not (repo_root / ".git").exists():
        return f"{label} | push: - | fetch: - | (no es un repo git, omitido)"
    push = git_run(repo_root, ["push", "origin", NOTES_REF])
    fetch = git_run(repo_root, ["fetch", "origin", f"{NOTES_REF}:{NOTES_REF}"])
    return f"{label} | push: {classify_push(push)} | fetch: {classify_fetch(fetch)}"


def cmd_sync(root: Path, rest):
    fed = parse_federation(root)
    if not fed:
        print(f"Bifrost --sync: no existe {federation_path(root)}. Corre --init primero.")
        return 1

    print(f"Bifrost --sync: sincronizando {NOTES_REF} vía git notes\n")
    results = []
    if (root / ".git").exists():
        results.append(sync_one(root, "self (.)"))
    else:
        results.append("self (.) | (root no es un repo git, omitido)")

    for r in fed.get("repos", []):
        repo_root = (root / r["path"]).resolve()
        results.append(sync_one(repo_root, r.get("role", r["path"])))

    for line in results:
        print(line)
    return 0 if all("ERR:" not in r for r in results) else 1


def main():
    root, rest = resolve_root(sys.argv[1:])
    if "--init" in rest:
        sys.exit(cmd_init(root, rest))
    if "--status" in rest:
        sys.exit(cmd_status(root, rest))
    if "--sync" in rest:
        sys.exit(cmd_sync(root, rest))
    print("Uso: bifrost.py --init|--status|--sync [--root PATH] [--repos p1:r1,p2:r2] [--name NOMBRE]")
    sys.exit(1)


if __name__ == "__main__":
    main()
