"""Loophole hunt: shared helpers (Lean batch runner, Mlang runner, burden, households).

Lean: ~/fr/lean/.lake/build/bin/frtax, one return per line `id;year;BOX=V,...`.
Mlang: ~/fr/bin/cal<year>, IRJ with REGCO/1 and ANREV/<year> (as harness/run.py).
"Burden" = everything the household pays on the return: net income tax (IMPNET, refunds negative), CEHR, CDHR,
social levies assessed on the return (PSNET) and the micro-entrepreneurs' flat levy (art. 151-0) on the turnover.
"""
import os, re, json, subprocess, tempfile, shutil, concurrent.futures as cf

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")
NCPU = 12  # the share of the build server this work may use

KEYS = ("NBPT", "RNG", "RNI", "IDRSFULL", "IDRSCAP", "IDRS", "IDEC", "ITRED", "CITOT", "PFU", "IDRS4", "IAVCR",
        "IMPNET", "REVKIRE", "PSNET", "CHRAPRES", "CDHR")


def line(cid, year, boxes):
    return f"{cid};{year};" + ",".join(f"{k}={int(v)}" for k, v in boxes.items())


def _lean_chunk(text):
    return subprocess.run([LEAN], input=text, capture_output=True, text=True).stdout


def parse_lean(s, out):
    for ln in s.splitlines():
        p = ln.split(";")
        if p[0] == "ERR":
            continue
        d = {}
        for kv in p[1:]:
            k, _, v = kv.partition("=")
            if k in KEYS:
                d[k] = float(v)
        out[p[0]] = d


def lean(cases, jobs=NCPU):
    """cases: iterable of (id, year, boxes). Returns {id: {KEY: value}}."""
    lines = [line(*c) for c in cases]
    out = {}
    if not lines:
        return out
    k = max(500, len(lines) // jobs + 1)
    chunks = ["\n".join(lines[i:i + k]) + "\n" for i in range(0, len(lines), k)]
    with cf.ThreadPoolExecutor(min(jobs, len(chunks))) as ex:
        for s in ex.map(_lean_chunk, chunks):
            parse_lean(s, out)
    return out


def vl_paid(b):
    """art. 151-0, II: 1 % of sales, 1.7 % of services, 2.2 % of BNC receipts (rounded as Lean's flatLevyPaid)."""
    def pct(p, x):
        return (2 * p * x + 10000) // 20000
    g = b.get
    return (pct(100, g("5TA", 0) + g("5UA", 0) + g("5VA", 0)) + pct(170, g("5TB", 0) + g("5UB", 0) + g("5VB", 0))
            + pct(220, g("5TE", 0) + g("5UE", 0) + g("5VE", 0)))


def burden(b, o):
    return o["IMPNET"] + o["CHRAPRES"] + o["CDHR"] + o["PSNET"] + vl_paid(b)


# ---------------------------------------------------------------- Mlang
MVARS = ["NBPT", "RNG", "RNI", "IDRS", "IDRS2", "IDRS3", "IDRS4", "IDEC", "ITRED", "IAN", "IRN", "IRE", "REVKIRE",
         "CHRAPRES", "CDHR", "PSNET", "IPROP", "IINET", "NAPCR", "IAVIM", "IINETIR"]


def irj(cid, year, boxes):
    lines = ["#NOM", cid, "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{year}"]
    lines += [f"{k}/{int(v)}" for k, v in sorted(boxes.items())]
    lines += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
              "#RESULTATS-CORRECTIF", "##"]
    return "\n".join(lines) + "\n"


def _m_chunk(args):
    year, files, outdir = args
    r = subprocess.run([f"{BIN}/cal{year}", "-completion", "-m", "p", "-a", str(year), "-dst", outdir] + files,
                       capture_output=True, text=True)
    return r.stdout


def mlang(cases, jobs=NCPU, batch=2400):
    """cases: iterable of (id, year, boxes). Returns ({id: {MVAR: value}}, {id: 'KO code'}).
    ids must be file-name safe. Runs in batches (each completed output is ~460 KB) and deletes them."""
    cases = list(cases)
    res, ko = {}, {}
    for i in range(0, len(cases), batch):
        r, k = _mlang_batch(cases[i:i + batch], jobs)
        res.update(r); ko.update(k)
    return res, ko


def _mlang_batch(cases, jobs):
    work = tempfile.mkdtemp(prefix="loopm_", dir=os.path.expanduser("~/fr/runs/loop"))
    tasks = []
    for year in sorted({c[1] for c in cases}):
        ind, outd = f"{work}/in{year}", f"{work}/out{year}"
        os.makedirs(ind, exist_ok=True); os.makedirs(outd, exist_ok=True)
        files = []
        for cid, y, b in cases:
            if y == year:
                p = f"{ind}/{cid}.irj"
                open(p, "w").write(irj(cid, y, b))
                files.append(p)
        k = max(1, len(files) // jobs + 1)
        tasks += [(year, files[i:i + k], outd) for i in range(0, len(files), k)]
    with cf.ThreadPoolExecutor(jobs) as ex:
        logs = "".join(ex.map(_m_chunk, tasks))
    # refused returns: "ATRT000 | KO | <code> ..." then 'IACT007 | "<id>.irj" KO'
    ko, last = {}, None
    for ln in logs.splitlines():
        m = re.search(r"KO \| (\S+)", ln)
        if m:
            last = m.group(1)
        m = re.search(r'"([^"/]+)\.irj" KO', ln)
        if m:
            ko[m.group(1)] = last or "?"
            last = None
    res = {}
    pat = "^(" + "|".join(MVARS) + ")/"
    for year in sorted({c[1] for c in cases}):
        outd = f"{work}/out{year}"
        r = subprocess.run(f"find {outd} -name '*.irj' -print0 | xargs -0 -r -n 2000 grep -H -E '{pat}'",
                           shell=True, capture_output=True, text=True)
        for l in r.stdout.splitlines():
            path, _, kv = l.partition(":")
            k, _, v = kv.partition("/")
            cid = os.path.basename(path)[:-4]
            d = res.setdefault(cid, {})
            if k not in d:
                try:
                    d[k] = float(v)
                except ValueError:
                    pass
    for cid in [c for c, v in res.items() if not v.get("NBPT")]:
        del res[cid]
        ko.setdefault(cid, "no parts")
    for cid, y, b in cases:
        if cid not in res and cid not in ko:
            ko[cid] = "no output"
    shutil.rmtree(work, ignore_errors=True)
    return res, ko


def m_burden(b, m):
    return m.get("IRN", 0) + m.get("CHRAPRES", 0) + m.get("CDHR", 0) + m.get("PSNET", 0) + vl_paid(b)


# ---------------------------------------------------------------- households
def kids(b, year, nf=0, nh=0, nj=0, ages=(8, 12, 5, 15, 3, 10)):
    """Children with the birth years M needs: nf wholly in charge (0CF, 0F0..), nh in shared residence (0CH, 0H0..),
    nj attached adults 18-25 (0DJ, 0J0..)."""
    if nf:
        b["0CF"] = nf
        for i in range(nf):
            b[f"0F{i}"] = year - ages[i % len(ages)]
    if nh:
        b["0CH"] = nh
        for i in range(nh):
            b[f"0H{i}"] = year - ages[i % len(ages)]
    if nj:
        b["0DJ"] = nj
        for i in range(nj):
            b[f"0J{i}"] = year - 20
    return b


def single(year, born=1980, **kw):
    b = {"0AC": 1, "0DA": born}
    b.update(kw)
    return b


def couple(year, born1=1980, born2=1980, kind="0AM", **kw):
    b = {kind: 1, "0DA": born1, "0DB": born2}
    b.update(kw)
    return b


def jdump(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
