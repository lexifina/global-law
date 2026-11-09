import LegalProofs.Basic

/-!
# Paragraphs and enabling powers

Two more kinds of mistake from the vulnerability list, as schemas:

* **Missing paragraph**: a provision refers to paragraph *n* of a section that has no paragraph *n* (any more).
* **Missing enabling power**: a regulation made under a power that did not exist on the day it was made is void
  (the citation requirement and the requirement of a statutory basis for delegated legislation).
-/

namespace Legal

/-- A section with numbered paragraphs: the paragraph numbers it has on each date (empty when it does not exist). -/
abbrev Section := Date → List Nat

/-- A reference to paragraph `n` of a section resolves on `d` only if that paragraph exists on `d`. -/
def resolves (s : Section) (n : Nat) (d : Date) : Bool := (s d).contains n

/-- A rule whose duty is "paragraph `n` of section `s`". -/
structure ParagraphRule where
  rule : Provision
  sec : Section
  para : Nat

def ParagraphRule.applicable (p : ParagraphRule) (d : Date) : Bool := inForce p.rule d && resolves p.sec p.para d

/-- **The missing-paragraph schema.** If from date `r` the section no longer has paragraph `n`, the rule cannot apply
from `r` on. -/
theorem missing_paragraph (p : ParagraphRule) (r : Date) (h : ∀ d, r ≤ d → p.para ∉ p.sec d) :
    ∀ d, r ≤ d → p.applicable d = false := by
  intro d hd
  simp [ParagraphRule.applicable, resolves, h d hd]

/-- A regulation: the day it was made and the enabling provision it cites. -/
structure Regulation where
  madeOn : Date
  power : Provision

/-- A regulation is validly made only if the power it cites was in force on the day it was made. -/
def Regulation.validlyMade (r : Regulation) : Bool := inForce r.power r.madeOn

/-- **The missing-power schema.** A regulation made on a day its cited power did not exist is void. -/
theorem void_without_power (r : Regulation) (h : r.power r.madeOn = none) : r.validlyMade = false := by
  simp [Regulation.validlyMade, inForce, h]

/-- Illustration (not a real case): a section whose paragraph 3 was renumbered away on 1 March 2024, and a fine that
still names paragraph 3. -/
example : ∀ d, 20240301 ≤ d →
    ({ rule := fun _ => some "fine", sec := fun d => if d < 20240301 then [1, 2, 3] else [1, 2], para := 3 } :
      ParagraphRule).applicable d = false := by
  apply missing_paragraph
  intro d hd
  have : ¬ d < 20240301 := Nat.not_lt.mpr hd
  simp [this]

end Legal
