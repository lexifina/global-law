"""scdb8: what the base build v3 and the round-6/7 SC linkers know about given Supreme Court decisions (diagnosis).

    python -X utf8 peek8.py <sc node> [<sc node> ...] [--below <node>]   (--below: a lower node to look for)

Reads only corpus-side files: round7/stage/v3/history.tsv, round7/out/v3/certs.tsv, round7/out/v3/status.tsv (only
for the nodes asked), the round-7 b4sc diag (round7/agents/b4sc/work/diag.jsonl.gz), round-7 b4sc rows. No key file.
"""
import gzip, json, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")


def load_hist_by(nodes):
    out = {n: [] for n in nodes}
    tg = {n: [] for n in nodes}
    with open(os.path.join(C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            by, t = int(p[2]), int(p[1])
            if by in out:
                out[by].append(p)
            if t in tg:
                tg[t].append(p)
    return out, tg


def certs(ids):
    r = {}
    with open(os.path.join(C2, "round7", "out", "v3", "certs.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[0] == "history" and p[1] in ids:
                r[p[1]] = p[2]
    return r


def diag(nodes):
    cache = os.path.join(WORK, "diag7_index.json")
    if os.path.exists(cache):
        idx = json.load(open(cache, encoding="utf-8"))
        return {n: idx.get(str(n)) for n in nodes}
    os.makedirs(WORK, exist_ok=True)
    idx = {}
    with gzip.open(os.path.join(C2, "round7", "agents", "b4sc", "work", "diag.jsonl.gz"), "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            idx[str(d["n"])] = d
    json.dump(idx, open(cache, "w", encoding="utf-8"))
    return {n: idx.get(str(n)) for n in nodes}


def main():
    args = sys.argv[1:]
    below = None
    if "--below" in args:
        i = args.index("--below")
        below = int(args[i + 1])
        del args[i:i + 2]
    nodes = [int(x) for x in args]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    F = L.Facts()
    hb, ht = load_hist_by(nodes + ([below] if below else []))
    ids = {p[0] for v in hb.values() for p in v} | {p[0] for v in ht.values() for p in v}
    cv = certs(ids)
    dg = diag(nodes)
    for n in nodes:
        r = L.node_row(n)
        print("=" * 100)
        print("SC", n, F.date[n], r[6][:90])
        d = dg.get(n)
        if d:
            print(" r7 reason:", d.get("reason"), "| reasons:", d.get("reasons"), "| ph_end:", d.get("ph_end"))
            print(" disp:", (d.get("disp_text") or "")[:300])
            for c in d.get("cands", []) or []:
                try:
                    tt = L.node_row(c["j"])[6][:60]
                except Exception:
                    tt = "?"
                print("  cand", c["j"], c["date"], F.court_name(c["court"])[:50], "|", tt, "| occ", c["occ"][:3])
        else:
            print(" r7: no diag (memorandum order or not stored)")
        for p in hb[n]:
            print("  ROW by", p[0], "target", p[1], F.court_name(F.court[int(p[1])])[:40], p[4], p[5], p[12], "cert=", cv.get(p[0]))
        if below:
            for p in ht.get(below, []):
                print("  ROW on below", p[0], "by", p[2], p[4], p[5], p[12], "cert=", cv.get(p[0]))


if __name__ == "__main__":
    main()
