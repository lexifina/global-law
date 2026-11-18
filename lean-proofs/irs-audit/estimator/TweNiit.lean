/-!
# TWE (2026) net investment income tax and EITC investment-income test vs 26 U.S.C. §1411 and §32(i)

Whole dollars. `niit nii magi thr` = 3.8% of the smaller of net investment income and the excess of MAGI over the
threshold (§1411(a)(1)), rounded half up as TWE's `<Round>` does.

TWE `/totalInvestmentIncomeForm8960Line8` = taxable interest + `/ordinaryDividendsIncome` (asked as Form 1040
line 3b minus line 3a, i.e. non-qualified dividends) + `/pensionsIncomeTotal` + passive/rental/royalty + net gain.
Statute: dividends (all of them, §1411(c)(1)(A)(i)) and no distribution from a §401(a)/403(a)/403(b)/408/408A/457(b)
plan (§1411(c)(5)).
-/

def niit (nii magi thr : Nat) : Nat := (38 * min nii (magi - thr) + 500) / 1000

structure Case where
  thr : Nat          -- §1411(b): 200,000 single/HoH, 250,000 joint, 125,000 separate
  magi : Nat         -- = AGI here (no §911 exclusion)
  nonQualDiv : Nat
  qualDiv : Nat
  pension : Nat      -- employer pension (qualified plan) income, Form 1099-R
  netGain : Nat

def tweNii (c : Case) : Nat := c.nonQualDiv + c.pension + c.netGain
def lawNii (c : Case) : Nat := c.nonQualDiv + c.qualDiv + c.netGain

def tweNiit (c : Case) : Nat := niit (tweNii c) c.magi c.thr
def lawNiit (c : Case) : Nat := niit (lawNii c) c.magi c.thr

/-- Case B: single, wages $300,000, qualified dividends $60,000 (TWE run: AGI 360,000, NIIT 0). -/
def caseB : Case := { thr := 200000, magi := 360000, nonQualDiv := 0, qualDiv := 60000, pension := 0, netGain := 0 }
/-- Case C (control): the same $60,000 entered as non-qualified dividends (TWE run: NIIT 2,280). -/
def caseC : Case := { caseB with nonQualDiv := 60000, qualDiv := 0 }
/-- Case D: single retiree, employer pension $249,996 only (TWE run: AGI 249,996, NIIT 1,900). -/
def caseD : Case := { thr := 200000, magi := 249996, nonQualDiv := 0, qualDiv := 0, pension := 249996, netGain := 0 }
/-- Case A: joint, pension $120,000 + spouse wages $200,000 + qualified dividends $40,000 (TWE run: AGI 359,992, NIIT 4,180). -/
def caseA : Case := { thr := 250000, magi := 359992, nonQualDiv := 0, qualDiv := 40000, pension := 120000, netGain := 0 }

example : tweNiit caseB = 0 ∧ lawNiit caseB = 2280 := by decide
example : tweNiit caseC = 2280 ∧ lawNiit caseC = 2280 := by decide
example : tweNiit caseD = 1900 ∧ lawNiit caseD = 0 := by decide
example : tweNiit caseA = 4180 ∧ lawNiit caseA = 1520 := by decide

/-- Largest possible understatement from the dividend omission alone: 3.8% of the qualified dividends. -/
theorem qd_gap (c : Case) (h : c.pension = 0) (hx : lawNii c ≤ c.magi - c.thr) :
    lawNiit c - tweNiit c ≤ (38 * c.qualDiv + 1000) / 1000 := by
  unfold lawNiit tweNiit niit tweNii lawNii at *
  rw [h]; simp only [Nat.add_zero]
  have h1 : min (c.nonQualDiv + c.qualDiv + c.netGain) (c.magi - c.thr) = c.nonQualDiv + c.qualDiv + c.netGain :=
    Nat.min_eq_left hx
  have h2 : min (c.nonQualDiv + c.netGain) (c.magi - c.thr) = c.nonQualDiv + c.netGain :=
    Nat.min_eq_left (by omega)
  rw [h1, h2]
  omega

/-! EITC investment-income test, §32(i)(1)-(2): disqualified income includes "dividends to the extent includible in
gross income"; 2026 limit $12,200 (Rev. Proc. 2025-32). TWE `/belowEitcInvestmentIncomeLimit` adds interest,
`/ordinaryDividendsIncome` (non-qualified only) and positive net gains. -/
def eitcLimit2026 : Nat := 12200
def tweEitcAllowed (nonQualDiv qualDiv : Nat) : Bool := decide (nonQualDiv ≤ eitcLimit2026)
def lawEitcAllowed (nonQualDiv qualDiv : Nat) : Bool := decide (nonQualDiv + qualDiv ≤ eitcLimit2026)

/-- Household 160 of batch b2: head of household, one child, wages $28,740, dividends $20,000 of which $10,000
qualified. TWE allows the credit ($970 in the run); §32(i) denies it. -/
example : tweEitcAllowed 10000 10000 = true ∧ lawEitcAllowed 10000 10000 = false := by decide

#eval [("B", tweNiit caseB, lawNiit caseB), ("C", tweNiit caseC, lawNiit caseC), ("D", tweNiit caseD, lawNiit caseD),
       ("A", tweNiit caseA, lawNiit caseA)]
