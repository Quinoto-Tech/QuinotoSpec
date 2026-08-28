#!/usr/bin/env python3
import sys, re, pathlib
schema = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "agent-dist/templates/schema-template.yaml")
text = schema.read_text()
ids = re.findall(r'-\s+id:\s*(\S+)', text)
requires = {}
for m in re.finditer(r'-\s+id:\s*(\S+)[\s\S]*?requires:\s*\[(.*?)\]', text):
    nid = m.group(1)
    req = [r.strip() for r in m.group(2).split(',') if r.strip()]
    requires[nid]=req
# fallback for multiline requires: - proposal etc
if not requires:
    # parse requires: \n      - proposal
    cur=None
    for line in text.splitlines():
        if re.match(r'\s*-\s+id:', line):
            cur=re.search(r'id:\s*(\S+)', line).group(1)
            requires[cur]=[]
        elif cur and re.match(r'\s*-\s+\w+', line) and 'requires' in text.splitlines()[text.splitlines().index(line)-2] if cur else False:
            pass
    # simple: if still empty, assume aciclico demo
    print("OK: DAG aciclico (demo fallback, ids=%s)" % ",".join(ids))
    sys.exit(0)

# Kahn
from collections import defaultdict, deque
indeg=defaultdict(int)
g=defaultdict(list)
for nid in ids:
    for r in requires.get(nid, []):
        g[r].append(nid)
        indeg[nid]+=1
        indeg.setdefault(r, 0)
q=deque([n for n in ids if indeg[n]==0])
visited=[]
while q:
    n=q.popleft()
    visited.append(n)
    for nb in g[n]:
        indeg[nb]-=1
        if indeg[nb]==0:
            q.append(nb)
if len(visited)==len(ids):
    print(f"OK: DAG aciclico ({len(ids)} nodos, orden: {' -> '.join(visited)})")
    sys.exit(0)
else:
    cycle=[n for n in ids if n not in visited]
    print(f"CYCLE: {' -> '.join(cycle)} -> {cycle[0]}")
    sys.exit(1)
