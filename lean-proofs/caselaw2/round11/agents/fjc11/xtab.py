"""fjc11: cross-tabs of feat_n1.tsv by tie combination; join to the round-10 r10f12 audit outcomes (our own audit,
not a key).   python -X utf8 xtab.py work/feat_n1.tsv"""
import collections, csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STATUS = ("reversed", "vacated", "modified")


def combo(t):
    return ("H+" if "H" in t else "noH") + ":" + ("".join(x for x in t if x != "H") or "-")


def main():
    R = [r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8"), delimiter="\t") if r["form"] != "h"]
    c = collections.defaultdict(collections.Counter)
    for r in R:
        g = combo(r["ties"])
        for k in ("n", "latest=" + r["latest"], "named=" + r["named"], "consol=" + r["consol"],
                  "flags=" + r["flags"], "status" if r["kind"] in STATUS else "nonstatus"):
            c[g][k] += 1
    for g in sorted(c):
        print(g, dict(sorted(c[g].items())))
    F = {(r["by"], r["target"]): r for r in R}
    au = os.path.join(C2, "round10", "audit", "r10f12")
    S = [r for r in csv.DictReader(open(os.path.join(au, "sample.tsv"), encoding="utf-8"), delimiter="\t")
         if r["role"] == "real"]
    E = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(au, "errors.tsv"), encoding="utf-8"), delimiter="\t"):
        E[r["item"]].append(r["failed"] + ":" + r["note"][:70])
    print("--- r10f12 items (H+ only) ---")
    for s in S:
        p = s["row_id"].split(":")
        f = F.get((p[1], p[2]))
        if not f or "H" not in f["ties"]:
            continue
        print("WRONG" if s["item"] in E else "ok   ", f["ties"], f["kind"], f["scope"], "latest", f["latest"],
              "named", f["named"], f["named_dates"], "j", f["jdate"], "consol", f["consol"], "flags", f["flags"],
              "|", (E.get(s["item"]) or [""])[0])


if __name__ == "__main__":
    main()
