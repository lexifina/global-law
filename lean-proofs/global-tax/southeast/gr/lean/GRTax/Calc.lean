import GRTax.Params

/-!
# Greece: one taxpayer's tax, and the household

Unit of assessment (ΚΦΕ art. 67 par. 4(α)): spouses file one joint return, but "Ο φόρος ... που αναλογούν στα
εισοδήματα εκάστου συζύγου βεβαιώνεται χωριστά": each spouse is taxed alone on the art. 15 scale, with the art. 16
reduction for the dependent children of the household (art. 11 par. 1(β); both spouses count them, as the OECD's
BTC for M100_67 shows: 853.75 + 1,020.82). A separate return (art. 67 par. 4(β)) changes nothing in this model
(par. 4(γ): art. 11 applies to each return), so `kernel Unit` is `separate` for spouses.
-/

namespace GRTax
open TaxKernel

structure Person where
  wages : Int := 0          -- cents, gross
  pension : Int := 0
  selfEmp : Int := 0        -- business profit (cents)
  age : Nat := 40
  kids : Nat := 0           -- dependent children for art. 16 (and the 2026 rates)
  interest : Int := 0
  dividends : Int := 0
  rent : Int := 0           -- gross rent
  gains : Int := 0
  substantial : Bool := false   -- art. 42: holding ≥ 0.5 %
  art5G : Bool := false         -- art. 5Γ: 50 % of wage income exempt (relocated worker, 7 years)
  cardSpent : Option Int := none -- art. 15 par. 6 card spending (cents); none = requirement met
  presumedMin : Int := 0        -- art. 28Α minimum (cents; 0 = not applied)
  publicSector : Bool := false  -- wages from the public sector (art. 43Α in 2022, art. 72 par. 74)
  deriving Repr, Inhabited

structure Calc where
  efka : Int := 0
  wageTaxable : Int := 0     -- wages − EFKA (− the art. 5Γ half)
  exempt5G : Int := 0
  business : Int := 0        -- profit after the art. 28Α minimum
  scaleBase : Int := 0       -- art. 15 base: wages + pensions + business
  taxScale : Int := 0        -- art. 15 tax (cents)
  wageShareTax : Int := 0    -- the part of it on wages and pensions (art. 29 par. 1)
  creditFull : Int := 0      -- art. 16 amount after the taper
  creditUsed : Int := 0
  mainTax : Int := 0
  cardPenalty : Int := 0
  rentTax : Int := 0
  divTax : Int := 0
  intTax : Int := 0
  gainTax : Int := 0
  solidarity : Int := 0      -- art. 43Α special solidarity contribution (2022: pensions, public wages)
  deriving Repr, Inhabited

def Calc.incomeTax (k : Calc) : Int := k.mainTax + k.rentTax + k.divTax + k.intTax + k.gainTax

/-- Rent after the 5 % deduction of art. 39. -/
def rentNet (rent : Int) : Int := rent - divR .down (rent * rentDeduction) BP

/-- Business profit after ΚΦΕ art. 28Α: not below the presumed minimum (capped at 50,000 €). -/
def businessAfterMin (profit presumed : Int) : Int :=
  if presumed > 0 then max profit (min presumedCap presumed) else profit

/-- ΚΦΕ art. 29 par. 1 (2025 wording, codif. fn 223): profits "φορολογούνται με την κλίμακα της παραγράφου 1 του
άρθρου 15, αφού προστεθούν σε τυχόν εισοδήματα από μισθούς και συντάξεις. Για τα κέρδη από επιχειρηματική
δραστηριότητα δεν εφαρμόζονται οι μειώσεις του άρθρου 16": the reduction is capped by the scale tax in proportion
to the wage and pension income (the εκκαθαριστικό's pro-rata split). -/
def wageShare (tax base wp : Int) : Int := if base ≤ 0 then 0 else divR .down (tax * wp) base

def personCalc (year : Nat) (p : Person) (oecd : Bool := false) (es : Bool := false) (em : Bool := false) : Calc :=
  let e := efkaAmount year p.wages oecd es em
  let wt0 := pos (p.wages - e)
  let ex := if p.art5G then divR .down wt0 2 else 0
  let wt := wt0 - ex
  -- art. 28Α applies from the tax year 2023 (ν. 5073/2023 art. 15)
  let bus := businessAfterMin p.selfEmp (if year ≥ 2023 then p.presumedMin else 0)
  let base := pos (wt + p.pension + bus)
  let sch := scaleFor year p.kids p.age
  let t := sch.tax Rule.unitHalfUp base
  let wp := wt + p.pension
  let ws := wageShare t base wp
  let cr := if wp > 0 then (creditTaper year p.kids).amount wp else 0
  let used := min cr ws
  let real := wt0 + p.pension + pos p.selfEmp
  let pen := match p.cardSpent with
    | none => 0
    | some s => divR .halfUp (cardPenaltyRate * pos (min cardCap (divR .down (real * cardShare) BP) - s)) BP
  { efka := e, wageTaxable := wt, exempt5G := ex, business := bus, scaleBase := base, taxScale := t,
    wageShareTax := ws, creditFull := cr, creditUsed := used, mainTax := t - used, cardPenalty := pen,
    rentTax := (rentScale year).tax Rule.unitHalfUp (rentNet p.rent),
    divTax := divR .halfUp (p.dividends * dividendRate) BP,
    intTax := divR .halfUp (p.interest * interestRate) BP,
    gainTax := if p.substantial then divR .halfUp (p.gains * gainRate) BP else 0,
    solidarity := solidarity year ((if p.publicSector then wt else 0) + p.pension) }

/-- Income counted for the child benefit: income before tax after contributions (art. 214 par. 3). -/
def benefitIncome (p : Person) (k : Calc) : Int :=
  k.scaleBase + k.exempt5G + p.interest + p.dividends + rentNet p.rent + p.gains

/-- The household's child benefit: `parents` is 1 for a lone parent (or an unmarried parent claiming alone),
2 for spouses / partners. -/
def childBenefit (parents : Nat) (kids : Nat) (famIncome : Int) : Int :=
  if kids = 0 then 0 else
  let q := scaleQuarters parents kids
  childBenefitAnnual (divR .down (famIncome * 4) q) kids

end GRTax
