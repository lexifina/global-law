"""Draw random validation samples from decisions2.tsv per field value and write their header regions to batch files
for reading (temporary; header snippets only).

    python sample_validate.py <out-dir> [seed]

Writes <out-dir>/val_<field>.txt (blocks: '### <k> node=<id> | court | date | predicted=<value> | src=<code>' +
the first 2,200 characters of the body after the front matter, + the last 500 characters) and <out-dir>/key_<field>.tsv
(k, node, field, predicted, src code, court id).
"""
import collections, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from show import fetch  # noqa: E402

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
DATA = os.path.join(WORK, "caselaw-lean-2", "data")
PLAN = {
    "bench": {"enBanc": 40, "limitedEnBanc": 10, "circulated": 12, "conflictPanel": 5, "division": 12,
              "wholeCourt": 10, "panel": 15},
    "publication": {"unpublished": 40, "summaryOrder": 10, "table": 15, "memorandum": 15, "published": 20},
    "form": {"perCuriam": 20, "plurality": 20, "equallyDivided": 15, "summaryAffirmance": 15, "certifiedAnswer": 15,
             "memorandum": 10, "full": 10},
    "unit": {"name": 8, "docket": 25, "header": 15, "county": 25, "judges": 45, "header-unitA": 2, "header-unitB": 4},
}
COL = {"bench": 4, "publication": 5, "form": 6}


def main(out, seed=20261112, plan=None):
    global PLAN
    if plan:
        import json
        PLAN = json.load(open(plan, encoding="utf-8"))
    random.seed(seed)
    names, units = {}, {}
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        names.setdefault(int(f[0]), f[3])
        m = re.match(r"unit-of:(\d+)", f[9])
        if m:
            units[(int(m.group(1)), int(f[8]))] = f[3]
    pools = collections.defaultdict(list)
    scotus = [c for c, n in names.items() if n == "Supreme Court of the United States"][0]
    with open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8") as f:
        for line in f:
            r = line.rstrip("\n").split("\t")
            src = dict(x.split(":", 1) for x in r[8].split(";"))
            for fld, col in COL.items():
                v = r[col]
                if v in PLAN[fld]:
                    if fld == "bench" and (v == "wholeCourt" and src["b"].startswith("default")):
                        continue
                    if fld == "bench" and v == "panel" and int(r[1]) == scotus:
                        continue
                    pools[(fld, v)].append(r)
            if r[3] != "0" and "unit" in PLAN:
                pools[("unit", src["u"])].append(r)
    os.makedirs(out, exist_ok=True)
    for fld, plan in PLAN.items():
        if not plan:
            continue
        picks = []
        for v, n in plan.items():
            pool = pools.get((fld, v), [])
            # reservoir would be cheaper; pools are in memory anyway
            picks += [(v, r) for r in random.sample(pool, min(n, len(pool)))]
        random.shuffle(picks)
        want = {}
        node_rows = {}
        with open(os.path.join(WORK, "graph/nodes.tsv"), encoding="utf-8") as fn:
            ids = {r[0] for _, r in picks}
            for line in fn:
                p = line.split("\t", 5)
                if p[0] in ids:
                    want[p[0]] = (p[1], p[2], p[3], p[4])
        texts = fetch(want)
        with open(os.path.join(out, "val_%s.txt" % fld), "w", encoding="utf-8", newline="\n") as fo, \
                open(os.path.join(out, "key_%s.tsv" % fld), "w", encoding="utf-8", newline="\n") as fk:
            for k, (v, r) in enumerate(picks, 1):
                t = texts.get(r[0], "")
                if t.startswith("---"):
                    end = t.find("\n---", 3)
                    keep = [l for l in t[3:end].splitlines() if l.split(":")[0] in
                            ("court", "docket", "judges", "precedential_status", "decision_type", "citations")]
                    t = "\n".join(keep) + "\n--" + t[end + 4:]
                src = dict(x.split(":", 1) for x in r[8].split(";"))
                code = {"bench": src["b"], "publication": src["p"], "form": src["f"], "unit": src["u"]}[fld]
                pred = r[COL[fld]] if fld != "unit" else "unit %s = %s" % (r[3], units.get((int(r[1]), int(r[3])), "?"))
                fo.write("### %d node=%s | %s | %s | predicted=%s | src=%s\n" % (k, r[0], names.get(int(r[1]), "?"),
                                                                                  r[2], pred, code))
                head = t[:2200 if fld != "unit" else 3000]
                fo.write(head + "\n")
                if len(t) > len(head):
                    fo.write("[... tail] " + t[-500:].replace("\n", " / ") + "\n")
                fo.write("\n")
                fk.write("\t".join([str(k), r[0], fld, v, code, r[1]]) + "\n")
        print(fld, len(picks))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20261112, sys.argv[3] if len(sys.argv) > 3 else None)
