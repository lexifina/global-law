import LegalProofs.Basic

/-!
# Switzerland (empty period): the GMO moratorium that wasn't there for seven months (GTG art. 37a)

Not a drafting mistake but a timing gap; included to show the empty-period schema.

Facts, from Fedlex:
* GTG art. 37a (version in force 1 Jan 2022 – 31 Jul 2026): no authorisations "für den Zeitraum bis zum
  31. Dezember 2025".
* AS 2026 417 replaces the end date with 31 December 2030, put into force on 1 August 2026; Fedlex records no
  retroactive entry into force.
-/

namespace Legal.GMOGap

def moratorium : Extension := { endsOn := 20251231, extendedFrom := 20260801, newUntil := 20301231 }

/-- **The gap.** From 1 January to 31 July 2026, the moratorium did not bind. -/
theorem gap : ∀ d, 20260101 ≤ d → d ≤ 20260731 → moratorium.binds d = false := by
  intro d h1 h2
  exact empty_period moratorium d (Nat.lt_of_lt_of_le (by decide) h1) (Nat.lt_of_le_of_lt h2 (by decide))

theorem bound_on_last_day : moratorium.binds 20251231 = true := by decide
theorem bound_again : moratorium.binds 20260801 = true := by decide

/-- The counterfactual the Federal Council itself suggested: had the extension been put into force retroactively from
the day after the old end date, there would be no gap. (Stated as `endsOn + 1` rather than `20260101`: with `YYYYMMDD`
numbers, values such as `20251299` sit between the two dates without being dates, and Lean rightly refuses a theorem
that ignores them.) -/
def retroactive : Extension := { moratorium with extendedFrom := moratorium.endsOn + 1 }

theorem retroactive_closes_gap : ∀ d, 20250101 ≤ d → d ≤ 20301231 → retroactive.binds d = true := by
  intro d _ h2
  by_cases h : d ≤ 20251231
  · simp [Extension.binds, retroactive, moratorium, h]
  · have : 20251231 + 1 ≤ d := by omega
    simp [Extension.binds, retroactive, moratorium, h, this, h2]

end Legal.GMOGap
