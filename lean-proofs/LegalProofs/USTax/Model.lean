/-!
# A model of 2025 US federal income tax for one household

Executable, exact (whole dollars, integer arithmetic), and small enough to reason about. It covers what a working
household with modest income meets:

* employee payroll tax (FICA: 6.2% Social Security up to the wage base, 1.45% Medicare);
* adjusted gross income, the standard deduction, and the ordinary rate schedule (IRC §1(j), as indexed for 2025);
* the Earned Income Tax Credit (§32), including the **disqualified-income limit** of §32(i);
* the Child Tax Credit and its refundable part (§24, as amended in 2025);
* the Retirement Savings Contributions Credit, the "Saver's Credit" (§25B), with its three AGI tiers.

Figures are for tax year 2025 and come from Rev. Proc. 2024-40 as amended by Pub. L. 119-21 (July 2025); each is cited
where it is defined. The EITC is computed from the statutory formula; the IRS tables round in $50 bands, so table
amounts can differ by a few dollars. What is left out (state tax, itemised deductions, other credits, benefits outside
the tax code) is listed in the write-up.
-/

namespace Legal.USTax

inductive Status where
  | single | mfj | hoh
  deriving DecidableEq, Repr

structure Household where
  status : Status
  kids : Nat       -- qualifying children (for both the EITC and the CTC)
  wages : Nat      -- earned income, dollars
  interest : Nat   -- taxable interest (investment income), dollars
  ira : Nat        -- deductible traditional IRA contributions, dollars
  deriving DecidableEq, Repr

/-! ## Parameters (2025) -/

/-- Standard deduction, as raised for 2025 by Pub. L. 119-21 §70102. -/
def stdDeduction : Status → Nat
  | .single => 15750 | .mfj => 31500 | .hoh => 23625

/-- EITC parameters by number of children (0, 1, 2, 3+): phase-in rate (basis points), earned income amount,
maximum credit, phase-out rate (basis points), phase-out start (single/HoH, MFJ). Rev. Proc. 2024-40 §2.06; §32(b). -/
structure EitcRow where
  inRate : Nat
  earnedAmt : Nat
  maxCredit : Nat
  outRate : Nat
  start : Nat
  startMfj : Nat

def eitcRow : Nat → EitcRow
  | 0 => ⟨765, 8490, 649, 765, 10620, 17730⟩
  | 1 => ⟨3400, 12730, 4328, 1598, 23350, 30470⟩
  | 2 => ⟨4000, 17880, 7152, 2106, 23350, 30470⟩
  | _ => ⟨4500, 17880, 8046, 2106, 23350, 30470⟩

/-- §32(i): no EITC at all if disqualified (investment) income exceeds this. Rev. Proc. 2024-40 §2.06(2). -/
def eitcInvestmentLimit : Nat := 11950

/-- Saver's Credit AGI ceilings for the 50%, 20% and 10% tiers. §25B(b), as indexed for 2025 by Notice 2024-80. -/
def saverTiers : Status → Nat × Nat × Nat
  | .mfj => (47500, 51000, 79000)
  | .hoh => (35625, 38250, 59250)
  | .single => (23750, 25500, 39500)

/-! ## The computation -/

def persons (s : Status) : Nat := if s = .mfj then 2 else 1

/-- Deductible IRA contributions, capped at $7,000 a person (2025). -/
def iraDeduction (h : Household) : Nat := min h.ira (7000 * persons h.status)

def agi (h : Household) : Nat := h.wages + h.interest - iraDeduction h

def taxable (h : Household) : Nat := agi h - stdDeduction h.status

/-- `rate`% of the part of `x` that falls between `lo` and `hi`. -/
def band (rate lo hi x : Nat) : Nat := rate * min (x - lo) (hi - lo)

/-- A seven-rate schedule with bracket edges `a < b < c < d < e < f`: 100 × the tax on `x`, before rounding. -/
def sched (a b c d e f x : Nat) : Nat :=
  band 10 0 a x + band 12 a b x + band 22 b c x + band 24 c d x + band 32 d e x + band 35 e f x + 37 * (x - f)

/-- The 2025 schedules (Rev. Proc. 2024-40 §2.01; unchanged by Pub. L. 119-21). -/
def schedule100 : Status → Nat → Nat
  | .single => sched 11925 48475 103350 197300 250525 626350
  | .mfj => sched 23850 96950 206700 394600 501050 751600
  | .hoh => sched 17000 64850 103350 197300 250500 626350

/-- Tax on taxable income `x` from the rate schedule, in whole dollars (rounded down). -/
def scheduleTax (s : Status) (x : Nat) : Nat := schedule100 s x / 100

def fica (h : Household) : Nat := (min h.wages 176100 * 620 + h.wages * 145) / 10000

def eitc (h : Household) : Nat :=
  if h.interest > eitcInvestmentLimit then 0 else
  let r := eitcRow h.kids
  let phaseIn := min (h.wages * r.inRate / 10000) r.maxCredit
  let start := if h.status = .mfj then r.startMfj else r.start
  let base := max (agi h) h.wages
  let reduction := (base - start) * r.outRate / 10000
  min phaseIn (r.maxCredit - reduction)

/-- Child Tax Credit before the tax limit: $2,200 a child, reduced $50 per $1,000 (or part) of AGI over the threshold. -/
def ctcFull (h : Household) : Nat :=
  let threshold := if h.status = .mfj then 400000 else 200000
  let over := agi h - threshold
  let steps := (over + 999) / 1000
  2200 * h.kids - 50 * steps

def saverRate (h : Household) : Nat :=
  let (t50, t20, t10) := saverTiers h.status
  let a := agi h
  if a ≤ t50 then 50 else if a ≤ t20 then 20 else if a ≤ t10 then 10 else 0

def saverFull (h : Household) : Nat := min h.ira (2000 * persons h.status) * saverRate h / 100

structure Result where
  agi : Nat
  incomeTax : Nat      -- after nonrefundable credits
  ctcNonref : Nat
  saver : Nat
  actc : Nat
  eitc : Nat
  fica : Nat
  net : Nat            -- wages + interest − income tax − FICA + refundable credits (IRA money stays the household's)
  deriving Repr

def compute (h : Household) : Result :=
  let before := scheduleTax h.status (taxable h)
  let ctcN := min (ctcFull h) before                     -- nonrefundable CTC first (Form 1040 line 19)
  let saver := min (saverFull h) (before - ctcN)         -- then the Saver's Credit, limited to what is left
  let tax := before - ctcN - saver
  let actc := min (ctcFull h - ctcN) (min (1700 * h.kids) ((h.wages - 2500) * 15 / 100))
  let e := eitc h
  let f := fica h
  { agi := agi h, incomeTax := tax, ctcNonref := ctcN, saver := saver, actc := actc, eitc := e, fica := f,
    net := h.wages + h.interest + actc + e - tax - f }

def net (h : Household) : Nat := (compute h).net

end Legal.USTax
