import LoopDe.Tariff

/-!
# Headline loophole results and the 2026 tariff boundary (EStG § 32a, § 34)

Tariff copied from `~/cmp/de/lean/DeTax/Tariff.lean` (statute coefficients). zvE values come from the `detax` exe
(`runs/recreate.json`); these theorems check the tariff arithmetic of the headline cases for those inputs.
-/

namespace LoopDe

/-! ## § 32a (1) Satz 2 from VZ 2026 (text fetched 2026-11-18, `refs/estg_32a_2026.html`):
"3. von 17 800 Euro bis 69 878 Euro: (173,10 • z + 2 397) • z + 1 034,87; 4. von 69 879 Euro bis 277 825 Euro:
0,42 • x – 11 135,63". Units of `num`: 10⁻¹⁰ euro. -/

/-- The zone-4 line starts 6,70 cent above the end of zone 3 (2025: 9,41 cent *below*, FINDINGS S1). -/
theorem jump2026_gap : (42 * 69878 - 1113563) * 100000000 - t2026.num 69878 = 670008290 := by decide

/-- By the unrounded formula the euro from 69 878 € to 69 879 € costs 48,70 cent: above the 45 % top rate. -/
theorem jump2026_step : t2026.num 69879 - t2026.num 69878 = 4870008290 := by decide

theorem jump2026_step_gt_top : t2026.num 69879 - t2026.num 69878 > 45 * 100000000 := by decide

/-- Satz 6 rounds the jump away: the tax is 18 213 € on both sides. -/
theorem jump2026_rounded : t2026.est 69878 = 18213 ∧ t2026.est 69879 = 18213 := by decide

/-- Around the jump (69 800 … 69 999 €) one more euro of zvE costs 0 or 1 euro of tax. -/
theorem jump2026_local_steps :
    (List.range 200).all (fun i =>
      let x : Int := 69800 + i
      decide (t2026.est x ≤ t2026.est (x + 1) ∧ t2026.est (x + 1) ≤ t2026.est x + 1)) = true := by decide

/-! ## L04: marrying by 31 December (§ 26 (1), § 32a (5)); one earner, 90 000 € wages.
zvE 73 346 € single, 73 310 € joint (two Sonderausgaben-Pauschbeträge). Soli 0 both ways. -/
theorem marriage_bonus_90k : t2025.est 73346 - t2025.estSplit 73310 = 7349 := by decide

/-! ## L27: severance of 100 000 € for an employee with 70 000 € wages (zvE 55 206 € without it).
§ 34 (1) Satz 2: ESt = ESt(verbleibendes zvE) + 5 × [ESt(verbleibendes zvE + 1/5 A) − ESt(verbleibendes zvE)];
Satz 3 when the remaining zvE is negative: 5 × ESt(zvE / 5). -/
def fuenftel (t : Tarif) (rest a : Int) : Int :=
  if rest < 0 ∧ 0 < rest + a then 5 * t.est ((rest + a) / 5)
  else t.est rest + 5 * (t.est (rest + a / 5) - t.est rest)

theorem severance_plain : t2025.est (55206 + 100000) = 54274 := by decide
theorem severance_fuenftel_same_year : fuenftel t2025 55206 100000 = 53030 := by decide
/-- Paid the next January with no other income (remaining zvE −36 €, the Sonderausgaben-Pauschbetrag). -/
theorem severance_fuenftel_empty_year : fuenftel t2025 (-36) 100000 = 8185 := by decide
/-- Moving the payment saves 32 260 € of income tax over the two years (Soli adds 2 916,65 €; `recreate.py` L27b). -/
theorem severance_timing_saving :
    fuenftel t2025 55206 100000 - (t2025.est 55206 + fuenftel t2025 (-36) 100000) = 32260 := by decide

end LoopDe
