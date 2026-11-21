import TaxKernel

/-! # Codul fiscal art. 77 alin. (2) as in force in 2022 (wording of OUG nr. 79/2017, in force 2018-01-01 until
OG nr. 16/2022 took effect on 2023-01-01), transcribed row by row by `improve-central` round 2 from
`law/r2/a77_2022.txt` (Global law read_law, art. 77 as in force on 2022-06-30; official text
https://legislatie.just.ro/Public/DetaliiDocument/194296). "Deducerea personală se acordă pentru persoanele fizice care
au un venit lunar brut de până la 1.950 lei inclusiv, astfel: ... 510 lei; ... 670 lei; ... 830 lei; ... 990 lei; ...
1.310 lei" and, for 1.951 to 3.600 lei, the table; "de peste 3.600 lei nu se acordă deducerea personală". Values
are lei for 0, 1, 2, 3 and "4 și peste 4" dependants. -/

namespace RoTax
open TaxKernel

/-- art. 77 alin. (2) (2022): (lo, hi, [lei for 0..4+ dependants]) by gross monthly wage. -/
def rows2022 : List (Int × Int × List Int) := [
  (1, 1950, [510, 670, 830, 990, 1310]),
  (1951, 2000, [495, 655, 815, 975, 1295]),
  (2001, 2050, [480, 640, 800, 960, 1280]),
  (2051, 2100, [465, 625, 785, 945, 1265]),
  (2101, 2150, [450, 610, 770, 930, 1250]),
  (2151, 2200, [435, 595, 755, 915, 1235]),
  (2201, 2250, [420, 580, 740, 900, 1220]),
  (2251, 2300, [405, 565, 725, 885, 1205]),
  (2301, 2350, [390, 550, 710, 870, 1190]),
  (2351, 2400, [375, 535, 695, 855, 1175]),
  (2401, 2450, [360, 520, 680, 840, 1160]),
  (2451, 2500, [345, 505, 665, 825, 1145]),
  (2501, 2550, [330, 490, 650, 810, 1130]),
  (2551, 2600, [315, 475, 635, 795, 1115]),
  (2601, 2650, [300, 460, 620, 780, 1100]),
  (2651, 2700, [285, 445, 605, 765, 1085]),
  (2701, 2750, [270, 430, 590, 750, 1070]),
  (2751, 2800, [255, 415, 575, 735, 1055]),
  (2801, 2850, [240, 400, 560, 720, 1040]),
  (2851, 2900, [225, 385, 545, 705, 1025]),
  (2901, 2950, [210, 370, 530, 690, 1010]),
  (2951, 3000, [195, 355, 515, 675, 995]),
  (3001, 3050, [180, 340, 500, 660, 980]),
  (3051, 3100, [165, 325, 485, 645, 965]),
  (3101, 3150, [150, 310, 470, 630, 950]),
  (3151, 3200, [135, 295, 455, 615, 935]),
  (3201, 3250, [120, 280, 440, 600, 920]),
  (3251, 3300, [105, 265, 425, 585, 905]),
  (3301, 3350, [90, 250, 410, 570, 890]),
  (3351, 3400, [75, 235, 395, 555, 875]),
  (3401, 3450, [60, 220, 380, 540, 860]),
  (3451, 3500, [45, 205, 365, 525, 845]),
  (3501, 3550, [30, 190, 350, 510, 830]),
  (3551, 3600, [15, 175, 335, 495, 815])]

/-- The 2022 personal deduction for gross monthly wage `g` and `n` dependants (0 above 3.600 lei; the first row
also covers a gross of 0). -/
def deduction2022 (g : Int) (n : Nat) : Int :=
  match rows2022.find? (fun (lo, hi, _) => decide (g ≤ hi) && (decide (lo ≤ g) || lo == 1)) with
  | some (_, _, v) => v.getD (min n 4) 0
  | none => 0

/-- The table is the formula "base − 15 lei per started 50 lei above 1.950 lei" (checked at both ends of every row
for every column). -/
theorem rows2022_formula :
    rows2022.all (fun (lo, hi, v) =>
      let k := if hi ≤ 1950 then 0 else (hi - 1950) / 50
      v == [510 - 15 * k, 670 - 15 * k, 830 - 15 * k, 990 - 15 * k, 1310 - 15 * k] &&
      (lo == 1 || lo == hi - 49)) = true := by decide

/-- art. 77 alin. (3) (2022): a dependant's income at most "510 lei lunar". -/
def dependantLimit2022 : Int := 510

end RoTax
