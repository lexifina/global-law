"""Round 5: the OLD, burned lists (SCDB, CRS / Constitution Annotated) for a variant, by class. NON-BLIND figures:
these lists were used in rounds 1-4 to diagnose and direct work; they are reported as a secondary number only.

    python round5/old_by_class.py <name>        (reads round5/out/<name>, round5/stage/<name>; or `baseline`)

Same definitions as tools/caselaw2/eval/score.py: a pair (Y, X) is "admitted" when a status-changing treatments row
by Y on X passed the checker. score.py counts explicit rows only (it skips the implicit tier). Here the admitted
set is built per class from classes.tsv (round-5 output): selfAnnounced, operativeWords (explicit rows), recognised
(witness rows the recognised check passed). At-risk witness rows are never admitted.
SCDB: a flagged decision is found when it is the Y of an admitted pair whose X is a Supreme Court decision.
CRS: a listed pair is found when it is admitted.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(HERE)
csv.field_size_limit(1 << 30)


def rows(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    name = sys.argv[1]
    if name == "baseline":
        out, data = os.path.join(C2, "out"), os.path.join(C2, "data")
    else:
        out, data = os.path.join(HERE, "out", name), os.path.join(HERE, "stage", name)
    scotus = {int(r["node"]) for r in rows(os.path.join(HERE, "gold_fresh", "work", "scotus_meta.tsv"))}
    cls = {}
    cp = os.path.join(out, "classes.tsv")
    if os.path.exists(cp):
        for r in rows(cp):
            cls[r["id"]] = (r["class"], r["verdict"])
    certs = {}
    with open(os.path.join(out, "certs.tsv"), encoding="utf-8") as f:
        next(f)
        for l in f:
            p = l.rstrip("\n").split("\t")
            if p[0].startswith("treatment"):
                certs[p[1]] = p[2]
    CH = {"overruled", "disapproved", "recededFrom", "abrogated"}
    by_class = {"selfAnnounced": set(), "operativeWords": set(), "recognised": set()}
    tp = os.path.join(data, "treatments.pre_round5.tsv") if name == "baseline" and os.path.exists(
        os.path.join(data, "treatments.pre_round5.tsv")) else os.path.join(data, "treatments.tsv")
    with open(tp, encoding="utf-8") as f:
        for l in f:
            p = l.rstrip("\n").split("\t")
            if len(p) < 16 or p[4] not in CH:
                continue
            res = certs.get(p[0], "")
            if not res.startswith("ok"):
                continue
            if p[0] in cls:
                c = cls[p[0]][0]
            else:  # round-4 output: no classes.tsv; explicit rows only, by the quote
                if p[7] != "1" or p[14].endswith(":implicit"):
                    continue
                q = p[11].lower()
                c = "selfAnnounced" if any(w in q for w in ("overrul", "disapprov", " reced", "abrogat")) else "operativeWords"
            if c in by_class:
                by_class[c].add((int(p[1]), int(p[2])))
    gold = os.path.join(C2, "gold")
    sc = rows(os.path.join(gold, "scdb.tsv"))
    flagged = {int(r["node"]) for r in sc if r["precedentAlteration"] == "1" and int(r["node"]) >= 0}
    allsc = {int(r["node"]) for r in sc if int(r["node"]) >= 0}
    cr = rows(os.path.join(gold, "crs_overruled.tsv"))

    def ii(s):
        try:
            return int(s)
        except ValueError:
            return -1
    sets = {"current_table": lambda r: r["in_current"] == "1",
            "2016_express": lambda r: r["in_2016"] == "1" and r["expressly_2016"] == "1",
            "2016_all": lambda r: r["in_2016"] == "1"}
    res = {}
    combos = [("selfAnnounced",), ("selfAnnounced", "operativeWords"), ("selfAnnounced", "operativeWords", "recognised"),
              ("selfAnnounced", "recognised"), ("recognised",), ("operativeWords",)]
    for combo in combos:
        adm = set()
        for c in combo:
            adm |= by_class[c]
        acting = {y for (y, x) in adm if y in allsc and x in scotus}
        d = {"scdb_found": len(flagged & acting), "scdb_flagged": len(flagged), "scdb_acting": len(acting),
             "scdb_acting_flagged": len(acting & flagged)}
        for k, sel in sets.items():
            pr = [(ii(r["by_node"]), ii(r["target_node"])) for r in cr if sel(r)]
            pr = [p for p in pr if p[0] >= 0 and p[1] >= 0]
            d["crs_" + k] = [sum(p in adm for p in pr), len(pr)]
        res["+".join(combo)] = d
    res["_rows"] = {c: len(v) for c, v in by_class.items()}
    os.makedirs(os.path.join(HERE, "results", name), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", name, "old_by_class.json"), "w", encoding="utf-8", newline="\n"),
              indent=1)
    print("admitted pairs by class:", res["_rows"])
    for k, d in res.items():
        if k.startswith("_"):
            continue
        print("%-45s SCDB %d/%d (precision %d/%d)  CRS current %d/%d  2016 express %d/%d  2016 all %d/%d" % (
            k, d["scdb_found"], d["scdb_flagged"], d["scdb_acting_flagged"], d["scdb_acting"],
            *d["crs_current_table"], *d["crs_2016_express"], *d["crs_2016_all"]))


if __name__ == "__main__":
    main()
