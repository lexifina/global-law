import FrTax.Liquidation

/-!
# Theorems

Two kinds. General ones hold for every input (no `sorry`, no `native_decide`, only the standard axioms). Concrete
ones are checked by the kernel on the numbers they name: the indexation the statute prescribes against the
amounts the DGFiP publishes, cliffs in the schedule, and counterexamples to figures printed in the DGFiP's
brochure pratique.
-/

namespace FrTax

/-! ## General properties -/

/-- The décote never makes the tax negative. -/
theorem decote_le (p : Params) (d : Decl) (t : Int) : decote p d t ≤ t := by
  unfold decote; exact Int.min_le_left _ _

/-- **The tax after the décote is non-decreasing in the tax before it**, for every couple or single person: the
décote (art. 197, I, 4, a) lowers tax but never reverses its order, rounding included. -/
theorem afterDecote_mono (base t t' : Int) (_h0 : 0 ≤ t) (h : t ≤ t') :
    t - min t (pos (rnd (base * 10000 - 4525 * t) 10000)) ≤
    t' - min t' (pos (rnd (base * 10000 - 4525 * t') 10000)) := by
  unfold pos rnd; omega

/-- Inside the décote's range a euro of tax before the décote costs 1.4525 euros after it, so the décote is a
45.25 % surcharge on each euro there (proved in 1/10 000 euro, before rounding). -/
theorem decote_slope (base t : Int) (_h1 : 0 ≤ base * 10000 - 4525 * t) (_h2 : base * 10000 - 4525 * t ≤ t * 10000) :
    t * 10000 - (base * 10000 - 4525 * t) = 14525 * t - base * 10000 := by omega

/-- One slice of the scale is non-decreasing in income. -/
theorem slice_mono (rate A B r r' : Int) (hrate : 0 ≤ rate) (h : r ≤ r') :
    rate * pos (min (4 * r) B - A) ≤ rate * pos (min (4 * r') B - A) := by
  apply Int.mul_le_mul_of_nonneg_left _ hrate
  unfold pos; omega

/-- **The tax on the scale is non-decreasing in income** for any number of parts and any year's brackets (art. 197,
I, 1 with art. 193 and the rounding of art. 1657). -/
theorem scaleTax_mono (p : Params) (q r r' : Int) (h : r ≤ r') : scaleTax p r q ≤ scaleTax p r' q := by
  unfold scaleTax
  apply rnd_mono (by omega)
  have h1 := slice_mono 11 (q * p.b1) (q * p.b2) r r' (by omega) h
  have h2 := slice_mono 30 (q * p.b2) (q * p.b3) r r' (by omega) h
  have h3 := slice_mono 41 (q * p.b3) (q * p.b4) r r' (by omega) h
  have h4 : 45 * pos (4 * r - q * p.b4) ≤ 45 * pos (4 * r' - q * p.b4) := by
    apply Int.mul_le_mul_of_nonneg_left _ (by omega); unfold pos; omega
  simp only []
  omega

/-- The cap on the quotient familial can only raise the tax (art. 197, I, 2), before the complement. -/
theorem capped_ge_full (p : Params) (d : Decl) (r : Int) : (capped p d r).full ≤ (capped p d r).capped := by
  unfold capped; simp only []; omega

/-! ## The statute's indexation reproduces the published amounts

Art. 157 bis: amounts "relevés chaque année dans la même proportion que la limite supérieure de la première
tranche du barème ... arrondis ... à l'euro supérieur en ce qui concerne les abattements et à la dizaine d'euros
supérieure en ce qui concerne les plafonds de revenus". First-slice limits: 11 294 € (income 2023), 11 497 €
(2024), 11 600 € (2025). -/

def ceilDiv (a b : Int) : Int := (a + b - 1) / b
def up (amount old new : Int) : Int := ceilDiv (amount * new) old
def upTen (amount old new : Int) : Int := 10 * ceilDiv (amount * new) (old * 10)

theorem age_2024 : up 2746 11294 11497 = p2024.ageHi ∧ up 1373 11294 11497 = p2024.ageLo ∧
    upTen 17200 11294 11497 = p2024.ageT1 ∧ upTen 27670 11294 11497 = p2024.ageT2 := by decide

theorem age_2025 : up 2796 11497 11600 = p2025.ageHi ∧ up 1398 11497 11600 = p2025.ageLo ∧
    upTen 17510 11497 11600 = p2025.ageT1 ∧ upTen 28170 11497 11600 = p2025.ageT2 := by decide

/-- Art. 83, 3°: the cap and minimum of the 10 % allowance on salaries are "relevé[s] dans la même proportion que
la limite supérieure de la première tranche": 14 171 € and 495 € (income 2023) give the published 14 426 € and
504 € for 2024, then 14 555 € and 509 € for 2025 (to the nearest euro). -/
theorem salary_allowance_indexed :
    rnd (14171 * 11497) 11294 = p2024.salMax ∧ rnd (495 * 11497) 11294 = p2024.salMin ∧
    rnd (14426 * 11600) 11497 = p2025.salMax ∧ rnd (504 * 11600) 11497 = p2025.salMin := by decide

/-- Art. 158, 5, a: the pension cap is "révisé selon les mêmes modalités que la limite supérieure de la première
tranche", that is by the year's indexation rate (+1.8 % for 2024, +0.9 % for 2025, the rates applied to the
scale). That gives the published 4 399 € and 4 439 €; the same-proportion rule of art. 83 would give 4 438 €
for 2025: the two articles' different words give different euros. -/
theorem pension_cap_indexed :
    rnd (4321 * 1018) 1000 = p2024.penMax ∧ rnd (4399 * 1009) 1000 = p2025.penMax ∧
    rnd (442 * 1018) 1000 = p2024.penMin ∧ rnd (450 * 1009) 1000 = p2025.penMin ∧
    rnd (4399 * 11600) 11497 = 4438 := by decide

/-! ## Cliffs -/

/-- **The 61 € notch** (art. 1657, 1 bis): a single person with 17 595 € of taxable income owes 60 €, which is not
collected; with one euro more, 62 € (income 2025). -/
theorem notch_61 : tableTax p2025 0 4 17595 = 60 ∧ tableTax p2025 0 4 17596 = 62 := by decide

/-- **The art. 157 bis cliff**: a single person over 65 whose revenu net global goes from 28 430 € to 28 431 €
loses the 1 411 € allowance; the tax rises by 226 € for one euro of income (income 2025). -/
theorem age_cliff :
    tableTax p2025 0 4 (28430 - 1411) = 1566 ∧ tableTax p2025 0 4 28431 = 1792 := by decide

/-! ## Counterexamples to figures printed in the brochure pratique

Tableau 7 ("Seuils de mise en recouvrement") prints the taxable income below which the tax is under 61 €. -/

/-- Edition 2025 (income 2024), married couple, 2.5 parts: printed 38 329 €. At 38 320 € the tax is already 61 €,
and 38 320 € is the first such income. -/
theorem brochure2025_table7_couple_25 :
    tableTax p2024 4 10 38320 = 61 ∧ tableTax p2024 4 10 38319 = 59 := by decide

/-- Edition 2026 (income 2025), married couple, 4.5 parts: printed 62 869 €; the threshold is 61 860 €. -/
theorem brochure2026_table7_couple_45 :
    tableTax p2025 4 18 61860 = 61 ∧ tableTax p2025 4 18 61859 = 60 := by decide

/-- Edition 2026, married couple, 2.5 parts: printed 38 669 €; the threshold is 38 660 € (the single-person row
of the same table, 17 596 € for one part, is right). -/
theorem brochure2026_table7_couple_25 :
    tableTax p2025 4 10 38660 ≥ 61 ∧ tableTax p2025 4 10 38659 < 61 ∧
    tableTax p2025 0 4 17596 ≥ 61 ∧ tableTax p2025 0 4 17595 < 61 := by decide

/-! ## Axioms used -/
#print axioms scaleTax_mono
#print axioms afterDecote_mono
#print axioms brochure2026_table7_couple_45
#print axioms age_2025

end FrTax
