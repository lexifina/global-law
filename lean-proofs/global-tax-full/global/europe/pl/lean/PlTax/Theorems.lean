import PlTax.Household

/-!
# Theorems for all inputs

No `sorry`, no `native_decide`. The kernel's generic facts (`schedRaw_mono`, rounding monotonicity) are instantiated
for the Polish scale; the rest are claims the statute makes or implies.
-/

namespace PlTax

/-! ## The scale, art. 27 ust. 1 -/

/-- The kernel schedule less the kwota zmniejszająca is exactly the statute's two-row table. -/
theorem scaleTax_eq_statute (g : Int) (h : 0 ≤ g) : scaleTax g = scaleStatute g := by
  simp only [scaleTax, scaleStatute, schedRaw, plScale, Band.width, pos, rhu, scaleThreshold, rateLow, rateHigh,
    kwotaZmniejszajaca]
  split <;> omega

/-- **Kwota wolna.** "12 % minus 3600 zł" is the same as a 0 % band to 30 000 zł, 12 % to 120 000 zł and 32 % above:
the 3600 zł is the tax-free amount 30 000 zł written as a credit (3600 / 12 % = 30 000). For every base. -/
def zeroBandScale : List Band := [⟨0, some 3000000, 0⟩, ⟨3000000, some 12000000, 1200⟩, ⟨12000000, none, 3200⟩]

theorem kwotaWolna (g : Int) (h : 0 ≤ g) : scaleTax g = rhu (schedRaw zeroBandScale g) 10000 := by
  simp only [scaleTax, zeroBandScale, schedRaw, plScale, Band.width, pos, rhu, scaleThreshold, rateLow, rateHigh,
    kwotaZmniejszajaca]
  omega

/-- Generic monotonicity (kernel `schedRaw_mono`) instantiated: more base never means less tax. -/
theorem scaleTax_mono {a b : Int} (h : a ≤ b) : scaleTax a ≤ scaleTax b := by
  unfold scaleTax
  apply pos_mono
  have := schedRaw_mono plScale (by intro bd hb; simp [plScale, rateLow, rateHigh] at hb; rcases hb with rfl | rfl <;> decide) h
  have := rhu_mono 10000 (by decide) this
  omega

theorem scaleTax_nonneg (g : Int) : 0 ≤ scaleTax g := pos_nonneg _

/-- No jump: one more złoty of base adds at most 32 grosze of tax (amounts in grosze). -/
theorem scale_step_le (b : Int) (h : 0 ≤ b) : scaleTax (100 * (b + 1)) - scaleTax (100 * b) ≤ 32 := by
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> omega

/-- Marginal rates on whole-złoty bases: nil below 30 000 zł, 12 % to 120 000 zł, 32 % above. -/
theorem marginal_zero (b : Int) (h0 : 0 ≤ b) (h : b < 30000) : scaleTax (100 * (b + 1)) = scaleTax (100 * b) := by
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> omega

theorem marginal_12 (b : Int) (h0 : 30000 ≤ b) (h : b < 120000) :
    scaleTax (100 * (b + 1)) - scaleTax (100 * b) = 12 := by
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> omega

theorem marginal_32 (b : Int) (h0 : 120000 ≤ b) :
    scaleTax (100 * (b + 1)) - scaleTax (100 * b) = 32 := by
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> omega

/-- The tax never exceeds 32 % of the base. -/
theorem scale_le_top (b : Int) (h : 0 ≤ b) : scaleTax (100 * b) ≤ 32 * b := by
  rw [scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> omega

/-! ## Splitting, art. 6 ust. 2 and 4d -/

/-- **Joint filing never costs more than separate assessment**, for any two bases. -/
theorem joint_le_separate (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) : jointTax a b ≤ sepTax a b := by
  simp only [jointTax, splitTax, sepTax]
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> split <;> omega

/-- The gain is at most 27 600 zł (20 points of rate on 120 000 zł plus the second kwota of 3600 zł) ... -/
theorem joint_gain_le (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) : sepTax a b - jointTax a b ≤ 2760000 := by
  simp only [jointTax, splitTax, sepTax]
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> split <;> omega

/-- ... and it is reached exactly when one spouse has no base and the other at least 240 000 zł. -/
theorem joint_gain_max (b : Int) (hb : 240000 ≤ b) : sepTax 0 b - jointTax 0 b = 2760000 := by
  simp only [jointTax, splitTax, sepTax]
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> split <;> omega

/-- When both bases lie in the same linear stretch (both between 30 000 and 120 000 zł), splitting gains nothing. -/
theorem joint_no_gain_same_band (a b : Int) (ha : 30000 ≤ a) (ha' : a ≤ 120000) (hb : 30000 ≤ b) (hb' : b ≤ 120000) :
    jointTax a b = sepTax a b := by
  simp only [jointTax, splitTax, sepTax]
  rw [scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega), scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, pos, rhu]
  split <;> split <;> split <;> omega

/-! ## Child relief, art. 27f -/

/-- The amount paid out never exceeds the contributions of ust. 9, and deduction plus payment never exceed the relief. -/
theorem relief_refund_le_cap (r t cap : Int) : (reliefSplit r t cap).2 ≤ pos cap := by
  simp only [reliefSplit]; omega

theorem relief_total_le (r t cap : Int) (_hr : 0 ≤ r) : (reliefSplit r t cap).1 + (reliefSplit r t cap).2 ≤ r := by
  simp only [reliefSplit, pos]; omega

/-- With contributions at least the relief, the relief is worth its full amount whatever the tax (fully refundable). -/
theorem relief_full (r t cap : Int) (hr : 0 ≤ r) (hc : r ≤ cap) :
    (reliefSplit r t cap).1 + (reliefSplit r t cap).2 = r := by
  simp only [reliefSplit, pos]; omega

/-- The official example (podatki.gov.pl, "Ulga na dziecko", 2026-11-19): three children, "Łącznie odliczysz
4224,12 zł". -/
theorem relief_three_children : childRelief 3 = 422412 := by decide

/-! ## Contributions -/

/-- Employee emerytalne + rentowe stop at the 260 190 zł ceiling: above it, only chorobowe (2,45 %) grows. -/
theorem emp_social_above_ceiling (w : Int) (h : 260190 ≤ w) :
    (empSocial w).emerytalne + (empSocial w).rentowe = 2539454 + 390285 := by
  simp only [empSocial, capped, ceiling, pctGr, rhu, eeEmerytalne, eeRentowe]
  omega

/-- The liniowy health deduction is capped: at most 12 900 zł whatever the income. -/
theorem liniowy_health_ded_le (h : Int) : min h liniowyHealthCap ≤ 1290000 := by
  simp [liniowyHealthCap]; omega

end PlTax
