"""Shared pieces of the owner-family entity search: the scenarios, the plan encoding, and the parallel Lean runner.

Every tax figure comes from `LegalProofs/USTax/Entity/Run.lean` (2025 law held fixed in real terms; see
Entity/Driver.lean for the assumptions). This file only builds plans and reads outcomes.
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # lean-proofs/
DATA = Path(r"~\Documents\tax-formalization-data\hunt\entity")
LAKE = str(Path.home() / ".elan" / "bin" / "lake.exe")


def biz(**kw):
    d = dict(profit=0, growthBp=300, fastYears=0, fastBp=0, multipleX10=40, staffWages=0, ubia=0, assetBasis=0,
             sstb=False, rcLo=0, rcHi=0, reasonableNeeds=0, capitalMaterial=True, needBp=0, needYears=0)
    d.update(kw); return d


def spec(**kw):
    d = dict(wageS=0, growthBp=350, divBp=150, intBp=50)
    d.update(kw); return d


def kid(age, wage):
    return dict(age=age, wage=wage)


# Four owner families. Real 2025 dollars. Profit is before the owner's pay and after staff wages.
SCENARIOS = {
    # A: a main-street business: $500,000 of profit, 4× multiple ($2M), growing 3% real; 15 years.
    "mainstreet": spec(ageH=50, ageS=50, spending=200000, brokerage=dict(value=1000000, basis=600000),
                       biz=biz(profit=500000, growthBp=300, multipleX10=40, staffWages=800000, assetBasis=200000,
                               rcLo=150000, rcHi=300000, reasonableNeeds=100000),
                       kids=[kid(24, 45000), kid(27, 60000)], horizon=15),
    # B: a growth company: $300,000 of profit growing 30% for 10 years then 3%, 10× multiple (≈$3M → ≈$48M); 15 years.
    "startup": spec(ageH=48, ageS=48, spending=180000, brokerage=dict(value=500000, basis=300000),
                    biz=biz(profit=300000, growthBp=300, fastYears=10, fastBp=3000, multipleX10=100,
                            staffWages=2000000, assetBasis=100000, rcLo=200000, rcHi=400000,
                            reasonableNeeds=200000),
                    kids=[kid(24, 50000), kid(26, 55000)], horizon=15),
    # B': the same growth company when it must reinvest every dollar of profit for its 10 growth years (a venture-style
    # business): the only scenario where profit cannot all be paid out.
    "venture": spec(ageH=48, ageS=48, spending=180000, brokerage=dict(value=2000000, basis=1200000),
                    biz=biz(profit=300000, growthBp=300, fastYears=10, fastBp=3000, multipleX10=100,
                            staffWages=2000000, assetBasis=100000, rcLo=200000, rcHi=400000,
                            reasonableNeeds=200000, needBp=10000, needYears=10),
                    kids=[kid(24, 50000), kid(26, 55000)], horizon=15),
    # C: a professional practice (a §199A / §1202(e)(3) field): $1.5M of profit, 2× multiple; 12 years.
    "practice": spec(ageH=55, ageS=55, spending=350000, brokerage=dict(value=3000000, basis=1500000),
                     biz=biz(profit=1500000, growthBp=200, multipleX10=20, staffWages=1500000, assetBasis=100000,
                             sstb=True, rcLo=300000, rcHi=600000, reasonableNeeds=150000, capitalMaterial=False),
                     kids=[kid(26, 50000), kid(29, 70000)], horizon=12),
    # D: a large private company: $4M of profit, 7× ($28M), growing 4%; 12 years.
    "large": spec(ageH=55, ageS=55, spending=500000, brokerage=dict(value=5000000, basis=2000000),
                  biz=biz(profit=4000000, growthBp=400, multipleX10=70, staffWages=6000000, assetBasis=3000000,
                          rcLo=400000, rcHi=800000, reasonableNeeds=500000),
                  kids=[kid(28, 60000), kid(30, 80000)], horizon=12),
}


def plan(forms=None, salary=0, payoutBp=10000, gifts=None, exit="sale"):
    return dict(forms=[list(f) for f in (forms or [])], salary=salary, payoutBp=payoutBp,
                gifts=[dict(year=g[0], bp=g[1], toTrusts=g[2]) for g in (gifts or [])], exit=exit)


def run(specs, jobs, procs=10, tag="run"):
    """Evaluate jobs [(spec_name, plan, log)] in `procs` parallel Lean processes; returns outcomes in order."""
    work = DATA / "work"; work.mkdir(parents=True, exist_ok=True)
    n = len(jobs); procs = max(1, min(procs, n))
    chunks = [jobs[i::procs] for i in range(procs)]
    ps = []
    for i, ch in enumerate(chunks):
        jin = work / f"{tag}_{i}_in.json"; jout = work / f"{tag}_{i}_out.json"
        json.dump({"specs": specs, "jobs": [{"spec": s, "plan": p, "log": lg} for s, p, lg in ch]}, open(jin, "w"))
        ps.append((subprocess.Popen([LAKE, "env", "lean", "--run", "LegalProofs/USTax/Entity/Run.lean", str(jin), str(jout)],
                                    cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)), jin, jout))
    outs = []
    for p, jin, jout in ps:
        o, e = p.communicate()
        if p.returncode != 0:
            raise RuntimeError(e.decode(errors="replace")[:2000] + o.decode(errors="replace")[:2000])
        outs.append(json.load(open(jout)))
        jin.unlink(); jout.unlink()
    res = [None] * n
    for i, ch in enumerate(outs):
        for j, o in enumerate(ch):
            res[i + j * procs] = o
    return res
