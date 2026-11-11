import LegalProofs.USTax.TaxCourt.Dependents

/-!
# Filing status: §1, §2(a) surviving spouse, §2(b) head of household, §7703 marital status (2012–2024)

None of §§2 and 7703 changed between 2016 and 2024 (the TCJA left them alone; §151(d)(5)(B) keeps the "entitled to a
deduction under section 151" tests working while the exemption amount is zero).

`determineStatus` takes the status claimed on the return and the court's findings and returns the status the law
allows: the claimed one if it is available, otherwise the most favourable one available (surviving spouse, then head
of household, then single; or married filing separately for a married taxpayer who did not file jointly).
-/

namespace Legal.USTax.TaxCourt

/-- The court's findings on marital status and the household. -/
structure StatusFacts where
  /-- Married at the close of the year (§7703(a)(1)); a spouse who died during the year counts as married. -/
  marriedAtYearEnd : Bool := false
  /-- Legally separated under a decree of divorce or of separate maintenance (§7703(a)(2)). -/
  legallySeparated : Bool := false
  /-- The return is a joint return (§6013). -/
  jointReturn : Bool := false
  /-- The spouse was not a member of the taxpayer's household during the last six months of the year (§7703(b)(3)). -/
  spouseAbsentLastSixMonths : Bool := false
  /-- The taxpayer furnished over one-half of the cost of maintaining the household (§2(b)(1), §7703(b)(2)). -/
  paidOverHalfHouseholdCost : Bool := false
  /-- Year the spouse died, if any (§2(a)(1)(A)). -/
  spouseDeathYear : Option Nat := none
  /-- Remarried before the close of the year (§2(a)(2)(A)). -/
  remarried : Bool := false
  /-- Could have filed jointly with the deceased spouse for the year of death (§2(a)(2)(B)). -/
  couldFileJointlyInDeathYear : Bool := true
  /-- Nonresident alien at any time during the year (§2(b)(3)(A); §2(a)(2)(B)). -/
  nonresidentAlien : Bool := false
  /-- The taxpayer can be claimed as a dependent by another taxpayer (§152(b)(1)). -/
  canBeClaimedAsDependent : Bool := false
  deriving Repr, Inhabited

/-- §7703(b)(1): the child whose home makes a married taxpayer "not married": a son, stepson, daughter, stepdaughter
or eligible foster child (§152(f)(1)) whose principal place of abode is the household for more than half the year,
for whom the taxpayer is entitled to a §151 deduction "or would be so entitled but for section 152(e)". -/
def childFor7703 (p : Params) (st : StatusFacts) (x : PersonFacts) : Bool :=
  (x.relationship == .child || x.relationship == .stepchild || x.relationship == .fosterChild) &&
    x.abodeMoreThanHalf p.year &&
    (isDependent p st.canBeClaimedAsDependent x ||
      (x.releasedToOtherParent && isDependent p st.canBeClaimedAsDependent { x with releasedToOtherParent := false }))

/-- §7703(a): married for the year (determined at year end or at the spouse's death), unless legally separated. -/
def isMarried (st : StatusFacts) : Bool := st.marriedAtYearEnd && !st.legallySeparated

/-- §7703(b): a married individual filing separately who keeps up a home for a child and whose spouse was away the
last six months "shall not be considered as married". -/
def consideredUnmarried (p : Params) (st : StatusFacts) (deps : List PersonFacts) : Bool :=
  isMarried st && !st.jointReturn && st.paidOverHalfHouseholdCost && st.spouseAbsentLastSixMonths &&
    deps.any (childFor7703 p st)

/-- §2(b)(1)(A)–(B): a person whose presence lets the taxpayer be a head of household.
* (A)(i) a qualifying child (§152(c) "determined without regard to section 152(e)") who lives in the household more
  than half the year — unless married at year end and not the taxpayer's dependent;
* (A)(ii) any other dependent living there more than half the year, if the taxpayer is entitled to a §151
  deduction for him — but not a dependent only by §152(d)(2)(H) or §152(d)(3) (§2(b)(3)(B));
* (B) a father or mother who is the taxpayer's dependent and whose household (anywhere) the taxpayer maintains. -/
def hohQualifyingPerson (p : Params) (st : StatusFacts) (x : PersonFacts) : Bool :=
  let qc := qualifyingChild p.year x { use152e := false }
  let dep := isDependent p st.canBeClaimedAsDependent x
  let aI := qc && (!x.married || dep)
  let aII := dep && x.abodeMoreThanHalf p.year && !qc &&
    !(x.relationship == .unrelated) && !x.viaMultipleSupportAgreement
  let b := x.relationship == .parent && dep && x.taxpayerMaintainsParentsHousehold && !x.viaMultipleSupportAgreement
  aI || aII || b

/-- §2(a): surviving spouse — the spouse died in either of the two preceding years, the taxpayer has not remarried,
and maintains a home that is for the whole year the principal place of abode of a son, stepson, daughter or
stepdaughter for whom the taxpayer is entitled to a §151 deduction, paying over half its cost. -/
def isSurvivingSpouse (p : Params) (st : StatusFacts) (deps : List PersonFacts) : Bool :=
  match st.spouseDeathYear with
  | none => false
  | some d =>
    (d + 1 == p.year || d + 2 == p.year) && !st.remarried && st.couldFileJointlyInDeathYear &&
      !st.marriedAtYearEnd && st.paidOverHalfHouseholdCost &&
      deps.any fun x => (x.relationship == .child || x.relationship == .stepchild) && x.livedWithWholeYear &&
        isDependent p st.canBeClaimedAsDependent x

/-- §2(b): head of household — unmarried at year end (or "not married" under §7703(b)), not a surviving spouse, not a
nonresident alien, paying over half the cost of a household that is home to a qualifying person. -/
def isHeadOfHousehold (p : Params) (st : StatusFacts) (deps : List PersonFacts) : Bool :=
  (!isMarried st || consideredUnmarried p st deps) && !isSurvivingSpouse p st deps && !st.nonresidentAlien &&
    st.paidOverHalfHouseholdCost && deps.any (hohQualifyingPerson p st)

/-- The statuses the law allows on these facts. -/
def allowedStatuses (p : Params) (st : StatusFacts) (deps : List PersonFacts) : List Filing :=
  if isMarried st && !consideredUnmarried p st deps then
    if st.jointReturn then [.mfj] else [.mfs]
  else
    (if isSurvivingSpouse p st deps then [.qss] else []) ++
    (if isHeadOfHousehold p st deps then [.hoh] else []) ++
    (if isMarried st then [.mfs] else [.single])

/-- The status that governs: the one claimed if the law allows it, otherwise the first (most favourable) allowed. -/
def determineStatus (p : Params) (claimed : Filing) (st : StatusFacts) (deps : List PersonFacts) : Filing :=
  let allowed := allowedStatuses p st deps
  if allowed.contains claimed then claimed else allowed.headD .single

theorem allowedStatuses_ne_nil (p : Params) (st : StatusFacts) (deps : List PersonFacts) :
    allowedStatuses p st deps ≠ [] := by
  unfold allowedStatuses
  split
  · split <;> simp
  · split <;> split <;> split <;> simp

/-- **The status determined is always one the law allows.** -/
theorem determineStatus_allowed (p : Params) (claimed : Filing) (st : StatusFacts) (deps : List PersonFacts) :
    determineStatus p claimed st deps ∈ allowedStatuses p st deps := by
  unfold determineStatus
  simp only
  split
  · rename_i h; simpa using h
  · have := allowedStatuses_ne_nil p st deps
    cases hl : allowedStatuses p st deps with
    | nil => exact absurd hl this
    | cons a l => simp

/-- A married taxpayer who files separately and is not "considered unmarried" can only be married filing separately
(a claim of head of household or single fails). -/
theorem married_separate_only (p : Params) (st : StatusFacts) (deps : List PersonFacts) (c : Filing)
    (hm : isMarried st = true) (hj : st.jointReturn = false) (hc : consideredUnmarried p st deps = false) :
    determineStatus p c st deps = .mfs := by
  unfold determineStatus allowedStatuses
  simp [hm, hj, hc]

/-! ## Tests (Pub. 501 examples; the rules are the same in every edition 2012–2024) -/

section
private def p19 : Params := (params? 2019).getD default
private def kid : PersonFacts := { name := "child", age := 8, daysWithTaxpayer := 365, livedWithWholeYear := true }

-- Unmarried parent paying the household costs, child lives with her all year: head of household.
#guard determineStatus p19 .hoh { paidOverHalfHouseholdCost := true } [kid] = .hoh
-- Same, but she did not pay over half the cost: single.
#guard determineStatus p19 .hoh {} [kid] = .single
-- Married at year end, spouse in the home in the last six months, filed separately claiming HoH: separate.
#guard determineStatus p19 .hoh { marriedAtYearEnd := true, paidOverHalfHouseholdCost := true } [kid] = .mfs
-- Pub. 501 "Considered unmarried": spouse left in March, taxpayer kept up the home for the child: HoH.
private def apart : StatusFacts :=
  { marriedAtYearEnd := true, paidOverHalfHouseholdCost := true, spouseAbsentLastSixMonths := true }
#guard determineStatus p19 .hoh apart [kid] = .hoh
-- Pub. 501 qualifying-surviving-spouse example: spouse died in 2017, child lived with the taxpayer all of 2019.
#guard determineStatus p19 .qss { spouseDeathYear := some 2017, paidOverHalfHouseholdCost := true } [kid] = .qss
-- ... in 2020 (third year after death) only HoH remains.
#guard determineStatus ((params? 2020).getD default) .qss
    { spouseDeathYear := some 2017, paidOverHalfHouseholdCost := true } [kid] = .hoh
-- Pub. 501 Table 4: a girlfriend who is a dependent only as a household member does not make the taxpayer HoH.
#guard determineStatus p19 .hoh { paidOverHalfHouseholdCost := true }
    [{ relationship := .unrelated, age := 30, youngerThanTaxpayer := false, livedWithWholeYear := true,
       daysWithTaxpayer := 365, taxpayerProvidedOverHalfSupport := true }] = .single
-- Pub. 501 Table 4: a dependent mother living in her own home the taxpayer pays for qualifies (§2(b)(1)(B)).
#guard determineStatus p19 .hoh { paidOverHalfHouseholdCost := true }
    [{ relationship := .parent, age := 70, youngerThanTaxpayer := false, taxpayerProvidedOverHalfSupport := true,
       taxpayerMaintainsParentsHousehold := true, grossIncome := 3000 }] = .hoh
-- A custodial parent who released the exemption under §152(e) is still HoH (determined without §152(e)).
#guard determineStatus p19 .hoh { paidOverHalfHouseholdCost := true } [{ kid with releasedToOtherParent := true }] = .hoh
-- The noncustodial parent who received the release is not.
#guard determineStatus p19 .hoh { paidOverHalfHouseholdCost := true }
    [{ kid with daysWithTaxpayer := 60, livedWithWholeYear := false, releasedUnder152e := true }] = .single
end

end Legal.USTax.TaxCourt
