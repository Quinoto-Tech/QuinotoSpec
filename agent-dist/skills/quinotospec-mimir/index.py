#!/usr/bin/env python3
import pathlib, hashlib, json, re, collections
ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / ".quinoto-spec"
DST = SRC / "mimir" / "index.json"
# Demo index for package itself (since .quinoto-spec not in package, index agent-dist)
docs = list(ROOT.glob("agent-dist/**/*.md"))
chunks=[]
for p in docs[:20]:
    text = p.read_text(errors="ignore")
    # chunk by heading
    parts = re.split(r'(?m)^##+ ', text)
    for i, part in enumerate(parts[:3]):
        chunks.append({"file": str(p.relative_to(ROOT)), "line": i, "text": part[:500]})
DST.parent.mkdir(parents=True, exist_ok=True)
# simple inverted index
inv={}
for idx,ch in enumerate(chunks):
    toks = re.findall(r'\w+', ch["text"].lower())
    for t in set(toks):
        inv.setdefault(t, []).append(idx)
json.dump({"chunks": chunks, "inv": inv, "count": len(chunks)}, open(DST,"w"), indent=2)
print(f"Mimir indexed {len(chunks)} chunks -> {DST}")
