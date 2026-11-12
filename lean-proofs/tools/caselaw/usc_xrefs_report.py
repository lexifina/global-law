"""Tables from Lean's statuses of every cross-reference in the US Code (see usc_xrefs.py).

    python tools/caselaw/usc_xrefs_report.py <versions.tsv> <data dir> <out dir> [today yyyymmdd]

An episode of dangling starts on a day Lean's status turns to "d" and ends when it turns back ("o": the target came
back or was fixed; "a": the referring text dropped the reference). Its class:
  written   the referring section's new version that day makes a reference that does not resolve (the law, or the
            edition, that wrote it is the cause);
  broken    the reference resolved the day before; the target's version of that day is the cause (by `status_stable`
            only a dated version of the source or target can change a status, and the source's text still makes it);
  at-start  it dangles on the first day judged (the record's start, or the day both titles are in it), unless a law
            made the referring version that day.
"""
import collections, json, os, pickle, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from usc_xrefs import load_versions, norm_ref, pstr  # noqa: E402


def in_force(vs, d):
    cur = None
    for v in vs:
        if v[0] <= d:
            cur = v
        else:
            break
    return cur


def label(v):
    if v is None:
        return ""
    return v[2] + (f" ({v[4]})" if v[4] else "")


def report(versions, data, outdir, today="20261112"):
    today = int(today)
    vers = load_versions(versions)
    scan_ = pickle.load(open(os.path.join(data, "scan.pkl"), "rb"))
    rows = {}
    for l in open(os.path.join(data, "rows.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        rows[int(f[0])] = (f[1], f[2], f[3], f[4])
    out = {}
    for k in range(4):
        for l in open(os.path.join(data, f"lean_out_{k}.tsv"), encoding="utf-8"):
            f = l.rstrip("\n").split("\t")
            tr = [(int(x.split(":")[0]), x.split(":")[1]) for x in f[1].split(" ") if x]
            out[int(f[0])] = (tr, f[2])
    years = list(range(1995, 2027))

    def ctx_of(src, tgt, path, d):
        v = in_force(vers[src], d)
        if not v or not v[3] or (src, v[3]) not in scan_:
            return ""
        want = (tgt, tuple(path.split(".")) if path else ())
        for kind, t, p, here, ctx, ln in scan_[(src, v[3])][5]:
            if want in norm_ref(t, p, vers):
                return re.sub(r"\s+", " ", ctx)
        return ""

    def why_target(tgt, path, d):
        if not vers.get(tgt):
            return "target never in record"
        v = in_force(vers[tgt], d)
        if v is None:
            return "target not yet in record"
        if not v[3]:
            return "target file removed"
        a = scan_[(tgt, v[3])]
        if not a[0]:
            return "target " + a[6].lower()
        p = tuple(path.split(".")) if path else ()
        return "designation repealed" if p in a[3] else "designation missing"

    eps = []  # (rid, start, end or 0, class, cause version, how ended)
    for rid, (tr, ys) in out.items():
        src, tgt, path, kinds = rows[rid]
        prev = None
        for i, (d, s) in enumerate(tr):
            if s == "d":
                sv = in_force(vers[src], d)
                tch = [v for v in vers.get(tgt, []) if v[0] == d]
                sch = [v for v in vers[src] if v[0] == d]
                if prev is None and not (sch and sch[-1][1]):
                    cls, cause = "at-start", None  # dangling on the first day judged (no law made it that day)
                elif prev == "o":
                    cls, cause = "broken", (tch[-1] if tch else None)
                else:
                    cls, cause = "written", (sch[-1] if sch else sv)
                end, how = 0, ""
                if i + 1 < len(tr):
                    end, how = tr[i + 1][0], {"o": "resolved", "a": "removed"}[tr[i + 1][1]]
                eps.append((rid, d, end, cls, cause, how))
            prev = s
    print("episodes", len(eps), collections.Counter(e[3] for e in eps), flush=True)
    os.makedirs(outdir, exist_ok=True)

    def W(name):
        return open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")

    with W("dangling_episodes.tsv") as f:
        f.write("row\tsource\ttarget\tpath\tkinds\tfrom\tuntil\tclass\tcause\tcause_day\tended\treason\tcontext\n")
        for rid, d, end, cls, cause, how in sorted(eps, key=lambda e: (rows[e[0]][0], e[1])):
            src, tgt, path, kinds = rows[rid]
            f.write(f"{rid}\t{src}\t{tgt}\t{path}\t{kinds}\t{d}\t{end or ''}\t{cls}\t{label(cause)}\t"
                    f"{cause[0] if cause else ''}\t{how}\t{why_target(tgt, path, d)}\t{ctx_of(src, tgt, path, d)[:400]}\n")
    cur = {e[0]: e for e in eps if e[2] == 0}
    ever_ok = {rid for rid, (tr, ys) in out.items() if any(s == "o" for _, s in tr)}
    today_rows = [rid for rid, (tr, ys) in out.items() if tr and tr[-1][1] == "d"]
    in_force_today = [rid for rid, (tr, ys) in out.items() if tr and tr[-1][1] != "a"]
    with W("dangling_today.tsv") as f:
        f.write("row\ttitle\tsource\ttarget\tpath\tkinds\tsince\tclass\tcause\tever_resolved\treason\tcontext\n")
        for rid in sorted(today_rows, key=lambda r: (int(rows[r][0].split("/")[0][6:]), rows[r][0])):
            src, tgt, path, kinds = rows[rid]
            e = cur[rid]
            f.write(f"{rid}\t{src.split('/')[0][6:]}\t{src}\t{tgt}\t{path}\t{kinds}\t{e[1]}\t{e[3]}\t{label(e[4])}\t"
                    f"{1 if rid in ever_ok else 0}\t{why_target(tgt, path, today)}\t{ctx_of(src, tgt, path, today)[:400]}\n")
    bt = collections.defaultdict(lambda: [0, 0, collections.Counter()])
    for rid in in_force_today:
        bt[int(rows[rid][0].split("/")[0][6:])][0] += 1
    for rid in today_rows:
        t = int(rows[rid][0].split("/")[0][6:])
        bt[t][1] += 1
        bt[t][2][why_target(rows[rid][1], rows[rid][2], today)] += 1
    reasons = ["designation missing", "designation repealed", "target repealed", "target transferred",
               "target file removed", "target never in record", "target vacant", "target reserved", "target omitted",
               "target expired"]
    with W("dangling_by_title.tsv") as f:
        f.write("title\treferences\tdangling\tpct\t" + "\t".join(r.replace(" ", "_") for r in reasons) + "\n")
        for t in sorted(bt):
            r, d, c = bt[t]
            f.write(f"{t}\t{r}\t{d}\t{100 * d / r:.2f}\t" + "\t".join(str(c[x]) for x in reasons) + "\n")
    secs = collections.Counter()
    for p, vs in vers.items():
        for y in years:
            d = today if y == 2026 else y * 10000 + 1231
            v = in_force(vs, d)
            if v and v[3] and (p, v[3]) in scan_ and scan_[(p, v[3])][0]:
                secs[y] += 1
    refs_y, dang_y = collections.Counter(), collections.Counter()
    for rid, (tr, ys) in out.items():
        for i, c in enumerate(ys):
            if c in "od":
                refs_y[years[i]] += 1
            if c == "d":
                dang_y[years[i]] += 1
    new_y = collections.defaultdict(collections.Counter)
    for rid, d, end, cls, cause, how in eps:
        new_y[d // 10000][cls] += 1
    with W("by_year.tsv") as f:
        f.write("year\tsections\treferences\tdangling\n")
        for y in years[1:]:  # 1995 lacks titles 7, 28 and 39, whose record starts 1996-01-16
            f.write(f"{y}\t{secs[y]}\t{refs_y[y]}\t{dang_y[y]}\n")
    with W("by_year_detail.tsv") as f:
        f.write("year\tsections\treferences\tdangling\tpct\tnew_written_dangling\tnew_broken_later\tdangling_at_record_start\n")
        for y in years:
            f.write(f"{y}\t{secs[y]}\t{refs_y[y]}\t{dang_y[y]}\t{100 * dang_y[y] / max(1, refs_y[y]):.2f}\t"
                    f"{new_y[y]['written']}\t{new_y[y]['broken']}\t{new_y[y]['at-start']}\n")
    laws = collections.defaultdict(collections.Counter)
    for rid, d, end, cls, cause, how in eps:
        if cause is not None:
            k = (label(cause), cause[1])
            laws[k][cls] += 1
            if end == 0:
                laws[k][cls + "-open"] += 1
    with W("laws.tsv") as f:
        f.write("cause\tby_law\tbroken_later\tbroken_later_still_dangling\twritten_dangling\twritten_still_dangling\n")
        for (lab, islaw), c in sorted(laws.items(), key=lambda x: -(x[1]["broken"] + x[1]["written"])):
            f.write(f"{lab}\t{1 if islaw else 0}\t{c['broken']}\t{c['broken-open']}\t{c['written']}\t{c['written-open']}\n")
    dup_now, dup_hist, first_dup = [], collections.Counter(), {}
    for p, vs in vers.items():
        prevset = set()
        for v in vs:
            a = scan_.get((p, v[3])) if v[3] else None
            ds = {(pstr(x[0]), x[1]) for x in a[4]} if a and a[0] else set()
            for k in ds - prevset:
                first_dup.setdefault((p, k), v)
            prevset = ds
        for y in years:
            d = today if y == 2026 else y * 10000 + 1231
            v = in_force(vs, d)
            a = scan_.get((p, v[3])) if v and v[3] else None
            if a and a[0]:
                dup_hist[y] += len(a[4])
        v = vs[-1]
        a = scan_.get((p, v[3])) if v[3] else None
        if a and a[0]:
            for parent, d, k in a[4]:
                dup_now.append((p, pstr(parent), d, k, first_dup.get((p, (pstr(parent), d)))))
    with W("duplicates_today.tsv") as f:
        f.write("section\tparent\tdesignation\tcount\tsince\tmade_by\n")
        for p, parent, d, k, v in sorted(dup_now):
            f.write(f"{p}\t{parent}\t{d}\t{k}\t{v[0] if v else ''}\t{label(v)}\n")
    dl = collections.Counter()
    for (p, k), v in first_dup.items():
        dl[(label(v), v[1])] += 1
    with W("duplicates_by_year.tsv") as f:
        f.write("year\tduplicates\n")
        for y in years:
            f.write(f"{y}\t{dup_hist[y]}\n")
    with W("duplicates_laws.tsv") as f:
        f.write("made_by\tby_law\tduplicates_made\n")
        for (lab, islaw), n in dl.most_common():
            f.write(f"{lab}\t{1 if islaw else 0}\t{n}\n")
    summ = {
        "references_in_force_today": len(in_force_today), "dangling_today": len(today_rows),
        "dangling_today_ever_resolved": sum(1 for r in today_rows if r in ever_ok),
        "dangling_today_class": dict(collections.Counter(cur[r][3] for r in today_rows)),
        "dangling_today_reason": dict(collections.Counter(why_target(rows[r][1], rows[r][2], today) for r in today_rows)),
        "dangling_today_kinds": dict(collections.Counter(rows[r][3] for r in today_rows)),
        "references_ever": len(out), "episodes": len(eps), "episode_class": dict(collections.Counter(e[3] for e in eps)),
        "episodes_closed": dict(collections.Counter(e[5] for e in eps if e[2])),
        "refs_never_resolved": sum(1 for rid, (tr, ys) in out.items() if any(s == "d" for _, s in tr) and rid not in ever_ok),
        "refs_broken_after_resolving": len({e[0] for e in eps if e[3] == "broken"}),
        "duplicates_today": len(dup_now), "duplicate_sections_today": len({x[0] for x in dup_now}),
        "duplicates_ever": len(first_dup),
    }
    with W("summary.json") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    report(*sys.argv[1:])
