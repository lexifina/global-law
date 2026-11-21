import NzTax.Model

/-!
# New Zealand: the canonical household (contract) in, the contract's output out

* Individual assessment (no joint return in New Zealand). Two adults are partners (married, civil union or de facto:
  Working for Families tests a "partner", which includes a de facto partner), whether or not `married` is set.
* Household investment income (interest, dividends, rent) and gifts are split equally between partners (`half1`,
  `half2`). Dividends are cash dividends from New Zealand companies, fully imputed (credit 28/72 of the cash).
* Capital gains: New Zealand has no general capital gains tax; gains on long-held listed shares held as an investor
  are not income (they are reported as untaxed; the bright-line test applies to residential land, not shares).
* `pension`: taxed as income; at age 65+ it is taken to be NZ Superannuation, which excludes the IETC.
* Children: dependent if under 18 (Working for Families); Best Start for a child aged 0 (first year, no income test,
  born before 1 April 2026) or aged 1-2 (abated).
* Extra input fields: `adults[i].studentLoan` (bool) adds the student loan repayment to `detail` (not a tax).
* `pensionContributions` (KiwiSaver member contributions) are not deductible and change no tax; the KiwiSaver
  government contribution is not modelled (listed in `unsupported` when contributions are given).
* Output: `incomeTax` = sum over persons of tax on taxable income − imputation credits used − IETC − donation
  credit (whole dollars, rounded half up from cents); `employeeSocial` = ACC earners' levy (whole dollars);
  `benefits` = Working for Families (FTC + IWTC + MFTC + Best Start); `detail` carries every figure in cents
  as dollars with two decimals.
-/

namespace NzTax
open TaxKernel Lean

/-- Cents to whole dollars, half up. -/
def toDollars (c : Int) : Int := (c + 50) / 100

/-- Cents as a JSON number of dollars with two decimals. -/
def money (c : Int) : Json := Json.num { mantissa := c, exponent := 2 }

def dm (k : String) (c : Int) : String × Json := (k, money c)

def adultStudentLoan (c : Canon) (i : Nat) : Bool :=
  match c.raw.getObjVal? "adults" with
  | .ok a => match a.getArrVal? i with
    | .ok ad => match ad.getObjVal? "studentLoan" with
      | .ok b => b.getBool?.toOption.getD false
      | .error _ => false
    | .error _ => false
  | .error _ => false

structure HouseholdResult where
  persons : List PersonOut
  wff : Wff
  ietcAllowed : List Bool
  deriving Repr

/-- The persons of a household, with investment income split equally; extension: `"investmentTo": 1` or `2` puts
all of it (interest, dividends, rent, gifts) on that adult (for the income-splitting scans). -/
def personsOf (c : Canon) : List PersonIn :=
  let two := c.adults.length == 2
  let to := (c.int? "investmentTo").getD 0
  let sh1 (x : Int) := if !two then x else if to == 1 then x else if to == 2 then 0 else half1 x
  let sh2 (x : Int) := if !two then 0 else if to == 2 then x else if to == 1 then 0 else half2 x
  c.adults.zipIdx.map fun (a, i) =>
    let f := if i == 0 then sh1 else sh2
    { age := a.age, wages := a.wages, selfEmployment := a.selfEmployment, pension := a.pension,
      interest := f c.interest, dividends := f c.dividends, rental := f c.rentalIncome, gifts := f c.charitable,
      studentLoan := adultStudentLoan c i }

def nzSuper (x : PersonIn) : Bool := x.age ≥ 65 && x.pension > 0

def householdCalc (c : Canon) : HouseholdResult :=
  let y2024 := c.year == 2024
  let p := paramsFor c.year
  let xs := personsOf c
  let first := xs.map fun x => person p y2024 x false
  let fsi := sumInts (first.map (·.netIncome))
  let tax := sumInts (first.map (·.taxOnIncome))
  let n := c.childrenUnder 18
  let nb0 := (c.children.filter (·.age == 0)).length
  let nb12 := (c.children.filter fun ch => ch.age == 1 || ch.age == 2).length
  let work := xs.any fun x => x.wages + x.selfEmployment > 0
  let wages := xs.any fun x => x.wages > 0
  let w := if y2024 then wff2024 n nb0 nb12 fsi work wages tax else wff p n nb0 nb12 fsi work wages tax
  let allowed := xs.map fun x => decide (w.total = 0) && !nzSuper x
  let ps := (xs.zip allowed).map fun (x, ok) => person p y2024 x ok
  { persons := ps, wff := w, ietcAllowed := allowed }

def personJson (x : PersonIn) (r : PersonOut) (ok : Bool) : Json := Json.mkObj [
  ("age", Json.num (JsonNumber.fromNat x.age)), dm "netIncome" r.netIncome, dm "taxableIncome" r.netIncome,
  dm "taxOnTaxableIncome" r.taxOnIncome, dm "imputationCredit" r.imputationCredit,
  dm "imputationCreditUsed" r.imputationUsed, dm "imputationCreditToLoss" r.imputationExcess,
  ("ietcEligible", Json.bool ok), dm "ietc" r.ietc, dm "donationCredit" r.donationCredit,
  dm "incomeTax" r.incomeTax, dm "accEarnersLevy" r.acc, dm "studentLoanRepayment" r.studentLoan]

/-- Extension: `"pieIncome"` (dollars, household total, attributed by a multi-rate PIE) taxed at `"pir"` (bp,
default 2800: 28 %, the top PIR) by the PIE as a final tax (IRD "Find your prescribed investor rate": PIRs 10.5 %,
17.5 %, 28 %). Not part of taxable income here; reported as the surtax `PIEtax`. -/
def pieTax (c : Canon) : Int := (c.int? "pir").getD 2800 * nzd ((c.int? "pieIncome").getD 0) / BP

/-- **Cost of living payment 2022** (Taxation (Cost of Living Payments) Act 2022; IRD Special report, July 2022,
"Eligibility": net income for 1 April 2021 - 31 March 2022 "of $70,000 or less", not eligible for a Winter Energy
Payment qualifying benefit (here: NZ super, `nzSuper`), "aged 18 or over"; a person with no net income has no
assessment and is not eligible ("Exclusion" paragraph); "$350 in total", paid August-October 2022, tax exempt). Paid
in the 2022-23 income year (household `year` 2022). The statute tests 2021-22 income, which the contract does not
carry: this year's net income stands in for it (listed in `unsupported`). Cents. -/
def costOfLiving2022 (c : Canon) (h : HouseholdResult) : Int :=
  if c.year != 2022 then 0 else
  let xs := personsOf c
  let n := ((xs.zip h.persons).filter fun (x, r) =>
    decide (x.age ≥ 18) && !nzSuper x && decide (0 < r.netIncome) && decide (r.netIncome ≤ nzd 70000)).length
  nzd 350 * (n : Int)

def out (c : Canon) : Out :=
  let h := householdCalc c
  let p := paramsFor c.year
  let xs := personsOf c
  let ps := h.persons
  let it := sumInts (ps.map (·.incomeTax))
  let ti := sumInts (ps.map (·.netIncome))
  let t0 := sumInts (ps.map (·.taxOnIncome))
  let acc := sumInts (ps.map (·.acc))
  let ie := sumInts (ps.map (·.ietc))
  let un := (if c.capitalGains ≠ 0 then ["capitalGains: not income (no general CGT; investor in listed shares)"] else [])
    ++ (if c.pensionContributions ≠ 0 then ["pensionContributions: KiwiSaver government contribution (s MK) not modelled; member contributions not deductible"] else [])
    ++ (if c.adults.length > 2 then ["more than two adults"] else [])
    ++ (if c.year ≤ 2023 then ["student loan repayment (detail only, when requested): the 2025-26 threshold is used for this year"] else [])
    ++ (if c.year == 2022 then ["cost of living payment 2022: eligibility read on this year's net income (the Act: 2021-22 net income)"] else [])
    ++ (if c.year < 2022 then [s!"income year {c.year} not modelled: 2022-23 rules used"] else [])
    ++ ["MFTC hours test (20/30 hours) assumed met by any salary or wage earner",
        "ACC self-employed minimum liable earnings and work levy not modelled",
        "Best Start and paid parental leave interaction not modelled"]
  let pie := pieTax c
  Out.make c "NZ" "NZD" (toDollars it) (surtaxes := if pie = 0 then [] else [("PIEtax", toDollars pie)])
    (employeeSocial := toDollars acc) (benefits := toDollars (h.wff.total + costOfLiving2022 c h))
    (detail := [
      ("incomeYear", Json.str p.year),
      ("taxableIncome", money ti), ("taxBeforeCredits", money t0), ("ietc", money ie),
      ("incomeTaxCents", money it), ("accEarnersLevy", money acc),
      ("familySchemeIncome", money (sumInts (ps.map (·.netIncome)))),
      dm "ftc" h.wff.ftc, dm "iwtc" h.wff.iwtc, dm "mftc" h.wff.mftc, dm "bestStart" h.wff.bestStart,
      dm "wffAbatement" h.wff.abatement, dm "wffTotal" h.wff.total,
      dm "studentLoanRepayment" (sumInts (ps.map (·.studentLoan))),
      ("employeeSocialIs", Json.str "ACC earners' levy (Accident Compensation Act 2001 ss 219-221); the OECD does not book it as a social contribution"),
      ("persons", Json.arr ((xs.zip (ps.zip h.ietcAllowed)).map fun (x, r, ok) => personJson x r ok).toArray)])
    (unsupported := un)

def country : Country :=
  { code := "NZ", name := "New Zealand", currency := "NZD", year := "2025-26 (1 April 2025 - 31 March 2026)",
    compute := out }

end NzTax
