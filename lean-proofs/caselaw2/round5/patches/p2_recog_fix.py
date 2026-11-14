"""Round 5 patch 2: proof fixes in Spec/Recognised.lean after the first build."""
import os
LP = r"~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2"


def rw(p, pairs):
    p = os.path.join(LP, p)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:60], s.count(a))
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


rw("Spec/Recognised.lean", [
("""  · exact h
  · rw [h] at ha; simp [Status.rank] at ha""",
"""  · exact h
  · rw [h] at ha; simp only [Status.rank] at ha; omega"""),
("""/-- Before date(W) the recognised effects are not negative. -/
theorem recognised_rank_before_witness (byHist wHist : List HEvent) (tr : TEvent) (r : Recog)
    (hr : tr.recog = some r) (k : Nat) (t u : Date) (ht : t < r.date) :
    (status (recogEffects byHist wHist tr) k t u).rank < 10 := by
  unfold recogEffects
  rw [hr]
  simp only []
  split
  · rw [status_cons, status_cons]
    have h2 : Effect.contrib _ k t u = .good := contrib_before_start _ k t u (by simpa using ht)
    rw [h2]
    simp only [status, List.foldl_nil, Status.join_good]
    by_cases hk : tr.powerKnown = true
    · exact contrib_unknown_rank _ .recognisedLater (by simp [hk]) k t u
    · exact contrib_unknown_rank _ .powerUnknown (by simp [hk]) k t u
  · simp [status, Status.rank]""",
"""/-- The shape of a recognised row's effects: none, or two: the first imposes an unknown, the second starts on
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
    exact contrib_unknown_rank e1 q h1 k t u"""),
("""    simp [recogEffects, hr, he, hc, hp, hk, hd, hs, hY, hW, status, Effect.contrib, Effect.live, h0, h1, hu,
      minOpt, ha, Status.join, Status.rank, Unk.idx, Neg.idx]""",
"""    simp [recogEffects, hr, he, hc, hp, hk, hd, hs, hY, hW, status, Effect.contrib, Effect.live, h0, h1, hu,
      minOpt, ha, Status.join, Status.rank, Unk.idx, Neg.idx, TKind.changesStatus]"""),
("""  · by_cases hk : tr.powerKnown = true <;> simp [hk, Status.rank, Unk.idx, Neg.idx]
  · by_cases hk : tr.powerKnown = true <;> simp [hk]
  · by_cases hk : tr.powerKnown = true <;> simp [hk]""",
"""  · by_cases hk : tr.powerKnown = true
    · simp only [hk, ↓reduceIte, Status.rank, Unk.idx]; omega
    · simp [hk, Status.rank, Unk.idx]
  · by_cases hk : tr.powerKnown = true <;> simp [hk]
  · by_cases hk : tr.powerKnown = true <;> simp [hk]"""),
])
print("patched")
