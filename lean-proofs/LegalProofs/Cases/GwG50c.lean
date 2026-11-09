import LegalProofs.Basic

/-!
# Germany: tax data sent to a body defined in a section that was never enacted (AO § 31b(3a), GwG § 50c)

Facts, from gesetze-im-internet.de and the Bundestag papers:
* AO § 31b(3a), in force from 6 December 2024 (Jahressteuergesetz 2024, BGBl. 2024 I Nr. 387): "Die Finanzbehörden
  übermitteln einer Koordinierenden Stelle eines Landes nach § 50c des Geldwäschegesetzes …".
* GwG § 50c was to be inserted by the Financial Crime Act bill (BT-Drs. 20/9648), which lapsed with the 20th Bundestag.
  The official note on the GwG: "Änderung durch Art. 41 Nr. 1 … ist nicht ausführbar, da § 50c nicht vorhanden ist".

Rule: a transfer of tax data needs a statutory basis that names its recipient; here the recipient is defined only by
§ 50c, so the transfer power is modelled as a blanket rule pointing at § 50c.
-/

namespace Legal.GwG50c

def ao31b_3a : Provision := fun d =>
  if 20241206 ≤ d then some "übermitteln einer Koordinierenden Stelle eines Landes nach § 50c des Geldwäschegesetzes" else none

/-- GwG § 50c: never enacted. -/
def gwg50c : Provision := fun _ => none

theorem gwg50c_never : neverEnacted gwg50c := fun _ => rfl

def transferPower : BlanketRule := { rule := ao31b_3a, pointsAt := gwg50c }

/-- **The vulnerability.** On no date can a transfer under AO § 31b(3a) rest on a defined recipient. -/
theorem transfer_never_valid : ∀ d, transferPower.applicable d = false :=
  phantom_reference transferPower gwg50c_never

/-- The transfer power itself is on the statute book: the defect is not that the power is missing, but that it points
at nothing. -/
theorem power_is_in_force : ∀ d, 20241206 ≤ d → inForce ao31b_3a d = true := by
  intro d hd
  simp [inForce, ao31b_3a, hd]

end Legal.GwG50c
