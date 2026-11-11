import LegalProofs.USTax.TaxCourt.Params

/-!
# §152 dependents: qualifying child, qualifying relative, the tie-breaker (tax years 2016–2024)

§152 was not amended in substance between 2016 and 2024. The 2018–2025 suspension of the exemption amount
(§151(d)(5)(A)) does not touch the definition of a dependent: §151(d)(5)(B) keeps "allowed a deduction under §151"
references working, and Notice 2018-70 keeps an indexed exemption amount for the §152(d)(1)(B) gross-income test
(`Params.exemption152d`).

One `PersonFacts` record holds what a court finds about one person the taxpayer claims (child, relative, household
member). `qualifyingChild`, `qualifyingRelative` and `isDependent` read it; the credit and filing-status modules read
the same record for their own variants (§32(c)(3) drops the support test and §152(e); §2(b) drops §152(e)).
-/

namespace Legal.USTax.TaxCourt

/-- How the person is related to the taxpayer (§152(c)(2), (d)(2), (f)). -/
inductive Relationship where
  /-- son or daughter, including a legally adopted child or one placed for adoption (§152(f)(1)(A)(i), (B)) -/
  | child
  /-- stepson or stepdaughter -/
  | stepchild
  /-- eligible foster child: placed by an authorized agency or by court order (§152(f)(1)(C)) -/
  | fosterChild
  /-- grandchild or other descendant of a child -/
  | descendantOfChild
  /-- brother or sister, including half (§152(f)(4)) -/
  | sibling
  /-- stepbrother or stepsister -/
  | stepsibling
  /-- son or daughter of a brother or sister (niece, nephew) -/
  | siblingsChild
  /-- any other descendant of a sibling or step-sibling (grand-niece; a step-sibling's child): §152(c)(2)(B) only -/
  | otherSiblingDescendant
  /-- father or mother, or an ancestor of either (§152(d)(2)(C)) -/
  | parent
  /-- stepfather or stepmother -/
  | stepparent
  /-- brother or sister of the father or mother (§152(d)(2)(F)) -/
  | auntUncle
  /-- son-, daughter-, father-, mother-, brother- or sister-in-law (§152(d)(2)(G)) -/
  | inLaw
  /-- unrelated: a dependent only as a member of the household (§152(d)(2)(H)) -/
  | unrelated
  deriving DecidableEq, Repr, Inhabited

/-- §152(c)(2): the qualifying-child relationships. -/
def Relationship.qcOk : Relationship → Bool
  | .child | .stepchild | .fosterChild | .descendantOfChild | .sibling | .stepsibling | .siblingsChild
  | .otherSiblingDescendant => true
  | _ => false

/-- §152(d)(2)(A)–(G): the qualifying-relative relationships other than the household-member rule. -/
def Relationship.qrOk : Relationship → Bool
  | .child | .stepchild | .fosterChild | .descendantOfChild | .sibling | .stepsibling | .siblingsChild
  | .parent | .stepparent | .auntUncle | .inLaw => true
  | _ => false

/-- What a court finds about one person. Every field has a default, so an encoding gives only what the opinion
finds; the defaults are the ordinary case (a U.S. citizen with an SSN who files no joint return). -/
structure PersonFacts where
  name : String := ""
  relationship : Relationship := .child
  /-- Age at the close of the calendar year (§152(c)(3)(A): "has not attained the age of 19 as of the close of the
  calendar year"). -/
  age : Nat := 0
  /-- Younger than the taxpayer (or, on a joint return, than either spouse): §152(c)(3)(A). -/
  youngerThanTaxpayer : Bool := true
  /-- A student (§152(f)(2): full-time at an educational organization during some part of each of 5 months). -/
  student : Bool := false
  /-- Permanently and totally disabled at any time during the year (§152(c)(3)(B), §22(e)(3)). -/
  disabled : Bool := false
  /-- Days during the year the person had the same principal place of abode as the taxpayer (temporary absences
  count as time at home, Reg. §1.152-4(c)). Used when `livedWithMoreThanHalfYear` is not given. -/
  daysWithTaxpayer : Int := 0
  /-- The court's finding that the person lived with the taxpayer for more than one-half of the year (overrides
  `daysWithTaxpayer`). A child born or who died during the year and lived with the taxpayer the whole time alive
  meets it (Reg. §1.152-4(c)). -/
  livedWithMoreThanHalfYear : Option Bool := none
  /-- Lived with the taxpayer the whole year (or the whole part of it the person was alive): §2(a) surviving
  spouse, §152(d)(2)(H) member of household. -/
  livedWithWholeYear : Bool := false
  /-- The person provided over one-half of his or her own support (§152(c)(1)(D)). -/
  providedOverHalfOwnSupport : Bool := false
  /-- The taxpayer provided over one-half of the person's support (§152(d)(1)(C)), or is the designated claimant
  under a multiple support agreement (§152(d)(3)). -/
  taxpayerProvidedOverHalfSupport : Bool := false
  /-- Support satisfied only through a multiple support agreement (§152(d)(3)); relevant to §2(b)(3)(B). -/
  viaMultipleSupportAgreement : Bool := false
  /-- Gross income of the person for the year (§152(d)(1)(B)). -/
  grossIncome : Int := 0
  /-- Married at the close of the year. -/
  married : Bool := false
  /-- Filed a joint return for the year other than only to claim a refund (§152(b)(2), (c)(1)(E)). -/
  filedJointReturn : Bool := false
  /-- U.S. citizen or national, or U.S. resident (§152(b)(3)(A), §24(c)(2)). -/
  usCitizenOrResident : Bool := true
  /-- Resident of Canada or Mexico (enough for §152(b)(3)(A), not for §24(c)(2)). -/
  residentOfContiguousCountry : Bool := false
  /-- An SSN valid for employment issued by the return's due date (§24(h)(7), §32(c)(3)(D), (m)). -/
  hasSSN : Bool := true
  /-- Some taxpayer identification number (SSN, ITIN or ATIN) issued by the due date (§24(e)). -/
  hasTIN : Bool := true
  /-- Principal place of abode in the United States for more than half the year (§32(c)(3)(C)). -/
  abodeInUS : Bool := true
  /-- The person is a qualifying child of another taxpayer for the year (§152(d)(1)(D)); Notice 2008-5: not so if
  that taxpayer need not file and files only for a refund. -/
  qualifyingChildOfAnother : Bool := false
  /-- Under the §152(c)(4) tie-breaker the person is treated as another taxpayer's qualifying child (see
  `tieBreak`). -/
  lostTieBreaker : Bool := false
  /-- §152(e): the taxpayer is the noncustodial parent and the custodial parent released the claim (Form 8332 or a
  pre-2009 decree); the child is then treated as the taxpayer's qualifying child for §§151, 24, but not §§2(b), 32. -/
  releasedUnder152e : Bool := false
  /-- §152(e) the other way: the taxpayer is the custodial parent who released the claim to the other parent. -/
  releasedToOtherParent : Bool := false
  /-- For a parent: the taxpayer maintains the parent's household, which need not be the taxpayer's (§2(b)(1)(B)). -/
  taxpayerMaintainsParentsHousehold : Bool := false
  /-- The person is the taxpayer's spouse at any time in the year (cannot be a §152(d)(2)(H) household member). -/
  isSpouse : Bool := false
  /-- The relationship violates local law (§152(f)(3)). -/
  relationshipViolatesLocalLaw : Bool := false
  deriving Repr, Inhabited

/-- "More than one-half of such taxable year" for calendar year `y`. -/
def PersonFacts.abodeMoreThanHalf (x : PersonFacts) (y : Nat) : Bool :=
  match x.livedWithMoreThanHalfYear with
  | some b => b
  | none => 2 * x.daysWithTaxpayer > daysInYear y || x.livedWithWholeYear

/-- §152(c)(3): younger than the taxpayer and under 19, or a student under 24; or disabled (any age). -/
def PersonFacts.ageOk (x : PersonFacts) : Bool :=
  x.disabled || (x.youngerThanTaxpayer && (x.age < 19 || (x.student && x.age < 24)))

/-- Which tests of §152(c)(1) to apply. -/
structure QcVariant where
  /-- §152(c)(1)(D) support test (dropped by §32(c)(3)(A)). -/
  supportTest : Bool := true
  /-- Let a §152(e) release stand in for the residence test (§152(e)(1); not for §§2(b), 32). -/
  use152e : Bool := true

/-- §152(c)(1) qualifying child: relationship, residence for more than half the year, age, not self-supporting, no
joint return; and not lost to another claimant under §152(c)(4). With `use152e`, a release under §152(e) makes the
child the noncustodial parent's (and not the custodial parent's) qualifying child for the purposes that rule reaches. -/
def qualifyingChild (y : Nat) (x : PersonFacts) (v : QcVariant := {}) : Bool :=
  let residence :=
    if v.use152e then (x.abodeMoreThanHalf y || x.releasedUnder152e) && !x.releasedToOtherParent
    else x.abodeMoreThanHalf y
  x.relationship.qcOk && residence && x.ageOk && (!v.supportTest || !x.providedOverHalfOwnSupport) &&
    !x.filedJointReturn && !x.lostTieBreaker

/-- The reasons `qualifyingChild` fails, for an encoding's report. -/
def qualifyingChildFailures (y : Nat) (x : PersonFacts) (v : QcVariant := {}) : List String :=
  (if x.relationship.qcOk then [] else ["§152(c)(1)(A) relationship"]) ++
  (if (if v.use152e then (x.abodeMoreThanHalf y || x.releasedUnder152e) && !x.releasedToOtherParent
       else x.abodeMoreThanHalf y) then [] else ["§152(c)(1)(B) residence more than half the year"]) ++
  (if x.ageOk then [] else ["§152(c)(3) age"]) ++
  (if !v.supportTest || !x.providedOverHalfOwnSupport then [] else ["§152(c)(1)(D) provided over half own support"]) ++
  (if x.filedJointReturn then ["§152(c)(1)(E) joint return"] else []) ++
  (if x.lostTieBreaker then ["§152(c)(4) another taxpayer has priority"] else [])

/-- §152(d)(2)(H): "an individual (other than an individual who at any time during the taxable year was the spouse
... of the taxpayer) who, for the taxable year of the taxpayer, has the same principal place of abode as the taxpayer
and is a member of the taxpayer's household", subject to §152(f)(3) (local law). -/
def PersonFacts.householdMember (x : PersonFacts) : Bool :=
  !x.isSpouse && x.livedWithWholeYear && !x.relationshipViolatesLocalLaw

/-- §152(d)(1) qualifying relative: relationship or household member; gross income less than the exemption amount;
over half support from the taxpayer; not a qualifying child of the taxpayer or of anyone else. -/
def qualifyingRelative (p : Params) (x : PersonFacts) : Bool :=
  (x.relationship.qrOk || x.householdMember) && x.grossIncome < p.exemption152d &&
    (x.taxpayerProvidedOverHalfSupport || x.releasedUnder152e) &&
    !qualifyingChild p.year x && !x.qualifyingChildOfAnother && !x.lostTieBreaker

def qualifyingRelativeFailures (p : Params) (x : PersonFacts) : List String :=
  (if x.relationship.qrOk || x.householdMember then [] else ["§152(d)(2) relationship or member of household"]) ++
  (if x.grossIncome < p.exemption152d then [] else [s!"§152(d)(1)(B) gross income not less than ${p.exemption152d}"]) ++
  (if x.taxpayerProvidedOverHalfSupport || x.releasedUnder152e then [] else ["§152(d)(1)(C) support"]) ++
  (if !qualifyingChild p.year x && !x.qualifyingChildOfAnother && !x.lostTieBreaker then []
   else ["§152(d)(1)(D) a qualifying child"])

/-- §152(a)–(b): a dependent of a taxpayer who is not himself a dependent of another (§152(b)(1)); not a married
person who filed jointly (§152(b)(2)); a citizen, national or resident of the U.S. or of Canada or Mexico
(§152(b)(3)). `taxpayerIsDependent`: the taxpayer can be claimed by someone else. -/
def isDependent (p : Params) (taxpayerIsDependent : Bool) (x : PersonFacts) : Bool :=
  !taxpayerIsDependent && !x.filedJointReturn && (x.usCitizenOrResident || x.residentOfContiguousCountry) &&
    (qualifyingChild p.year x || qualifyingRelative p x)

/-! ## The tie-breaker, §152(c)(4) -/

/-- A taxpayer who could claim the child as a qualifying child (all of §152(c)(1) met for that taxpayer). Parents
filing a joint return together are one claimant. -/
structure Claimant where
  name : String := ""
  isParent : Bool := false
  /-- Days the child resided with this claimant during the year (§152(c)(4)(B)(i)). -/
  daysResided : Int := 0
  agi : Int := 0
  /-- Whether this claimant actually claims the child (§152(c)(4)(B), (C) look at who claims). -/
  claims : Bool := true
  deriving Repr, Inhabited, DecidableEq

/-- The first element that no later element strictly beats (`better a b`: `a` strictly better than `b`). -/
def pickBest (better : Claimant → Claimant → Bool) : List Claimant → Option Claimant
  | [] => none
  | c :: cs => match pickBest better cs with
    | none => some c
    | some d => if better d c then some d else some c

theorem pickBest_mem (b : Claimant → Claimant → Bool) (cs : List Claimant) (c : Claimant)
    (h : pickBest b cs = some c) : c ∈ cs := by
  induction cs with
  | nil => simp [pickBest] at h
  | cons x xs ih =>
    simp only [pickBest] at h
    split at h
    · simp at h; simp [h]
    · rename_i d hd
      split at h
      · simp at h; subst h; exact List.mem_cons_of_mem _ (ih hd)
      · simp at h; simp [h]

theorem pickBest_isSome (b : Claimant → Claimant → Bool) (cs : List Claimant) (h : cs ≠ []) :
    (pickBest b cs).isSome := by
  cases cs with
  | nil => exact absurd rfl h
  | cons x xs =>
    simp only [pickBest]
    split <;> (try split) <;> rfl

/-- Parents compete on days of residence, then AGI (§152(c)(4)(B)). -/
def parentBetter (a b : Claimant) : Bool := a.daysResided > b.daysResided || (a.daysResided == b.daysResided && a.agi > b.agi)
/-- Everyone else competes on AGI (§152(c)(4)(A)(ii)). -/
def agiBetter (a b : Claimant) : Bool := a.agi > b.agi

/-- **§152(c)(4).** Of the claimants who could treat the child as a qualifying child:
* (A)(i), (B): if any parent claims, the claiming parent with whom the child resided longest, and if equal, with the
  higher AGI;
* (C): if a parent could claim but no parent does, a non-parent may claim only with AGI higher than that of every
  parent who could; among those, the highest AGI;
* (A)(ii): if no claimant is a parent, the highest AGI among those claiming.
Exact ties (equal days and equal AGI) are not resolved by the statute; the first listed wins and the encoding should
say so. Returns `none` if nobody may treat the child as a qualifying child. -/
def tieBreak (cs : List Claimant) : Option Claimant :=
  let claiming := cs.filter (·.claims)
  let parentsClaiming := claiming.filter (·.isParent)
  let parents := cs.filter (·.isParent)
  if parentsClaiming ≠ [] then pickBest parentBetter parentsClaiming
  else if parents ≠ [] then
    let topParentAgi := parents.foldl (fun m c => max m c.agi) (parents.head!.agi)
    pickBest agiBetter (claiming.filter (fun c => c.agi > topParentAgi))
  else pickBest agiBetter claiming

/-- **The tie-breaker picks at most one claimant, and only one who claims.** -/
theorem tieBreak_claims (cs : List Claimant) (c : Claimant) (h : tieBreak cs = some c) :
    c ∈ cs ∧ c.claims = true := by
  unfold tieBreak at h
  simp only at h
  split at h
  · have := pickBest_mem _ _ _ h; simp [List.mem_filter] at this; exact ⟨this.1, this.2.2⟩
  · split at h
    · have := pickBest_mem _ _ _ h; simp [List.mem_filter] at this; exact ⟨this.1, this.2.2⟩
    · have := pickBest_mem _ _ _ h; simp [List.mem_filter] at this; exact ⟨this.1, this.2⟩

/-- **When a parent claims, exactly one claimant is picked, and it is a parent who claims.** -/
theorem tieBreak_parent (cs : List Claimant) (hp : ∃ c ∈ cs, c.claims = true ∧ c.isParent = true) :
    ∃ w, tieBreak cs = some w ∧ w.isParent = true ∧ w.claims = true ∧ w ∈ cs := by
  have hne : (cs.filter (·.claims)).filter (·.isParent) ≠ [] := by
    obtain ⟨c, hc, h1, h2⟩ := hp
    intro he
    have : c ∈ (cs.filter (·.claims)).filter (·.isParent) := by simp [List.mem_filter, hc, h1, h2]
    simp [he] at this
  have hs := pickBest_isSome parentBetter _ hne
  obtain ⟨w, hw⟩ := Option.isSome_iff_exists.mp hs
  have hm := pickBest_mem _ _ _ hw
  simp [List.mem_filter] at hm
  refine ⟨w, ?_, hm.2.1, hm.2.2, hm.1⟩
  unfold tieBreak; simp only; rw [if_pos hne]; exact hw

/-- **With no parent among the claimants, someone is always picked when anyone claims.** -/
theorem tieBreak_no_parent (cs : List Claimant) (hnp : ∀ c ∈ cs, c.isParent = false)
    (hc : ∃ c ∈ cs, c.claims = true) : (tieBreak cs).isSome := by
  have h1 : (cs.filter (·.claims)).filter (·.isParent) = [] := by
    apply List.eq_nil_iff_forall_not_mem.mpr
    intro c hc; simp [List.mem_filter] at hc; have := hnp c hc.1; simp_all
  have h2 : cs.filter (·.isParent) = [] := by
    apply List.eq_nil_iff_forall_not_mem.mpr
    intro c hc; simp [List.mem_filter] at hc; have := hnp c hc.1; simp_all
  have h3 : cs.filter (·.claims) ≠ [] := by
    obtain ⟨c, hcs, hcl⟩ := hc
    intro he
    have : c ∈ cs.filter (·.claims) := by simp [List.mem_filter, hcs, hcl]
    simp [he] at this
  unfold tieBreak; simp only; rw [if_neg (by simpa using h1), if_neg (by simpa using h2)]
  exact pickBest_isSome _ _ h3

/-! ## Tests: the Pub. 501 / Pub. 596 tie-breaker examples (the rules have been the same in every edition 2016–2024)
-/

-- Pub. 501, "Tiebreaker rules", Example 1 (child lived with mother and grandmother; mother's AGI $15,000,
-- grandmother's $25,000; both claim): the mother, as parent, wins.
#guard (tieBreak [{ name := "mother", isParent := true, daysResided := 365, agi := 15000 },
                  { name := "grandmother", daysResided := 365, agi := 25000 }]).map (·.name) = some "mother"
-- Example 1 variant: the mother does not claim; the grandmother's AGI ($25,000) exceeds the mother's: she may claim.
#guard (tieBreak [{ name := "mother", isParent := true, daysResided := 365, agi := 15000, claims := false },
                  { name := "grandmother", daysResided := 365, agi := 25000 }]).map (·.name) = some "grandmother"
-- ... but not if her AGI is lower than the parent's (§152(c)(4)(C)).
#guard (tieBreak [{ name := "mother", isParent := true, daysResided := 365, agi := 30000, claims := false },
                  { name := "grandmother", daysResided := 365, agi := 25000 }]).map (·.name) = none
-- Parents not filing jointly, both claim: the child lived with the father 210 days, the mother 155: the father.
#guard (tieBreak [{ name := "mother", isParent := true, daysResided := 155, agi := 50000 },
                  { name := "father", isParent := true, daysResided := 210, agi := 20000 }]).map (·.name) = some "father"
-- Equal time: the higher AGI.
#guard (tieBreak [{ name := "mother", isParent := true, daysResided := 182, agi := 50000 },
                  { name := "father", isParent := true, daysResided := 182, agi := 20000 }]).map (·.name) = some "mother"
-- No parent: the highest AGI (Pub. 501 Example: two siblings of the child's late parent).
#guard (tieBreak [{ name := "aunt", agi := 40000 }, { name := "uncle", agi := 45000 }]).map (·.name) = some "uncle"

-- Qualifying child: a 19-year-old non-student fails the age test; a 23-year-old student passes; disabled passes.
#guard qualifyingChild 2019 { age := 19, livedWithMoreThanHalfYear := some true } = false
#guard qualifyingChild 2019 { age := 23, student := true, livedWithMoreThanHalfYear := some true } = true
#guard qualifyingChild 2019 { age := 40, disabled := true, youngerThanTaxpayer := false, daysWithTaxpayer := 300 } = true
-- 183 of 365 days is more than half; 183 of 366 (2016, 2020, 2024) is not.
#guard qualifyingChild 2019 { age := 5, daysWithTaxpayer := 183 } = true
#guard qualifyingChild 2020 { age := 5, daysWithTaxpayer := 183 } = false
-- Qualifying relative gross income test by year: $4,149 passes in 2018 ($4,150), $4,150 does not.
#guard qualifyingRelative ((params? 2018).getD default)
  { relationship := .parent, grossIncome := 4149, taxpayerProvidedOverHalfSupport := true, youngerThanTaxpayer := false,
    age := 70 } = true
#guard qualifyingRelative ((params? 2018).getD default)
  { relationship := .parent, grossIncome := 4150, taxpayerProvidedOverHalfSupport := true, youngerThanTaxpayer := false,
    age := 70 } = false
-- An unrelated girlfriend who lived with the taxpayer all year is a qualifying relative (member of household).
#guard qualifyingRelative ((params? 2023).getD default)
  { relationship := .unrelated, age := 30, youngerThanTaxpayer := false, livedWithWholeYear := true, grossIncome := 0,
    taxpayerProvidedOverHalfSupport := true } = true

end Legal.USTax.TaxCourt
