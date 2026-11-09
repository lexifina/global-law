import LegalProofs.Basic
import LegalProofs.Structure

/-!
# Certificates for the other flag categories

Like `RefFlag` in `History.lean`: each flag is a small record of facts taken from the published flag list, a
computable certificate Lean evaluates for every flag, and one soundness theorem saying what a certificate proves.

* **Empty periods**: a time-limited rule, its end date, and the date its extension took effect. The generator also picks
  a witness: the first real calendar day after the old end date.
* **Pre-publication dates**: an instrument dated in force before the day it was made (and so before it was published).
* **Missing paragraphs**: a reference to paragraph *n* of a section, and the paragraphs that section has today.
-/

namespace Legal

/-! ## Empty periods -/

structure GapFlag where
  ext : Extension
  witness : Date   -- first real day after `ext.endsOn`

def GapFlag.certified (f : GapFlag) : Bool := decide (f.ext.endsOn < f.witness) && decide (f.witness < f.ext.extendedFrom)

/-- A certified gap flag names a real day on which the rule did not bind. -/
theorem GapFlag.certified_sound (f : GapFlag) (h : f.certified = true) : f.ext.binds f.witness = false := by
  simp [GapFlag.certified] at h
  exact empty_period f.ext f.witness h.1 h.2

/-! ## In force before it was made -/

/-- `madeOn` is the date the instrument was made (enacted, signed); publication is on or after it. -/
structure PrepubFlag where
  statedFrom : Date
  madeOn : Date

def PrepubFlag.certified (f : PrepubFlag) : Bool := decide (f.statedFrom < f.madeOn)

/-- A certified flag: for any publication date on or after the making date, the instrument does not bind on the day its
own text says it starts. -/
theorem PrepubFlag.certified_sound (f : PrepubFlag) (h : f.certified = true) (publishedOn : Date)
    (hp : f.madeOn ≤ publishedOn) : ({ statedFrom := f.statedFrom, publishedOn := publishedOn } : Enactment).binds f.statedFrom = false := by
  simp [PrepubFlag.certified] at h
  exact prepublication_window _ f.statedFrom (Nat.le_refl _) (Nat.lt_of_lt_of_le h hp)

/-! ## Missing paragraphs (current text) -/

structure ParaFlag where
  para : Nat
  has : List Nat  -- the paragraphs the cited section has today

def ParaFlag.certified (f : ParaFlag) : Bool := !(f.has.contains f.para)

/-- A certified flag: a rule that names this paragraph cannot apply today. -/
theorem ParaFlag.certified_sound (f : ParaFlag) (h : f.certified = true) (rule : Provision) (today : Date) :
    ({ rule := rule, sec := fun _ => f.has, para := f.para } : ParagraphRule).applicable today = false := by
  simp [ParaFlag.certified] at h
  simp [ParagraphRule.applicable, resolves, h]

end Legal
