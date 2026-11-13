"""Step 3a: opinion excerpts for each candidate (node, family): the start of the court's own opinion (facts) plus
windows around the family holdings' sentences. -> factors_work/excerpts.jsonl"""
import json, os, sys
from common import WORK
import text, core  # holdings helpers (path set by common)
HEAD, WIN, CAP = 5000, 1200, 13000

def excerpt(t, holds):
    parts, _ = core.court_parts(t)
    if parts:
        b = parts[0][0]
    else:
        b = 0
    spans = [(b, min(len(t), b + HEAD))]
    for h in holds:
        spans.append((max(0, h["start"] - WIN), min(len(t), h["end"] + WIN)))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    out, n = [], 0
    for s, e in merged:
        seg = t[s:e]
        if n + len(seg) > CAP:
            seg = seg[:max(0, CAP - n)]
        out.append(seg); n += len(seg)
        if n >= CAP:
            break
    return "\n[...]\n".join(out)

CANDS = [json.loads(l) for l in open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8")]
BY = {}
for c in CANDS:
    BY.setdefault(c["node"], []).append(c)

def fn(nid, raw):
    t = text.norm_text(raw)
    return [(c["node"], c["family"], excerpt(t, c["holdings"])) for c in BY[nid]]

if __name__ == "__main__":
    n = 0
    with open(os.path.join(WORK, "excerpts.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for res in text.map_nodes(list(BY), fn, procs=8):
            if isinstance(res, tuple) and res and res[0] == "__error__":
                print("err", res, file=sys.stderr); continue
            for node, fam, ex in res:
                f.write(json.dumps({"node": node, "family": fam, "excerpt": ex}) + "\n"); n += 1
    print("excerpts", n)
