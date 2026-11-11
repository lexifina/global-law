import LegalProofs.USTax.TaxCourt.Basic

/-!
# §911 foreign earned income and housing exclusions, and the §911(f) stacking rule (tax years 2012–2024)

* `feieCap y` — the §911(b)(2)(D) exclusion amount for calendar year `y`, from each year's revenue procedure.
* `proratedCap y days` — §911(b)(2)(A): the cap is limited to the part of the year in which the taxpayer qualifies
  (bona fide residence or physical presence, §911(d)(1)), "computed on a daily basis": `cap × days / days in year`.
* `housingBase`, `housingLimit`, `housingAmount` — §911(c)(1)–(2): the housing cost amount is the reasonable
  housing expenses (limited to 30% of the cap, prorated, unless a location listed in the year's notice has a higher
  limit) over 16% of the cap (prorated).
* `housingExclusion`, `housingDeduction` — §911(a)(2), §911(c)(4): the part of the housing amount paid for with
  employer-provided amounts is excluded; the rest is deductible (self-employed), limited to foreign earned income not
  otherwise excluded.
* `feie` — §911(d)(7): foreign earned income less the housing exclusion, up to the prorated cap.
* `stackedTax` — §911(f): tax = tax on (taxable income + excluded amount) − tax on the excluded amount.

Amounts are whole dollars; daily proration rounds the result to the nearest dollar once.
-/

namespace Legal.USTax.TaxCourt.Extra
open Legal.USTax.TaxCourt

/-- §911(b)(2)(D) exclusion amount, by year. 2012 Rev. Proc. 2011-52; 2013 Rev. Proc. 2013-15 (after ATRA); 2014
Rev. Proc. 2013-35; 2015 Rev. Proc. 2014-61; 2016 Rev. Proc. 2015-53; 2017 Rev. Proc. 2016-55; 2018 Rev. Proc.
2018-18; 2019 Rev. Proc. 2018-57; 2020 Rev. Proc. 2019-44; 2021 Rev. Proc. 2020-45; 2022 Rev. Proc. 2021-45; 2023
Rev. Proc. 2022-38; 2024 Rev. Proc. 2023-34. Zero outside 2012–2024. -/
def feieCap : Int → Int
  | 2012 => 95100
  | 2013 => 97600
  | 2014 => 99200
  | 2015 => 100800
  | 2016 => 101300
  | 2017 => 102100
  | 2018 => 104100
  | 2019 => 105900
  | 2020 => 107600
  | 2021 => 108700
  | 2022 => 112000
  | 2023 => 120000
  | 2024 => 126500
  | _ => 0

/-- Qualifying days clamped to `[0, days in year]`. -/
def clampDays (y days : Int) : Int := max 0 (min days (daysInYear y))

/-- §911(b)(2)(A): the cap for a year in which the taxpayer qualifies on `days` days. -/
def proratedCap (y days : Int) : Int :=
  roundDollar (feieCap y * clampDays y days) (daysInYear y)

/-- `bps` basis points of the cap, prorated by qualifying days (rounded once to the dollar). -/
def capShare (y days bps : Int) : Int :=
  roundDollar (feieCap y * bps * clampDays y days) (10000 * daysInYear y)

/-- §911(c)(1)(B): the base housing amount, 16% of the cap for each qualifying day. -/
def housingBase (y days : Int) : Int := capShare y days 1600

/-- §911(c)(2)(A): the default limit on housing expenses, 30% of the cap for each qualifying day. `limitOverride` is
the higher full-year limit for a location listed in the year's IRS notice (prorated the same way). -/
def housingLimit (y days : Int) (limitOverride : Option Int := none) : Int :=
  match limitOverride with
  | none => capShare y days 3000
  | some full => roundDollar (full * clampDays y days) (daysInYear y)

/-- §911(c)(1): the housing cost amount: reasonable housing expenses (up to the limit) over the base amount. -/
def housingAmount (y days expenses : Int) (limitOverride : Option Int := none) : Int :=
  pos (min expenses (housingLimit y days limitOverride) - housingBase y days)

/-- §911(a)(2), §911(c)(4)(A): the housing exclusion is the housing amount to the extent of employer-provided amounts
(and never more than foreign earned income). -/
def housingExclusion (y days expenses employerProvided fei : Int) (limitOverride : Option Int := none) : Int :=
  min (min (housingAmount y days expenses limitOverride) (pos employerProvided)) (pos fei)

/-- §911(d)(7), §911(b)(2)(A): the foreign earned income exclusion: foreign earned income less the housing exclusion,
up to the prorated cap. -/
def feie (y days fei housingExcl : Int) : Int :=
  min (pos (fei - housingExcl)) (proratedCap y days)

/-- §911(c)(4)(B): the housing deduction (housing amount not excluded, i.e. paid from self-employment), limited to
foreign earned income not excluded under §911(a)(1) or (a)(2). (The carryover of the disallowed part, §911(c)(4)(C),
is not modelled.) -/
def housingDeduction (y days expenses employerProvided fei : Int) (limitOverride : Option Int := none) : Int :=
  let ha := housingAmount y days expenses limitOverride
  let hx := housingExclusion y days expenses employerProvided fei limitOverride
  let ex := feie y days fei hx
  min (pos (ha - hx)) (pos (fei - hx - ex))

/-- **§911(f)(1)** (as amended by TIPRA 2005 §515; unchanged 2012–2024): if any amount is excluded under §911(a),
the tax is the tax on (taxable income + the excluded amount) less the tax on the excluded amount. `tax y f ti` is the
caller's regular-tax function (schedule or Table, with or without the capital gain worksheet); `excluded` is the
§911 exclusion total less the deductions disallowed by §911(d)(6) (Form 1040 Foreign Earned Income Tax Worksheet,
line 2c). No tax if taxable income is not positive. -/
def stackedTax {F : Type} (tax : Int → F → Int → Int) (y : Int) (f : F) (taxable excluded : Int) : Int :=
  if taxable ≤ 0 then 0
  else if excluded ≤ 0 then tax y f taxable
  else pos (tax y f (taxable + excluded) - tax y f excluded)

theorem feie_le_cap (y days fei hx : Int) : feie y days fei hx ≤ proratedCap y days := by
  unfold feie; omega

/-! ## Tests -/

-- Caps, per the revenue procedures.
#guard [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024].map feieCap =
  [95100, 97600, 99200, 100800, 101300, 102100, 104100, 105900, 107600, 108700, 112000, 120000, 126500]
-- A full year qualifies for the full cap (2024 has 366 days).
#guard proratedCap 2024 366 = 126500 ∧ proratedCap 2023 365 = 120000 ∧ proratedCap 2023 400 = 120000
-- Part-year: 2023, 75 qualifying days: 120,000 × 75 / 365 = 24,657.53 → 24,658.
#guard proratedCap 2023 75 = 24658
-- Form 2555 (2024) line 32 prints the base as $55.30 a day (16% × 126,500 / 366); a full year: $20,240.
#guard housingBase 2024 366 = 20240 ∧ housingBase 2024 100 = 5530
-- Form 2555 (2023): $52.60 a day; (2022): $49.10 a day (100 days).
#guard housingBase 2023 100 = 5260 ∧ housingBase 2022 100 = 4910
-- Default limit 30%: 2024 full year $37,950.
#guard housingLimit 2024 366 = 37950
-- Employee, 2024 full year, $150,000 wages, $45,000 housing (above the limit), employer-paid: housing amount
-- 37,950 − 20,240 = 17,710 excluded; FEIE min(150,000 − 17,710, 126,500) = 126,500; nothing left to deduct.
#guard housingAmount 2024 366 45000 = 17710
#guard housingExclusion 2024 366 45000 150000 150000 = 17710
#guard feie 2024 366 150000 17710 = 126500
#guard housingDeduction 2024 366 45000 150000 150000 = 0
-- Self-employed (no employer amounts), $130,000 earnings: FEIE 126,500, deduction limited to the $3,500 left.
#guard housingDeduction 2024 366 45000 0 130000 = 3500

/-- The 2024 single rate schedule (Rev. Proc. 2023-34 Table 3), whole dollars rounded half up (tests only). -/
private def sched24 (_ : Int) (_ : Unit) (x : Int) : Int :=
  let m := if x ≤ 0 then 0
    else if x ≤ 11600 then 100 * x
    else if x ≤ 47150 then 1160000 + 120 * (x - 11600)
    else if x ≤ 100525 then 5426000 + 220 * (x - 47150)
    else if x ≤ 191950 then 17168500 + 240 * (x - 100525)
    else if x ≤ 243725 then 39110500 + 320 * (x - 191950)
    else if x ≤ 609350 then 55678500 + 350 * (x - 243725)
    else 183647250 + 370 * (x - 609350)
  roundDollar m 1000

-- $50,000 taxable after excluding $126,500: tax on 176,500 (35,402.50) − tax on 126,500 (23,402.50) = 12,000:
-- every remaining dollar is taxed at 24%, not the $6,053 the bottom brackets would give.
#guard sched24 2024 () 50000 = 6053
#guard stackedTax sched24 2024 () 50000 126500 = 12000
#guard stackedTax sched24 2024 () 50000 0 = 6053
#guard stackedTax sched24 2024 () 0 126500 = 0

end Legal.USTax.TaxCourt.Extra
