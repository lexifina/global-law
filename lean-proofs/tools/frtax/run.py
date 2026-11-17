"""Run returns through Mlang's C backend (the DGFiP M code) and the Lean model, and compare.

usage: run.py cases.jsonl workdir [jobs]
Writes workdir/m.jsonl (M outputs), workdir/lean.jsonl, workdir/report.txt, workdir/diffs.jsonl.
"""
import json, os, subprocess, sys, collections, concurrent.futures as cf, shutil, re

BIN = os.path.expanduser("~/fr/bin")
LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
MVARS = ["NBPT", "RNG", "RNI", "IDRS", "IDRS2", "IDRS3", "IDRS4", "IDEC", "ITRED", "CITOT", "IAN", "IINET",
         "IRN", "IRNET", "IMPNET", "REVKIRE", "IAD11", "PLAFQF", "IPROP", "TOTIRPS", "NAPCR", "CHRAPRES", "CDHR",
         "PSNET", "IREST", "IRE"]
# Lean field -> M variable compared
PAIRS = [("NBPT", "NBPT"), ("RNG", "RNG"), ("RNI", "RNI"), ("IDRS", "IDRS"), ("IDEC", "IDEC"),
         ("ITRED", "ITRED"), ("CITOT", "IRE"), ("IMPNET", "IRN"), ("REVKIRE", "REVKIRE"), ("PSNET", "PSNET"), ("CHRAPRES", "CHRAPRES"), ("CDHR", "CDHR")]

def irj(c):
    lines = ["#NOM", c["id"], "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{c['year']}"]
    lines += [f"{k}/{v}" for k, v in sorted(c["boxes"].items())]
    lines += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
              "#RESULTATS-CORRECTIF", "##"]
    return "\n".join(lines) + "\n"

def run_chunk(args):
    year, files, outdir = args
    r = subprocess.run([f"{BIN}/cal{year}", "-completion", "-m", "p", "-a", str(year), "-dst", outdir] + files,
                       capture_output=True, text=True)
    return r.stdout

def parse_out(path):
    vals = {}
    sec = None
    with open(path, errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#"):
                sec = line
                continue
            if sec == "#RESULTATS-PRIMITIF" and "/" in line:
                k, v = line.split("/", 1)
                if k in MVARS:
                    vals[k] = float(v)
    return vals

def main():
    cases_path, work = sys.argv[1], sys.argv[2]
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    cases = [json.loads(l) for l in open(cases_path)]
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
                open(p, "w").write(irj(c))
                files.append(p)
        k = max(1, len(files) // jobs + 1)
        tasks += [(year, files[i:i + k], outd) for i in range(0, len(files), k)]
    logs = []
    with cf.ThreadPoolExecutor(jobs) as ex:
        for out in ex.map(run_chunk, tasks):
            logs.append(out)
    open(f"{work}/cal.log", "w").write("".join(logs))
    rejected = collections.Counter(re.findall(r"KO \| (\S+)", "".join(logs)))
    # parse with grep (the completed files are ~30 000 lines each): one line per wanted variable, file:VAR/value
    m = {}
    pat = "^(" + "|".join(MVARS) + ")/"
    for year in sorted({c["year"] for c in cases}):
        outd = f"{work}/out{year}"
        r = subprocess.run(f"find {outd} -name '*.irj' -print0 | xargs -0 -n 2000 grep -H -E '{pat}'",
                           shell=True, capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if ":" not in line or "/" not in line.split(":", 1)[1]:
                continue
            path, kv = line.split(":", 1)
            cid = os.path.basename(path)[:-4]
            k, v = kv.split("/", 1)
            m.setdefault(cid, {}).setdefault(k, float(v))
    # a completed file with no parts is a return M refused without a KO line (2020: unknown boxes such as 7UJ)
    for cid in [k for k, v in m.items() if not v.get("NBPT")]:
        del m[cid]
        rejected["no parts"] += 1
    with open(f"{work}/m.jsonl", "w") as f:
        for k, v in m.items():
            f.write(json.dumps({"id": k, **v}) + "\n")
    # Lean
    inp = "".join(f"{c['id']};{c['year']};" + ",".join(f"{k}={v}" for k, v in c["boxes"].items()) + "\n"
                  for c in cases if c["id"] in m)
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    lean = {}
    for line in r.stdout.splitlines():
        parts = line.split(";")
        if parts[0] == "ERR":
            continue
        lean[parts[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in parts[1:]}
    with open(f"{work}/lean.jsonl", "w") as f:
        for k, v in lean.items():
            f.write(json.dumps({"id": k, **v}) + "\n")
    byid = {c["id"]: c for c in cases}
    stats = collections.Counter()
    allok = 0
    diffs = []
    for cid, mv in m.items():
        lv = lean.get(cid)
        if lv is None:
            stats["lean-missing"] += 1
            continue
        bad = []
        for lf, mf in PAIRS:
            a, b = lv.get(lf, 0.0), mv.get(mf, 0.0)
            if abs(a - b) > 0.001:
                bad.append(lf)
                stats[lf] += 1
        if not bad:
            allok += 1
        else:
            diffs.append({"id": cid, "year": byid[cid]["year"], "bad": bad, "boxes": byid[cid]["boxes"],
                          "lean": lv, "m": mv})
    with open(f"{work}/diffs.jsonl", "w") as f:
        for d in diffs:
            f.write(json.dumps(d) + "\n")
    n = len(m)
    rep = [f"cases {len(cases)}; accepted by M {n}; rejected {len(cases) - n} {dict(rejected.most_common(8))}",
           f"all fields equal: {allok}/{n} ({100 * allok / max(n, 1):.2f}%)"]
    for lf, mf in PAIRS:
        rep.append(f"  {lf:8s} vs M {mf:8s}: {n - stats[lf]}/{n} equal")
    open(f"{work}/report.txt", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))

if __name__ == "__main__":
    main()
