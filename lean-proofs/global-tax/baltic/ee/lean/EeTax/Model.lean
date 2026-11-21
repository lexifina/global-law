import TaxKernel
import EeTax.Params

/-!
# Estonia 2025: one resident's annual income tax (TuMS), in cents

Composition from kernel parts: `Taper` (§ 23 basic exemption withdrawn between 14 400 and 25 200 euro of "tulu"),
`Schedule.flat` (§ 4(1) 22 %), `Contribution` (unemployment insurance and II pillar, deductible under § 28^1),
`cappedDeduction`-style caps (§ 28^2, § 28(2)), `Rounding` (half-up to the cent).
-/

namespace EeTax
open TaxKernel

/-- 22 % of a base in cents, half-up to the cent. -/
def tax22 (base : Int) : Int := Rule.unitHalfUp.ofTicks (sched.ticks base)

/-- The § 4(1) tax of a year (20 % to 2024, 22 % from 2025), half-up to the cent. -/
def taxAt (y : Nat) (base : Int) : Int := Rule.unitHalfUp.ofTicks ((Schedule.flat (rateFor y)).ticks base)

/-- `x × num / den` rounded half-up (cents). -/
def mulDiv (x num den : Int) : Int := divR .halfUp (x * num) den

/-- bp share of x, half-up to the cent. -/
def pct (r x : Int) : Int := mulDiv x r BP

/-- Employee unemployment-insurance premium on wages (TKindlS § 40(1) p1, regulation § 1(1)). -/
def uiContribution : Contribution := { name := "töötuskindlustusmakse", sched := Schedule.flat uiEmployee, round := Rule.unitHalfUp }

/-- One person's inputs (cents). `rent` is residential rent received; `dividendsEE` are dividends from Estonian
companies that paid the distribution CIT (§ 50), not taxed again (§ 12(2)) but counted in § 23(3) "tulu". -/
structure PIn where
  pensionAge : Bool := false
  boardMember : Bool := false   -- pay is a management-board fee: no unemployment insurance (TKindlS § 3, § 40)
  wages : Int := 0
  business : Int := 0           -- FIE profit after business expenses (§ 14, § 32), before social tax
  pension : Int := 0            -- state pension (§ 19(2))
  interest : Int := 0
  gains : Int := 0
  rent : Int := 0
  dividendsEE : Int := 0
  gifts : Int := 0              -- § 27 (and § 26 training) claims
  pillar3 : Int := 0            -- § 28 III-pillar contributions
  p2Rate : Int := pillar2Default
  year2026 : Bool := false      -- versioned law: the flat 8 400 euro exemption of 2026
  year : Nat := 2025            -- tax year (2022-2025 modelled; round 2)
  extraEx : Int := 0            -- § 23^1 / § 23^4 extra exemptions (2022-2023), set by the household
  deriving Repr, Inhabited

structure POut where
  ui : Int
  p2 : Int
  fieSocial : Int
  fieBase : Int
  bizTaxable : Int
  incomeTaxable : Int   -- taxable income before deductions (no Estonian dividends)
  tulu : Int            -- § 23(2)-(3) income for the taper
  exemption : Int
  dedGifts : Int
  dedP3 : Int
  taxable : Int
  tax : Int
  deriving Repr, Inhabited

/-- FIE (sole trader) social tax and the business income left for income tax: TuMS § 14(5^3)-(5^5), SMS § 2(1) p5
(ceiling 10 × 12 minimum wages), § 2(5) (floor 12 × kuumäär, not for a state-pension recipient, p2). Returns
(social tax, SMS base, business income for income tax). -/
def fie (pensionAge : Bool) (profit : Int) : Int × Int × Int :=
  if profit ≤ 0 then (0, 0, profit) else
  let base0 := profit * fieDivNum / fieDivDen
  let floorB := if pensionAge then 0 else 12 * kuumaar
  let ceilB := 10 * 12 * minWage2025
  let base := min ceilB (max floorB base0)
  let st := pct socialTax base
  -- § 14(5^4): social tax above the business income is carried forward (§ 35), not set against other income
  let biz := if base = base0 then base0 else pos (profit - st)
  (st, base, biz)

/-- The FIE's II-pillar base: the SMS § 2(1) p5 income itself (KoPS § 11(2^1)), capped, not the § 2(5) minimum. -/
def fieP2Base (profit : Int) : Int :=
  if profit ≤ 0 then 0 else min (10 * 12 * minWage2025) (profit * fieDivNum / fieDivDen)

/-- The annual computation for one resident (TuMS §§ 12, 23, 23^5, 26-28^2, 4(1)). -/
def person (p : PIn) : POut :=
  let ui := if p.pensionAge || p.boardMember then 0 else uiContribution.amount p.wages
  let (fst, fbase, biz) := fie p.pensionAge p.business
  let p2rate := if p.pensionAge then 0 else p.p2Rate
  let p2 := pct p2rate p.wages + pct p2rate (fieP2Base p.business)
  let rent80 := p.rent - pct rentDeductionPct p.rent
  let incT := p.wages + biz + p.pension + p.interest + p.gains + rent80
  let tulu := incT + p.dividendsEE
  let ex := if p.pensionAge then pensionAgeExemption
    else if p.year2026 then exemption2026 else (exemptionFor p.year).amount tulu
  let dG := min (pos p.gifts) (min dedCap (pct dedPct (pos incT)))
  let dP := min (pos p.pillar3) (min p3Cap (pct p3Pct (pos incT)))
  let taxable := pos (incT - ui - p2 - dG - dP - ex - pos p.extraEx)
  { ui, p2, fieSocial := fst, fieBase := fbase, bizTaxable := biz, incomeTaxable := incT, tulu,
    -- the exemption actually deducted (never more than the income it is set against; round 2: a non-earning
    -- spouse's unused § 23 amount was reported as an exemption)
    exemption := min (ex + pos p.extraEx) (pos (incT - ui - p2 - dG - dP)), dedGifts := dG, dedP3 := dP, taxable,
    tax := taxAt p.year taxable }

/-- Employee-side compulsory payments of the person (unemployment insurance, II pillar, FIE social tax). -/
def POut.social (o : POut) : Int := o.ui + o.p2 + o.fieSocial

/-- Distribution CIT paid by the company on a net dividend (§ 4(1^1), § 50(1)): D × 22/78. -/
def citOnDividend (d : Int) : Int := mulDiv d citNum citDen

end EeTax
