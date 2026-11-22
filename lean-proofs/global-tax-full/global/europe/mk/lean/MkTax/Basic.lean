import MkTax.Params

/-!
# North Macedonia 2025: personal income tax (flat 10 %), contributions

Base (член 9): gross income less compulsory contributions, less the tax reduction (for pay and pensions only, член 10
(1)), less statutory costs. All contributions in North Macedonia are calculated on the gross wage and withheld from it
(Закон за придонеси член 25): the employee bears 28 %. Minimum base (50 % of the average wage, член 15) and maximum
monthly base (16 average wages, член 16) need the average wage published in January 2025: not reached, not applied.
Capital income and capital gains at 10 % (член 11 (1)); deposit interest untaxed (член 12 (1) 37), член 116).
-/

namespace MkTax
open TaxKernel

def contrib (w : Int) : Int :=
  if w ≤ 0 then 0 else
  divR .halfUp (w * pension) BP + divR .halfUp (w * health) BP + divR .halfUp (w * healthExtra) BP +
    divR .halfUp (w * unemployment) BP

def taxOf (x : Int) : Int := divR .halfUp (schedule.ticks (pos x)) BP

def wageBase (w : Int) : Int := if w ≤ 0 then 0 else pos (w - contrib w - taxReduction)

def out (c : Canon) : Out :=
  let ws := c.adults.map (·.wages)
  let wageT := sumInts (ws.map fun w => taxOf (wageBase w))
  let selfT := sumInts (c.adults.map fun a => taxOf a.selfEmployment)
  let capT := taxOf (pos c.dividends + pos c.capitalGains)
  let rentT := taxOf (pos c.rentalIncome - divR .halfUp (pos c.rentalIncome * rentCosts) BP)
  let unsup :=
    ["tax reduction (член 10): the 2025 amount published by the Minister of Finance was not reached; the act's printed 96 000 MKD is used"] ++
    ["contributions: the 2025 minimum and maximum bases (член 15-16, average wage of January 2025) were not reached; not applied"] ++
    (if c.interest != 0 then ["interest: taken as deposit interest, not taxed (член 12 (1) 37), член 116); other interest (10 %) not distinguished"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: 10 % on the amount given as taxable income; contributions of the self-employed not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: the tax reduction also applies to pensions (член 10 (1)); pension income not modelled"] else [])
  Out.make c "MK" "MKD" (wageT + selfT + capT + rentT) (employeeSocial := sumInts (ws.map contrib))
    (detail := [Out.d "wageTax" wageT, Out.d "capitalIncomeTax" capT, Out.d "rentTax" rentT,
                Out.d "taxableIncome" (sumInts (ws.map wageBase)), Out.d "taxReduction" taxReduction,
                Out.dStr "note" "flat 10 % (член 11, 274/2022) on gross pay less 28 % contributions and the tax reduction"])
    (unsupported := unsup)

def country : Country :=
  { code := "MK", name := "North Macedonia (данок на личен доход, придонеси)", currency := "MKD", year := "2025",
    compute := out }

end MkTax
