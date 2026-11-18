import UkTax.Rates

/-!
# One individual's liability (ITA 2007 s. 23, Steps 1 to 7)

Married couples and civil partners are taxed separately; what a couple chooses together (the marriage allowance
election, a transfer of blind person's allowance, the married couple's allowance) arrives as `Elections`.

* Step 1 (s. 23): total income, in three components: non-savings (employment, trading, pension, property income),
  savings (interest, s. 18) and dividends (s. 19).
* Step 2: the one Step 2 relief modelled is pension contributions relieved on a claim (FA 2004 s. 194(1), listed in
  s. 24(1)(a)), within the annual limit of FA 2004 s. 190.
* Step 3: the personal allowance (s. 35, tapered by adjusted net income, s. 58) and the blind person's allowance
  (s. 38). **s. 25(2)**: "deduct the reliefs and allowances in the way which will result in the greatest reduction
  in the taxpayer's liability to income tax" — an optimisation, computed exactly below (`bestSlices`).
* Steps 4 and 5: `Rates.lean`.
* Step 6: the marriage allowance tax reduction (s. 55B) and the married couple's allowance (s. 45, 46), each only
  "so far as there is sufficient tax" (s. 29(2)).
* Step 7: the Gift Aid charge (s. 424). The high income child benefit charge (ITEPA 2003 s. 681B, also a Step 7
  amount under s. 30) is computed for the household (`Household.lean`).

Capital gains tax (TCGA 1992 s. 1H–1K) and National Insurance (SSCBA 1992 s. 8, 11, 15) are computed alongside, as
they read the same figures.
-/

namespace UkTax

/-- One individual's income and payments for the tax year, in whole pounds. -/
structure Person where
  /-- Age on 6 April 2025 (the start of the tax year). -/
  age : Nat := 40
  blind : Bool := false
  /-- A Scottish taxpayer (ITA 2007 s. 11A; residence-based, Scotland Act 1998 s. 80D). -/
  scottish : Bool := false
  /-- Employment income (ITEPA 2003 Part 2); also the earnings for Class 1 contributions. -/
  employment : Int := 0
  /-- Trading profits (ITTOIA 2005 Part 2); also the profits for Class 4 contributions. -/
  trading : Int := 0
  /-- Pension income (ITEPA 2003 Part 9): no National Insurance. -/
  pension : Int := 0
  /-- Property income (ITTOIA 2005 Part 3), profits after expenses. -/
  property : Int := 0
  /-- Savings income: interest (ITA 2007 s. 18(3)(a)). -/
  interest : Int := 0
  /-- Dividend income (s. 19). -/
  dividends : Int := 0
  /-- Chargeable gains (TCGA 1992), before the annual exempt amount. -/
  gains : Int := 0
  /-- Gift Aid donations: the amount paid (the net gift, s. 414(2)(a)). -/
  giftAid : Int := 0
  /-- Pension contributions under relief at source, gross (FA 2004 s. 192; the member pays 80 %). -/
  rasGross : Int := 0
  /-- Pension contributions relieved on a claim, paid gross (FA 2004 s. 194(1), a Step 2 relief). -/
  claimContrib : Int := 0
  deriving Repr, DecidableEq, Inhabited

/-- What a married couple or civil partners choose together, as it touches one of them. -/
structure Elections where
  /-- s. 55C: this individual relinquishes the transferable amount of the personal allowance. -/
  maGive : Bool := false
  /-- s. 55B: this individual is the gaining party. -/
  maReceive : Bool := false
  /-- s. 39: excess blind person's allowance transferred from the spouse (whole pounds). -/
  bpaReceived : Int := 0
  /-- s. 45 / 46 / 51: married couple's allowance tax reduction available to this individual (ticks). -/
  mcaReduction : Int := 0
  /-- Amount transferred, if not the statutory transferable amount (only under `Reading.peMaUnused`). -/
  maAmount : Option Int := none
  deriving Repr, DecidableEq, Inhabited

def Person.nonSavings (x : Person) : Int := gbp (x.employment + x.trading + x.pension + x.property)
def Person.savings (x : Person) : Int := gbp x.interest
def Person.divs (x : Person) : Int := gbp x.dividends
/-- Step 1: "The sum of those amounts is 'total income'." -/
def Person.totalIncome (x : Person) : Int := x.nonSavings + x.savings + x.divs

/-- FA 2004 s. 189(2): "relevant UK earnings" are employment income and trading income. -/
def Person.relevantEarnings (x : Person) : Int := pos (x.employment + x.trading)

/-- FA 2004 s. 190(1)–(2) and s. 191(7): relief up to relevant UK earnings, or up to the basic amount (£3,600) for
relief at source only. s. 188(3)(a): no relief for "contributions paid after the individual has reached the age of
75" (age on 6 April 2025 of 75 or more: none in the year). Returns (relieved on a claim, relieved at source), in
pounds. -/
def relievedContributions (p : Params) (x : Person) : Int × Int :=
  if x.age ≥ 75 then (0, 0) else
  let claim := min (pos x.claimContrib) x.relevantEarnings
  let ras := min (pos x.rasGross) (pos (max p.pensionBasicAmount x.relevantEarnings - claim))
  (claim, ras)

/-- **s. 35**: the personal allowance for adjusted net income `a` (pence), in whole pounds: (1) £12,570; (2) "reduced
by one-half of the excess" over £100,000; (3) "rounded up to the nearest amount which is a multiple of £1". -/
def personalAllowance (p : Params) (a : Int) : Int :=
  pos (ceilDiv (2 * gbp p.personalAllowance - pos (a - gbp p.paIncomeLimit)) 200)

/-! ## Step 3 allocation (s. 25(2))

The deductions at Steps 2 and 3 (`ded`, in pence) can be taken from the three components in any proportions. With
`N, S, D` the components and `t = N + S + D - ded` the Step 3 income, an allocation is fixed by the slice
boundaries `c1` (non-savings left) and `c2` (non-savings and savings left):
`0 ≤ c1 ≤ N`, `c1 ≤ c2 ≤ c1 + S`, `t - D ≤ c2 ≤ t`.

The tax is linear in `(c1, c2)` between break lines: `c1` or `c2` equal to the limits (starting rate limit, basic
and higher rate limits, the limits less the savings or dividend allowance), `c2 = t - D`, `t`, `t - £500`, and
`c2 - c1` equal to 0, `S` or the savings allowance. A linear function on a polygon is least at a vertex, so the
least tax over all allocations is the least over the crossing points of those lines that are feasible. -/

def feasible (N S D t c1 c2 : Int) : Bool :=
  decide (0 ≤ c1) && decide (c1 ≤ N) && decide (c1 ≤ c2) && decide (c2 ≤ c1 + S) && decide (t - D ≤ c2)
    && decide (c2 ≤ t)

/-- The usual order (non-savings income first, then savings, then dividends). -/
def defaultSlices (N S D ded : Int) : Int × Int :=
  let d := min (pos ded) (N + S + D)
  let aN := min N d
  let aS := min S (d - aN)
  (N - aN, N - aN + S - aS)

def candidates (p : Params) (l : Limits) (N S D t : Int) : List (Int × Int) :=
  let srl := gbp p.startingRateLimitSavings
  let da := gbp p.dividendAllowance
  let psas : List Int := [gbp p.psaBasic, gbp p.psaHigher]
  let v : List Int := [0, N, srl, l.brl, l.hrl] ++ psas.map (l.brl - ·) ++ psas.map (l.hrl - ·)
  let h : List Int := [t - D, t, srl, l.brl, l.hrl, l.brl - da, l.hrl - da, t - da] ++ psas.map (srl + ·)
  let dg : List Int := [0, S] ++ psas
  (v.flatMap fun a => h.map fun b => (a, b)) ++ (v.flatMap fun a => dg.map fun d => (a, a + d))
    ++ (h.flatMap fun b => dg.map fun d => (b - d, b))

/-- One step of the search: keep the better of the best so far and the next candidate. -/
def bestStep (f : Int → Int → Int) (ok : Int → Int → Bool) (best c : Int × Int) : Int × Int :=
  if ok c.1 c.2 && decide (f c.1 c.2 < f best.1 best.2) then c else best

/-- The feasible candidate with the least value of `f`; the default order wins ties. -/
def bestSlices (f : Int → Int → Int) (ok : Int → Int → Bool) (dflt : Int × Int) (cs : List (Int × Int)) :
    Int × Int :=
  cs.foldl (bestStep f ok) dflt

theorem bestStep_le_best (f : Int → Int → Int) (ok : Int → Int → Bool) (b c : Int × Int) :
    f (bestStep f ok b c).1 (bestStep f ok b c).2 ≤ f b.1 b.2 := by
  unfold bestStep
  split
  · next h => simp only [Bool.and_eq_true, decide_eq_true_eq] at h; omega
  · exact Int.le_refl _

theorem bestStep_le_c (f : Int → Int → Int) (ok : Int → Int → Bool) (b c : Int × Int)
    (hok : ok c.1 c.2 = true) : f (bestStep f ok b c).1 (bestStep f ok b c).2 ≤ f c.1 c.2 := by
  unfold bestStep
  split
  · exact Int.le_refl _
  · next h => simp only [hok, Bool.true_and, decide_eq_true_eq] at h; omega

theorem foldl_bestStep_le_init (f : Int → Int → Int) (ok : Int → Int → Bool) (cs : List (Int × Int)) :
    ∀ b : Int × Int, f (cs.foldl (bestStep f ok) b).1 (cs.foldl (bestStep f ok) b).2 ≤ f b.1 b.2 := by
  induction cs with
  | nil => intro b; simp
  | cons c cs ih =>
    intro b
    simp only [List.foldl_cons]
    exact Int.le_trans (ih _) (bestStep_le_best f ok b c)

theorem foldl_bestStep_le_mem (f : Int → Int → Int) (ok : Int → Int → Bool) (cs : List (Int × Int))
    (c : Int × Int) (hc : c ∈ cs) (hok : ok c.1 c.2 = true) :
    ∀ b : Int × Int, f (cs.foldl (bestStep f ok) b).1 (cs.foldl (bestStep f ok) b).2 ≤ f c.1 c.2 := by
  induction cs with
  | nil => simp at hc
  | cons d cs ih =>
    intro b
    simp only [List.foldl_cons]
    rcases List.mem_cons.mp hc with h | h
    · subst h
      exact Int.le_trans (foldl_bestStep_le_init f ok cs _) (bestStep_le_c f ok b c hok)
    · exact ih h _

/-- The search never does worse than the usual order. -/
theorem bestSlices_le_dflt (f : Int → Int → Int) (ok : Int → Int → Bool) (dflt : Int × Int)
    (cs : List (Int × Int)) : f (bestSlices f ok dflt cs).1 (bestSlices f ok dflt cs).2 ≤ f dflt.1 dflt.2 :=
  foldl_bestStep_le_init f ok cs dflt

/-- Every feasible candidate is at least as costly as the one chosen. -/
theorem bestSlices_le (f : Int → Int → Int) (ok : Int → Int → Bool) (dflt : Int × Int)
    (cs : List (Int × Int)) (c : Int × Int) (hc : c ∈ cs) (hok : ok c.1 c.2 = true) :
    f (bestSlices f ok dflt cs).1 (bestSlices f ok dflt cs).2 ≤ f c.1 c.2 :=
  foldl_bestStep_le_mem f ok cs c hc hok dflt

/-- **S.I. 2001/1004 reg. 100**: the annual maximum of Class 4 contributions of an earner who also pays primary
Class 1 contributions. `c1main`: primary Class 1 paid at the main primary percentage (ticks); `P`: profits (pence);
`c4main`: Class 4 at the main Class 4 percentage (ticks).
Step One: upper less lower profits limit; Step Two: × 6 %; Step Four: less the Class 1 at the main percentage.
Case 1: positive and more than Class 1 + Class 4 at the main percentages: that is the maximum. Case 2 / 3: the
(non-negative) Step Four, plus Step Eight: 2 % of (Step Six: profits up to the upper limit less the lower limit,
less Step Five: Step Four × 100/6), plus Step Nine: 2 % of profits above the upper limit. -/
def class4Maximum (p : Params) (c1main : Int) (P : Int) (c4main : Int) : Int :=
  let lpl := gbp p.class4Lower
  let upl := gbp p.class4Upper
  let step2 := p.class4MainRate * (upl - lpl)
  let step4raw := step2 - c1main
  if step4raw > 0 && step4raw > c1main + c4main then step4raw
  else
    let step4 := pos step4raw
    let step6 := min upl P - lpl
    let step8 := pos (p.class4MainRate * step6 - step4) * p.class4AdditionalRate / p.class4MainRate
    let step9 := p.class4AdditionalRate * pos (P - upl)
    step4 + step8 + step9

/-- The result of Steps 1 to 7 (and CGT and NI) for one individual. Money in pence, tax in ticks. -/
structure PersonResult where
  totalIncome : Int
  netIncome : Int
  claimRelieved : Int
  rasRelieved : Int
  grossGift : Int
  ani : Int
  /-- Personal allowance (pounds) after any marriage-allowance reduction (s. 55B(6)). -/
  pa : Int
  /-- Blind person's allowance, own plus any received from the spouse (pounds). -/
  bpa : Int
  /-- Reliefs and allowances deducted at Steps 2 and 3 (pence; never more than the income, s. 25(4)). -/
  deducted : Int
  rasExtends : Bool
  limits : Limits
  /-- The Scottish limits used, for a Scottish taxpayer. -/
  scot : Option ScotLimits
  /-- The rate conditions of s. 55B(2)(b)/(ba) and s. 55C(1)(c)/(ca) hold. -/
  maRates : Bool
  c1 : Int
  c2 : Int
  /-- Step 3 income (s. 12A(7)). -/
  t : Int
  ch : Charged
  tax5 : Int
  maReduction : Int
  mcaUsed : Int
  tax6 : Int
  /-- s. 414(2)(a): the tax treated as deducted from the gifts ("amount A" of s. 424). -/
  giftAidTax : Int
  giftAidCharge : Int
  /-- The liability to income tax (Step 7), without the high income child benefit charge. -/
  liability : Int
  /-- FA 2004 s. 192(1): basic-rate tax deducted and retained from relief-at-source contributions. -/
  rasRelief : Int
  cgtTaxable : Int
  cgt : Int
  class1 : Int
  class4 : Int
  deriving Repr

/-- The Step 3 slices and the charge for given limits, choosing the allocation by s. 25(2). `maGain` is the
marriage-allowance reduction the individual would get if its rate conditions hold (it is part of the liability
that s. 25(2) minimises). -/
def allocate (p : Params) (r : Reading) (l : Limits) (sc : Option ScotLimits) (N S D ded : Int) (maGain : Int) :
    Int × Int × Int :=
  let tot := N + S + D
  let t := tot - min (pos ded) tot
  let f : Int → Int → Int := fun c1 c2 =>
    let c := charged p r l c1 c2 t
    let tx := stepTax p sc c c1
    tx - (if maRatesOK sc c c1 then min maGain tx else 0)
  let ok := feasible N S D t
  let d := defaultSlices N S D ded
  let b := bestSlices f ok d (candidates p l N S D t)
  (b.1, b.2, t)

/-- Steps 1 to 7 for one individual, with capital gains tax and National Insurance. -/
def personCalc (p : Params) (r : Reading) (x : Person) (e : Elections) : PersonResult :=
  let N := pos x.nonSavings
  let S := pos x.savings
  let D := pos x.divs
  let tot := N + S + D
  let (claimP, rasP) := relievedContributions p x
  let claimRelieved := min (gbp claimP) tot
  let rasRelieved := gbp rasP
  let netIncome := tot - claimRelieved
  let grossGift := 125 * pos x.giftAid
  let ani := netIncome - grossGift - rasRelieved
  let paFull := personalAllowance p ani
  let maAmt := e.maAmount.getD p.maTransferable
  let pa := if e.maGive then pos (paFull - maAmt) else paFull
  let bpa := (if x.blind then p.blindAllowance else 0) + pos e.bpaReceived
  -- `--pe`: relief-at-source contributions deducted like an allowance (no relief at source, no band extension)
  let rasDed := if r.peRasDeduction then rasRelieved else 0
  let ded := claimRelieved + min (gbp (pa + bpa) + rasDed) netIncome
  let maGain : Int := if e.maReceive then gbp maAmt * p.basicRate else 0
  -- Gift Aid always extends the limits (s. 414(2)(b)); relief at source only if, apart from s. 192, tax is
  -- chargeable at the higher or additional rate (s. 192(4)).
  let l0 : Limits := { brl := gbp p.basicRateLimit + grossGift, hrl := gbp p.higherRateLimit + grossGift }
  -- s. 414(2)(b): the Scottish limits from the basic rate's upper limit up are increased by the gift
  let sl0 : ScotLimits :=
    { starter := gbp p.scotStarterLimit, basic := gbp p.scotBasicLimit + grossGift,
      intermediate := gbp p.scotIntermediateLimit + grossGift, higher := gbp p.scotHigherLimit + grossGift,
      advanced := gbp p.higherRateLimit + grossGift }
  let sc0 : Option ScotLimits := if x.scottish then some sl0 else none
  let (a1, a2, t0) := allocate p r l0 sc0 N S D ded maGain
  let ch0 := charged p r l0 a1 a2 t0
  let rasExtends := !r.peRasDeduction && decide (rasRelieved > 0) &&
    (match r.ras with
     | .unconditional => true
     | .anyHigherRate => ch0.anyHigher
     | .mainRatesOnly => ch0.mainHigher)
  let l : Limits := if rasExtends then { brl := l0.brl + rasRelieved, hrl := l0.hrl + rasRelieved } else l0
  -- FA 2004 s. 192(4A): a Scottish taxpayer's limits above the Scottish basic rate's, when a Scottish rate above the
  -- Scottish basic rate is chargeable apart from s. 192
  let scotExtends := x.scottish && !r.peRasDeduction && decide (rasRelieved > 0) &&
    (match r.ras with
     | .unconditional => true
     | _ => decide (a1 > sl0.basic))
  let sc : Option ScotLimits :=
    if !x.scottish then none
    else if scotExtends then
      some { sl0 with basic := sl0.basic + rasRelieved, intermediate := sl0.intermediate + rasRelieved,
                      higher := sl0.higher + rasRelieved, advanced := sl0.advanced + rasRelieved }
    else some sl0
  let (c1, c2, t) := allocate p r l sc N S D ded maGain
  let ch := charged p r l c1 c2 t
  let tax5 := stepTax p sc ch c1
  let maRates := maRatesOK sc ch c1
  let maReduction := if e.maReceive && maRates then min maGain tax5 else 0
  let mcaUsed := min (pos e.mcaReduction) (tax5 - maReduction)
  let tax6 := tax5 - maReduction - mcaUsed
  -- TCGA 1992 s. 1K: annual exempt amount; s. 1H(3), 1I, 1J: 18 % within the unused basic rate band, 24 % above,
  -- and 24 % on all gains if any income is charged at a higher income tax rate.
  let gainsP := gbp (pos x.gains)
  let cgtTaxable := pos (gainsP - gbp p.cgtExemptAmount)
  let unused :=
    if r.peRasDeduction then
      -- PolicyEngine: the band extended by the relieved contributions, against income before their deduction
      pos (l0.brl + rasRelieved - (tot - min (claimRelieved + min (gbp (pa + bpa)) netIncome) tot))
    else pos (l.brl - t)
  let low := if ch.anyHigher && !r.peRasDeduction then 0 else min cgtTaxable unused
  let cgt := p.cgtLowerRate * low + p.cgtHigherRate * (cgtTaxable - low)
  -- s. 424: if the tax treated as deducted from the gifts exceeds the income tax (s. 425: Steps 1–6) and CGT
  -- charged, the difference is charged.
  let giftAidTax := grossGift * p.basicRate
  let giftAidCharge := if r.peNoGiftAidCharge then 0 else pos (giftAidTax - (tax6 + cgt))
  let liability := tax6 + giftAidCharge
  let rasRelief := if r.peRasDeduction then 0 else rasRelieved * p.basicRate
  -- SSCBA 1992 s. 6(3), 8: primary Class 1 below pensionable age, annual earnings period (reg. 11(3)(b), (2A)(b)).
  let E := gbp (pos x.employment)
  let young := decide (x.age < p.statePensionAge)
  let c1main := if young then p.niMainRate * overlap 0 E (gbp p.niPrimaryThreshold) (gbp p.niUpperEarningsLimit) else 0
  let class1 := c1main + (if young then p.niAdditionalRate * above 0 E (gbp p.niUpperEarningsLimit) else 0)
  -- s. 15(3), (3ZA); S.I. 2001/1004 reg. 91: no Class 4 if over pensionable age at the start of the year; reg. 100:
  -- capped for an earner who also pays primary Class 1.
  let P := gbp (pos x.trading)
  let c4main := if young then p.class4MainRate * overlap 0 P (gbp p.class4Lower) (gbp p.class4Upper) else 0
  let c4full := c4main + (if young then p.class4AdditionalRate * above 0 P (gbp p.class4Upper) else 0)
  let class4 := if class1 > 0 then min c4full (class4Maximum p c1main P c4main) else c4full
  { totalIncome := tot, netIncome, claimRelieved, rasRelieved, grossGift, ani, pa, bpa, deducted := ded,
    rasExtends, limits := l, scot := sc, maRates, c1, c2, t, ch, tax5, maReduction, mcaUsed, tax6, giftAidTax,
    giftAidCharge, liability, rasRelief, cgtTaxable, cgt, class1, class4 }

end UkTax
