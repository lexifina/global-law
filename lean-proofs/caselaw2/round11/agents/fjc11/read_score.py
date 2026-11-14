"""fjc11: score the reader answers against the rows (reader-side only; no key).
    python -X utf8 read_score.py work/read [work/feat_n2.tsv]
right = same case, under review, disposition compatible with the row's kind and scope (as the round-10 type-B judge:
kind equal; or scope != all and disposition 'affirmed_in_part_reversed_or_vacated_in_part' for reversed / vacated)."""
import collections, csv, glob, json, os, sys

STATUS = ("reversed", "vacated", "modified")
COMPAT = {"affirmed": {"affirmed"}, "reversed": {"reversed"}, "vacated": {"vacated", "reversed"},
          "modified": {"modified"}, "reviewDismissed": {"appeal_dismissed"}}


def wilson(k, n, z=1.959964):
    if not n:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return ((c - a) / d, (c + a) / d)


def main():
    d = sys.argv[1]
    items = {r["item"]: r for r in csv.DictReader(open(os.path.join(d, "items.tsv"), encoding="utf-8"), delimiter="\t")}
    feat = {}
    if len(sys.argv) > 2:
        feat = {(r["by"], r["target"]): r for r in csv.DictReader(open(sys.argv[2], encoding="utf-8"), delimiter="\t")}
    ans = {}
    for f in sorted(glob.glob(os.path.join(d, "ans_*.jsonl"))):
        for l in open(f, encoding="utf-8"):
            l = l.strip()
            if l:
                a = json.loads(l)
                ans[a["item"]] = a
    tot = collections.defaultdict(collections.Counter)
    errs = []
    for it, r in items.items():
        a = ans.get(it)
        if not a:
            tot["missing"]["n"] += 1
            continue
        link = a["same_case"] == "yes" and a["under_review"] == "yes"
        disp = a["disposition"]
        kind_ok = disp in COMPAT.get(r["kind"], set()) or (
            r["scope"] != "all" and r["kind"] in ("reversed", "vacated") and disp.startswith("affirmed_in_part"))
        scope_ok = r["scope"] != "all" or a["whole"] != "no"
        right = link and kind_ok and scope_ok
        st = "status" if r["kind"] in STATUS else "nonstatus"
        for g in (r["group"], "ALL", st, r["group"] + ":" + st):
            tot[g]["n"] += 1
            tot[g]["link"] += link
            tot[g]["right"] += right
        if not right:
            f = feat.get((r["by"], r["target"]), {})
            errs.append((r["group"], r["kind"], r["scope"], r["ties"], r["flags"], f.get("named", ""),
                         f.get("latest", ""), a["same_case"], a["under_review"], disp, a["whole"], a["note"][:110],
                         r["by"], r["target"]))
    for g in sorted(tot):
        t = tot[g]
        lo, hi = wilson(t["right"], t["n"])
        print("%-18s right %3d/%3d = %.3f [%.3f, %.3f]  link %d" % (g, t["right"], t["n"], t["right"] / max(1, t["n"]),
                                                                   lo, hi, t["link"]))
    for e in sorted(errs):
        print("ERR", *e, sep=" | ")


if __name__ == "__main__":
    main()
