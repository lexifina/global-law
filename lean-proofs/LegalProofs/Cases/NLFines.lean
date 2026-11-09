import LegalProofs.Basic

/-!
# Netherlands: higher criminal fine ceilings in force before publication (Stb. 2022, 7)

Facts, from officielebekendmakingen.nl:
* Stb. 2022, 7 (Besluit van 21 december 2021, under Criminal Code art. 23(9)), art. II: "Dit besluit treedt in werking met
  ingang van 1 januari 2022." Publication line: "Uitgegeven de vijfde januari 2022."
* Category 6 maximum: €870,000 before, €900,000 under the decree (all six categories rise similarly).

Rule: a penalty cannot exceed the one that bound when the offence was committed, and a rule binds only once published.
-/

namespace Legal.NLFines

def decree : Enactment := { statedFrom := 20220101, publishedOn := 20220105 }

/-- What the decree's own text claims the category 6 maximum is on date `d` (from 1 January 2022). -/
def claimedMax6 (d : Date) : Nat := if 20220101 ≤ d then 900000 else 870000

/-- The category 6 maximum that actually binds on date `d`. -/
def bindingMax6 (d : Date) : Nat := if decree.binds d then 900000 else 870000

/-- **The vulnerability.** For offences on 1–4 January 2022, the decree claims €900,000 but €870,000 binds. -/
theorem first_four_days : ∀ d, 20220101 ≤ d → d < 20220105 →
    claimedMax6 d = 900000 ∧ bindingMax6 d = 870000 := by
  intro d h1 h2
  have hb : decree.binds d = false := prepublication_window decree d h1 h2
  exact ⟨by simp [claimedMax6, h1], by simp [bindingMax6, hb]⟩

/-- From publication on, the claim and the law agree again. -/
theorem agree_after : ∀ d, 20220105 ≤ d → claimedMax6 d = bindingMax6 d := by
  intro d hd
  have h1 : 20220101 ≤ d := Nat.le_trans (by decide) hd
  have hb : decree.binds d = true := by simp [Enactment.binds, decree, h1, hd]
  simp [claimedMax6, bindingMax6, hb, h1]

end Legal.NLFines
