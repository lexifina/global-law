import PTTax.Household

/-!
# Loopholes, cliffs and notches found in the 2025 model (NOVEL.md / CATALOGUE.md), each proved on the model

Every statement below is about the model's own functions (`abono`, `houseCalc`, `personCalc`), evaluated by
`decide`: the amounts are exact, in cents.
-/

namespace PTTax
open TaxKernel

/-! ## N1 Abono de família: the 3.º → 4.º escalão cliff for children over six

DL 176/2003 art. 14 n.º 2 (escalão limit 1,7 × 14 × IAS = 12 435,50 € of reference income) and Portaria
112/2025/1 art. 2 n.º 1 d) (the 4.º escalão has amounts only up to 72 months): with two children aged 8 and 10,
the reference income is the household's income / 3, so one euro above 37 306,50 € of household income removes the
whole abono. -/

/-- Couple, two children (8 and 10): 1 276,32 € at 37 306 €, nothing at 37 307 €. -/
theorem abono_cliff_couple : (abono 3730600 [8, 10] false).1 = 127632 ∧ (abono 3730700 [8, 10] false).1 = 0 := by
  decide

/-- Single parent, same children: 1 914,48 € (monoparental +50 %, paid monthly) at 37 306 €, nothing at 37 307 €. -/
theorem abono_cliff_single_parent :
    (abono 3730600 [8, 10] true).1 = 191448 ∧ (abono 3730700 [8, 10] true).1 = 0 := by decide

/-- The 2.º → 3.º escalão step (household income 3 × 7 315 € = 21 945 €): 2 × (73,51 − 53,18) × 12 = 487,92 €. -/
theorem abono_step_2_3 : (abono 2194500 [8, 10] false).1 - (abono 2194600 [8, 10] false).1 = 48792 := by decide

/-! ## N2 Art. 70 n.º 4 a): the joint return loses every mínimo de existência abatimento at 2 × 16 093 €

"O abatimento ... não se aplica a qualquer dos titulares quando a soma dos rendimentos brutos de todos os
titulares é superior a 2,2 x 14 x IAS multiplicado pelo número de sujeitos passivos" (2025: 32 186 € for two). -/

def spouseA : Person := { wages := 1300000 }
def spouseB (w : Int) : Person := { wages := w }

/-- Joint return, 13 000 € + 19 186 € (sum 32 186 €): the 13 000 € spouse keeps an abatimento of 3 585,85 € and
the couple's IRS is 2 584,01 €. One euro more (19 187 €): no abatimento, joint IRS 3 157,90 €, and separate
returns (where the 13 000 € spouse keeps the abatimento) cost 2 833,93 €. The best choice loses 249,92 € for
one euro of extra income (573,89 € if the couple stays joint). -/
theorem me_joint_notch :
    (houseCalc [spouseA, spouseB 1918600] [] 0 "joint" {}).irs = 258401 ∧
    (houseCalc [spouseA, spouseB 1918700] [] 0 "joint" {}).irs = 315790 ∧
    (houseCalc [spouseA, spouseB 1918700] [] 0 "separate" {}).irs = 283393 ∧
    (houseCalc [spouseA, spouseB 1918600] [] 0 "separate" {}).irs = 283372 := by decide

/-! ## N3 IRS Jovem (art. 12-B): the cliff at the 36th birthday and after the 10th year -/

/-- 30 000 € of wages in the 3rd year of income: 22 500 € exempt at 35, nothing at 36 ("até 35 anos de idade",
assessed on 31 December per the AT leaflet), nothing in an 11th year. -/
theorem jovem_age_cliff :
    (personCalc { wages := 3000000, age := 35, jovemYear := 3 } {}).exempt = 2250000 ∧
    (personCalc { wages := 3000000, age := 36, jovemYear := 3 } {}).exempt = 0 ∧
    (personCalc { wages := 3000000, age := 30, jovemYear := 11 } {}).exempt = 0 := by decide

/-- The cap of 55 × IAS binds from 28 737,50 € of A/B income in the first year (100 %). -/
theorem jovem_cap : (personCalc { wages := 5000000, age := 25, jovemYear := 1 } {}).exempt = 2873750 := by decide

end PTTax
