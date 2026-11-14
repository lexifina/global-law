"""Reader packs (diagnosis): post-2013 GVR orders of the h0 misses (diag_h0.tsv, v9c) that C2/C6 do not link, with the
order's own text and corpus candidates for the decision below (caption-token decisions of the court(s) the order
names, 1..1,095 days before; nearest first). No key field is written into a pack: the candidates come from the
corpus only and are not marked.
    python -X utf8 round10/agents/shadow10/readpacks.py   -> readers/pack_<k>.md, readers/index.tsv (not for readers)
"""
import collections
import os
import pickle
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cap10  # noqa: E402

R, M, L, C2 = cap10.R, cap10.M, cap10.L, cap10.C2
OUT = os.path.join(HERE, "readers")
os.makedirs(OUT, exist_ok=True)
cand = pickle.load(open(os.path.join(HERE, "work", "cap_cand.pkl"), "rb"))
tokidx = pickle.load(open(os.path.join(cap10.S9W, "tokidx.pkl"), "rb"))
courts = M.Courts()
F = L.Facts()
orders = R.orders()
pool = []
with open(os.path.join(C2, "round9/agents/shadow9/work/diag_h0.tsv"), encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        era, stage = p[2], p[7].split("|")[0]
        ords = [int(x) for x in p[8].split(";") if x.strip().isdigit()]
        if era != "post2013" or stage not in ("no_signal", "cap_only_right", "cap_only_other"):
            continue
        o = next((x for x in ords if x in orders and orders[x]["kind"] in ("vacated", "reversed")), None)
        if o is None:
            continue
        rec = cand.get(o)
        if rec and any(cap10.pick(rec, r) is not None for r in ("C6_fullname_unique_nosib", "C2_unique_nosib")):
            continue
        pool.append(o)
random.seed(10)
pool = sorted(set(pool))
pick = random.sample(pool, min(30, len(pool)))
print("pool", len(pool), "picked", len(pick))
items = []
for o in pick:
    od = orders[o]
    ids = set()
    for k in od["courts"]:
        if k is not None:
            ids.update(courts.group.get(k, ()))
    ocap = M.toks(" ".join(od["caps"]) or od["title"])
    oo = M.ordinal(od["date"])
    cs = set()
    for c in ids:
        for w in ocap:
            for n in tokidx.get((c, w), ()):
                dn = int(F.date[n])
                if dn < od["date"] and 0 < oo - M.ordinal(dn) <= 1095:
                    cs.add(n)
    # rank: both-sides first, then nearest in time; at most 10
    bs = set((cand.get(o) or {"T": {}})["T"])
    cs = sorted(cs, key=lambda n: (n not in bs, -int(F.date[n])))[:10]
    items.append((o, cs))
texts = L.fetch_texts([o for o, _ in items] + [n for _, cs in items for n in cs])
packs = [items[i:i + 10] for i in range(0, len(items), 10)]
with open(os.path.join(OUT, "index.tsv"), "w", encoding="utf-8", newline="\n") as fi:
    for k, pk in enumerate(packs, 1):
        lines = ["# Reader pack %d" % k, ""]
        for j, (o, cs) in enumerate(pk, 1):
            od = orders[o]
            t = texts.get(o, ("", ""))[1]
            q0, q1 = od["disp"]
            lines += ["## Item %d.%d" % (k, j), "", "### Supreme Court order (node %d, %d)" % (o, od["date"]), "",
                      "```", t[max(0, q0 - 1500):q1 + 1200], "```", "", "### Candidate decisions", ""]
            for i, n in enumerate(cs, 1):
                r = L.node_row(n)
                tx = texts.get(n, ("", ""))[1]
                lines += ["#### Candidate %s (node %d, court %s, date %d)" % (chr(64 + i), n, L.Facts().court_name(int(F.court[n])) if hasattr(L.Facts(), "court_name") else int(F.court[n]), int(F.date[n])),
                          "", "Title: " + (r[6] if len(r) > 6 else ""), "", "```", tx[:1800], "```", ""]
                fi.write("%d\t%d\t%d\t%s\t%d\n" % (k, j, o, chr(64 + i), n))
        open(os.path.join(OUT, "pack_%d.md" % k), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("packs", len(packs))
