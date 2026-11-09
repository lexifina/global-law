import LegalProofs.Basic

/-!
# Brazil: the overtime rule for minors points at deleted articles (CLT art. 413, sole paragraph)

Facts, from the Câmara dos Deputados consolidated text and the amending laws:
* CLT art. 413, sole paragraph: "Aplica-se à prorrogação do trabalho do menor o disposto no art. 375, no parágrafo único
  do art. 376, no art. 378 e no art. 384 desta Consolidação." In force since the CLT (10 November 1943) in that form.
* Art. 376 sole paragraph held the 48-hour written-notice duty. Art. 376 was repealed by Lei 10.244/2001, published
  28 June 2001.
* The only general fallback, the notice duty in art. 61 §1, was removed by Lei 13.467/2017 (in force 11 November 2017).

Rule: an administrative fine needs an existing legal duty (Constitution art. 5 II). The notice duty for minors' overtime
can only come from art. 376 (via art. 413) or from art. 61 §1.
-/

namespace Legal.CLT413

def art413 : Provision := fun d => if 19431110 ≤ d then some "Aplica-se … o disposto no parágrafo único do art. 376" else none

/-- Art. 376 sole paragraph: notice within 48 hours. Repealed from 28 June 2001. -/
def art376 : Provision := fun d =>
  if 19431110 ≤ d ∧ d < 20010628 then some "deverá ser comunicada por escrito … dentro do prazo de quarenta e oito horas" else none

/-- Art. 61 §1 notice duty (general emergency overtime). Removed from 11 November 2017. -/
def art61_1_notice : Provision := fun d =>
  if 19431110 ≤ d ∧ d < 20171111 then some "comunicado … à autoridade competente" else none

def viaArt413 : BlanketRule := { rule := art413, pointsAt := art376 }

/-- A fine for not giving notice can rest on art. 413 → art. 376, or on the general art. 61 §1 duty. -/
def noticeFineAvailable (d : Date) : Bool := viaArt413.applicable d || inForce art61_1_notice d

theorem art376_repealed : repealedFrom art376 20010628 := by
  intro d hd
  have : ¬ d < 20010628 := Nat.not_lt.mpr hd
  simp [art376, this]

theorem notice_removed : repealedFrom art61_1_notice 20171111 := by
  intro d hd
  have : ¬ d < 20171111 := Nat.not_lt.mpr hd
  simp [art61_1_notice, this]

/-- The route through art. 413 has been dead since 28 June 2001. -/
theorem via413_dead : ∀ d, 20010628 ≤ d → viaArt413.applicable d = false :=
  dead_reference viaArt413 20010628 art376_repealed

/-- **The vulnerability.** From 11 November 2017, no route to a notice fine is left. -/
theorem no_notice_fine : ∀ d, 20171111 ≤ d → noticeFineAvailable d = false := by
  intro d hd
  have h1 : 20010628 ≤ d := Nat.le_trans (by decide) hd
  simp [noticeFineAvailable, via413_dead d h1, inForce, notice_removed d hd]

/-- Sanity check: in 2000 the route through art. 413 still worked. -/
theorem worked_in_2000 : noticeFineAvailable 20000101 = true := by decide

end Legal.CLT413
