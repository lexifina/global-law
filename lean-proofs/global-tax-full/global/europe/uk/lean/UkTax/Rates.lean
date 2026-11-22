import UkTax.Params

/-!
# Step 4: the rates at which income is charged (ITA 2007 Part 2 Chapter 2)

After Step 3 an individual's income is three components: non-savings income `N`, savings income `S` and dividend
income `D` (all in pence). Section 16 stacks them: "savings and dividend income ... together treated as the highest
part of the person's total income, and ... the dividend income is treated as the higher part" (s. 16(5)). So with
`c1 = N`, `c2 = N + S`, `t = N + S + D` (the "Step 3 income", s. 12A(7)) the income occupies positions

    non-savings [0, c1],  savings [c1, c2],  dividends [c2, t]

and each slice is charged by where it sits against the basic rate limit `brl` and the higher rate limit `hrl`
(both increased by Gift Aid, s. 414(2), and by relieved pension contributions, FA 2004 s. 192(4)):

* s. 10(2), (3), (3A): non-savings income up to `brl` at the basic rate, to `hrl` at the higher rate, above at
  the additional rate;
* s. 12(1): savings income "up to the starting rate limit for savings" that "would otherwise be charged at the
  basic rate" at the starting rate for savings (0 %, s. 7(1));
* s. 12A: if Step 3 income exceeds the starting rate limit `L`, "the lowest £A of the excess" of savings above
  `L` at the savings nil rate (0 %), `A` the savings allowance of s. 12B;
* s. 11D: other savings income at the savings basic, higher and additional rates by position;
* s. 13A: the first £500 of dividend income (taken in the order ordinary, upper, additional — the lowest £500 of
  the dividend slice) at the dividend nil rate;
* s. 13: other dividend income at the dividend ordinary, upper and additional rates by position.

The nil rates replace a rate but keep the income where it is: nil-rate income still uses up the bands.

Two readings are kept apart (`Reading`), because the words and HMRC's practice part company:

* **s. 12B(8)** defines "higher-rate income" as income "charged at the higher rate, default higher rate or dividend
  upper rate" (or that would be but for s. 12A / 13A). Since 2017-18 savings above the basic rate limit are
  charged at the *savings* higher rate (s. 11D, inserted by FA 2016 s. 6, the same section that added the
  "default" rates to s. 12B(8) but not the savings rates). Read literally, savings never make anyone a
  higher-rate taxpayer for the savings allowance. HMRC (gov.uk/apply-tax-free-interest-on-savings: "To work out
  your tax band, add all the interest you've earned to your other income") counts them. `psaLiteral := false`
  (the default) follows HMRC; `true` follows the words.
* **FA 2004 s. 192(4)** extends the bands for relief-at-source pension contributions only "If (apart from this
  section) income tax at the higher rate or the additional rate ... is chargeable". Three readings (`RasRule`):
  `anyHigherRate` (the default: the condition, with "the higher rate" taken to cover every rate of the higher and
  additional bands — the savings higher rate and the dividend upper rate as well); `mainRatesOnly` (the words: only
  the main higher and additional rates, so income above the basic rate limit that is all savings or dividends does
  not qualify); `unconditional` (HMRC's Capital Gains Manual CG21204: the band is extended "where relief at source is
  given for a pension contribution", no condition stated; PolicyEngine).
-/

/-- Which taxpayers' rate limits FA 2004 s. 192(4) increases. -/
inductive RasRule where
  | unconditional
  | anyHigherRate
  | mainRatesOnly
  deriving Repr, DecidableEq

namespace UkTax

structure Reading where
  /-- ITA 2007 s. 12B(8) read literally: savings charged at the savings higher or additional rate is not
  "higher-rate income" or "additional-rate income". -/
  psaLiteral : Bool := false
  /-- FA 2004 s. 192(4): see `RasRule`. -/
  ras : RasRule := .anyHigherRate
  /-- **Conventions of another implementation, for differential testing only** (`--pe`). PolicyEngine-UK:
  relief-at-source contributions deducted from income instead of extending the bands with 20 % relief at source; -/
  peRasDeduction : Bool := false
  /-- the marriage allowance transfers only the partner's unused personal allowance (capped at 10 %, rounded up to
  £10) and does not reduce the transferor's allowance; -/
  peMaUnused : Bool := false
  /-- no Gift Aid charge (s. 424); -/
  peNoGiftAidCharge : Bool := false
  /-- the married couple's allowance is not computed (an input there). -/
  peNoMca : Bool := false
  /-- **OECD Taxing Wages conventions** (`--oecd`; scored separately from the statute, cmp20/TESTING.md 2.2).
  Child benefit annualised as 365/7 weeks of the weekly rates (the statute counts the weeks of the tax year by their
  Mondays, ITEPA 2003 s. 681H(3) and S.I. 2006/965 reg. 2: 52 weeks in 2025-26); -/
  oecdCbAnnual : Bool := false
  /-- the high income child benefit charge as a continuous share of child benefit, without the whole-percent and
  whole-pound rounding of ITEPA 2003 s. 681C(3). -/
  oecdHicbcContinuous : Bool := false
  deriving Repr, DecidableEq

/-- HMRC's practice. -/
def Reading.hmrc : Reading := {}
/-- The words of s. 12B(8) and s. 192(4). -/
def Reading.literal : Reading := { psaLiteral := true, ras := .mainRatesOnly }
/-- The OECD Taxing Wages conventions (HMRC's reading otherwise). -/
def Reading.oecd : Reading := { oecdCbAnnual := true, oecdHicbcContinuous := true }
/-- PolicyEngine-UK's conventions (HMRC's reading otherwise). -/
def Reading.pe : Reading :=
  { peRasDeduction := true, peMaUnused := true, peNoGiftAidCharge := true, ras := .unconditional, peNoMca := true }

/-- The rate limits for one person, in pence (already increased by s. 414(2) / s. 192(4)). -/
structure Limits where
  brl : Int
  hrl : Int
  deriving Repr, DecidableEq

/-- Is any income "higher-rate income" (s. 12B(8)(b))? `c1, c2, t` are the slice boundaries.
HMRC: any income above the basic rate limit. Literal: non-savings income above it, or dividend income above it
(charged at the dividend upper rate or, but for s. 13A, it would be). -/
def higherRateIncome (r : Reading) (l : Limits) (c1 c2 t : Int) : Bool :=
  if r.psaLiteral then decide (c1 > l.brl) || (decide (t > l.brl) && decide (c2 < t))
  else decide (t > l.brl)

/-- Is any income "additional-rate income" (s. 12B(8)(a))? -/
def additionalRateIncome (r : Reading) (l : Limits) (c1 c2 t : Int) : Bool :=
  if r.psaLiteral then decide (c1 > l.hrl) || (decide (t > l.hrl) && decide (c2 < t))
  else decide (t > l.hrl)

/-- **s. 12B(2)–(4)**: the individual's savings allowance, in pence. -/
def savingsAllowance (p : Params) (r : Reading) (l : Limits) (c1 c2 t : Int) : Int :=
  if additionalRateIncome r l c1 c2 t then gbp p.psaAdditional
  else if higherRateIncome r l c1 c2 t then gbp p.psaHigher
  else gbp p.psaBasic

/-- The charge on a slice `[a, b]` at three rates by position (basic band `[0, brl]`, higher band `[brl, hrl]`,
additional band above `hrl`), in ticks. -/
def slice3 (l : Limits) (r1 r2 r3 a b : Int) : Int :=
  r1 * overlap a b 0 l.brl + r2 * overlap a b l.brl l.hrl + r3 * above a b l.hrl

/-- How the Step 3 income is charged: the amount in each band of each kind, in pence. -/
structure Charged where
  nsBasic : Int
  nsHigher : Int
  nsAdditional : Int
  savStarting : Int      -- s. 12: starting rate for savings (0 %)
  savNil : Int           -- s. 12A: savings nil rate (0 %)
  savBasic : Int
  savHigher : Int
  savAdditional : Int
  divNil : Int           -- s. 13A: dividend nil rate (0 %)
  divNilAbove : Int      -- of which above the basic rate limit (at the upper rate "if section 13A ... were omitted")
  divOrdinary : Int
  divUpper : Int
  divAdditional : Int
  psa : Int              -- the savings allowance applied (s. 12B)
  deriving Repr, DecidableEq

/-- **Step 4** for the slices `[0,c1]`, `[c1,c2]`, `[c2,t]` (s. 10, 11D, 12, 12A, 12B, 13, 13A, 16). -/
def charged (p : Params) (r : Reading) (l : Limits) (c1 c2 t : Int) : Charged :=
  let srl := gbp p.startingRateLimitSavings
  let psa := savingsAllowance p r l c1 c2 t
  -- s. 12A: the excess is the savings above the starting rate limit; its lowest £A is nil-rated
  let m := max c1 srl
  let nilS := min (pos (c2 - m)) psa
  let s0 := m + nilS
  -- s. 13A: the lowest £500 of the dividend slice
  let nilD := min (pos (t - c2)) (gbp p.dividendAllowance)
  let d0 := c2 + nilD
  { nsBasic := overlap 0 c1 0 l.brl
    nsHigher := overlap 0 c1 l.brl l.hrl
    nsAdditional := above 0 c1 l.hrl
    savStarting := overlap c1 c2 0 (min srl l.brl)
    savNil := nilS
    savBasic := overlap s0 c2 0 l.brl
    savHigher := overlap s0 c2 l.brl l.hrl
    savAdditional := above s0 c2 l.hrl
    divNil := nilD
    divNilAbove := above c2 d0 l.brl
    divOrdinary := overlap d0 t 0 l.brl
    divUpper := overlap d0 t l.brl l.hrl
    divAdditional := above d0 t l.hrl
    psa := psa }

/-- **Step 4 and Step 5**: tax at each rate, added together (ticks). -/
def Charged.tax (p : Params) (c : Charged) : Int :=
  p.basicRate * c.nsBasic + p.higherRate * c.nsHigher + p.additionalRate * c.nsAdditional
  + p.savingsBasicRate * c.savBasic + p.savingsHigherRate * c.savHigher
  + p.savingsAdditionalRate * c.savAdditional
  + p.dividendOrdinaryRate * c.divOrdinary + p.dividendUpperRate * c.divUpper
  + p.dividendAdditionalRate * c.divAdditional

/-- The tax on the non-savings slice at the main rates (what s. 11A replaces for a Scottish taxpayer). -/
def Charged.nsMainTax (p : Params) (c : Charged) : Int :=
  p.basicRate * c.nsBasic + p.higherRate * c.nsHigher + p.additionalRate * c.nsAdditional

/-- A Scottish taxpayer's rate limits (pence): the upper limits of the starter, basic, intermediate, higher and
advanced rates. s. 414(2)(b) increases "the upper limit for the Scottish basic rate and the limits for any Scottish
rates above the Scottish basic rate" by the grossed-up gift; FA 2004 s. 192(4A) does the same for relieved pension
contributions when a Scottish rate above the Scottish basic rate is chargeable. -/
structure ScotLimits where
  starter : Int
  basic : Int
  intermediate : Int
  higher : Int
  advanced : Int
  deriving Repr, DecidableEq

/-- **ITA 2007 s. 11A**: "Income tax is charged at Scottish rates on the non-savings income of a Scottish taxpayer"
(the slice `[0, c1]`); savings and dividends keep the UK rates and the UK limits "as if" not a Scottish taxpayer
(s. 11D(6), s. 13(5)). Ticks. -/
def scotNonSavingsTax (p : Params) (s : ScotLimits) (c1 : Int) : Int :=
  p.scotStarterRate * overlap 0 c1 0 s.starter + p.scotBasicRate * overlap 0 c1 s.starter s.basic
  + p.scotIntermediateRate * overlap 0 c1 s.basic s.intermediate
  + p.scotHigherRate * overlap 0 c1 s.intermediate s.higher
  + p.scotAdvancedRate * overlap 0 c1 s.higher s.advanced + p.scotTopRate * above 0 c1 s.advanced

/-- Step 5: the UK charge, or, for a Scottish taxpayer, with the non-savings slice at the Scottish rates. -/
def stepTax (p : Params) (sc : Option ScotLimits) (c : Charged) (c1 : Int) : Int :=
  match sc with
  | none => c.tax p
  | some s => c.tax p - c.nsMainTax p + scotNonSavingsTax p s c1

/-- Is any income charged above the basic rate limit at a positive rate (the higher-rate test of FA 2004
s. 192(4) on HMRC's reading, and of TCGA 1992 s. 1I(1) / s. 1J(1), whose "higher income tax rate" lists the higher
rate, the savings higher rate and the dividend upper rate)? -/
def Charged.anyHigher (c : Charged) : Bool :=
  decide (c.nsHigher + c.nsAdditional + c.savHigher + c.savAdditional + c.divUpper + c.divAdditional > 0)

/-- The literal test of FA 2004 s. 192(4): income "at the higher rate or the additional rate". -/
def Charged.mainHigher (c : Charged) : Bool := decide (c.nsHigher + c.nsAdditional > 0)

/-- **s. 55B(2)(b) and (ba)** (and s. 55C(1)(c), (ca) for the other spouse): liable to tax at no rate other than
the basic rate, the savings basic rate, the dividend nil rate, the dividend ordinary rate, the savings nil rate or
the starting rate for savings; and, if liable at the dividend nil rate, not liable at the dividend upper or
additional rate "if section 13A ... were omitted". The savings nil rate has no such proviso: savings nil-rated
above the basic rate limit do not bar the allowance. -/
def Charged.basicRateOnly (c : Charged) : Bool :=
  decide (c.nsHigher + c.nsAdditional + c.savHigher + c.savAdditional + c.divUpper + c.divAdditional = 0)
  && (decide (c.divNil = 0) || decide (c.divNilAbove = 0))

/-- The same test for a Scottish taxpayer: the permitted rates include "the Scottish basic rate, a Scottish rate below
the Scottish basic rate, the Scottish intermediate rate" (s. 55B(2)(b)): non-savings income no higher than the
intermediate rate's limit; savings and dividends as for anyone else. -/
def maRatesOK (sc : Option ScotLimits) (c : Charged) (c1 : Int) : Bool :=
  match sc with
  | none => c.basicRateOnly
  | some s => decide (c1 ≤ s.intermediate)
      && decide (c.savHigher + c.savAdditional + c.divUpper + c.divAdditional = 0)
      && (decide (c.divNil = 0) || decide (c.divNilAbove = 0))

end UkTax
