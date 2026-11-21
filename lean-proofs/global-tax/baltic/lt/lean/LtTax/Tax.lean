import LtTax.Npd

/-!
# Lithuania: one resident's income tax (GPM) and contributions, and the household

Individual taxation (no joint return in the GPMĮ). Everything in cents; the output is rounded half-up to euros.

Order of the statute (16 str. 1 d.): exempt income (17 str.) → business-certificate income (not modelled) →
individual-activity deductions (the contract's `selfEmployment` is already the taxable profit) → NPD (20 str.,
employment-related income only: 1 d. "taikomas tik su darbo santykiais ... susijusioms pajamoms") → the resident's
expenses (21 str.) → rates (6 str.) → the individual-activity credit (18² str.).
-/

namespace LtTax
open TaxKernel

/-- One person's income for the year (cents). -/
structure PIn where
  wages : Int := 0
  /-- individual-activity taxable income (individuali veikla, 10 str., after 18 str. deductions) -/
  ia : Int := 0
  interest : Int := 0
  dividends : Int := 0
  gains : Int := 0
  rent : Int := 0
  /-- 21 str. 1 d. 1, 2, 2¹ p. expenses claimed (life insurance, III-pillar pension) -/
  ded : Int := 0
  pillar2 : Bool := false
  /-- optional: the 12 monthly wages (cents) for the withholding path (20 str. 2, 8 d.); empty = equal months -/
  months : List Int := []

structure POut where
  gmp : Int
  npd : Int
  ded : Int
  empTaxable : Int
  empTax : Int
  iaGross : Int
  iaCredit : Int
  iaTax : Int
  otherTaxable : Int
  otherTax : Int
  divTax : Int
  gpm : Int
  npdMonthly : Int
  withheldEmp : Int
  social : Int
  iaSocial : Int

/-- 18² str. 2-4 d.: credit = income × 0,1 up to 20 000 €; above, "× (0,1 – 2/300 000 × (... – 20 000))", "Jeigu
... kreditas yra neigiamas, laikoma, kad jis lygus 0". In cents this is s × (3 500 000 – s) / 15 000 000. -/
def iaCredit (s : Int) : Int :=
  if s ≤ 0 then 0
  else if s ≤ 2000000 then divR .halfUp s 10
  else pos (divR .halfUp (s * (3500000 - s)) 15000000)

/-- 15 % of the individual-activity income minus the credit (18² str. 1 d.). -/
def iaTax (s : Int) : Int := pos (divR .halfUp (rate15 * pos s) BP - iaCredit s)

/-- Taxable interest, gains and rent (17 str. 1 d. 20 and 30 p. exemptions; rent fully taxable). -/
def otherTaxable (p : PIn) : Int := pos (p.interest - interestExempt) + pos (p.gains - gainExempt) + pos p.rent

/-- GMP, 20 str. 7 d.: "gyventojo mokestinio laikotarpio apmokestinamųjų pajamų ... sumai", except 5 %-rate income,
business-certificate income and some insurance/pension payouts, "neatėmus ... 21 straipsnyje nurodytų išlaidų ir ...
MNPD". So individual activity, dividends and other income all reduce the annual NPD on wages. -/
def gmpOf (p : PIn) : Int := pos p.wages + pos p.ia + pos p.dividends + otherTaxable p

/-- Employee contributions (Sodra): VSD 12.52 % to 60 VDU, PSD 6.98 %, optional II pillar 3 %. -/
def employeeSocial (yp : YP) (p : PIn) : Int :=
  (vsd yp).amount (pos p.wages) + psd.amount (pos p.wages) + (if p.pillar2 then pillar2.amount (pos p.wages) else 0)

/-- Individual-activity contributions: 90 % base, VSD 12.52 % to 43 VDU, PSD 6.98 % with the MMA monthly minimum when
the person has no employment insuring them. -/
def iaSocial (yp : YP) (p : PIn) : Int :=
  if p.ia ≤ 0 then 0 else
  let base := divR .halfUp (iaBasePct * p.ia) 100
  let v := divR .halfUp (vsdRate * min base (iaCeilingVdu * yp.vdu)) BP
  let h := divR .halfUp (psdRate * base) BP
  let hmin := if p.wages ≤ 0 then 12 * divR .halfUp (psdRate * yp.mma) BP else 0
  v + max h hmin

def person (yp : YP) (p : PIn) : POut :=
  let other := otherTaxable p
  let gmp := gmpOf p
  let npd := min (mnpd yp gmp) (pos p.wages)
  let empAfter := pos p.wages - npd
  -- 21 str. 3 d.: 25 % of the income taxed at 6 str. 1, 1¹, 1² d. rates after 16 str. 1 d. 1-5 p. (dividends excluded,
  -- [EM] "No deductions can be made to the income from distributed profit"), and 1 500 € for items 1, 2, 2¹.
  let ded := min (min (pos p.ded) dedCap) (min (dedPct * (empAfter + pos p.ia + other) / 100) empAfter)
  let empTaxable := empAfter - ded
  let empTax := yp.emp.tax Rule.unitHalfUp empTaxable
  let iaG := divR .halfUp (rate15 * pos p.ia) BP
  let iaT := iaTax p.ia
  let otherTax := (otherSched yp.vdu).tax Rule.unitHalfUp other
  let divTax := divR .halfUp (rate15 * pos p.dividends) BP
  -- monthly withholding (20 str. 2 d.): the employer applies the monthly NPD to each month's wages (equal months
  -- unless `months` is given); the 32 % applies once the cumulative amount passes 60 VDU (6 str. 1¹ d.)
  let m := pos p.wages / 12
  let npdM := if p.months.length = 12 then sumInts (p.months.map fun w => min (npdMonth yp (pos w)) (pos w))
    else 12 * min (npdMonth yp m) m
  let withheld := yp.emp.tax Rule.unitHalfUp (pos p.wages - npdM)
  { gmp, npd, ded, empTaxable, empTax, iaGross := iaG, iaCredit := iaG - iaT, iaTax := iaT,
    otherTaxable := other, otherTax, divTax, gpm := empTax + iaT + otherTax + divTax,
    npdMonthly := npdM, withheldEmp := withheld, social := employeeSocial yp p, iaSocial := iaSocial yp p }

/-! ## Household -/

def cents (x : Int) : Int := 100 * x
def euros (x : Int) : Int := divR .halfUp x 100

/-- Split the household's investment income and deductions between the adults (contract: equal halves). -/
def persons (c : Canon) : List PIn :=
  let p2 := c.bool? "pillar2" |>.getD false
  let monthsOf (k : String) : List Int :=
    let l := (arrField c.raw k).toList.filterMap fun j => match j.getNum? with
      | .ok n => some (cents (numToInt n)) | .error _ => none
    if l.length = 12 then l else []
  let mk (a : Adult) (f : Int → Int) (ms : List Int) : PIn :=
    { wages := if ms.length = 12 then sumInts ms else cents a.wages, months := ms, ia := cents a.selfEmployment, interest := f (cents c.interest),
      dividends := f (cents c.dividends), gains := f (cents c.capitalGains), rent := f (cents c.rentalIncome),
      ded := f (cents c.pensionContributions), pillar2 := p2 }
  match c.adults with
  | [a] => [mk a id (monthsOf "monthlyWages1")]
  | a :: b :: _ => [mk a half1 (monthsOf "monthlyWages1"), mk b half2 (monthsOf "monthlyWages2")]
  | [] => []

/-- Child benefits (Išmokų vaikams įstatymas): universal 1.75 BSI per child; additional 1.03 BSI per child for 3+
children, or for 1-2 children when net income per family member is at most 2 VRP a month ([EM] §2.6.3-2.6.4). -/
structure CB where
  universal : Int
  additional : Int
  eligible : Bool

def childBenefit (yp : YP) (kids members netAnnual : Int) : CB :=
  if kids ≤ 0 then ⟨0, 0, false⟩ else
  let u := yp.segs.foldl (fun acc s => acc + s.months * kids * divR .halfUp (cbUniversal * s.bsi) 100) 0
  let ok (s : Seg) : Bool := kids ≥ 3 || decide (netAnnual ≤ 12 * cbVrpMult * s.vrp * members)
  let a := yp.segs.foldl (fun acc s => acc + (if ok s then s.months * kids * divR .halfUp (cbAdditional * s.bsi) 100
    else 0)) 0
  ⟨u, a, yp.segs.any ok⟩

/-- The whole household in cents: (GPM, contributions, benefits, persons). -/
def household (yp : YP) (c : Canon) : Int × Int × CB × List POut :=
  let ps := (persons c).map (person yp)
  let gpm := sumInts (ps.map (·.gpm))
  let soc := sumInts (ps.map fun p => p.social + p.iaSocial)
  let gross := cents (c.adults.foldl (fun a x => a + x.wages + x.selfEmployment + x.pension) 0
    + c.interest + c.dividends + c.capitalGains + c.rentalIncome)
  let kids : Int := c.childrenUnder 18
  let cb := childBenefit yp kids (c.adults.length + kids) (gross - gpm - soc)
  (gpm, soc, cb, ps)

/-- Net household income in cents (gross − GPM − contributions + benefits), for the theorems. -/
def netCents (yp : YP) (c : Canon) : Int :=
  let (gpm, soc, cb, _) := household yp c
  let gross := cents (c.adults.foldl (fun a x => a + x.wages + x.selfEmployment + x.pension) 0
    + c.interest + c.dividends + c.capitalGains + c.rentalIncome)
  gross - gpm - soc + cb.universal + cb.additional

/-- The output for a given year record (`out` uses the statute's `yearParams`; `--euromod` the 30-June one). -/
def outWith (yp : YP) (c : Canon) : Out :=
  let (gpm, soc, cb, ps) := household yp c
  let s (f : POut → Int) := euros (sumInts (ps.map f))
  Out.make c "LT" "EUR" (euros gpm) (employeeSocial := euros soc) (benefits := euros (cb.universal + cb.additional))
    (detail := [Out.d "year" yp.year, Out.d "taxableIncome" (s (·.empTaxable)), Out.d "taxBeforeCredits" (euros gpm),
      Out.d "gmp" (s (·.gmp)), Out.d "npdAnnual" (s (·.npd)), Out.d "npdMonthlyTotal" (s (·.npdMonthly)),
      Out.d "deductions21" (s (·.ded)), Out.d "employmentTax" (s (·.empTax)),
      Out.d "withheldEmployment" (s (·.withheldEmp)),
      Out.d "annualSettlement" (s (fun p => p.empTax - p.withheldEmp)),
      Out.d "individualActivityTax" (s (·.iaTax)), Out.d "individualActivityCredit" (s (·.iaCredit)),
      Out.d "otherIncomeTax" (s (·.otherTax)), Out.d "dividendTax" (s (·.divTax)),
      Out.d "employeeContributions" (s (·.social)), Out.d "selfEmployedContributions" (s (·.iaSocial)),
      Out.d "childBenefitUniversal" (euros cb.universal), Out.d "childBenefitAdditional" (euros cb.additional),
      Out.dStr "note" "GPMĮ 2025 (2022-2024 and 2026 by year); cents internally; individual taxation"])
    (unsupported := ["disability NPD (GPMĮ 20 str. 6 d.)", "verslo liudijimas fixed tax (6 str. 3-5 d.)",
      "pensions treated as exempt state social insurance pensions (17 str.)",
      "21 str. expenses: only the household pensionContributions (III pillar / life insurance), split equally",
      "additional child benefit for a disabled child; children 18-22 in education",
      "2026: child benefits and the individual-activity regime"])

def out (c : Canon) : Out := outWith (yearParams c.year) c

/-- Round 15, `--euromod` only: EUROMOD's legislative parameters are those in force on 30 June of the policy year
(tests/convention_policy.json `euromod_convention_mode`; EUROMOD "Nowcasting prices" note Feb 2025, 1.3-1.4). The
country report LT keeps the full-year adjustment off in the baseline (CR LT, extensions: "full-year adjustments (FYA).
... are switched OFF in the baseline model") and prints the levels "effective on 30th June" (Table 1.2: BSI 46 €, VRP
147 € in 2022 from 1 June). So the segment in force on 30 June applies to all twelve months: 2022 BSI 46 € and VRP
147 € (Vyriausybės nutarimai, as the model's `y2022` segments); one-segment years are unchanged. -/
def june30Segs : List Seg → Nat → List Seg
  | [], _ => []
  | s :: rest, before =>
    if 6 ≤ before + s.months.toNat then [⟨12, s.bsi, s.vrp⟩] else june30Segs rest (before + s.months.toNat)

def yearParamsJune30 (y : Nat) : YP :=
  let q := yearParams y
  match q.segs with
  | [] => q
  | [_] => q
  | ss => { q with segs := june30Segs ss 0 }

def country : Country :=
  { code := "LT", name := "Lithuania", currency := "EUR", year := "2025", compute := out }

end LtTax
