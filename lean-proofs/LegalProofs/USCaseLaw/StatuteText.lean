import LegalProofs.USCaseLaw.Statute

/-!
# What a decision applied, and what the law says now

`Statute.lean` asks whether a section has changed since a decision. Over the whole US Code the record says more: each
version of a section was made either by a law (an Act of Congress, on the day it took effect) or by an edition (the
start of the record, or text the printed Code changed that no law accounts for), and each version has its words. A
court that cites a subsection, "§ 362(b)", applied only that subsection's words.

For a decision decided on day `d`, read on day `t`, the model answers:
* `amendedSince`: a law changed the section after `d` (and by `t`);
* `wordsDiffer`: the section in force on `t` does not read as the one in force on `d`;
* `subDiffers`: the subsection the court cited does not read the same.

Proved: words can differ only if something changed in between (`wordsDiffer_changed`, `subDiffers_changed`); the
version in force on a day came into force on or before it (`inForceOn_le`); and amendment, once true, stays true
(`amendedSince_mono`).
-/

namespace Legal.USCaseLaw

/-- A version of a section: the day it came into force, whether a law made it, and identifiers of the words of the
whole section and of the subsection a decision cited (equal identifiers, equal words). -/
structure SVersion where
  from_ : Nat
  byLaw : Bool
  text : Nat
  sub : Nat
  deriving Repr, DecidableEq, Inhabited

/-- The version in force on day `d`: the last version that came into force on or before `d`. -/
def sInForceOn (h : List SVersion) (d : Nat) : Option SVersion :=
  (h.filter (fun v => v.from_ ≤ d)).getLast?

/-- The versions that came into force after `d` and on or before `t`. -/
def sChangesBetween (h : List SVersion) (d t : Nat) : List SVersion :=
  h.filter (fun v => d < v.from_ && v.from_ ≤ t)

/-- The laws that changed the section after `d` and by `t`. -/
def lawChangesBetween (h : List SVersion) (d t : Nat) : List SVersion :=
  (sChangesBetween h d t).filter (·.byLaw)

def amendedSince (h : List SVersion) (d t : Nat) : Bool := !(lawChangesBetween h d t).isEmpty

def wordsDiffer (h : List SVersion) (d t : Nat) : Bool :=
  (sInForceOn h d).map (·.text) != (sInForceOn h t).map (·.text)

def subDiffers (h : List SVersion) (d t : Nat) : Bool :=
  (sInForceOn h d).map (·.sub) != (sInForceOn h t).map (·.sub)

/-- With nothing coming into force between `d` and `t`, the same version is in force on both days. -/
theorem sInForceOn_stable (h : List SVersion) (d t : Nat) (hle : d ≤ t) (hno : sChangesBetween h d t = []) :
    sInForceOn h d = sInForceOn h t := by
  unfold sChangesBetween at hno
  simp [List.filter_eq_nil_iff] at hno
  unfold sInForceOn
  congr 1
  apply List.filter_congr
  intro v hv
  have := hno v hv
  by_cases h1 : v.from_ ≤ d
  · simp [h1]; omega
  · simp [h1]
    have := this (by omega)
    omega

/-- If the section's words on `t` differ from those on `d`, some version came into force in between. -/
theorem wordsDiffer_changed (h : List SVersion) (d t : Nat) (hle : d ≤ t) (hw : wordsDiffer h d t = true) :
    sChangesBetween h d t ≠ [] := by
  intro hno
  have := sInForceOn_stable h d t hle hno
  simp [wordsDiffer, this] at hw

/-- The same for the subsection a decision cited. -/
theorem subDiffers_changed (h : List SVersion) (d t : Nat) (hle : d ≤ t) (hw : subDiffers h d t = true) :
    sChangesBetween h d t ≠ [] := by
  intro hno
  have := sInForceOn_stable h d t hle hno
  simp [subDiffers, this] at hw

/-- The version in force on a day came into force on or before it. -/
theorem inForceOn_le (h : List SVersion) (d : Nat) (v : SVersion) (hv : sInForceOn h d = some v) : v.from_ ≤ d := by
  unfold sInForceOn at hv
  have := List.mem_of_getLast? hv
  simp at this
  exact this.2

/-- Amendment only accumulates: amended since `d` by `t` is still amended by any later day. -/
theorem amendedSince_mono (h : List SVersion) (d t t' : Nat) (hle : t ≤ t') (ha : amendedSince h d t = true) :
    amendedSince h d t' = true := by
  unfold amendedSince lawChangesBetween sChangesBetween at *
  simp [List.filter_eq_nil_iff] at *
  obtain ⟨v, hv, hb, h1, h2⟩ := ha
  exact ⟨v, hv, hb, h1, by omega⟩

-- Example: a section from the 1994 edition; a law rewrites subsection (b) on 2005-10-17; an edition reprints it with
-- a corrected cross-reference on 2012-01-03. A decision of 2001 citing (a), and one citing (b).
section
private def s : List SVersion := [⟨19950104, false, 0, 0⟩, ⟨20051017, true, 1, 0⟩, ⟨20120103, false, 2, 0⟩]
private def sb : List SVersion := [⟨19950104, false, 0, 0⟩, ⟨20051017, true, 1, 1⟩, ⟨20120103, false, 2, 1⟩]
#guard amendedSince s 20010601 20261112 == true
#guard wordsDiffer s 20010601 20261112 == true
#guard subDiffers s 20010601 20261112 == false   -- (a) still reads the same
#guard subDiffers sb 20010601 20261112 == true   -- (b) does not
#guard amendedSince s 20060101 20261112 == false -- only an edition since
#guard wordsDiffer s 20060101 20261112 == true
#guard (lawChangesBetween s 20010601 20261112).length == 1
end

end Legal.USCaseLaw
