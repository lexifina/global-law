#!/usr/bin/env python3
"""Link each Shepardized/Songer case to exactly one corpus decision by reporter citation, checked by court and year.

Inputs: work/shepardized.tsv, work/songer96.tsv (year), work/fed_nodes.tsv.
Output: results/links.tsv  (casenum, citation key, songer circuit, songer date, link status, node, node court repo,
        node date, node name, candidates).
Link status:
  linked            exactly one decision at the citation whose court and year agree
  linked_by_date    several decisions at the citation agree on court and year; exactly one has the exact Songer date
  not_in_corpus     no decision with that citation
  court_mismatch    decision(s) at the citation, none in the Songer circuit
  year_mismatch     decision(s) at the citation in the circuit, none in the Songer year
  several_on_page   more than one decision still fits (never guessed)
  bad_citation      the Shepardized citation field cannot be parsed
Never guesses: anything else than the two "linked" statuses is unlinked.
"""
import collections
import csv
import datetime
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "work")
R = os.path.join(HERE, "results")
CIT = re.compile(r"^\s*0*(\d+)\s*f\s*(2d|3d)\s*0*(\d+)\s*$", re.I)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def main():
    os.makedirs(R, exist_ok=True)
    year96 = {r["casenum"]: r["year"] for r in rows(os.path.join(W, "songer96.tsv"))}
    cand = collections.defaultdict(list)
    with open(os.path.join(W, "fed_nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            cand[p[0]].append(p)
    stat = collections.Counter()
    out = open(os.path.join(R, "links.tsv"), "w", encoding="utf-8", newline="\n")
    out.write("casenum\tcite_key\tsonger_circuit\tsonger_date\tlink\tnode\tnode_repo\tnode_date\tnode_name\tn_candidates\n")
    for r in rows(os.path.join(W, "shepardized.tsv")):
        cn = r["casenum"]
        m = CIT.match(r["citation"])
        circ = r["circuit"]
        repo = "cadc" if circ == "0" else "ca" + circ
        if int(cn) >= 20001:
            d = ""
            if r["decision_date"]:
                d = (datetime.date(1960, 1, 1) + datetime.timedelta(days=int(float(r["decision_date"])))).strftime("%Y%m%d")
        else:
            y = year96.get(cn, "")
            d = "%s%02d%02d" % (y, int(r["month"] or 0), int(r["day"] or 0)) if y else ""
        year = d[:4]
        node = nrepo = ndate = nname = ""
        if not m:
            link, n = "bad_citation", 0
            key = r["citation"]
        else:
            key = "%d f%s %d" % (int(m.group(1)), m.group(2).lower(), int(m.group(3)))
            c = cand.get(key, [])
            n = len(c)
            if not c:
                link = "not_in_corpus"
            else:
                c1 = [x for x in c if x[4] == repo]
                c2 = [x for x in c1 if x[3][:4] == year and year]
                if not c1:
                    link = "court_mismatch"
                elif not c2:
                    link = "year_mismatch"
                elif len(c2) == 1:
                    link, pick = "linked", c2[0]
                else:
                    c3 = [x for x in c2 if x[3] == d]
                    if len(c3) == 1:
                        link, pick = "linked_by_date", c3[0]
                    else:
                        link = "several_on_page"
                if link.startswith("linked"):
                    node, nrepo, ndate, nname = pick[1], pick[4], pick[3], pick[6]
                elif c:
                    nrepo = ",".join(sorted({x[4] for x in c}))
                    ndate = ",".join(sorted({x[3] for x in c}))
        stat[link] += 1
        out.write("\t".join([cn, key, circ, d, link, node, nrepo, ndate, nname, str(n)]) + "\n")
    out.close()
    tot = sum(stat.values())
    with open(os.path.join(R, "link_summary.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("link\tcases\tshare\n")
        for k, v in stat.most_common():
            o.write("%s\t%d\t%.4f\n" % (k, v, v / tot))
            print(k, v, "%.2f%%" % (100 * v / tot))
        o.write("total\t%d\t1\n" % tot)
    print("total", tot)


if __name__ == "__main__":
    main()
