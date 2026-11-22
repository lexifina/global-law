import SmTax.Params

/-!
# San Marino 2025: IGR on employment and pension income (Titolo II), 2025 wording

Per person (individual taxation): employment income less the employee's compulsory contributions (household input
`sm_employeeContributions`, whole euros, default 0: the contribution rates are in the social-security laws, which the
Global law record does not hold: unsupported) and the 7 % abatement (max 2 800 €); pensions less the art. 26
abatement; the C1 c. 3 deduction (9 000 € tapered from 9 000 to 40 000 €, ratio truncated to 4 decimals); the art. 14
spending deduction (input `sm_smacSpending`, default 0); the tariff; then the art. 16 credits, not below 0.
Children are minors (art. 16 c. 2 a); their 250 € credits go to one parent or 50/50 (art. 16 c. 5): the cheaper.
A spouse is dependent when he or she has no income (art. 16 c. 3 limit = the social pension, not cited: reading).
-/

namespace SmTax
open TaxKernel

def cents (x : Int) : Int := x * 100

/-- C1 c. 3 deduction for art. 24-26 income `y` (cents). -/
def c3Deduction (y : Int) : Int :=
  if y ≤ 0 then 0 else
  let ratio := (c3TopC - y) * 10000 / c3SpanC     -- four decimals, truncated
  if ratio ≥ 10000 then c3MaxC else if ratio ≤ 0 then 0 else c3MaxC * ratio / 10000

structure Person where
  empInc : Int
  taxable : Int
  gross : Int
  credits : Int
  tax : Int

def person (wageE pensionE contribE spendE : Int) (credits : Int) : Person :=
  let w := cents (pos wageE)
  let emp := if w ≤ 0 then 0 else pos (w - cents contribE - min empAbatementCapC (divR .halfUp (w * empAbatementRate) BP))
  let p := cents (pos pensionE)
  let pen := pos (p - divR .halfUp (pensionAbatement.ticks p) BP)
  let y := emp + pen
  let d3 := c3Deduction y
  let spend := min (cents (pos spendE)) (pos (spendingCapC - d3))
  let taxable := pos (y - d3 - spend)
  let gross := divR .halfUp (tariff.ticks taxable) BP
  let low := if y > 0 && y ≤ lowIncomeLimitC then lowIncomeCreditC else 0
  let cr := credits + low
  { empInc := y, taxable, gross, credits := cr, tax := pos (gross - cr) }

def out (c : Canon) : Out :=
  let as := c.adults
  let n := as.length
  let kids : Int := c.childrenUnder 18
  let incomes := as.map fun a => a.wages + a.pension + a.selfEmployment
  let spouseDep := fun (i : Nat) => c.married && n == 2 && incomes.getD (1 - i) 0 ≤ 0 && incomes.getD i 0 > 0
  let dependants := fun (i : Nat) => kids + (if spouseDep i then 1 else 0)
  let up := fun (i : Nat) (x : Int) => if dependants i > 2 then x + divR .halfUp (x * familyUplift) BP else x
  let contrib := (c.int? "sm_employeeContributions").getD 0
  let spend := (c.int? "sm_smacSpending").getD 0
  -- child credits: share s = 0 equal halves, 1 all to the first adult, 2 all to the second
  let credFor := fun (s : Nat) (i : Nat) =>
    let kidC := if n == 2 then (if s == 0 then kids * childCreditC / 2 else if s == i + 1 then kids * childCreditC else 0)
      else kids * childCreditC
    up i (kidC + (if spouseDep i then spouseCreditC else 0))
  let options := [0, 1, 2].map fun s => (as.zipIdx).map fun (a, i) =>
    person a.wages a.pension (if i == 0 then contrib else 0) (if i == 0 then spend else 0) (credFor s i)
  let ps := options.foldl (fun b o => if sumInts (o.map (·.tax)) < sumInts (b.map (·.tax)) then o else b) (options.headD [])
  let taxC := sumInts (ps.map (·.tax))
  let unsup :=
    (if (c.int? "sm_employeeContributions").isNone && as.any (·.wages > 0) then
      ["employee social-security contributions (ISS/FONDISS): the rates are not in the Global law record; not computed and not deducted (input sm_employeeContributions)"] else []) ++
    (if (c.int? "sm_smacSpending").isNone then ["assumption: no in-territory electronic (SMaC) spending; the art. 14 c. 1 a) deduction is 0 (input sm_smacSpending)"] else []) ++
    (if c.interest != 0 || c.dividends != 0 then ["interest/dividends: final withholding (arts. 102-104, 2025 wording) not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: separate taxation art. 13 c) not modelled"] else []) ++
    (if c.rentalIncome != 0 then ["rentalIncome: not modelled"] else []) ++
    (if as.any (·.selfEmployment != 0) then ["selfEmployment: separate taxation (art. 13) not modelled"] else [])
  Out.make c "SM" "EUR" (divR .halfUp taxC 100)
    (detail := [Out.d "taxableIncome" (divR .halfUp (sumInts (ps.map (·.taxable))) 100),
                Out.d "taxBeforeCredits" (divR .halfUp (sumInts (ps.map (·.gross))) 100),
                Out.d "credits" (divR .halfUp (sumInts (ps.map (·.credits))) 100),
                Out.dStr "note" "IGR 2025 wording (art. 148 c. 8): Allegato C tariff 9-35 %, 7 % abatement (max 2 800), C1 c. 3 deduction 9 000 tapered to 40 000, art. 16 credits"])
    (unsupported := unsup)

def country : Country :=
  { code := "SM", name := "San Marino (imposta generale sui redditi, 2025 wording)", currency := "EUR", year := "2025",
    compute := out }

end SmTax
