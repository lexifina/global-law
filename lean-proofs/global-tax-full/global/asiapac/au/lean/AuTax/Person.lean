import AuTax.Params

/-!
# One person: taxable income, basic income tax, offsets, levies (ITAA 1997 s. 4-10)

ITAA 1997 s. 4-10(3): "Work out your income tax for the financial year using this formula:
(Taxable income x Rate) - Tax offsets", and s. 4-15(1): "taxable income = Assessable income - Deductions".
The Medicare levy is a separate tax imposed by the Medicare Levy Act 1986 and assessed with income tax (MLA s. 5;
ITAA 1936 Part VIIB); offsets reduce income tax only, except refundable offsets (ITAA 1997 s. 67-25), which are
refunded once all tax is paid.
-/

namespace AuTax

/-- One taxpayer's year, whole dollars. Investment amounts are this person's share. -/
structure Person where
  age : Nat := 40
  wages : Int := 0
  selfEmployment : Int := 0
  pension : Int := 0
  interest : Int := 0
  /-- Cash dividends from Australian listed companies, assumed fully franked at the 30 % corporate rate. -/
  dividends : Int := 0
  /-- Gains on assets held at least 12 months (discount capital gains, ITAA 1997 s. 115-25). -/
  capitalGains : Int := 0
  /-- Net rent (negative: a rental loss, deductible against other income). -/
  rental : Int := 0
  /-- Gifts to deductible gift recipients (ITAA 1997 s. 30-15). -/
  gifts : Int := 0
  /-- Personal contributions to a complying super fund for which a deduction is claimed (ITAA 1997 s. 290-150),
  or salary-sacrificed (employer) contributions: either way concessional and reportable. -/
  superContrib : Int := 0
  /-- `true`: `superContrib` is salary-sacrificed out of `wages` (the package before the sacrifice). -/
  sacrifice : Bool := false
  privateCover : Bool := true
  helpDebt : Bool := false
  /-- Corporate tax rate at which the dividends are franked (bp): 3000 (listed companies) or 2500 (a base rate
  entity, ITRA s. 23(2); ITAA 1997 s. 202-60 corporate tax rate for imputation purposes). -/
  frankingRate : Int := 3000
  deriving Repr, Inhabited

/-- Franking credit on a fully franked dividend, in cents: d x t / (1 - t) for the corporate tax rate t
(ITAA 1997 s. 202-60 maximum franking credit; s. 207-20(1) gross-up, (2) tax offset of the same amount). -/
def frankingCreditC (divDollars : Int) (rateBp : Int := 3000) : Int := (divDollars * 100 * rateBp) / (10000 - rateBp)

/-- Net capital gain: 50 % discount for an individual (s. 115-100(a)); a net capital loss is carried forward
(s. 102-10), so it is nil for the year. In cents. -/
def netCapitalGainC (g : Int) : Int := pos (aud g) / 2

/-- Deductible super contributions (s. 290-150): capped here at the concessional cap (amounts above it are excess
concessional contributions, Div 291, not modelled). Salary sacrifice is not a deduction (already out of wages). -/
def superDeductionC (p : Params) (x : Person) : Int :=
  if x.sacrifice then 0 else aud (min (pos x.superContrib) p.concessionalCap)

def concessionalC (p : Params) (x : Person) : Int := aud (min (pos x.superContrib) p.concessionalCap)

/-- Salary sacrificed to super: employer contributions, not the employee's assessable income (ITAA 1997
s. 6-5 needs a receipt; contributions are not; s. 295-160 taxes them in the fund). `wages` is the package
before the sacrifice. -/
def sacrificedC (p : Params) (x : Person) : Int := if x.sacrifice then concessionalC p x else 0

/-- Assessable income in cents (s. 6-5 ordinary income; s. 207-20 gross-up; s. 102-5 net capital gain). -/
def assessableC (p : Params) (x : Person) : Int :=
  aud (x.wages + x.selfEmployment + x.pension + x.interest + x.dividends + x.rental) - sacrificedC p x +
    frankingCreditC (pos x.dividends) x.frankingRate + netCapitalGainC x.capitalGains

/-- Taxable income (s. 4-15), whole dollars (in cents). Gifts and personal super deductions cannot create a loss
(s. 26-55); a rental loss reduces other income (no quarantining in Australia). A tax loss is carried forward,
so taxable income is at least nil. -/
def taxableIncomeC (p : Params) (x : Person) : Int :=
  let a := assessableC p x
  let ded := min (aud (pos x.gifts) + superDeductionC p x) (pos a)
  wholeDollars (pos (a - ded))

/-- Total net investment loss (ITAA 1997 s. 995-1): here the rental loss. -/
def netInvestmentLossC (x : Person) : Int := aud (pos (-x.rental))

/-- Reportable super contributions (s. 16-182): deducted personal contributions plus salary-sacrifice amounts. -/
def reportableSuperC (p : Params) (x : Person) : Int := concessionalC p x

/-- Income for surcharge purposes (s. 995-1), and the FTB adjusted taxable income (FA Act Sch 3 cl 2) and HELP
repayment income (HESA s. 154-5), which for this household are the same sum: taxable income + reportable super
contributions + total net investment loss (no fringe benefits, foreign income or tax-free pensions here). -/
def broadIncomeC (p : Params) (x : Person) : Int :=
  taxableIncomeC p x + reportableSuperC p x + netInvestmentLossC x

/-- ITRA Sch 7 Pt I cl 1 as a kernel `Schedule` in whole dollars (a zero band below the tax-free threshold). -/
def auSchedule (p : Params) : TaxKernel.Schedule := TaxKernel.Schedule.ofList ((0, 0) :: p.brackets)

/-- Tax on taxable income `ti` (cents, a whole number of dollars), in cents: dollars x bp = ticks of 1/100 cent. -/
def basicTaxC (p : Params) (ti : Int) : Int := (auSchedule p).ticks (ti / 100) / 100

/-- ITAA 1997 s. 61-115(1) table as two kernel credits in cents: item 1-2 ($700, less 5 % over $37,500) and item 3
($325, less 1.5 % over $45,000); the offset is the larger of the two (item 2 is the larger up to $45,000, where both
are $325). -/
def lito1 (p : Params) : TaxKernel.Credit :=
  { full := aud p.litoMax, start := aud p.litoT1, num := p.litoR1, den := 10000 }
def lito2 (p : Params) : TaxKernel.Credit :=
  { full := aud p.litoMid, start := aud p.litoT2, num := p.litoR2, den := 10000 }

/-- s. 61-110(1)(b): entitled only if taxable income does not exceed $66,667. -/
def litoC (p : Params) (ti : Int) : Int :=
  if ti > aud p.litoCeiling then 0
  else max ((lito1 p).value 0 ti) ((lito2 p).value 0 ti)

/-- ITAA 1997 s. 61-107 (2021-22, as the ATO tabulates it, see `Params`): the low and middle income tax offset, cents,
for taxable income `ti` (cents); nil from $126,000 and in every other year. -/
def lmitoC (p : Params) (ti : Int) : Int :=
  if !p.lmito || ti ≥ aud 126000 then 0
  else if ti ≤ aud 37000 then aud 675
  else if ti ≤ aud 48000 then min (aud 1500) (aud 675 + pct (ti - aud 37000) 750)
  else if ti ≤ aud 90000 then aud 1500
  else pos (aud 1500 - pct (ti - aud 90000) 300)

/-- The statute's three items read literally (the pre-kernel definition; `Theorems.lito_kernel_eq` proves the
kernel form equal to it). -/
def litoStatute (p : Params) (ti : Int) : Int :=
  if ti ≤ aud p.litoT1 then aud p.litoMax
  else if ti ≤ aud p.litoT2 then pos (aud p.litoMax - pct (ti - aud p.litoT1) p.litoR1)
  else if ti ≤ aud p.litoCeiling then pos (aud p.litoMid - pct (ti - aud p.litoT2) p.litoR2)
  else 0

/-- MLA ss. 6(1), 7(1)-(2) as a kernel `Surcharge` on whole dollars: 2 %, nothing up to the threshold amount, at most
10 % of the excess (the glide zone ends where 2 % takes over, at the phase-in limit). -/
def mlSurcharge (p : Params) : TaxKernel.Surcharge := { rate := p.mlRate, exempt := p.mlThreshold, glide := p.mlShadeRate }

/-- The levy before the family reduction (s. 8) and the surcharge (ss. 8B-8D), cents. -/
def levyS7C (p : Params) (ti : Int) : Int := (mlSurcharge p).ticks (ti / 100) / 100

/-- s. 7 read literally, with the phase-in limit as written (`Theorems.levy_kernel_eq` proves it equal to the
kernel form on whole dollars). -/
def levyStatute (p : Params) (ti : Int) : Int :=
  if ti ≤ aud p.mlThreshold then 0
  else if ti ≤ aud p.mlPhaseIn then min (pct ti p.mlRate) (pct (ti - aud p.mlThreshold) p.mlShadeRate)
  else pct ti p.mlRate

/-- Division 293 tax (ITAA 1997 s. 293-20): 15 % of the lesser of the taxable contributions and the excess of
(income for surcharge purposes, excluding reportable super contributions, + low tax contributions) over $250,000. -/
def div293C (p : Params) (x : Person) : Int :=
  let c := concessionalC p x
  let inc := taxableIncomeC p x + netInvestmentLossC x + c
  pct (min c (pos (inc - aud p.div293Threshold))) p.div293Rate

/-- 15 % tax paid by the fund on concessional contributions (ITRA s. 26; ITAA 1997 s. 295-160). -/
def contribTaxC (p : Params) (x : Person) : Int := pct (concessionalC p x) p.contribTaxRate

/-- HELP compulsory repayment (HESA s. 154-20; ATO tables): 2024-25 a rate on all repayment income; 2025-26
marginal. In cents. -/
def helpBandRate : List (Int × Int) → Int → Int
  | [], _ => 0
  | (lo, r) :: rest, ri => if ri ≥ aud lo then max r (helpBandRate rest ri) else helpBandRate rest ri

def helpRepaymentC (p : Params) (ri : Int) : Int :=
  if p.helpMarginal then
    if ri ≤ aud p.helpMin then 0
    else if ri ≤ aud p.helpMid then pct (ri - aud p.helpMin) p.helpR1
    else if ri ≤ aud p.helpTop then aud p.helpMidBase + pct (ri - aud p.helpMid) p.helpR2
    else pct ri p.helpTopRate
  else pct ri (helpBandRate p.helpBands (wholeDollars ri))

end AuTax
