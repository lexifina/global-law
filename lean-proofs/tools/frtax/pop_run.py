"""Run a candidate pool through the Lean model and through the DGFiP M code (Mlang C backend), in chunks on /dev/shm
so the ~460 KB completed IRJ of each return never piles up on disk.
usage: pop_run.py cases.jsonl workdir [jobs=12] [chunk=400]
Writes workdir/lean.jsonl, workdir/m.jsonl, workdir/m_rejected.jsonl (id + anomaly codes)."""
import json, os, re, subprocess, sys, shutil, tempfile, concurrent.futures as cf

BIN = os.path.expanduser("~/fr/bin")
LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
MVARS = ["NBPT", "RNG", "RNI", "IDRS", "IDRS2", "IDRS3", "IDRS4", "IDEC", "ITRED", "CITOT", "IAN", "IINET",
         "IRN", "IRNET", "IMPNET", "REVKIRE", "IAD11", "PLAFQF", "IPROP", "TOTIRPS", "NAPCR", "CHRAPRES", "CDHR",
         "PSNET", "IREST", "IRE", "IAVIM", "TXMOYIMP", "IINETIR", "NAPTIR"]
PAT = re.compile(r"^(" + "|".join(MVARS) + r")/(.*)$")


def irj(c):
    lines = ["#NOM", c["id"], "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{c['year']}"]
    lines += [f"{k}/{v}" for k, v in sorted(c["boxes"].items())]
    # M only: last year's deducted CSG set to this year's 6DE, so the N-1 discordance DD22 does not fire
    if "6DE" in c["boxes"]:
        lines.append(f"V_BTCSGDED/{c['boxes']['6DE']}")
    lines += [f"{k}/{v}" for k, v in sorted(c.get("m_extra", {}).items())]
    lines += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
              "#RESULTATS-CORRECTIF", "##"]
    return "\n".join(lines) + "\n"


def m_chunk(args):
    year, chunk = args
    tmp = tempfile.mkdtemp(prefix="pop_", dir="/dev/shm")
    try:
        ind, outd = f"{tmp}/in", f"{tmp}/out"
        os.makedirs(ind); os.makedirs(outd)
        files = []
        for c in chunk:
            p = f"{ind}/{c['id']}.irj"
            with open(p, "w") as f:
                f.write(irj(c))
            files.append(p)
        r = subprocess.run([f"{BIN}/cal{year}", "-completion", "-m", "p", "-a", str(year), "-dst", outd] + files,
                           capture_output=True, text=True)
        res, rej = {}, {}
        g = subprocess.run(f"find {outd} -name '*.irj' -print0 | xargs -0 -r grep -H -E '^({'|'.join(MVARS)})/'",
                           shell=True, capture_output=True, text=True)
        for line in g.stdout.splitlines():
            path, kv = line.split(":", 1)
            cid = os.path.basename(path)[:-4]
            k, v = kv.split("/", 1)
            res.setdefault(cid, {}).setdefault(k, float(v))
        # anomalies: "traitement du fichier "x.irj"" then "KO | CODE text" lines
        cur = None
        for line in r.stdout.splitlines():
            m = re.search(r'traitement du fichier "([\w]+)\.irj"', line)
            if m:
                cur = m.group(1)
                continue
            m = re.search(r"\| KO \| (\S+)", line)
            if m and cur:
                rej.setdefault(cur, []).append(m.group(1))
        return res, rej, r.stdout[-2000:] if not res else ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    cases_path, work = sys.argv[1], sys.argv[2]
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    size = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    cases = [json.loads(l) for l in open(cases_path)]
    os.makedirs(work, exist_ok=True)
    # Lean (4 processes)
    def lean_part(part):
        inp = "".join(f"{c['id']};{c['year']};" + ",".join(f"{k}={v}" for k, v in c["boxes"].items()) + "\n" for c in part)
        return subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout
    q = (len(cases) + 3) // 4
    with cf.ThreadPoolExecutor(4) as ex:
        outs = list(ex.map(lean_part, [cases[i:i + q] for i in range(0, len(cases), q)]))
    with open(f"{work}/lean.jsonl", "w") as f:
        for out in outs:
            for line in out.splitlines():
                p = line.split(";")
                if p[0] == "ERR" or len(p) < 3:
                    continue
                f.write(json.dumps({"id": p[0], **{kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:]}}) + "\n")
    print("lean done", flush=True)
    tasks = []
    for year in sorted({c["year"] for c in cases}):
        cy = [c for c in cases if c["year"] == year]
        tasks += [(year, cy[i:i + size]) for i in range(0, len(cy), size)]
    done = 0
    allres, allrej = {}, {}
    with cf.ThreadPoolExecutor(jobs) as ex:
        for res, rej, tail in ex.map(m_chunk, tasks):
            allres.update(res)
            allrej.update(rej)
            if tail:
                print("chunk with no output:", tail[-300:], flush=True)
            done += 1
            if done % 25 == 0:
                print(f"M chunks {done}/{len(tasks)}", flush=True)
    # second pass: IM15 (net tax >= 1 M EUR "valider avec une habilitation") is skipped by M for V_NOTRAIT 23
    # (a later processing run); pop_check_notrait.py shows V_NOTRAIT 23 changes no result on accepted returns.
    byid = {c["id"]: c for c in cases}
    redo = [dict(byid[cid], m_extra={"V_NOTRAIT": 23}) for cid, codes in allrej.items() if set(codes) == {"IM15"}]
    if redo:
        t2 = []
        for year in sorted({c["year"] for c in redo}):
            cy = [c for c in redo if c["year"] == year]
            t2 += [(year, cy[i:i + size]) for i in range(0, len(cy), size)]
        with cf.ThreadPoolExecutor(jobs) as ex:
            for res, rej, tail in ex.map(m_chunk, t2):
                for cid, v in res.items():
                    allres[cid] = dict(v, _notrait23=1)
                    allrej.pop(cid, None)
                for cid, codes in rej.items():
                    allrej[cid] = sorted(set(codes)) + ["(after V_NOTRAIT 23)"]
        print(f"IM15 second pass: {len(redo)} returns", flush=True)
    with open(f"{work}/m.jsonl", "w") as fm:
        for cid, v in allres.items():
            fm.write(json.dumps({"id": cid, **v}) + "\n")
    with open(f"{work}/m_rejected.jsonl", "w") as fr:
        for cid, codes in allrej.items():
            if cid not in allres:
                fr.write(json.dumps({"id": cid, "codes": sorted(set(codes))}) + "\n")
    print("M done", flush=True)


if __name__ == "__main__":
    main()
