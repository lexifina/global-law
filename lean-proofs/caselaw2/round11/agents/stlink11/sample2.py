"""stlink11 step 2: stratified diagnosis sample (seeded) over work/feat.jsonl by tie form x state x decade, for opus
readers (corpus text only). -> read2/items_<k>.md, read2/sample.tsv (strata; not shown to readers)."""
import collections, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import BO, L  # noqa: E402

NL = chr(10)
OUT = os.path.join(HERE, "read2")
SEED = 20261115


def forms(x):
    return [k for k, ok in (("docket", x["docket"] == "strong"), ("docketweak", x["docket"] == "weak"),
                            ("cite", x["cite"] in ("front", "body")), ("date", x["date"] == "present")) if ok]


def main():
    random.seed(SEED)
    recs = [json.loads(l) for l in open(os.path.join(HERE, "work", "feat.jsonl"), encoding="utf-8")]
    pools = collections.defaultdict(list)
    for r in recs:
        cs = [x for x in r.get("cands", []) if "err" not in x]
        full = sorted([x for x in cs if x["names"] == "full"], key=lambda x: x["tdate"])
        if full:
            T = full[-1]
            f = forms(T)
            if any(x["tdate"] == T["tdate"] for x in full[:-1]):
                pools["full_sibling"].append((r, T))
            elif "docket" in f:
                pools["full_docket"].append((r, T))
            elif "cite" in f:
                pools["full_cite"].append((r, T))
            elif "date" in f:
                pools["full_date"].append((r, T))
            else:
                pools["full_notie"].append((r, T))
        else:
            for k in ("mismatch", "surname_only"):
                xs = [x for x in cs if x["names"] == k]
                if xs:
                    pools["names_" + k].append((r, sorted(xs, key=lambda x: x["tdate"])[-1]))
                    break
    plan = [("full_docket", 6), ("full_cite", 8), ("full_date", 6), ("full_notie", 6), ("full_sibling", 4),
            ("names_mismatch", 5), ("names_surname_only", 5)]
    picked = []
    for name, k in plan:
        cells = collections.defaultdict(list)
        for r, T in pools[name]:
            cells[(r["sys"], r["date"] // 100000 * 10)].append((r, T))
        keys = sorted(cells)
        random.shuffle(keys)
        for c in keys:
            random.shuffle(cells[c])
        got = []
        while len(got) < k and any(cells[c] for c in keys):
            for c in keys:
                if cells[c] and len(got) < k:
                    got.append(cells[c].pop())
        picked += [(name, r, T) for r, T in got]
        print(name, len(pools[name]), len(got))
    random.shuffle(picked)
    BO.init()
    F = BO.G["F"]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "sample.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("item\tstratum\tby\ttarget\tsys\tdecade\tforms\n")
        for i, (s, r, T) in enumerate(picked):
            f.write("\t".join(str(x) for x in [i, s, r["n"], T["j"], r["sys"], r["date"] // 100000 * 10,
                                               "+".join(forms(T)) or "-"]) + NL)
    per = 10
    for k in range(0, len(picked), per):
        out = ["# Reader pack %d" % (k // per), ""]
        for i in range(k, min(k + per, len(picked))):
            _s, r, T = picked[i]
            n, j = r["n"], T["j"]
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
