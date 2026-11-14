import LegalProofs.CaseLaw2.Spec.Status

/-!
# Spec: recognised overrulings and operative words (round 5; DESIGN5.md §2, §3)

*Brown v. Board of Education* never says it overrules *Plessy v. Ferguson*. Through round 4 a status changed only on
the overruling court's own words, so *Plessy* stayed good law with an "at risk" note. Round 5 admits one more
source of words: a **later decision W of a court that itself has power to overrule X** saying, in a certified
majority sentence, that X was overruled by Y. `Spec.recogEffects` (in `Status.lean`, next to the other effect
compilers) turns such a row into two effects; the theorems here say what they can and cannot do:

* nothing is negative before date(W) on the row's account (`recognised_never_neg_before_witness`);
* nothing at all without W's power, without the recognition, or on an explicit row (`recognised_needs_power`,
  `witness_without_claim_no_effect`, `recognised_not_explicit`);
* the order of rows still does not matter (`status_append_comm`; `status_perm` is unchanged);
* an explicit row and a recognised row for the same pair agree from date(W) (`explicit_recognised_agree_from_witness`);
* a recognised row never weakens what is already there (`recognised_never_weakens`);
* the timeline: unknown between Y and W, negative from W (`recognised_unknown_between`, `recognised_neg_from_witness`).

For operative words that do not dispose of a case as a whole the scope is demoted (`demote`): the target is partly
negative, never overruled (`demoted_never_neg`).
-/

namespace CaseLaw2.Spec
open CaseLaw2

/-! ## Generic lemmas -/

theorem Status.join_self (a : Status) : a.join a = a := by
  unfold Status.join; simp

/-- A join is negative only if a side is; when the left side is not negative, it is the right side. -/
theorem Status.join_eq_neg_right {a b : Status} {n : Neg} (ha : a.rank < 10) (h : a.join b = .neg n) :
    b = .neg n := by
  unfold Status.join at h
  split at h
  · exact h
  · rw [h] at ha; simp only [Status.rank] at ha; omega

theorem Status.join_unknown_neg (q : Unk) (n : Neg) : (Status.unknown q).join (.neg n) = .neg n := by
  cases q <;> cases n <;> rfl

theorem Status.partially_rank (s : Status) : s.partially.rank < 10 := by
  cases s <;> simp [Status.partially, Status.rank, Unk.idx]

/-- The status of two lists of effects together is the join of their statuses. -/
theorem status_append (a l : List Effect) (k : Nat) (t u : Date) :
    status (a ++ l) k t u = (status a k t u).join (status l k t u) := by
  induction a with
  | nil => simp [status]
  | cons e a ih => rw [List.cons_append, status_cons, status_cons, ih, Status.join_assoc]

/-- **Order independence across groups of effects** (round 5): the effects of a recognised row, of an explicit row
and of anything else may be taken in any order (a corollary of `status_perm`). -/
theorem status_append_comm (a b l : List Effect) (k : Nat) (t u : Date) :
    status (a ++ b ++ l) k t u = status (b ++ a ++ l) k t u :=
  status_perm (List.Perm.append_right l List.perm_append_comm) k t u

/-- Adding effects never makes a status less severe. -/
theorem status_append_rank_le (a l : List Effect) (k : Nat) (t u : Date) :
    (status l k t u).rank ≤ (status (a ++ l) k t u).rank := by
  rw [status_append, Status.rank_join]; omega

/-- An effect that imposes an unknown never contributes a negative. -/
theorem contrib_unknown_rank (e : Effect) (r : Unk) (he : e.eff = .unknown r) (k : Nat) (t u : Date) :
    (e.contrib k t u).rank < 10 := by
  unfold Effect.contrib
  split
  · split
    · rw [he]; cases r <;> simp [Status.rank, Unk.idx]
    · split
      · rw [he]; cases r <;> simp [Status.rank, Unk.idx]
      · split
        · exact Status.partially_rank _
        · simp [Status.rank]
    · exact Status.partially_rank _
    · split
      · exact Status.partially_rank _
      · simp [Status.rank]
  · simp [Status.rank]

/-- An effect that has not started contributes nothing. -/
theorem contrib_before_start (e : Effect) (k : Nat) (t u : Date) (ht : t < e.start) : e.contrib k t u = .good := by
  have h1 : ¬ e.start ≤ t := Nat.not_le.mpr ht
  simp [Effect.contrib, Effect.live, h1]

/-- Two effects with the same scope that are live together, the second at least as severe and neither `good`: the
second decides. -/
theorem contrib_join_dominated (a b : Effect) (k : Nat) (t u : Date) (hs : a.scope = b.scope)
    (hl : a.live t u = b.live t u) (hr : a.eff.rank ≤ b.eff.rank) (ha : a.eff ≠ .good) (hb : b.eff ≠ .good) :
    (a.contrib k t u).join (b.contrib k t u) = b.contrib k t u := by
  have hp : a.eff.partially = b.eff.partially := by
    cases hae : a.eff <;> cases hbe : b.eff <;> simp_all [Status.partially]
  have hj : a.eff.join b.eff = b.eff := by simp [Status.join, hr]
  unfold Effect.contrib
  rw [hl, hs]
  split
  · split
    · exact hj
    · split
      · exact hj
      · split
        · rw [hp, Status.join_self]
        · rfl
    · rw [hp, Status.join_self]
    · split
      · rw [hp, Status.join_self]
      · rfl
  · rfl

/-- Effects that agree on what they impose, on their scope and on being live contribute the same. -/
theorem contrib_congr (a b : Effect) (k : Nat) (t u : Date) (he : a.eff = b.eff) (hs : a.scope = b.scope)
    (hl : a.live t u = b.live t u) : a.contrib k t u = b.contrib k t u := by
  unfold Effect.contrib; rw [he, hs, hl]

/-! ## Recognised overrulings -/

/-- **Never without W's power**: a row whose recognising court lacks power over the target has no effect. -/
theorem recognised_needs_power (byHist wHist : List HEvent) (tr : TEvent) (r : Recog) (hr : tr.recog = some r)
    (hp : r.power = false) : recogEffects byHist wHist tr = [] := by
  simp [recogEffects, hr, hp]

/-- **A witness row without recognition has no status effect**: the round-4 "at risk" tier is unchanged. -/
theorem witness_without_claim_no_effect (byHist wHist : List HEvent) (tr : TEvent) (h : tr.recog = none) :
    recogEffects byHist wHist tr = [] := by
  simp [recogEffects, h]

/-- **A row is explicit or recognised, never both**: an explicit row has no recognised effects (its effects are
`treatEffects`; with `inferred_treatment_no_effect` each row has one source of effects at most). -/
theorem recognised_not_explicit (byHist wHist : List HEvent) (tr : TEvent) (h : tr.explicit = true) :
    recogEffects byHist wHist tr = [] := by
  unfold recogEffects
  cases tr.recog <;> simp [h]

/-- The shape of a recognised row's effects: none, or two: the first imposes an unknown, the second starts on
date(W). -/
theorem recogEffects_shape (byHist wHist : List HEvent) (tr : TEvent) (r : Recog) (hr : tr.recog = some r) :
    recogEffects byHist wHist tr = [] ∨
      ∃ e1 e2 q, recogEffects byHist wHist tr = [e1, e2] ∧ e1.eff = .unknown q ∧ e2.start = r.date := by
  unfold recogEffects
  rw [hr]
  simp only []
  split
  · right
    by_cases hk : tr.powerKnown = true
    · exact ⟨_, _, .recognisedLater, rfl, by simp [hk], rfl⟩
    · exact ⟨_, _, .powerUnknown, rfl, by simp [hk], rfl⟩
  · left; rfl

/-- Before date(W) the recognised effects are not negative. -/
theorem recognised_rank_before_witness (byHist wHist : List HEvent) (tr : TEvent) (r : Recog)
    (hr : tr.recog = some r) (k : Nat) (t u : Date) (ht : t < r.date) :
    (status (recogEffects byHist wHist tr) k t u).rank < 10 := by
  rcases recogEffects_shape byHist wHist tr r hr with h | ⟨e1, e2, q, h, h1, h2⟩
  · rw [h]; simp [status, Status.rank]
  · rw [h, status_cons, status_cons, contrib_before_start e2 k t u (by rw [h2]; exact ht)]
    simp only [status, List.foldl_nil, Status.join_good]
    exact contrib_unknown_rank e1 q h1 k t u

/-- **Never negative before date(W) on a recognised row**: if the status is negative on a question date before the
recognising decision, the negative comes from the other effects, not from the recognised row. -/
theorem recognised_never_neg_before_witness (byHist wHist : List HEvent) (tr : TEvent) (r : Recog)
    (hr : tr.recog = some r) (l : List Effect) (k : Nat) (t u : Date) (ht : t < r.date) (n : Neg)
    (h : status (recogEffects byHist wHist tr ++ l) k t u = .neg n) : status l k t u = .neg n := by
  rw [status_append] at h
  exact Status.join_eq_neg_right (recognised_rank_before_witness byHist wHist tr r hr k t u ht) h

/-- **A recognised row never weakens an existing status**: with the row, the status is at least as severe. -/
theorem recognised_never_weakens (byHist wHist : List HEvent) (tr : TEvent) (l : List Effect) (k : Nat)
    (t u : Date) : (status l k t u).rank ≤ (status (recogEffects byHist wHist tr ++ l) k t u).rank :=
  status_append_rank_le _ l k t u

/-- What a status-changing row imposes when its power is verified. -/
def negOf (tr : TEvent) : Status :=
  if tr.powerKnown then .neg (if tr.kind == .abrogated then .abrogated else .overruled) else .unknown .powerUnknown

/-- **The timeline, between Y and W**: with verified power, on the whole decision, while Y stands, the status
from date(Y) up to the day before date(W) is `unknown recognisedLater`. -/
theorem recognised_unknown_between (byHist wHist : List HEvent) (tr : TEvent) (r : Recog)
    (hr : tr.recog = some r) (he : tr.explicit = false) (hc : tr.kind.changesStatus = true) (hp : r.power = true)
    (hk : tr.powerKnown = true) (hs : tr.scope = .all) (hY : lapseOfDecision byHist tr.date = none)
    (k : Nat) (t u : Date) (h1 : tr.date ≤ t) (h2 : t < r.date)
    (hu : temporalConductFrom tr.temporal tr.date ≤ u) :
    status (recogEffects byHist wHist tr) k t u = .unknown .recognisedLater := by
  have hd : tr.date ≤ r.date := Nat.le_of_lt (Nat.lt_of_le_of_lt h1 h2)
  have h2' : ¬ r.date ≤ t := Nat.not_le.mpr h2
  simp [recogEffects, hr, he, hc, hp, hk, hd, hs, hY, status, Effect.contrib, Effect.live, h1, h2', hu, minOpt]

/-- **The timeline, from W**: with verified power, on the whole decision, while Y and W stand, the status from
date(W) is negative: overruled (abrogated for an `abrogated` row). -/
theorem recognised_neg_from_witness (byHist wHist : List HEvent) (tr : TEvent) (r : Recog)
    (hr : tr.recog = some r) (he : tr.explicit = false) (hc : tr.kind.changesStatus = true) (hp : r.power = true)
    (hk : tr.powerKnown = true) (hs : tr.scope = .all) (hd : tr.date ≤ r.date)
    (hY : lapseOfDecision byHist tr.date = none) (hW : lapseOfDecision wHist r.date = none)
    (k : Nat) (t u : Date) (h1 : r.date ≤ t) (hu : temporalConductFrom tr.temporal tr.date ≤ u) :
    status (recogEffects byHist wHist tr) k t u =
      .neg (if tr.kind == .abrogated then .abrogated else .overruled) := by
  have h0 : tr.date ≤ t := Nat.le_trans hd h1
  unfold recogEffects
  rw [hr]
  simp only [he, hc, hp, hd, hk, hY, hW, minOpt, Bool.not_false, Bool.and_self, decide_true, ↓reduceIte]
  rw [status_cons, status_cons]
  simp [status, Effect.contrib, Effect.live, hs, h0, h1, hu, Status.join_unknown_neg]

/-- **An explicit row and a recognised row for the same pair agree from date(W)**: the same by-decision, target,
kind, scope and temporal reach, once as the overruling court's own words and once as a later court's recognition,
give the same status on every question date from date(W) on, while neither Y nor W has lapsed. -/
theorem explicit_recognised_agree_from_witness (byHist wHist : List HEvent) (tr : TEvent) (r : Recog)
    (he : tr.explicit = true) (hc : tr.kind.changesStatus = true) (hp : r.power = true) (hd : tr.date ≤ r.date)
    (hY : lapseOfDecision byHist tr.date = none) (hW : lapseOfDecision wHist r.date = none)
    (k : Nat) (t u : Date) (ht : r.date ≤ t) :
    status (treatEffects byHist tr) k t u =
      status (recogEffects byHist wHist { tr with explicit := false, recog := some r }) k t u := by
  have h0 : tr.date ≤ t := Nat.le_trans hd ht
  simp only [treatEffects, treatEffect, he, hc, Bool.and_self, ↓reduceIte, hY, Option.bind_none, recogEffects,
    Bool.not_false, hp, hd, decide_true, Bool.true_and, minOpt, hW]
  rw [status_cons, status_cons, status_cons]
  simp only [status, List.foldl_nil, Status.join_good]
  rw [contrib_join_dominated]
  · apply contrib_congr
    · rfl
    · rfl
    · simp [Effect.live, h0, ht]
  · rfl
  · simp [Effect.live, h0, ht]
  · by_cases hk : tr.powerKnown = true
    · simp only [hk, ↓reduceIte, Status.rank, Unk.idx]; omega
    · simp [hk, Status.rank, Unk.idx]
  · by_cases hk : tr.powerKnown = true <;> simp [hk]
  · by_cases hk : tr.powerKnown = true <;> simp [hk]

/-! ## Operative words: demoted scope -/

/-- **A demoted effect never makes anything negative** (DESIGN5 §3.3): operative words that do not dispose of the
case as a whole leave the target partly negative (`unknown partialScope`) at most. -/
theorem demoted_never_neg (e : Effect) (s : Scope) (h : e.scope = demote s) (k : Nat) (t u : Date) :
    (e.contrib k t u).rank < 10 := by
  unfold Effect.contrib
  split
  · rw [h]
    cases s with
    | all => exact Status.partially_rank _
    | issues ks =>
      simp only [demote]
      split
      · exact Status.partially_rank _
      · simp [Status.rank]
    | someIssue => exact Status.partially_rank _
    | someOf ks =>
      simp only [demote]
      split
      · exact Status.partially_rank _
      · simp [Status.rank]
  · simp [Status.rank]

/-- So the status of a list of demoted effects is never negative. -/
theorem demoted_status_never_neg (l : List Effect) (h : ∀ e ∈ l, ∃ s, e.scope = demote s) (k : Nat) (t u : Date) :
    (status l k t u).rank < 10 := by
  induction l with
  | nil => simp [status, Status.rank]
  | cons e l ih =>
    rw [status_cons, Status.rank_join]
    obtain ⟨s, hs⟩ := h e (by simp)
    have h1 := demoted_never_neg e s hs k t u
    have h2 := ih (fun e he => h e (by simp [he]))
    omega

/-! ## Round 7: doctrine rows (`round7/DESIGN7.md` §2.4)

A doctrine row ("the doctrine of 'separate but equal' has no place", tied to *Plessy* by a second quote of the same
opinion) rejects a doctrine, not a case as a whole: its effects are always demoted, whatever the scope written. -/

/-- The event of an admitted doctrine row: its scope demoted (the runner applies this to every event the row
yields, after the issue/power splitting). -/
def doctrineEvent (tr : TEvent) : TEvent := { tr with scope := demote tr.scope }

/-- The effects of a doctrine row. -/
def doctrineEffects (byHist : List HEvent) (tr : TEvent) : List Effect := treatEffects byHist (doctrineEvent tr)

/-- What a partial event says is good or `unknown partialScope`. -/
theorem Status.partially_rank_le (s : Status) : s.partially.rank ≤ 1 := by
  cases s <;> simp [Status.partially, Status.rank, Unk.idx]

/-- A treatment's effect has the treatment's scope. -/
theorem treatEffect_scope (byHist : List HEvent) (tr : TEvent) (e : Effect) (h : treatEffect byHist tr = some e) :
    e.scope = tr.scope := by
  unfold treatEffect at h
  split at h
  · cases h; rfl
  · cases h

/-- Every effect of a treatment (the effect, and its revival) has the treatment's scope. -/
theorem treatEffects_scope (byHist : List HEvent) (tr : TEvent) : ∀ e ∈ treatEffects byHist tr, e.scope = tr.scope := by
  intro e he
  unfold treatEffects at he
  split at he
  · simp at he
  · rename_i e0 h0
    split at he
    · rcases List.mem_cons.mp he with h | h
      · rw [h]; exact treatEffect_scope _ _ _ h0
      · simp at h
        obtain ⟨a, ha, rfl⟩ := h
        exact treatEffect_scope _ tr a ha
    · rcases List.mem_singleton.mp he with h
      rw [h]; exact treatEffect_scope _ _ _ h0

/-- **Every effect of a doctrine row has a demoted scope.** -/
theorem doctrine_effects_demoted (byHist : List HEvent) (tr : TEvent) :
    ∀ e ∈ doctrineEffects byHist tr, ∃ s, e.scope = demote s :=
  fun e he => ⟨tr.scope, treatEffects_scope byHist (doctrineEvent tr) e he⟩

/-- A demoted effect contributes `good` or `unknown partialScope`. -/
theorem demoted_contrib_le (e : Effect) (s : Scope) (h : e.scope = demote s) (k : Nat) (t u : Date) :
    (e.contrib k t u).rank ≤ 1 := by
  unfold Effect.contrib
  split
  · rw [h]
    cases s with
    | all => exact Status.partially_rank_le _
    | issues ks =>
      simp only [demote]
      split
      · exact Status.partially_rank_le _
      · simp [Status.rank]
    | someIssue => exact Status.partially_rank_le _
    | someOf ks =>
      simp only [demote]
      split
      · exact Status.partially_rank_le _
      · simp [Status.rank]
  · simp [Status.rank]

/-- So the status of a list of demoted effects is `good` or `unknown partialScope` (rank at most 1). -/
theorem demoted_status_le (l : List Effect) (h : ∀ e ∈ l, ∃ s, e.scope = demote s) (k : Nat) (t u : Date) :
    (status l k t u).rank ≤ 1 := by
  induction l with
  | nil => simp [status, Status.rank]
  | cons e l ih =>
    rw [status_cons, Status.rank_join]
    obtain ⟨s, hs⟩ := h e (by simp)
    have h1 := demoted_contrib_le e s hs k t u
    have h2 := ih (fun e he => h e (by simp [he]))
    omega

/-- **A doctrine row never makes a status negative**: with any other effects, a negative status is theirs; alone,
the row gives at most `unknown partialScope` (DESIGN7 §2.4). -/
theorem doctrine_never_neg (byHist : List HEvent) (tr : TEvent) (l : List Effect) (k : Nat) (t u : Date) :
    (∀ n, status (doctrineEffects byHist tr ++ l) k t u = .neg n → status l k t u = .neg n) ∧
      (status (doctrineEffects byHist tr) k t u = .good ∨
        status (doctrineEffects byHist tr) k t u = .unknown .partialScope) := by
  have hd := doctrine_effects_demoted byHist tr
  refine ⟨fun n hn => ?_, ?_⟩
  · rw [status_append] at hn
    exact Status.join_eq_neg_right (demoted_status_never_neg _ hd k t u) hn
  · have hle := demoted_status_le _ hd k t u
    cases hs : status (doctrineEffects byHist tr) k t u with
    | good => exact Or.inl rfl
    | unknown r =>
      right
      rw [hs] at hle
      cases r <;> simp_all [Status.rank, Unk.idx]
    | neg n =>
      rw [hs] at hle
      simp only [Status.rank] at hle
      omega

end CaseLaw2.Spec
