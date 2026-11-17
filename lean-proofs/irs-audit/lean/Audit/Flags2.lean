import Audit.Formula
import Audit.CPI
import Audit.Alfred
open TaxCode.Indexing
/-! Kernel-checked statements behind findings A2 and A3 (C-CPI-U vintage of the August 2025 release, `ccpiu_v2025`;
    August 2026 release `ccpiu_v2026` with the eleven published months for 2027). -/

/-- A2: an increase rounded to a multiple of $50 added to $23,625 can never give $24,150. -/
theorem hoh2026_impossible : ∀ k : Nat, 23625 + 50 * k ≠ 24150 := by intro k; omega

/-- A2: §63(c)(7)(B)(ii): $23,625 × C(2025)/C(2024), increase rounded down to $50, = $24,175. -/
theorem hoh2026_statute :
    adjustND 23625 (ratio ccpiu_v2025 cpiu [] [] (.year 2024) 2026).1 (ratio ccpiu_v2025 cpiu [] [] (.year 2024) 2026).2 (.incDown 50) = 24175 := by
  decide +kernel

/-- A3 (2026): the estate table's $2,550 indexed from 2017 (the clause for the start of a bracket above 22%) gives
    $3,250; from 2016 it gives the published $3,300. -/
theorem est2026 :
    adjustND 2550 (ratio ccpiu_v2025 cpiu [] [] (.year 2017) 2026).1 (ratio ccpiu_v2025 cpiu [] [] (.year 2017) 2026).2 (.incDown 50) = 3250 ∧
    adjustND 2550 (ratio ccpiu_v2025 cpiu [] [] (.year 2016) 2026).1 (ratio ccpiu_v2025 cpiu [] [] (.year 2016) 2026).2 (.incDown 50) = 3300 := by
  decide +kernel

#print axioms hoh2026_statute
#print axioms est2026
