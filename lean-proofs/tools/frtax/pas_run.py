"""Withholding rates (art. 204 H, 204 M): Lean against Mlang (the DGFiP's M code), household by household.

usage: pas_run.py reuse RUN_DIR OUT_DIR            # cases and M outputs already in RUN_DIR/in<year>, out<year> (run.py)
       pas_run.py fresh CASES.jsonl OUT_DIR [jobs]  # runs M first (run.py's driver)
Writes OUT_DIR/pas_m.jsonl, pas_lean.jsonl, pas_diffs.jsonl, pas_report.txt.
"""
import json, os, subprocess, sys, collections, shutil
import concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
MV = ["RASTXFOYER", "RASTXDEC1", "RASTXDEC2", "PASNUMF", "PASDENF", "IRTOTAL", "TSRASF", "REVACOMP", "REVTOT",
      "INDTAZ", "TXPASMIN", "NBPT", "IDRS4", "IDRS3", "IDEC", "REVKIRE", "TXINDIV1", "TXINDIV2", "PASNUMI1", "PASDENI1",
      "PASNUMI2", "PASDENI2", "IRINDIV1", "REVINDIV", "INDPAS", "IRN", "INDIRN1", "IITAZIR"]


def read_irj_boxes(path):
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


def grep_m(outdirs):
    m = {}
    pat = "^(" + "|".join(MV) + ")/"
    for outd in outdirs:
        r = subprocess.run(f"find {outd} -name '*.irj' -print0 | xargs -0 -n 2000 grep -H -E '{pat}'",
                           shell=True, capture_output=True, text=True)
        for line in r.stdout.splitlines():
            path, kv = line.split(":", 1)
            k, v = kv.split("/", 1)
            m.setdefault(os.path.basename(path)[:-4], {}).setdefault(k, float(v))
    return {k: v for k, v in m.items() if v.get("NBPT")}


def lean_run(cases):
    inp = "".join(f"{c['id']};{c['year']};" + ",".join(f"{k}={v}" for k, v in c["boxes"].items()) + "\n" for c in cases)
    out = subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout
    lean = {}
    for line in out.splitlines():
        p = line.split(";")
        if p[0] != "ERR":
            lean[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    return lean


def run_m(cases, work, jobs=30):
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    tasks = []
    for year in sorted({c["year"] for c in cases}):
        ind, outd = f"{work}/in{year}", f"{work}/out{year}"
        os.makedirs(ind); os.makedirs(outd)
        files = []
        for c in cases:
            if c["year"] == year:
                p = f"{ind}/{c['id']}.irj"
                open(p, "w").write(R.irj(c))
                files.append(p)
        k = max(1, len(files) // jobs + 1)
        tasks += [(year, files[i:i + k], outd) for i in range(0, len(files), k)]
    with cf.ThreadPoolExecutor(jobs) as ex:
        logs = list(ex.map(R.run_chunk, tasks))
    open(f"{work}/cal.log", "w").write("".join(logs))
    years = sorted({c["year"] for c in cases})
    return grep_m([f"{work}/out{y}" for y in years])


def eq(a, b):
    return a is not None and b is not None and abs(a - b) < 1e-6


def classify(lv, mv):
    """Name the cause of a household-rate difference from the intermediate amounts."""
    tags = []
    if not eq(lv.get("PASIR"), mv.get("IRTOTAL", 0)):
        if 0 < lv.get("PASIR", 0) < 61 and mv.get("IRTOTAL", 0) == 0:
            tags.append("61-euro rule (M: IRTOTAL=0 under 61 EUR)")
        else:
            tags.append("tax")
    if not eq(lv.get("PASDEN"), mv.get("PASDENF", 0)):
        tags.append("denominator")
    if not eq(lv.get("PASX"), mv.get("TSRASF", 0) + mv.get("REVACOMP", 0)):
        tags.append("income of 204 A (numerator share)")
    if not eq(lv.get("PASTOT"), mv.get("REVTOT", 0)):
        tags.append("total income")
    if not tags and not eq(lv.get("PASNUM"), mv.get("PASNUMF", 0)):
        tags.append("numerator rounding")
    if not tags:
        num, den = lv["PASNUM"], lv["PASDEN"]
        frac = (1000 * num / den) % 1 if den else 0
        if 0.49994 <= frac < 0.5:
            tags.append("M rounding margin (rate fraction .49995-.49999)")
        elif mv.get("INDTAZ"):
            tags.append("II zero rate (M INDTAZ)")
        elif lv.get("PASII"):
            tags.append("II zero rate (Lean)")
        else:
            tags.append("other")
    return " + ".join(tags)


def compare(cases, m, lean, out):
    byid = {c["id"]: c for c in cases}
    st = collections.Counter()
    cls = collections.Counter()
    clsy = collections.Counter()
    icls = collections.Counter()
    diffs = []
    for cid, mv in m.items():
        lv = lean.get(cid)
        if lv is None or "TXFOYER" not in lv:
            st["outside"] += 1
            continue
        y = byid[cid]["year"]
        st["households"] += 1
        st[f"households {y}"] += 1
        ok = eq(lv["TXFOYER"], mv.get("RASTXFOYER", 0))
        st["TXFOYER equal"] += ok
        st[f"TXFOYER equal {y}"] += ok
        st["TXFOYER61 equal"] += eq(lv["TXFOYER61"], mv.get("RASTXFOYER", 0))
        for a, b in (("PASNUM", "PASNUMF"), ("PASDEN", "PASDENF"), ("PASIR", "IRTOTAL"), ("PASTOT", "REVTOT")):
            st[f"{a} equal"] += eq(lv[a], mv.get(b, 0))
        row = {"id": cid, "year": y, "boxes": byid[cid]["boxes"], "lean": lv, "m": mv, "bad": []}
        if not ok:
            c = classify(lv, mv)
            cls[c] += 1
            clsy[(y, c)] += 1
            row["bad"].append("TXFOYER")
            row["class"] = c
        if "TXDEC1" in lv:
            st["couples"] += 1
            for k in ("1", "2"):
                st["TXDEC" + k + " equal"] += eq(lv["TXDEC" + k], mv.get("RASTXDEC" + k, 0))
                st["TXDEC" + k + "S equal"] += eq(lv["TXDEC" + k + "S"], mv.get("RASTXDEC" + k, 0))
            both = all(eq(lv["TXDEC" + k], mv.get("RASTXDEC" + k, 0)) for k in "12")
            bothS = all(eq(lv["TXDEC" + k + "S"], mv.get("RASTXDEC" + k, 0)) for k in "12")
            st["couples both equal"] += both
            st["couples both equal S"] += bothS
            if not both:
                row["bad"].append("TXDEC")
                ic = ("single-person decote (equal with TXDECnS)" if bothS else
                      "household rate differs" if not ok else "other")
                icls[ic] += 1
                row["indiv_class"] = ic
            if not bothS:
                row["bad"].append("TXDECS")
                lo = "1" if mv.get("TXPASMIN") == 1 else "2"
                ics = ("household rate differs" if not ok else
                       "61-euro rule, individual (M: IRINDIV1=0 under 61 EUR)"
                       if mv.get("IRINDIV1", 0) == 0 and mv.get("TXPASMIN") in (1, 2) and lv["TXDEC" + lo + "S"] > 0 else
                       "quarter-part cap rounded with the tax (M 2020-2024: IRINDPAS2)"
                       if y <= 2024 and mv.get("NBPT", 2) % 1 else "other")
                icls["single-decote variant: " + ics] += 1
                row["indivS_class"] = ics
        if row["bad"]:
            diffs.append(row)
    with open(f"{out}/pas_diffs.jsonl", "w") as f:
        for d in diffs:
            f.write(json.dumps(d) + "\n")
    n = st["households"]
    rep = [f"M accepted {len(m)}; in Lean's PAS scope {n}; outside it {st['outside']}",
           f"household rate (TXFOYER = RASTXFOYER): {st['TXFOYER equal']}/{n}",
           f"  diagnostic, a tax under 61 EUR counted as nil (TXFOYER61): {st['TXFOYER61 equal']}/{n}"]
    for y in sorted({c['year'] for c in cases}):
        if st[f'households {y}']:
            rep.append(f"  income {y} (rate from Sept {y + 1}): {st[f'TXFOYER equal {y}']}/{st[f'households {y}']}")
    for a in ("PASNUM", "PASDEN", "PASIR", "PASTOT"):
        rep.append(f"  {a} equal: {st[a + ' equal']}/{n}")
    nc = st["couples"]
    rep += [f"couples with individualised rates (art. 204 M): {nc}",
            f"  couples' decote (words of art. 197, I, 4): TXDEC1 {st['TXDEC1 equal']}/{nc}, TXDEC2 {st['TXDEC2 equal']}/{nc}, both {st['couples both equal']}/{nc}",
            f"  single decote (M's reading):               TXDEC1 {st['TXDEC1S equal']}/{nc}, TXDEC2 {st['TXDEC2S equal']}/{nc}, both {st['couples both equal S']}/{nc}",
            "classes of household-rate differences:"]
    rep += [f"  {v:6d}  {k}" for k, v in cls.most_common()]
    rep += ["classes of individualised-rate differences:"] + [f"  {v:6d}  {k}" for k, v in icls.most_common()]
    rep += ["household classes by income year:"] + [f"  {y} {v:6d}  {k}" for (y, k), v in sorted(clsy.items())]
    open(f"{out}/pas_report.txt", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def main():
    mode, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    if mode == "fresh":
        cases = [json.loads(l) for l in open(src)]
        m = run_m(cases, out + "/mwork", int(sys.argv[4]) if len(sys.argv) > 4 else 30)
    elif mode == "recheck":   # M outputs already grepped into OUT_DIR/pas_m.jsonl; cases from SRC (jsonl or run dir)
        if src.endswith(".jsonl"):
            cases = [json.loads(l) for l in open(src)]
        else:
            cases = []
            for d in os.listdir(src):
                if d.startswith("in"):
                    for f in os.listdir(f"{src}/{d}"):
                        cases.append({"id": f[:-4], "year": int(d[2:]), "boxes": read_irj_boxes(f"{src}/{d}/{f}")})
        m = {}
        for l in open(f"{out}/pas_m.jsonl"):
            r = json.loads(l)
            m[r.pop("id")] = r
    else:
        cases = []
        years = [int(d[2:]) for d in os.listdir(src) if d.startswith("in")]
        for y in years:
            for f in os.listdir(f"{src}/in{y}"):
                cases.append({"id": f[:-4], "year": y, "boxes": read_irj_boxes(f"{src}/in{y}/{f}")})
        m = grep_m([f"{src}/out{y}" for y in years])
    lean = lean_run([c for c in cases if c["id"] in m])
    with open(f"{out}/pas_m.jsonl", "w") as f:
        for k, v in m.items():
            f.write(json.dumps({"id": k, **v}) + "\n")
    with open(f"{out}/pas_lean.jsonl", "w") as f:
        for k, v in lean.items():
            f.write(json.dumps({"id": k, **v}) + "\n")
    compare(cases, m, lean, out)


if __name__ == "__main__":
    main()
