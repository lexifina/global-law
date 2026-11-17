"""Weighted totals of the calibrated population (Lean and M) against the DGFiP's published aggregates, coverage of the
published boxes and RICI by the Lean model, and the scale of each finding in the calibrated population.
usage: pop_report.py year   (reads runs/pop/<year>/{cases,lean,m,m_rejected}.jsonl, weights.json; data/pop/targets_<year>.json)
writes runs/pop/<year>/report.json and prints the tables."""
import json, math, os, sys, collections
import numpy as np

year = int(sys.argv[1])
H = os.path.expanduser("~/fr")
D = sys.argv[2] if len(sys.argv) > 2 else f"{H}/runs/pop/{year}"
T = json.load(open(f"{H}/data/pop/targets_{year}.json"))
W = json.load(open(f"{D}/weights.json"))["weights"]
cases = {json.loads(l)["id"]: json.loads(l) for l in open(f"{D}/cases.jsonl")}
L = {json.loads(l)["id"]: json.loads(l) for l in open(f"{D}/lean.jsonl")}
M = {json.loads(l)["id"]: json.loads(l) for l in open(f"{D}/m.jsonl")}
ids = [i for i in W if i in L]
w = np.array([W[i] for i in ids])
N = w.sum()
out = {"year": year, "households_weighted": N, "pool": len(ids)}

def lv(f):
    return np.array([L[i].get(f, 0.0) for i in ids])

def mv(f, fill=None):
    # M value; for returns M refuses, the Lean value of the matching field (documented fill)
    return np.array([M[i].get(f, 0.0) if i in M else (L[i].get(fill, 0.0) if fill else np.nan) for i in ids])

inM = np.array([i in M for i in ids])
out["m_refused_households_weighted"] = float(w[~inM].sum())
out["m_refused_pool"] = int((~inM).sum())

# ---------------- totals ----------------
lean_net = lv("IMPNET") + lv("CHRAPRES")
m_net = mv("IRN", "IMPNET") + mv("CHRAPRES", "CHRAPRES")
rows = []
def row(name, lean_val, m_val, pub, note=""):
    rows.append({"name": name, "lean": lean_val, "m": m_val, "published": pub, "note": note})

irc = T["ircom"]; bul = T["bulletin"]
row("households", N, N, irc["total"]["n"], "calibrated")
row("net income tax incl. CEHR (EUR)", float(w @ lean_net), float(w @ m_net), irc["total"]["tax_k"] * 1000,
    f"IRCOM 'impôt net (total)'; bulletin: {bul['net_tax']:.4g}")
row("  of which non-residents (published only)", None, None, irc["nonresidents"]["tax_k"] * 1000, "not in the pool")
row("taxed households (net tax > 0)", float(w @ (lean_net > 0)), float(w @ (m_net > 0)), irc["total"]["n_taxed"],
    f"bulletin: {bul['households_taxed']:.4g}")
row("tax at the scale after décote, before RICI (EUR)", float(w @ lv("IDRS4")), float(w @ mv("IDRS4", "IDRS4")),
    bul["tax_scale_before_rici"], "bulletin 'impôt au barème'")
row("flat-rate tax (PFU etc.) (EUR)", float(w @ lv("PFU")), float(w @ mv("IPROP", "PFU")), bul["tax_flat_hors_bareme"],
    "bulletin 'impôt hors barème'")
row("CEHR (EUR)", float(w @ lv("CHRAPRES")), float(w @ mv("CHRAPRES", "CHRAPRES")), bul["cehr"], "bulletin")
row("CEHR households", float(w @ (lv("CHRAPRES") > 0)), float(w @ (mv("CHRAPRES", "CHRAPRES") > 0)), None, "not published")
row("reductions (EUR)", float(w @ lv("ITRED")), float(w @ mv("ITRED", "ITRED")), bul["ri"], "bulletin, RI hors PFU")
row("credits excl. PFO (EUR)", float(w @ lv("CITOT")), float(w @ mv("IRE", "CITOT")), bul["ci"], "bulletin, CI hors PFU")
row("households with a reduction or credit", float(w @ ((lv("ITRED") + lv("CITOT")) > 0)),
    float(w @ ((mv("ITRED", "ITRED") + mv("IRE", "CITOT")) > 0)), bul["rici_n"], "bulletin")
row("décote (EUR)", float(w @ lv("IDEC")), float(w @ mv("IDEC", "IDEC")), None, "not published")
row("décote households", float(w @ (lv("IDEC") > 0)), float(w @ (mv("IDEC", "IDEC") > 0)), None, "not published")
iav_l = lv("IAVCR") + lv("CHRAPRES")
iav_m = mv("IAN", "IAVCR") + mv("CHRAPRES", "CHRAPRES")
row("households with tax before credits in (0, 61) EUR", float(w @ ((iav_l > 0) & (iav_l < 61))),
    float(w @ ((iav_m > 0) & (iav_m < 61))), None, "not published")
row("RFR (EUR)", float(w @ lv("REVKIRE")), float(w @ mv("REVKIRE", "REVKIRE")), irc["total"]["rfr_k"] * 1000, "calibrated by bracket")
out["totals"] = rows

# marginal rate (published by quotient familial = RNI / parts)
BOUNDS = {2023: [11294, 28797, 82341, 177106], 2024: [11497, 29315, 83823, 180294]}[year]
qf = lv("RNI") / np.maximum(lv("NBPT"), 1)
tmi = np.searchsorted(np.array(BOUNDS), qf, side="left")  # 0..4 ; QF <= bound stays in the lower band
tmi_rows = []
for k, p in enumerate(T["marginal"][:5]):
    sel = tmi == k
    tmi_rows.append({"band": p["label"], "rate": p["rate"], "published_n": p["n_k"] * 1000, "lean_n": float(w @ sel),
                     "published_tax": p["tax_M"] * 1e6, "lean_tax": float(w @ (lean_net * sel)),
                     "m_tax": float(w @ (m_net * sel))})
out["marginal"] = tmi_rows

# RFR brackets: tax and taxed households by IRCOM bracket (outcomes; counts were calibrated)
rfr = lv("REVKIRE")
br_rows = []
for b in irc["brackets"]:
    sel = (rfr > b["lo"]) & ((rfr <= b["hi"]) if b["hi"] else True) if b["lo"] else (rfr <= b["hi"])
    br_rows.append({"bracket": b["label"], "published_n": b["n"], "pool_n": float(w @ sel),
                    "published_tax": b["tax_k"] * 1000, "lean_tax": float(w @ (lean_net * sel)), "m_tax": float(w @ (m_net * sel)),
                    "published_taxed": b["n_taxed"], "lean_taxed": float(w @ (sel & (lean_net > 0)))})
out["brackets"] = br_rows

# deciles of RFR per part (table nid_25518, 2024 only: components per part): where the gap sits
dec_rows = []
if year >= 2024:
    rows25518 = [r for r in T["deciles_raw"] if r and str(r[0]).strip() in [str(k) for k in range(1, 11)]]
    rpp = rfr / np.maximum(lv("NBPT"), 1)
    NDEC = irc["total"]["n"] / 10
    for r in rows25518:
        k = int(str(r[0]).strip()); v = [float(x) if str(x).replace(".", "").replace("-", "").isdigit() else None for x in r[1:]]
        if k == 1:
            lo_, hi_, rest = None, v[0], v[1:]
        elif k == 10:
            lo_, hi_, rest = v[0], None, v[1:]
        else:
            lo_, hi_, rest = v[0], v[1], v[2:]
        pm, rp, bar, flat, ceh, rici, net = rest[:7]
        sel = np.asarray((rpp > lo_ * 1000 if lo_ else np.ones(len(ids), bool)) & ((rpp <= hi_ * 1000) if hi_ else True), dtype=bool)
        P = pm * NDEC * 1000   # parts x 1000 EUR (table in k EUR per part)
        dec_rows.append({"decile": k, "pub_scale": bar * P, "lean_scale": float(w @ (lv("IDRS4") * sel)),
                         "pub_flat": flat * P, "lean_flat": float(w @ (lv("PFU") * sel)),
                         "pub_cehr": ceh * P, "lean_cehr": float(w @ (lv("CHRAPRES") * sel)),
                         "pub_rici": rici * P, "lean_rici": float(w @ ((lv("ITRED") + lv("CITOT")) * sel)),
                         "pub_net": net * P, "lean_net": float(w @ (lean_net * sel))})
out["deciles"] = dec_rows

# ---------------- Lean vs M on the population ----------------
both = inM
d_net = (lean_net - m_net)
diff = both & (np.abs(d_net) > 0.5)
out["lean_vs_m"] = {"households_differing_net_tax": float(w @ diff), "pool_differing": int(diff.sum()),
                    "net_tax_difference_eur": float(w @ (d_net * both)),
                    "abs_difference_eur": float(w @ (np.abs(d_net) * both))}

# classify differences
def cls(i):
    b = cases[i]["boxes"]; l = L[i]; m = M[i]
    tags = []
    if b.get("2AB") and abs(l.get("CITOT", 0) - m.get("IRE", 0)) > 0.5:
        tags.append("2AB")
    if b.get("6GP") and abs(l.get("RNG", 0) - m.get("RNG", 0)) > 0.5:
        tags.append("6GP")
    if abs(l.get("CITOT", 0) - m.get("IRE", 0)) > 0.5 and (b.get("7AC") or b.get("7AE")) and (b.get("1GH", 0) > 5000 or b.get("1HH", 0) > 5000):
        tags.append("F1")
    if abs(l.get("CHRAPRES", 0) - m.get("CHRAPRES", 0)) > 0.5 and any(b.get(k) for k in ("5TA", "5TB", "5TE", "5UA", "5UB", "5UE")):
        tags.append("F2")
    if abs(l.get("IDRS4", 0) - m.get("IDRS4", 0)) in (1.0, 2.0) or abs(l.get("IMPNET", 0) - m.get("IRN", 0)) in (1.0, 2.0):
        if any(b.get(k) for k in ("5TA", "5TB", "5TE", "5UA", "5UB", "5UE")):
            tags.append("F5")
    return "+".join(tags) or "other"
cl = collections.defaultdict(lambda: [0.0, 0, 0.0])
examples = collections.defaultdict(list)
for k, i in enumerate(ids):
    if diff[k]:
        c = cls(i)
        cl[c][0] += w[k]; cl[c][1] += 1; cl[c][2] += w[k] * d_net[k]
        if len(examples[c]) < 5:
            examples[c].append({"id": i, "boxes": cases[i]["boxes"], "lean": {f: L[i].get(f) for f in ("IMPNET", "CITOT", "CHRAPRES", "IDRS4", "ITRED", "REVKIRE")},
                                "m": {f: M[i].get(f) for f in ("IRN", "IRE", "CHRAPRES", "IDRS4", "ITRED", "REVKIRE")}})
out["lean_vs_m"]["classes"] = {k: {"households": v[0], "pool": v[1], "net_eur": v[2]} for k, v in cl.items()}
out["lean_vs_m"]["examples"] = examples

# ---------------- findings in the population ----------------
F = {}
boxes = lambda f: np.array([float(cases[i]["boxes"].get(f, 0)) for i in ids])
# F1: union-dues credit (M = production uses 5 000 EUR in 2022-2024)
cit_d = mv("IRE", "CITOT") - lv("CITOT")
union = (boxes("7AC") > 0) | (boxes("7AE") > 0)
ot = ((boxes("1GH") > 5000) & (boxes("7AC") > 0)) | ((boxes("1HH") > 5000) & (boxes("7AE") > 0))
no2ab = boxes("2AB") == 0
F["F1"] = {"households_with_union_dues": float(w @ union), "with_overtime_over_5000_and_dues": float(w @ ot),
           "households_credit_differs": float(w @ (both & union & no2ab & (np.abs(cit_d) > 0.5))),
           "pool_credit_differs": int((both & union & no2ab & (np.abs(cit_d) > 0.5)).sum()),
           "eur_M_minus_Lean": float(w @ (cit_d * (both & union & no2ab)))}
# new: 2AB (tax credit on foreign securities income, art. 199 ter): M imputes it up to the tax and refunds nothing
# (chap-3.m CIRCMAVFT = min(IRB + ..., RCMAVFT)); Lean adds it to the refundable credits (Liquidation.lean, credits)
has2ab = boxes("2AB") > 0
F["L_2AB"] = {"households_with_2AB": float(w @ has2ab), "amount_2AB": float(w @ boxes("2AB")),
              "households_net_differs": float(w @ (both & has2ab & (np.abs(d_net) > 0.5))),
              "pool": int((both & has2ab & (np.abs(d_net) > 0.5)).sum()),
              "eur_Lean_minus_M_net": float(w @ (d_net * (both & has2ab)))}
# new: 6GP (alimony under a court decision before 2006): M deducts it increased by 25 % (chap-7.m TOTPA =
# arr(PAAV * MAJREV) + PAAP; art. 156, II, 2°); Lean deducts the amount as declared (Income.lean)
has6gp = (boxes("6GP") > 0) & ~has2ab
rng_d = lv("RNG") - mv("RNG", "RNG")
F["L_6GP"] = {"households_with_6GP": float(w @ (boxes("6GP") > 0)), "amount_6GP": float(w @ boxes("6GP")),
              "households_rng_differs": float(w @ (both & has6gp & (np.abs(rng_d) > 0.5))),
              "pool": int((both & has6gp & (np.abs(rng_d) > 0.5)).sum()),
              "taxable_income_Lean_minus_M": float(w @ (rng_d * (both & has6gp))),
              "eur_Lean_minus_M_net": float(w @ (d_net * (both & has6gp))),
              "households_net_differs": float(w @ (both & has6gp & (np.abs(d_net) > 0.5)))}
# F2: CEHR with flat-levy micro income
vl = sum(boxes(k) for k in ("5TA", "5TB", "5TE", "5UA", "5UB", "5UE")) > 0
ch_d = mv("CHRAPRES", "CHRAPRES") - lv("CHRAPRES")
F["F2"] = {"cehr_households": float(w @ (lv("CHRAPRES") > 0)), "cehr_households_with_flat_levy_micro": float(w @ ((lv("CHRAPRES") > 0) & vl)),
           "households_cehr_differs": float(w @ (both & (np.abs(ch_d) > 0.5))), "eur_M_minus_Lean": float(w @ (ch_d * both)),
           "flat_levy_micro_households": float(w @ vl)}
# F5: effective-rate rounding margin (tax at the scale differs by 1-2 EUR, flat-levy micro income present)
idr_d = mv("IDRS4", "IDRS4") - lv("IDRS4")
f5 = both & vl & (np.abs(idr_d) >= 0.5) & (np.abs(idr_d) <= 2.5)
F["F5"] = {"households": float(w @ f5), "pool": int(f5.sum()), "eur_M_minus_Lean_net": float(w @ (d_net * -1 * f5)),
           "effective_rate_households": float(w @ vl)}
# W1: tax under 61 EUR -> statute rate > 0, M/production 0
tx, tx61 = lv("TXFOYER"), lv("TXFOYER61")
den = lv("PASDEN")
w1 = (tx > 0) & (tx61 == 0)
F["W1"] = {"households": float(w @ w1), "pool": int(w1.sum()),
           "withholding_a_year_at_statute_rate_eur": float(w @ (w1 * tx / 100 * den)),
           "mean_rate": float((w * w1) @ tx / max(w @ w1, 1))}
# W2: rate rounding margin: 1000*num/den has a fraction in [0.49995, 0.5)
num = lv("PASNUM")
with np.errstate(divide="ignore", invalid="ignore"):
    x = np.where(den > 0, 1000 * num / den, 0)
frac = x - np.floor(x)
w2 = (den > 0) & (num > 0) & (frac >= 0.49995) & (frac < 0.5) & ~w1
F["W2"] = {"households": float(w @ w2), "pool": int(w2.sum()),
           "extra_withholding_a_year_eur": float(w @ (w2 * 0.001 * den)),
           "households_with_a_rate": float(w @ ((den > 0) & (num > 0)))}
# W4: couples' individualised rates, statute (couples' décote) vs single-person décote (M, production)
couple = np.array([("0AM" in cases[i]["boxes"] or "0AO" in cases[i]["boxes"]) for i in ids])
t1, t2, t1s, t2s = lv("TXDEC1"), lv("TXDEC2"), lv("TXDEC1S"), lv("TXDEC2S")
w4 = couple & ((np.abs(t1 - t1s) > 1e-9) | (np.abs(t2 - t2s) > 1e-9))
inc1 = sum(boxes(k) for k in ("1AJ", "1AS", "1AP", "1AZ", "1GB", "1AA"))
inc2 = sum(boxes(k) for k in ("1BJ", "1BS", "1BP", "1BZ", "1HB", "1BA"))
F["W4"] = {"couples": float(w @ couple), "couples_differing": float(w @ w4), "pool": int(w4.sum()),
           "abs_withholding_shift_a_year_eur": float(w @ (w4 * (np.abs(t1 - t1s) * inc1 + np.abs(t2 - t2s) * inc2) / 100)),
           "net_withholding_shift_a_year_eur_statute_minus_production": float(w @ (w4 * ((t1 - t1s) * inc1 + (t2 - t2s) * inc2) / 100))}
# F4 (OpenFisca): couples both 65 or over, art. 157 bis allowance; OpenFisca gives one instead of two
ages = np.array([(year - cases[i]["boxes"].get("0DA", year), year - cases[i]["boxes"].get("0DB", 0) if cases[i]["boxes"].get("0DB") else -1) for i in ids])
LIM = {2023: (17200, 27670, 2746, 1373), 2024: (17200, 27670, 2796, 1398)}[year]
rng = lv("RNG")
both65 = couple & (ages[:, 0] >= 65) & (ages[:, 1] >= 65)
f4 = both65 & (rng <= LIM[1])
allow = np.where(rng <= LIM[0], LIM[2], LIM[3])
rate = np.array([0.0, 0.11, 0.30, 0.41, 0.45])[tmi]
F["F4"] = {"couples_both_65_plus": float(w @ both65), "couples_eligible": float(w @ f4),
           "taxable_income_understated_eur": float(w @ (f4 * allow)),
           "tax_overstated_upper_eur": float(w @ (f4 * allow * rate)),
           "eligible_and_taxed": float(w @ (f4 & (lean_net > 0)))}
# OpenFisca RFR: exempt overtime not added
otb = boxes("1GH") + boxes("1HH") + boxes("1IH") + boxes("1JH")
F["OF_RFR_overtime"] = {"households": float(w @ (otb > 0)), "rfr_understated_eur_pool": float(w @ otb)}
# OpenFisca age on 1 January: a declarant turning 65 during the year (157 bis), or 75 (W/S half part)
t65 = (ages[:, 0] == 65) | (ages[:, 1] == 65)
F["OF_age"] = {"households_with_a_65th_birthday": float(w @ t65),
               "of_which_with_low_income_157bis": float(w @ (t65 & (rng <= LIM[1])))}
out["findings"] = F

json.dump(out, open(f"{D}/report.json", "w"), indent=1, default=float)

def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float) and abs(v) >= 1e9:
        return f"{v / 1e9:,.2f} bn"
    if isinstance(v, float) and abs(v) >= 1e6:
        return f"{v / 1e6:,.2f} M"
    return f"{v:,.0f}"
print(f"# income {year}: {len(ids)} pool households, weighted {N:,.0f}; M refused {out['m_refused_pool']} (weighted {out['m_refused_households_weighted']:,.0f}, Lean values used)")
print("| figure | published | Lean | M | Lean/pub | note |")
for r in rows:
    ratio = f"{r['lean'] / r['published']:.3f}" if r["published"] and r["lean"] is not None else ""
    print(f"| {r['name']} | {fmt(r['published'])} | {fmt(r['lean'])} | {fmt(r['m'])} | {ratio} | {r['note']} |")
print("\nmarginal rate bands:")
for r in tmi_rows:
    print(f"  {r['rate']:.2f}: households pub {fmt(r['published_n'])} Lean {fmt(r['lean_n'])}; tax pub {fmt(r['published_tax'])} Lean {fmt(r['lean_tax'])} M {fmt(r['m_tax'])}")
print("\nRFR brackets (tax, taxed households):")
for r in br_rows:
    print(f"  {r['bracket']:>24}: n pub {fmt(r['published_n'])} pool {fmt(r['pool_n'])} | tax pub {fmt(r['published_tax'])} Lean {fmt(r['lean_tax'])} M {fmt(r['m_tax'])} | taxed pub {fmt(r['published_taxed'])} Lean {fmt(r['lean_taxed'])}")
if dec_rows:
    print("\nRFR-per-part deciles (published vs Lean): scale | flat | CEHR | RICI | net")
    for r in dec_rows:
        print(f"  D{r['decile']:>2}: " + " | ".join(f"{fmt(r['pub_' + k])} / {fmt(r['lean_' + k])}" for k in ("scale", "flat", "cehr", "rici", "net")))
print("\nLean vs M:", {k: v for k, v in out["lean_vs_m"].items() if k != "examples"})
print("\nfindings:")
for k, v in F.items():
    print(" ", k, {a: (round(b, 1) if isinstance(b, float) else b) for a, b in v.items()})
