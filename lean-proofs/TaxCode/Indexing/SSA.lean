/-
  Social Security contribution and benefit base for 2025 and 2026, recomputed from 42 U.S.C. §430 and the
  automatic cost-of-living increase of 42 U.S.C. §415(i).

  §430(a): the base is redetermined only when the Commissioner "pursuant to section 415(i) ... increases benefits
  effective with the December following a cost-of-living computation quarter".
  §430(b): the base is the base in effect in the determination year or, if larger, $60,600 × AWI(year before the
  determination year) / AWI(1992), "if not a multiple of $300, being rounded to the next higher multiple of $300
  where such product is a multiple of $150 but not of $300 and to the nearest multiple of $300 in any other case"
  (= nearest $300, halves up).
  §415(i)(1)-(2): the increase is the percentage rise of the CPI (CPI-W) from the last cost-of-living computation
  quarter to the third quarter of the current year, "rounded to the nearest one-tenth of 1 percent"; 20 CFR 404.275
  rounds each quarterly mean to 0.001.

  Inputs (Federal Register notices "Cost-of-Living Increase and Other Determinations" for 2025, 89 FR 85276,
  doc. 2024-24871, and for 2026, doc. 2025-19763; https://www.federalregister.gov): AWI 1992 $22,935.42,
  AWI 2023 $66,621.80, AWI 2024 $69,846.57; CPI-W Jul–Sep 2023 299.899, 301.551, 302.257; Jul–Sep 2024 308.501,
  308.640, 309.046; Jul–Sep 2025 316.349, 317.306, 318.139. Published: base $168,600 (2024), $176,100 (2025),
  $184,500 (2026); COLA 2.5% (Dec 2024), 2.8% (Dec 2025).
-/
import TaxCode.Indexing.Formula
namespace TaxCode.Indexing.SSA
open TaxCode.Indexing

/-- National average wage index, in cents. -/
def awi1992 : Nat := 2293542
def awi2023 : Nat := 6662180
def awi2024 : Nat := 6984657

/-- §430(b): base for the year after the determination year `prior` = base in effect in the determination year. -/
def cbb (prior awiPrev : Nat) : Nat := max prior (roundNear (60600 * awiPrev) awi1992 300)

/-- quarterly CPI-W mean (thousandths), rounded to the nearest 0.001 (20 CFR 404.275) -/
def qmean (a b c : Nat) : Nat := roundNear (a + b + c) 3 1

/-- §415(i)(2)(A)(ii): percentage increase in tenths of a percent, rounded to the nearest tenth -/
def colaTenths (q0 q1 : Nat) : Nat := roundNear (1000 * (q1 - q0)) q0 1

def q2023 : Nat := qmean 299899 301551 302257
def q2024 : Nat := qmean 308501 308640 309046
def q2025 : Nat := qmean 316349 317306 318139

theorem quarter_means : q2023 = 301236 ∧ q2024 = 308729 ∧ q2025 = 317265 := by decide

/-- COLAs: 2.5% effective December 2024, 2.8% effective December 2025 (both > 0, so §430(a) redetermines the base). -/
theorem colas : colaTenths q2023 q2024 = 25 ∧ colaTenths q2024 q2025 = 28 := by decide

/-- Base for 2025 (determined in 2024 from AWI 2023) and 2026 (determined in 2025 from AWI 2024). -/
theorem cbb_2025 : cbb 168600 awi2023 = 176100 := by decide
theorem cbb_2026 : cbb 176100 awi2024 = 184500 := by decide

/-- The unrounded products, to show how far each is from a rounding boundary:
    $176,028.21 → $176,100 and $184,548.70 → $184,500 (cents, truncated). -/
theorem cbb_unrounded : 6060000 * awi2023 / awi1992 = 17602821 ∧ 6060000 * awi2024 / awi1992 = 18454870 := by decide

/-- The rounding is nearest-$300 with halves up, as the statute describes, for every product. -/
theorem cbb_rounding_is_multiple (n d : Nat) : 300 ∣ roundNear n d 300 := roundNear_dvd n d 300

end TaxCode.Indexing.SSA
