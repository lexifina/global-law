"""Pattern 4: a holding superseded by statute applied to conduct after the statute's effective date (two-date error).

Spec.appliesSupersededHolding: statusAtConduct = neg superseded, where the supersession reaches conduct from
retroactiveTo.getD effective (supersession_prospective). The runner evaluates it with conduct = the citing date (t = u),
so it can only see supersessions admitted with a holding-level issue (26 rows, all Ledbetter, 11th Cir.). Here the
targets are the Congress override lists (gold/congress_overrides.tsv: Christiansen & Eskridge; Hasen), the runner's
own superseded decisions, and the 11th Cir. Ledbetter; the conduct date is read from the citing opinion.

    python p4_superseded.py prep   -> work/p4_in.jsonl
    python llm_run.py super work/p4_in.jsonl work/p4_out.jsonl
    python p4_superseded.py score  -> data/p4_superseded.tsv
"""
import json, os, random, re, sys
from collections import Counter, defaultdict
import hcommon as C
import passages as P

random.seed(4)
# (effective, conduct_from) where the law's own text sets them (lawchanges.tsv rows read by hand; see STATUTES.md)
OVERRIDE_DATES = {
    "Pub. L. 111-2": (20090129, 20070528, "claims pending on or after 28 May 2007 (sec. 6)"),
    "Pub. L. 110-325": (20090101, 20090101, "effective 1 Jan 2009 (sec. 8); not retroactive"),
}
HOLDING = {
    6239607: "a Title VII pay-discrimination charge runs from the pay decision, not from each later paycheck",
    441098: "a Title VII pay-discrimination charge runs from the pay decision, not from each later paycheck",
    6186393: "'disability' is judged with mitigating measures (glasses, medication) taken into account",
    6186394: "'disability' is judged with mitigating measures taken into account",
    6186396: "'disability' is judged with mitigating measures (the body's own compensation) taken into account",
    6206740: "'substantially limits' and 'major life activities' are interpreted strictly to create a demanding standard",
    6157819: "'use' of a firearm under 18 U.S.C. 924(c) requires active employment",
    6239714: "'proceeds' in the money-laundering statute means profits, not receipts",
    6215948: "dilution under the FTDA requires actual dilution, not a likelihood of dilution",
    6199932: "a fee award requires a judgment or court-ordered consent decree (catalyst theory rejected)",
    6239720: "False Claims Act liability requires intent that the government itself pay the claim",
    6208254: "patent counterclaims do not give the Federal Circuit appellate jurisdiction (well-pleaded complaint)",
    6234032: "the FCA retaliation limitations period borrows the state limitations period",
    6171290: "a secured claim in Chapter 13 cramdown is valued at replacement value",
    6164595: "sentencing departures are reviewed for abuse of discretion",
}


def law_dates():
    d = defaultdict(list)
    for p in C.read_tsv(os.path.join(C.DATA, "lawchanges.tsv"), header=False):
        d[p[1]].append((int(p[4] or 0), int(p[5] or 0)))
    out = {}
    for law, v in d.items():
        eff = min(x[0] for x in v if x[0]) if any(x[0] for x in v) else 0
        rt = [x[1] for x in v if x[1] > 1]
        out[law] = (eff, min(rt) if rt else eff)
    return out


ACKRX = None


def prep():
    over = list(C.read_tsv(os.path.join(C.GOLD, "congress_overrides.tsv")))
    LD = law_dates()
    targets = {}
    for r in over:
        n = int(r[0]) if r[0].lstrip("-").isdigit() else -1
        if n < 0:
            continue
        law, title = r[4], r[5]
        if law in OVERRIDE_DATES:
            eff, cf, note = OVERRIDE_DATES[law]
        else:
            eff, cf = LD.get(law, (int(r[6]) * 10000 + 101, int(r[6]) * 10000 + 101))
            note = "lawchanges.tsv"
        targets[n] = dict(law="%s (%s)" % (title, law), effective=eff, conduct_from=cf, date_note=note,
                          title=title)
    targets[441098] = dict(targets[6239607])          # 11th Cir. Ledbetter, the runner's 26 findings
    tset = set(targets)
    citers = defaultdict(set)
    for a, b in C.iter_edges(want_cited=tset):
        citers[b].add(a)
    meta = C.nodes(set().union(*citers.values()) | tset)
    items = []
    for t, cs in citers.items():
        e = targets[t]["effective"]
        for c in cs:
            if c in meta and meta[c]["date"] > e:
                items.append(dict(citing=c, cited=t, actor=None, **targets[t]))
    C.log("citations after the effective date", len(items), Counter(meta[i["cited"]]["name"][:30] for i in items).most_common(40))
    out = os.path.join(C.HWORK, "p4_passages.jsonl")
    P.run(items, out, workers=8)
    ps = [json.loads(l) for l in open(out, encoding="utf-8")]
    meta = C.nodes({p["citing"] for p in ps} | {p["cited"] for p in ps})
    texts = None
    sel = []
    for p in ps:
        if p["hits"] <= 0:
            continue
        toks = [t for t in re.findall(r"[A-Z][A-Za-z]+", p["title"]) if t not in ("Act", "The", "And", "Of")][:3]
        rx = re.compile(r"supersed|overrid|overrode|amend|Pub\.? ?L|Congress|legislative(?:ly)? overrul|"
                        r"abrogat|in response to|" + "|".join(re.escape(t) for t in toks), re.I)
        p["ack"] = int(any(rx.search(w) for w in p["windows"]))
        sel.append(p)
    C.log("located", len(sel), "silent", sum(1 - p["ack"] for p in sel))
    # LLM: every silent passage, capped at 250 per target (random), plus 150 acknowledged at random (leak check)
    by = defaultdict(list)
    for p in sel:
        if not p["ack"]:
            by[p["cited"]].append(p)
    pick = []
    for t, v in by.items():
        k = min(250, len(v))
        for p in random.sample(v, k):
            p["stratum"], p["weight"] = "silent", len(v) / k
            pick.append(p)
    ackd = [p for p in sel if p["ack"]]
    for p in random.sample(ackd, min(150, len(ackd))):
        p["stratum"], p["weight"] = "ack", len(ackd) / min(150, len(ackd))
        pick.append(p)
    texts = C.fetch({p["citing"]: meta[p["citing"]] for p in pick})
    with open(os.path.join(C.HWORK, "p4_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for p in pick:
            mc, md = meta[p["citing"]], meta[p["cited"]]
            p.update(hkey="super|%s|%s" % (p["citing"], p["cited"]), holding=HOLDING.get(p["cited"], "(see the decision)"),
                     cited_name=md["name"], cited_cite=md["cite"].split("|")[0], cited_date=md["date"],
                     citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0], citing_court_name=mc["court_name"],
                     citing_date=mc["date"], head=C.body(texts.get(p["citing"], ""))[:1000])
            f.write(json.dumps(p) + "\n")
    C.log("LLM rows", len(pick))


def score():
    ins = {json.loads(l)["hkey"]: json.loads(l) for l in open(os.path.join(C.HWORK, "p4_in.jsonl"), encoding="utf-8")}
    outs = [json.loads(l) for l in open(os.path.join(C.HWORK, "p4_out.jsonl"), encoding="utf-8")]
    rows = []
    for o in outs:
        a, r = o["ans"], ins[o["key"]]
        if isinstance(a.get("error"), str):      # a failed call; the task's own field `error` is a boolean
            continue
        rows.append([r["citing"], r["citing_name"][:70], r["citing_cite"], r["citing_date"], r["citing_court_name"],
                     r["cited"], r["cited_name"][:60], r["law"], r["effective"], r["conduct_from"], r["stratum"],
                     round(r["weight"], 2), int(a["applies_old_rule"]), int(a["notes_statute"]), a["conduct_year"],
                     a["conduct_after_effective"], int(a["error"]), a["proposition"], a["reason"]])
    rows.sort(key=lambda x: (-x[16], x[5], -x[3]))
    C.write_tsv(os.path.join(C.HUNT, "data", "p4_superseded.tsv"), rows,
                ["citing", "citing_name", "citing_cite", "citing_date", "citing_court", "cited", "cited_name", "law",
                 "effective", "conduct_from", "stratum", "weight", "applies_old_rule", "notes_statute", "conduct_year",
                 "conduct_after_effective", "error", "proposition", "reason"])
    C.log("classified", len(rows), "errors", sum(r[16] for r in rows))
    C.log(Counter((r[6][:25], r[16]) for r in rows).most_common(40))


if __name__ == "__main__":
    {"prep": prep, "score": score}[sys.argv[1]]()
