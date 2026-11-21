import TaxKernel

/-!
# Kernel fidelity: the German tariff, splitting, Soli and social contributions 2025 with kernel parts

Built from kernel parts and the statute's parameters (no code from `~/cmp/de`), compared with `detax` on a grid
(`fidelity/check_fidelity.py`): the tariff and Soli on the zvE / Soli base `detax` reports, and each employee's
contributions on the wages.

| Statute | Kernel part |
|---|---|
| EStG § 32a (1) (2025, BGBl. 2024 I Nr. 449): zvE "auf volle Euro abgerundet"; five zones, two of them quadratic; result "abzurunden" | **not a `Schedule`** (a formula tariff; kernel gap: the tariff is a plain `Int → Int` with `Rounding`) |
| EStG § 32a (5) Splitting: "das Zweifache des Steuerbetrags ... für die Hälfte" | `splitting` (Unit) |
| SolZG § 3 (3), § 4: 5.5 %, Freigrenze €19,950 (€39,900 joint), at most 11.9 % of the excess | `Surcharge {rate := 550, exempt, glide := 1190}` in cents, `Rule.unitDown` |
| SGB VI § 158/§ 168, SGB III § 341, SGB V § 241/§ 242, SGB XI § 55 (2025): RV 9.3 %, AV 1.3 % to €96,600; KV 7.3 % + 1.25 % (half the average Zusatzbeitrag 2.5 %), PV 1.8 % (+0.6 % childless from 23; −0.25 % per child under 25 from the 2nd) to €66,150 | `Contribution.flatCapped`, cents, `Rule.unitHalfUp` |
-/

namespace Fidelity.De
open TaxKernel

/-- § 32a (1) 2025 in units of 10⁻¹⁰ euro for `x` whole euros (zones as in the statute). -/
def num (x : Int) : Int :=
  if x ≤ 12096 then 0
  else if x ≤ 17443 then (93230 * (x - 12096) + 1400 * 1000000) * (x - 12096)
  else if x ≤ 68480 then (17664 * (x - 17443) + 2397 * 1000000) * (x - 17443) + 101513 * 100000000
  else if x ≤ 277825 then (42 * x - 1091192) * 100000000
  else (45 * x - 1924667) * 100000000

/-- § 32a (1) Satz 6: one rounding, down to the euro (`Rounding.divR .down`). -/
def est (x : Int) : Int := divR .down (num x) 10000000000

/-- Single or joint (§ 32a (5) via the kernel's `splitting`, with the couple's zvE given as one amount). -/
def tariff (joint : Bool) (zve : Int) : Int := if joint then splitting est zve 0 else est zve

/-- SolZG § 3, § 4 in cents. -/
def soli (joint : Bool) : Surcharge :=
  { rate := 550, exempt := if joint then 3990000 else 1995000, glide := 1190, round := Rule.unitDown }

/-- Employee contributions 2025 (cents), half up to the cent. -/
def contributions (kidsUnder25 : Nat) (childless : Bool) : List Contribution :=
  let pv : Int := if childless then 240 else if kidsUnder25 ≤ 1 then 180
    else 180 - 25 * (min ((kidsUnder25 : Int) - 1) 4)
  [ { Contribution.flatCapped "RV" 930 9660000 with round := Rule.unitHalfUp },
    { Contribution.flatCapped "AV" 130 9660000 with round := Rule.unitHalfUp },
    { Contribution.flatCapped "KV" 855 6615000 with round := Rule.unitHalfUp },
    { Contribution.flatCapped "PV" pv 6615000 with round := Rule.unitHalfUp } ]

/-- Splitting through the kernel equals the statute's "twice the tax on half". -/
theorem tariff_joint (zve : Int) : tariff true zve = 2 * est (zve / 2) := by
  simp [tariff, splitting]

end Fidelity.De
