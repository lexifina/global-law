import HrTax.Household

/-!
# Croatia 2025: the findings as theorems on named households (FINDINGS.md F-numbers)

Each statement is a concrete computation of the full model (`computeCents`, cents) checked by the kernel (`decide`).
-/

set_option maxRecDepth 200000

namespace HrTax
open TaxKernel

/-- Household net income in cents (contract: gross − taxes − contributions + benefits). -/
def netCents (c : Canon) : Int := let h := computeCents c; C * c.gross - h.tax - h.social + h.benefit

/-! ## F10 Doplatak za djecu: five brackets, each an all-or-nothing step -/
/-- One earner, spouse without income, children 6 and 11, Zagreb. -/
def cpl2k (w : Int) : Canon :=
  { id := "cpl2k", adults := [{ age := 40, wages := w }, { age := 40 }], married := true,
    children := [{ age := 6 }, { age := 11 }] }
/-- At 40.899 € the family gets 741,60 € of doplatak; one euro more of pay and it gets nothing: net income falls by
741,01 € (the extra euro leaves 0,59 € after contributions and tax, against 741,60 € of benefit lost). -/

theorem dzd_cliff :
    ((computeCents (cpl2k 40899)).benefit, (computeCents (cpl2k 40900)).benefit,
      netCents (cpl2k 40899) - netCents (cpl2k 40900)) = (74160, 0, 74101) := by decide

/-- The steps for a lone parent with two children (3 members), the year: 158,88 € at 7.272 €, 211,92 € at 11.539 €, 211,92 € at 19.885 € and 741,60 € at 30.205 € of pay. -/
def sp2k (w : Int) : Canon := { id := "sp2k", adults := [{ age := 40, wages := w }], children := [{ age := 6 }, { age := 11 }] }

theorem dzd_steps :
    [7271, 7272, 11538, 11539, 19884, 19885, 30204, 30205].map (fun w => (computeCents (sp2k w)).benefit) =
      [132432, 116544, 116544, 95352, 95352, 74160, 74160, 0] := by decide

/-! ## F11 A dependent spouse: 1 € of the spouse's own income costs the earner 828 € -/
def cplDep (s : Int) : Canon :=
  { id := "dep", adults := [{ age := 40, wages := 30000 }, { age := 66, pension := s }], married := true }
theorem dependant_cliff :
    ((computeCents (cplDep 3600)).tax, (computeCents (cplDep 3601)).tax,
      netCents (cplDep 3600) - netCents (cplDep 3601)) = (303600, 386400, 82700) := by decide

/-! ## F12 Paušal classes: one cent over a class limit costs 72-192,60 € of tax -/
theorem pausal_notches :
    [1130000, 1530000, 1990000, 3060000, 4000000, 5000000].map (fun r => pausalTax (r + 1) - pausalTax r) =
      [7200, 8280, 19260, 16920, 18000, 18000] := by decide

/-! ## F13 Pay timing across months: the pension-base reduction and the monthly cap have no annual equalisation -/
/-- 24.000 € a year: evenly 2.000 € a month, or the 2025 minimum wage (970 €, Uredba o visini minimalne plaće za 2025., NN 124/2024-2072) in
eleven months and 13.330 € in December. Employee contributions: 4.800,00 € vs 4.019,35 €. -/
def even24 : List Int := List.replicate 12 200000
def uneven24 : List Int := List.replicate 11 97000 ++ [1333000]
theorem pay_timing :
    (even24.foldl (· + ·) 0, uneven24.foldl (· + ·) 0, eeContribMonths true even24, eeContribMonths true uneven24) =
      (2400000, 2400000, 480000, 401935) := by decide
/-- Of the 780,65 € saved, 272,25 € is the base reduction harvested in eleven months (15 % × 11 × 165 €; pension
rights are computed without it, ZD čl. 21.a st. 7) and 508,40 € the December pay above the monthly cap of
10.788 € (20 % × 2.542 €; pension rights also capped). -/
theorem pay_timing_parts :
    (11 * (p1Month true 97000 + p2Month true 97000) + (p1Month true 1333000 + p2Month true 1333000),
      11 * rnd (1500 * baseReduction.amount 97000), rnd (2000 * (1333000 - maxMonthlyBase))) =
      (401935, 27225, 50840) := by decide

/-! ## F14 Residence: the same wage in Zagreb (23 %) and in a 15 % municipality -/
def single (w : Int) (lo hi : Int) : Canon :=
  { id := "s", adults := [{ age := 40, wages := w }], raw := Lean.Json.mkObj [("lowerRate", lo), ("higherRate", hi)] }
theorem residence_gain :
    ((computeCents (single 24612 2300 3300)).tax, (computeCents (single 24612 1500 2500)).tax) = (287261, 187344) := by
  decide

/-! ## F15 Young workers: the year of the 26th and 31st birthdays -/
def young (a : Nat) : Canon := { id := "y", adults := [{ age := a, wages := 30000 }] }
theorem young_steps :
    [25, 26, 30, 31].map (fun a => (computeCents (young a)).tax) = [0, 193200, 193200, 386400] := by decide

end HrTax

namespace HrTax
open TaxKernel

/-! ## F8 Zagreb 2025: January and February withheld at the 2024 rates (refunded in the annual assessment) -/
def emp (w : Int) : Person := { wageDoh := w - eeContribYear true w, receipts := w }
/-- Single employee, no children, pay 24.612 € (Eurostat's 2025 AW), 48.000 € and 96.000 €: withheld 2.885,06 € vs
annual tax 2.872,61 € (12,45 € refunded), 31,20 € and 98,40 € refunded. -/
theorem zagreb_overwithholding :
    [2461200, 4800000, 9600000].map (fun w => whYearZagreb true basicPA w - (emp w).tax zagreb2025) =
      [1245, 3120, 9840] := by decide

end HrTax
