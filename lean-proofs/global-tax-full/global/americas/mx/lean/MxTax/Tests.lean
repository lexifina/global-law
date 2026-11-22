import MxTax.Household

/-!
# Official figures reproduced (kernel-checked with `decide`; no `native_decide`)

1. OECD Taxing Wages 2025, Mexico (`cmp20/emerging/oecd/tw_cou_xdc_4.json`, MEX 2025): CGITFP of S67, S100, S167
   (12,163.21; 25,804.83; 57,233.41 MXN) and BTA (4,603.55; 5,091.30), to the centavo.
2. The subsidy decree of DOF 31-12-2024 (considerandos): a worker with taxable income of 1.2 minimum wages a month
   (1.2 × 278.80 × 30.4 = 10,170.62) has "$9,381.00" a month after ISR without the subsidy, and the 2024 worker at
   1.2 × 248.93 × 30.4 = 9,081.04 had "$8,800.00" with the 2024 subsidy of 11.82 % of the UMA (= 390.12);
   13.8 % of the 2025 UMA "representa un monto de $475.00" and makes the increase proportional to the 12 %
   minimum-wage rise (8,800 × 1.12 = 9,856; ours 9,855.80).
-/

namespace MxTax
open TaxKernel

/-- OECD S100: ISR on 219,608.23 less the exempt 5,091.30 = 214,516.93 is 25,804.84 (OECD CGITFP 25,804.834 on the unrounded AW 219,608.226). -/
theorem oecd_S100_cgitfp : ticksToCentavos (tarifaTicks tarifa152 21451693) = 2580484 := by decide
/-- OECD S67: 147,137.51 − 4,603.55 = 142,533.96 → 12,163.21 (OECD 12,163.211). -/
theorem oecd_S67_cgitfp : ticksToCentavos (tarifaTicks tarifa152 14253396) = 1216321 := by decide
/-- OECD S167: 366,745.74 − 5,091.30 = 361,654.44 → 57,233.41 (OECD 57,233.407). -/
theorem oecd_S167_cgitfp : ticksToCentavos (tarifaTicks tarifa152 36165444) = 5723341 := by decide
/-- OECD BTA at S100: 30 UMA + 15 UMA = 5,091.30. -/
theorem oecd_S100_bta : (({ wages := 219608 } : WageIn).exempt) = 509130 := by decide
/-- OECD BTA at S67 (whole pesos of the canonical wage 147,138): 3,394.20 + 3 days of 147,138/365 = 4,603.55. -/
theorem oecd_S67_bta : (({ wages := 147138 } : WageIn).exempt) = 460355 := by decide

/-- DOF 31-12-2024: monthly ISR at 10,170.62 without subsidy is 789.47, leaving 9,381.15 ("$9,381.00"). -/
theorem decree2025_9381 : 1017062 - ticksToCentavos (tarifaTicks tarifa96 1017062) = 938115 := by decide
/-- DOF 31-12-2024: the 2024 worker at 9,081.04 with the 11.82 % subsidy (390.12) kept 8,800.24 ("$8,800.00"). -/
theorem decree2024_8800 :
    908104 - (ticksToCentavos (tarifaTicks tarifa96 908104) - mulDivHU umaMonthly2024 1182 BP) = 880024 := by decide
/-- With the 2025 subsidy of 474.65: 9,855.80 (the decree's target 8,800 × 1.12 = 9,856). -/
theorem decree2025_target :
    1017062 - (ticksToCentavos (tarifaTicks tarifa96 1017062) - subsidyMonth 2) = 985580 := by decide
/-- "13.8% ... representa un monto de $475.00": 474.65. -/
theorem subsidy_feb : subsidyMonth 2 = 47465 := by decide
theorem subsidy_jan : subsidyMonth 1 = 47495 := by decide
/-- The cap is 1.2 minimum wages a month: 1.2 × 278.80 × 30.4 = 10,170.62, rounded up to 10,171.00. -/
theorem cap_is_1p2_sm : salarioMinimo * 12 * 304 / 100 = 1017062 := by decide

end MxTax
