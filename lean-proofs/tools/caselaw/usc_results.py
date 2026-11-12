"""Aggregate the statute check over the whole US Code (after RunStatuteText.lean).

    python tools/caselaw/usc_results.py <work dir> <today yyyymmdd>

Reads <work>/usc/{versions.tsv, enc/rows.tsv, enc/lean_out.tsv}, <work>/graph/nodes.tsv and <work>/lean-in-v3/courts.tsv
+ decisions.tsv; writes <work>/usc/results/{summary.json, by_year.tsv, laws.tsv, sections.tsv, titles.tsv,
survival.tsv, rows_out.tsv}.
"""
import collections, json, os, sys


def ymd(d):
    return f"{d // 10000:04d}-{d // 100 % 100:02d}-{d % 100:02d}"


def main(work, today):
    today = int(today)
    U = os.path.join(work, "usc")
    out = os.path.join(U, "results")
    os.makedirs(out, exist_ok=True)
    vers = collections.defaultdict(list)
    for i, l in enumerate(open(os.path.join(U, "versions.tsv"), encoding="utf-8")):
        f = l.rstrip("\n").split("\t")
        vers[f[0]].append((int(f[4]), f[2], f[3], f[6], i))
    for p in vers:
        vers[p].sort(key=lambda v: (v[0], v[4]))
    rows = {}
    for l in open(os.path.join(U, "enc", "rows.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        rows[int(f[0])] = (int(f[1]), int(f[2]), int(f[3]), f[4], f[5], int(f[6]))
    res = {}
    for l in open(os.path.join(U, "enc", "lean_out.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        res[int(f[0])] = tuple(int(x) for x in f[1:])
    need = {r[0] for r in rows.values()}
    court, name, repo = {}, {}, {}
    for l in open(os.path.join(work, "graph", "nodes.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        i = int(f[0])
        if i in need:
            name[i] = f[6]; repo[i] = f[1] + "\t" + f[2] + "\t" + f[5]
    for l in open(os.path.join(work, "lean-in-v3", "decisions.tsv"), encoding="utf-8"):
        i, c, _ = l.split("\t")
        if int(i) in need:
            court[int(i)] = int(c)
    ctab = {}
    for l in open(os.path.join(work, "lean-in-v3", "courts.tsv"), encoding="utf-8"):
        i, s, t, c = l.rstrip("\n").split("\t")
        ctab[int(i)] = (int(s), t)

    S = collections.Counter()
    dec = collections.defaultdict(lambda: [0, 0, 0])   # node -> [any amended, any words differ, any sub differs]
    year = collections.defaultdict(lambda: [0, 0, 0, 0])   # year -> rows, amended, words, sub
    laws = collections.defaultdict(set)                  # first law after the decision -> decisions
    lawrows = collections.Counter()
    lawname = {}
    secs = collections.defaultdict(lambda: [0, 0, 0, set()])  # section -> rows, amended, sub differs, decisions amended
    titles = collections.defaultdict(lambda: [0, 0, 0])
    surv = []                                            # (years to first law change or censoring, event)
    fed = collections.Counter()
    with open(os.path.join(out, "rows_out.tsv"), "w", encoding="utf-8", newline="\n") as fo:
        for rid, (nid, d, t, s, sub, nm) in rows.items():
            a, nl, first, w, sd, nch = res[rid]
            path = f"title-{t}/{s}.md"
            S["rows"] += 1; S["amended"] += a; S["words"] += w; S["sub"] += sd
            S["edition_only"] += (w and not a)
            if sub:
                S["rows_sub"] += 1; S["amended_sub"] += a; S["sub_differs_sub"] += sd
                S["amended_sub_same"] += (a and not sd)
            dd = dec[nid]; dd[0] |= a; dd[1] |= w; dd[2] |= sd
            y = d // 10000
            yy = year[y]; yy[0] += 1; yy[1] += a; yy[2] += w; yy[3] += sd
            sec = f"{t} U.S.C. § {s}"
            ss = secs[sec]; ss[0] += 1; ss[1] += a; ss[2] += sd
            ti = titles[t]; ti[0] += 1; ti[1] += a; ti[2] += sd
            fl = ""
            if a:
                ss[3].add(nid)
                v = next(v for v in vers[path] if v[0] == first and v[1] == "law")
                fl = v[2]
                laws[fl].add(nid); lawrows[fl] += 1; lawname[fl] = v[3]
            sys_, tier = ctab.get(court.get(nid, -1), (999, "T"))
            fed["federal" if sys_ == 0 else "state", a] += 1
            if sys_ == 0 and tier == "L":
                S["scotus_rows"] += 1; S["scotus_amended"] += a
            t1 = (first if a else today)
            dy = (t1 // 10000 - y) + ((t1 // 100 % 100) - (d // 100 % 100)) / 12
            surv.append((max(dy, 0.0), a))
            fo.write(f"{rid}\t{nid}\t{ymd(d)}\t{sec}\t{sub}\t{a}\t{nl}\t{ymd(first) if first else ''}\t{fl}\t{w}\t{sd}\t{name.get(nid, '')}\t{repo.get(nid, '')}\n")
    S["decisions"] = len(dec)
    S["decisions_amended"] = sum(1 for v in dec.values() if v[0])
    S["decisions_words"] = sum(1 for v in dec.values() if v[1])
    S["decisions_sub"] = sum(1 for v in dec.values() if v[2])
    S["sections"] = len(secs)
    S["laws_affecting"] = len(laws)
    S["federal_rows"] = fed["federal", 0] + fed["federal", 1]; S["federal_amended"] = fed["federal", 1]
    S["state_rows"] = fed["state", 0] + fed["state", 1]; S["state_amended"] = fed["state", 1]
    S["code_sections"] = len(vers)
    S["code_law_versions"] = sum(1 for p in vers for v in vers[p] if v[1] == "law")
    S["code_laws"] = len({v[2] for p in vers for v in vers[p] if v[1] == "law"})
    # Kaplan-Meier: share of applied sections not yet amended by a law, N years after the decision
    surv.sort()
    n, alive, km, i = len(surv), 1.0, [], 0
    at = n
    for yr in range(0, 32):
        while i < n and surv[i][0] <= yr:
            j = i; ev = 0
            while j < n and surv[j][0] == surv[i][0]:
                ev += surv[j][1]; j += 1
            if at:
                alive *= 1 - ev / at
            at -= j - i; i = j
        km.append((yr, alive, at))
    half = next((yr for yr, a, _ in km if a <= .5), None)
    S["half_life_years"] = half
    json.dump(S, open(os.path.join(out, "summary.json"), "w"), indent=1)
    with open(os.path.join(out, "survival.tsv"), "w", newline="\n") as f:
        for yr, a, at_ in km:
            f.write(f"{yr}\t{a:.4f}\t{at_}\n")
    with open(os.path.join(out, "by_year.tsv"), "w", newline="\n") as f:
        for y in sorted(year):
            f.write(f"{y}\t" + "\t".join(map(str, year[y])) + "\n")
    with open(os.path.join(out, "laws.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for l in sorted(laws, key=lambda k: -len(laws[k])):
            f.write(f"{l}\t{lawname[l]}\t{len(laws[l])}\t{lawrows[l]}\n")
    with open(os.path.join(out, "sections.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for s in sorted(secs, key=lambda k: -len(secs[k][3])):
            r = secs[s]
            f.write(f"{s}\t{r[0]}\t{r[1]}\t{r[2]}\t{len(r[3])}\n")
    with open(os.path.join(out, "titles.tsv"), "w", newline="\n") as f:
        for t in sorted(titles):
            f.write(f"{t}\t" + "\t".join(map(str, titles[t])) + "\n")
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
