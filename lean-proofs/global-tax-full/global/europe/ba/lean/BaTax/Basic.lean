import BaTax.Params

/-!
# Federation of BiH 2025: income tax on employment, rent; employee contributions

* Employment income (član 10) is the gross pay; the employee's compulsory contributions are deducted (član 11).
* The personal deduction (član 24): 3 600 KM, plus 0,5 × 3 600 for a dependent spouse (spouse's income not above
  3 600: član 24 (3)), and 0,5 / 0,7 / 0,9 × 3 600 for the first / second / third and further child. When both parents
  support the children the child deductions are shared equally (član 24 (4) "ravnomjerno se raspoređuje").
* Dividends are not income (član 5-6: "prihodi na osnovu učešća u raspodjeli dobiti ... (dividende ili udjeli)"), and
  interest on bank savings and accounts is not taxed (član 12 list, point 12): both 0.
* Rent of immovable property: 10 % of 70 % of the rent (član 21 (2), withholding final under član 31).
-/

namespace BaTax
open TaxKernel

def contrib (w : Int) : Int :=
  if w ≤ 0 then 0 else
  divR .halfUp (w * pio) BP + divR .halfUp (w * health) BP + divR .halfUp (w * unemployment) BP

/-- Child deduction amounts by rank (thousandths of the basic deduction), for `n` children. -/
def childDed (n : Nat) : Int :=
  divR .halfUp (basicDeduction * perChildByRank childFactors n) 1000

def taxOf (base : Int) : Int := divR .halfUp (schedule.ticks (pos base)) BP

structure Person where
  wage : Int
  contrib : Int
  ded : Int
  taxable : Int
  tax : Int

def person (w se ded : Int) : Person :=
  let k := contrib w
  let taxable := pos (w - k + se - ded)
  { wage := w, contrib := k, ded, taxable, tax := taxOf taxable }

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 18
  let cd := childDed kids
  let as := c.adults
  let incomes := as.map fun a => pos (a.wages - contrib a.wages) + a.selfEmployment
  let earners := (incomes.filter (· > 0)).length
  -- child deductions: shared equally unless the parents agree otherwise (član 24 (4) "osim ako se ne dogovore
  -- drugačije"): the parents' choice, made cheapest-first among equal sharing, all to the first, all to the second
  let dedFor := fun (share : Nat) (i : Nat) =>
    let own := incomes.getD i 0
    let other := incomes.getD (1 - i) 0
    let spouse := if c.married && as.length == 2 && other ≤ basicDeduction && own > 0 then
      divR .halfUp (basicDeduction * spouseFactor) 1000 else 0
    let child := if own ≤ 0 && earners > 0 then 0 else
      if earners == 2 then
        (if share == 0 then (if i == 0 then half1 cd else half2 cd) else if share == i + 1 then cd else 0)
      else cd
    basicDeduction + spouse + child
  let options := [0, 1, 2].map fun s => (as.zipIdx).map fun (a, i) => person a.wages a.selfEmployment (dedFor s i)
  let ps := options.foldl (fun best o => if sumInts (o.map (·.tax)) < sumInts (best.map (·.tax)) then o else best)
    (options.headD [])
  let rentT := divR .halfUp (pos c.rentalIncome * (BP - rentCostRate) * rate) (BP * BP)
  let empT := sumInts (ps.map (·.tax))
  let region := (c.str? "region").getD "federation"
  let unsup :=
    (if region != "federation" && region != "fbih" then ["region: only the Federation of BiH is modelled; Republika Srpska and Brčko District laws not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as net income (član 12-16); the self-employed's contributions not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: treatment of pensions not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: not modelled"] else []) ++
    (if c.interest != 0 then ["interest: taken as interest on bank savings/accounts, not taxed (član 12 point 12); interest on loans (član 22, 10 %) not modelled"] else []) ++
    ["contributions: the minimum base (Zakon o doprinosima član 7, the lowest wage) is not applied to low pay"]
  Out.make c "BA" "BAM" (empT + rentT) (employeeSocial := sumInts (ps.map (·.contrib)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "personalDeductions" (sumInts (ps.map (·.ded))),
                Out.d "rentTax" rentT, Out.d "dividendsNotIncome" (pos c.dividends),
                Out.dStr "note" "Federation of BiH (entity default): 10 % on pay less 31 % employee contributions and the personal deduction 3 600 KM + family factors"])
    (unsupported := unsup)

def country : Country :=
  { code := "BA", name := "Bosnia and Herzegovina: Federation of BiH (porez na dohodak, doprinosi)", currency := "BAM",
    year := "2025", compute := out }

end BaTax
