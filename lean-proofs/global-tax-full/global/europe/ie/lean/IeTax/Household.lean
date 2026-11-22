import IeTax.Model

/-!
# Canonical household → Irish return(s) → contract output

* Each adult is a person: `wages` → PAYE emoluments with PRSI Class A1; `pension` → an occupational pension (PAYE
  emoluments, no PRSI); `selfEmployment` → Case I/II profits (earned income credit, Class S, USC surcharge).
* Household `interest` (deposit interest, DIRT), `dividends` (Irish, Schedule F), `rentalIncome` (Case V),
  `capitalGains` (CGT) are split equally between two adults (`half1`/`half2`).
* `pensionContributions` (household total): given first to adult 1 up to that adult's age-related limit, the rest
  to adult 2 (the household's choice; relief is not transferable).
* `charitable`: no effect. Since 2013 relief on donations under s. 848A goes to the charity, not the donor.
* Children under 18 are qualified children (child benefit, WFP, s. 462B, s. 466A, s. 188(2A)).
* Extra input fields: `ieShare1` (percent of investment income and gains held by adult 1), `ieDirector` (adult 1
  is a proprietary director paid `wages` by their own company).
* Options: `--joint` (married: joint assessment only), `--single` (married: each spouse single); `--oecd` = the
  OECD's conventions (`--prsi41`: PRSI 4.1 % all year; `--wfp-exact`: WFP weekly rate not rounded up).
Output money in whole euros (half up from cents); the cents are in `detail`.
-/

namespace IeTax
open TaxKernel Lean

def toCents (x : Int) : Int := 100 * x
def euros (c : Int) : Int := divR .halfUp c 100

def mkHH (c : Canon) : HH :=
  let n := c.adults.length
  -- extra field "ieShare1": percent of interest, dividends, rent and gains held by adult 1 (default: equal halves)
  let sh (x : Int) (i : Nat) : Int :=
    if n == 2 then
      match c.int? "ieShare1" with
      | some k => let a := x * (max 0 (min 100 k)) / 100; if i == 0 then a else x - a
      | none => if i == 0 then half1 x else half2 x
    else x
  let dir := (c.bool? "ieDirector").getD false
  let base := c.adults.zipIdx.map fun (a, i) =>
    ({ age := a.age, wages := toCents a.wages, pension := toCents a.pension, se := toCents a.selfEmployment,
       dividends := toCents (sh c.dividends i), rent := toCents (sh c.rentalIncome i),
       interest := toCents (sh c.interest i), gains := toCents (sh c.capitalGains i),
       director := dir && i == 0 } : Person)
  -- pension contributions: adult 1 up to the limit, the rest to adult 2
  let pc := toCents (pos c.pensionContributions)
  let limit (p : Person) : Int := pensionPct p.age * min (pos (p.wages + p.se)) pensionEarningsCap / BP
  let persons := match base with
    | [p] => [{ p with contrib := pc }]
    | [p1, p2] =>
      let c1 := min pc (limit p1)
      [{ p1 with contrib := c1 }, { p2 with contrib := pc - c1 }]
    | l => l
  { persons, married := c.married && n == 2, kids := c.childrenUnder 18 }

def itJson (r : ITResult) : Json := Json.mkObj [
  ("option", Json.str r.option), ("taxableIncome", toJson (euros r.taxable)), ("standardRateBand", toJson (euros r.band)),
  ("grossTaxCents", toJson r.grossTax), ("creditsCents", toJson r.credits), ("homeCarerCreditCents", toJson r.homeCarer),
  ("incomeTaxCents", toJson r.tax)]

def outOf (args : List String) (c : Canon) : Out :=
  let h := mkHH c
  let el : Election := if args.contains "--joint" then .jointOnly else if args.contains "--single" then .singleOnly
    else .best
  let rd : Reading := { prsiFlat41 := args.contains "--oecd" || args.contains "--prsi41",
                        wfpExact := args.contains "--oecd" || args.contains "--wfp-exact",
                        wfpNoMinimum := args.contains "--wfp-nomin",
                        prsiFirstRate := args.contains "--prsi-first-rate" }
  let y := ypFor c.year
  let r := hhCalc h el rd y
  let uns := (if c.charitable > 0 then ["charitable: no donor relief (TCA s. 848A relief goes to the charity)"] else [])
    ++ ["medical card (USC s. 531AN(3)) and rent tax credit (s. 473B) not in the household contract",
        "PRSI on unearned income read as Class S with the EUR 650 minimum (SWCA s. 20-21)",
        "WFP: 38 hours a fortnight assumed when there are earnings; assessed on this year's income (in law: at claim, fixed 52 weeks)",
        "DIRT refund to over-65s (s. 267) not modelled"]
    ++ (if c.year < 2022 || c.year > 2025 then [s!"tax year {c.year} not modelled: computed with the {y.year} parameters"] else [])
  Out.make c "IE" "EUR" (euros r.it) (surtaxes := [("USC", euros r.usc), ("capitalGainsTax", euros r.cgt)])
    (employeeSocial := euros (r.prsiA + r.prsiS)) (benefits := euros (r.cb + r.wfp))
    (detail := [Out.dStr "taxYear" (toString y.year), Out.dStr "assessment" r.assessment,
      Out.d "taxableIncome" (euros (sumL (r.itParts.map (·.taxable)))),
      Out.d "taxBeforeCredits" (euros (sumL (r.itParts.map (·.grossTax)))),
      Out.d "incomeTaxCents" r.it, Out.d "dirtCents" r.dirt, Out.d "uscCents" r.usc,
      ("uscEachCents", toJson r.uscEach),
      Out.d "prsiClassA1Cents" r.prsiA, Out.d "prsiClassSCents" r.prsiS, Out.d "cgtCents" r.cgt,
      Out.d "childBenefitCents" r.cb, Out.d "wfpWeeklyCents" r.wfpWeekly, Out.d "wfpCents" r.wfp,
      Out.d "familyIncomeWeeklyCents" r.familyIncomeWeekly,
      Out.d "jointAssessmentTaxCents" r.jointTax, Out.d "singleAssessmentTaxCents" r.singleTax,
      ("returns", Json.arr (r.itParts.map itJson).toArray)])
    (unsupported := uns)

def country : Country :=
  { code := "IE", name := "Ireland", currency := "EUR", year := "2022-2025", compute := outOf [],
    computeWith := outOf }

end IeTax
