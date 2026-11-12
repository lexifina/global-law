/-!
# US case law: courts, and who is bound by whom

The doctrine of precedent as rules over courts, for every court in the US case law of global-law (federal, the fifty
states, the District of Columbia and the territories).

* A **system** is the federal courts or one state's (or territory's) courts. Each court sits in one system.
* A **tier**: the court of last resort, an intermediate appellate court, a trial court, or a special court
  (bankruptcy, tax, claims, military, tribal…), which this model treats like a trial court of its system.
* A federal court also has a **circuit** (1–11, 12 = D.C., 13 = Federal Circuit); 0 elsewhere.

Rules (vertical and horizontal *stare decisis*):
* `binds a b`: decisions of court `a` bind court `b`.
  - The US Supreme Court binds every court (on federal law, the only law it decides for the states).
  - A court of last resort binds every court of its system.
  - A federal court of appeals binds the district and special courts of its circuit, and itself.
  - A state intermediate appellate court binds the trial courts of its state (the majority rule; some states limit
    this to a district or division, which the model does not see) and itself.
  - A court of last resort binds itself.
* `mayOverrule a b`: court `a` has power to overrule a decision of court `b`: same system, and `a` is `b` or ranks
  above it. A court can never overrule a decision that binds it, unless it is the same court
  (`no_overrule_of_binding_superior`).
-/

namespace Legal.USCaseLaw

inductive Tier where
  | last | appellate | trial | special
  deriving Repr, DecidableEq, Inhabited

/-- Rank within a system: higher binds lower. Special courts rank with trial courts. -/
def Tier.rank : Tier → Nat
  | .last => 3
  | .appellate => 2
  | .trial => 1
  | .special => 1

structure Court where
  /-- Index of the court in the court table (`Courts.tsv`). -/
  id : Nat
  /-- 0 = the federal courts; otherwise the state, DC or territory (its index in the system table). -/
  system : Nat
  tier : Tier
  /-- Federal courts: circuit 1–13; 0 for the Supreme Court, national courts and every state court. -/
  circuit : Nat := 0
  deriving Repr, DecidableEq, Inhabited

def Court.federal (c : Court) : Bool := c.system == 0
def Court.scotus (c : Court) : Bool := c.federal && c.tier == .last

/-- Decisions of court `a` bind court `b`. -/
def binds (a b : Court) : Bool :=
  a.scotus ||
  (a.system == b.system && a.tier == .last) ||
  (a.id == b.id && a.tier == .appellate) ||
  (a.system == b.system && a.tier == .appellate && b.tier.rank < 2 &&
    (!a.federal || (a.circuit != 0 && a.circuit == b.circuit)))

/-- Court `a` may overrule a decision of court `b`. -/
def mayOverrule (a b : Court) : Bool :=
  a.system == b.system && (a.id == b.id || b.tier.rank < a.tier.rank) &&
  -- a federal court of appeals overrules only decisions of its own circuit
  (!a.federal || a.tier != .appellate || b.circuit == a.circuit)

theorem scotus_binds_all (a b : Court) (h : a.scotus = true) : binds a b = true := by
  simp [binds, h]

theorem last_binds_own_system (a b : Court) (hs : a.system = b.system) (ht : a.tier = .last) :
    binds a b = true := by
  simp [binds, hs, ht]

/-- A court never has power over the decisions of a court that binds it, unless it is that court. -/
theorem no_overrule_of_binding_superior (a b : Court) (hab : a.id ≠ b.id)
    (hrank : a.tier.rank < b.tier.rank) : mayOverrule a b = false := by
  unfold mayOverrule
  have : ¬ b.tier.rank < a.tier.rank := by omega
  simp [hab, this]

/-- Only the Supreme Court may overrule the Supreme Court. -/
theorem only_scotus_overrules_scotus (a b : Court) (hb : b.scotus = true) (h : mayOverrule a b = true) :
    a.id = b.id := by
  unfold mayOverrule at h
  unfold Court.scotus Court.federal at hb
  simp at h hb
  obtain ⟨⟨_, h2⟩, _⟩ := h
  rcases h2 with h2 | h2
  · exact h2
  · have hbt : b.tier = .last := by simpa using hb.2
    rw [hbt] at h2; cases ht : a.tier <;> simp [Tier.rank, ht] at h2

/-- A state court never overrules a federal decision, and a federal court never overrules a state decision. -/
theorem no_cross_system (a b : Court) (h : a.system ≠ b.system) : mayOverrule a b = false := by
  simp [mayOverrule, h]

end Legal.USCaseLaw
