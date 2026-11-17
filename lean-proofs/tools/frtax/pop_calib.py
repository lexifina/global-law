"""Calibrate weights on the candidate pool so that weighted margins match the DGFiP's published figures.
Method: calibration with the bounded logit distance of Deville and Särndal (1992) from design weights that are
post-stratified on the IRCOM RFR groups; every weight stays within [0.05, 20] times its design weight (POP_LO,
POP_UP). Soft constraints: every constraint column is divided by its target (so each target is 1) and c_j is the
softness (residual = -c_j lam_j); the dual is solved by L-BFGS.
Calibrated margins (inputs, not outcomes):
  * IRCOM: households and RFR amount per RFR bracket (13 groups), households with salaries / with pensions per group;
  * 2042-nat: households filling each modelled box, and the amount, for boxes the pool generates (n >= 20 000);
  * family situation (0AC 0AD 0AV 0AM 0AO).
Never calibrated (they are the outcomes compared in pop_report.py): tax, taxed households, décote, reductions,
credits, CEHR, marginal-rate counts.
usage: pop_calib.py year pooldir out_weights.json out_fit.tsv"""
import json, os, sys, math
import numpy as np
import scipy.sparse as sp
from scipy.optimize import minimize

year, pool, out_w, out_fit = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
T = json.load(open(os.path.expanduser(f"~/fr/data/pop/targets_{year}.json")))
lean = {json.loads(l)["id"]: json.loads(l) for l in open(f"{pool}/lean.jsonl")}
cases = [json.loads(l) for l in open(f"{pool}/cases.jsonl")]
cases = [c for c in cases if c["id"] in lean]
n = len(cases)
SAL = ["1AJ", "1BJ", "1CJ", "1DJ", "1AA", "1BA", "1GB", "1HB", "1AP", "1BP", "1CP"]
PEN = ["1AS", "1BS", "1CS", "1AZ", "1BZ", "1AO", "1BO", "1CO", "1DO", "1AW", "1BW", "1CW", "1DW"]
GROUPS = [(0, 10000), (10000, 12000), (12000, 15000), (15000, 20000), (20000, 30000), (30000, 50000),
          (50000, 100000), (100000, 200000), (200000, 300000), (300000, 500000), (500000, 1000000),
          (1000000, 3000000), (3000000, None)]

cols, targets, names, soft = [], [], [], []

def add(name, vec, target, c):
    if target is None or target <= 0:
        return
    cols.append(np.asarray(vec, dtype=float) / target)
    targets.append(target); names.append(name); soft.append(c)

rfr = np.array([lean[c["id"]]["REVKIRE"] for c in cases])
parts = np.array([lean[c["id"]]["NBPT"] for c in cases])
hassal = np.array([any(c["boxes"].get(k, 0) > 0 for k in SAL) for c in cases])
haspen = np.array([any(c["boxes"].get(k, 0) > 0 for k in PEN) for c in cases])
salamt = np.array([sum(c["boxes"].get(k, 0) for k in SAL) for c in cases], dtype=float)
penamt = np.array([sum(c["boxes"].get(k, 0) for k in PEN) for c in cases], dtype=float)
irc = T["ircom"]
# IRCOM's salary and pension amounts use the DGFiP's own aggregation; scale them to the boxes' national totals
sal_ratio = sum(T["boxes"][k]["amount"] for k in SAL if k in T["boxes"]) / (1000 * irc["total"]["sal_k"])
pen_ratio = sum(T["boxes"][k]["amount"] for k in PEN if k in T["boxes"]) / (1000 * irc["total"]["pen_k"])
print(f"box/IRCOM ratios: salaries {sal_ratio:.3f}, pensions {pen_ratio:.3f}")
add("households", np.ones(n), irc["total"]["n"], 1e-5)
for lo, hi in GROUPS:
    brs = [b for b in irc["brackets"] if b["lo"] >= lo and (hi is None or (b["hi"] is not None and b["hi"] <= hi))]
    ing = (rfr > lo if lo else rfr >= -1e18) & ((rfr <= hi) if hi else True)
    lab = f"RFR {lo}-{hi or 'inf'}"
    add(f"{lab}: households", ing, sum(b["n"] for b in brs), 1e-4)
    add(f"{lab}: RFR amount", ing * np.maximum(rfr, 0), 1000 * sum(b["rfr_k"] for b in brs), 1e-3)
    if all(b["n_sal"] for b in brs):
        add(f"{lab}: households with salaries", ing & hassal, sum(b["n_sal"] for b in brs), 3e-3)
        add(f"{lab}: salary amount", ing * salamt, sal_ratio * 1000 * sum(b["sal_k"] for b in brs), 1e-2)
    if all(b["n_pen"] for b in brs):
        add(f"{lab}: households with pensions", ing & haspen, sum(b["n_pen"] for b in brs), 3e-3)
        add(f"{lab}: pension amount", ing * penamt, pen_ratio * 1000 * sum(b["pen_k"] for b in brs), 1e-2)
# deciles of RFR per part (DGFiP table nid_25518): households, parts and RFR per decile (2024 table; the 2023
# table gives the bounds only), and beneficiaries of the main credits per decile (nid_25535) as box presence
import openpyxl
R = os.path.expanduser("~/fr/data/pop/raw/tables")
rpp = rfr / np.maximum(parts, 1)
ws = openpyxl.load_workbook(f"{R}/nid_25518_ir_deciles_rfr_par_part.xlsx", data_only=True)[f"a{year}"]
drows = [[v for v in r if v is not None] for r in ws.iter_rows(values_only=True)]
def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
dec = {}
for r in drows:
    if r and str(r[0]).strip() in [str(k) for k in range(1, 11)]:
        k = int(str(r[0]).strip())
        v = [fnum(x) for x in r[1:]]
        if year >= 2024:
            if k == 1:
                lo_, hi_, pm, rp = None, v[0], v[1], v[2]
            elif k == 10:
                lo_, hi_, pm, rp = v[0], None, v[1], v[2]
            else:
                lo_, hi_, pm, rp = v[0], v[1], v[2], v[3]
        else:
            lo_, hi_, pm, rp = v[0], v[1], None, None
        dec[k] = (lo_, hi_, pm, rp)
NDEC = irc["total"]["n"] / 10
for k, (lo_, hi_, pm, rp) in sorted(dec.items()):
    sel = (rpp > lo_ * 1000 if lo_ else True) & ((rpp <= hi_ * 1000) if hi_ else True)
    sel = np.asarray(sel, dtype=bool) if not isinstance(sel, bool) else np.full(n, sel)
    add(f"RFR/part decile {k}: households", sel, NDEC, 3e-3)
    if pm:
        add(f"RFR/part decile {k}: parts", sel * parts, pm * NDEC, 3e-3)
        if rp and k > 1:
            add(f"RFR/part decile {k}: RFR", sel * np.maximum(rfr, 0), rp * 1000 * pm * NDEC, 1e-2)
wc = openpyxl.load_workbook(f"{R}/nid_25535_ir_ci_deciles_rfr_par_part.xlsx", data_only=True)[f"{year} nombres"]
crow = [[v for v in r if v is not None] for r in wc.iter_rows(values_only=True)]
hdr = next(r for r in crow if r and str(r[0]).startswith("Numéro"))
tot = next(r for r in crow if r and str(r[0]).strip().startswith("Total"))
CIBOX = {"CI EMPLOI SALARIE A DOMICILE": ["7DB"], "CI FRAIS DE GARDE JEUNES ENFANTS": ["7GA", "7GB", "7GC", "7GE", "7GF", "7GG"],
         "CI COTISATIONS SYNDICALES": ["7AC", "7AE"]}
for name, bx in CIBOX.items():
    j = [str(h).strip() for h in hdr].index(name) - 3          # position among the device columns
    has = np.array([any(c["boxes"].get(b, 0) for b in bx) for c in cases])
    ratio = (sum(T["boxes"][b]["n"] for b in bx if b in T["boxes"]) / fnum(tot[3 + j])) if fnum(tot[3 + j]) else 1
    for r in crow:
        if r and str(r[0]).strip() in [str(k) for k in range(1, 11)]:
            k = int(str(r[0]).strip())
            vals = [fnum(x) for x in r[1:]]
            devs = vals[1:] if k in (1, 10) else vals[2:]   # deciles 1 and 10 print one bound only
            lo_, hi_ = dec[k][0], dec[k][1]
            sel = np.asarray((rpp > lo_ * 1000 if lo_ else np.ones(n, bool)) & ((rpp <= hi_ * 1000) if hi_ else True), dtype=bool)
            add(f"{name} decile {k}: households with {'/'.join(bx[:2])}", sel & has, min(ratio, 1.2) * devs[j], 1e-2)
for s in ("0AC", "0AD", "0AV", "0AM", "0AO"):
    add(f"box {s}: households", [1 if s in c["boxes"] else 0 for c in cases], T["boxes"][s]["n"], 1e-4)
modelled = json.load(open(os.path.expanduser(f"~/fr/data/pop/lean_boxes_{year}.json")))
skip = {"0AC", "0AD", "0AV", "0AM", "0AO", "2BH", "0DA", "0DB"}
used_boxes = []
for k, t in sorted(T["boxes"].items()):
    if k in skip or t["n"] < 20000:
        continue
    has = np.array([1.0 if c["boxes"].get(k, 0) else 0.0 for c in cases])
    if has.sum() < 30:
        continue
    used_boxes.append(k)
    add(f"box {k}: households", has, t["n"], 2e-3)
    if t["amount"] != t["n"]:
        add(f"box {k}: amount", [float(c["boxes"].get(k, 0)) for c in cases], t["amount"], 5e-3)

X = sp.csc_matrix(np.column_stack(cols))   # most columns are sparse indicators
m = X.shape[1]
c = np.array(soft)
NTOT = irc["total"]["n"]
X = X * NTOT          # work with u = w / NTOT (sums to about 1), so the dual is O(1)
# design weights: post-stratify the pool on the 13 IRCOM RFR groups (undoes the deliberate oversampling of the
# income tail), then entropy-balance away from them as little as the margins require
d = np.zeros(n)
for lo, hi in GROUPS:
    ing = (rfr > lo if lo else np.ones(n, bool)) & ((rfr <= hi) if hi else True)
    brs = [b for b in irc["brackets"] if b["lo"] >= lo and (hi is None or (b["hi"] is not None and b["hi"] <= hi))]
    d[ing] = sum(b["n"] for b in brs) / max(ing.sum(), 1)
d = d / d.sum()

# Bounded calibration: the logit distance of Deville and Särndal (1992), so every ratio g = w / d stays in [LO, UP].
# g(s) = UP - (UP - LO) a / (a + b e^{A s}), a = UP - 1, b = 1 - LO, A = (UP - LO) / (a b); g(0) = 1.
# Dual: minimise sum_i d_i G(x_i . lam) - sum_j lam_j + 1/2 sum_j c_j lam_j^2 with G(s) = int_0^s g, i.e.
# G(s) = UP s - (UP - LO) [s - (1/A) ln((a + b e^{A s}) / (a + b))].
LO, UP = float(os.environ.get("POP_LO", 0.05)), float(os.environ.get("POP_UP", 20))
a_, b_ = UP - 1, 1 - LO
A_ = (UP - LO) / (a_ * b_)
lab_ = np.log(a_ + b_)

def gfun(s):
    return UP - (UP - LO) * a_ * np.exp(-np.logaddexp(np.log(a_), np.log(b_) + A_ * s))

def Gfun(s):
    return UP * s - (UP - LO) * (s - (np.logaddexp(np.log(a_), np.log(b_) + A_ * s) - lab_) / A_)

def obj(lam):
    # columns of X are divided by their targets, so every moment X.T @ w must reach 1
    eta = X @ lam
    val = d @ Gfun(eta) - lam.sum() + 0.5 * (c * lam * lam).sum()
    g = X.T @ (d * gfun(eta)) - 1.0 + c * lam
    return val, g

r = minimize(obj, np.zeros(m), jac=True, method="L-BFGS-B", options={"maxiter": 30000, "maxfun": 60000, "gtol": 1e-12, "ftol": 1e-15})
lam = r.x
w = d * gfun(X @ lam)
ach = X.T @ w
print(f"bounds on w/d: [{LO}, {UP}]; at the lower bound {np.mean(w / d < LO * 1.01):.3%}, at the upper {np.mean(w / d > UP * 0.99):.3%}")
w = w * NTOT
ess = w.sum() ** 2 / (w * w).sum()
print(f"year {year}: {n} households, {m} constraints, converged={r.success} ({r.message}), iterations {r.nit}")
print(f"weights: sum {w.sum():.0f}, min {w.min():.3g}, median {np.median(w):.3g}, max {w.max():.4g}, Kish ESS {ess:.0f}")
with open(out_fit, "w") as fo:
    fo.write("margin\ttarget\tachieved\trel_error\n")
    errs = []
    for nm, t, a in zip(names, targets, ach):
        fo.write(f"{nm}\t{t:.0f}\t{a * t:.0f}\t{a - 1:+.4f}\n")
        errs.append((abs(a - 1), nm, a - 1))
errs.sort(reverse=True)
print("worst margins:", [(nm, round(e, 3)) for _, nm, e in errs[:12]])
for lim in (0.001, 0.01, 0.05, 0.10):
    print(f"  within {lim:.1%}: {sum(1 for e in errs if e[0] <= lim)}/{len(errs)}")
json.dump({"year": year, "weights": {cs["id"]: float(wi) for cs, wi in zip(cases, w)}, "boxes_calibrated": used_boxes,
           "ess": ess, "n": n, "constraints": m}, open(out_w, "w"))
