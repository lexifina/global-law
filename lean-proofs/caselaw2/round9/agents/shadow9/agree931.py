"""Signal agreement on the round-8 remand-docket links (round8/agents/orderdock/work/remand_links.tsv, 931 orders):
per signal, how often it holds, and agreement with non-key truths (own Reported below / history strings / list
rows) when it holds. Also K9 (v2) on the same orders. Writes work/agree931.txt.
"""
import collections, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agree as A  # noqa: E402
import rules9 as R  # noqa: E402
C2 = R.C2
NL = chr(10)
links = []
for i, l in enumerate(open(os.path.join(C2, "round8/agents/orderdock/work/remand_links.tsv"), encoding="utf-8")):
    if i:
        p = l.rstrip(NL).split("\t")
        links.append((int(p[0]), int(p[1]), p[4]))
cand = pickle.load(open(os.path.join(HERE, "work", "cand.pkl"), "rb"))
link = pickle.load(open(os.path.join(HERE, "work", "link.pkl"), "rb"))
tr = A.truths()
R.set_join(True, True)
c = collections.Counter()
for o, t, kind in links:
    g = "gvr" if kind in ("vacated", "reversed") else "other"
    rec = cand.get(o, {}).get("T", {}).get(t)
    sig = {"all": True}
    if rec:
        sig.update({"capB": bool(rec["capB"]), "citeBT": bool(rec["citeBT"]), "reason": bool(rec["reason"]),
                    "latest": rec["latest"]})
    sig["bothSides"] = R.both_sides(o, t)
    lk = link.get(o)
    if lk and t in lk["T"]:
        bs = lk["T"][t]["B"].values()
        sig["cue"] = any(s["cue"] for s in bs)
        sig["tieO"] = any(R.ties(s) for s in bs)
        sig["odocket"] = any(s["odocket"] for s in bs)
        sig["odate"] = any(s["odate"] for s in bs)
    k9 = R.pick(lk, "K9", o) if lk else None
    sig["K9_same"] = k9 == t
    sig["K9_other"] = k9 is not None and k9 != t
    for k, v in sig.items():
        if v:
            c[(g, k, "n")] += 1
            if o in tr:
                c[(g, k, "right" if t in tr[o] else "wrong")] += 1
out = ["group\tsignal\tholds\tvs truth right\twrong"]
for g in ("gvr", "other"):
    for k in ("all", "capB", "citeBT", "reason", "latest", "bothSides", "cue", "tieO", "odocket", "odate",
              "K9_same", "K9_other"):
        out.append("%s\t%s\t%d\t%d\t%d" % (g, k, c[(g, k, "n")], c[(g, k, "right")], c[(g, k, "wrong")]))
txt = NL.join(out) + NL
open(os.path.join(HERE, "work", "agree931.txt"), "w", encoding="utf-8", newline=NL).write(txt)
print(txt)
