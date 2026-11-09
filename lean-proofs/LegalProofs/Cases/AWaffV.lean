import LegalProofs.Basic

/-!
# Germany: the fine for using a shut-down shooting range (AWaffV § 34 no. 11)

Facts, from the official consolidated text (gesetze-im-internet.de) and the amending act:
* AWaffV § 34 no. 11: "Ordnungswidrig … handelt, wer … entgegen § 12 Abs. 2 Satz 2 eine Schießstätte betreibt oder
  benutzt". In force throughout (the regulation dates from 2003; modelled from 1 Dec 2003).
* AWaffV § 12(2) sentence 2 ("Der weitere Betrieb oder die Benutzung der Schießstätte ist im Falle der Untersagung …
  verboten") was deleted by art. 4c of the Third Act amending weapons law (BGBl. I 2020 S. 166) with effect from
  1 September 2020. It is now "§ 12 (weggefallen)".
* The same ban now sits in WaffG § 27a(2) sentence 2, in force from 1 September 2020. No item of the Weapons Act's fine
  list (§ 53(1) WaffG) names § 27a.
-/

namespace Legal.AWaffV

def deletedOn : Date := 20200901

/-- AWaffV § 34 no. 11, the fine provision. -/
def fine34_11 : Provision := fun d =>
  if 20031201 ≤ d then some "entgegen § 12 Abs. 2 Satz 2 eine Schießstätte betreibt oder benutzt" else none

/-- AWaffV § 12(2) sentence 2, the duty it names. -/
def duty12_2 : Provision := fun d =>
  if 20031201 ≤ d ∧ d < deletedOn then some "Der weitere Betrieb oder die Benutzung … ist … verboten" else none

/-- WaffG § 27a(2) sentence 2, where the ban lives now. -/
def waffg27a_2 : Provision := fun d =>
  if deletedOn ≤ d then some "Der weitere Betrieb oder die Benutzung der Schießstätte ist … verboten" else none

def fine : BlanketRule := { rule := fine34_11, pointsAt := duty12_2 }

theorem duty_deleted : repealedFrom duty12_2 deletedOn := by
  intro d hd
  have : ¬ d < deletedOn := Nat.not_lt.mpr hd
  simp [duty12_2, this]

/-- **The vulnerability.** From 1 September 2020 on, the fine in § 34 no. 11 cannot be imposed. -/
theorem fine_dead : ∀ d, deletedOn ≤ d → fine.applicable d = false :=
  dead_reference fine deletedOn duty_deleted

/-- Sanity check: the fine worked the day before the deletion. -/
theorem fine_worked_before : fine.applicable 20200831 = true := by decide

/-- The conduct is still prohibited: the ban exists, in the Weapons Act, on every date the fine is dead. -/
theorem ban_survives : ∀ d, deletedOn ≤ d → inForce waffg27a_2 d = true := by
  intro d hd
  simp [inForce, waffg27a_2, hd]

/-- So, on any date from 1 September 2020: the conduct is banned, and the only fine for it cannot be applied. -/
theorem banned_but_unfineable :
    ∀ d, deletedOn ≤ d → inForce waffg27a_2 d = true ∧ fine.applicable d = false :=
  fun d hd => ⟨ban_survives d hd, fine_dead d hd⟩

/-! ## The counterargument, made explicit

The claim depends on reading the reference literally (no analogy against the person fined). If a court were allowed to
read "§ 12 Abs. 2 Satz 2 AWaffV" as "§ 27a Abs. 2 Satz 2 WaffG", the fine would apply again. Lean shows exactly that:
the vulnerability is the no-analogy rule plus the stale reference, nothing more. -/

def fineReadByAnalogy : BlanketRule := { rule := fine34_11, pointsAt := waffg27a_2 }

theorem analogy_would_rescue : ∀ d, deletedOn ≤ d → fineReadByAnalogy.applicable d = true := by
  intro d hd
  have : 20031201 ≤ d := Nat.le_trans (by decide) hd
  simp [fineReadByAnalogy, BlanketRule.applicable, inForce, fine34_11, waffg27a_2, hd, this]

end Legal.AWaffV
