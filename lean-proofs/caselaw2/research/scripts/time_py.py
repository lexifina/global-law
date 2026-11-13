"""Time a Python full-text regex pass over 50,000 sample files. python time_py.py <sample-dir> <procs>"""
import os, re, sys, time
from multiprocessing import Pool
S, NP = sys.argv[1], int(sys.argv[2])
P = re.compile(r"overruled in part|to the extent that|abrogated|superseded by statute|disapproved|receded from|"
               r"limited to its facts|questioned|decline to follow|abrogated on other grounds", re.I)


def f(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    return len(P.findall(t)), len(t)


if __name__ == "__main__":
    man = [l.split("\t") for l in open(os.path.join(S, "manifest.tsv"), encoding="utf-8")]
    paths = [os.path.join(S, m[0], m[1] + ".md") for m in man if m[7].strip() == "1"][:50000]
    t0 = time.time()
    if NP == 1:
        res = list(map(f, paths))
    else:
        with Pool(NP) as p:
            res = p.map(f, paths, chunksize=500)
    dt = time.time() - t0
    print("files %d bytes %d hits %d procs %d seconds %.1f files/s %.0f" % (len(paths), sum(r[1] for r in res),
          sum(r[0] for r in res), NP, dt, len(paths) / dt))
