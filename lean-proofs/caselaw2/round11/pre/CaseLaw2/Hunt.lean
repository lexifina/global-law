import LegalProofs.CaseLaw2.Spec.Findings
import LegalProofs.CaseLaw2.Spec.Horty
import LegalProofs.CaseLaw2.Spec.Splits

/-!
# The loophole and mistake hunt: six search patterns as predicates

`caselaw-lean-2/hunt/HUNT.md` reports the search of the corpus; this module states what was searched for. Each
pattern is a decidable predicate over (a) what the Spec computes for a citation or a treatment (status, force,
publication, power) and (b) what a reader of the citing opinion reports (does it rely on the cited decision, does it
note the negative history, which bench decided it, when was the conduct). The Spec side comes from `Spec.Findings`,
`Spec.Status`, `Spec.Horty` and `Spec.Splits`; the reader side is input, exactly as `followed` is input to
`Spec.citesUnpublishedAsBinding`.

The `#guard`s replay known cases and cases the blind audit confirmed (HUNT.md gives the citations), together with the
near misses that made the first search of each pattern imprecise: a negation on a different point, a reporter-published
opinion labelled unpublished, an en banc footnote, a citation of a superseded decision for an unaffected holding.

1. `zombie`                    reliance on a negated holding without acknowledgement
2. `unpublishedAsBinding`      an unpublished opinion treated as binding (and `mislabelled`, the data error found)
3. `panelOverrulesPanel`       a panel departs from its own court's precedent without en banc
4. `twoDateError`              a superseded holding applied to conduct from the statute's date on
5. `inconsistentBase`, `persistingSplit`, `losingSideAfterResolution`
6. `forumDependent`, `cutoffWindow`, `orphaned`, `adoptionCarriesOverruled`, `dualHighCourtConflict`,
   `commissionForce`           loopholes in the rules themselves
-/

namespace CaseLaw2.Hunt
open CaseLaw2 CaseLaw2.Spec

/-! ## 1. Zombie precedent -/

/-- What a reader reports about one citation of a decision whose status is negative. -/
structure Use where
  /-- the citing court uses the cited decision as authority for a proposition it applies -/
  relies : Bool
  /-- the citing opinion notes the negative history, or cites the negating decision on the point -/
  acknowledges : Bool
  /-- the citing opinion is part of the same litigation -/
  sameCase : Bool
  /-- the proposition taken is the one negated (or the decision fell as a whole) -/
  onNegatedPoint : Bool
  deriving Repr, DecidableEq, Inhabited

/-- The negative states a later court can rely on by mistake: the holding was overruled or abrogated, or the decision
reversed, vacated or withdrawn. (`superseded` is pattern 4; `reviewPending` and `depublished` are publication states.) -/
def deadLaw : Status → Bool
  | .neg .overruled | .neg .abrogated | .neg .reversed | .neg .vacated | .neg .withdrawn => true
  | _ => false

/-- Pattern 1. `s` is the status of the cited issue on the citing date (`Spec.statusOf`). -/
def zombie (s : Status) (u : Use) : Bool :=
  deadLaw s && u.relies && !u.acknowledges && !u.sameCase && u.onNegatedPoint

/-- The Spec's own findings are the candidate set: every zombie is a `citesOverruled`, `citesVacated` or
`citesWithdrawn` row. The search reads the opinion to decide the other four limbs. -/
theorem zombie_is_spec_finding (c : CiteFacts) (u : Use) (h : zombie c.status u = true) :
    (citesOverruled c || citesVacated c || citesWithdrawn c) = true := by
  cases hs : c.status with
  | good => simp [zombie, deadLaw, hs] at h
  | unknown r => simp [zombie, deadLaw, hs] at h
  | neg n => cases n <;> simp_all [zombie, deadLaw, citesOverruled, citesVacated, citesWithdrawn]

theorem good_law_never_zombie (u : Use) : zombie .good u = false := by
  simp [zombie, deadLaw]

theorem acknowledged_never_zombie (s : Status) (u : Use) (h : u.acknowledges = true) : zombie s u = false := by
  simp [zombie, h]

/-- Hammer v. Dagenhart, 247 U.S. 251, overruled by United States v. Darby (3 Feb 1941); United States v. Helsey,
463 F. Supp. 1111 (D. Mont. 1979) quotes it as authority and strikes down a federal statute. -/
def helsey : Use := ⟨true, false, false, true⟩
#guard zombie (.neg .overruled) helsey
/- National League of Cities v. Usery, overruled by Garcia (19 Feb 1985); In re Odyssey Healthcare, 310 S.W.3d 419
(Tex. 2010) applies its test. -/
#guard zombie (.neg .overruled) ⟨true, false, false, true⟩
/- State v. Hurst (N.C. App.), reversed by the N.C. Supreme Court; Kott v. State, 518 So. 2d 957 (Fla. DCA 1988). -/
#guard zombie (.neg .reversed) ⟨true, false, false, true⟩
/- Near miss (audit): Howard Hess Dental v. Dentsply, 602 F.3d 237, cites Albrecht v. Herald Co. for a point State
Oil v. Khan did not touch. -/
#guard !zombie (.neg .overruled) ⟨true, false, false, false⟩
/- Near miss: a citation that gives the subsequent history. -/
#guard !zombie (.neg .overruled) ⟨true, true, false, true⟩
/- Near miss: Bowers v. Hardwick cited on 25 Jun 2003, the day before Lawrence. -/
#guard !zombie .good ⟨true, false, false, true⟩

/-! ## 2. Unpublished opinions treated as binding -/

/-- Pattern 2. `force` is the force of the cited decision on the citing court (`Spec.force`, which applies the
unpublished-opinion rule of the issuing court at the decision's date). -/
def unpublishedAsBinding (pub : Publication) (force : Force) (treatsAsBinding sameCase : Bool) : Bool :=
  pub != .published && decide (force.rank < Force.bindingAbsentConflict.rank) && treatsAsBinding && !sameCase

/-- The Spec's version with `followed` read from the opinion. -/
theorem unpublishedAsBinding_spec (c : CiteFacts) (f : Force) (p : List RuleId) (pub : Publication)
    (hp : c.pub = some pub) (hf : c.force = some (f, p)) (hfo : c.followed = true)
    (h : unpublishedAsBinding pub f true false = true) : citesUnpublishedAsBinding c = true := by
  simp [unpublishedAsBinding] at h
  simp [citesUnpublishedAsBinding, hp, hf, hfo, h]

/-- The data error the audit found: `decisions2.pub` says unpublished, but the decision is printed in a reporter of
published opinions (it attaches, or reviews, an unpublished order). -/
def mislabelled (pub : Publication) (printedReporter : Bool) : Bool := pub != .published && printedReporter

/-- Pattern 2 on corrected labels. -/
def unpublishedAsBinding' (pub : Publication) (printedReporter : Bool) (force : Force)
    (treatsAsBinding sameCase : Bool) : Bool :=
  !mislabelled pub printedReporter && unpublishedAsBinding pub force treatsAsBinding sameCase

theorem corrected_implies_first (pub : Publication) (pr : Bool) (f : Force) (b s : Bool)
    (h : unpublishedAsBinding' pub pr f b s = true) : unpublishedAsBinding pub f b s = true := by
  simp [unpublishedAsBinding'] at h
  exact h.2

/- United States v. Beuns, 614 F. App'x 284 (6th Cir. 2015): "our precedent, which holds", citing only the
unpublished United States v. Gilmore, 431 F. App'x 428. -/
#guard unpublishedAsBinding' .unpublished false .persuasive true false
/- Near miss (audit, 17 of 20): United States v. Slaughter, 238 F.3d 580 (5th Cir. 2000) is labelled unpublished in
the data, is printed in F.3d, and is rightly treated as binding ("foreclosed by Slaughter"). -/
#guard unpublishedAsBinding .unpublished .persuasive true false
#guard !unpublishedAsBinding' .unpublished true .persuasive true false
/- Near miss: law of the case (United States v. MacArthur, 571 F. App'x 885). -/
#guard !unpublishedAsBinding' .unpublished false .persuasive true true
/- Not an instance: a Fifth Circuit unpublished opinion issued before 1 Jan 1996 is precedent (5th Cir. R. 47.5.3). -/
#guard !unpublishedAsBinding' .unpublished false .binding true false

/-! ## 3. Panel overrules panel -/

/-- The grounds on which a panel may depart from its court's precedent. -/
inductive Exception where
  | interveningHigherCourt | interveningEnBanc | statuteChange | circulatedToFullCourt | earlierConflictingPrecedent
  | dictaOnly | unpublished
  deriving Repr, DecidableEq, Inhabited

/-- What the data and a reader report about one departure. -/
structure Departure where
  /-- the later decision overrules, recedes from, disapproves or refuses to follow the earlier holding -/
  departs : Bool
  /-- same court, and the same unit where precedent binds within the unit only -/
  sameCourt : Bool
  /-- the court's horizontal rule is strong (`system_rules horizontal = strong`, or `withinUnitOnly`) -/
  strongRule : Bool
  /-- the later decision's bench is a panel -/
  panel : Bool
  /-- the court had an en banc procedure on the date -/
  enBancAvailable : Bool
  exception : Option Exception
  deriving Repr, DecidableEq, Inhabited

/-- Pattern 3. -/
def panelOverrulesPanel (d : Departure) : Bool :=
  d.departs && d.sameCourt && d.strongRule && d.panel && d.enBancAvailable && d.exception.isNone

theorem panelOverrulesPanel_needs (d : Departure) (h : panelOverrulesPanel d = true) :
    d.panel = true ∧ d.strongRule = true ∧ d.exception = none := by
  simp [panelOverrulesPanel] at h
  exact ⟨h.1.1.2, h.1.1.1.2, h.2⟩

theorem enBanc_never (d : Departure) (h : d.panel = false) : panelOverrulesPanel d = false := by
  simp [panelOverrulesPanel, h]

/- Tarrant Appraisal Dist. v. Tarrant Reg'l Water Dist., 547 S.W.3d 917 (Tex. App. Fort Worth 2018): a three-justice
panel overrules the court's own Grand Prairie Hospital Authority (1986); en banc reconsideration denied. -/
#guard panelOverrulesPanel ⟨true, true, true, true, true, none⟩
/- Franklin v. Franklin, 171 F.2d 12 (D.C. Cir. 1948): a divided division declares three of the court's decisions
"should be overruled". -/
#guard panelOverrulesPanel ⟨true, true, true, true, true, none⟩
/- Near miss: Fisher v. United States, 402 F.3d 1167 (Fed. Cir. 2005): the overruling part was decided en banc. -/
#guard !panelOverrulesPanel ⟨true, true, true, false, true, none⟩
/- Near miss: United States v. Ortiz, 143 F.3d 728 (2d Cir. 1998): circulated to all active judges. -/
#guard !panelOverrulesPanel ⟨true, true, true, true, true, some .circulatedToFullCourt⟩
/- Near miss: United States v. Conti, 804 F.3d 977 (9th Cir. 2015): clearly irreconcilable with Neder. -/
#guard !panelOverrulesPanel ⟨true, true, true, true, true, some .interveningHigherCourt⟩
/- Near miss: Mollica v. State, 374 So. 2d 1022 (Fla. 2d DCA 1979): no en banc procedure before 1980. -/
#guard !panelOverrulesPanel ⟨true, true, true, true, false, none⟩
/- Near miss: Fidelity & Casualty v. De Jesus, 402 So. 2d 15: the decision receded from is of another district. -/
#guard !panelOverrulesPanel ⟨true, false, true, true, true, none⟩

/-! ## 4. Two-date errors -/

/-- Pattern 4. `conductFrom` is the date from which the statute governs (its effective date, or its stated
retroactive date); `conduct` is the date of the conduct, claim or filing the citing court decides. -/
def twoDateError (conductFrom conduct : Date) (appliesSupersededHolding notesStatute : Bool) : Bool :=
  appliesSupersededHolding && !notesStatute && decide (conductFrom ≤ conduct)

/-- Prospectivity (the reader-side mirror of `Spec.supersession_prospective`): before the date, no error. -/
theorem earlier_conduct_no_error (d u : Date) (a n : Bool) (h : u < d) : twoDateError d u a n = false := by
  have : ¬ d ≤ u := Nat.not_le.mpr h
  simp [twoDateError, this]

theorem twoDateError_dates (d u : Date) (a n : Bool) (h : twoDateError d u a n = true) : d ≤ u := by
  simp [twoDateError] at h
  exact h.2

/- Toyota Motor Mfg. v. Williams, 534 U.S. 184, overridden by the ADA Amendments Act for conduct from 1 Jan 2009;
Nadel v. Shinseki, 57 F. Supp. 3d 288 (S.D.N.Y. 2014) applies Toyota to 2010-2011 employment. -/
#guard twoDateError 20090101 20100601 true false
/- Koon v. United States: abuse-of-discretion review of departures, displaced by the PROTECT Act (30 Apr 2003);
United States v. Mayle, 334 F.3d 552 (6th Cir. 1 Jul 2003). -/
#guard twoDateError 20030430 20030701 true false
/- Ledbetter v. Goodyear: superseded for claims pending on or after 28 May 2007 (Pub. L. 111-2, enacted 29 Jan 2009). -/
#guard twoDateError 20070528 20080301 true false
#guard !twoDateError 20070528 20060301 true false
/- Near miss (audit, 20 of 20 runner findings): the Eleventh Circuit Ledbetter cited after 2009 for a holding the
Act did not touch (weighing evidence; the 180-day period). -/
#guard !twoDateError 20070528 20120101 false false
/- Near miss: Toyota applied to a 2007 termination, decided 2010. -/
#guard !twoDateError 20090101 20071101 true false

/-! ## 5. Inconsistent binding bases and splits -/

open Horty in
/-- Pattern 5(a): the binding case base of a court is inconsistent in Horty's pair form. -/
def inconsistentBase (Γ : List Horty.FCase) : Bool := !Horty.consistent Γ

/-- Overruling a case never creates an inconsistency (from `Horty.consistent_erase`). -/
theorem erase_keeps_consistent (Γ : List Horty.FCase) (c : Horty.FCase) (h : inconsistentBase Γ = false) :
    inconsistentBase (Γ.erase c) = false := by
  simp [inconsistentBase] at *
  exact Horty.consistent_erase c h

/-- Express pre-emption, factors 5002 (the clause names the regulated transaction; for pre-emption) and 5008 (an
exception names the state's regulatory subject; against). -/
def f5002 : Horty.Factor := ⟨5002, .pi⟩
def f5008 : Horty.Factor := ⟨5008, .delta⟩
/-- Aloha Airlines v. Director of Taxation, 464 U.S. 7 (1983): both present, pre-empted, reason 5002. -/
def aloha : Horty.FCase := ⟨[f5002, f5008], [f5002], .pi⟩
/-- Chamber of Commerce v. Whiting, 563 U.S. 582 (2011): both present, not pre-empted, reason 5008. -/
def whiting : Horty.FCase := ⟨[f5002, f5008], [f5008], .delta⟩
#guard Horty.conflict aloha whiting
#guard inconsistentBase [aloha, whiting]
#guard !inconsistentBase [aloha]
#guard !inconsistentBase [whiting]

/-- Pattern 5(b): a split that persists: two courts' resolved binding answers differ and neither binds the other. -/
def persistingSplit (r₁ r₂ : List Cand) : Bool := Spec.split r₁ r₂ false

/-- Pattern 5(c): after the Supreme Court resolved the split, a court relies on the losing side for the resolved
question without noting the resolution. -/
def losingSideAfterResolution (scotus citing : Date) (citedAnswer scotusAnswer : Answer)
    (reliesOnPoint notesScotus : Bool) : Bool :=
  decide (scotus < citing) && citedAnswer != scotusAnswer && reliesOnPoint && !notesScotus

theorem winning_side_never (s c : Date) (a : Answer) (r n : Bool) : losingSideAfterResolution s c a a r n = false := by
  simp [losingSideAfterResolution]

/- Whitfield v. United States (11 Jan 2005): no overt act for a section 1956(h) conspiracy; United States v.
Armstrong, 550 F.3d 382 (5th Cir. 2008) states the overt-act element, citing United States v. Wilson, 249 F.3d 366. -/
#guard losingSideAfterResolution 20050111 20081121 .yes .no true false
/- Rotella v. Wood (23 Feb 2000) rejected injury-and-pattern discovery accrual; Wade v. Gaither, 623 F. Supp. 2d
1277 (D. Utah 2009) applies it, citing Bath v. Bushkin. -/
#guard losingSideAfterResolution 20000223 20090306 .yes .no true false
/- Near miss (audit, 10 of 20): the losing-side decision cited for another point. -/
#guard !losingSideAfterResolution 20000223 20090306 .yes .no false false
#guard !losingSideAfterResolution 20050111 20040101 .yes .no true false

/-! ## 6. Loopholes in the rules -/

/-- A force that makes a court follow the decision. -/
def binds (f : Force) : Bool := decide (Force.bindingAbsentConflict.rank ≤ f.rank)

/-- 6(a) Forum choice: the same holding binds one forum and not a sibling forum. -/
def forumDependent (inForum inSibling : Force) : Bool := binds inForum != binds inSibling

/-- 6(d) Cut-off window: two decisions of one court, a day or a rule apart, of which only one binds the destination. -/
def cutoffWindow (before after : Force) : Bool := binds before && !binds after

/-- 6(b) Successor gap: the old court's decision binds no appellate court of the new structure. -/
def orphaned (onNewHighCourt onNewIntermediate : Force) : Bool := !binds onNewHighCourt && !binds onNewIntermediate

/-- 6(e) Adoption chain: a decision adopted by two heirs, negated by one, still carries authority in the other. The
Spec's status is not relative to the citing court, so the Spec reports the other heir's citations as `citesOverruled`. -/
def adoptionCarriesOverruled (negatedByOtherHeir : Bool) (authorityOnThisHeir : Force) : Bool :=
  negatedByOtherHeir && binds authorityOnThisHeir

/-- 6(c) Dual courts of last resort: both bind the intermediate court, they answer differently, and neither has power
over the other. -/
def dualHighCourtConflict (civilOnIntermediate criminalOnIntermediate : Force) (a₁ a₂ : Answer)
    (power₁₂ power₂₁ : Bool) : Bool :=
  binds civilOnIntermediate && binds criminalOnIntermediate && a₁ != a₂ && !power₁₂ && !power₂₁

/-- 6(f) Commission opinions: the notation the adopting court printed decides the force. -/
inductive Notation where
  | opinionAdopted | holdingApproved | judgmentAdopted | none
  deriving Repr, DecidableEq, Inhabited

def commissionForce : Notation → Force
  | .opinionAdopted => .binding
  | .holdingApproved => .binding
  | .judgmentAdopted => .none
  | .none => .persuasive

theorem forumDependent_symm (a b : Force) : forumDependent a b = forumDependent b a := by
  simp [forumDependent, bne_comm]

theorem no_conflict_with_power (c k : Force) (a b : Answer) (p : Bool) :
    dualHighCourtConflict c k a b true p = false := by
  simp [dualHighCourtConflict]

theorem same_notation_same_force (n m : Notation) (h : n = m) : commissionForce n = commissionForce m := by
  rw [h]

/- Bonner v. City of Prichard: a Fifth Circuit decision of 30 Sep 1981 binds the Eleventh Circuit; one of 1 Oct 1981
is another circuit's. (Reference engine, hunt/data/p6f_named_probes.tsv.) -/
#guard cutoffWindow .binding .persuasive
/- M.A.P. v. Ryan: a D.C. Circuit decision of 29 Jan 1971 binds the D.C. trial courts; one of 2 Feb 1971 does not. -/
#guard cutoffWindow .binding .persuasive
/- The Tenth Circuit (1929) took nothing from the Eighth: the same kind of succession, the opposite answer. -/
#guard !cutoffWindow .persuasive .persuasive
#guard forumDependent .binding .persuasive
/- New Jersey 1948: a decision of the old Supreme Court (an intermediate court, 21,129 decisions) binds neither the
new Supreme Court nor the Appellate Division. -/
#guard orphaned .persuasive .persuasive
/- Kentucky 1976: no gap: the old Court of Appeals binds the new intermediate court. -/
#guard !orphaned .persuasiveStrong .binding
/- United States v. Salinas (5th Cir. Aug 1981), overruled by the Fifth Circuit en banc in United States v. Adamson
(1983), is still binding precedent in the Eleventh Circuit. -/
#guard adoptionCarriesOverruled true .binding
/- Texas: the Supreme Court and the Court of Criminal Appeals both bind a court of appeals; neither can overrule
the other (hunt/data/p6c_dual_high_courts.tsv: power no, `H2.dualLastResort`). -/
#guard dualHighCourtConflict .binding .binding .yes .no false false
#guard !dualHighCourtConflict .binding .binding .yes .yes false false
#guard commissionForce .opinionAdopted == .binding
#guard commissionForce .judgmentAdopted == .none
#guard binds (commissionForce .opinionAdopted) && !binds (commissionForce .none)

end CaseLaw2.Hunt
