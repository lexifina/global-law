"""shadow9 diagnosis of v8e Shadow Docket h0 misses (diagnosis only: reads the h0 cases file, sanctioned by
DESIGN9 0.2(b); nothing here feeds a reader, linker or candidate generator).

    python -X utf8 round9/agents/shadow9/diag.py   -> work/diag_h0.tsv, work/diag_h0.txt (counts only)
"""
import collections
import csv
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
MEMO = os.path.join(HIST, "rules", "memo")
OD = os.path.join(C2, "round8", "agents", "orderdock")
sys.path.insert(0, HIST)
sys.path.insert(0, MEMO)
import r6lib as L  # noqa: E402
import memolib as M  # noqa: E402

WORK = os.path.join(HERE, "work")
NL = chr(10)


def ndk(s):
    s = s.strip().upper().replace("NO.", "").replace(" ", "")
    for ch in ("–", "—", "‑", "‐"):
        s = s.replace(ch, "-")
    return s.strip(".;:")


def main():
    rows = list(csv.DictReader(open(os.path.join(C2, "round8/results/v8e/bench/shadow_docket.h0.cases.tsv"),
                                    encoding="utf-8"), delimiter="\t"))
    miss = [r for r in rows if r["class"] == "NEG" and r["model_class"] != "NEG_HIST"]
    orders = pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]
    by_dk = collections.defaultdict(list)
    for o in orders:
        for d in (o["docket"] or "").replace(",", " ").replace("&", " ").split():
            by_dk[ndk(d)].append(o)
    remand = {}
    for i, l in enumerate(open(os.path.join(OD, "work", "remand_links.tsv"), encoding="utf-8")):
        if i:
            p = l.rstrip(NL).split("\t")
            remand[int(p[0])] = int(p[1])
    cap = collections.defaultdict(set)
    for p in (os.path.join(MEMO, "rows.jsonl"), os.path.join(C2, "round7", "agents", "orderhead", "v2", "rows.jsonl")):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if ":cap-" in r["rule"]:
                cap[r["by"]].add(r["target"])
    F = L.Facts()
    st = collections.Counter()
    out = []
    for r in miss:
        node = int(r["node"])
        y = r["order_date"][:4]
        era = "post2013" if r["order_date"] >= "20130101" else ("2005" if y == "2005" else "pre2013")
        dks = [ndk(d) for d in r["sc_dockets"].replace(",", " ").replace(";", " ").replace("|", " ").split()]
        os_ = []
        for d in dks:
            for o in by_dk.get(d, ()):
                if abs(int(o["date"]) - int(r["order_date"])) <= 10 and o not in os_:
                    os_.append(o)
        if r["sc_in_corpus"] != "yes":
            stage = "gap_not_in_corpus"
        elif not os_:
            stage = "order_not_parsed"
        else:
            o = os_[0]
            kinds = {x["kind"] for x in os_}
            parts = {x["part"] for x in os_}
            rm = [remand.get(x["n"]) for x in os_ if x["n"] in remand]
            cp = set().union(*[cap.get(x["n"], set()) for x in os_])
            if not (kinds & {"vacated", "reversed"}):
                stage = "order_kind_" + "+".join(sorted(kinds))
            elif node in rm:
                stage = "remand_right" + ("+cap" if node in cp else "")
            elif rm:
                stage = "remand_other" + ("+cap_right" if node in cp else "")
            elif node in cp:
                stage = "cap_only_right"
            elif cp:
                stage = "cap_only_other"
            else:
                stage = "no_signal"
            stage += "|" + "+".join(sorted(parts))
        st[(era, stage.split("|")[0])] += 1
        st[("part", stage)] += 1
        out.append((r["node"], r["order_date"], era, r["court"], r["court_label"], r["sub"], r["model_class"],
                    stage, ";".join(str(x["n"]) for x in os_)))
    with open(os.path.join(WORK, "diag_h0.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("node\torder_date\tera\tcourt\tcourt_label\tsub\tmodel_class\tstage\torders" + NL)
        for x in out:
            f.write("\t".join(x) + NL)
    with open(os.path.join(WORK, "diag_h0.txt"), "w", encoding="utf-8", newline=NL) as f:
        for k in sorted(st):
            f.write("%s\t%s\t%d" % (k[0], k[1], st[k]) + NL)
    for k in sorted(st):
        print(k, st[k])


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    main()
