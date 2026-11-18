/-!
# TWE (2026): Additional Medicare Tax withheld by the employer is never credited

§3101(b)(2): 0.9% of wages over $200,000 ($250,000 joint, $125,000 separate) [§3101(b)(2), (thresholds)].
§3102(f)(1): the employer withholds that 0.9% on wages it pays in excess of $200,000, disregarding the spouse's wages.
§3102(f)(2): "To the extent that the amount of any tax imposed by section 3101(b)(2) is not collected by the employer,
such tax shall be paid by the employee." Form 8959 line 24 carries the withheld amount to Form 1040 line 25c.

TWE: amount owed = tax including `/additionalMedicareTax` − income-tax withholding − estimated payments − refundable
credits; the employer's 0.9% withholding appears nowhere. Whole dollars; one employer per earner.
-/

def addlMedicareTax (wages thr : Nat) : Nat := (9 * (wages - thr) + 500) / 1000
def employerWithholds (wagesFromEmployer : Nat) : Nat := (9 * (wagesFromEmployer - 200000) + 500) / 1000

/-- What the employee still owes (positive) or gets back (negative) on the Additional Medicare Tax after withholding. -/
def lawNetDue (wages thr : Nat) : Int := (addlMedicareTax wages thr : Int) - employerWithholds wages
/-- TWE's figure: the whole tax, no withholding credited. -/
def tweNetDue (wages thr : Nat) : Int := addlMedicareTax wages thr

-- Case E: single, one job, wages $399,996 (TWE run: /additionalMedicareTax 1,800, all of it in /totalOwed).
example : tweNetDue 399996 200000 = 1800 ∧ lawNetDue 399996 200000 = 0 := by decide
-- Case F: joint, one earner, wages $499,992 (TWE run: /additionalMedicareTax 2,250).
example : tweNetDue 499992 250000 = 2250 ∧ lawNetDue 499992 250000 = -450 := by decide

/-- For a single filer with one employer the overstatement is exactly the employer's withholding. -/
theorem single_one_job (w : Nat) : tweNetDue w 200000 - lawNetDue w 200000 = employerWithholds w := by
  unfold tweNetDue lawNetDue addlMedicareTax employerWithholds; omega

/-- Break-even: the overstatement reaches $1,000 once one employer pays more than $311,111. -/
example : employerWithholds 311111 = 1000 ∧ employerWithholds 311000 = 999 := by decide
