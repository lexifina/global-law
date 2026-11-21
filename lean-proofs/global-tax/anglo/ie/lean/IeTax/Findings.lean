import IeTax.Theorems

/-!
# The findings as Lean statements (FINDINGS.md F-numbers)

Kernel-checked (`theorem ... := by decide`) where the computation is small; household-level figures (which run the
whole household function) are `#guard`s, evaluated when the file is compiled.
-/

namespace IeTax
open TaxKernel

/-! ## F9: the PRSI notch at €352.01 grows with every scheduled rate rise (the €12 credit is fixed) -/
/-- 4 % (2016-Sep 2024): €2.0804 a week. -/
theorem prsi_notch_400 : prsiWeekX 400 35201 = 12482400 := by decide
/-- 4.1 % (Oct 2024-Sep 2025): €2.4324. -/
theorem prsi_notch_410 : prsiWeekX 410 35201 = 14594460 := by decide
/-- 4.2 % (Oct 2025-Sep 2026): €2.7845. -/
theorem prsi_notch_420 : prsiWeekX 420 35201 = 16706520 := by decide
/-- 4.7 % (from 1 Oct 2028, SW(MP)A 2024 s. 3(5), Table col. (8)): €4.5444. -/
theorem prsi_notch_470 : prsiWeekX 470 35201 = 27266820 := by decide

/-! ## F12: investment income held by the lower-earning spouse raises the s. 15(3) band -/
-- one earner €100,000 and €50,000 of dividends: all held by the earner vs all held by the other spouse
def f12a : HH := { persons := [{ wages := eur 100000, dividends := eur 50000 }, {}], married := true, kids := 0 }
def f12b : HH := { persons := [{ wages := eur 100000 }, { dividends := eur 50000 }], married := true, kids := 0 }
-- income tax: the band rises by €35,000 (20 points on €35,000 = €7,000)
#guard (hhCalc f12a).it - (hhCalc f12b).it = eur 7000
-- with USC and PRSI (individual), the whole gain is €9,954 (results/search/s3_allocation.json)
#guard ((hhCalc f12a).it + (hhCalc f12a).usc + (hhCalc f12a).prsiS)
     - ((hhCalc f12b).it + (hhCalc f12b).usc + (hhCalc f12b).prsiS) = eur 9954

/-! ## F13: a one-earner married couple pays €3,800 less than the same unmarried couple -/
def f13m : HH := { persons := [{ wages := eur 60000 }, {}], married := true, kids := 0 }
def f13u : HH := { persons := [{ wages := eur 60000 }, {}], married := false, kids := 0 }
#guard (hhCalc f13u).it - (hhCalc f13m).it = eur 3800

/-! ## F16: the USC 70+ limit of €60,000 is a cliff of €326.18 -/
theorem usc70_cliff : usc { age := 71, pension := eur 60000 + 1 } - usc { age := 71, pension := eur 60000 } = 32618 := by
  decide

/-! ## F17: the €20 minimum WFP ends in a cliff of €1,040 a year (52 × €20) -/
def lp (w : Int) : HH := { persons := [{ age := 35, wages := eur w }], married := false, kids := 2 }
#guard (hhCalc (lp 49090)).wfp = 52 * eur 20
#guard (hhCalc (lp 49100)).wfp = 0

/-! ## F19: Class S €650 minimum at €5,000 of reckonable income -/
theorem classS_notch : prsiS { se := eur 5000 } - prsiS { se := eur 5000 - 1 } = eur 650 := by decide

end IeTax
