"""Run the US TY2025 model (read-only copy in ../lean/TaxCode) on households, via the compiled `usloop` exe.

    from model import H, run, net, fica
    r = run([H(filing="single", wages=50000)])[0]   # dict of Form 1040 lines

`H(**kw)` builds a household with every field present; pass `facts={...}` for group B's facts (§199A W-2 wages,
UBIA, SSTB, the §63(e) election, §63(c)(6)(A) spouse itemizes). Batches are split across processes.
"""
import json, os, subprocess, tempfile, copy
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "..", "lean", ".lake", "build", "bin", "usloop")

HOUSEHOLD = dict(
    filing="single", head={"age": 40, "blind": False}, spouse=None, dependents=[], canBeClaimedAsDependent=False,
    wages=0, wagesSpouse=0, seIncome=0, taxableInterest=0, taxExemptInterest=0, ordinaryDividends=0,
    qualifiedDividends=0, shortTermGains=0, longTermGains=0, iraDistributions=0, pensions=0, socialSecurity=0,
    unemployment=0, otherIncome=0, qbi=0, iraContributions=0, activeParticipant=False, hsaContributions=0,
    studentLoanInterest=0, educatorExpenses=0, qualifiedTips=0, qualifiedOvertime=0, carLoanInterest=0,
    stateLocalTaxes=0, mortgageInterest=0, charitableCash=0, medicalExpenses=0, childCareExpenses=0,
    qualifiedTuition=[], retirementContributions=0, marketplacePremium=0, benchmarkPremium=0)
FACTS = dict(spouseItemizes=False, spouseNoIncomeNotDependent=False, headSsn=True, spouseSsn=True, earnerSsn=True,
             vinReported=True, excludedIncome=0, qbiW2Wages=0, qbiUbia=0, qbiSstb=False, electItemize=None)
DEPENDENT = dict(age=10, ssn=True, student=False, disabled=False, monthsWithTaxpayer=12)


def kid(age=10, **kw):
    d = dict(DEPENDENT); d.update(age=age, **kw); return d


def H(facts=None, **kw):
    h = copy.deepcopy(HOUSEHOLD)
    for k, v in kw.items():
        if k not in h:
            raise KeyError(k)
        h[k] = v
    if h["filing"] in ("mfj",) and h["spouse"] is None:
        h["spouse"] = {"age": h["head"]["age"], "blind": False}
    f = dict(FACTS); f.update(facts or {})
    return {"h": h, "f": f}


def _run_chunk(cases):
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, "in.json"), os.path.join(d, "out.json")
        with open(i, "w") as fh:
            json.dump(cases, fh)
        subprocess.run([EXE, i, o], check=True)
        with open(o) as fh:
            return json.load(fh)


def run(cases, procs=None, chunk=4000):
    cases = list(cases)
    if not cases:
        return []
    procs = procs or min(28, os.cpu_count() or 4)
    n = max(1, min(chunk, -(-len(cases) // procs)))
    parts = [cases[k:k + n] for k in range(0, len(cases), n)]
    with ThreadPoolExecutor(procs) as ex:
        outs = list(ex.map(_run_chunk, parts))
    return [r for p in outs for r in p]


def net(case):
    return run([case])[0]["netTax"]


def fica(w):
    """Employee (= employer) share of FICA on wages w: §3101(a) 6.2% to the $176,100 base, §3101(b)(1) 1.45%.
    The additional 0.9% (§3101(b)(2)) is in the model's return (Form 8959)."""
    return round(0.062 * min(max(w, 0), 176100) + 0.0145 * max(w, 0))
