import LegalProofs.USCaseLaw.Courts

/-!
# US case law: decisions, overruling and good law

Facts of a decision: its court, the day it was decided (`yyyymmdd`), the decisions it cites, and the decisions it says
it overrules (an `Overruling` event, read from the overruling decision's own words). Rules:

* An overruling is **valid** when the overruling court has power over the overruled decision's court
  (`mayOverrule`) and the overruled decision is not later than the overruling one.
* A decision is **overruled on a day** `d` when a valid overruling of it was decided on or before `d`
  (`overruledOn`); once overruled it stays overruled (`overruledOn_mono`). Partial overruling, overruling "on other
  grounds" and revival are not modelled: the model answers only whether a court with power said it overruled the
  decision.
* Checks run on every decision (`Findings`):
  - it cites a decision decided after it (`citesLater`);
  - it claims to overrule a decision its court has no power over (`invalidOverrulings`);
  - it cites a decision that a court binding it had already overruled (`citesOverruled`). Citing an overruled case
    is not wrong in itself (a court may cite it to say so), so these are counted, not called errors.
-/

namespace Legal.USCaseLaw

structure Decision where
  id : Nat
  court : Court
  /-- Day decided, `yyyymmdd`; a month-only date is the 1st, a year-only date 1 January. -/
  date : Nat
  cites : List Nat := []
  deriving Repr, Inhabited

/-- Decision `by_` says it overrules decision `target`. -/
structure Overruling where
  by_ : Nat
  target : Nat
  deriving Repr, Inhabited, DecidableEq

/-- The record: every decision, and every overruling event. `dec i` is decision `i` (a default when missing). -/
structure Record where
  dec : Nat → Decision
  events : List Overruling

def Record.valid (r : Record) (e : Overruling) : Bool :=
  mayOverrule (r.dec e.by_).court (r.dec e.target).court && (r.dec e.target).date ≤ (r.dec e.by_).date

/-- The valid overrulings of `x` decided on or before day `d`. -/
def Record.overrulersOn (r : Record) (x d : Nat) : List Overruling :=
  r.events.filter (fun e => e.target == x && r.valid e && (r.dec e.by_).date ≤ d)

def Record.overruledOn (r : Record) (x d : Nat) : Bool := !(r.overrulersOn x d).isEmpty

/-- Once overruled, always overruled (no revival in the model). -/
theorem Record.overruledOn_mono (r : Record) (x d d' : Nat) (hle : d ≤ d') (h : r.overruledOn x d = true) :
    r.overruledOn x d' = true := by
  unfold Record.overruledOn Record.overrulersOn at *
  simp [List.filter_eq_nil_iff] at *
  obtain ⟨e, he, h1, h2, h3⟩ := h
  exact ⟨e, he, h1, h2, by omega⟩

/-- An overruling by a court bound by the overruled decision's court is never valid (unless the same court). -/
theorem Record.invalid_from_below (r : Record) (e : Overruling)
    (hid : (r.dec e.by_).court.id ≠ (r.dec e.target).court.id)
    (hr : (r.dec e.by_).court.tier.rank < (r.dec e.target).court.tier.rank) : r.valid e = false := by
  unfold Record.valid
  rw [no_overrule_of_binding_superior _ _ hid hr]
  simp

/-- A decision of the Supreme Court is overruled only by the Supreme Court. -/
theorem Record.scotus_overruled_only_by_scotus (r : Record) (x d : Nat) (hx : (r.dec x).court.scotus = true)
    (e : Overruling) (he : e ∈ r.overrulersOn x d) : (r.dec e.by_).court.id = (r.dec x).court.id := by
  unfold Record.overrulersOn Record.valid at he
  simp at he
  obtain ⟨_, ⟨ht, hv, _⟩, _⟩ := he
  subst ht
  exact only_scotus_overrules_scotus _ _ hx hv

/-! ## Citation order -/

/-- Every citation points to a decision decided on or before the citing one. -/
def Record.citesBackward (r : Record) (ids : List Nat) : Prop :=
  ∀ i ∈ ids, ∀ j ∈ (r.dec i).cites, (r.dec j).date ≤ (r.dec i).date

/-- A chain of citations `i₀ → i₁ → … → iₙ` (each cites the next). -/
def Record.chain (r : Record) : List Nat → Prop
  | [] => True
  | [_] => True
  | i :: j :: rest => j ∈ (r.dec i).cites ∧ r.chain (j :: rest)

/-- Along a citation chain dates never increase, so no decision can rely, through any chain, on a later one, and a
    citation cycle can only join decisions of one day. -/
theorem Record.chain_dates (r : Record) (hb : ∀ i, ∀ j ∈ (r.dec i).cites, (r.dec j).date ≤ (r.dec i).date) :
    ∀ (l : List Nat) (i k : Nat), r.chain (i :: l) → (l.getLast? = some k) → (r.dec k).date ≤ (r.dec i).date
  | [], _, _, _, h => by simp at h
  | j :: rest, i, k, hc, hk => by
    obtain ⟨hij, hrest⟩ := hc
    have h1 := hb i j hij
    cases rest with
    | nil => simp at hk; subst hk; exact h1
    | cons m rest' =>
      have hk' : (m :: rest').getLast? = some k := by simpa [List.getLast?_cons_cons] using hk
      have := Record.chain_dates r hb (m :: rest') j k hrest hk'
      omega

/-! ## Findings for one decision -/

structure Findings where
  citesLater : List Nat := []
  invalidOverrulings : List Nat := []
  citesOverruled : List (Nat × Nat) := []   -- (cited decision, the earlier binding overruling decision)
  deriving Repr, Inhabited

def Record.findings (r : Record) (i : Nat) : Findings :=
  let y := r.dec i
  { citesLater := y.cites.filter (fun j => y.date < (r.dec j).date)
    invalidOverrulings := (r.events.filter (fun e => e.by_ == i && !r.valid e)).map (·.target)
    citesOverruled := y.cites.filterMap (fun j =>
      match (r.overrulersOn j y.date).find? (fun e =>
          (r.dec e.by_).date < y.date && binds (r.dec e.by_).court y.court) with
      | some e => some (j, e.by_)
      | none => none) }

end Legal.USCaseLaw
