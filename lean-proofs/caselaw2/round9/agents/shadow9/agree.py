"""Signal agreement of the remand-docket bridge (cand.pkl) against non-key truths: the order's own "Reported below"
citation (memo rbn), the round-8 history-string bridges (bridge_links.tsv) and list "Reported below" rows.
    python -X utf8 round9/agents/shadow9/agree.py [cand.pkl]
"""
import collections, json, os, pickle, sys
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OD = os.path.join(C2, "round8", "agents", "orderdock")
NL = chr(10)


def truths():
    tr = collections.defaultdict(set)
    orders = pickle.load(open(os.path.join(C2, "round6/history/rules/memo/work/orders.pkl"), "rb"))["orders"]
    for o in orders:
        for t, *_ in o.get("rbn", []):
            if t is not None:
                tr[o["n"]].add(int(t))
    for i, l in enumerate(open(os.path.join(OD, "work", "bridge_links.tsv"), encoding="utf-8")):
        if i:
            p = l.rstrip(NL).split("\t")
            tr[int(p[0])].add(int(p[1]))
    for l in open(os.path.join(OD, "rows_listcite.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        tr[r["by"]].add(int(r["target"]))
    return tr


def pick(rec, rule):
    T = rec["T"]
    if rule == "R0_unique_capT":
        c = [n for n, t in T.items() if t["capT"]]
    elif rule == "R0b_unique_capT_capB":
        c = [n for n, t in T.items() if t["capT"] and t["capB"]]
    elif rule == "R1_capT_citeBT":
        c = [n for n, t in T.items() if t["capT"] and t["citeBT"]]
    elif rule == "R2_capT_reason":
        c = [n for n, t in T.items() if t["capT"] and t["reason"]]
    elif rule == "R3_capT_latest":
        c = [n for n, t in T.items() if t["capT"] and t["latest"]]
    elif rule == "R4_capT_latest_(cite|reason)":
        c = [n for n, t in T.items() if t["capT"] and t["latest"] and (t["citeBT"] or t["reason"])]
    elif rule == "R5_capT_capB_latest_(cite|reason)":
        c = [n for n, t in T.items() if t["capT"] and t["capB"] and t["latest"] and (t["citeBT"] or t["reason"])]
    elif rule == "R6_capT_capB_latest_cite":
        c = [n for n, t in T.items() if t["capT"] and t["capB"] and t["latest"] and t["citeBT"]]
    else:
        c = list(T)
    return c[0] if len(c) == 1 else None


RULES = ["any_unique", "R0_unique_capT", "R0b_unique_capT_capB", "R1_capT_citeBT", "R2_capT_reason",
         "R3_capT_latest", "R4_capT_latest_(cite|reason)", "R5_capT_capB_latest_(cite|reason)",
         "R6_capT_capB_latest_cite"]


def main():
    cand = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "work", "cand.pkl"), "rb"))
    tr = truths()
    for rule in RULES:
        c = collections.Counter()
        for o, rec in cand.items():
            t = pick(rec, rule)
            if t is None:
                continue
            g = "vac" if rec["kind"] in ("vacated", "reversed") else "oth"
            c["linked_" + g] += 1
            if o in tr:
                c["right_" if t in tr[o] else "wrong_"] += 1
        r, w = c["right_"], c["wrong_"]
        print("%-36s linked vac %4d oth %4d | vs truth right %4d wrong %3d  %.3f" % (
            rule, c["linked_vac"], c["linked_oth"], r, w, r / max(1, r + w)))


if __name__ == "__main__":
    main()
