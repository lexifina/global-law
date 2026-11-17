"""Scale of each finding from published counts (2042-nat boxes, IRCOM brackets), arithmetic shown.
Complements the calibrated-population estimates of pop_report.py. usage: pop_scale.py -> data/pop/scale.json"""
import csv, json, math, os
from scipy.stats import norm
from scipy.optimize import brentq

H = os.path.expanduser("~/fr")
B = {}
for r in csv.DictReader(open(f"{H}/data/pop/raw/ir-declarations-2042-nat.csv", encoding="utf-8-sig"), delimiter=";"):
    B.setdefault(int(r["annee"]), {})[r["nom"]] = (float(r["nombre"]), float(r["montant"]))
out = {}

def capped_lognormal(mean_target, sigma, cap):
    """mu such that E[min(X, cap)] = mean_target for X ~ LN(mu, sigma)."""
    def m(mu):
        z = (math.log(cap) - mu) / sigma
        part = math.exp(mu + sigma ** 2 / 2) * norm.cdf(z - sigma)
        return part + cap * (1 - norm.cdf(z)) - mean_target
    return brentq(m, -10, 30)

def p_above(mu, sigma, x):
    return 1 - norm.cdf((math.log(x) - mu) / sigma)

# ---- F1: union dues with exempt overtime between 5 000 and 7 500 EUR, income 2022-2024 ----
f1 = {}
for y in (2022, 2023, 2024):
    rows = {}
    for d, ot, sal, dues in (("declarant 1", "1GH", "1AJ", "7AC"), ("declarant 2", "1HH", "1BJ", "7AE")):
        n_ot, a_ot = B[y][ot]; n_sal = B[y][sal][0]; n_d, a_d = B[y][dues]
        mean = a_ot / n_ot
        shares = {}
        for s in (0.8, 1.0, 1.2):
            mu = capped_lognormal(mean, s, 7500)
            shares[s] = p_above(mu, s, 5000)
        union_rate = n_d / n_sal
        people = {s: n_ot * sh * union_rate for s, sh in shares.items()}
        rows[d] = {"overtime_n": n_ot, "overtime_mean": mean, "share_over_5000_by_sigma": shares,
                   "dues_n": n_d, "dues_mean": a_d / n_d, "dues_rate_among_salaried": union_rate,
                   "people_overtime_5000_7500_and_dues_by_sigma": people}
    lo = sum(min(r["people_overtime_5000_7500_and_dues_by_sigma"].values()) for r in rows.values())
    hi = sum(max(r["people_overtime_5000_7500_and_dues_by_sigma"].values()) for r in rows.values())
    f1[y] = {"by_person": rows, "people_low": lo, "people_high": hi,
             "eur_upper_bound_high": hi * 16.5,
             "note": "upper bound: 16.50 EUR each (66 % x 1 % x 2 500 EUR); the extra credit is paid only when dues exceed 1 % of the base"}
out["F1"] = f1

# ---- F2: CEHR and flat-levy micro income ----
T = json.load(open(f"{H}/data/pop/targets_2024.json"))
br = T["ircom"]["brackets"]
n_250 = sum(b["n"] for b in br if b["lo"] >= 300000) + 0.5 * sum(b["n"] for b in br if b["lo"] == 200000)
vl = sum(B[2024][k][0] for k in ("5TA", "5TB", "5TE", "5UA", "5UB", "5UE"))
vl_amt = sum(B[2024][k][1] for k in ("5TA", "5TB", "5TE", "5UA", "5UB", "5UE"))
share = vl / 41635259
out["F2"] = {"households_rfr_over_250k_approx": n_250, "flat_levy_filers": vl, "flat_levy_turnover": vl_amt,
             "flat_levy_share_all": share,
             "affected_if_same_share": n_250 * share, "affected_if_3x_share": n_250 * 3 * share,
             "note": "per household the program charges about CEHR x (flat-levy base / RFR) less: 1.4-2.3 % on the 22 production returns"}
# ---- F5 / W2: rounding margin ----
eff = vl + B[2024].get("8TI", (0, 0))[0] + B[2024].get("8TK", (0, 0))[0]
out["F5"] = {"effective_rate_households_approx": eff, "probability_per_rounding": 5e-5,
             "expected_households": eff * 5e-5, "eur_each": "1-2"}
# ---- W6: dependants' default grid, monthly base 8 739-8 788 EUR (income 2025 code) ----
w6 = {}
for k in ("1CJ", "1DJ"):
    n, a = B[2024][k]
    mean = a / n
    for s in (1.0, 1.5):
        mu = math.log(mean) - s * s / 2
        p = norm.cdf((math.log(8789 * 12) - mu) / s) - norm.cdf((math.log(8739 * 12) - mu) / s)
        w6[f"{k} sigma {s}"] = {"filers": n, "mean": mean, "share_in_band": p, "people": n * p}
out["W6"] = {"by_box": w6, "eur_each_month_max": 0.04 * 8788,
             "note": "default grid applies to dependants' own pay; a dependant earning 8 739-8 788 EUR a month (105 k a year) is rare"}
# ---- F8: OpenFisca JEI / JEIR reduction 2024 ----
n_cr, a_cr = B[2024]["7CR"]; n_dz, a_dz = B[2024]["7DZ"]
out["F8"] = {"7CR_n": n_cr, "7CR_amount": a_cr, "7DZ_n": n_dz, "7DZ_amount": a_dz,
             "reduction_upper_eur": 0.30 * a_cr + 0.50 * a_dz, "households_upper": n_cr + n_dz,
             "note": "M: 30 % of 7CR (cap 75 000 EUR per person), 50 % of 7DZ (cap 50 000), within the tax; OpenFisca leaves it out for 2024"}
# ---- OpenFisca RFR: exempt overtime ----
out["OF_RFR"] = {y: {"1GH_n": B[y]["1GH"][0], "overtime_amount": sum(B[y][k][1] for k in ("1GH", "1HH", "1IH", "1JH") if k in B[y])}
                 for y in (2022, 2023, 2024)}
json.dump(out, open(f"{H}/data/pop/scale.json", "w"), indent=1)
for k, v in out.items():
    print(k, json.dumps(v, default=float)[:900])
