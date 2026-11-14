"""Round 7, agent `antecedent`: ids files of the certified rows by audit sub-class (lead's request).

    python -X utf8 subclass_ids.py  ->  ids_A_joined.tsv, ids_B_onesentence.tsv, ids_D_window.tsv, ids_C_weak.tsv

A = two-sentence joined rows (tiers A/B), B = one-sentence rows (tiers A/B), D = plain rows whose naming is in the
certifier window (antecedent:window, tiers A/B), C = every row from tier C (weak verbs: repudiate / disavow /
overturn / "no longer"). Columns: id, by, target, kind, scope, rule, tier, jlen, gap, court group, decade.
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import summarize as S  # noqa: E402
L = S.L
NL = chr(10)


def main():
    F = L.Facts()
    cert = set(l.split("\t")[0] for l in open(os.path.join(HERE, "cert", "treatments_delta.tsv"), encoding="utf-8"))
    out = collections.defaultdict(list)
    for line in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        tid = "t7:%d:%d:%d" % (r["by"], r["target"], r["main"][0])
        if tid not in cert:
            continue
        note = r.get("note", "")
        tier = re.search(r"tier=(\w*)", note).group(1)
        jl = re.search(r"jlen=(\S+)", note).group(1)
        gp = re.search(r"gap=(\S+)", note).group(1)
        sub = "C" if tier == "C" else {"antecedent:joined": "A", "antecedent:onesentence": "B",
                                       "antecedent:window": "D"}[r["rule"]]
        out[sub].append([tid, r["by"], r["target"], r["kind"], r["scope"], r["rule"], tier, jl, gp,
                         S.group(F, r["by"]), str(int(F.date[r["by"]]) // 100000 * 10)])
    names = {"A": "ids_A_joined.tsv", "B": "ids_B_onesentence.tsv", "D": "ids_D_window.tsv", "C": "ids_C_weak.tsv"}
    for k, fn in names.items():
        with open(os.path.join(HERE, fn), "w", encoding="utf-8", newline=NL) as f:
            for row in out[k]:
                f.write("\t".join(str(x) for x in row) + NL)
        c = collections.Counter(x[3] for x in out[k])
        g = collections.Counter(x[9].split(":")[0] for x in out[k])
        extra = ""
        if k == "A":
            gb = collections.Counter("<=300" if int(x[8]) <= 300 else ("301-600" if int(x[8]) <= 600 else ">600")
                                     for x in out[k])
            jb = collections.Counter("<=300" if int(x[7]) <= 300 else ("301-600" if int(x[7]) <= 600 else ">600")
                                     for x in out[k])
            extra = " gap %s jlen %s" % (dict(gb), dict(jb))
        print(k, fn, len(out[k]), dict(c), dict(g), dict(collections.Counter(x[4] for x in out[k])), extra)


if __name__ == "__main__":
    main()
