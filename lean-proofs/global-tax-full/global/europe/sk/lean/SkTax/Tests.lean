import SkTax.Country

/-!
# Official worked figures, kernel-checked (`decide`, no `native_decide`)

**Source A**: Finančná správa, "Daňový bonus na vyživované dieťa za rok 2025", podpora.financnasprava.sk/790897
(fetched 2026-11-19, `refs/fs/fs_bonus2025_790897.txt`), otázky 2–6.
**Source B**: Finančná správa, "Daňový bonus na dieťa v roku 2025", podpora.financnasprava.sk/272586
(`refs/fs/fs_bonus2025_272586.txt`), príklady 1, 2, 4–8.
**Source C**: Finančná správa, "Zmeny platné od 1.1.2025", podpora.financnasprava.sk/476621
(`refs/fs/fs_zmeny2025_476621.txt`), otázky 1–5.
**Source D**: OECD Taxing Wages 2025 (SVK, year 2025; `cmp20/central/oecd/tw_cou_xdc_3.json`): the OECD's cent
values at its own average wage 19 590,43 € (GEBT). The OECD charges 13,4 % on the annual wage in one step; the statute
rounds each insurance's monthly amount down (ZSP § 129 ods. 2), see `oecdStyle` below and FINDINGS F1.
-/

namespace SkTax
open TaxKernel

/-! ## A: annual bonus (amounts in cents) -/
-- otázka 2: base 23 500 €, children 5 and 10 → 2 400 €
example : bonus [{age := 5}, {age := 10}] 2350000 2350000 = 240000 := by decide
-- otázka 3: base 6 250 €, children 2 and 12 → 36 % = 2 250 €
example : bonus [{age := 2}, {age := 12}] 625000 625000 = 225000 := by decide
-- otázka 4: base 3 250 €, a 12-year-old and a child born in November → 785,40 + 195 = 980,40 €
example : bonus [{age := 12}, {age := 0, fromMonth := 11}] 325000 325000 = 98040 := by decide
-- otázka 5: base 30 000 €, children 2 and 12 → 2 × (1 200 − 426) = 1 548 €
example : bonus [{age := 2}, {age := 12}] 3000000 3000000 = 154800 := by decide
-- otázka 6: base 30 000 €, a 5-year-old and a child born in November → 774 + 129 = 903 €
example : bonus [{age := 5}, {age := 0, fromMonth := 11}] 3000000 3000000 = 90300 := by decide

/-! ## B: annual (príklady 4, 7, 8) and monthly (príklady 1, 2, 5, 6, 7) -/
example : bonus [{age := 7}] 2750000 2750000 = 102400 := by decide                    -- príklad 4: 1 024 €
example : bonus [{age := 7}, {age := 9}] 2550000 2550000 = 240000 := by decide       -- príklad 7: 2 400 €
example : bonus [{age := 7}] 2635000 2635000 = 113900 := by decide                    -- príklad 8: 1 139 €
example : monthBonus [{age := 5}, {age := 9}] 1 100000 = 20000 := by decide           -- príklad 1: 200 €
example : monthBonus [{age := 5}] 10 33000 = 9570 := by decide                       -- príklad 2: 95,70 €
example : monthBonus [{age := 10}] 9 240000 = 7450 := by decide                      -- príklad 5: 74,50 €
example : monthBonus [{age := 4}, {age := 17}] 3 255000 = 6900 := by decide          -- príklad 6: 59,50 + 9,50 €
example : monthBonus [{age := 5}, {age := 9}] 11 350000 = 0 := by decide             -- príklad 7: November 0 €

/-! ## C: age limits and the monthly forms -/
example : bonus [{age := 15, birthMonth := 6}] 2000000 2000000 = 90000 := by decide  -- otázka 1: 6 × 100 + 6 × 50
example : bonus [{age := 18, birthMonth := 4}] 2000000 2000000 = 20000 := by decide  -- otázka 2: until April
example : monthBonus [{age := 5}, {age := 9}] 1 50000 = 18000 := by decide           -- otázka 3: 180 €
example : monthBonus [{age := 5}] 1 250000 = 6450 := by decide                       -- otázka 4: 64,50 €
example : bonus [{age := 7}] 2750000 2750000 = 102400 := by decide                    -- otázka 5: 1 024 €

/-! ## D: OECD Taxing Wages 2025, at the OECD's cent wages -/

/-- The OECD's own convention: 13,4 % of the annual wage, rounded once. -/
def oecdStyleZd5 (w : Int) : Int := w - pctH w 1340

/-- With the OECD convention for contributions, the model's § 11 and § 15 give the OECD's values to the cent (the OECD
keeps unrounded fractions: GEBT 32 716,013426, BTA 5 027,341093, CGTC 23 304,726534, HFTA 5 260,608):
S67 (13 125,59 €): CGTC 5 612,97, CGITLETC 1 066,46; S100 (19 590,43 €): 11 211,52, 2 130,19;
S167 (32 716,01 €): BTA 5 027,34, CGTC 23 304,72 (OECD 23 304,7265), CGITLETC 4 427,90; M100_0: HFTA 5 260,61,
CGTC 5 950,91, CGITLETC 1 130,67. -/
example : oecdStyleZd5 1312559 - nczTaxpayer (oecdStyleZd5 1312559) = 561297 ∧
    taxSched (oecdStyleZd5 1312559 - nczTaxpayer (oecdStyleZd5 1312559)) = 106646 := by decide
example : oecdStyleZd5 1959043 - nczTaxpayer (oecdStyleZd5 1959043) = 1121152 ∧
    taxSched (oecdStyleZd5 1959043 - nczTaxpayer (oecdStyleZd5 1959043)) = 213019 := by decide
example : nczTaxpayer (oecdStyleZd5 3271601) = 502734 ∧
    oecdStyleZd5 3271601 - nczTaxpayer (oecdStyleZd5 3271601) = 2330472 ∧
    taxSched (oecdStyleZd5 3271601 - nczTaxpayer (oecdStyleZd5 3271601)) = 442790 := by decide
example : nczSpouse (oecdStyleZd5 1959043) 0 = 526061 ∧
    oecdStyleZd5 1959043 - nczTaxpayer (oecdStyleZd5 1959043) - nczSpouse (oecdStyleZd5 1959043) 0 = 595091 ∧
    taxSched (oecdStyleZd5 1959043 - nczTaxpayer (oecdStyleZd5 1959043) - nczSpouse (oecdStyleZd5 1959043) 0) = 113067 := by
  decide
-- OECD CTC 2 400 € and CTGG 1 440 € for two children aged 6 and 11
example : bonus [{age := 6}, {age := 11}] 1136697 1136697 = 240000 ∧ pridavokFor [{age := 6}, {age := 11}] = 144000 := by
  decide
/-- The statutory monthly rounding (ZSP § 129 ods. 2) gives contributions 0,21 €–0,30 € below the OECD's single 13,4 %
(S67: 1 758,62 vs 1 758,83; S100: 2 624,89 vs 2 625,12; S167: 4 383,65 vs 4 383,95). -/
example : eeSocialYear 1312559 + eeHealthYear 1312559 = 175862 ∧ eeSocialYear 1959043 + eeHealthYear 1959043 = 262489 ∧
    eeSocialYear 3271601 + eeHealthYear 3271601 = 438365 := by decide

end SkTax

namespace SkTax
/-! ## E: a third-party worked example (not official): podnikajte.sk, "Daňový bonus na dieťa od 1.1.2025 – príklady"
(`refs/lit/podnikajte_bonus2025_priklady.txt`): pán Pavol, base 4 400 € and children of 15 and under 15 → 36 % = 1 584 €;
base 26 800 € (54 000 − 20 000 − 7 200) and children of 16 and 17 → 2 × (600 − 106) = 988 €. -/
example : bonus [{age := 10}, {age := 16}] 440000 440000 = 158400 := by decide
example : bonus [{age := 16}, {age := 17}] 2680000 2680000 = 98800 := by decide
end SkTax
