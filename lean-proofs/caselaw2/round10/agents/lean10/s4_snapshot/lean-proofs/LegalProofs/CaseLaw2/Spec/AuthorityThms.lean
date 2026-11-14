import LegalProofs.CaseLaw2.Spec.Authority

/-!
# Spec theorems: authority and power (doctrine §9 items 22–23)

Every theorem holds for **all** parameter tables (`Rules`), all court epochs and all adoption/succession data, so no
table row, U-tagged or not, is a premise (DESIGN D2). Where adoption can change the answer (the D.C. Court of Appeals
adopts pre-1971 D.C. Circuit law across systems), the theorem says "absent adoption" and `Examples.lean` shows the
adoption case.
-/

namespace CaseLaw2.Spec
open CaseLaw2

set_option linter.unusedSimpArgs false

/-! ## Generic lemmas (proved once) -/

theorem foldl_max_rank_le {α} (g : α → Force) (n : Nat) :
    ∀ (l : List α) (init : Force), init.rank ≤ n → (∀ a ∈ l, (g a).rank ≤ n) →
      (l.foldl (fun f a => Force.max f (g a)) init).rank ≤ n
  | [], _, h, _ => h
  | a :: l, init, h, hl => by
    simp only [List.foldl_cons]
    apply foldl_max_rank_le g n l
    · simp only [Force.rank_max]; have := hl a (by simp); omega
    · intro b hb; exact hl b (by simp [hb])

/-- If the relation is bounded on every court, the force is bounded (adoption and caps cannot lift it). -/
theorem force_rank_le (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query) (n : Nat)
    (hrel : ∀ S, (relation L S x (h.domain.getD ((sourceEpoch L x p).map CourtEpoch.home |>.getD .federalGeneral)) q).1.rank ≤ n)
    (r : Force × List RuleId) (hr : force L x h p q = some r) : r.1.rank ≤ n := by
  unfold force at hr
  cases hS : sourceEpoch L x p with
  | none => simp [hS] at hr
  | some S =>
    simp only [hS] at hr
    have hdom := hrel S
    simp only [hS, Option.map_some, Option.getD_some] at hdom
    have hfold := foldl_max_rank_le (adoptedForce L x (h.domain.getD S.home) q) n (adoptionsOf L x) .none
      (by simp [Force.rank]) (by
        intro a _
        unfold adoptedForce
        split
        · rename_i A _; simp only [Force.rank_min]; have := hrel A; simp only [hS, Option.map_some, Option.getD_some] at this; omega
        · simp [Force.rank])
    cases hr
    simp only [Force.rank_min, Force.rank_max]
    omega

/-- With no adoption, the force is at most the relation. -/
theorem force_le_relation_noAdopt (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query)
    (S : CourtEpoch) (hS : sourceEpoch L x p = some S) (hA : adoptionsOf L x = [])
    (r : Force × List RuleId) (hr : force L x h p q = some r) :
    r.1.rank ≤ (relation L S x (h.domain.getD S.home) q).1.rank := by
  unfold force at hr
  simp only [hS, hA, List.foldl_nil] at hr
  cases hr
  simp only [Force.rank_min, Force.rank_max]
  simp [Force.rank]
  omega

/-! ## (a) SCOTUS binds every court on federal law -/

theorem relation_scotus_federal (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query)
    (hS : S.scotus = true) (hd : dom.federal = true) (hq : q.dst.tier ≠ .last) :
    relation L S x dom q = (.binding, .F1) := by
  unfold relation
  have : (q.dst.tier == Tier.last) = false := by simpa using hq
  simp [this, hS, hd]

/-- §9 22(a): a published, full-court SCOTUS majority holding on a federal issue binds every court below the Supreme
Court, whatever the tables say. -/
theorem scotus_binds_federal (L : Lookups) (x : Decision) (h : Holding) (q : Query) (S : CourtEpoch)
    (hS : L.epochAt x.court x.date = some S) (hsc : S.scotus = true)
    (hdom : ∀ d, h.domain = some d → d.federal = true)
    (hpub : x.pub = some .published) (hform : x.form = some .full ∨ x.form = some .perCuriam)
    (hrole : h.role ≠ some .plurality) (hq : q.dst.tier ≠ .last) :
    (force L x h false q).map (·.1) = some .binding := by
  have hsrc : sourceEpoch L x false = some S := by simp [sourceEpoch, hS]
  have hfed : (h.domain.getD S.home).federal = true := by
    cases hd : h.domain with
    | some d => simpa using hdom d hd
    | none =>
      have : S.system = 0 := by simp [CourtEpoch.scotus] at hsc; exact hsc.1
      simp [CourtEpoch.home, this, Domain.federal]
  have hrel := relation_scotus_federal L S x _ q hsc hfed hq
  unfold force
  simp only [hsrc, hrel]
  have hfc : (formCap x h).1 = .binding := by
    unfold formCap
    rcases hform with hf | hf <;> (cases hr : h.role with
      | none => simp [hf]
      | some r => cases r <;> simp_all)
  have hpc : (pubCap L S x).1 = .binding := by simp [pubCap, hpub]
  simp only [Option.map_some]
  congr 1
  apply Force.rank_inj
  simp only [Force.rank_min, Force.rank_max, hfc, hpc]
  have := (Force.le_binding (List.foldl (fun f a => Force.max f (adoptedForce L x (h.domain.getD S.home) q a))
    Force.none (adoptionsOf L x)))
  simp [Force.rank] at this ⊢
  omega

/-! ## (b) Nothing binds a court of last resort on its own system's law -/

theorem relation_lastResort_own_law (L : Lookups) (S : CourtEpoch) (x : Decision) (q : Query)
    (ht : q.dst.tier = .last) (hs : q.dst.system ≠ 0) :
    (relation L S x (.stateLaw q.dst.system) q).1.rank ≤ Force.persuasiveStrong.rank := by
  unfold relation stateHier fedHier horizontalForce trialScopeForce
  simp_all [Domain.federal, CourtEpoch.scotus]
  repeat' split
  all_goals simp_all [Force.rank]

/-- §9 22(b): on its own system's law, no decision of any court binds that system's court of last resort; whatever
the parameter tables, adoptions and successions say. (SCOTUS binds only on federal questions; see (a).) -/
theorem nothing_binds_last_resort (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query)
    (ht : q.dst.tier = .last) (hs : q.dst.system ≠ 0) (hd : h.domain = some (.stateLaw q.dst.system))
    (r : Force × List RuleId) (hr : force L x h p q = some r) : r.1 ≠ .binding := by
  have := force_rank_le L x h p q Force.persuasiveStrong.rank (by
    intro S; rw [hd]; exact relation_lastResort_own_law L S x q ht hs) r hr
  intro hb; rw [hb] at this; simp [Force.rank] at this

/-- Hunt H6: the division rule only ever concerns a court of last resort. For every other bound court, the force on
the court as it ordinarily sits is the Spec's `force`. -/
theorem forceDiv_eq_force (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query)
    (ht : q.dst.tier ≠ .last) : forceDiv L x h p q = force L x h p q := by
  have hd : ∀ S d, divisionRelation L S d x q = none := by
    intro S d
    have : (q.dst.tier == Tier.last) = false := by simpa using ht
    simp [divisionRelation, this]
  have hr : ∀ S dom, relationDiv L S x dom q = relation L S x dom q := by
    intro S dom; simp [relationDiv, hd]
  have ha : ∀ dom a, adoptedForceDiv L x dom q a = adoptedForce L x dom q a := by
    intro dom a; unfold adoptedForceDiv adoptedForce; split <;> simp [hd]
  unfold forceDiv force
  cases sourceEpoch L x p with
  | none => rfl
  | some S => simp only [hr, ha]

/-- Hunt H6, *M.A.P. v. Ryan*: where a court of last resort has a strong court-level horizontal row, a division (a
panel) of it has no power over the court's own decision; only an en banc–equivalent bench has. -/
theorem division_cannot_overrule (L : Lookups) (X B : CourtEpoch) (b x : Decision) (hc : B.court = X.court)
    (hh : L.rules.horizontalCourt X.court x.date = some .strong) (hp : b.bench = some .panel ∨ b.bench = some .division) :
    lastResortBench L X B b x = (false, .strongNeedsEnBanc) := by
  unfold lastResortBench enBancEquiv
  rcases hp with hp | hp <;> simp [hc, hh, hp]

/-! ## (c) Erie is one-directional -/

theorem relation_state_on_federal (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query)
    (hS : S.system ≠ 0) (hd : dom.federal = true) (hq : q.dst.system = 0) :
    relation L S x dom q = (.persuasive, .E3stateOnFederal) := by
  unfold relation
  have h1 : (S.system == q.dst.system) = false := by simp [hq, hS]
  have h2 : S.scotus = false := by simp [CourtEpoch.scotus, hS]
  cases dom <;> simp_all [Domain.federal]

theorem relation_fed_on_state (L : Lookups) (S : CourtEpoch) (x : Decision) (s : Nat) (q : Query)
    (hS : S.system = 0) (hq : q.dst.system ≠ 0) :
    (relation L S x (.stateLaw s) q).1 = .persuasive := by
  unfold relation stateHier fedHier horizontalForce trialScopeForce
  simp_all [Domain.federal, CourtEpoch.scotus]
  repeat' split
  all_goals simp_all [Force.rank]

/-- §9 22(c), *Erie* one-directional: absent an adoption row, (i) no state-court decision binds a federal court on
federal law, and (ii) no federal decision binds a state court on state law. -/
theorem erie_one_directional (L : Lookups) (x : Decision) (h : Holding) (p : Bool) (q : Query) (S : CourtEpoch)
    (hS : sourceEpoch L x p = some S) (hA : adoptionsOf L x = []) (r : Force × List RuleId)
    (hr : force L x h p q = some r) :
    (S.system ≠ 0 → (∃ d, h.domain = some d ∧ d.federal = true) → q.dst.system = 0 → r.1 ≠ .binding) ∧
    (S.system = 0 → (∃ s, h.domain = some (.stateLaw s)) → q.dst.system ≠ 0 → r.1 ≠ .binding) := by
  have hle := force_le_relation_noAdopt L x h p q S hS hA r hr
  constructor
  · intro hs ⟨d, hdd, hfd⟩ hq hb
    have hfed : (h.domain.getD S.home).federal = true := by simp [hdd, hfd]
    rw [relation_state_on_federal L S x _ q hs hfed hq, hb] at hle
    simp [Force.rank] at hle
  · intro hs ⟨s, hd⟩ hq hb
    rw [hd] at hle
    simp only [Option.getD_some] at hle
    rw [relation_fed_on_state L S x s q hs hq, hb] at hle
    simp [Force.rank] at hle

/-! ## (d) Trial courts never bind -/

theorem relation_trial (L : Lookups) (S : CourtEpoch) (x : Decision) (dom : Domain) (q : Query)
    (ht : S.tier = .trial) : (relation L S x dom q).1.rank ≤ Force.persuasive.rank := by
  unfold relation stateHier fedHier horizontalForce trialScopeForce
  simp_all [Domain.federal, CourtEpoch.scotus]
  repeat' split
  all_goals simp_all [Force.rank]

/-- §9 22(d), F13/§4.4: a trial court's decision (not promoted, not adopted) is at most persuasive for every court. -/
theorem trial_never_binding (L : Lookups) (x : Decision) (h : Holding) (q : Query) (S : CourtEpoch)
    (hS : L.epochAt x.court x.date = some S) (ht : S.tier = .trial) (hA : adoptionsOf L x = [])
    (r : Force × List RuleId) (hr : force L x h false q = some r) : r.1.rank ≤ Force.persuasive.rank := by
  have hsrc : sourceEpoch L x false = some S := by simp [sourceEpoch, hS]
  have := force_le_relation_noAdopt L x h false q S hsrc hA r hr
  have := relation_trial L S x (h.domain.getD S.home) q ht
  omega

/-! ## Power to change status -/

/-- §9 item 23, F7: in a court with a strong horizontal rule, a panel cannot overrule a panel of the same court. -/
theorem no_panel_overrules_panel_in_strong (L : Lookups) (b x : Decision) (dom : Option Domain)
    (B X : CourtEpoch) (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X)
    (hc : B.court = X.court) (htB : B.tier = .appellate) (htX : X.tier = .appellate)
    (hh : L.rules.horizontal X.court X.system x.date = some .strong) (hp : b.bench = some .panel) :
    (canChangeStatus L b x dom).map (·.1) = some false := by
  unfold canChangeStatus
  simp only [hB, hX, Option.map_some]
  have hsc : B.scotus = false := by simp [CourtEpoch.scotus, htB]
  have hrank : ¬ X.tier.rank < B.tier.rank := by simp [htB, htX, Tier.rank]
  have hlast : (B.tier == Tier.last) = false := by simp [htB]
  congr 1
  split
  · rfl
  simp only [hsc, Bool.false_and, Bool.false_eq_true, ↓reduceIte, hlast]
  have : (decide (X.tier.rank < B.tier.rank)) = false := by simpa using hrank
  simp only [this, Bool.and_false, Bool.false_and, Bool.false_eq_true, ↓reduceIte, hc, beq_self_eq_true,
    htB, htX, Nat.le_refl, decide_true, Bool.and_self]
  unfold benchRule enBancEquiv
  simp [hh, hp]

/-- v1 `no_overrule_of_binding_superior`, lifted: absent adoption, a lower court of the same system never has power
over a higher court's decision. -/
theorem no_overrule_of_binding_superior (L : Lookups) (b x : Decision) (dom : Option Domain)
    (B X : CourtEpoch) (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X)
    (hrank : B.tier.rank < X.tier.rank) (hc : B.court ≠ X.court)
    (hA : (adoptionsOf L x).any (·.adopter == b.court) = false) :
    (canChangeStatus L b x dom).map (·.1) = some false := by
  unfold canChangeStatus
  simp only [hB, hX, Option.map_some]
  have hlast : B.tier ≠ .last := by
    intro h; rw [h] at hrank; cases hx : X.tier <;> simp [Tier.rank, hx] at hrank
  have hsc : B.scotus = false := by simp [CourtEpoch.scotus, hlast]
  have hA' : ∀ a ∈ adoptionsOf L x, a.adopter ≠ b.court := by simpa using hA
  have hnr : ¬ X.tier.rank < B.tier.rank := by omega
  simp only [hsc, hnr, decide_false, Bool.and_false, Bool.false_and, Bool.false_eq_true, ↓reduceIte, hc,
    beq_iff_eq, hlast, false_and, and_false, ite_false, hA]
  repeat' split
  all_goals simp_all

/-- Only SCOTUS (or the same court) changes the status of a SCOTUS decision, absent adoption. -/
theorem only_scotus_changes_scotus (L : Lookups) (b x : Decision) (dom : Option Domain)
    (B X : CourtEpoch) (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X)
    (hsx : X.scotus = true) (hA : (adoptionsOf L x).any (·.adopter == b.court) = false)
    (hpow : (canChangeStatus L b x dom).map (·.1) = some true) : B.scotus = true ∨ B.court = X.court := by
  unfold canChangeStatus at hpow
  simp only [hB, hX, Option.map_some, Option.some.injEq, hA, Bool.false_and] at hpow
  have hX0 : X.system = 0 ∧ X.tier = .last := by simpa [CourtEpoch.scotus] using hsx
  have hA' : ∀ a ∈ adoptionsOf L x, a.adopter ≠ b.court := by simpa using hA
  by_cases hc : B.court = X.court
  · exact Or.inr hc
  left
  revert hpow
  simp only [hX0, Tier.rank]
  repeat' split
  all_goals intro hpow
  all_goals simp_all [CourtEpoch.scotus, CourtEpoch.federal, Tier.rank]
  all_goals (try omega)
  all_goals (cases hb : B.tier <;> simp_all [Tier.rank])

/-- A decision never has power over a later one. -/
theorem no_power_over_later (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch)
    (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X) (hlt : b.date < x.date) :
    canChangeStatus L b x dom = some (false, .cLater) := by
  unfold canChangeStatus
  simp [hB, hX, hlt]

/-- No cross-system power, absent adoption, except SCOTUS on federal law. -/
theorem no_cross_system (L : Lookups) (b x : Decision) (dom : Option Domain) (B X : CourtEpoch)
    (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X)
    (hs : B.system ≠ X.system) (hsc : B.scotus = false) (hc : B.court ≠ X.court)
    (hA : (adoptionsOf L x).any (·.adopter == b.court) = false) :
    (canChangeStatus L b x dom).map (·.1) = some false := by
  unfold canChangeStatus
  simp only [hB, hX, Option.map_some]
  have h1 : (B.system == X.system) = false := by simpa using hs
  have h2 : (B.court == X.court) = false := by simpa using hc
  congr 1
  split
  · rfl
  simp [hsc, h1, h2, hA]


/-! ## Round 9 (`round9/DESIGN9.md` §6, D9-6): adoption by a successor court of like jurisdiction

New Jersey's rule is carried by data (adoption rows `1099 ← 1095`, `1222 ← 1206`); these two theorems state what the
existing `canChangeStatus` does with such a row, for any court system. -/

/-- **An adopter of the target's dated tier holds the adopted decision as its own**: an adopter that is not a court
of last resort, not the target's court, not above the target in its system, and of the target's dated tier or above,
under a soft or no horizontal rule, has power (*In re Estate of Johnson*, 240 N.J. Super. 134 (App. Div. 1990)). -/
theorem adoptedSameTier_power (L : Lookups) (b x : Decision) (dom? : Option Domain) (B X : CourtEpoch)
    (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X) (hd : x.date ≤ b.date)
    (hs : B.scotus = false) (hl : B.tier ≠ .last) (hc : B.court ≠ X.court)
    (hh : ¬(B.system = X.system ∧ X.tier.rank < B.tier.rank))
    (ha : (adoptionsOf L x).any (·.adopter == b.court) = true) (ht : X.tier.rank ≤ B.tier.rank)
    (hr : L.rules.horizontal B.court B.system x.date = some .none ∨
      L.rules.horizontal B.court B.system x.date = some .soft) :
    canChangeStatus L b x dom? = some (true, .sameCourtSoft) := by
  have hlt : ¬ b.date < x.date := Nat.not_lt.mpr hd
  have hl' : (B.tier == Tier.last) = false := by simpa using hl
  have hc' : (B.court == X.court) = false := by simpa using hc
  have hsys : (B.system == X.system && decide (X.tier.rank < B.tier.rank)) = false := by
    by_cases he : B.system = X.system
    · have hn : ¬ X.tier.rank < B.tier.rank := fun h => hh ⟨he, h⟩
      simp [he, hn]
    · simp [he]
  have hdt : decide (X.tier.rank ≤ B.tier.rank) = true := decide_eq_true ht
  have hbr : benchRule L B B b { x with unit := none } = (true, .sameCourtSoft) := by
    unfold benchRule
    rcases hr with hr | hr <;> simp [hr]
  unfold canChangeStatus
  simp only [hB, hX, hlt, hs, hsys, hl', hc', ha, hdt, hbr, Bool.false_and, Bool.and_false, Bool.true_and,
    Bool.and_self, Bool.false_eq_true, ↓reduceIte, if_false]

/-- **No power below the target's dated tier**: a court ranked below the target's dated tier (the Supreme Court of the
United States aside) has no power over it, whatever the adoption rows say (the Appellate Division under the Court of
Errors and Appeals; Kentucky 1976). -/
theorem adopted_lowerTier_noPower (L : Lookups) (b x : Decision) (dom? : Option Domain) (B X : CourtEpoch)
    (hB : L.epochAt b.court b.date = some B) (hX : L.epochAt x.court x.date = some X) (hs : B.scotus = false)
    (hlow : B.tier.rank < X.tier.rank) :
    (canChangeStatus L b x dom?).map (·.1) = some false := by
  have hBl : B.tier ≠ .last := by
    intro h
    rw [h] at hlow
    cases hx : X.tier <;> simp [Tier.rank, hx] at hlow
  have hl' : (B.tier == Tier.last) = false := by simpa using hBl
  have hd1 : decide (X.tier.rank < B.tier.rank) = false := decide_eq_false (by omega)
  have hd2 : decide (X.tier.rank ≤ B.tier.rank) = false := decide_eq_false (by omega)
  unfold canChangeStatus
  simp only [hB, hX, hs, hd1, hd2, hl', Bool.false_and, Bool.and_false, Bool.false_eq_true, ↓reduceIte, if_false]
  split <;> (try split) <;> rfl

end CaseLaw2.Spec
