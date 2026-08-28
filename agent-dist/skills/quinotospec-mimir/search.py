#!/usr/bin/env python3
import json, re, pathlib, math, sys, collections
ROOT = pathlib.Path(__file__).resolve().parents[3]
IDX = ROOT / ".quinoto-spec/mimir/index.json"
if not IDX.exists():
    print("No encontrado: corre index.py --reindex"); sys.exit(1)
data=json.load(open(IDX))
chunks=data["chunks"]
inv=data["inv"]
N=len(chunks)
avgdl=sum(len(re.findall(r'\w+', c["text"])) for c in chunks)/N if N else 0
query=" ".join(sys.argv[1:]) if len(sys.argv)>1 else "TOTP"
qterms=re.findall(r'\w+', query.lower())
scores=collections.Counter()
k1=1.5; b=0.75
for term in qterms:
    if term not in inv: continue
    df=len(inv[term])
    idf=math.log((N-df+0.5)/(df+0.5)+1)
    for idx in inv[term]:
        tf=re.findall(r'\w+', chunks[idx]["text"].lower()).count(term)
        dl=len(re.findall(r'\w+', chunks[idx]["text"]))
        denom=tf + k1*(1-b+b*dl/avgdl) if avgdl else tf+k1
        scores[idx]+= idf * (tf*(k1+1)/denom)
for idx, sc in scores.most_common(3):
    c=chunks[idx]
    print(f"[{sc:.2f}] {c['file']}:{c['line']} \n  {c['text'][:200].replace(chr(10),' ')}\n")
