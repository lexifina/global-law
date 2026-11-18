/-!
# The households entered into the live irs.gov Tax Withholding Estimator on 18 November 2026

Each `example` pins what the live calculator showed (read from its own fact graph, `window.factGraph`) next to what
the statute gives. Definitions repeat `TweNiit.lean` and `TweAddlMedicare.lean` so this file stands alone.
-/

def niit (nii magi thr : Nat) : Nat := (38 * min nii (magi - thr) + 500) / 1000

structure Case where
  thr : Nat
  magi : Nat
  nonQualDiv : Nat
  qualDiv : Nat
  pension : Nat

-- TWE /totalInvestmentIncomeForm8960Line8 reads non-qualified dividends and pensions; §1411(c)(1)(A)(i) and (c)(5)
-- say every dividend and no qualified-plan pension.
def tweNiit (c : Case) : Nat := niit (c.nonQualDiv + c.pension) c.magi c.thr
def lawNiit (c : Case) : Nat := niit (c.nonQualDiv + c.qualDiv) c.magi c.thr

/-- V1, live: single, salary $192,000, qualified dividends $68,000. Live: /netInvestmentIncomeTax 0.00. -/
def v1 : Case := { thr := 200000, magi := 260000, nonQualDiv := 0, qualDiv := 68000, pension := 0 }
/-- V1 control, live: the same $68,000 typed as ordinary dividends. Live: 2280.00. -/
def v1c : Case := { v1 with nonQualDiv := 68000, qualDiv := 0 }
/-- V2, live: single, 65+, employer pension $264,000. Live: line 8 264000.00, NIIT 2432.00. -/
def v2 : Case := { thr := 200000, magi := 264000, nonQualDiv := 0, qualDiv := 0, pension := 264000 }

example : tweNiit v1 = 0 ∧ lawNiit v1 = 2280 := by decide
example : tweNiit v1c = 2280 ∧ lawNiit v1c = 2280 := by decide
example : tweNiit v2 = 2432 ∧ lawNiit v2 = 0 := by decide

-- EITC, §32(i): disqualified income includes "interest or dividends to the extent includible in gross income";
-- 2026 limit $12,200 (Rev. Proc. 2025-32). TWE /belowEitcInvestmentIncomeLimit reads non-qualified dividends only.
def eitcLimit2026 : Nat := 12200
def tweEitcAllowed (nonQualDiv _qualDiv : Nat) : Bool := decide (nonQualDiv ≤ eitcLimit2026)
def lawEitcAllowed (nonQualDiv qualDiv : Nat) : Bool := decide (nonQualDiv + qualDiv ≤ eitcLimit2026)

/-- V1 (EITC), live: head of household, one child, salary $24,000, qualified dividends $13,000.
Live: /belowEitcInvestmentIncomeLimit true, /earnedIncomeCredit 2328.00. -/
example : tweEitcAllowed 0 13000 = true ∧ lawEitcAllowed 0 13000 = false := by decide
/-- Control, live: the same $13,000 as ordinary dividends. Live: limit false, EITC question hidden. -/
example : tweEitcAllowed 13000 0 = false ∧ lawEitcAllowed 13000 0 = false := by decide

-- V3: §3101(b)(2) tax; §3102(f)(1) the employer withholds 0.9% of its wages over $200,000; §3102(f)(2) the
-- employee pays only what was not withheld. TWE counts the tax and credits none of the withholding.
def addlMedicareTax (wages thr : Nat) : Nat := (9 * (wages - thr) + 500) / 1000
def employerWithholds (w : Nat) : Nat := (9 * (w - 200000) + 500) / 1000
def lawNetDue (wages thr : Nat) : Int := (addlMedicareTax wages thr : Int) - employerWithholds wages
def tweNetDue (wages thr : Nat) : Int := addlMedicareTax wages thr

/-- V3, live: single, one salary job $420,000. Live: /additionalMedicareTax 1980.00, /totalPayments 0.00,
balance owed $1,978 with income-tax withholding set $2 above income tax. -/
example : tweNetDue 420000 200000 = 1980 ∧ lawNetDue 420000 200000 = 0 := by decide

/-- For any single filer with one employer, the calculator overstates the bill by exactly what the employer withheld. -/
theorem single_one_job (w : Nat) : tweNetDue w 200000 - lawNetDue w 200000 = employerWithholds w := by
  unfold tweNetDue lawNetDue addlMedicareTax employerWithholds; omega
