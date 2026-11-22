S = {'cc': 'UK', 'fam': 'Property', 'doc': '# UK 2025: transfer duties on purchases (4400); recurrent property tax not modelled\n\nSource: Finance Act 2003 s. 55, Sch. 4ZA, Sch. 6ZA at 2025-07-01 (legislation.gov.uk, `uk/law/fa2003_*_2025-07-01.html`); sha256 in `law/SHA256SUMS`.\n* s. 55 Table A (residential): "So much as does not exceed £125,000 0%"; "£125,000 ... £250,000 2%"; "£250,000 ... £925,000 5%"; "£925,000 ... £1,500,000 10%"; "The remainder 12%"\n* Table B (non-residential or mixed): "does not exceed £150,000 0%"; "£150,000 ... £250,000 2%"; "The remainder 5%"\n* Sch. 4ZA (higher rates for additional dwellings): 5 %, 7 %, 10 %, 15 %, 17 % on the same slices (5 points more)\n* Sch. 6ZA (first-time buyers): consideration "not more than £500,000": "So much as does not exceed £300,000 0%"; "Any remainder (so far as not exceeding £500,000) 5%"\n', 'lean': 'def d0 : TransferDuty :=\n  { name := "Stamp duty land tax (residential)",\n    sched := Schedule.ofList [(0, 0), (125000, 200), (250000, 500), (925000, 1000), (1500000, 1200)],\n    kinds := [.home],\n    firstHomeCap := 500000,\n    firstHomeSched := Schedule.ofList [(0, 0), (300000, 500)],\n    additionalBp := 500 }\n\ndef d1 : TransferDuty :=\n  { name := "Stamp duty land tax (non-residential)",\n    sched := Schedule.ofList [(0, 0), (150000, 200), (250000, 500)],\n    kinds := [.realEstate, .land] }', 'families': [('4400 transfer duties', ['.transactions'], 'd0.charges g.purchases "FA 2003 s. 55 Table A; Sch. 4ZA (+5 points); Sch. 6ZA (first-time buyers)"\n       ++ d1.charges g.purchases "FA 2003 s. 55 Table B"')], 'notes': ['UK 4400: legislation.gov.uk 2025-07-01 (bands from 1 April 2025)'], 'unsupported': [('g.purchases.any (·.nonResident)', 'non-resident surcharge (Sch. 9A, 2 points) not applied'), ('g.purchases.any (fun p => p.region == "Scotland" || p.region == "Wales")', 'LBTT (Scotland) and LTT (Wales) not modelled: SDLT applies in England and Northern Ireland'), ('g.assets.any (·.kind.isRealEstate)', 'recurrent property tax (4100) not modelled')], 'guards': ['d0.amount { kind := .home, price := 200000 } == 1500', 'd0.amount { kind := .home, price := 2000000 } == 153750', 'd0.amount { kind := .home, price := 500000, firstHome := true } == 10000', 'd0.amount { kind := .home, price := 500001, firstHome := true } == 15000', 'd0.amount { kind := .home, price := 300000, additionalHome := true } == 20000', 'd1.amount { kind := .realEstate, price := 200000 } == 1000', 'd1.amount { kind := .realEstate, price := 2000000 } == 89500'], 'taxes': [{'oecd': '4400', 'tax': 'Stamp duty land tax (residential)', 'statute': 'FA 2003 s. 55 Table A; Sch. 4ZA (+5 points); Sch. 6ZA (first-time buyers)', 'dated': 'legislation.gov.uk 2025-07-01 (bands from 1 April 2025)', 'grade': 'A', 'kernel_parts': ['TransferDuty'], 'unsupported': ['non-resident surcharge (Sch. 9A, 2 points) not applied', 'LBTT (Scotland) and LTT (Wales) not modelled: SDLT applies in England and Northern Ireland']}, {'oecd': '4400', 'tax': 'Stamp duty land tax (non-residential)', 'statute': 'FA 2003 s. 55 Table B', 'dated': 'legislation.gov.uk 2025-07-01 (bands from 1 April 2025)', 'grade': 'A', 'kernel_parts': ['TransferDuty'], 'unsupported': ['non-resident surcharge (Sch. 9A, 2 points) not applied', 'LBTT (Scotland) and LTT (Wales) not modelled: SDLT applies in England and Northern Ireland']}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'local', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["the default municipality's act and rate not read in the P5 pass; would unlock: the property-tax act and the reference municipality's rate (registry choice)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): council tax (Westminster) and business rates (England) ----
S["doc"] = S["doc"].replace("; recurrent property tax not modelled", "; council tax and business rates (4100)") + r'''

## Council tax (Westminster) and business rates (England), 2025-26 (pass 3)
Sources (legislation.gov.uk point-in-time 2025-04-01 and GOV.UK; sha256 in `law/SHA256SUMS`):
* **LGFA 1992 s. 5 (1)** (`lgfa1992_s5_2025-04-01`): amounts for bands A-H "in the proportion 6: 7: 8: 9: 11: 13: 15:
  18"; **s. 5 (2)** bands for England: "Values not exceeding £40,000 A ... exceeding £40,000 but not exceeding £52,000
  B ... £68,000 C ... £88,000 D ... £120,000 E ... £160,000 F ... £320,000 G ... exceeding £320,000 H" (values at
  1 April 1991).
* **Westminster Band D 2025-26 = £1,019.00**: MHCLG official statistics "Council Tax levels set by local authorities
  in England 2025 to 2026" (revised), Table 9 "Area council tax for a dwelling occupied by two adults by band"
  (`ct_levels_2025-26_tables1-9.ods`): "Westminster ... 679.33 | 792.56 | 905.78 | 1,019.00 | 1,245.44 | 1,471.89 |
  1,698.33 | 2,038.00" (area average: Westminster incl. adult social care and the Queen's Park parish precept,
  Table 8a 528.62, plus the GLA precept). Secondary source (the council's s. 30 resolution not read): grade B.
* **LGFA 1988 Sch. 4ZA para. 1** (`lgfa1988_sch4za_2025-04-01`): chargeable amount per day "A multiplied by M over C";
  para. 10: A = rateable value, B = the non-domestic rating multiplier, D = the small business multiplier, C = days
  in the year, M "whichever of B or D is prescribed ... by the Treasury in regulations".
* **SI 2024/111** reg. 2 (point in time 2025-04-01): "M is prescribed as D for any chargeable day for which A is not
  more than £50,999, but (b) in any other case M is prescribed as B".
* **Multipliers 2025-26** (Sch. 7 paras. A4, A6; SI 2024/1321 sets C = 132 for the small business multiplier): the
  values are in the Secretary of State's notice (not read); Business Rates Information Letter 4/2024 (GOV.UK,
  `bril_4_2024`): "The small business multiplier will be frozen at 49.9p. The standard multiplier will be uprated
  in April in line with September's CPI figure (1.6%), increasing the multiplier from 54.6p to 55.5p." Grade B.
Base: council tax on a household's `home`, banded on its `assessed` value (the 1 April 1991 value); without it the
market value stands in. Business rates on a company's `realEstate`, on its `annualValue` (the rateable value);
without one no charge is made (flagged).
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- LGFA 1992 s. 5 (2): band upper limits (1.4.1991 values) for A-G; above G is H. -/
def ctBandLimits : List Int := [40000, 52000, 68000, 88000, 120000, 160000, 320000]
/-- LGFA 1992 s. 5 (1): ninths of Band D, bands A-H. -/
def ctRatios : List Int := [6, 7, 8, 9, 11, 13, 15, 18]
/-- The band index (0 = A ... 7 = H) of a 1991 value. -/
def ctBand (v : Int) : Nat := (ctBandLimits.filter (fun l => l < v)).length
/-- Westminster area Band D 2025-26 in pence (MHCLG Table 9). -/
def westminsterBandD : Int := 101900
/-- Council tax for the year, whole pounds (rounded down): Band D x ratio / 9. -/
def councilTax (v : Int) : Int := divR .down (westminsterBandD * ctRatios.getD (ctBand v) 18) 900
/-- 2025-26 multipliers, tenths of a penny per pound (BRIL 4/2024). -/
def standardMultiplier : Int := 555
def smallBusinessMultiplier : Int := 499
/-- SI 2024/111 reg. 2: M = D where A is not more than £50,999, else B. -/
def multiplierFor (rv : Int) : Int := if rv ≤ 50999 then smallBusinessMultiplier else standardMultiplier
/-- Sch. 4ZA para. 1 over a full year (A x M), whole pounds rounded down. -/
def businessRates (rv : Int) : Int := divR .down (pos rv * multiplierFor rv) 1000
def councilTaxCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.assets.zipIdx.filter fun (a, _) => a.kind == .home).map fun (a, i) =>
    charge .propertyRecurrent "Council tax (Westminster)" a.statutoryValue (fun v => v) (fun v => councilTax v)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "LGFA 1992 s. 5 (1), (2); Westminster Band D 2025-26 £1,019.00 (MHCLG Table 9)")
def businessRateCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company then [] else
  (g.assets.zipIdx.filter fun (a, _) => a.kind == .realEstate && 0 ≤ a.annualValue).map fun (a, i) =>
    charge .propertyRecurrent "Non-domestic rates (England)" a.annualValue (fun v => v) (fun v => businessRates v)
      (event := s!"asset {i + 1}")
      (statute := "LGFA 1988 s. 43, Sch. 4ZA paras. 1, 10; SI 2024/111 reg. 2; multipliers 2025-26 55.5p / 49.9p (BRIL 4/2024)")
'''
S["families"] = S.get("families", []) + [("4100 council tax and business rates", [".propertyRecurrent"], "councilTaxCharges g ++ businessRateCharges g")]
S["unsupported"] = [u for u in S["unsupported"] if "4100" not in u[1]] + [
  ("g.entity != .company && g.assets.any (fun a => a.kind == .home && a.assessed < 0)", "4100 council tax: no 1991 value given: the market value stands in for the band"),
  ("g.entity != .company && g.assets.any (fun a => a.kind == .realEstate || a.kind == .land)", "4100 council tax: let or empty dwellings (tenant liability, empty-home premiums) and discounts (single person s. 11, 25 %) not applied"),
  ("g.entity == .company && g.assets.any (fun a => a.kind.isRealEstate && a.annualValue < 0)", "4100 business rates: no rateable value (annualValue) given: no charge made"),
  ("g.entity == .company && g.assets.any (·.kind.isRealEstate)", "4100 business rates: reliefs (small business rate relief SI 2023/1250, retail/hospitality/leisure, charitable, empty property) not applied")]
S["notes"] = S.get("notes", []) + ["UK 4100: council tax Westminster 2025-26 (Band D £1,019.00, MHCLG Table 9); business rates multipliers 2025-26 55.5p / 49.9p (BRIL 4/2024), SI 2024/111 threshold £50,999"]
S["guards"] = S.get("guards", []) + [
  "-- MHCLG Table 9, Westminster: A 679.33, D 1,019.00, H 2,038.00 (pence dropped)",
  "councilTax 40000 == 679", "councilTax 40001 == 792", "councilTax 88000 == 1019", "councilTax 88001 == 1245",
  "councilTax 320000 == 1698", "councilTax 320001 == 2038",
  "-- SI 2024/111: small business multiplier up to £50,999",
  "businessRates 50999 == 25448", "businessRates 51000 == 28305", "businessRates 0 == 0"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4100"] + [
 {"oecd": "4100", "tax": "Council tax (Westminster)", "statute": "Local Government Finance Act 1992 s. 5 (1), (2); Westminster Band D 2025-26",
  "dated": "legislation.gov.uk point in time 2025-04-01; Band D £1,019.00 from MHCLG Council Tax levels 2025 to 2026, Table 9 (official statistics)",
  "grade": "B", "kernel_parts": ["charge (band of the 1991 value x ratio/9 x Band D)"],
  "unsupported": ["Band D from official statistics (area average incl. Queen's Park parish), not the s. 30 resolution", "discounts, exemptions, premiums, council tax reduction", "1991 value is an input (asset.assessed)"]},
 {"oecd": "4100", "tax": "Non-domestic rates (England)", "statute": "Local Government Finance Act 1988 s. 43, Sch. 4ZA paras. 1, 10, Sch. 7 paras. A4, A6; SI 2024/111 reg. 2; SI 2024/1321",
  "dated": "legislation.gov.uk point in time 2025-04-01; multipliers 2025-26 55.5p and 49.9p from Business Rates Information Letter 4/2024",
  "grade": "B", "kernel_parts": ["charge (rateable value x multiplier)"],
  "unsupported": ["multiplier values from GOV.UK (the Secretary of State's notice not read)", "reliefs (small business rate relief, RHL, charitable, improvement), empty property rates", "rateable value is an input (asset.annualValue)"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")

# ---- FT review (2026-11-21): FA 2003 s. 75ZA non-resident rates and the £40,000 de minimis (FT1a dev failures) ----
S["doc"] += r'''

## FT review (2026-11-21): non-resident rates and the £40,000 de minimis
Sources (legislation.gov.uk point in time 2025-07-01; sha256 in `law/SHA256SUMS`):
* **FA 2003 s. 75ZA (1)** (`fa2003_s75za_2025-07-01`; inserted by FA 2021 Sch. 16 para. 2): "In its application for
  the purpose of determining the amount of tax chargeable in respect of a chargeable transaction that is a
  non-resident transaction, this Part has effect as if 2% were added to each rate specified in the rate-specifying
  provisions." **(2)**: "(a) in section 55(1B), Table A; (b) in Schedule 4ZA, in paragraph 1(2), Table A; ... (e) in
  Schedule 6ZA, in paragraph 4, Table A". 2 points on every slice of a table, the nil slice included, is 2 % of the
  whole consideration on top (`nonResidentBp := 200`); s. 55 Table B (non-residential) is not listed.
* **Sch. 9A para. 2 (1)** (`fa2003_sch9a_2025-07-01`): a non-resident transaction needs "(b) the main subject-matter
  of the transaction consists of— (i) a major interest in one or more dwellings" and "(d) the de minimis threshold is
  exceeded"; **para. 2 (3) (a)**: "the chargeable consideration for the transaction is £40,000 or more".
* **Sch. 4ZA para. 3 (1) (c), (2)** (`fa2003_sch4za_2025-07-01`): a single-dwelling purchase by an individual is a
  higher rates transaction only if "Conditions A to D are met"; "Condition A is that the chargeable consideration for
  the transaction is £40,000 or more."
The entity's `nonResident` flag stands for the Sch. 9A paras. 3-6 test (183 days); `additionalHome` for Conditions B-D.
'''
S["lean"] = S["lean"].replace("additionalBp := 500 }", "additionalBp := 500, nonResidentBp := 200 }") + r'''
/-- FA 2003 Sch. 4ZA para. 3 (2) (Condition A) and Sch. 9A para. 2 (1) (d), (3) (a): neither the higher rates nor the
non-resident rates apply where the chargeable consideration is under £40,000. -/
def deMinimis (p : Purchase) : Purchase :=
  if p.price < 40000 then { p with additionalHome := false, nonResident := false } else p
/-- Residential SDLT on one purchase: s. 55 Table A, Sch. 4ZA, Sch. 6ZA, s. 75ZA, with the de minimis. -/
def sdlt (p : Purchase) : Int := d0.amount (deMinimis p)
'''
_st_old = "FA 2003 s. 55 Table A; Sch. 4ZA (+5 points); Sch. 6ZA (first-time buyers)"
_st_new = "FA 2003 s. 55 Table A; Sch. 4ZA (+5 points from £40,000, para. 3 (2)); Sch. 6ZA (first-time buyers); s. 75ZA, Sch. 9A (non-resident +2 points from £40,000, para. 2 (3) (a))"
S["families"] = [(n, k, e.replace("d0.charges g.purchases", "d0.charges (g.purchases.map deMinimis)").replace(_st_old, _st_new)) for (n, k, e) in S["families"]]
S["unsupported"] = [u for u in S["unsupported"] if "Sch. 9A" not in u[1]]
S["guards"] = S["guards"] + [
  "-- s. 75ZA: 2 points on every slice of s. 55 Table A (1,500 + 2 % of 200,000)",
  "sdlt { kind := .home, price := 200000, nonResident := true } == 5500",
  "-- s. 75ZA (2) (e): Sch. 6ZA Table A 2 % to 300,000 and 7 % to 500,000",
  "sdlt { kind := .home, price := 400000, firstHome := true, nonResident := true } == 13000",
  "-- s. 75ZA (2) (b): Sch. 4ZA Table A 7 / 9 / 12 %",
  "sdlt { kind := .home, price := 300000, additionalHome := true, nonResident := true } == 26000",
  "-- Sch. 4ZA para. 3 (2) and Sch. 9A para. 2 (3) (a): the £40,000 edges",
  "sdlt { kind := .home, price := 39999, additionalHome := true } == 0",
  "sdlt { kind := .home, price := 40000, additionalHome := true } == 2000",
  "sdlt { kind := .home, price := 39999, nonResident := true } == 0",
  "sdlt { kind := .home, price := 40000, nonResident := true } == 800",
  "sdlt { kind := .home, price := 39999, additionalHome := true, nonResident := true } == 0",
  "-- s. 75ZA (2) does not list Table B: no non-resident rate on non-residential property",
  "d1.amount { kind := .realEstate, price := 200000, nonResident := true } == 1000"]
for _t in S["taxes"]:
    if _t["oecd"] == "4400":
        _t["unsupported"] = [u for u in _t["unsupported"] if "Sch. 9A" not in u]
        if "residential)" in _t["tax"] and "non-" not in _t["tax"]:
            _t["statute"] = _st_new
            _t["dated"] = "legislation.gov.uk 2025-07-01 (bands from 1 April 2025); s. 75ZA point in time 2025-07-01"
            _t["unsupported"] = _t["unsupported"] + ["Sch. 9A residence test (183 days) and company purchasers: the entity's nonResident flag is taken as given"]
