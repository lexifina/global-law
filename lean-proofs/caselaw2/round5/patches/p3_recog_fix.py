"""Round 5 patch 3: recognised_neg_from_witness proof."""
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
("""  have h0 : tr.date ≤ t := Nat.le_trans hd h1
  by_cases ha : tr.kind = .abrogated <;>
    simp [recogEffects, hr, he, hc, hp, hk, hd, hs, hY, hW, status, Effect.contrib, Effect.live, h0, h1, hu,
      minOpt, ha, Status.join, Status.rank, Unk.idx, Neg.idx, TKind.changesStatus]""",
"""  have h0 : tr.date ≤ t := Nat.le_trans hd h1
  unfold recogEffects
  rw [hr]
  simp only [he, hc, hp, hd, hk, hY, hW, minOpt, Bool.not_false, Bool.and_self, decide_true, ↓reduceIte]
  rw [status_cons, status_cons]
  simp [status, Effect.contrib, Effect.live, hs, h0, h1, hu, Status.join_unknown_neg]"""),
("""theorem Status.partially_rank (s : Status) : s.partially.rank < 10 := by""",
"""theorem Status.join_unknown_neg (q : Unk) (n : Neg) : (Status.unknown q).join (.neg n) = .neg n := by
  cases q <;> cases n <;> rfl

theorem Status.partially_rank (s : Status) : s.partially.rank < 10 := by"""),
])
print("patched")
