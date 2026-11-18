#!/usr/bin/env python3
"""Compare the Lean PAP (detax --pap) with the BMF interface responses.

compare_pap.py cases.jsonl lean_out.jsonl BMFDIR
"""
import json, os, re, sys
from collections import Counter

FIELDS = ["LSTLZZ", "SOLZLZZ", "BK", "VFRB", "WVFRB"]

def bmf(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    out = {m.group(1): m.group(2) for m in re.finditer(r'<ausgabe name="(\w+)" value="([^"]*)"', s)}
    errs = re.findall(r'status="(?!ok)[^"]*"', s)
    return out, errs, s

def main():
    cases = {c["id"]: c for c in map(json.loads, open(sys.argv[1])) if c}
    lean = {o["id"]: o for o in map(json.loads, open(sys.argv[2]))}
    d = sys.argv[3]
    n = ok = 0
    diff = Counter()
    bad = []
    for cid, c in cases.items():
        p = os.path.join(d, cid + ".xml")
        if not os.path.exists(p):
            continue
        b, errs, raw = bmf(p)
        if not b:
            bad.append((cid, "no outputs", raw[:300]))
            continue
        n += 1
        l = lean[cid]
        mism = [f for f in FIELDS if f in b and int(b[f]) != int(l[f])]
        if mism:
            for f in mism:
                diff[f] += 1
            bad.append((cid, {f: (int(b[f]), l[f]) for f in mism}, c))
        else:
            ok += 1
    print(f"compared {n}: identical on {FIELDS}: {ok}; mismatches by field: {dict(diff)}")
    for x in bad[:40]:
        print(x)

if __name__ == "__main__":
    main()
