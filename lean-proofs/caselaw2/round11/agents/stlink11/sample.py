"""stlink10 step 1: stratified diagnosis sample (seeded) of state court-of-last-resort / intermediate-decision pairs
for opus readers (corpus text only).

    python -X utf8 sample.py         -> read1/items_<k>.md, read1/sample.tsv (strata; not shown to readers)
"""
import collections, csv, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import BO, L  # noqa: E402

NL = chr(10)
OUT = os.path.join(HERE, "read1")
SEED = 20261114
PLAN = [  # (stratum, filter, n)
    ("cited_unmarked_nocourt", lambda r: r["how"] == "cited" and r["mark"] == "-" and r["r6"] in ("cand_no_court_phrase", "cand_no_design_cue"), 9),
    ("cited_unmarked_guard", lambda r: r["how"] == "cited" and r["mark"] == "-" and r["r6"] in ("cand_earlier_proceeding", "cand_later_events", "cand_interlocutory_ruling"), 9),
    ("cited_unmarked_named_other", lambda r: r["how"] == "cited" and r["mark"] == "-" and r["r6"] in ("cand_named_other_case", "cand_one_side_caption"), 6),
    ("cited_unmarked_signal_hist", lambda r: r["how"] == "cited" and r["mark"] == "-" and r["r6"] in ("cand_signal", "cand_history_after_cite", "cand_history_before_cite"), 4),
    ("cited_unmarked_after", lambda r: r["how"] == "cited" and r["mark"] == "-" and r["r6"].startswith("after_"), 4),
    ("cited_marked", lambda r: r["how"] == "cited" and r["mark"] != "-", 6),
    ("uncited_unique", lambda r: r["how"] == "uncited", 14),
    ("trial_named", lambda r: r["how"] == "trialnamed", 8),
]


def main():
    random.seed(SEED)
    rows = list(csv.DictReader(open(os.path.join(HERE, "work", "pairs.tsv"), encoding="utf-8"), delimiter="\t"))
    rows = [r for r in rows if r["how"] == "cited"]
    rows += list(csv.DictReader(open(os.path.join(HERE, "work", "uncited_unique.tsv"), encoding="utf-8"), delimiter="\t"))
    # trial-named: judgment line names only the trial court negatively, a cited A decision cap 2 in the window
    recs = {}
    for f in os.listdir(os.path.join(HERE, "work", "pop")):
        if f.endswith(".jsonl"):
            for l in open(os.path.join(HERE, "work", "pop", f), encoding="utf-8"):
                r = json.loads(l)
                if r["ka"] is None and r["kt"] in ("reversed", "vacated", "modified"):
                    cs = [c for c in r["cands"] if c["cap"] >= 2]
                    if len(cs) == 1:
                        rows.append({"by": str(r["n"]), "target": str(cs[0]["j"]), "how": "trialnamed", "sys": str(r["sys"]),
                                     "decade": str(r["date"] // 100000 * 10), "mark": "?", "r6": cs[0].get("r6", ""),
                                     "tag": r["tag"]})
    picked = []
    for name, flt, k in PLAN:
        pool = [r for r in rows if flt(r)]
        # stratify by state x decade: round-robin over (sys, decade) cells in seeded random order
        cells = collections.defaultdict(list)
        for r in pool:
            cells[(r["sys"], r["decade"])].append(r)
        keys = sorted(cells)
        random.shuffle(keys)
        for c in keys:
            random.shuffle(cells[c])
        got = []
        while len(got) < k and any(cells[c] for c in keys):
            for c in keys:
                if cells[c] and len(got) < k:
                    got.append(cells[c].pop())
        for r in got:
            picked.append((name, r))
        print(name, len(pool), len(got))
    random.shuffle(picked)
    BO.init()
    F, N = BO.G["F"], BO.G["N"]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "sample.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("item\tstratum\tby\ttarget\tsys\tdecade\tr6\tmark\n")
        for i, (s, r) in enumerate(picked):
            f.write("\t".join([str(i), s, r["by"], r["target"], r["sys"], r["decade"], r.get("r6", ""), r.get("mark", "")]) + NL)
    per = 10
    for k in range(0, len(picked), per):
        out = ["# Reader pack %d" % (k // per), ""]
        for i in range(k, min(k + per, len(picked))):
            _s, r = picked[i]
            n, j = int(r["by"]), int(r["target"])
            rn, rj = L.node_row(n), L.node_row(j)
            out.append("## Item %d" % i)
            out.append("- Opinion D: node %d — %s — %s — %s (%s)" % (n, rn[6], BO.court_at(int(F.court[n]), int(F.date[n]))[0], rn[4], rn[5]))
            out.append("- Decision T: node %d — %s — %s — %s (%s)" % (j, rj[6], BO.court_at(int(F.court[j]), int(F.date[j]))[0], rj[4], rj[5]))
            out.append("")
        with open(os.path.join(OUT, "items_%d.md" % (k // per)), "w", encoding="utf-8", newline=NL) as f:
            f.write(NL.join(out) + NL)
    print("items", len(picked))


if __name__ == "__main__":
    main()
