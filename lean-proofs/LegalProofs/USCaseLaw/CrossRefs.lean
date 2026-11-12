/-!
# Cross-references in the US Code, over time

A section of the US Code refers to others: "section 2244 of this title", "subsection (c)(1) of section 924 of title
18", "paragraph (2) of subsection (a)". A reference names a target section and a designation path in it (`["c", "1"]`;
the empty path is the whole section). It resolves on a day if, in the Code as it stood that day, the target section is
live (it has text and is not repealed, transferred or reserved) and has that designation. Otherwise it dangles.

The Code on a day is a `Snapshot`: for each section, the version in force. Each section has a history of dated
versions; the referring section's versions say only whether its text makes the reference.

Proved:
* `dangling_of_snapshot`: whether a reference dangles is decided by the snapshot alone (indeed by the target's
  version in force that day), whatever the histories that led to it;
* `status_stable`: if neither the referring section nor the target has a version coming into force after `d` and on
  or before `t`, a reference has the same status on `t` as on `d`;
* `status_change_day`: so a status changes only across a day on which the source or the target has a dated version;
* `resolvesIn_restrict`: deciding membership against only the paths that some reference names (as the runner does)
  gives the same answer as against all of a version's paths.
-/

namespace Legal.USCaseLaw.CrossRefs

/-- A designation path from the top of a section: `["b", "2", "A"]` is (b)(2)(A); `[]` is the whole section. -/
abbrev Path := List String

/-- A dated version of a section: the day it came into force, whether it is live, and its designation paths. -/
structure TVersion where
  from_ : Nat
  live : Bool
  paths : List Path
  deriving Repr, DecidableEq, Inhabited

/-- A dated version of the referring section, reduced to whether its text makes the reference. -/
structure RVersion where
  from_ : Nat
  makes : Bool
  deriving Repr, DecidableEq, Inhabited

/-- A reference: the target section (its path in the record, "title-18/924.md") and a designation path in it. -/
structure Ref where
  target : String
  path : Path
  deriving Repr, DecidableEq, Inhabited

/-- The element of a dated history in force on day `d`: the last one that came into force on or before `d`. -/
def inForceBy {α : Type} (f : α → Nat) (h : List α) (d : Nat) : Option α :=
  (h.filter (fun v => f v ≤ d)).getLast?

/-- The elements that came into force after `d` and on or before `t`. -/
def changesBy {α : Type} (f : α → Nat) (h : List α) (d t : Nat) : List α :=
  h.filter (fun v => d < f v && f v ≤ t)

/-- With nothing coming into force between `d` and `t`, the same element is in force on both days. -/
theorem inForceBy_stable {α : Type} (f : α → Nat) (h : List α) (d t : Nat) (hle : d ≤ t)
    (hno : changesBy f h d t = []) : inForceBy f h d = inForceBy f h t := by
  unfold changesBy at hno
  simp [List.filter_eq_nil_iff] at hno
  unfold inForceBy
  congr 1
  apply List.filter_congr
  intro v hv
  have := hno v hv
  by_cases h1 : f v ≤ d
  · simp [h1]; omega
  · simp [h1]
    have := this (by omega)
    omega

/-- The Code on a day: each section's version in force (none before its first version). -/
def Snapshot := String → Option TVersion

/-- The snapshot of a whole history of the Code on day `d`. -/
def snapshotOn (code : String → List TVersion) (d : Nat) : Snapshot := fun s => inForceBy (·.from_) (code s) d

/-- A path resolves in a version if the version is live and the path is the whole section or one of its paths. -/
def resolvesIn (v : Option TVersion) (p : Path) : Bool :=
  match v with
  | none => false
  | some v => v.live && (p.isEmpty || v.paths.contains p)

def resolves (snap : Snapshot) (r : Ref) : Bool := resolvesIn (snap r.target) r.path

def dangling (snap : Snapshot) (r : Ref) : Bool := !resolves snap r

/-- Whether a reference dangles is decided by the snapshot: by the target's version in force that day, whatever the
two histories and the two days. -/
theorem dangling_of_snapshot (code₁ code₂ : String → List TVersion) (d₁ d₂ : Nat) (r : Ref)
    (h : snapshotOn code₁ d₁ r.target = snapshotOn code₂ d₂ r.target) :
    dangling (snapshotOn code₁ d₁) r = dangling (snapshotOn code₂ d₂) r := by
  simp only [dangling, resolves, h]

/-- The status of a reference on a day: the referring section's text does not make it, it resolves, or it dangles. -/
inductive Status where
  | absent
  | ok
  | dangling
  deriving Repr, DecidableEq, Inhabited

def Status.code : Status → Char
  | .absent => 'a'
  | .ok => 'o'
  | .dangling => 'd'

/-- The status on day `d` of a reference to path `p`, given the histories of the referring section and the target. -/
def status (src : List RVersion) (tgt : List TVersion) (p : Path) (d : Nat) : Status :=
  match inForceBy (·.from_) src d with
  | some v => if v.makes then (if resolvesIn (inForceBy (·.from_) tgt d) p then .ok else .dangling) else .absent
  | none => .absent

/-- The status agrees with `dangling` on the snapshot whenever the referring text makes the reference. -/
theorem status_dangling (src : List RVersion) (code : String → List TVersion) (r : Ref) (d : Nat) (v : RVersion)
    (hv : inForceBy (·.from_) src d = some v) (hm : v.makes = true) :
    (status src (code r.target) r.path d = .dangling) ↔ dangling (snapshotOn code d) r = true := by
  simp [status, hv, hm, dangling, resolves, snapshotOn]

/-- No dated version of the source or the target after `d` and by `t`: the status is the same on both days. -/
theorem status_stable (src : List RVersion) (tgt : List TVersion) (p : Path) (d t : Nat) (hle : d ≤ t)
    (hs : changesBy (·.from_) src d t = []) (ht : changesBy (·.from_) tgt d t = []) :
    status src tgt p d = status src tgt p t := by
  unfold status
  rw [inForceBy_stable _ src d t hle hs, inForceBy_stable _ tgt d t hle ht]

/-- So a status changes only across a day on which the source or the target has a dated version. -/
theorem status_change_day (src : List RVersion) (tgt : List TVersion) (p : Path) (d t : Nat) (hle : d ≤ t)
    (hc : status src tgt p d ≠ status src tgt p t) :
    changesBy (·.from_) src d t ≠ [] ∨ changesBy (·.from_) tgt d t ≠ [] := by
  by_cases hs : changesBy (·.from_) src d t = []
  · by_cases ht : changesBy (·.from_) tgt d t = []
    · exact absurd (status_stable src tgt p d t hle hs ht) hc
    · exact Or.inr ht
  · exact Or.inl hs

/-- A version reduced to the paths in `keep` (those some reference names). -/
def restrict (keep : List Path) (v : TVersion) : TVersion := { v with paths := v.paths.filter (keep.contains ·) }

/-- For a path in `keep`, the reduced version decides the reference as the full one does. -/
theorem resolvesIn_restrict (keep : List Path) (v : Option TVersion) (p : Path) (hp : keep.contains p = true) :
    resolvesIn (v.map (restrict keep)) p = resolvesIn v p := by
  cases v with
  | none => rfl
  | some v =>
    simp only [Option.map, resolvesIn, restrict]
    congr 1
    congr 1
    simp only [List.contains_iff_mem] at *
    simp [hp]

-- Example, from the record: 18 U.S.C. § 2101 (the Anti-Riot Act). In the 1994 edition subsection (a) opens
-- "(a)(1) Whoever travels ... with intent— (A) to incite a riot; ... (D) ..."; subsection (b) speaks of "the overt
-- acts described in subparagraph (A), (B), (C), or (D) of paragraph (1) of subsection (a)". On 1996-10-11 Pub. L.
-- 104-294 struck the "(1)" and made (A)-(D) paragraphs (1)-(4). Subsection (b) still says the same today (the
-- publisher marks it "So in original"). Both sections here are § 2101 itself: the source and target are one history.
section
private def r2101 : List TVersion :=
  [⟨19950104, true, [["a"], ["a", "1"], ["a", "1", "A"], ["a", "1", "B"], ["a", "1", "C"], ["a", "1", "D"], ["b"]]⟩,
   ⟨19961011, true, [["a"], ["a", "1"], ["a", "2"], ["a", "3"], ["a", "4"], ["b"]]⟩]
private def s2101 : List RVersion := [⟨19950104, true⟩, ⟨19961011, true⟩]
private def code : String → List TVersion := fun s => if s == "title-18/2101.md" then r2101 else []
#guard status s2101 r2101 ["a", "1", "A"] 19960101 == .ok
#guard status s2101 r2101 ["a", "1", "A"] 19961011 == .dangling
#guard status s2101 r2101 ["a", "1", "A"] 20261112 == .dangling
#guard dangling (snapshotOn code 20261112) ⟨"title-18/2101.md", ["a", "1", "A"]⟩ == true
#guard dangling (snapshotOn code 20261112) ⟨"title-18/2101.md", ["a", "1"]⟩ == false
#guard dangling (snapshotOn code 20261112) ⟨"title-18/2102.md", []⟩ == true
-- a repealed target: live = false
#guard resolvesIn (some ⟨20100101, false, []⟩) [] == false
end

end Legal.USCaseLaw.CrossRefs
