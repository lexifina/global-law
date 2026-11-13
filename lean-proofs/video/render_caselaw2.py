"""Render caselaw2_film.html (three.js, WebGL on the GPU) frame by frame and encode with NVENC, like render_caselaw.py.

    python video/render_caselaw2.py --build-data       # writes video/caselaw2_data.json from the caselaw-lean-2 files
    python video/render_caselaw2.py --still 3 12 20    # video/out/cl2_003.0.png ...
    python video/render_caselaw2.py [--fps 30]         # video/out/caselaw-lean-2.mp4 (1920x1080) and caselaw-lean-2-share.mp4
    python video/render_caselaw2.py --share-only       # only re-encode the share cut from the mp4

Every number in the film is read here from ~/Documents/us-caselaw-lean-work/caselaw-lean-2 (and the declaration map
from ../caselaw-anatomy.jsonl); a number that cannot be found stops the build.
"""
import argparse, collections, datetime, json, math, random, re, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAME = "caselaw-lean-2"
ARGS = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu-rasterization", "--ignore-gpu-blocklist", "--enable-webgl",
        "--disable-web-security"]

W = Path.home() / "Documents" / "us-caselaw-lean-work"
C = W / "caselaw-lean-2"
MONTHS = "January February March April May June July August September October November December".split()


def day(d):
    d = int(d)
    return f"{d % 100} {MONTHS[d // 100 % 100 - 1]} {d // 10000}"


def rows(p, skip=0):
    with open(p, encoding="utf-8", newline="\n") as f:
        for i, l in enumerate(f):
            if i >= skip:
                yield l.rstrip("\n").split("\t")


def need(pattern, text, what):
    m = re.search(pattern, text)
    if not m:
        sys.exit(f"build-data: cannot find {what}")
    return m


def num(s):
    return int(s.replace(",", ""))


def anatomy():
    """The declaration map: the layout of tools/caselaw/caselaw_v1v2_anatomy.py, as dots and edges."""
    sys.path.insert(0, str(HERE.parent / "tools" / "caselaw"))
    import caselaw_v1v2_anatomy as A
    L = [json.loads(l) for l in open(HERE.parents[1] / "caselaw-anatomy.jsonl", encoding="utf-8")]
    L = [x for x in L if not A.auto(x["n"])]
    names = {x["n"] for x in L}
    mod = {x["n"]: x["m"] for x in L}
    kind = {x["n"]: x["k"] for x in L}
    col = {}
    for n in names:
        for k, c in enumerate(A.COLS):
            if c[3](mod[n]):
                col[n] = k
                break
    names = {n for n in names if n in col}
    deps = {x["n"]: [d for d in x["d"] if d in names] for x in L if x["n"] in names}
    users = collections.Counter(d for ds in deps.values() for d in ds)
    sys.setrecursionlimit(100000)
    memo = {}

    def depth(n):
        if n not in memo:
            memo[n] = 0
            memo[n] = 1 + max((depth(m) for m in deps[n]), default=-1)
        return memo[n]
    for n in names:
        depth(n)
    maxd = max(memo.values())
    NC = len(A.COLS)
    pan = lambda n: A.COLS[col[n]][4]
    X0, GAP, PGAP, PW = 70, 18, 56, [250, 1000]
    counts = [collections.Counter(memo[n] for n in names if col[n] == k) for k in range(NC)]
    share = [max(max(c.values()) if c else 1, 12) ** .62 for c in counts]
    cw, cx = [0.0] * NC, [0.0] * NC
    x = X0
    for p in range(2):
        ks = [k for k in range(NC) if A.COLS[k][4] == p]
        usable = PW[p] - GAP * (len(ks) - 1)
        tot = sum(share[k] for k in ks)
        for k in ks:
            cw[k] = usable * share[k] / tot
            cx[k] = x
            x += cw[k] + GAP
        x += PGAP - GAP
    stp = [9.0 if A.COLS[k][4] == 0 else 7.0 for k in range(NC)]
    per_line = [max(1, int(cw[k] // stp[k])) for k in range(NC)]
    band_h = [max(16, max(math.ceil(counts[k].get(d, 0) / per_line[k]) * stp[k] for k in range(NC)) + 8) for d in range(maxd + 1)]
    band_y = [sum(band_h[:d]) for d in range(maxd + 1)]
    order, pos = [], {}
    for k in range(NC):
        for d in range(maxd + 1):
            ns = sorted((n for n in names if col[n] == k and memo[n] == d), key=lambda n: (mod[n], n))
            pl, step = per_line[k], stp[k]
            nrows = math.ceil(len(ns) / pl) if ns else 0
            for i, n in enumerate(ns):
                r, c = divmod(i, pl)
                n_in = min(pl, len(ns) - r * pl)
                pos[n] = (cx[k] + (cw[k] - n_in * step) / 2 + c * step + step / 2, band_y[d] + (band_h[d] - nrows * step) / 2 + r * step + step / 2)
                order.append(n)
    idx = {n: i for i, n in enumerate(order)}
    dots = [[round(pos[n][0], 1), round(pos[n][1], 1), col[n], memo[n], 1 if kind[n] == "thm" else 0, users[n]] for n in order]
    edges = [[idx[d], idx[n]] for n, ds in deps.items() for d in ds]
    short = ["COURTS", "PRECEDENT", "AUTHORITY", "STATUS", "SPLITS", "CERTIFICATES", "EXEC", "HUNT", "TESTS", "DATA I/O"]
    cols = [dict(name=short[k], color=c[2], x=round(cx[k], 1), w=round(cw[k], 1), panel=c[4]) for k, c in enumerate(A.COLS)]
    stats = [dict(decl=sum(1 for n in names if pan(n) == p), thm=sum(1 for n in names if pan(n) == p and kind[n] == "thm")) for p in range(2)]
    return dict(dots=dots, edges=edges, cols=cols, x0=X0, x1=max(cx[k] + cw[k] for k in range(NC)), h=sum(band_h), maxd=maxd), stats


def build_data():
    random.seed(2026)
    S, D = {}, {}
    # ---- the model: declaration map, theorem lock, mutants ----
    D["anat"], st = anatomy()
    v = json.loads((C / "report" / "caselaw-v1-v2.json").read_text())["panels"]
    if [st[0]["decl"], st[1]["decl"]] != [v[0]["decl"], v[1]["decl"]]:
        sys.exit(f"declaration map {st} differs from report/caselaw-v1-v2.json {v}")
    S.update(decl1=v[0]["decl"], decl2=v[1]["decl"], thm1=v[0]["thm"], thm2_all=v[1]["thm"])
    trust = (C / "TRUST.md").read_text(encoding="utf-8")
    lean = (C / "LEAN.md").read_text(encoding="utf-8")
    S["locked"] = num(need(r"\*\*Proved:\*\* ([\d,]+) kernel-checked theorems, each statement locked", trust, "locked theorems")[1])
    m = need(r"\*\*Mutation:\*\* (\d+) properties against (\d+) mutants, all killed", lean, "mutants")
    S["props"], S["mutants"] = int(m[1]), int(m[2])
    # ---- differential testing (DIFFTEST.md section 8, final row) and fuzzing ----
    dt = (C / "DIFFTEST.md").read_text(encoding="utf-8")
    m = re.findall(r"Real data \(`(\w+)`\) \| certs \*\*0/([\d,]+)\*\*, splits \*\*0/([\d,]+)\*\*, conflicts \*\*0/([\d,]+)\*\*, status \*\*(\d+)/([\d,]+)\*\*, findings \*\*(\d+)/([\d,]+)\*\*", dt)
    if not m:
        sys.exit("build-data: cannot find the DIFFTEST real-data row")
    m = m[-1]  # the latest run
    S.update(dt_certs=num(m[1]), dt_splits=num(m[2]), dt_conflicts=num(m[3]), dt_status=[int(m[4]), num(m[5])], dt_findings=[int(m[6]), num(m[7])])
    S["dt_run"] = m[0]
    sw = re.findall(r"\*\*0 of ([\d,]+) universes disagree\*\*", dt)
    rg = re.findall(r"Regression set, (\d+) universes[^|]*\| \*\*0 disagreements\*\*", dt)
    if not sw or not rg:
        sys.exit("build-data: cannot find the DIFFTEST sweep or regression rows")
    S.update(dt_universes=num(sw[-1]), dt_regress=int(rg[-1]))
    fz = (C / "FUZZ.md").read_text(encoding="utf-8")
    S["fuzz_cases"] = num(need(r"\| B, seed 7 \| ([\d,]+) \|", fz, "fuzz run B")[1])
    need(r"P1–P4: 0 failures", fz, "fuzz result")
    S["fuzz_rows"] = need(r"run B \(5,000 cases, (\d+)k rows\)", fz, "fuzz rows")[1] + ",000"
    need(r"nine bugs", trust, "fuzz bugs"); S["fuzz_bugs"] = 9
    # ---- certificates ----
    cert = collections.Counter()
    for t, _, r, _ in rows(C / "out" / "certs.tsv", 1):
        cert[t, r] += 1
    tot = lambda t: sum(n for (a, _), n in cert.items() if a == t)
    okc = lambda t: sum(n for (a, r), n in cert.items() if a == t and r.startswith("ok"))
    S.update(treat_rows=tot("treatment"), treat_ok=okc("treatment"), hist_rows=tot("history"), hist_ok=okc("history"), holdings=tot("holding"))
    S["admitted"], S["rejected"] = S["treat_ok"] + S["hist_ok"], S["treat_rows"] + S["hist_rows"] - S["treat_ok"] - S["hist_ok"]
    # ---- treatments by kind ----
    tk = collections.Counter(f[4] for f in rows(C / "data" / "treatments.tsv"))
    D["kinds"] = tk.most_common()
    if sum(tk.values()) != S["treat_rows"]:
        sys.exit("treatments.tsv and certs.tsv disagree on the number of treatments")
    # ---- runner counters ----
    sm = collections.Counter()
    for f in rows(C / "out" / "summary.tsv"):
        if f[0] in ("edges", "horty_bases", "horty_inconsistent", "bad_edges"):
            sm[f[0]] += int(f[1])
    S.update(citations=sm["edges"], horty=sm["horty_bases"], horty_ok=sm["horty_bases"] - sm["horty_inconsistent"])
    sp = collections.Counter(f[0] for f in rows(C / "out" / "splits.tsv", 1))
    S.update(splits=sp["split"], conflicts=sp["conflict"])
    # ---- findings, and a sample of them placed by the citing decision ----
    FK = ["atRisk", "citesOverruled", "citesVacated", "citesNotCitable", "citesWithdrawn", "panelDepartsWithoutEnBanc"]
    fc, samp = collections.Counter(), {}
    RATE = 12
    for f in rows(C / "out" / "findings.tsv", 1):
        fc[f[0]] += 1
        if f[0] in FK and random.random() < 1 / RATE:
            samp.setdefault(int(f[1]), FK.index(f[0]))
    D["findings"] = [[k, fc[k]] for k in FK]
    S["findings_rate"] = RATE
    courts = {}
    for f in rows(C / "data" / "courts2.tsv"):
        courts.setdefault(int(f[0]), (int(f[4]), f[5]))
    pts, fnd, n = [], [], 0
    for f in rows(C / "data" / "decisions2.tsv"):
        n += 1
        i, c, d = int(f[0]), int(f[1]), int(f[2])
        s, t = courts.get(c, (999, "T"))
        if s > 56 or d < 16000101:
            continue
        if random.random() < 36000 / 6.9e6:
            pts.append([d // 10000, s, t if t in "LAT" else "T"])
        if i in samp:
            fnd.append([d // 10000, s, samp[i]])
    S["decisions"] = n
    D["pts"], D["fnd"] = pts, fnd
    # the corpus opening reuses the v1 film's points (video/caselaw_data.json: [year, court-system row, tier])
    v1 = json.loads((HERE / "caselaw_data.json").read_text(encoding="utf-8"))
    if v1["S"]["decisions"] != n:
        sys.exit("v1 film data and decisions2.tsv disagree on the number of decisions")
    D["v1pts"], D["v1rows"] = v1["pts"], len(v1["rows"])
    # ---- one partial overruling: Ring v. Arizona on Walton v. Arizona ----
    RING, WALTON = 6209369, 6123204
    LAW, BOW, IMPL = 6218081, 6102809, [5950738, 5988307, 6074209]
    want = {RING, WALTON, 704585, 548001, 6206754, 6239607, LAW, BOW, *IMPL}
    node = {int(f[0]): f for f in rows(W / "graph" / "nodes.tsv") if int(f[0]) in want}
    cite = lambda i: node[i][5].split("|")[0]
    st_rows = [f for f in rows(C / "out" / "status.tsv", 1) if f[0] in (str(WALTON), "6239607", str(BOW))]
    # ---- one worked case: Lawrence v. Texas on Bowers v. Hardwick ----
    bs = next(f for f in st_rows if f[0] == str(BOW) and f[1] == "-" and f[5] == "neg:overruled")
    lt = next(f for f in rows(C / "data" / "treatments.tsv") if f[0] == bs[8])
    if int(lt[1]) != LAW or next(f for f in rows(C / "out" / "certs.tsv", 1) if f[1] == lt[0])[2:] != ["ok", "ok"]:
        sys.exit("Lawrence: the status witness is not an admitted Lawrence treatment")
    notes = [f for f in rows(C / "gold" / "reports_typed.tsv", 1) if f[3] == str(BOW) and f[5] == str(LAW) and f[8] == "overruled"]
    nt = next(f for f in notes if "overruled by Lawrence v. Texas, 539 U.S. 558" in f[17] and "Bowers v. Hardwick, 478 U.S. 186" in f[17])
    sn = nt[17]; a0 = sn.index("Bowers v. Hardwick, 478 U.S. 186"); a1 = sn.index("(2003)", a0) + 6
    D["law"] = dict(by=f"{node[LAW][6]}, {node[LAW][5].split('|')[0]}", by_day=day(lt[3]), quote=lt[11], start=int(lt[9]), end=int(lt[10]), part=lt[13],
                    evidence=lt[12], kind=lt[4], scope=lt[5], target=f"{node[BOW][6]}, {node[BOW][5].split('|')[0]} ({node[BOW][4][:4]})",
                    same_court=node[LAW][3] == node[BOW][3], from_day=day(bs[3]), status=bs[5], note=sn[a0:a1], note_day=day(nt[2]), note_node=int(nt[1]), notes=len(notes))
    wit = next(f for f in st_rows if f[0] == str(WALTON) and f[5] == "neg:overruled")
    tr = next(f for f in rows(C / "data" / "treatments.tsv") if f[0] == wit[8])
    a, b = int(tr[9]), int(tr[10])
    win = next(f for f in rows(C / "data" / "cert_text.tsv") if f[0] == tr[8] and int(f[1]) <= a and b <= int(f[2]))
    q0 = a - int(win[1])
    if win[3][q0:q0 + b - a] != tr[11]:
        sys.exit("Ring certificate: quote is not at its offset in the window")
    pre, post = win[3][:q0], win[3][q0 + b - a:]
    pre = pre[pre.rfind(". ", 0, len(pre) - 150) + 2:] if pre.rfind(". ", 0, len(pre) - 150) > 0 else pre[-260:]
    post = post[:post.find(". ", 90) + 1] if post.find(". ", 90) > 0 else post[:200]
    hold = {f[0]: f for f in rows(C / "data" / "holdings.tsv") if f[1] in (str(WALTON), "6239607", "704585", "548001", "6206754")}
    wh = []
    for f in st_rows:
        if f[0] == str(WALTON) and f[2] != "-" and f[4] == "20261112":
            wh.append([hold[f[2]][3], f[5]])
    wh.sort(key=lambda x: x[1] == "good")
    D["partial"] = dict(by=f"{node[RING][6]}, {cite(RING)}", by_day=day(tr[3]), target=f"{node[WALTON][6]}, {cite(WALTON)} ({node[WALTON][4][:4]})",
                        pre=pre, quote=tr[11], post=post, id=tr[0], start=a, end=b, part=tr[13], kind=tr[4], scope=tr[5], holdings=wh)
    # ---- two dates: Ledbetter and the Fair Pay Act ----
    LED = 6239607
    led = [f for f in st_rows if f[0] == str(LED) and f[5] == "neg:superseded"]
    if len(led) != 1:
        sys.exit("Ledbetter: expected one superseded holding")
    D["led"] = dict(name=node[LED][6], cite=cite(LED), decided=int(node[LED][4]), known=int(led[0][3]), holding=hold[led[0][2]][3])
    sup = next(f for f in rows(C / "data" / "supersessions.tsv") if f[1] == str(LED) and f[2] == led[0][1])
    law = next(f for f in rows(C / "data" / "lawchanges.tsv") if f[0] == sup[3])
    D["led"].update(law=law[1], block=law[2], enacted=int(law[3]), effective=int(law[4]), retro=int(law[5]))
    if D["led"]["enacted"] != D["led"]["known"]:
        sys.exit("Ledbetter: status row and the law's enactment date differ")
    # ---- a split and its resolution: 42 U.S.C. 1997e(a) ----
    iss = next(f for f in rows(C / "data" / "issues.tsv") if f[0] == "usc:42:1997e(a):q12")
    dec = {int(f[0]): int(f[1]) for f in rows(C / "data" / "decisions2.tsv") if int(f[0]) in (704585, 548001, 6206754)}
    cname = {int(f[0]): f[3] for f in rows(C / "data" / "courts2.tsv")}
    side = []
    for nid in (704585, 548001, 6206754):
        h = next(f for f in hold.values() if f[1] == str(nid) and f[2] == iss[0])
        side.append(dict(name=node[nid][6], cite=cite(nid), day=day(node[nid][4]), year=node[nid][4][:4], court=cname[dec[nid]], answer=h[4], quote=h[9]))
    D["split"] = dict(question=iss[4], section="42 U.S.C. § 1997e(a)", sides=side)
    # ---- heatmap: decisions relying on bad law, by day, 1990-2019 ----
    hm = json.loads((C / "report" / "heatmaps" / "heatmaps.json").read_text())["badlaw"]
    y0, y1 = hm["years"]
    years = {y: [0] * ((datetime.date(y + 1, 1, 1) - datetime.date(y, 1, 1)).days) for y in range(y0, y1 + 1)}
    for f in rows(C / "report" / "heatmaps" / "series" / "badlaw.tsv", 1):
        d = int(f[0]); y = d // 10000
        if y in years:
            years[y][(datetime.date(y, d // 100 % 100, d % 100) - datetime.date(y, 1, 1)).days] = int(f[1])
    if sum(map(sum, years.values())) != hm["total"]:
        sys.exit("heatmap series and heatmaps.json disagree")
    pk = hm["peaks"][0]
    D["heat"] = dict(years=[[y, datetime.date(y, 1, 1).weekday(), years[y]] for y in sorted(years)], total=hm["total"], parts=hm["parts"],
                     peak_day=day(pk["day"]), peak=pk["count"], max=max(max(v) for v in years.values()))
    # ---- the hunt ----
    hs = json.loads((C / "hunt" / "summary.json").read_text(encoding="utf-8"))
    S["hunt_confirmed"] = sum(p["counts"].get("confirmed_by_audit", 0) for p in hs["patterns"].values())
    S["hunt_patterns"] = sum(1 for p in hs["patterns"].values() if "confirmed_by_audit" in p["counts"])
    z = hs["patterns"]["p1_zombie"]
    S["zombie_audit"] = [z["audit"]["two_stage"]["confirmed"], z["audit"]["two_stage"]["n"]]
    S["zombie_est"] = [z["counts"]["estimated_true_low"], z["counts"]["estimated_true_high"]]
    hd = None
    zs = []
    for f in rows(C / "hunt" / "data" / "p1_zombies.tsv"):
        if hd is None:
            hd = f; continue
        zs.append(dict(zip(hd, f)))
    od = next(r for r in zs if r["citing_name"].startswith("In re Odyssey"))
    psg = next(json.loads(l) for l in open(C / "hunt" / "work" / "p1_passages.jsonl", encoding="utf-8") if '"citing": %s, "cited": %s,' % (od["citing"], od["cited"]) in l)
    w = psg["windows"][0]
    a = w.index("The Tenth Amendment is a limitation"); b = w.index("(1976).", a) + 7
    c0 = w.index("Nat’l League of Cities v. Usery", a)
    D["zombie"] = dict(citing=f'{od["citing_name"]} {od["citing_cite"]}', court=od["citing_court"], day=day(od["citing_date"]),
                       pre=w[a:c0], hit=w[c0:b], by=f'{od["negated_by"]}, {od["negated_by_cite"]}', by_day=day(od["neg_from"]), by_quote=psg["wquote"],
                       years=(int(od["citing_date"]) - int(od["neg_from"])) // 10000)
    more = []
    for nm in ("United States v. Helsey", "International Ass", "Kimoktoak"):
        r = next(r for r in zs if r["citing_name"].startswith(nm))
        more.append([f'{r["citing_name"]}, {r["citing_cite"]} ({r["citing_date"][:4]})', r["cited_name"], r["negated_by"], r["neg_from"][:4]])
    D["zombie"]["more"] = more
    # ---- evaluation ----
    ev = json.loads((C / "eval" / "results.json").read_text())
    ev1 = json.loads((C / "eval" / "results_v1.json").read_text())
    sc, sc1 = ev["scdb"], ev1["scdb"]
    S.update(scdb_flagged=sc["of_which_flagged"], scdb_admitted=sc["scotus_decisions_with_admitted_overruling_of_scotus"],
             scdb_pct=round(100 * sc["precision"], 1), scdb_all=sc["flagged_decisions"], scdb_found=sc["flagged_with_admitted_overruling"],
             scdb_recall=round(100 * sc["recall"], 1), scdb_v1_pct=round(100 * sc1["precision"]))
    r1 = json.loads((C / "eval" / "results_round1.json").read_text())["scdb"]
    crs = ev["crs"]["current_table"]
    pa = ev["reports"]["precision_of_admitted"]
    if sum(v["admitted"] for v in pa.values()) != ev["inputs"]["admitted"]:
        sys.exit("eval: admitted treatments by kind do not add up")
    S.update(scdb_recall_r1=round(100 * r1["recall"], 1), crs_found=crs["found"], crs_pairs=crs["resolved"], crs_pct=round(100 * crs["recall"], 1),
             eval_admitted=ev["inputs"]["admitted"], eval_kinds=sorted(pa, key=lambda k: -pa[k]["admitted"]))
    bl = json.loads((C / "eval" / "audits" / "notes-blind" / "score.json").read_text())["verdicts"]
    S.update(blind_express=bl["express"], blind_n=sum(bl.values()), blind_pct=round(100 * bl["express"] / sum(bl.values())))
    # ---- the implicit tier: an overruling a later decision states, admitted as a witness row, raises atRisk only ----
    inf = {(f[1], f[2]) for f in rows(C / "out" / "findings.tsv", 1) if f[0] == "atRisk" and f[4].startswith("inferredRejection")}
    wt = [f for f in rows(C / "data" / "treatments.tsv") if f[0].startswith("tw:") and int(f[2]) in IMPL]
    if sorted(int(f[2]) for f in wt) != sorted(IMPL) or any((f[2], f[1]) not in inf for f in wt):
        sys.exit("implicit tier: Plessy, Wolf and Roberts are not all atRisk inferredRejection findings")
    S["implicit_rows"] = len(inf)
    # Brown v. Board of Education on Plessy: in the data only as a witness row (stated by a later decision), not in Brown's own words
    pl = next(f for f in wt if int(f[2]) == IMPL[0])
    brown = next(f for f in rows(W / "graph" / "nodes.tsv") if f[0] == pl[1])
    if not brown[6].startswith("Brown v. Board") or any(f[2] == pl[2] and f[1] == pl[1] and not f[0].startswith("tw:") for f in rows(C / "data" / "treatments.tsv")):
        sys.exit("Brown / Plessy: expected only a witness row")
    D["brown"] = "Brown v. Board of Education"
    D["implicit"] = [node[i][6] for i in IMPL]
    D["S"] = S
    (HERE / "caselaw2_data.json").write_text(json.dumps(D, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(json.dumps(S, indent=1))
    for k in ("law",):
        print(k, json.dumps(D[k], ensure_ascii=False, indent=1)[:2600])
    print("dots", len(D["anat"]["dots"]), "edges", len(D["anat"]["edges"]), "pts", len(pts), "fnd", len(fnd), "kinds", D["kinds"], "findings", D["findings"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--build-data", action="store_true"); ap.add_argument("--share-only", action="store_true")
    a = ap.parse_args()
    if a.build_data:
        return build_data()
    OUT.mkdir(exist_ok=True)
    mp4 = OUT / f"{NAME}.mp4"
    share = OUT / f"{NAME}-share.mp4"
    if not a.share_only:
        from playwright.sync_api import sync_playwright
        data = (HERE / "caselaw2_data.json").read_text(encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch(args=ARGS)
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.add_init_script(f"window.CL2 = {data};")
            msgs = []
            pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
            pg.goto((HERE / "caselaw2_film.html").as_uri())
            try:
                pg.wait_for_function("window.READY === true", timeout=90000)
            except Exception:
                print("\n".join(msgs)); raise
            if a.still is not None:
                for t in a.still:
                    pg.evaluate(f"render({t})")
                    pg.screenshot(path=str(OUT / f"cl2_{t:05.1f}.png"))
                print("\n".join(m for m in msgs if "error" in m.lower())); b.close(); return
            dur = pg.evaluate("window.DUR"); n = int(dur * a.fps)
            cmd = [FF, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-", "-c:v", "h264_nvenc",
                   "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "17", "-b:v", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                   str(mp4)]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            for i in range(n):
                pg.evaluate(f"render({i / a.fps})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
                if i % 300 == 0:
                    print(f"frame {i}/{n}", flush=True)
            ff.stdin.close(); ff.wait(); b.close()
        if ff.returncode:
            sys.exit("ffmpeg failed")
    print(mp4, round(mp4.stat().st_size / 1e6, 1), "MB")
    # share version: second NVENC pass at the reference share bitrate (~3.6 Mbit/s), as render_caselaw.py does
    cmd = [FF, "-y", "-loglevel", "error", "-i", str(mp4), "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr",
           "-b:v", "3600k", "-maxrate", "6000k", "-bufsize", "12000k", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(share)]
    if subprocess.run(cmd).returncode:
        sys.exit("ffmpeg share pass failed")
    print(share, round(share.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
