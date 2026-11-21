import IlTax.Params

/-!
# Israel 2025: income tax with credit points, surtax, national and health insurance (employee)

Unit: each spouse is computed separately ("חישוב נפרד", ITO s. 66(ג); separate computation is the default when both
have personal-exertion income, and either may ask for it, (1א)). Per person:
* personal-exertion income (wages, self-employment; pensions on the same scale, flagged) on the s. 121 scale;
* less credit points × 2.904 NIS (non-refundable): 2 (s. 34) + ¼ (s. 36) + ½ for a woman (s. 36א) + children
  (s. 66(ג)(4) for the mother, (5) for the father; a single adult with children gets the mother's schedule, s. 40(ב)(1));
* capital income: dividends 25 % (s. 125ב(1)); interest and capital gains at 25 % (sections not read, flagged);
* surtax s. 121ב: 3 % of taxable income above 721.560, and 2 % of capital income above it.
The canonical household has no sex: optional fields `adult1Sex` / `adult2Sex` ("F"/"M"); defaults: a single adult
"M", a couple "M" then "F" (detail.sexes).
-/

namespace IlTax
open TaxKernel

def quartersValue (q : Int) : Int := divR .halfUp (q * creditPoint) 4

def childQuarters (female single : Bool) (ages : List Nat) : Int :=
  sumInts (ages.map fun a => if female || single then motherChildQuarters a else fatherChildQuarters a)

structure Person where
  exertion : Int
  capital : Int
  taxBefore : Int
  quarters : Int
  credit : Int
  capitalTax : Int
  surtax : Int
  tax : Int
  ni : Int
  health : Int
  deriving Repr

/-- Employee national + health insurance on a year's wage paid in 12 equal months (ticks summed, rounded at the end). -/
def employeeContrib (wage : Int) : Int × Int :=
  if wage ≤ 0 then (0, 0) else
  let ms : List Nat := [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
  let m := fun (i : Nat) => min (wage * ((i : Int) + 1) / 12 - wage * (i : Int) / 12) niCeilingMonth
  let ni := sumInts (ms.map fun i => let x := m i; min x reducedBandMonth * niLowcBp + pos (x - reducedBandMonth) * niHighcBp)
  let he := sumInts (ms.map fun i => let x := m i
    min x reducedBandMonth * healthLowcBp + pos (x - reducedBandMonth) * (if i == 0 then healthHighJancBp else healthHighcBp))
  (divR .halfUp ni (BP * 100), divR .halfUp he (BP * 100))

def person (female single : Bool) (kids : List Nat) (wage se pension interest dividends gains : Int) : Person :=
  let exertion := pos wage + pos se + pos pension
  let capital := pos interest + pos dividends + pos gains
  let t0 := exertionScale.tax Rule.unitHalfUp exertion
  let q := residentQuarters + (if female then womanQuarters else 0) + childQuarters female single kids
  let cr := quartersValue q
  let incomeTax := pos (t0 - cr)
  let capTax := divR .halfUp (capital * dividendRate) BP
  let sur := divR .halfUp (pos (exertion + capital - surtaxThreshold) * surtaxRate) BP +
    divR .halfUp (pos (capital - surtaxThreshold) * surtaxCapitalRate) BP
  let (ni, he) := employeeContrib wage
  { exertion, capital, taxBefore := t0, quarters := q, credit := min cr t0, capitalTax := capTax, surtax := sur,
    tax := incomeTax + capTax, ni, health := he }

def sexOf (c : Canon) (k : Nat) (n : Nat) : Bool :=
  let key := if k == 0 then "adult1Sex" else "adult2Sex"
  match c.str? key with
  | some s => s == "F" || s == "f"
  | none => n == 2 && k == 1

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let ages := c.children.map (·.age)
  let rows := (((c.adults.zip (sh c.interest)).zip (sh c.dividends)).zip (sh c.capitalGains))
  let ps := rows.zipIdx.map fun ((((a, i), d), g), k) =>
    person (sexOf c k n) (n == 1) ages a.wages a.selfEmployment a.pension i d g
  let unsup :=
    ["child allowance: residents' children under 18 (NI Law s. 65-68), the household's children counted in age order; the study grant (מענק לימודים) and other means-tested additions not modelled"] ++
    (if c.interest != 0 || c.capitalGains != 0 then ["interest/capitalGains: taxed at 25 % (s. 125ב rate used; s. 91 and 125ג not read)"] else []) ++
    (if c.rentalIncome != 0 then ["rentalIncome: residential rent tracks (exemption / 10 %) not modelled; not taxed"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: s. 9א exemption not modelled; taxed on the exertion scale; NI/health on pensions not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as net personal-exertion income; NI/health of the self-employed not modelled"] else []) ++
    (if c.pensionContributions != 0 || c.charitable != 0 then ["pensionContributions/charitable: s. 45א and 46 credits not modelled"] else []) ++
    []
  let kidsU18 := (c.children.filter (·.age < 18)).length
  let allowance := 12 * sumInts ((List.range kidsU18).map childAllowance)
  Out.make c "IL" "ILS" (sumInts (ps.map (·.tax))) (surtaxes := [("s121b", sumInts (ps.map (·.surtax)))])
    (benefits := allowance)
    (employeeSocial := sumInts (ps.map fun p => p.ni + p.health))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map fun p => p.exertion + p.capital)),
                Out.d "taxBeforeCredits" (sumInts (ps.map (·.taxBefore))),
                Out.d "creditPointsQuarters" (sumInts (ps.map (·.quarters))),
                Out.d "creditsUsed" (sumInts (ps.map (·.credit))),
                Out.d "capitalTax" (sumInts (ps.map (·.capitalTax))),
                Out.d "nationalInsurance" (sumInts (ps.map (·.ni))), Out.d "healthInsurance" (sumInts (ps.map (·.health))),
                Out.dStr "sexes" (String.intercalate "," ((List.range n).map fun k => if sexOf c k n then "F" else "M"))])
    (unsupported := unsup)

/- NI ceiling: on 1,000,000 a year (83,333 a month) the employee pays on 50,695 a month only. -/
#guard (employeeContrib 1000000).1 = (employeeContrib (12 * niCeilingMonth)).1
/- Two children: (169 + 214) x 12 = 4,596 a year. -/
#guard 12 * sumInts ((List.range 2).map childAllowance) = 4596

def country : Country :=
  { code := "IL", name := "Israel (income tax, national and health insurance)", currency := "ILS", year := "2025",
    compute := out }

end IlTax
