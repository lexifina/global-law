import TaxCode.Individual.D.ChildTaxCredit
import TaxCode.Individual.D.EarnedIncome
import TaxCode.Individual.D.DependentCare
import TaxCode.Individual.D.Education
import TaxCode.Individual.D.Saver
import TaxCode.Individual.D.PremiumTaxCredit

/-!
# Ordering credits against tax (Form 1040 lines 19–21, 27–31), tax year 2025

§26(a): "The aggregate amount of credits allowed by this subpart [A: nonrefundable personal credits] ... shall not
exceed" regular tax (less the foreign tax credit) plus the AMT. The statute fixes only the aggregate; the order in
which the individual credits use up the limit comes from the forms, and it matters for the CTC because the unused
part of the CTC is what becomes refundable (§24(d)(1)).

The forms' order (2025):
1. foreign tax credit (Schedule 3 line 1; the CDCC's Credit Limit Worksheet subtracts it);
2. child and dependent care credit (Schedule 3 line 2; Form 2441 Credit Limit Worksheet: Form 1040 line 18 minus
   Schedule 3 line 1);
3. education credits (Schedule 3 line 3; Form 8863 Credit Limit Worksheet: line 18 minus Schedule 3 lines 1, 2,
   6d, 6l);
4. saver's credit (Schedule 3 line 4);
5. CTC and ODC (Form 1040 line 19; Schedule 8812 Credit Limit Worksheet A: line 18 minus Schedule 3 lines 1, 2,
   3, 4, 5b, 6d, 6f, 6l, 6m).
So although the CTC sits on line 19, ABOVE the Schedule 3 total on line 20, it is computed LAST.
Refundable (lines 27–31): EIC (27), ACTC (28), AOTC refundable part (29), net PTC (Schedule 3 line 9 → 31). Excess
advance PTC is a tax (Schedule 2 line 1a), returned separately.
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- Credits before the §26(a) limit. -/
structure CreditInputs where
  foreignTax : Int := 0     -- §27 (Schedule 3 line 1), outside this group; an input
  cdcc : Int := 0
  educationNonref : Int := 0
  saver : Int := 0
  ctc : Int := 0            -- §24 after the phase-out (Schedule 8812 line 12)
  actcCap : Int := 0        -- §24(d)(1)(A) with (h)(5) (statute) — or n × $1,700 for the form's version
  actcX : Int := 0          -- §24(d)(1)(B)
  eic : Int := 0
  aotcRefundable : Int := 0
  ptcNet : Int := 0         -- credit minus advance payments, if positive (§36B(f)(1))
  deriving Repr

structure CreditResult where
  foreignTax : Int
  cdcc : Int
  education : Int
  saver : Int
  ctcUsed : Int
  actc : Int
  nonrefundable : Int       -- Form 1040 line 21
  refundable : Int          -- lines 27 + 28 + 29 + 31 (this group's)
  deriving Repr, DecidableEq

/-- One nonrefundable credit against the tax left: the amount used. -/
def used (left credit : Int) : Int := min (pos credit) (pos left)

/-- Several nonrefundable credits in order: the total used. -/
def useAll : Int → List Int → Int
  | _, [] => 0
  | l, c :: cs => used l c + useAll (l - used l c) cs

def othersOf (c : CreditInputs) : List Int := [c.foreignTax, c.cdcc, c.educationNonref, c.saver]

/-- The forms' order: foreign tax credit, CDCC, education, saver's, then CTC/ODC. -/
def applyCreditsDetail (tax : Int) (c : CreditInputs) : CreditResult :=
  let f := used tax c.foreignTax
  let d := used (tax - f) c.cdcc
  let e := used (tax - f - d) c.educationNonref
  let s := used (tax - f - d - e) c.saver
  let o := useAll tax (othersOf c)
  let k := used (tax - o) c.ctc
  let actc := pos (min c.actcCap (min c.actcX (pos c.ctc - k)))
  { foreignTax := f, cdcc := d, education := e, saver := s, ctcUsed := k, actc := actc,
    nonrefundable := o + k,
    refundable := actc + pos c.eic + pos c.aotcRefundable + pos c.ptcNet }

/-- `applyCredits tax c = (nonrefundable credits used, refundable credits)`. -/
def applyCredits (tax : Int) (c : CreditInputs) : Int × Int :=
  ((applyCreditsDetail tax c).nonrefundable, (applyCreditsDetail tax c).refundable)

/-- The other order (CTC first, as the line numbers would suggest), for comparison. -/
def applyCreditsCtcFirst (tax : Int) (c : CreditInputs) : Int × Int :=
  let k := used tax c.ctc
  let o := useAll (tax - k) (othersOf c)
  let actc := pos (min c.actcCap (min c.actcX (pos c.ctc - k)))
  (o + k, actc + pos c.eic + pos c.aotcRefundable + pos c.ptcNet)

/-- Applying credits one after another uses exactly the lesser of the tax and their sum. -/
theorem useAll_eq (l : Int) (cs : List Int) : useAll l cs = min (pos l) (cs.map pos).sum := by
  induction cs generalizing l with
  | nil => simp only [useAll, List.map_nil, List.sum_nil, pos]; omega
  | cons c cs ih =>
    have hs : 0 ≤ (cs.map pos).sum := by
      clear ih; induction cs with
      | nil => simp
      | cons x xs ih2 => simp only [List.map_cons, List.sum_cons]; have := pos_nonneg x; omega
    simp only [useAll, ih, List.map_cons, List.sum_cons, used, pos] at *
    omega

/-! ## Everything from one household -/

/-- What this group takes as given: AGI and the MAGI variants (computed by other groups), earned income, tax before
credits (Form 1040 line 18), and facts `Household` does not record. -/
structure CreditContext where
  agi : Int
  magiCtc : Int              -- §24(b)(1): AGI + §§911, 931, 933 exclusions
  magiEducation : Int        -- §25A(d)(2): same additions
  agiSaver : Int             -- §25B(e): AGI without §§911, 931, 933
  householdIncome : Int      -- §36B(d)(2)
  earnedIncome : Int         -- §32(c)(2) (also §24(d))
  earnedHead : Int           -- §21(d) per spouse
  earnedSpouse : Int
  taxBeforeCredits : Int     -- Form 1040 line 18
  taxpayerSSN : Bool := true -- §24(h)(7)(A)(i)
  socialSecurityTaxes : Int := 0  -- §24(d)(2)
  foreignTaxCredit : Int := 0
  dependentCareExcluded : Int := 0  -- §129
  llcExpenses : Int := 0
  saverPeople : List (Int × Int) := []  -- (contributions, distributions) per eligible individual
  aptc : Int := 0
  kiddieTax : Bool := false

/-- All the group's credits for a household, filled into `Return`'s credit fields. -/
def credits2025 (h : Household) (x : CreditContext) : Return :=
  let counts := householdCtcCounts h x.taxpayerSSN
  let ctc := ctcAfterPhaseout h.filing x.magiCtc counts
  let eic := eic2025 h x.earnedIncome x.agi
  let cd := cdcc2025 h.filing (careIndividuals h) h.childCareExpenses x.dependentCareExcluded x.earnedHead
    x.earnedSpouse x.agi
  let edu := education2025 h.filing x.magiEducation h.qualifiedTuition x.llcExpenses x.kiddieTax
  let sv := saverCredit h.filing x.agiSaver x.saverPeople
  let size := h.persons + h.dependents.length
  -- §36B(c)(1)(C): a married taxpayer is an applicable taxpayer only on a joint return (the Treas. Reg.
  -- §1.36B-2(b)(2)(ii) abuse/abandonment relief is not modelled); §36B(c)(1)(D): no credit to an individual for
  -- whom a §151 deduction is allowable to another taxpayer.
  let ptc := if h.filing = .mfs ∨ h.canBeClaimedAsDependent then 0 else
    ptcStatute2025 (fpl2024 size) h.benchmarkPremium h.marketplacePremium x.householdIncome
  let r := applyCreditsDetail x.taxBeforeCredits
    { foreignTax := x.foreignTaxCredit, cdcc := cd, educationNonref := edu.aotcNonrefundable + edu.llc,
      saver := sv, ctc := ctc, actcCap := actcCapA h.filing x.magiCtc counts,
      actcX := actcEarnedAmount counts x.earnedIncome x.socialSecurityTaxes eic,
      eic := eic, aotcRefundable := edu.aotcRefundable, ptcNet := pos (ptc - x.aptc) }
  let childPart := min r.ctcUsed (pos (ctcPerChild * counts.children - ctcReduction h.filing x.magiCtc))
  { nonrefundableCredits := r.nonrefundable, refundableCredits := r.refundable,
    ctc := childPart, odc := r.ctcUsed - childPart, actc := r.actc, eitc := eic, cdcc := r.cdcc,
    aotcNonref := min r.education edu.aotcNonrefundable, aotcRef := edu.aotcRefundable,
    llc := r.education - min r.education edu.aotcNonrefundable, saver := r.saver, ptc := ptc }

/-! ## Tests -/

-- A family the size of Form 8962's examples is not given numerically; these check the mechanics.
-- $3,000 of tax, $600 CDCC, $4,400 CTC for two children, $6,000 earned-income amount: CDCC first ($600), then
-- $2,400 of CTC; $2,000 of CTC unused, refundable up to the $3,400 cap: ACTC $2,000.
#guard applyCreditsDetail 3000 { cdcc := 600, ctc := 4400, actcCap := 3400, actcX := 6000 } =
  { foreignTax := 0, cdcc := 600, education := 0, saver := 0, ctcUsed := 2400, actc := 2000,
    nonrefundable := 3000, refundable := 2000 }
#guard applyCredits 0 { ctc := 2200, actcCap := 1700, actcX := 1000, eic := 3000 } = (0, 4000)
-- End to end (consistency, not an IRS example): head of household, children 5 and 8, wages $30,000, $4,000 of
-- child care, $1,000 of tax before credits. CDCC 27% × $4,000 = $1,080 uses the whole $1,000 of tax, so none of
-- the $4,400 CTC is used and $3,400 (2 × $1,700) is refundable; EIC: Pub. 596 (2025) row $30,000–$30,050, single/
-- HOH, 2 children, "5,746".
def exampleHousehold : Household :=
  { filing := .hoh, head := ⟨34, false⟩, dependents := [{ age := 5 }, { age := 8 }], wages := 30000,
    childCareExpenses := 4000 }
def exampleContext : CreditContext :=
  { agi := 30000, magiCtc := 30000, magiEducation := 30000, agiSaver := 30000, householdIncome := 30000,
    earnedIncome := 30000, earnedHead := 30000, earnedSpouse := 0, taxBeforeCredits := 1000 }
#guard (credits2025 exampleHousehold exampleContext).cdcc = 1000
#guard (credits2025 exampleHousehold exampleContext).actc = 3400
#guard (credits2025 exampleHousehold exampleContext).eitc = 5746
#guard (credits2025 exampleHousehold exampleContext).nonrefundableCredits = 1000
#guard (credits2025 exampleHousehold exampleContext).refundableCredits = 9146
-- (Review) §36B(c)(1)(C)/(D): no PTC on a separate return or for someone another taxpayer can claim.
def ptcSeparateReturn : Household :=
  { filing := .mfs, head := ⟨40, false⟩, spouse := some ⟨40, false⟩, benchmarkPremium := 8000,
    marketplacePremium := 8000 }
def ptcSingleReturn : Household :=
  { filing := .single, head := ⟨40, false⟩, benchmarkPremium := 8000, marketplacePremium := 8000 }
#guard (credits2025 ptcSeparateReturn exampleContext).ptc = 0
#guard (credits2025 ptcSingleReturn exampleContext).ptc > 0
#guard (credits2025 { ptcSingleReturn with canBeClaimedAsDependent := true } exampleContext).ptc = 0

/-! ## Properties -/

/-- **§26(a) holds.** The nonrefundable credits used are exactly the lesser of the tax and the sum of the
(non-negative parts of the) credits: never more than the tax, never below zero. -/
theorem nonrefundable_eq_min (tax : Int) (c : CreditInputs) :
    (applyCredits tax c).1 =
      min (pos tax) (pos c.foreignTax + pos c.cdcc + pos c.educationNonref + pos c.saver + pos c.ctc) := by
  simp only [applyCredits, applyCreditsDetail, useAll_eq, othersOf, List.map_cons, List.map_nil, List.sum_cons,
    List.sum_nil, used, pos]
  omega

theorem nonrefundable_same_either_order (tax : Int) (c : CreditInputs) :
    (applyCredits tax c).1 = (applyCreditsCtcFirst tax c).1 := by
  simp only [applyCredits, applyCreditsDetail, applyCreditsCtcFirst, useAll_eq, othersOf, List.map_cons,
    List.map_nil, List.sum_cons, List.sum_nil, used, pos]
  omega

/-- The forms' order (CTC last) never gives a smaller refund than the CTC-first variant, which counts only the unused
CTC in §24(d)(1)(B). (Review: the statute's (B) counts all unused subpart A credits and so does not depend on order;
see `forms_order_matches_statute`. The CTC-first variant is a misreading, not a lawful alternative order.) -/
theorem forms_order_dominates (tax : Int) (c : CreditInputs) :
    (applyCreditsCtcFirst tax c).2 ≤ (applyCredits tax c).2 := by
  have hS : 0 ≤ ((othersOf c).map pos).sum := by
    simp only [othersOf, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil]
    have := pos_nonneg c.foreignTax; have := pos_nonneg c.cdcc; have := pos_nonneg c.educationNonref
    have := pos_nonneg c.saver; omega
  have hC := pos_nonneg c.ctc
  simp only [applyCredits, applyCreditsDetail, applyCreditsCtcFirst, useAll_eq, used]
  generalize ((othersOf c).map pos).sum = S at *
  generalize pos c.ctc = C at *
  generalize pos c.eic = a
  generalize pos c.aotcRefundable = b
  generalize pos c.ptcNet = d
  generalize c.actcCap = A
  generalize c.actcX = X
  unfold pos
  omega

theorem forms_order_strictly_better :
    applyCreditsCtcFirst 2200 { cdcc := 1000, ctc := 2200, actcCap := 1700, actcX := 5000 } = (2200, 0) ∧
    applyCredits 2200 { cdcc := 1000, ctc := 2200, actcCap := 1700, actcX := 5000 } = (2200, 1000) := by
  decide +kernel

/-- The refundable CTC never exceeds the cap given (statute: `actcCapA`, at most $1,700 per child), and the CTC used
plus the refundable CTC never exceed the CTC. -/
theorem actc_le_unused (tax : Int) (c : CreditInputs) :
    (applyCreditsDetail tax c).actc ≤ pos c.actcCap ∧
    (applyCreditsDetail tax c).ctcUsed + (applyCreditsDetail tax c).actc ≤ pos c.ctc := by
  simp only [applyCreditsDetail, useAll_eq, othersOf, List.map_cons, List.map_nil, List.sum_cons, List.sum_nil,
    used, pos]
  omega

/-- (Review) **The forms' order implements the statute, which is order-free.** §24(d)(1)(B) counts the increase in the
AGGREGATE subpart A credits, i.e. every credit left unused, not only the CTC. Applying the CTC last (and given the
(d)(1)(A) cap is at most the CTC, as `actcCapA` is) gives exactly min(cap, earned-income amount, all unused
CDCC + education + saver's + CTC credits), whatever order the statute's credits are taken in. So
`applyCreditsCtcFirst`, which counts only the unused CTC, is not a reading of the statute. -/
theorem forms_order_matches_statute (tax : Int) (c : CreditInputs) (hA0 : 0 ≤ c.actcCap)
    (hA : c.actcCap ≤ pos c.ctc) :
    let L := pos tax - min (pos c.foreignTax) (pos tax)
    let T := pos c.cdcc + pos c.educationNonref + pos c.saver + pos c.ctc
    (applyCreditsDetail tax c).actc = min c.actcCap (min (pos c.actcX) (T - min L T)) := by
  intro L T
  simp only [L, T, applyCreditsDetail, useAll_eq, othersOf, List.map_cons, List.map_nil, List.sum_cons,
    List.sum_nil, used]
  have := pos_nonneg c.foreignTax; have := pos_nonneg c.cdcc; have := pos_nonneg c.educationNonref
  have := pos_nonneg c.saver; have := pos_nonneg c.ctc; have := pos_nonneg tax
  generalize pos c.foreignTax = a at *
  generalize pos c.cdcc = b at *
  generalize pos c.educationNonref = d at *
  generalize pos c.saver = g at *
  generalize pos c.ctc = C at *
  unfold pos
  omega

end TaxCode.Individual.D
