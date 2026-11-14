"""Round 11: round10/old_by_class10.py on round-11 paths (round11/out, round11/stage, round11/results; nothing else
changed). Round 10: round9/old_by_class9.py on round-10 paths (nothing else
changed). Round 9: round8/old_by_class8.py on round-9 paths (nothing else
changed). Round 8: round7/old_by_class7.py on round-8 paths (nothing else
changed). Round 7: round5/old_by_class.py on round-7 paths (the round-5 file is not changed). The OLD, burned lists (SCDB,
CRS / Constitution Annotated) for a variant, by class. NON-BLIND figures: reported as a secondary number only.

    python round11/old_by_class11.py <name>    (reads round11/out/<name>, round11/stage/<name>;
                                                writes round11/results/<name>/old_by_class.json)

Same definitions as round 5: a pair (Y, X) is admitted when a status-changing treatments row by Y on X passed the
checker; the admitted set is built per class from classes.tsv: selfAnnounced, operativeWords (explicit rows),
recognised (witness rows the recognised check passed). At-risk witness rows and round-7 `doctrine` rows (always
demoted, never negative: DESIGN7 2.4) are never admitted; the doctrine rows are counted in `_rows`.
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
    out, data = os.path.join(HERE, "out", name), os.path.join(HERE, "stage", name)
    scotus = {int(r["node"]) for r in rows(os.path.join(C2, "round5", "gold_fresh", "work", "scotus_meta.tsv"))}
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
    by_class = {"selfAnnounced": set(), "operativeWords": set(), "recognised": set(), "doctrine": set()}
    with open(os.path.join(data, "treatments.tsv"), encoding="utf-8") as f:
        for l in f:
            p = l.rstrip("\n").split("\t")
            if len(p) < 16 or p[4] not in CH:
                continue
            if not certs.get(p[0], "").startswith("ok"):
                continue
            if p[0] in cls:
                c = cls[p[0]][0]
            else:
                if p[7] != "1" or p[14].endswith(":implicit"):
                    continue
                q = p[11].lower()
                c = "selfAnnounced" if any(w in q for w in ("overrul", "disapprov", " reced", "abrogat")) else \
                    "operativeWords"
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
    with open(os.path.join(HERE, "results", name, "old_by_class.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=1)
    print("admitted pairs by class:", res["_rows"])
    for k, d in res.items():
        if k.startswith("_"):
            continue
        print("%-45s SCDB %d/%d (precision %d/%d)  CRS current %d/%d  2016 express %d/%d  2016 all %d/%d" % (
            k, d["scdb_found"], d["scdb_flagged"], d["scdb_acting_flagged"], d["scdb_acting"],
            *d["crs_current_table"], *d["crs_2016_express"], *d["crs_2016_all"]))


if __name__ == "__main__":
    main()
