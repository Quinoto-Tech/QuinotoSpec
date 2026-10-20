#!/usr/bin/env python3
"""Norns — versionado atomico y deteccion de drift sin LLM.

Uso:
    norns.py --check [--root PATH] [--json]
    norns.py --to X.Y.Z --dry-run [--root PATH]
    norns.py --to X.Y.Z [--root PATH]

`--check` compara la version e inventario declarados contra el estado real del
repositorio y devuelve exit 0 (sin drift) o exit 1 (drift). No escribe nada.

`--to X.Y.Z --dry-run` valida el semver y lista los archivos/campos que se
actualizarian sin tocar disco.

`--to X.Y.Z` delega en scripts/update-version.sh.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
BADGE_RE = re.compile(r"badge/(version|workflows|skills|rules)-(\d+(?:\.\d+){0,2})-([a-z]+)")

COUNT_KEYS = ("workflows", "skills", "rules", "agents", "templates")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def fs_counts(root):
    inventory = root / "agent-dist"
    counts = {}
    workflows = inventory / "workflows"
    counts["workflows"] = len(list(workflows.glob("*.md"))) if workflows.is_dir() else 0
    skills = inventory / "skills"
    counts["skills"] = (
        len([p for p in skills.iterdir() if p.is_dir()]) if skills.is_dir() else 0
    )
    rules_file = inventory / "rules" / "quinotospec-rules.md"
    rules_text = read_text(rules_file) or ""
    counts["rules"] = sum(1 for line in rules_text.splitlines() if line.startswith("# "))
    agents = inventory / "agents"
    counts["agents"] = len(list(agents.glob("*.md"))) if agents.is_dir() else 0
    templates = inventory / "templates"
    if templates.is_dir():
        counts["templates"] = len(
            [
                p
                for p in templates.iterdir()
                if p.is_file() and p.suffix.lower() in {".md", ".yaml", ".yml"}
            ]
        )
    else:
        counts["templates"] = 0
    return counts


def add_check(checks, source, expected, actual):
    checks.append(
        {
            "source": source,
            "expected": str(expected),
            "actual": str(actual),
            "status": "OK" if str(expected) == str(actual) else "DRIFT",
        }
    )


def parse_manifest(root):
    text = read_text(root / "manifest.json")
    if text is None:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def template_references(root):
    """Extrae referencias `template:` no nulas de schema-template.yaml."""
    schema = root / "agent-dist" / "templates" / "schema-template.yaml"
    text = read_text(schema)
    if text is None:
        return None, []
    references = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("template:"):
            continue
        value = stripped.split(":", 1)[1].strip().strip("\"'")
        if not value or value in {"null", "~"}:
            continue
        references.append(value)
    return schema, references


def build_checks(root):
    checks = []
    expected_version = (read_text(root / ".version") or "").strip()

    manifest = parse_manifest(root)
    if manifest is None:
        checks.append(
            {
                "source": "manifest.json",
                "expected": "JSON object",
                "actual": "missing or invalid",
                "status": "DRIFT",
            }
        )
        manifest = {}

    add_check(checks, ".version", expected_version or "<missing>", (read_text(root / ".version") or "").strip() or "<missing>")
    add_check(checks, "manifest.json:version", expected_version, manifest.get("version", "<missing>"))

    install_text = read_text(root / "install.sh") or ""
    match = re.search(r'INSTALLER_VERSION="([^"]*)"', install_text)
    add_check(checks, "install.sh:INSTALLER_VERSION", expected_version, match.group(1) if match else "<missing>")

    plugin_text = read_text(root / ".cursor-plugin" / "plugin.json") or ""
    try:
        plugin_version = json.loads(plugin_text).get("version", "<missing>") if plugin_text else "<missing>"
    except json.JSONDecodeError:
        plugin_version = "<invalid>"
    add_check(checks, ".cursor-plugin/plugin.json:version", expected_version, plugin_version)

    counts = fs_counts(root)
    for key in COUNT_KEYS:
        add_check(checks, "manifest.json:" + key, counts[key], manifest.get(key, "<missing>"))

    for readme_name in ("README.md", "README_EN.md"):
        text = read_text(root / readme_name) or ""
        badges = {}
        for name, value, _ in BADGE_RE.findall(text):
            badges.setdefault(name, value)
        add_check(checks, readme_name + ":badge version", expected_version, badges.get("version", "<missing>"))
        for key in ("workflows", "skills", "rules"):
            add_check(checks, readme_name + ":badge " + key, counts[key], badges.get(key, "<missing>"))

    arch_text = read_text(root / "docs" / "ARCHITECTURE.md") or ""
    arch_match = re.search(r"v(\d+\.\d+\.\d+) Hird Edition", arch_text)
    add_check(checks, "docs/ARCHITECTURE.md:release", expected_version, arch_match.group(1) if arch_match else "<missing>")

    changelog_text = read_text(root / "CHANGELOG.md") or ""
    has_changelog = bool(re.search(r"^## \[" + re.escape(expected_version) + r"\]", changelog_text, re.MULTILINE))
    add_check(checks, "CHANGELOG.md:section", expected_version, expected_version if has_changelog else "<missing>")

    roadmap_text = read_text(root / "V3_ROADMAP.md") or ""
    roadmap_match = re.search(r"\*\*Version actual:\*\*\s*(\d+\.\d+\.\d+)", roadmap_text)
    add_check(checks, "V3_ROADMAP.md:**Version actual:**", expected_version, roadmap_match.group(1) if roadmap_match else "<missing>")

    validate_text = read_text(root / "scripts" / "validate-all.sh") or ""
    expected_counts = re.search(r"EXPECTED_COUNTS=\((.*?)\)", validate_text, re.DOTALL)
    declared = {}
    if expected_counts:
        for key, value in re.findall(r"\"?([a-z]+):(\d+)\"?", expected_counts.group(1)):
            declared[key] = int(value)
    for key in COUNT_KEYS:
        add_check(
            checks,
            "scripts/validate-all.sh:EXPECTED_COUNTS " + key,
            counts[key],
            declared.get(key, "<missing>"),
        )

    schema, references = template_references(root)
    templates_dir = root / "agent-dist" / "templates"
    if schema is None:
        checks.append(
            {
                "source": "agent-dist/templates/schema-template.yaml",
                "expected": "readable",
                "actual": "missing",
                "status": "DRIFT",
            }
        )
    else:
        for reference in references:
            add_check(
                checks,
                "schema-template.yaml:template " + reference,
                "exists",
                "exists" if (templates_dir / reference).is_file() else "missing",
            )

    return checks, expected_version


def render_table(checks):
    headers = ("Fuente", "Esperado", "Actual", "Estado")
    rows = [(c["source"], c["expected"], c["actual"], c["status"]) for c in checks]
    widths = [len(h) for h in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    separator = " | ".join("-" * width for width in widths)
    lines = [" | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)), separator]
    for row in rows:
        lines.append(" | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
    return "\n".join(lines)


def mode_check(root, as_json):
    checks, expected_version = build_checks(root)
    drifts = [item for item in checks if item["status"] != "OK"]
    if as_json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "version": expected_version,
                    "passed": not drifts,
                    "checks": checks,
                    "drift_count": len(drifts),
                },
                ensure_ascii=False,
            )
        )
    else:
        print("Norns --check: version esperada {}".format(expected_version or "<missing>"))
        print(render_table(checks))
        print("")
        if drifts:
            print("DRIFT: {} desfase(s) detectado(s)".format(len(drifts)))
        else:
            print("OK: no drift")
    return 1 if drifts else 0


def mode_to(root, target, dry_run):
    update_script = root / "scripts" / "update-version.sh"
    if not update_script.is_file():
        print("ERROR: scripts/update-version.sh not found under " + str(root), file=sys.stderr)
        return 1
    if dry_run:
        checks, current = build_checks(root)
        print("[DRY-RUN] Norns would update {} -> {}".format(current or "<missing>", target))
        print("Files that would be rewritten:")
        for relative in (
            ".version",
            "manifest.json",
            ".cursor-plugin/plugin.json",
            "install.sh",
            "README.md",
            "README_EN.md",
            "docs/ARCHITECTURE.md",
            "V3_ROADMAP.md",
            "CHANGELOG.md",
            "scripts/validate-all.sh",
        ):
            print("  - " + relative)
        print("No files were modified ({} check(s) evaluated).".format(len(checks)))
        return 0
    completed = subprocess.run(
        ["bash", str(update_script), target],
        cwd=str(root),
        check=False,
    )
    return completed.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description="Norns — versionado atomico sin drift")
    parser.add_argument("--root", default=".", help="Raiz del repositorio")
    parser.add_argument("--check", action="store_true", help="Detectar drift sin escribir")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar cambios sin escribir")
    parser.add_argument("--to", metavar="X.Y.Z", help="Version destino (semver)")
    parser.add_argument("--json", action="store_true", help="Salida JSON (solo --check)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print("ERROR: root not found: " + str(root), file=sys.stderr)
        return 1

    if args.check:
        if args.to:
            print("ERROR: --check and --to are mutually exclusive", file=sys.stderr)
            return 2
        return mode_check(root, args.json)

    if args.to:
        if not SEMVER_RE.match(args.to):
            print("ERROR: invalid semver '{}' (expected X.Y.Z)".format(args.to), file=sys.stderr)
            return 2
        return mode_to(root, args.to, args.dry_run)

    parser.print_usage(sys.stderr)
    print("ERROR: use --check or --to X.Y.Z", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
