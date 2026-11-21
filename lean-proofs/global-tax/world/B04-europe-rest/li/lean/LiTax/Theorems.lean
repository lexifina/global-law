import LiTax.Basic

/-! # Liechtenstein: the printed "rate · x − subtract" tariff checked at its thresholds -/

namespace LiTax
open TaxKernel

/-- Jump (Rappen) of the literal tariff between the last franc of a row and the first franc of the next. -/
def jumps (rows : List Row) : List Int :=
  (rows.drop 1).map fun r => tariffRp rows r.lo - tariffRp rows (r.lo - 1)

/-- F1: the printed subtractions are rounded to the franc, so the literal tariff is not exactly continuous: at the
thresholds it moves by less than 1 CHF either way, and at several thresholds one franc more of Erwerb LOWERS the tax
(by up to 53 Rappen, tariff b at 206 116 CHF). The exact jumps, in Rappen: -/
theorem jumps_exact :
    (jumps tariffA, jumps tariffB, jumps tariffC) =
      ([0, 83, -16, -5, 6, 11, -33, 8], [0, 23, 24, -10, -44, 64, -53, 8], [11, -37, 64, -15, 6, 16, 27, 8]) := by decide
theorem jumps_below_one_franc :
    ((jumps tariffA ++ jumps tariffB ++ jumps tariffC).all fun j => -100 < j && j < 100) = true := by decide

/-- F2: the joint tariff c taxes a couple like two persons on tariff a with half the Erwerb each (full splitting),
within 1 CHF, on probes. -/
def probes : List Int := [30000, 50000, 80000, 100000, 150000, 200000]
theorem joint_is_splitting :
    (probes.all fun x => (tariffRp tariffC (2 * x) - 2 * tariffRp tariffA x) * (tariffRp tariffC (2 * x) - 2 * tariffRp tariffA x) ≤ 10000) = true := by
  decide

end LiTax
