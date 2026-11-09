import LegalProofs.Basic

/-!
# Switzerland: pest-control costs charged for breaching a repealed article (LwG art. 154(2))

Facts, from Fedlex (consolidations of 1 January 2026 and 1 January 2027):
* LwG art. 154(2): "Wer Pflanzenmaterial produziert, einführt oder in Verkehr bringt und sich vorsätzlich oder
  fahrlässig den Pflichten nach Artikel 151 entzieht, kann zur Übernahme der Kosten herangezogen werden."
* LwG art. 151: "Aufgehoben durch Ziff. I des BG vom 16. Juni 2023, mit Wirkung seit 1. Jan. 2025 (AS 2024 623)."

Rule: a public charge needs a statutory basis naming who pays and why (Federal Constitution arts. 5 and 127).
-/

namespace Legal.LwG154

def art154_2 : Provision := fun d => if 19990101 ≤ d then some "… den Pflichten nach Artikel 151 entzieht …" else none

def art151 : Provision := fun d =>
  if 19990101 ≤ d ∧ d < 20250101 then some "Grundsätze des Pflanzenschutzes beachten; besonders gefährliche Schadorganismen melden" else none

def costCharge : BlanketRule := { rule := art154_2, pointsAt := art151 }

theorem art151_repealed : repealedFrom art151 20250101 := by
  intro d hd
  have : ¬ d < 20250101 := Nat.not_lt.mpr hd
  simp [art151, this]

/-- **The vulnerability.** From 1 January 2025, the cost charge in art. 154(2) has no duty to attach to. -/
theorem charge_dead : ∀ d, 20250101 ≤ d → costCharge.applicable d = false :=
  dead_reference costCharge 20250101 art151_repealed

theorem charge_worked_in_2024 : costCharge.applicable 20240601 = true := by decide

end Legal.LwG154
