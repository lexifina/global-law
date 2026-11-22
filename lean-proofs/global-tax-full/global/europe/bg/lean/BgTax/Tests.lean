import BgTax.Household

/-!
# Regression tests: Eurostat `earn_nt_net` 2025 households (gross = Eurostat EUR × 1.95583, whole leva)

Referee values (BGN = EUR × 1.95583), `refs/eurostat/eurostat_bg.json`:
* P1_NCH_AW100: gross 36 421 (18 621.54 € × 1.95583 = 36 420.59); SOC 2 566.05 € = 5 018.76 лв.; TAX 1 605.55 € = 3 140.18 лв.
* P1_CH2_AW67: gross 24 402; SOC 3 362.56; TAX 903.91; FAM 828.31 € = 1 620.03 лв.
* CPL_CH2_AW100: FAM 1 620.03 лв. (model 1 554: Eurostat applies the April limit of 760 лв. to January-March;
  ЗДБРБ 2025 чл. 64, ал. 2, т. 1 sets 710 лв. for those months: FINDINGS F2).
* P1_NCH_AW167: SOC 6 829.46 лв. (model 6 672.24: Eurostat applies 4 130 лв. to January-March; ЗБДОО 2025 чл. 9,
  т. 1, б. "в" sets 3 750 лв.: FINDINGS F1).
-/

namespace BgTax.Tests
open TaxKernel BgTax

def h (id : String) (ws : List Int) (kids : List Nat := []) : Canon :=
  { id, adults := ws.map fun w => { wages := w }, married := ws.length == 2,
    children := kids.map fun a => { age := a } }

example : (out (h "aw100" [36421])).employeeSocial = 501876 := by native_decide
example : (out (h "aw100" [36421])).incomeTax = 314022 := by native_decide
example : (out (h "sp67" [24402] [6, 11])).incomeTax = 90395 := by native_decide
example : (out (h "sp67" [24402] [6, 11])).benefits = 162000 := by native_decide
example : (out (h "cpl" [36420, 0] [6, 11])).benefits = 155400 := by native_decide
example : (out (h "aw167" [60822])).employeeSocial = 667224 := by native_decide
/-- Above the year's ceiling the employee contributions are 13.78 % of 48 420 лв. = 6 672.28 лв. up to the
per-month rounding (6 672.24 лв.). -/
example : (out (h "hi" [100000])).employeeSocial = 667224 := by native_decide

end BgTax.Tests
