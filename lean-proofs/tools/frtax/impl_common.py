"""Shared harness for the other implementations (IMPLEMENTATIONS.md): load our benchmarks, run Lean and Mlang
on new returns, score an implementation's outputs against them.

Benchmarks (each a list of cases {id, year, boxes, ...}):
  bareme    data/official_bareme_tables.jsonl: printed brochure cells (tax after QF cap and decote); the household
            each cell stands for is brochure_tables.household(...) + 4BA = taxable income (as bareme_all.py)
  examples  data/official_examples.jsonl: boxes_guess + stated figures (as official_examples_run.py)
  random    runs/final (2024-2025) and runs/old (2020-2023): the returns M accepted, with saved Lean and M outputs
  bound     harness/boundaries.py: returns on statutory thresholds and +-1 EUR (Lean and M run here)
Common output names are the Lean model's: NBPT RNI REVKIRE IDRS (after QF cap, before decote) IDEC IDRS4
(after decote, before reductions) IMPNET (net income tax) CHRAPRES (CEHR).
"""
import collections, glob, json, math, os, re, subprocess, sys, tempfile, shutil, concurrent.futures as cf

FR = os.path.expanduser("~/fr")
LEAN = f"{FR}/lean/.lake/build/bin/frtax"
BIN = f"{FR}/bin"
NCPU = 12
sys.path.insert(0, f"{FR}/harness")


def round_euro(x):
    """art. 193 / 1657: nearest euro, 0.50 counted as 1"""
    return math.floor(x + 0.5)


# ------------------------------------------------------------------ loaders
SITS = {"single": 0, "single, lives alone, raised a child alone >= 5 years (case L)": 1,
        "single, lives alone with children (case T)": 2, "widowed with dependent children": 3, "couple": 4}


def bareme_cases():
    from brochure_tables import household
    out = []
    for i, l in enumerate(open(f"{FR}/data/official_bareme_tables.jsonl")):
        r = json.loads(l)
        f = r["facts"]
        sit, parts, inc = SITS[f["situation"]], float(f["parts"]), int(f["net_taxable_income"])
        b = household(sit, parts)
        out.append({"id": f"bar{i}", "year": r["income_year"], "sit": sit, "parts": parts, "income": inc,
                    "expected": {"IDRS4": r["expected"]["impot_apres_plafonnement_et_decote"]},
                    "boxes": None if b is None else {**b, "4BA": inc}})
    return out


EX_MAP = {"impot_apres_plafonnement": "IDRS", "impot_brut_apres_plafonnement_qf_avant_decote": "IDRS",
          "decote": "IDEC", "impot_apres_decote": "IDRS4", "cehr": "CHRAPRES", "parts": "NBPT", "rfr": "REVKIRE",
          "rref": "REVKIRE", "revenu_net_imposable": "RNI", "impot_brut": "IDRSCAP", "impot_taux_effectif": "IDRSCAP",
          "impot_du": "IAVCR", "impot_net": "IAVCR", "reduction_dons": "ITRED", "reduction": "ITRED", "cdhr": "CDHR"}


def example_cases():
    out = []
    for l in open(f"{FR}/data/official_examples.jsonl"):
        e = json.loads(l)
        b = e.get("boxes_guess")
        if not b or e["income_year"] not in range(2020, 2026):
            continue
        b = dict(b)
        for cnt, pre in (("0CF", "0F"), ("0CH", "0H"), ("0DJ", "0J")):
            for i in range(int(b.get(cnt, 0))):
                b.setdefault(f"{pre}{i}", e["income_year"] - (20 if cnt == "0DJ" else 10))
        for k in ("0DA", "0DB"):
            if k == "0DA" or "0AM" in b or "0AO" in b:
                b.setdefault(k, 1980)
        exp = {EX_MAP[k]: v for k, v in e["expected"].items() if k in EX_MAP and isinstance(v, (int, float))}
        if exp:
            out.append({"id": e["id"], "year": e["income_year"], "boxes": b, "expected": exp, "flags": e.get("flags")})
    return out


def read_irj(path):
    b, sec = {}, None
    for line in open(path):
        line = line.strip()
        if line.startswith("#"):
            sec = line
            continue
        if sec == "#ENTREES-PRIMITIF" and "/" in line:
            k, v = line.split("/", 1)
            if k not in ("REGCO", "ANREV"):
                b[k] = int(float(v))
    return b


def random_cases(which):
    """which: 'final' (2024-2025) or 'old' (2020-2023): the returns M accepted, with saved 'lean' and 'm' outputs.
    Boxes are read lazily (fill_boxes)."""
    d = f"{FR}/runs/{which}"
    lean = {j["id"]: j for j in map(json.loads, open(f"{d}/lean.jsonl"))}
    m = {j["id"]: j for j in map(json.loads, open(f"{d}/m.jsonl"))}
    out = []
    for ydir in sorted(glob.glob(f"{d}/in20*")):
        year = int(ydir[-4:])
        for p in os.listdir(ydir):
            cid = p[:-4]
            if cid in m:
                out.append({"id": f"{which}_{year}_{cid}", "src_id": cid, "year": year, "boxes": None,
                            "_path": f"{ydir}/{p}", "lean": lean.get(cid), "m": m_as_common(m[cid])})
    return out


def fill_boxes(cases):
    for c in cases:
        if c["boxes"] is None and "_path" in c:
            c["boxes"] = read_irj(c["_path"])
    return cases


COMPL_BOXES = ("0AP", "0AF", "0AW", "0AS", "0AG", "0CG", "0CI", "0CR")


def sim_common(s, boxes=None):
    """A saved production-simulator answer (sim_run.parse) under the common names; None if production refused.
    Production's "Droits simples" is the tax after the QF cap but before the complementary reductions of art. 197,
    I, 2 (invalidity, veterans, widow(er)s: M IDRS2, Lean IDRSCAP), so it is read as IDRS (and IDRS4 = IDRS - IDEC)
    only for returns where none of them can apply."""
    if not s or s.get("_error") or "NBPT" not in s:
        return None
    d = {k: s.get(k) for k in ("NBPT", "REVKIRE", "RNI")}
    b = boxes or {}
    no_compl = not any(b.get(k) for k in COMPL_BOXES) and not (b.get("0AV") and (b.get("0CF") or b.get("0CH")))
    if "IDRS" in s:
        d["IDRSCAP"] = s["IDRS"]
        d["IDEC"] = s.get("IDEC", 0.0)
        if no_compl:
            d["IDRS"] = s["IDRS"]
            d["IDRS4"] = s["IDRS"] - d["IDEC"]
    if "CEHR" in s:  # a page with no CEHR line is not read as 0 (h5425: CEHR not printed under that label)
        d["CHRAPRES"] = s["CEHR"]
    d["IAVCR"] = s.get("AVCR")
    d["IRNET"] = s.get("IRNET")
    return d


def sim_cases():
    """Every saved production-simulator answer (runs/*sim*.jsonl, earlier work) whose return we have, deduplicated
    (a refetch replaces the first answer). Each case: {id, year, boxes, sim, expected (common names)}."""
    R = f"{FR}/runs"
    boxes = {}
    for p in (f"{R}/targets.jsonl", f"{R}/fam_targets.jsonl", f"{R}/loop/sim_cases.jsonl",
              f"{R}/ofsuite/sim_cases.jsonl", f"{R}/ofsuite/sim_cases2.jsonl", f"{R}/pas/prod_cases.jsonl",
              f"{R}/impl/sim_cases.jsonl"):
        if os.path.exists(p):
            for l in open(p):
                c = json.loads(l)
                boxes[(c["id"], c["year"])] = c["boxes"]
    ans = {}
    for p in (f"{R}/sim2.jsonl", f"{R}/sim_targets_v2.jsonl", f"{R}/sim_fam.jsonl", f"{R}/loop/sim.jsonl",
              f"{R}/ofsuite/sim.jsonl", f"{R}/pas/sim_prod.jsonl", f"{R}/sim_refetch.jsonl", f"{R}/impl/sim.jsonl"):
        if os.path.exists(p):
            src = os.path.relpath(p, R)
            for l in open(p):
                a = json.loads(l)
                key = (a["id"], a["year"])
                if key not in boxes and a["id"].startswith("h"):
                    ip = f"{R}/final/in{a['year']}/{a['id']}.irj"
                    if os.path.exists(ip):
                        boxes[key] = read_irj(ip)
                if key in boxes:
                    ans[key] = (src, a["sim"])
    out = []
    for (cid, year), (src, s) in ans.items():
        out.append({"id": f"sim_{src.replace('/', '_').replace('.jsonl', '')}_{cid}_{year}", "src": src, "year": year,
                    "boxes": boxes[(cid, year)], "sim": s, "expected": sim_common(s, boxes[(cid, year)])})
    return out


def bound_cases():
    p = f"{FR}/runs/impl/bound.jsonl"
    subprocess.run([sys.executable, f"{FR}/harness/boundaries.py", p], capture_output=True)
    return [json.loads(l) for l in open(p)]


# ------------------------------------------------------------------ Lean / Mlang on new returns
MVARS = ["NBPT", "RNG", "RNI", "IDRS", "IDRS2", "IDRS3", "IDRS4", "IDEC", "ITRED", "IAN", "IRN", "IRE", "REVKIRE",
         "CHRAPRES", "CDHR", "PSNET", "IPROP", "IINET", "NAPCR"]


def run_lean(cases):
    """cases with id, year, boxes -> {id: Lean outputs}"""
    lines = [f"{c['id']};{c['year']};" + ",".join(f"{k}={int(v)}" for k, v in c["boxes"].items()) for c in cases]
    out = {}
    if not lines:
        return out
    k = max(500, len(lines) // NCPU + 1)
    chunks = ["\n".join(lines[i:i + k]) + "\n" for i in range(0, len(lines), k)]

    def go(t):
        return subprocess.run([LEAN], input=t, capture_output=True, text=True).stdout
    with cf.ThreadPoolExecutor(NCPU) as ex:
        for s in ex.map(go, chunks):
            for ln in s.splitlines():
                p = ln.split(";")
                if p[0] != "ERR":
                    out[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    return out


def run_m(cases):
    """-> ({id: common-named M outputs}, {id: KO code}); ids must be file-name safe."""
    work = tempfile.mkdtemp(prefix="m_", dir=f"{FR}/runs/impl")
    tasks = []
    for year in sorted({c["year"] for c in cases}):
        ind, outd = f"{work}/in{year}", f"{work}/out{year}"
        os.makedirs(ind); os.makedirs(outd)
        files = []
        for c in cases:
            if c["year"] == year:
                p = f"{ind}/{c['id']}.irj"
                body = ["#NOM", c["id"], "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{year}"]
                body += [f"{k}/{int(v)}" for k, v in sorted(c["boxes"].items())]
                body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                         "#RESULTATS-CORRECTIF", "##"]
                open(p, "w").write("\n".join(body) + "\n")
                files.append(p)
        k = max(1, len(files) // NCPU + 1)
        tasks += [(year, files[i:i + k], outd) for i in range(0, len(files), k)]

    def go(a):
        year, files, outd = a
        return subprocess.run([f"{BIN}/cal{year}", "-completion", "-m", "p", "-a", str(year), "-dst", outd] + files,
                              capture_output=True, text=True).stdout
    with cf.ThreadPoolExecutor(NCPU) as ex:
        logs = "".join(ex.map(go, tasks))
    ko, last = {}, None
    for ln in logs.splitlines():
        mm = re.search(r"KO \| (\S+)", ln)
        if mm:
            last = mm.group(1)
        mm = re.search(r'"([^"/]+)\.irj" KO', ln)
        if mm:
            ko[mm.group(1)] = last or "?"
            last = None
    res = {}
    pat = "^(" + "|".join(MVARS) + ")/"
    for year in sorted({c["year"] for c in cases}):
        r = subprocess.run(f"find {work}/out{year} -name '*.irj' -print0 | xargs -0 -r -n 2000 grep -H -E '{pat}'",
                           shell=True, capture_output=True, text=True)
        for l in r.stdout.splitlines():
            path, _, kv = l.partition(":")
            k, _, v = kv.partition("/")
            d = res.setdefault(os.path.basename(path)[:-4], {})
            if k not in d:
                d[k] = float(v)
    shutil.rmtree(work, ignore_errors=True)
    for cid in [c for c, v in res.items() if not v.get("NBPT")]:
        ko.setdefault(cid, "no parts")
        del res[cid]
    return {k: m_as_common(v) for k, v in res.items()}, ko


def m_as_common(mv):
    """M variables under the common (Lean) names."""
    if mv is None:
        return None
    d = {k: mv.get(k) for k in ("NBPT", "RNI", "REVKIRE", "IDRS", "IDEC", "IDRS4", "CHRAPRES", "CDHR", "ITRED")}
    d["IMPNET"] = mv.get("IRN")
    return d


# ------------------------------------------------------------------ scoring
def cmp(x, ref, field):
    """'eq' exact (x rounded to the euro; parts exact), 'le1'/'le2' within 1/2 EUR, 'ne' otherwise, 'na' missing."""
    if x is None or ref is None:
        return "na"
    if field == "NBPT":
        return "eq" if abs(x - ref) < 1e-6 else "ne"
    d = abs(round_euro(x) - ref)
    return "eq" if d < 0.01 else ("le1" if d <= 1.01 else ("le2" if d <= 2.01 else "ne"))


def score(rows, fields, refs=("lean", "m", "expected")):
    """rows: [{id, year, boxes, impl:{...}, lean:{...}, m:{...}, expected:{...}}] -> (summary, disagreements)"""
    s = {r: collections.Counter() for r in refs}
    dis = []
    for row in rows:
        for ref in refs:
            rv = row.get(ref)
            if not rv:
                continue
            # a figure the implementation leaves out on purpose (None in an answer that has others) is not compared
            fs = [f for f in fields if rv.get(f) is not None and (row["impl"].get(f) is not None or not row["impl"])]
            if not fs:
                continue
            res = {f: cmp(row["impl"].get(f), rv[f], f) for f in fs}
            s[ref]["n"] += 1
            s[ref]["all_eq"] += all(v == "eq" for v in res.values())
            s[ref]["all_le2"] += all(v in ("eq", "le1", "le2") for v in res.values())
            for f, v in res.items():
                s[ref][f + "_n"] += 1
                s[ref][f + "_eq"] += v == "eq"
            if ref != "m" and any(v != "eq" for v in res.values()):
                dis.append({"id": row["id"], "ref": ref, "bad": [f for f, v in res.items() if v != "eq"],
                            "year": row.get("year"), "boxes": row.get("boxes"),
                            "impl": {f: row["impl"].get(f) for f in fields},
                            "lean": {f: (row.get("lean") or {}).get(f) for f in fields},
                            "m": {f: (row.get("m") or {}).get(f) for f in fields},
                            "expected": row.get("expected")})
    return {r: dict(v) for r, v in s.items()}, dis


def fmt_summary(name, s, fields):
    out = []
    for ref, c in s.items():
        if not c.get("n"):
            continue
        per = ", ".join(f"{f} {c.get(f + '_eq', 0)}/{c.get(f + '_n', 0)}" for f in fields if c.get(f + "_n"))
        out.append(f"  {name} vs {ref}: {c['n']} cases; every compared figure equal {c['all_eq']}/{c['n']} "
                   f"({100 * c['all_eq'] / c['n']:.1f} %); within 2 EUR {c['all_le2']}/{c['n']}; per figure: {per}")
    return "\n".join(out)
