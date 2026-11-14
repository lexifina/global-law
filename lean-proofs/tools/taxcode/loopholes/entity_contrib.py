"""Blind search of the contribution game (Entity/Contrib.lean): a parent's built-in-gain equipment in a family
partnership with an adult child.

    python tools/taxcode/loopholes/entity_contrib.py [procs]

Games: a grid over the parent's wage, the child's wage, the built-in gain, the years left on the schedule and the
child's cash. Moves: every §704(c) method × every sale year. Each is scored by the family's total
tax against the baseline (no partnership). Natural values only: bracket edges for wages, round amounts, schedule
lives. Writes DATA/contrib.json.
"""
import itertools, json, subprocess, sys, time
from entity_lib import ROOT, DATA, LAKE

def games():
    out = []
    for wP, wK, (book, basis), rem, cashMul in itertools.product(
            [250000, 500000, 1000000], [0, 50000], [(1000000, 100000), (1000000, 500000), (4000000, 400000)],
            [1, 3, 7], [1, 3]):
        out.append(dict(wageP=wP, wageK=wK, book=book, basis=basis, remaining=rem, newLife=7,
                        childCash=book * cashMul, cashBp=500, horizon=10))
    return out

def moves():
    out = []
    for m in ("traditional", "curative", "remedial"):
        for s in (1, 2, 3, 4, 5, 7, 8, 9):
            out.append(dict(method=m, saleYear=s))
    return out

def main():
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    G, M = games(), moves()
    work = DATA / "work"; work.mkdir(parents=True, exist_ok=True)
    chunks = [G[i::procs] for i in range(procs)]
    ps = []
    t0 = time.time()
    for i, ch in enumerate(chunks):
        jin, jout = work / f"contrib_{i}_in.json", work / f"contrib_{i}_out.json"
        json.dump({"games": ch, "moves": M}, open(jin, "w"))
        ps.append((subprocess.Popen([LAKE, "env", "lean", "--run", "LegalProofs/USTax/Entity/ContribRun.lean", str(jin), str(jout)],
                                    cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)), jin, jout, ch))
    rows = []
    for p, jin, jout, ch in ps:
        o, e = p.communicate()
        if p.returncode: raise RuntimeError(e.decode()[:2000])
        for g, r in zip(ch, json.load(open(jout))):
            for mv, x in zip(M, r):
                rows.append(dict(game=g, move=mv, family=x[0], parent=x[1], child=x[2], baseline=x[3],
                                 saving=x[3] - x[0]))
        jin.unlink(); jout.unlink()
    json.dump(rows, open(DATA / "contrib.json", "w"))
    print(f"{len(rows)} plays, {time.time() - t0:.0f}s")
    rows.sort(key=lambda r: -r["saving"])
    for r in rows[:15]:
        g = r["game"]
        print(r["saving"], r["move"], {k: g[k] for k in ("wageP", "wageK", "book", "basis", "remaining", "childCash")})

if __name__ == "__main__":
    main()
