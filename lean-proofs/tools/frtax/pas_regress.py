"""Income-tax regression for a Lean change: two Lean binaries on the random sets, the 12 figures compared with M.

usage: pas_regress.py BEFORE_BIN AFTER_BIN OUT_DIR [jobs]

Sets: runs/final (income 2024-2025) and runs/old (income 2020-2023); the returns are the inputs M accepted
(RUN/m.jsonl), their boxes read from RUN/in<year>/*.irj. For each set: returns whose 12 compared figures (run.py
PAIRS) are identical before and after; returns whose whole output line is identical; and the returns equal to M on
all 12 figures, before and after (RESULTS #7, #8). Writes OUT_DIR/regress_<set>.json with the ids that changed.
"""
import json, os, subprocess, sys, collections
import concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R
import pas_run as P

H = os.path.expanduser("~/fr")
BEFORE, AFTER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
JOBS = int(sys.argv[4]) if len(sys.argv) > 4 else 12
PAS_FIELDS = ("TXFOYER", "TXFOYER61", "PASNUM", "PASDEN", "PASIR", "PASX", "PASTOT", "PASII",
              "TXDEC1", "TXDEC2", "TXDEC1S", "TXDEC2S")


def run_bin(binary, lines):
    k = len(lines) // JOBS + 1
    chunks = ["".join(lines[i:i + k]) for i in range(0, len(lines), k)]
    with cf.ThreadPoolExecutor(JOBS) as ex:
        outs = list(ex.map(lambda s: subprocess.run([binary], input=s, capture_output=True, text=True).stdout, chunks))
    res = {}
    for out in outs:
        for line in out.splitlines():
            p = line.split(";")
            if p[0] != "ERR":
                res[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in ("final", "old"):
        rd = f"{H}/runs/{name}"
        m = {}
        for l in open(f"{rd}/m.jsonl"):
            r = json.loads(l)
            m[r.pop("id")] = r
        lines = []
        for d in sorted(os.listdir(rd)):
            if d.startswith("in") and d[2:].isdigit():
                y = int(d[2:])
                for f in os.listdir(f"{rd}/{d}"):
                    cid = f[:-4]
                    if cid in m:
                        b = P.read_irj_boxes(f"{rd}/{d}/{f}")
                        lines.append(f"{cid};{y};" + ",".join(f"{k}={v}" for k, v in b.items()) + "\n")
        before, after = run_bin(BEFORE, lines), run_bin(AFTER, lines)
        st = collections.Counter()
        changed12, changed_other, changed_pas = [], [], collections.Counter()
        for cid, mv in m.items():
            a, b = before.get(cid), after.get(cid)
            if a is None or b is None:
                st["missing"] += 1
                continue
            st["returns"] += 1
            same12 = all(a.get(lf) == b.get(lf) for lf, _ in R.PAIRS)
            st["12 figures identical"] += same12
            if not same12:
                changed12.append(cid)
            st["whole line identical"] += a == b
            if a != b:
                ks = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
                for k in ks:
                    changed_pas[k] += 1
                if any(k not in PAS_FIELDS for k in ks):
                    changed_other.append(cid)
            for tag, lv in (("before", a), ("after", b)):
                st[f"= M on all 12 ({tag})"] += all(abs(lv.get(lf, 0.0) - mv.get(mf, 0.0)) <= 0.001 for lf, mf in R.PAIRS)
        print(f"== {name} ({rd}): " + ", ".join(f"{k} {v}" for k, v in st.items()))
        print(f"   fields that changed (returns): {dict(changed_pas)}")
        json.dump({"stats": dict(st), "changed_fields": dict(changed_pas), "changed12": changed12,
                   "changed_non_pas": changed_other}, open(f"{OUT}/regress_{name}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
