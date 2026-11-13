"""Pattern 5: splits the Supreme Court resolved, and lower courts that kept citing the losing side.

Spec.scotus_resolves_split: a later binding SCOTUS holding on the question resolves the split for every court it
binds, so a losing-side court of appeals holding is no longer law there (an abrogation, not always announced; the
runner's `atRisk contraryBinding` family, never a status change by itself, Spec §9 item 26).

  side   (LLM) for each SCOTUS decision in gold/splits_resolved.tsv with conflict nodes (statutory, conflict language),
         which of the cited court of appeals decisions answered the question the other way (losing side);
  cites  every later citation of a losing-side decision by a federal court (edges), with passages;
  split  (LLM) does the citing court rely on the losing side's answer to the resolved question without noting SCOTUS?

    python p5_splits.py side_prep  -> work/p5_side_in.jsonl
    python llm_run.py side work/p5_side_in.jsonl work/p5_side_out.jsonl
    python p5_splits.py cites      -> work/p5_in.jsonl
    python llm_run.py split work/p5_in.jsonl work/p5_out.jsonl
    python p5_splits.py score      -> data/p5_losing_side.tsv, data/p5_unresolved_splits.tsv
"""
import json, os, random, re, sys
from collections import Counter, defaultdict
import hcommon as C
import passages as P

random.seed(5)


def side_prep():
    rows = [r for r in C.read_tsv(os.path.join(C.GOLD, "splits_resolved.tsv"))
            if r[8] != "-" and r[9] == "1" and "conflictLanguage" in r[12]]
    nodes = {int(r[0]) for r in rows}
    conf = {int(x) for r in rows for x in r[8].split(",") if x.strip().isdigit()}
    meta = C.nodes(nodes | conf)
    texts = C.fetch({n: meta[n] for n in nodes if n in meta})
    with open(os.path.join(C.HWORK, "p5_side_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            n = int(r[0])
            t = texts.get(n)
            if not t:
                continue
            off = int(r[11]) if r[11].lstrip("-").isdigit() and int(r[11]) >= 0 else 0
            b = t
            k = b.find(r[10][:60]) if r[10] != "-" else -1
            k = k if k >= 0 else off
            cn = [int(x) for x in r[8].split(",") if x.strip().isdigit() and int(x) in meta]
            f.write(json.dumps(dict(hkey="side|%d" % n, node=n, name=meta[n]["name"], cite=meta[n]["cite"].split("|")[0],
                                    date=meta[n]["date"], usc=r[5], conflict_nodes=cn,
                                    conflict_cites=["%s, %s" % (meta[c]["name"][:50], meta[c]["cite"].split("|")[0]) for c in cn],
                                    opening=b[max(0, k - 2500):k + 2500], closing=b[-1500:])) + "\n")
    C.log("side rows", len(rows))


def cites():
    ins = [json.loads(l) for l in open(os.path.join(C.HWORK, "p5_side_in.jsonl"), encoding="utf-8")]
    outs = {json.loads(l)["key"]: json.loads(l)["ans"] for l in open(os.path.join(C.HWORK, "p5_side_out.jsonl"), encoding="utf-8")}
    losing = {}
    stats = Counter()
    for r in ins:
        a = outs.get(r["hkey"])
        if not a or "sides" not in a:
            continue
        for cn, cc in zip(r["conflict_nodes"], r["conflict_cites"]):
            cite = cc.split(", ")[-1].lower().replace(".", "")
            s = "unclear"
            for x in a["sides"]:
                xc = x["cite"].lower().replace(".", "")
                if cite and (cite in xc or xc in cite or cc.split(",")[0].lower()[:15] in x["cite"].lower()):
                    s = x["side"]
            stats[s] += 1
            if s == "losing":
                losing[cn] = dict(scotus=r["node"], scotus_name=r["name"], scotus_cite=r["cite"], scotus_date=r["date"],
                                  qa="Q: %s  A: %s" % (a["question"], a["answer"]))
    C.log("conflict nodes by side", stats, "losing", len(losing))
    lset = set(losing)
    citers = defaultdict(set)
    for x, y in C.iter_edges(want_cited=lset):
        citers[y].add(x)
    meta = C.nodes(set().union(*citers.values()) | lset)
    # status of the losing decisions in our runner output
    st = defaultdict(set)
    for r in C.read_tsv(os.path.join(C.OUT, "status.tsv")):
        if int(r[0]) in lset and r[1] == "-":
            st[int(r[0])].add(r[5])
    items = []
    for y, cs in citers.items():
        L = losing[y]
        for x in cs:
            m = meta.get(x)
            if not m or m["date"] <= L["scotus_date"]:
                continue
            if m["court2"] is None:
                continue
            items.append(dict(citing=x, cited=y, actor=L["scotus"], **L))
    C.log("later citations of losing-side decisions", len(items))
    out = os.path.join(C.HWORK, "p5_passages.jsonl")
    P.run(items, out, workers=8)
    ps = [json.loads(l) for l in open(out, encoding="utf-8")]
    meta = C.nodes({p["citing"] for p in ps} | {p["cited"] for p in ps})
    sel = [p for p in ps if p["hits"] > 0 and not p["ack_actor"] and not p["actor_any"]]
    C.log("located", sum(p["hits"] > 0 for p in ps), "silent (no SCOTUS cite anywhere)", len(sel))
    by = defaultdict(list)
    for p in sel:
        by[p["cited"]].append(p)
    pick = []
    for y, v in by.items():
        k = min(20, len(v))
        for p in random.sample(v, k):
            p["weight"] = len(v) / k
            pick.append(p)
    with open(os.path.join(C.HWORK, "p5_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for p in pick:
            mc, md = meta[p["citing"]], meta[p["cited"]]
            p.update(hkey="split|%s|%s" % (p["citing"], p["cited"]), cited_name=md["name"], cited_cite=md["cite"].split("|")[0],
                     cited_date=md["date"], citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0],
                     citing_court_name=mc["court_name"], citing_date=mc["date"],
                     cited_status=",".join(sorted(st.get(p["cited"], {"(no status row)"}))))
            f.write(json.dumps(p) + "\n")
    C.log("LLM rows", len(pick))


def score():
    ins = {json.loads(l)["hkey"]: json.loads(l) for l in open(os.path.join(C.HWORK, "p5_in.jsonl"), encoding="utf-8")}
    outs = [json.loads(l) for l in open(os.path.join(C.HWORK, "p5_out.jsonl"), encoding="utf-8")]
    rows = []
    for o in outs:
        a, r = o["ans"], ins[o["key"]]
        if "error" in a:
            continue
        rows.append([r["citing"], r["citing_name"][:70], r["citing_cite"], r["citing_date"], r["citing_court_name"],
                     r["cited"], r["cited_name"][:60], r["cited_cite"], r["scotus"], r["scotus_name"][:50],
                     r["scotus_date"], r["cited_status"], round(r["weight"], 2), a["side"], int(a["relies_on_point"]),
                     int(a["notes_scotus"]), int(a["zombie"]), a["reason"], r["qa"][:300]])
    rows.sort(key=lambda x: (-x[16], -x[3]))
    C.write_tsv(os.path.join(C.HUNT, "data", "p5_losing_side.tsv"), rows,
                ["citing", "citing_name", "citing_cite", "citing_date", "citing_court", "losing", "losing_name",
                 "losing_cite", "scotus", "scotus_name", "scotus_date", "losing_status_ours", "weight", "side_llm",
                 "relies", "notes_scotus", "zombie", "reason", "qa"])
    C.log("classified", len(rows), "zombies", sum(r[16] for r in rows), Counter((r[13], r[16]) for r in rows))


if __name__ == "__main__":
    {"side_prep": side_prep, "cites": cites, "score": score}[sys.argv[1]]()
