import LegalProofs.USTax.TaxCourt.Params

/-!
# §36B premium tax credit and the §36B(f) reconciliation, tax years 2014–2024

The annual computation of Form 8962 (Parts I–II, annual column; Part III):

* **Household income** (§36B(d)(2)): the modified AGI of the taxpayer and of every member of the family required to
  file — AGI plus tax-exempt interest, the social security benefits excluded under §86, and §911 exclusions. All
* **Poverty line** (§36B(d)(3)): the HHS guidelines for the year *before* the tax year (48 states and D.C., Alaska,
  Hawaii), as printed in Form 8962 Table 1-1: base + increment × (family size − 1), except the 2016 guidelines (tax
  year 2017), printed size by size to 8 (`fplTable2017`).
* **Line 5** (household income as a percentage of the poverty line): from 2015 Worksheet 2's "drop any numbers after
  the decimal point" (401 if over 400%); for 2014 the instructions' own rule (`line5_2014`).
* **Applicable figure** (§36B(b)(3)(A); Table 2): linear within each band of the year's table, rounded half up to the
  basis point — `figure` reproduces every printed Table 2 entry 2014–2024. Bands: 2014–2020 under 133%, 133–150, 150–200,
  200–250, 250–300, 300–400 (Rev. Procs. 2014-37, 2017-36, 2018-34, 2019-29 and the statute for 2014); 2021–2024
  (ARPA §9661, extended by Pub. L. 117-169 §12001) 0% to 150%, 2%, 4%, 6% at 200/250/300%, 8.5% at 400% and over.
* **Eligibility**: 2014–2020, line 5 from 100 to 400; 2021–2024, at least 100 (§36B(c)(1)(E): no upper limit). Under
  100% only with the Form 8962 exceptions (Marketplace estimate of at least 100% and advance payments, or a lawfully
  present alien ineligible for Medicaid; `below100Allowed`). Married filing separately: no credit (§36B(c)(1)(C)),
  unless the domestic-abuse / abandonment relief applies (`mfsRelief`).
* **Credit** (§36B(b)(2), annual): the smaller of the enrolled premiums and the benchmark (second lowest cost silver
  plan) premium less the contribution (household income × applicable figure, rounded to the dollar).
* **Reconciliation** (§36B(f)): advance payments over the credit increase tax, capped (§36B(f)(2)(B), Table 5) below
  400%; no cap at 400% or more; for 2020 no increase at all (§36B(f)(2)(B)(iii), Pub. L. 117-2 §9662). A credit over
  the advance payments is refundable (net premium tax credit).

Not modelled: monthly computation (coverage for part of the year, changes in family), shared policy allocation,
alternative calculation for the year of marriage, self-employed health insurance iteration.
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-- (base, increment) of the poverty guidelines used for tax year `y` (the prior year's HHS guidelines, Form 8962
Table 1-1): 0 = 48 states and D.C., 1 = Alaska, 2 = Hawaii. -/
def fplParams (y : Nat) (state : Nat) : Int × Int :=
  match y, state with
  | 2014, 0 => (11490, 4020) | 2014, 1 => (14350, 5030) | 2014, _ => (13230, 4620)
  | 2015, 0 => (11670, 4060) | 2015, 1 => (14580, 5080) | 2015, _ => (13420, 4670)
  | 2016, 0 => (11770, 4160) | 2016, 1 => (14720, 5200) | 2016, _ => (13550, 4780)
  | 2018, 0 => (12060, 4180) | 2018, 1 => (15060, 5230) | 2018, _ => (13860, 4810)
  | 2019, 0 => (12140, 4320) | 2019, 1 => (15180, 5400) | 2019, _ => (13960, 4970)
  | 2020, 0 => (12490, 4420) | 2020, 1 => (15600, 5530) | 2020, _ => (14380, 5080)
  | 2021, 0 => (12760, 4480) | 2021, 1 => (15950, 5600) | 2021, _ => (14680, 5150)
  | 2022, 0 => (12880, 4540) | 2022, 1 => (16090, 5680) | 2022, _ => (14820, 5220)
  | 2023, 0 => (13590, 4720) | 2023, 1 => (16990, 5900) | 2023, _ => (15630, 5430)
  | _, 0 => (14580, 5140) | _, 1 => (18210, 6430) | _, _ => (16770, 5910)

/-- 2016 HHS guidelines (81 FR 4036; tax year 2017), sizes 1–8, then the increment. -/
def fplTable2017 (state : Nat) : List Int × Int :=
  match state with
  | 0 => ([11880, 16020, 20160, 24300, 28440, 32580, 36730, 40890], 4160)
  | 1 => ([14840, 20020, 25200, 30380, 35560, 40740, 45920, 51120], 5200)
  | _ => ([13670, 18430, 23190, 27950, 32710, 37470, 42230, 47010], 4780)

def fpl (y : Nat) (state : Nat) (size : Nat) : Int :=
  let n := max size 1
  if y == 2017 then
    let (t, inc) := fplTable2017 state
    if n ≤ 8 then t.getD (n - 1) 0 else t.getD 7 0 + inc * ((n : Int) - 8)
  else
    let (b, inc) := fplParams y state
    b + inc * ((n : Int) - 1)

/-- 2014 line 5 (Form 8962 instructions (2014)): r = income ÷ poverty line; under 1.00 round down; 1.00–3.99 round to
the nearest percent; between 3.99 and 4.00 enter 399; over 4.00 round up; over 9.99 enter 999. -/
def line5_2014 (F h : Int) : Int :=
  if h < F then 100 * h / F
  else if 100 * h ≤ 399 * F then (200 * h + F) / (2 * F)
  else if 100 * h < 400 * F then 399
  else if 100 * h = 400 * F then 400
  else if 100 * h ≤ 999 * F then (100 * h + F - 1) / F
  else 999

/-- Line 5 for the year. -/
def line5 (y : Nat) (F h : Int) : Int :=
  if y == 2014 then line5_2014 F h else if 4 * F < h then 401 else 100 * h / F

/-- The year's applicable percentage table (2014–2020), in basis points: under 133%, and at 133, 150, 200, 250 and
300–400%. -/
def pctTable (y : Nat) : List Int :=
  match y with
  | 2014 => [200, 300, 400, 630, 805, 950]   -- §36B(b)(3)(A)(i) as enacted; Form 8962 (2014) Table 2
  | 2015 => [201, 302, 402, 634, 810, 956]   -- Rev. Proc. 2014-37
  | 2016 => [203, 305, 407, 641, 818, 966]   -- Form 8962 (2016) Table 2
  | 2017 => [204, 306, 408, 643, 821, 969]   -- Rev. Proc. 2016-24
  | 2018 => [201, 302, 403, 634, 810, 956]   -- Rev. Proc. 2017-36
  | 2019 => [208, 311, 415, 654, 836, 986]   -- Rev. Proc. 2018-34
  | _ => [206, 309, 412, 649, 829, 978]      -- 2020: Rev. Proc. 2019-29

/-- Linear between (a, lo) and (b, hi), rounded half up to the basis point. -/
def interp (a b lo hi p : Int) : Int := (2 * (lo * (b - a) + (hi - lo) * (p - a)) + (b - a)) / (2 * (b - a))

/-- **The applicable figure** (basis points) for line 5 = `p`. -/
def figure (y : Nat) (p : Int) : Int :=
  if y ≥ 2021 then
    if p ≤ 150 then 0 else if p < 200 then interp 150 200 0 200 p else if p < 250 then interp 200 250 200 400 p
    else if p < 300 then interp 250 300 400 600 p else if p < 400 then interp 300 400 600 850 p else 850
  else
    match pctTable y with
    | [r0, r133, r150, r200, r250, r300] =>
      if p < 133 then r0 else if p < 150 then interp 133 150 r133 r150 p
      else if p < 200 then interp 150 200 r150 r200 p else if p < 250 then interp 200 250 r200 r250 p
      else if p < 300 then interp 250 300 r250 r300 p else r300
    | _ => 0

/-- §36B(f)(2)(B) caps (Form 8962 Table 5): (single, other) for line 5 under 200, 200–299, 300–399. -/
def repayCaps (y : Nat) : List (Int × Int) :=
  match y with
  | 2014 | 2015 => [(300, 600), (750, 1500), (1250, 2500)]
  | 2016 | 2017 => [(300, 600), (750, 1500), (1275, 2550)]
  | 2018 => [(300, 600), (775, 1550), (1300, 2600)]
  | 2019 => [(300, 600), (800, 1600), (1325, 2650)]
  | 2020 | 2021 => [(325, 650), (800, 1600), (1350, 2700)]
  | 2022 => [(325, 650), (825, 1650), (1400, 2800)]
  | 2023 => [(350, 700), (900, 1800), (1500, 3000)]
  | _ => [(375, 750), (950, 1900), (1575, 3150)]

def repayCap (y : Nat) (single : Bool) (p : Int) : Option Int :=
  let pick (c : Int × Int) := if single then c.1 else c.2
  let cs := repayCaps y
  if p < 200 then some (pick (cs.getD 0 (0, 0))) else if p < 300 then some (pick (cs.getD 1 (0, 0)))
  else if p < 400 then some (pick (cs.getD 2 (0, 0))) else none

/-- What the court finds for §36B (annual amounts). -/
structure PtcFacts where
  familySize : Nat := 1
  /-- "contiguous" (48 states and D.C.), "alaska" or "hawaii". -/
  state : String := "contiguous"
  /-- Annual premiums of the plans enrolled in (Form 1095-A column A) and of the benchmark plan (column B). -/
  enrolledPremium : Int := 0
  benchmarkPremium : Int := 0
  /-- Advance payments received (column C). -/
  advancePayments : Int := 0
  /-- MAGI of dependents required to file, added to household income (§36B(d)(2)(A)(ii)). -/
  dependentsMagi : Int := 0
  /-- Household income as found, when the opinion states it. -/
  householdIncomeOverride : Option Int := none
  /-- Under 100%: one of the Form 8962 exceptions applies. -/
  below100Allowed : Bool := false
  /-- Married filing separately: the domestic abuse / abandonment relief applies. -/
  mfsRelief : Bool := false
  /-- Otherwise an applicable taxpayer with coverage that qualifies (not eligible for other minimum essential coverage,
  not a dependent of another). False: no credit, only reconciliation. -/
  eligible : Bool := true
  deriving Repr, Inhabited

structure PtcResult where
  householdIncome : Int := 0
  povertyLine : Int := 0
  /-- Form 8962 line 5. -/
  fplPercent : Int := 0
  applicableFigure : Int := 0
  contribution : Int := 0
  credit : Int := 0
  /-- §36B(f)(2): the increase in tax for excess advance payments. -/
  excessAdvanceRepayment : Int := 0
  /-- Net premium tax credit (refundable). -/
  netCredit : Int := 0
  reasons : List String := []
  deriving Repr, Inhabited, DecidableEq

def stateCode (s : String) : Nat :=
  if s.toLower == "alaska" || s.toLower == "ak" then 1 else if s.toLower == "hawaii" || s.toLower == "hi" then 2 else 0

/-- **§36B for the year.** `magi`: the taxpayer's AGI plus tax-exempt interest, excluded social security and §911
exclusions. -/
def premiumTaxCredit (p : Params) (f : Filing) (magi : Int) (x : PtcFacts) : PtcResult :=
  if p.year < 2014 then { reasons := ["§36B applies from 2014"] } else
  let h := x.householdIncomeOverride.getD (magi + x.dependentsMagi)
  let F := fpl p.year (stateCode x.state) x.familySize
  let pct := line5 p.year F h
  let fig := figure p.year pct
  let contribution := roundDollar (h * fig) 10000
  let reasons : List String :=
    (if pct < 100 && !x.below100Allowed then ["§36B(c)(1)(A) household income under 100% of the poverty line"] else []) ++
    (if p.year ≤ 2020 && pct > 400 then ["§36B(c)(1)(A) household income over 400% of the poverty line"] else []) ++
    (if f == .mfs && !x.mfsRelief then ["§36B(c)(1)(C) married filing separately"] else []) ++
    (if x.eligible then [] else ["not an applicable taxpayer / coverage not eligible"])
  let credit := if reasons.isEmpty then min (pos x.enrolledPremium) (pos (x.benchmarkPremium - contribution)) else 0
  let excess := pos (x.advancePayments - credit)
  let repay := if p.year == 2020 then 0 else
    match repayCap p.year (f == .single) pct with
    | some cap => min excess cap
    | none => excess
  { householdIncome := h, povertyLine := F, fplPercent := pct, applicableFigure := fig, contribution := contribution,
    credit := credit, excessAdvanceRepayment := repay, netCredit := pos (credit - pos x.advancePayments),
    reasons := reasons }

/-! ## Tests: Form 8962 tables -/

section
private def py (y : Nat) : Params := (params? y).getD default

-- Table 1-1: 2015 family of 2, 48 states: $15,730; 2017 family of 7: $36,730; 2024 Alaska family of 1: $18,210.
#guard fpl 2015 0 2 = 15730 ∧ fpl 2017 0 7 = 36730 ∧ fpl 2017 0 9 = 45050 ∧ fpl 2024 1 1 = 18210
-- Table 2 entries: 2014 under 133 → 0.0200, 133 → 0.0300, 300–400 → 0.0950; 2015 at 200 → 0.0634;
-- 2021 at 301 → 0.0603 (602.5 rounded up); 2024 at 400 → 0.0850, 150 → 0.
#guard figure 2014 120 = 200 ∧ figure 2014 133 = 300 ∧ figure 2014 350 = 950 ∧ figure 2015 200 = 634
#guard figure 2021 301 = 603 ∧ figure 2024 400 = 850 ∧ figure 2024 150 = 0 ∧ figure 2024 175 = 100
-- 2014 line 5: 1.854 → 185, 3.565 → 357, 0.996 → 99, 4.004 → 401.
#guard line5_2014 1000 1854 = 185 ∧ line5_2014 1000 3565 = 357 ∧ line5_2014 1000 996 = 99 ∧ line5_2014 1000 4004 = 401

-- 2018 single, family of 1, household income $24,120 (200% of $12,060): figure 0.0634, contribution $1,529;
-- benchmark $6,000, enrolled $5,000: credit $4,471; advance $5,000: excess $529, capped at $775 → $529.
private def f2018 : PtcFacts := { benchmarkPremium := 6000, enrolledPremium := 5000, advancePayments := 5000 }
private def r2018 : PtcResult :=
  { householdIncome := 24120, povertyLine := 12060, fplPercent := 200, applicableFigure := 634, contribution := 1529,
    credit := 4471, excessAdvanceRepayment := 529, netCredit := 0, reasons := [] }
#guard premiumTaxCredit (py 2018) .single 24120 f2018 = r2018
-- 2019 single at 250%: cap $800 on a $3,000 excess; 2020: nothing repaid.
#guard (premiumTaxCredit (py 2019) .single 30350 { advancePayments := 3000, eligible := false }).excessAdvanceRepayment
  = 800
#guard (premiumTaxCredit (py 2020) .single 31225 { advancePayments := 3000, eligible := false }).excessAdvanceRepayment
  = 0
-- 2022 at 500%: still eligible (ARPA): 8.5% of $64,400 = $5,474; benchmark $8,000: credit $2,526.
#guard (premiumTaxCredit (py 2022) .single 64400 { benchmarkPremium := 8000, enrolledPremium := 8000 }).credit = 2526
end

end Legal.USTax.TaxCourt
