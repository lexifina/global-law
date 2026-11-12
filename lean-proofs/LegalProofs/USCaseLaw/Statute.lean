/-!
# The statute a decision applied, and whether it still reads the same

A section of the US Code has a history of versions, each in force from a day (`yyyymmdd`). A decision that applied the
section on the day it was decided applied the version in force that day (`inForceOn`). The question a lawyer citing the
decision today has to ask is whether the section still reads the same (`changedSince`).

Proved: a section that has not changed between two days is in the same version on both (`inForceOn_stable`), and a
section changed since a decision by one day is still changed on any later day (`changedSince_mono`).
-/

namespace Legal.USCaseLaw

/-- One version of a section: the day it came into force, and an identifier of its text. -/
structure Version where
  from_ : Nat
  text : Nat
  deriving Repr, DecidableEq, Inhabited

/-- The version in force on day `d`: the last version that came into force on or before `d` (versions in date order). -/
def inForceOn (h : List Version) (d : Nat) : Option Version :=
  (h.filter (fun v => v.from_ ≤ d)).getLast?

/-- The versions that came into force after day `d` and on or before day `t`. -/
def changesBetween (h : List Version) (d t : Nat) : List Version :=
  h.filter (fun v => d < v.from_ && v.from_ ≤ t)

/-- The section has changed since the decision: some version came into force after it and on or before `t`. -/
def changedSince (h : List Version) (d t : Nat) : Bool := !(changesBetween h d t).isEmpty

/-- If nothing came into force between `d` and `t` (`d ≤ t`), the version in force is the same on both days. -/
theorem inForceOn_stable (h : List Version) (d t : Nat) (hle : d ≤ t) (hno : changedSince h d t = false) :
    inForceOn h d = inForceOn h t := by
  unfold changedSince changesBetween at hno
  simp [List.filter_eq_nil_iff] at hno
  unfold inForceOn
  congr 1
  apply List.filter_congr
  intro v hv
  have := hno v hv
  by_cases h1 : v.from_ ≤ d
  · simp [h1]; omega
  · simp [h1]
    have := this (by omega)
    omega

/-- Changes only accumulate: a section changed since `d` by day `t` is still changed by any later day. -/
theorem changedSince_mono (h : List Version) (d t t' : Nat) (hle : t ≤ t') (hc : changedSince h d t = true) :
    changedSince h d t' = true := by
  unfold changedSince changesBetween at *
  simp [List.filter_eq_nil_iff] at *
  obtain ⟨v, hv, h1, h2⟩ := hc
  exact ⟨v, hv, h1, by omega⟩

-- Examples: a section amended on 2020-03-27 and 2022-06-21; a decision of 2018-07-10.
section
private def h11 : List Version := [⟨19940101, 0⟩, ⟨20200327, 1⟩, ⟨20220621, 2⟩]
#guard inForceOn h11 20180710 == some ⟨19940101, 0⟩
#guard changedSince h11 20180710 20261111 == true
#guard (changesBetween h11 20180710 20261111).length == 2
#guard changedSince h11 20220701 20261111 == false
end

end Legal.USCaseLaw
