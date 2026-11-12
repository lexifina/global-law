import LegalProofs.USCaseLaw.StatuteText

/-!
# Congress answering a court: override candidates

`StatuteText.lean` says whether the words a decision cited still read the same. This module asks a narrower question
about the first change to them. A decision decided on day `d` cites a block of a section (the subsection it names, or
the whole section). Walking the section's versions after `d`, the *first rewrite* is the first version whose words of
that block differ from those in force on `d`. When a law (not an edition of the Code) made it, that law is the *first
rewriting law*: the first time Congress touched exactly the words the court read.

An *override candidate* is a citation whose first rewriting law came within a window of `y` years of the decision
(days are `yyyymmdd`, so `d + 10000 * y` is the same day `y` years later), and for which outside evidence points at
the decision: the law's own text names it, a committee report on the law names it, or the decision quoted the words
the law struck. The evidence is read outside Lean and passed in as a flag; Lean decides the rest.

Proved:
* a candidate's law amended the section after the decision and within the window (`candidate_amendedSince`), and the
  words it made differ from those the court read (`candidate_rewrites`);
* widening the window keeps every candidate (`candidate_window_mono`);
* each citation has at most one first rewriting law (`firstRewritingLaw_unique`), and no version between the decision
  and that law changed the cited words (`firstRewrite_first`): it really is the first;
* no evidence, no candidate (`candidate_evidence`).
-/

namespace Legal.USCaseLaw

/-- The first version after `d` (in the history's order) whose words of the cited block differ from those in force on
`d`. None if nothing was in force on `d` or the words never changed. -/
def firstRewrite (h : List SVersion) (d : Nat) : Option SVersion :=
  match sInForceOn h d with
  | none => none
  | some v0 => h.find? (fun v => decide (d < v.from_) && v.sub != v0.sub)

/-- The first rewrite, when a law made it. An edition that first changes the words is not Congress answering the court,
and it also ends the search: the law that comes later rewrote words the court never read. -/
def firstRewritingLaw (h : List SVersion) (d : Nat) : Option SVersion :=
  (firstRewrite h d).filter (·.byLaw)

/-- An override candidate: a first rewriting law within `y` years of the decision, plus outside evidence. -/
def overrideCandidate (h : List SVersion) (d y : Nat) (evidence : Bool) : Bool :=
  match firstRewritingLaw h d with
  | some v => decide (v.from_ ≤ d + 10000 * y) && evidence
  | none => false

theorem firstRewrite_spec {h : List SVersion} {d : Nat} {v : SVersion} (hv : firstRewrite h d = some v) :
    v ∈ h ∧ d < v.from_ ∧ ∃ v0, sInForceOn h d = some v0 ∧ v.sub ≠ v0.sub := by
  unfold firstRewrite at hv
  split at hv
  · simp at hv
  · rename_i v0 h0
    have hm := List.mem_of_find?_eq_some hv
    have hp := List.find?_some hv
    simp at hp
    exact ⟨hm, hp.1, v0, h0, hp.2⟩

theorem firstRewritingLaw_spec {h : List SVersion} {d : Nat} {v : SVersion} (hv : firstRewritingLaw h d = some v) :
    firstRewrite h d = some v ∧ v.byLaw = true := by
  unfold firstRewritingLaw at hv
  cases hf : firstRewrite h d with
  | none => simp [hf] at hv
  | some w =>
    simp [hf, Option.filter] at hv
    obtain ⟨hb, rfl⟩ := hv
    exact ⟨rfl, hb⟩

/-- A candidate's law is in the history, was made by a law, came after the decision and inside the window. -/
theorem candidate_law {h : List SVersion} {d y : Nat} {e : Bool} (hc : overrideCandidate h d y e = true) :
    ∃ v, firstRewritingLaw h d = some v ∧ v ∈ h ∧ v.byLaw = true ∧ d < v.from_ ∧ v.from_ ≤ d + 10000 * y := by
  unfold overrideCandidate at hc
  split at hc
  · rename_i v hv
    simp at hc
    obtain ⟨hf, hb⟩ := firstRewritingLaw_spec hv
    obtain ⟨hm, hlt, _⟩ := firstRewrite_spec hf
    exact ⟨v, hv, hm, hb, hlt, hc.1⟩
  · simp at hc

/-- A candidate implies the section was amended by a law after the decision, within the window. -/
theorem candidate_amendedSince {h : List SVersion} {d y : Nat} {e : Bool} (hc : overrideCandidate h d y e = true) :
    amendedSince h d (d + 10000 * y) = true := by
  obtain ⟨v, _, hm, hb, hlt, hle⟩ := candidate_law hc
  have hmem : v ∈ lawChangesBetween h d (d + 10000 * y) := by
    unfold lawChangesBetween sChangesBetween
    simp [List.mem_filter, hm, hlt, hle, hb]
  unfold amendedSince
  cases hl : lawChangesBetween h d (d + 10000 * y) with
  | nil => simp [hl] at hmem
  | cons _ _ => simp

/-- The candidate's law made words of the cited block that differ from those the court read. -/
theorem candidate_rewrites {h : List SVersion} {d y : Nat} {e : Bool} (hc : overrideCandidate h d y e = true) :
    ∃ v v0, firstRewritingLaw h d = some v ∧ sInForceOn h d = some v0 ∧ v.sub ≠ v0.sub := by
  obtain ⟨v, hv, _⟩ := candidate_law hc
  obtain ⟨hf, _⟩ := firstRewritingLaw_spec hv
  obtain ⟨_, _, v0, h0, hne⟩ := firstRewrite_spec hf
  exact ⟨v, v0, hv, h0, hne⟩

/-- Widening the window keeps every candidate. -/
theorem candidate_window_mono {h : List SVersion} {d y y' : Nat} {e : Bool} (hy : y ≤ y')
    (hc : overrideCandidate h d y e = true) : overrideCandidate h d y' e = true := by
  unfold overrideCandidate at *
  split at hc
  · rename_i v hv
    simp at hc ⊢
    refine ⟨?_, hc.2⟩
    have : 10000 * y ≤ 10000 * y' := Nat.mul_le_mul_left _ hy
    omega
  · simp at hc

/-- No evidence, no candidate. -/
theorem candidate_evidence {h : List SVersion} {d y : Nat} {e : Bool} (hc : overrideCandidate h d y e = true) :
    e = true := by
  unfold overrideCandidate at hc
  split at hc <;> simp_all

/-- At most one first rewriting law per citation. -/
theorem firstRewritingLaw_unique {h : List SVersion} {d : Nat} {v w : SVersion}
    (hv : firstRewritingLaw h d = some v) (hw : firstRewritingLaw h d = some w) : v = w := by
  rw [hv] at hw; exact Option.some.inj hw

/-- It really is the first: every version listed before it that came into force after the decision leaves the cited
words as the court read them. -/
theorem firstRewrite_first {h : List SVersion} {d : Nat} {v v0 : SVersion} (h0 : sInForceOn h d = some v0)
    (hv : firstRewrite h d = some v) :
    ∃ as bs, h = as ++ v :: bs ∧ ∀ u ∈ as, d < u.from_ → u.sub = v0.sub := by
  unfold firstRewrite at hv
  rw [h0] at hv
  simp only at hv
  obtain ⟨_, as, bs, heq, hno⟩ := List.find?_eq_some_iff_append.mp hv
  refine ⟨as, bs, heq, fun u hu hlt => ?_⟩
  have := hno u hu
  simp [hlt] at this
  exact this

-- Example: a section from the 1994 edition. A decision of 2007-05-29 reads subsection (e); a law of 2009-01-29
-- rewrites (e); a law of 2010 changes (e) again; an edition of 2012 reprints it.
section
private def led : List SVersion :=
  [⟨19950104, false, 0, 10⟩, ⟨20090129, true, 1, 11⟩, ⟨20100323, true, 2, 12⟩, ⟨20120103, false, 3, 12⟩]
#guard (firstRewritingLaw led 20070529).map (·.from_) == some 20090129
#guard overrideCandidate led 20070529 2 true == true
#guard overrideCandidate led 20070529 1 true == false    -- 20 months is outside one year
#guard overrideCandidate led 20070529 2 false == false   -- no evidence
-- A decision of 2009-06-01 read the 2009 words; its first rewriting law is the one of 2010.
#guard (firstRewritingLaw led 20090601).map (·.from_) == some 20100323
-- An edition that changes the words first ends the search.
private def ed : List SVersion := [⟨19950104, false, 0, 10⟩, ⟨20000101, false, 1, 13⟩, ⟨20090129, true, 2, 11⟩]
#guard firstRewritingLaw ed 19970101 == none
end

end Legal.USCaseLaw
