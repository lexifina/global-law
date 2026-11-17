"""Courts as test cases, step 4: run every extracted case through Lean (frtax) and M (Mlang, cal<year>), and
optionally the production simulator, and score each figure the court states.

usage:
  python3 -I harness/court_run.py merge            # data/court/cases_*.jsonl -> data/court/cases.jsonl (+ review defaults)
  python3 -I harness/court_run.py run              # Lean + M -> runs/court/results.jsonl
  python3 -I harness/court_run.py sim [MAX]        # production simulator for complete 2020-2025 cases (flock, 1.2 s)
  python3 -I harness/court_run.py score            # -> runs/court/scores.json + printed scoreboards

Years: Lean covers income 2020-2025; M exists for 2018 (release 6.7, ~/fr/hist/bin) and 2019-2025 (~/fr/bin).
A figure that does not depend on the year's parameters (year_independent, e.g. a number of parts) of an earlier
year is run as income 2020 in Lean and 2018 in M ("proxy year"); other figures of 2015-2017 are not scored.
"""
import collections, copy, fcntl, glob, json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

H = os.path.expanduser("~/fr")
D = f"{H}/data/court"
R = f"{H}/runs/court"
LEAN = f"{H}/lean/.lake/build/bin/frtax"
sys.path.insert(0, f"{H}/harness")
from of_calc_tests import LEAN_BOXES  # noqa: E402

SIT = ("0AM", "0AO", "0AC", "0AD", "0AV")
SAL = {"A": ("1AJ", "1AK"), "B": ("1BJ", "1BK"), "C": ("1CJ", "1CK"), "D": ("1DJ", "1DK")}
PEN = {"A": "1AS", "B": "1BS", "C": "1CS", "D": "1DS"}
MICRO = ("5KO", "5KP", "5HQ", "5ND", "5OD", "5PD", "5LO", "5LP", "5IQ", "5MO", "5MP", "5JQ", "5TA", "5TB", "5TE", "5UA", "5UB", "5UE", "4BE")
ALIM = ("6EL", "6EM", "6GU", "6GP", "6GI", "6GJ")
RED_BOXES = {"DONS": ("7UF", "7UD", "7VA", "7VC", "7UH"), "EMPLOI": ("7DB", "7DR", "7DQ", "7DL", "7DG", "7DD"),
             "GARDE": ("7GA", "7GB", "7GC", "7GE", "7GF", "7GG"), "PRESTCOMP": ("7WN", "7WO", "7WP", "7WM")}


def lean_year(c):
    y = c["income_year"]
    if 2020 <= y <= 2025:
        return y, False
    if c.get("year_independent") and 2010 <= y < 2020:
        return 2020, True
    return None, False


def m_year(c):
    y = c["income_year"]
    if 2018 <= y <= 2025:
        return y, False
    if c.get("year_independent") and 2010 <= y < 2018:
        return 2018, True
    return None, False


def m_bin(y):
    return f"{H}/hist/bin/cal_sources2018m_6_7" if y == 2018 else f"{H}/bin/cal{y}"


def complete_boxes(b, y):
    """Defaults the programs need and the decisions rarely give: birth years of declarants and children.
    Returns (boxes, list of defaults applied)."""
    b = {k: int(round(float(v))) for k, v in b.items() if v not in (None, "", 0) or k in ("0CF",)}
    added = []
    if not any(k in b for k in SIT):
        b["0AC"] = 1
        added.append("0AC (situation not given)")
    couple = "0AM" in b or "0AO" in b
    if "0DA" not in b:
        b["0DA"] = 1980
        added.append("0DA=1980")
    if couple and "0DB" not in b:
        b["0DB"] = 1980
        added.append("0DB=1980")
    for cnt, pre, age in (("0CF", "0F", 10), ("0CH", "0H", 10), ("0DJ", "0J", 20)):
        for i in range(int(b.get(cnt, 0))):
            if f"{pre}{i}" not in b:
                b[f"{pre}{i}"] = y - age
                if i == 0:
                    added.append(f"{pre}* birth years={y - age}")
    return b, added


def in_lean_scope(b):
    return all(k in LEAN_BOXES or re.fullmatch(r"0[FHJ]\d", k) for k in b)


def run_lean(jobs):
    """jobs: list of (key, year, boxes) -> {key: outputs}"""
    inp = "".join(f"{k};{y};" + ",".join(f"{a}={v}" for a, v in b.items()) + "\n" for k, y, b in jobs)
    out = {}
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    for l in r.stdout.splitlines():
        p = l.split(";")
        try:
            out[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
        except ValueError:
            out[p[0]] = {"_error": l[:200]}
    return out


MV = ("NBPT", "RNI", "RNG", "RBG", "REVKIRE", "IDRS2", "IDRS3", "IDEC", "IAN", "IRE", "ITRED", "IRN", "CHRAPRES",
      "CDHR", "IPROP", "IINET", "TSN", "BON", "REPDON", "RON", "RBG1")


def run_m_one(job):
    key, y, b = job
    d = tempfile.mkdtemp(prefix="court_m_")
    os.makedirs(d + "/o")
    body = ["#NOM", "X", "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{y}"] + [f"{k}/{v}" for k, v in b.items()]
    body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
             "#RESULTATS-CORRECTIF", "##"]
    open(d + "/x.irj", "w").write("\n".join(body) + "\n")
    r = subprocess.run([m_bin(y), "-completion", "-m", "p", "-a", str(y), "-dst", d + "/o", d + "/x.irj"],
                       capture_output=True, text=True)
    ko = re.findall(r"KO \| (\S+)", r.stdout)
    vals = {}
    if os.path.exists(d + "/o/x.irj"):
        for line in open(d + "/o/x.irj"):
            k = line.split("/")[0]
            if k in MV and k not in vals:
                try:
                    vals[k] = float(line.split("/")[1])
                except ValueError:
                    pass
    subprocess.run(["rm", "-rf", d])
    if ko or not vals.get("NBPT"):
        return key, {"_refused": ",".join(ko) or "no output"}
    return key, vals


def run_m(jobs):
    with ThreadPoolExecutor(10) as ex:
        return dict(ex.map(run_m_one, jobs))


def variants(c, b):
    """Extra runs needed to derive figures that are not a direct output (allowances, deductions)."""
    v = {}
    want = set(c.get("court_figures", {}))
    if "ABAT10" in want:
        for p, (sj, sk) in SAL.items():
            if sj in b and sk not in b:
                v[f"sal{p}"] = {"0AC": 1, "0DA": 1980, sj: b[sj]}
            if PEN[p] in b:
                v[f"pen{p}"] = {"0AC": 1, "0DA": 1980, PEN[p]: b[PEN[p]]}
    if "MICRO_ABAT" in want:
        m = {k: b[k] for k in MICRO if k in b}
        if m:
            v["micro"] = {"0AC": 1, "0DA": 1980, **m}
    if "PA_DED" in want:
        v["noalim"] = {k: x for k, x in b.items() if k not in ALIM}
        if not any(re.fullmatch(r"[1-5]\w\w", k) for k in b):  # no income stated: probe with a salary so the
            probe = "1AJ"                                         # deduction shows in the taxable income
            v["alimP"] = {**b, probe: 300000}
            v["noalimP"] = {**v["noalim"], probe: 300000}
    if "A157BIS" in want:
        v["young"] = {**b, "0DA": 1980, **({"0DB": 1980} if "0DB" in b else {})}
    for name, boxes in RED_BOXES.items():
        if f"RED_{name}" in want or f"CRED_{name}" in want:
            v[f"no{name}"] = {k: x for k, x in b.items() if k not in boxes}
    return v


def merge():
    rows, seen = [], set()
    for f in sorted(glob.glob(f"{D}/cases_b*.jsonl")):
        for l in open(f):
            if not l.strip():
                continue
            c = json.loads(l)
            key = (c["source_id"], c["income_year"], json.dumps(c.get("boxes"), sort_keys=True))
            if key in seen:
                continue
            seen.add(key)
            c["batch"] = os.path.basename(f)[6:-6]
            rows.append(c)
    cur = json.load(open(f"{D}/curation.json")) if os.path.exists(f"{D}/curation.json") else {}
    for c in rows:
        e = cur.get(c["case_id"])
        if not e:
            continue
        c["curated"] = True
        if "set_boxes" in e:
            c["boxes"] = dict(e["set_boxes"])
        c["boxes"] = {**(c.get("boxes") or {}), **e.get("add_boxes", {})}
        if "alt_boxes" in e:
            c["alt_boxes"] = e["alt_boxes"]
        figs = c.get("court_figures") or {}
        for old, new in e.get("rename_figures", {}).items():
            if old in figs:
                figs[new] = figs.pop(old)
        dropped = {k: {"figure": figs.pop(k), "why": why} for k, why in e.get("drop_figures", {}).items() if k in figs}
        if dropped:
            c["dropped_figures"] = dropped
        figs.update(e.get("add_figures", {}))
        c["court_figures"] = figs
        c["assumptions"] = (c.get("assumptions") or []) + e.get("assumptions_add", [])
        for k in ("completeness", "year_independent", "sim", "excluded"):
            if k in e:
                c[k] = e[k]
    with open(f"{D}/cases.jsonl", "w") as fo:
        for c in rows:
            fo.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("cases", len(rows), collections.Counter(c["batch"] for c in rows))


def run():
    cases = [json.loads(l) for l in open(f"{D}/cases.jsonl")]
    lean_jobs, m_jobs, meta = [], [], {}
    for c in cases:
        scen = {"court": c.get("boxes") or {}}
        for k, bx in (c.get("alt_boxes") or {}).items():
            if bx:
                scen[k] = bx
        ly, lproxy = lean_year(c)
        my, mproxy = m_year(c)
        meta[c["case_id"]] = {"lean_year": ly, "lean_proxy": lproxy, "m_year": my, "m_proxy": mproxy, "defaults": {}}
        for s, bx in scen.items():
            runs = {"": bx}
            if s == "court":
                runs.update({"~" + k: x for k, x in variants(c, bx).items()})
            for suffix, raw in runs.items():
                key = f"{c['case_id']}|{s}{suffix}"
                if ly:
                    b, added = complete_boxes(raw, ly)
                    if not suffix:
                        meta[c["case_id"]]["defaults"][s] = added
                    if in_lean_scope(b):
                        lean_jobs.append((key, ly, b))
                if my:
                    b, added = complete_boxes(raw, my)
                    if not suffix and s not in meta[c["case_id"]]["defaults"]:
                        meta[c["case_id"]]["defaults"][s] = added
                    m_jobs.append((key, my, b))
    lean = run_lean(lean_jobs) if lean_jobs else {}
    m = run_m(m_jobs) if m_jobs else {}
    os.makedirs(R, exist_ok=True)
    with open(f"{R}/results.jsonl", "w") as fo:
        for c in cases:
            cid = c["case_id"]
            res = {"case_id": cid, **meta[cid], "lean": {}, "m": {}}
            for k, v in lean.items():
                if k.split("|")[0] == cid:
                    res["lean"][k.split("|", 1)[1]] = v
            for k, v in m.items():
                if k.split("|")[0] == cid:
                    res["m"][k.split("|", 1)[1]] = v
            bx =complete_boxes(c.get("boxes") or {}, meta[cid]["lean_year"] or 2020)[0]
            res["lean_out_of_scope"] = sorted(k for k in bx if not (k in LEAN_BOXES or re.fullmatch(r"0[FHJ]\d", k)))
            fo.write(json.dumps(res) + "\n")
    print("lean runs", len(lean_jobs), "m runs", len(m_jobs))


# --- figures -----------------------------------------------------------------------------------------------
def fig(prog, out, key):
    """value of a court-figure KEY from one program's outputs dict (scenario 'court' and its variants)."""
    o = out.get("court") or {}
    if not o or "_refused" in o or "_error" in o:
        return None
    g = lambda d, k: None if d is None or d.get(k) is None else float(d[k])  # noqa: E731
    if prog == "lean":
        direct = {"NBPT": "NBPT", "RNI": "RNI", "REVKIRE": "REVKIRE", "IDRS": "IDRSCAP", "IDEC": "IDEC",
                  "ITRED": "ITRED", "CEHR": "CHRAPRES", "PFU": "PFU", "RNG": "RNG"}
        ir_net = lambda d: None if g(d, "IAVCR") is None else g(d, "IAVCR") - (g(d, "CITOT") or 0)  # noqa: E731
        ir_bc = lambda d: g(d, "IAVCR")  # noqa: E731
        red = lambda d: None if d is None or g(d, "ITRED") is None else g(d, "ITRED") + (g(d, "CITOT") or 0)  # noqa: E731
    elif prog == "m":
        direct = {"NBPT": "NBPT", "RNI": "RNI", "RBG": "RBG1", "REVKIRE": "REVKIRE", "IDRS": "IDRS2", "IDEC": "IDEC",
                  "ITRED": "ITRED", "CEHR": "CHRAPRES", "PFU": "IPROP", "RNG": "RNG",
                  "DONS_BASE": "BON", "DONS_CARRY": "REPDON"}
        ir_net = lambda d: None if g(d, "IAN") is None else g(d, "IAN") - (g(d, "IRE") or 0)  # noqa: E731
        ir_bc = lambda d: g(d, "IAN")  # noqa: E731
        red = lambda d: None if d is None or g(d, "ITRED") is None else g(d, "ITRED") + (g(d, "IRE") or 0)  # noqa: E731
    else:  # production simulator
        direct = {"NBPT": "NBPT", "RNI": "RNI", "REVKIRE": "REVKIRE", "IDRS": "IDRS", "IDEC": "IDEC", "ITRED": "ITRED",
                  "CEHR": "CEHR", "PFU": "PROP", "RBG": "RBG"}
        ir_net = lambda d: None if g(d, "IRNET") is None else g(d, "IRNET") - (g(d, "CEHR") or 0) - (g(d, "CDHR") or 0)  # noqa: E731
        ir_bc = lambda d: None  # noqa: E731
        red = lambda d: g(d, "ITRED")  # noqa: E731
    if key in direct:
        v = g(o, direct[key])
        if v is None and key in ("IDEC", "ITRED", "CEHR", "PFU"):
            v = 0.0
        return [v] if v is not None else None
    if key == "IR_NET":
        return [x for x in (ir_net(o), ir_bc(o)) if x is not None] or None  # [after credits, before credits]
    if key == "CRED_TOTAL":
        k = {"lean": "CITOT", "m": "IRE"}.get(prog)
        return None if k is None or g(o, k) is None else [g(o, k)]
    if key == "TAX_DELTA":  # the losing (or other stated) version minus the court's
        a = out.get("administration") or next((v for k, v in out.items() if not k.startswith("court")), None)
        if a and "_refused" not in a and ir_net(a) is not None:
            return [ir_net(a) - ir_net(o)] + ([ir_bc(a) - ir_bc(o)] if ir_bc(a) is not None else [])
        return None
    return None


def derived(prog, out, key, boxes):
    """figures computed from variant runs: returns list of candidate values, or None."""
    g = lambda d, k: None if not d or "_refused" in d or d.get(k) is None else float(d[k])  # noqa: E731
    o = out.get("court")
    if key == "ABAT10":
        vals, tot = [], {"sal": 0.0, "pen": 0.0}
        for p in SAL:
            for kind, box in (("sal", SAL[p][0]), ("pen", PEN[p])):
                rni = g(out.get(f"court~{kind}{p}"), "RNI")
                if rni is not None and box in boxes:
                    a = boxes[box] - rni
                    vals.append(a)
                    tot[kind] += a
        if vals:
            vals += [tot["sal"], tot["pen"], tot["sal"] + tot["pen"]]
        return vals or None
    if key == "MICRO_ABAT":
        rni = g(out.get("court~micro"), "RNI")
        if rni is None:
            return None
        return [sum(boxes.get(k, 0) for k in MICRO) - rni]
    if key == "PA_DED":
        a, b = g(out.get("court~noalim"), "RNI"), g(o, "RNI")
        if "court~alimP" in out:  # no income stated: deduction measured on a probe salary
            a, b = g(out.get("court~noalimP"), "RNI"), g(out.get("court~alimP"), "RNI")
        return None if a is None or b is None else [a - b]
    if key == "A157BIS":
        a, b = g(out.get("court~young"), "RNI"), g(o, "RNI")
        return None if a is None or b is None else [a - b]
    m = re.fullmatch(r"(?:RED|CRED)_(\w+)", key)
    if m and m.group(1) in RED_BOXES:
        cr = "CITOT" if prog == "lean" else "IRE"
        x, y = out.get(f"court~no{m.group(1)}"), o
        if g(x, "ITRED") is None or g(y, "ITRED") is None:
            return None
        return [(g(y, "ITRED") + (g(y, cr) or 0)) - (g(x, "ITRED") + (g(x, cr) or 0)),
                g(y, "ITRED") - g(x, "ITRED")]
    return None


def values(prog, out, key, boxes):
    m = re.fullmatch(r"(?:RED|CRED)_(\w+)", key)
    if key in ("ABAT10", "MICRO_ABAT", "PA_DED", "A157BIS") or (m and m.group(1) in RED_BOXES):
        return derived(prog, out, key, boxes)
    return fig(prog, out, key)


def tol(key, want):
    return 0.01 if key == "NBPT" else 1.0


def sim(maxn):
    sys.path.insert(0, f"{H}/harness")
    import sim_run
    cases = [json.loads(l) for l in open(f"{D}/cases.jsonl")]
    out_path = f"{R}/sim.jsonl"
    done = {json.loads(l)["key"] for l in open(out_path)} if os.path.exists(out_path) else set()
    todo = []
    simkeys = {"NBPT", "RNI", "RBG", "REVKIRE", "IDRS", "IDEC", "ITRED", "IR_NET", "CEHR", "PFU", "TAX_DELTA",
               "A157BIS", "PA_DED"}
    # complete returns first, then partial ones, then parts-only
    order = {"full": 0, "partial": 1, "parts_only": 2}
    for c in sorted(cases, key=lambda c: order.get(c.get("completeness"), 3)):
        y = c["income_year"]
        figs = set(c.get("court_figures") or {}) & simkeys
        if not (2020 <= y <= 2025) or not figs or c.get("sim") is False or c.get("excluded"):
            continue
        if any(not (k in LEAN_BOXES or re.fullmatch(r"0[FHJ]\d", k)) for k in c["boxes"]):
            continue  # boxes the simulator's form may not carry (quotient lines etc.)
        todo.append((f"{c['case_id']}|court", y, complete_boxes(c["boxes"], y)[0]))
        alts = c.get("alt_boxes") or {}
        if "TAX_DELTA" in figs and alts:
            k, bx = ("administration", alts["administration"]) if "administration" in alts else next(iter(alts.items()))
            todo.append((f"{c['case_id']}|{k}", y, complete_boxes(bx, y)[0]))
        vs = variants(c, c["boxes"])
        if "alimP" in vs:
            vs.pop("noalim")  # without income the deduction is measured on the probe pair only
        for k, bx in vs.items():
            if k in ("young", "noalim", "alimP", "noalimP") and figs & {"A157BIS", "PA_DED"}:
                todo.append((f"{c['case_id']}|court~{k}", y, complete_boxes(bx, y)[0]))
    print("sim candidates", len(todo), [t[0] for t in todo])
    todo = [t for t in todo if t[0] not in done][:maxn]
    print("sim requests", len(todo))
    if not todo:
        return
    os.makedirs(out_path + ".html", exist_ok=True)
    with open(f"{H}/.sim.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(out_path, "a") as f:
            for key, y, b in todo:
                try:
                    page = sim_run.post(y, b)
                    open(f"{out_path}.html/{key.replace('|', '__')}.html", "w", encoding="latin-1", errors="replace").write(page)
                    r = sim_run.parse(page)
                except Exception as e:  # noqa: BLE001
                    r = {"_error": repr(e)[:200]}
                f.write(json.dumps({"key": key, "year": y, "sim": r}) + "\n")
                f.flush()
                time.sleep(1.2)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("SIM-DONE")


def score():
    cases = {(c := json.loads(l))["case_id"]: c for l in open(f"{D}/cases.jsonl")}
    res = {(r := json.loads(l))["case_id"]: r for l in open(f"{R}/results.jsonl")}
    simr = collections.defaultdict(dict)
    if os.path.exists(f"{R}/sim.jsonl"):
        for l in open(f"{R}/sim.jsonl"):
            d = json.loads(l)
            cid, s = d["key"].split("|")
            simr[cid][s] = d["sim"]
    rows = []
    for cid, c in cases.items():
        r = res.get(cid, {})
        boxes = complete_boxes(c.get("boxes") or {}, r.get("lean_year") or r.get("m_year") or 2020)[0]
        for key, f in (c.get("court_figures") or {}).items():
            want = f.get("value") if isinstance(f, dict) else f
            if not isinstance(want, (int, float)):
                continue
            row = {"case_id": cid, "key": key, "court": want, "year": c["income_year"], "topic": c.get("topic"),
                   "who": f.get("who") if isinstance(f, dict) else None, "batch": c.get("batch")}
            for prog, out in (("lean", r.get("lean", {})), ("m", r.get("m", {})), ("prod", simr.get(cid, {}))):
                if prog == "lean" and r.get("lean_out_of_scope"):
                    row[prog] = {"status": "out_of_scope", "boxes": r["lean_out_of_scope"]}
                    continue
                if prog != "prod" and not out:
                    row[prog] = {"status": "not_run"}
                    continue
                if prog == "prod" and not out:
                    continue
                co = out.get("court") or {}
                if "_refused" in co or "_error" in co:
                    row[prog] = {"status": "refused", "why": co.get("_refused") or co.get("_error")}
                    continue
                vals = values(prog, out, key, boxes)
                if vals is None:
                    row[prog] = {"status": "no_equivalent"}
                    continue
                hit = [i for i, v in enumerate(vals) if v is not None and abs(v - want) <= tol(key, want)]
                row[prog] = {"status": "match" if hit else "mismatch", "value": vals[0], "alts": vals[1:],
                             "matched_alt": hit[0] if hit else None}
            row["proxy"] = bool(r.get("lean_proxy") or r.get("m_proxy"))
            rows.append(row)
    json.dump(rows, open(f"{R}/scores.json", "w"), indent=1, ensure_ascii=False)
    # scoreboards
    sb = collections.defaultdict(collections.Counter)
    for row in rows:
        for prog in ("lean", "m", "prod"):
            st = row.get(prog, {}).get("status")
            if st:
                sb[prog][st] += 1
    for prog in ("lean", "m", "prod"):
        print(prog, dict(sb[prog]))
    by = collections.defaultdict(collections.Counter)
    for row in rows:
        for prog in ("lean", "m", "prod"):
            st = row.get(prog, {}).get("status")
            if st in ("match", "mismatch"):
                by[(prog, row["key"])][st] += 1
    for (prog, key), cnt in sorted(by.items()):
        print(f"  {prog:5} {key:12} {cnt['match']}/{cnt['match'] + cnt['mismatch']}")
    print("mismatches:")
    for row in rows:
        if any(row.get(p, {}).get("status") == "mismatch" for p in ("lean", "m", "prod")):
            print(" ", row["case_id"], row["key"], "court", row["court"],
                  {p: (row[p].get("value"), row[p].get("alts")) for p in ("lean", "m", "prod") if p in row and "value" in row[p]})


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "merge":
        merge()
    elif cmd == "run":
        run()
    elif cmd == "sim":
        sim(int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    elif cmd == "score":
        score()
