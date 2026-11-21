import ITTax.Household

/-!
# Properties of the 2025 Italian rules, proved for all inputs (or at the statute's edges)

Kernel instances (TaxKernel API §5) for the art. 11 schedule and the Lazio schedules; then the Italy-specific
claims: what is continuous and what jumps at 8.500, 15.000, 20.000, 28.000, 32.000 and 40.000. Money in cents.
-/

namespace ITTax
open TaxKernel

/-! ## Art. 11: the kernel's schedule theorems -/
theorem irpef_progressive : irpefSched.progressive = true := by decide
theorem irpef_mono : Monotone' irpefSched.ticks :=
  Schedule.ticks_mono_of_progressive irpefSched irpef_progressive
theorem irpef_convex : Convex irpefSched.ticks := Schedule.ticks_convex _ irpef_progressive
/-- The marginal rate on (x, x+1] is the band's (23 / 35 / 43 %). -/
theorem irpef_marginal (x : Int) : irpefSched.ticks (x + 1) - irpefSched.ticks x = irpefSched.rate x :=
  Schedule.ticks_succ irpefSched x
theorem lazioHigh_progressive : lazioHigh.progressive = true := by decide
theorem lazioLow_progressive : lazioLow.progressive = true := by decide

/-! ## L. 207/2024 c. 6: the extra detrazione is continuous (at most one cent per cent of income) -/
/-- Between 32.000 and 40.000 one more cent of income removes at most one cent of the detrazione (1/8 of a
cent per cent before rounding): the withdrawal is a 12,5 % taper, no jump. -/
theorem ulteriore_taper_step (r : Int) (h1 : eur 32000 ≤ r) (h2 : r < eur 40000) :
    0 ≤ ulteriore r - ulteriore (r + 1) ∧ ulteriore r - ulteriore (r + 1) ≤ 1 := by
  unfold ulteriore mulFrac ulterioreFull eur at *
  simp only [divR] at *
  split <;> split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> omega

/-- At 20.000 the cash sum of c. 4 (4,8 % of employment income) ends and the c. 6 detrazione (1.000) starts:
an employee with reddito complessivo = employment income = 20.000 gets 960 in cash; at 20.000,01 he gets a
detrazione of 1.000 instead (worth 1.000 only if his net tax can absorb it). -/
theorem cuneo_at_20000 : cuneoSomma (eur 20000) (eur 20000) = eur 960 ∧ ulteriore (eur 20000) = 0 ∧
    cuneoSomma (eur 20000 + 1) (eur 20000 + 1) = 0 ∧ ulteriore (eur 20000 + 1) = eur 1000 := by decide

/-! ## L. 207/2024 c. 4: the percentage applies to the whole income, so the sum falls at 8.500 and 15.000 -/
/-- 8.500: 7,1 % of 8.500 = 603,50; 5,3 % of 8.500,01 = 450,50: one cent more income, 153 euro less. -/
theorem cuneo_cliff_8500 :
    cuneoSomma (eur 8500) (eur 8500) = 60350 ∧ cuneoSomma (eur 8500 + 1) (eur 8500 + 1) = 45050 := by decide
/-- 15.000: 5,3 % of 15.000 = 795; 4,8 % of 15.000,01 = 720: 75 euro less. -/
theorem cuneo_cliff_15000 :
    cuneoSomma (eur 15000) (eur 15000) = eur 795 ∧ cuneoSomma (eur 15000 + 1) (eur 15000 + 1) = eur 720 := by decide

/-! ## Art. 13 c. 1: the detrazione jumps UP at 15.000 (1.955 -> 3.099,88), while the trattamento integrativo
(1.200) stops for a taxpayer without family detrazioni -/
theorem detrDip_jump_15000 : detrDip (eur 15000) = eur 1955 ∧ detrDip (eur 15000 + 1) = 309988 := by decide
/-- Art. 13 c. 1 b)-c) meet at 28.000 in the formulas (1.910 both sides), but the four-decimal truncation of
c. 6 makes the ratio (50.000 − 28.000,01)/22.000 = 0,99999… count as 0,9999: the detrazione (with the 65 euro of c. 1.1) drops by 0,19 euro
for one more cent (a rounding notch the statute creates); it reaches 0 at 50.000. -/
theorem detrDip_28000_50000 : detrDip (eur 28000) = eur 1975 ∧ detrDip (eur 28000 + 1) = 197481 ∧
    detrDip (eur 50000) = 0 := by decide

/-! ## DL 3/2020: the trattamento integrativo never exceeds 1.200 -/
theorem ti_le (r rld l d : Int) : trattIntegrativo r rld l d ≤ tiFull := by
  unfold trattIntegrativo
  dsimp only
  split
  · unfold tiFull eur; omega
  · split
    · split <;> (unfold tiFull eur; omega)
    · split
      · split <;> (unfold tiFull eur at *; omega)
      · unfold tiFull eur; omega

/-- Where it starts: imposta lorda on the employment income must exceed 1.955 − 75 = 1.880, i.e. income above
1.880 / 0,23 = 8.173,91 and, with the imposta lorda rounded to the cent, at least 8.173,94: at 8.173,93 nothing,
at 8.173,94 the full 1.200 (and no IRPEF is due below 8.500). -/
theorem ti_starts : trattIntegrativo 817393 817393 (lorda 817393) 0 = 0 ∧
    trattIntegrativo 817394 817394 (lorda 817394) 0 = tiFull := by decide

/-! ## Addizionali: exemption thresholds are notches (kernel `Surcharge.exempt_notch` shape) -/
/-- Roma: 14.000 pays 0, 14.000,01 pays 0,9 % of the whole: 126 euro. -/
theorem roma_notch : roma (eur 14000) = 0 ∧ roma (eur 14000 + 1) = 12600 := by decide
/-- Lazio: 28.000 pays 1,73 % (484,40); 28.000,01 pays 1,73 % to 15.000 and 3,33 % above (692,40) and gets no
60-euro detrazione until 28.001 (the band is "compreso tra 28.001 e 35.000,00"). -/
theorem lazio_notch : lazio (eur 28000) = 48440 ∧ lazio (eur 28000 + 1) = 69240 ∧ lazio (eur 28001) = 63243 := by
  decide

end ITTax
