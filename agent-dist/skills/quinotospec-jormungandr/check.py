#!/usr/bin/env python3
"""Jormungandr -- deteccion de ciclos en el DAG de schema.yaml (algoritmo de Kahn)."""
from __future__ import annotations

import pathlib
import re
import sys
from collections import defaultdict, deque


def parse_schema_artifacts(text: str) -> tuple[list[str], dict[str, list[str]]]:
    ids: list[str] = []
    requires: dict[str, list[str]] = {}
    cur: str | None = None
    in_requires = False
    in_artifacts = True

    for line in text.splitlines():
        m_top = re.match(r"^([A-Za-z0-9_-]+):\s*(?:.*)?$", line)
        if m_top:
            key = m_top.group(1)
            cur = None
            in_requires = False
            if key == "artifacts":
                in_artifacts = True
            elif key not in ("name", "version", "contract_version", "description"):
                in_artifacts = False
            continue
        if not in_artifacts:
            continue
        m_id = re.match(r"\s*-\s+id:\s*(\S+)", line)
        if m_id:
            cur = m_id.group(1)
            ids.append(cur)
            requires[cur] = []
            in_requires = False
            continue
        if cur is None:
            continue
        if re.match(r"\s*requires:\s*\[\s*\]\s*$", line):
            in_requires = False
            continue
        m_inline = re.match(r"\s*requires:\s*\[(.*?)\]", line)
        if m_inline:
            requires[cur] = [r.strip() for r in m_inline.group(1).split(",") if r.strip()]
            in_requires = False
            continue
        if re.match(r"\s*requires:\s*$", line):
            in_requires = True
            continue
        if in_requires:
            m_req = re.match(r"\s*-\s+(\S+)", line)
            if m_req:
                requires[cur].append(m_req.group(1))
                continue
            in_requires = False

    return ids, requires


def check_schema_dag(schema_path: pathlib.Path) -> tuple[bool, list[str], list[str]]:
    text = pathlib.Path(schema_path).read_text(encoding="utf-8", errors="ignore")
    ids, requires = parse_schema_artifacts(text)
    if not ids:
        return False, [], []

    indeg: dict[str, int] = defaultdict(int)
    g: dict[str, list[str]] = defaultdict(list)
    for nid in ids:
        for r in requires.get(nid, []):
            g[r].append(nid)
            indeg[nid] += 1
            indeg.setdefault(r, 0)

    q = deque([n for n in ids if indeg[n] == 0])
    visited: list[str] = []
    while q:
        n = q.popleft()
        visited.append(n)
        for nb in g[n]:
            indeg[nb] -= 1
            if indeg[nb] == 0:
                q.append(nb)

    if len(visited) == len(ids):
        return False, visited, ids
    cycle = [n for n in ids if n not in visited]
    return True, cycle, ids


def main() -> int:
    schema = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "agent-dist/templates/schema-template.yaml")
    if not schema.exists():
        print(f"ERROR: schema file not found: {schema}")
        return 1
    has_cycle, nodes, ids = check_schema_dag(schema)
    if not ids:
        print(f"ERROR: no artifact nodes ('id:') found in {schema}")
        return 1
    if not has_cycle:
        print(f"OK: DAG aciclico ({len(ids)} nodos, orden: {' -> '.join(nodes)})")
        return 0
    print(f"CYCLE: {' -> '.join(nodes)} -> {nodes[0]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
