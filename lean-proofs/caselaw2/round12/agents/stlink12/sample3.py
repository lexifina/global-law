"""stlink12 step 2: stratified diagnosis sample (seeded) over work/feat3.jsonl (pool, strict names) by third-tie form x
era x state -> read3/items_<k>.md, read3/sample.tsv (strata; not shown to readers)."""
import collections, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import BO, L  # noqa: E402

NL = chr(10)
OUT = os.path.join(HERE, "read3")
SEED = 20261114
PLAN = [("fdate", 12), ("judge", 6), ("author", 6), ("tdocket", 6), ("county", 5), ("none", 4)]


def era(d):
    y = d // 10000
    return "pre1970" if y < 1970 else ("1970_89" if y < 1990 else "1990on")


def main():
    random.seed(SEED)
    recs = [json.loads(l) for l in open(os.path.join(HERE, "work", "feat3.jsonl"), encoding="utf-8")]
    recs = [r for r in recs if r["src"] == "pool" and "err" not in r and r["strict"]]
    used = set()
    picked = []
    for form, k in PLAN:
        if form == "none":
            pool = [r for r in recs if not r["ties3"]]
        else:
            pool = [r for r in recs if form in r["ties3"]]
        single = [r for r in pool if len(r["ties3"]) <= 1]
        multi = [r for r in pool if len(r["ties3"]) > 1]
        got = []
        for sub, kk in ((single, k - k // 3), (multi, k // 3)):
            cells = collections.defaultdict(list)
            for r in sub:
                if r["n"] not in used:
                    cells[(era(r["date"]), r["sys"])].append(r)
            keys = sorted(cells)
            random.shuffle(keys)
            for c in keys:
                random.shuffle(cells[c])
            # round robin over eras first, then states
            byera = collections.defaultdict(list)
            for c in keys:
                byera[c[0]].append(c)
            g = []
            while len(g) < kk and any(cells[c] for c in keys):
                for e in sorted(byera):
                    for c in byera[e]:
                        if cells[c]:
                            g.append(cells[c].pop())
                            break
                    if len(g) >= kk:
                        break
            got += g
        for r in got:
            used.add(r["n"])
        picked += [(form, r) for r in got]
        print(form, "pool", len(pool), "single", len(single), "picked", len(got))
    random.shuffle(picked)
    BO.init()
    F = BO.G["F"]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "sample.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("item\tstratum\tby\ttarget\tsys\tera\tties3\n")
        for i, (s, r) in enumerate(picked):
            f.write("\t".join(str(x) for x in [i, s, r["n"], r["j"], r["sys"], era(r["date"]),
                                               json.dumps(r["ties3"], ensure_ascii=False)]) + NL)
    per = 8
    for k in range(0, len(picked), per):
        out = ["# Reader pack %d" % (k // per), ""]
        for i in range(k, min(k + per, len(picked))):
            _s, r = picked[i]
            n, j = r["n"], r["j"]
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
