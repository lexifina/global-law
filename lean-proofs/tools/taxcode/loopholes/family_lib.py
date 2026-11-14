"""Shared pieces of the family search: the families, the plan encoding, and the parallel Lean runner.

Every tax figure comes from `LegalProofs/USTax/Family/Run.lean` (the 2025 law, held fixed in real terms; see
Driver.lean). This file only builds plans and reads outcomes.
"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # lean-proofs/
DATA = Path(r"~\Documents\tax-formalization-data\hunt\family")
LAKE = str(Path.home() / ".elan" / "bin" / "lake.exe")

def parent(age, **kw):
    d = dict(age=age, wage=0, ira=0, roth=0, ss=0, ssAge=67, rmdAge=75, retireAge=65); d.update(kw); return d

def kid(age, **kw):
    d = dict(age=age, studentThrough=22, adultWage=50000, support=25000); d.update(kw); return d

def spec(**kw):
    d = dict(business=0, charity=0, mortgage=0, salt=0, premium=0, gainsInDni=False, kidWageCap=[]); d.update(kw)
    return d

# Four families. Real 2025 dollars; returns real (price growth + qualified dividends + interest).
FAMILIES = {
    # A: two parents of 45 with a sole proprietorship (Schedule C $250,000) and children of 8 and 12.
    "owners": spec(head=parent(45, ira=500000, ss=40000), spouse=parent(45, wage=60000, ira=200000, roth=50000, ss=25000),
                   brokerage=dict(value=800000, basis=400000), business=250000, spending=150000, charity=10000,
                   mortgage=15000, salt=15000, kids=[kid(8), kid(12)], growthBp=350, divBp=150, intBp=50, horizon=43,
                   kidWageCap=[[7, 6000], [12, 12000], [16, 16000], [18, 20000]]),
    # B: early retirees at 58 on the marketplace until 65, Social Security at 70, adult children.
    "retirees": spec(head=parent(58, ira=1600000, ss=45000, ssAge=70), spouse=parent(58, ira=900000, ss=30000, ssAge=70),
                     brokerage=dict(value=1600000, basis=900000), spending=110000, charity=5000, premium=24000,
                     kids=[kid(28, adultWage=60000), kid(31, adultWage=45000)], growthBp=350, divBp=150, intBp=50,
                     horizon=34),
    # C: two employees of 40 earning $450,000, children of 3 and 6.
    "earners": spec(head=parent(40, wage=300000, ira=600000, ss=45000, retireAge=60),
                    spouse=parent(40, wage=150000, ira=300000, ss=35000, retireAge=60),
                    brokerage=dict(value=1500000, basis=1000000), spending=230000, charity=20000, mortgage=30000,
                    salt=40000, kids=[kid(3), kid(6)], growthBp=350, divBp=150, intBp=50, horizon=47),
    # D: investors of 50 living on an $8 million portfolio, children of 10 and 14.
    "investors": spec(head=parent(50, ira=700000, ss=40000), spouse=parent(50, ira=300000, ss=30000),
                      brokerage=dict(value=8000000, basis=2000000), spending=300000, charity=30000, salt=30000,
                      kids=[kid(10), kid(14)], growthBp=350, divBp=150, intBp=50, horizon=40),
}

YEAR_DEFAULT = dict(convH=0, convS=0, convTo=0, harvestTo=0, gifts=[], trustFund=0, trustDistBp=[], trustHarvestTo=0,
                    kidWage=[], kidRoth=[], kidHarvestTo=[], form8814=[], charity=-1, charityShares=False, mfs=False)

def blank_plan(spec):
    return [dict(YEAR_DEFAULT) for _ in range(spec["horizon"])]

def run(specs, jobs, procs=10, tag="run"):
    """Evaluate jobs [(spec_name, plan, log)] in `procs` parallel Lean processes; returns outcomes in order."""
    work = DATA / "work"; work.mkdir(parents=True, exist_ok=True)
    n = len(jobs); procs = max(1, min(procs, n))
    chunks = [jobs[i::procs] for i in range(procs)]
    ps = []
    for i, ch in enumerate(chunks):
        jin = work / f"{tag}_{i}_in.json"; jout = work / f"{tag}_{i}_out.json"
        json.dump({"specs": specs, "jobs": [{"spec": s, "plan": p, "log": lg} for s, p, lg in ch]}, open(jin, "w"))
        ps.append((subprocess.Popen([LAKE, "env", "lean", "--run", "LegalProofs/USTax/Family/Run.lean", str(jin), str(jout)],
                                    cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)), jout))
    outs = []
    for p, jout in ps:
        o, e = p.communicate()
        if p.returncode != 0:
            raise RuntimeError(e.decode(errors="replace")[:2000])
        outs.append(json.load(open(jout)))
    res = [None] * n
    for i, ch in enumerate(outs):
        for j, o in enumerate(ch):
            res[i + j * procs] = o
    return res
