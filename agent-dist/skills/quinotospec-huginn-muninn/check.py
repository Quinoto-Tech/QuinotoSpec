#!/usr/bin/env python3
"""Huginn & Muninn — calculo real de entropia sin LLM.

Uso:
    check.py [service-path] [--json]

Sin --json imprime un encabezado legible y el resumen JSON.
Con --json emite UNICAMENTE el objeto JSON (para parsing en CI).

Las formulas siguen agent-dist/skills/quinotospec-entropy-calculator/SKILL.md:
    H_size    = entropia de Shannon normalizada de la distribucion de tamanos
    H_testing = 1 - (test_files / source_files)
    H_total   = 0.5 * H_size + 0.5 * H_testing
    S_proxy   = 0.5 * archivos_grandes + 0.5 * densidad_de_ramas
    S_final   = 0.6 * H_total + 0.4 * S_proxy
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

CODE_EXTENSIONS = {".py", ".sh", ".js", ".ts", ".go", ".rs", ".java"}
DOC_EXTENSIONS = {".md", ".yaml", ".yml"}
EXTENSIONS = CODE_EXTENSIONS | DOC_EXTENSIONS

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".quinoto-spec-backups",
    ".venv",
    "venv",
    "dist",
    "vendor",
}

BRANCH_TOKENS = ("if ", "if(", "for ", "for(", "while ", "while(", "case ", "except", "elif ", "catch")
BRANCH_DENSITY_CAP = 0.25
LARGE_FILE_LINES = 300


def is_excluded(relative_parts):
    for part in relative_parts:
        if part in EXCLUDED_DIRS:
            return True
        if part.startswith("temp_"):
            return True
    return False


def collect_files(root):
    """Devuelve [(path, line_count, is_test)] para archivos analizables."""
    collected = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        try:
            relative = current.relative_to(root)
        except ValueError:
            relative = Path(".")
        dirnames[:] = sorted(
            name for name in dirnames if not is_excluded(relative.parts + (name,))
        )
        for name in sorted(filenames):
            if is_excluded(relative.parts):
                continue
            suffix = Path(name).suffix.lower()
            if suffix not in EXTENSIONS:
                continue
            if name.startswith("temp_"):
                continue
            path = current / name
            try:
                if not path.is_file() or path.is_symlink():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
            relative_path = str(relative / name) if str(relative) != "." else name
            collected.append(
                {
                    "path": relative_path,
                    "lines": lines,
                    "text": text,
                    "code": suffix in CODE_EXTENSIONS,
                    "test": is_test_file(relative_path),
                }
            )
    return collected


def is_test_file(relative_path):
    lowered = relative_path.lower()
    parts = lowered.split(os.sep)
    if any(part in {"tests", "test", "__tests__", "spec", "specs"} for part in parts[:-1]):
        return True
    stem = os.path.splitext(parts[-1])[0]
    return (
        stem.startswith("test_")
        or stem.endswith("_test")
        or stem.endswith("_spec")
        or stem.endswith(".test")
        or stem.endswith(".spec")
        or "test" in stem
    )


def normalized_shannon(counts, buckets=4):
    """Entropia de Shannon normalizada a [0, 1] sobre `buckets` categorias."""
    total = sum(counts)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in counts:
        if count <= 0:
            continue
        probability = count / total
        entropy -= probability * math.log2(probability)
    ceiling = math.log2(buckets) if buckets > 1 else 1.0
    return max(0.0, min(1.0, entropy / ceiling))


def size_buckets(files):
    buckets = [0, 0, 0, 0]
    for item in files:
        lines = item["lines"]
        if lines <= 50:
            buckets[0] += 1
        elif lines <= 100:
            buckets[1] += 1
        elif lines <= LARGE_FILE_LINES:
            buckets[2] += 1
        else:
            buckets[3] += 1
    return buckets


def branch_density(files):
    code_files = [item for item in files if item["code"]]
    total_lines = sum(item["lines"] for item in code_files)
    if total_lines <= 0:
        return 0.0
    branches = 0
    for item in code_files:
        for token in BRANCH_TOKENS:
            branches += item["text"].count(token)
    return min(1.0, (branches / total_lines) / BRANCH_DENSITY_CAP)


def analyze(root):
    files = collect_files(root)
    buckets = size_buckets(files)
    h_size = normalized_shannon(buckets, buckets=4)

    code_files = [item for item in files if item["code"]]
    test_files = [item for item in code_files if item["test"]]
    source_total = len(code_files)
    h_testing = max(0.0, min(1.0, 1.0 - (len(test_files) / max(1, source_total))))

    large_ratio = (
        sum(1 for item in files if item["lines"] > LARGE_FILE_LINES) / len(files)
        if files
        else 0.0
    )
    s_proxy = max(
        0.0,
        min(1.0, 0.5 * min(1.0, large_ratio) + 0.5 * branch_density(files)),
    )

    h_total = round(0.5 * h_size + 0.5 * h_testing, 2)
    s_final = round(0.6 * h_total + 0.4 * s_proxy, 2)

    if s_final < 0.35:
        classification = "baja"
        status = "HEALTHY"
    elif s_final < 0.65:
        classification = "media"
        status = "WARNING"
    else:
        classification = "alta"
        status = "CRITICAL"

    return {
        "S_final": s_final,
        "H_total": h_total,
        "S_proxy": round(s_proxy, 2),
        "H_size": round(h_size, 2),
        "H_testing": round(h_testing, 2),
        "classification": classification,
        "status": status,
        "files_analyzed": len(files),
        "target": str(root),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Huginn & Muninn — metricas de entropia sin LLM"
    )
    parser.add_argument("service_path", nargs="?", default=".", help="Directorio a analizar")
    parser.add_argument("--json", action="store_true", help="Emitir solo JSON")
    args = parser.parse_args(argv)

    root = Path(args.service_path)
    if not root.exists() or not root.is_dir():
        print(
            json.dumps({"error": "service path not found: " + str(root)})
            if args.json
            else "ERROR: service path not found: " + str(root),
            file=sys.stderr if not args.json else sys.stdout,
        )
        return 1

    report = analyze(root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print("Huginn: analizando {}".format(root))
        print("Muninn: {} archivos analizados".format(report["files_analyzed"]))
        print(
            "  H_size={H_size} H_testing={H_testing} H_total={H_total}".format(**report)
        )
        print(
            "  S_proxy={S_proxy} S_final={S_final} ({classification} / {status})".format(
                **report
            )
        )
        print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
