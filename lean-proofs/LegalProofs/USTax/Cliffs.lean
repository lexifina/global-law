import LegalProofs.USTax.Schedule

/-!
# Cliffs, traps and a marriage penalty, proved

`Schedule.lean` proves that the rate schedule alone never takes more than the extra dollar. These theorems show where the
rest of the code does: each is checked by Lean evaluating the model, so the figures are exact for the model's 2025 rules.
-/

namespace Legal.USTax

/-! ## The investment-income cliff (§32(i)) -/

/-- §32(i) is all-or-nothing: above the limit there is no EITC at all, whatever the household earns. -/
theorem eitc_zero_over_limit (h : Household) (hi : eitcInvestmentLimit < h.interest) : eitc h = 0 := by
  unfold eitc; simp [hi]

/-- **One dollar of interest costs $8,045.** A married couple with three children and $18,000 of wages: interest of
$11,950 keeps the full EITC; $11,951 removes it. -/
theorem investment_cliff_8045 :
    net ⟨.mfj, 3, 18000, 11951, 0⟩ + 8045 = net ⟨.mfj, 3, 18000, 11950, 0⟩ := by decide

/-- The same dollar for a single parent of three on $20,000. -/
theorem investment_cliff_single :
    net ⟨.single, 3, 20000, 11951, 0⟩ + 6234 = net ⟨.single, 3, 20000, 11950, 0⟩ := by decide

/-! ## Saver's Credit tiers (§25B(b)) -/

/-- **One dollar of wages costs $799.** A married couple contributing $4,000 to IRAs: AGI $47,500 earns the 50% credit,
AGI $47,501 only the 20% credit. -/
theorem savers_cliff_799 :
    net ⟨.mfj, 0, 51501, 0, 4000⟩ + 799 = net ⟨.mfj, 0, 51500, 0, 4000⟩ := by decide

/-- The tier test is a hard threshold: one dollar of AGI moves the rate from 50% to 20%. -/
theorem saver_rate_jump : saverRate ⟨.mfj, 0, 51500, 0, 4000⟩ = 50 ∧ saverRate ⟨.mfj, 0, 51501, 0, 4000⟩ = 20 := by
  decide

/-! ## Marriage penalties -/

/-- **Marrying costs $3,511 a year.** Two single parents, each with one child and $20,000 of wages, filing as heads of
household, against the same two filing jointly. -/
theorem marriage_penalty_3511 :
    net ⟨.mfj, 2, 40000, 0, 0⟩ + 3511 = net ⟨.hoh, 1, 20000, 0, 0⟩ + net ⟨.hoh, 1, 20000, 0, 0⟩ := by decide

/-- A parent of two and a childless worker, each on $22,000: $1,999 a year. -/
theorem marriage_penalty_1999 :
    net ⟨.mfj, 2, 44000, 0, 0⟩ + 1999 = net ⟨.hoh, 2, 22000, 0, 0⟩ + net ⟨.single, 0, 22000, 0, 0⟩ := by decide

/-! ## The arbitrage the cliffs create -/

/-- Moving the last dollar of interest out of taxable savings (into an IRA, whose earnings are not disqualified income)
is worth $8,045 to the first household: the same family, the same wages, one dollar less of taxable interest. -/
theorem arbitrage_value : net ⟨.mfj, 3, 18000, 11950, 0⟩ - net ⟨.mfj, 3, 18000, 11951, 0⟩ = 8045 := by decide

/-- A $1 IRA contribution moves the Saver's cliff household back under the 50% tier and is worth $800 to it. -/
theorem ira_dollar_value : net ⟨.mfj, 0, 51501, 0, 4001⟩ - net ⟨.mfj, 0, 51501, 0, 4000⟩ = 800 := by decide

end Legal.USTax
