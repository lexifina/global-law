import LegalProofs.USTax.TaxCourt.Params

/-!
# Penalties and additions to tax: §6662(a), (b)(1)–(2), (d) and §6651(a)(1)–(2), (c)(1), (f) (2012–2024)

**§6662.** A 20% penalty on the portion of an underpayment attributable to negligence or to a substantial
understatement. An understatement is substantial if it exceeds the greater of 10% of the tax required to be shown or
$5,000 (§6662(d)(1)(A)); 5% instead of 10% for a taxpayer who claims a §199A deduction (§6662(d)(1)(C), years after
2017). The understatement is reduced by items with substantial authority, or adequately disclosed with a reasonable
basis (§6662(d)(2)(B)). No penalty for a portion with reasonable cause and good faith (§6664(c)(1)), and none unless
the initial determination was personally approved in writing by the immediate supervisor (§6751(b)(1)), except a
penalty "automatically calculated through electronic means" (§6751(b)(2)(B)). These rules did not change 2012–2024.

Amounts compared are "tax" in the deficiency sense: refundable credits count as negative tax (§6211(b)(4)), so an
over-claimed EIC can create an understatement — the measure the Tax Court uses when it sustains §6662 penalties on
disallowed refundable credits. Callers can pass other measures.

**§6651.** (a)(1) failure to file: 5% of the net amount required to be shown (§6651(b)(1): less timely payments and
credits) for each month or fraction of lateness, up to 25%; if more than 60 days late, not less than the lesser of the
year's minimum (`Params.ftfMinimum`) or 100% of that amount. (a)(2) failure to pay the tax shown: 0.5% per month or
fraction, up to 25%. (c)(1): for a month both apply, (a)(1) is reduced by (a)(2). (c)(2): when the tax shown exceeds the tax required to be
shown, (a)(2) (and so the (c)(1) offset) uses the smaller amount. (f): fraudulent failure to file:
15% per month, up to 75%. Each is excused by reasonable cause and not willful neglect.

Not modelled: §6651(a)(3), the 1% (levy notice) and 0.25% (installment agreement) rates of §6651(d), (h); the
substantial-valuation and other §6662(b) grounds; §6663 fraud; §6664(c)(2)–(3).
-/

namespace Legal.USTax.TaxCourt

/-! ## §6662 -/

structure AccuracyFacts where
  /-- The IRS asserted the substantial-understatement ground. -/
  assertsSubstantialUnderstatement : Bool := true
  /-- The court found negligence or disregard of rules or regulations (§6662(b)(1), (c)). -/
  negligence : Bool := false
  /-- Part of the understatement attributable to items with substantial authority or adequately disclosed
  (§6662(d)(2)(B)). -/
  authorityOrDisclosure : Int := 0
  /-- Reasonable cause and good faith for the whole underpayment (§6664(c)(1)). -/
  reasonableCause : Bool := false
  /-- Written supervisory approval of the initial determination (§6751(b)(1)). -/
  supervisoryApproval : Bool := true
  /-- The penalty was automatically calculated through electronic means (§6751(b)(2)(B)). -/
  automaticallyCalculated : Bool := false
  /-- The taxpayer claimed a §199A deduction (§6662(d)(1)(C)). -/
  claimed199A : Bool := false
  /-- If the penalty is asserted on only part of the underpayment, that part. -/
  penaltyBase : Option Int := none
  deriving Repr, Inhabited

structure AccuracyOutcome where
  understatement : Int
  /-- after §6662(d)(2)(B) -/
  reducedUnderstatement : Int
  substantial : Bool
  applies : Bool
  base : Int
  penalty : Int
  reasons : List String
  deriving Repr, Inhabited

/-- §6662(d)(1)(A), (C): `u` (understatement after (d)(2)(B)) exceeds the greater of `pct`% of `required` and $5,000.
Exact: "exceeds 10 percent of R" is `10 u > R`. -/
def substantialUnderstatement (u required : Int) (fivePct : Bool) : Bool :=
  u > 5000 && (if fivePct then 20 * u > required else 10 * u > required)

/-- **Test equivalence**: the statute's "exceeds the greater of 10% of the tax required to be shown or $5,000" is the
same as exceeding $5,000 and exceeding 10% of the tax required to be shown — for every understatement and every tax
(including a negative tax, where only the $5,000 matters). -/
theorem substantial_iff (u r : Int) :
    substantialUnderstatement u r false = true ↔ 10 * u > max r 50000 := by
  unfold substantialUnderstatement
  simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.false_eq_true, ↓reduceIte]
  omega

theorem substantial_iff_5pct (u r : Int) :
    substantialUnderstatement u r true = true ↔ 20 * u > max r 100000 := by
  unfold substantialUnderstatement
  simp only [Bool.and_eq_true, decide_eq_true_eq, ↓reduceIte]
  omega

/-- An understatement of $5,000 or less is never substantial, whatever the tax. -/
theorem not_substantial_le_5000 (u r : Int) (b : Bool) (h : u ≤ 5000) : substantialUnderstatement u r b = false := by
  unfold substantialUnderstatement; simp; omega

/-- A larger understatement against the same tax is substantial whenever a smaller one is. -/
theorem substantial_mono (u u' r : Int) (b : Bool) (h : u ≤ u') (hs : substantialUnderstatement u r b = true) :
    substantialUnderstatement u' r b = true := by
  unfold substantialUnderstatement at *
  cases b <;> simp at * <;> omega

/-- **The penalty.** `required` is the tax required to be shown, `shown` the tax shown (both net of refundable
credits); the underpayment is their difference (no prior assessments or rebates). -/
def accuracyPenalty (p : Params) (required shown : Int) (a : AccuracyFacts) : AccuracyOutcome :=
  let u := pos (required - shown)
  let ur := pos (u - pos a.authorityOrDisclosure)
  let subst := a.assertsSubstantialUnderstatement && substantialUnderstatement ur required (a.claimed199A && p.year ≥ 2018)
  let ground := subst || a.negligence
  let approved := a.supervisoryApproval || a.automaticallyCalculated
  let applies := ground && !a.reasonableCause && approved
  let base0 := if a.negligence then u else ur
  let base := match a.penaltyBase with | some b => min (pos b) base0 | none => base0
  let reasons :=
    (if ground then [] else ["no substantial understatement and no negligence"]) ++
    (if a.reasonableCause then ["§6664(c) reasonable cause"] else []) ++
    (if approved then [] else ["§6751(b) no written supervisory approval"])
  ⟨u, ur, subst, applies, base, if applies then pctRound base 2000 else 0, reasons⟩

/-- The penalty is 20% of the underpayment, never more. -/
theorem accuracyPenalty_le (p : Params) (r s : Int) (a : AccuracyFacts) :
    0 ≤ (accuracyPenalty p r s a).penalty ∧
    (accuracyPenalty p r s a).penalty ≤ pctRound (pos (r - s)) 2000 := by
  unfold accuracyPenalty pctRound roundDollar pos
  simp only
  (repeat' split) <;> omega

/-! ## §6651 -/

structure LateFacts where
  /-- Date the return was filed; `none`: no return filed by `asOf`. -/
  filed : Option Date := none
  /-- A valid extension of time to file (§6081). -/
  extension : Bool := false
  /-- Due date found by the court if not the ordinary one (e.g. a disaster postponement). -/
  dueDate : Option Date := none
  /-- Date the tax shown was paid in full; `none`: unpaid at `asOf`. -/
  paid : Option Date := none
  /-- The date the additions are computed to (e.g. the trial or decision date). -/
  asOf : Date := ⟨2026, 1, 1⟩
  /-- Withholding, estimated tax and other credits paid by the due date (§6651(b)(1)–(2)). -/
  timelyPayments : Int := 0
  /-- Reasonable cause and not willful neglect, failure to file / failure to pay. -/
  reasonableCauseFiling : Bool := false
  reasonableCausePayment : Bool := false
  /-- §6651(f): fraudulent failure to file. -/
  fraudulent : Bool := false
  /-- Whether (a)(2) is in issue (on a substitute for return, §6651(g)). -/
  assertsFailureToPay : Bool := true
  deriving Repr, Inhabited

structure LateOutcome where
  monthsLateFiling : Int
  monthsLatePayment : Int
  failureToFile : Int
  failureToPay : Int
  minimumApplied : Bool
  deriving Repr, Inhabited, DecidableEq

/-- **§6651(a)(1), (a)(2), (c)(1), (f).** `required`: the tax required to be shown; `shown`: the tax shown on the
return (or on the §6020(b) substitute). Both before payments. -/
def lateAdditions (p : Params) (required shown : Int) (l : LateFacts) : LateOutcome :=
  let fileDue := l.dueDate.getD (if l.extension then p.extendedDueDate else p.dueDate)
  let payDue := l.dueDate.getD p.dueDate
  let filedOn := l.filed.getD l.asOf
  let mFile := max 0 (min (monthsOrFraction fileDue filedOn) 5)
  let mPay := if l.assertsFailureToPay then max 0 (min (monthsOrFraction payDue (l.paid.getD l.asOf)) 50) else 0
  let net := pos (required - l.timelyPayments)
  -- §6651(c)(2): if the tax required to be shown is less than the tax shown, (a)(2) uses the lower amount
  let netShown := pos (min shown required - l.timelyPayments)
  let ratePerMonth : Int := if l.fraudulent then 1500 else 500
  -- §6651(c)(1): for each month both apply, (a)(1) is reduced by (a)(2); computed exactly, rounded once
  let overlap := min mFile mPay
  let reduced := roundDollar (pos (net * (ratePerMonth * mFile) - netShown * (50 * overlap))) 10000
  let over60 := daysBetween fileDue filedOn > 60
  let floor := if over60 then min p.ftfMinimum net else 0
  let ftf := if l.reasonableCauseFiling then 0 else max reduced floor
  let ftp := if l.reasonableCausePayment then 0 else pctRound netShown (50 * mPay)
  ⟨mFile, mPay, ftf, ftp, !l.reasonableCauseFiling && over60 && floor > reduced⟩

/-- Failure to file never exceeds 25% (75% if fraudulent) of the net amount required to be shown, or else the
minimum addition. -/
theorem lateFiling_le (p : Params) (r s : Int) (l : LateFacts) :
    (lateAdditions p r s l).failureToFile ≤
      max (pctRound (pos (r - l.timelyPayments)) (if l.fraudulent then 7500 else 2500))
        (min p.ftfMinimum (pos (r - l.timelyPayments))) := by
  unfold lateAdditions
  simp only
  generalize hm : max 0 (min (monthsOrFraction _ _) 5) = m
  have h0 : 0 ≤ m ∧ m ≤ 5 := by omega
  generalize hp : (if l.assertsFailureToPay = true then _ else (0 : Int)) = mp
  have hmp : 0 ≤ mp := by rw [← hp]; split <;> omega
  have hred : 0 ≤ pos (min s r - l.timelyPayments) * (50 * min m mp) :=
    Int.mul_nonneg (pos_nonneg _) (by omega)
  generalize pos (min s r - l.timelyPayments) * (50 * min m mp) = red at hred
  generalize daysBetween _ _ = dd
  have hn := pos_nonneg (r - l.timelyPayments)
  generalize pos (r - l.timelyPayments) = n at hn
  have : m = 0 ∨ m = 1 ∨ m = 2 ∨ m = 3 ∨ m = 4 ∨ m = 5 := by omega
  rcases this with h | h | h | h | h | h <;> subst h <;>
    cases l.fraudulent <;> cases l.reasonableCauseFiling <;> simp only [Bool.false_eq_true, ↓reduceIte] <;>
    (try simp only [pctRound, roundDollar, pos]) <;> (repeat' split) <;> omega

/-! ## Tests -/

section
private def py (y : Nat) : Params := (params? y).getD default

-- §6662: understatement $6,000 on required tax $20,000: exceeds $5,000 and 10% ($2,000): substantial; 20% = $1,200.
#guard (accuracyPenalty (py 2019) 20000 14000 {}).penalty = 1200
-- understatement $4,000: not substantial, no negligence: none.
#guard (accuracyPenalty (py 2019) 20000 16000 {}).penalty = 0
-- ... but negligence found: $800.
#guard (accuracyPenalty (py 2019) 20000 16000 { negligence := true }).penalty = 800
-- understatement $6,000 on required tax $70,000: 10% is $7,000: not substantial.
#guard (accuracyPenalty (py 2019) 70000 64000 {}).substantial = false
-- ... with a §199A deduction (5%: $3,500): substantial.
#guard (accuracyPenalty (py 2019) 70000 64000 { claimed199A := true }).substantial = true
-- ... but not in 2017 (no §199A).
#guard (accuracyPenalty (py 2017) 70000 64000 { claimed199A := true }).substantial = false
-- An EIC over-claim: required −$1,000 (refund due), shown −$7,000: understatement $6,000: substantial.
#guard (accuracyPenalty (py 2021) (-1000) (-7000) {}).penalty = 1200
-- No supervisory approval: no penalty.
#guard (accuracyPenalty (py 2021) 20000 14000 { supervisoryApproval := false }).penalty = 0

-- §6651, tax year 2018 (due 15 Apr 2019): required $10,000, nothing paid, return filed 20 Aug 2019 (5 months):
-- (a)(1) 25% less the (c)(1) offset of 5 × 0.5% = $2,250; (a)(2) to 20 Aug: 5 months × 0.5% = $250.
#guard lateAdditions (py 2018) 10000 10000 { filed := some ⟨2019, 8, 20⟩, paid := some ⟨2019, 8, 20⟩ } =
  ⟨5, 5, 2250, 250, false⟩
-- Small tax filed 3 months late (more than 60 days): the $215 minimum (or 100% of a $150 tax).
#guard (lateAdditions (py 2018) 1000 1000 { filed := some ⟨2019, 7, 1⟩, paid := some ⟨2019, 4, 15⟩ }).failureToFile = 215
#guard (lateAdditions (py 2018) 150 150 { filed := some ⟨2019, 7, 1⟩, paid := some ⟨2019, 4, 15⟩ }).failureToFile = 150
-- 2019 returns were due 15 Jul 2020 (Notice 2020-23): filed 1 Jul 2020 is timely.
#guard (lateAdditions (py 2019) 5000 5000 { filed := some ⟨2020, 7, 1⟩, paid := some ⟨2020, 7, 1⟩ }).failureToFile = 0
-- With an extension to 15 Oct 2019, a return filed 1 Oct 2019 is timely, but payment was due 15 Apr: 6 months of (a)(2).
#guard lateAdditions (py 2018) 4000 4000 { filed := some ⟨2019, 10, 1⟩, extension := true, paid := some ⟨2019, 10, 1⟩ } =
  ⟨0, 6, 0, 120, false⟩
-- §6651(c)(2): an SFR showing $5,000 when only $1,000 is required: (a)(2) on $1,000 (10 months × 0.5% = $50), and the
-- (c)(1) offset on $1,000 too: (a)(1) 25% × $1,000 − 5 × 0.5% × $1,000 = $225.
#guard lateAdditions (py 2018) 1000 5000 { asOf := ⟨2020, 2, 1⟩ } = ⟨5, 10, 225, 50, false⟩
-- Withholding covers the tax: no addition.
#guard (lateAdditions (py 2022) 3000 3000 { filed := some ⟨2024, 1, 1⟩, timelyPayments := 3500 }).failureToFile = 0
end

end Legal.USTax.TaxCourt
