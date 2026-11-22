import SkTax.Theorems

/-!
# The findings, as Lean statements (see `FINDINGS.md`)

Each statement is checked by the kernel (`decide` / `omega`); amounts in cents.
-/

namespace SkTax
open TaxKernel

/-- **F5 (bonus claimant)**: a couple with two children under 15, § 5 bases 51 960 € (gross 60 000 €) and 10 392 €
(gross 12 000 €). Claimed by the higher earner the § 33 ods. 11 reduction wipes the bonus out; claimed by the lower
earner it is paid in full (her base carries the 36 % cap: 36 % × 10 392 € > 2 400 €), and no reduction applies. -/
theorem f5_claimant : claimBonus [kidU15, kidU15] 5196000 1039200 = 0 ∧
    claimBonus [kidU15, kidU15] 1039200 5196000 = 240000 := by decide

/-- F5, generally: a claimant whose own base is at most 25 740 € loses nothing to § 33 ods. 11, whatever the other
parent earns (no pooling needed when the own base carries the cap). -/
theorem f5_no_taper_below (b : Int) (h : b ≤ 2574000) : kidU15.reduction b = 0 := by
  rw [kid_reduction_eq]; unfold pos; omega

/-- **F6 (METR above 100 %)**: in the band 25 740 €–37 740 € of base (inside the § 11 band), 40 cents more base
cost `4 n` cents of bonus and 50 cents more taxable base at 19 % (9,5 cents): with 8 children under 15 that is
41,5 cents per 40 cents of base (103,75 % of the base; 103,3 % of gross after the 13,4 % contributions). -/
theorem f6_eight_children (b : Int) (h1 : 2574000 ≤ b) (h2 : b + 40 ≤ 3774000) :
    taperedBonus (List.replicate 8 kidU15) b - taperedBonus (List.replicate 8 kidU15) (b + 40) = 32 := by
  have s1 := bonus_taper_step 8 b h1 (by omega)
  have s2 := bonus_taper_step 8 (b + 10) (by omega) (by omega)
  have s3 := bonus_taper_step 8 (b + 20) (by omega) (by omega)
  have s4 := bonus_taper_step 8 (b + 30) (by omega) (by omega)
  rw [show b + 10 + 10 = b + 20 by omega] at s2
  rw [show b + 20 + 10 = b + 30 by omega] at s3
  rw [show b + 30 + 10 = b + 40 by omega] at s4
  omega

/-- **F8 (the 100 000 € notch of § 15 písm. a) bod 2)**: one cent of business receipts above 100 000 € moves the
whole § 6 base from 15 % to 19 %: on a base `b` up to 48 441,43 € the tax jumps by 4 % of `b` (± a cent). -/
theorem f8_notch (b : Int) (h0 : 0 ≤ b) (h1 : b ≤ 4844143) :
    4 * b - 100 ≤ 100 * (taxBiz b 10000001 - taxBiz b 10000000) ∧
      100 * (taxBiz b 10000001 - taxBiz b 10000000) ≤ 4 * b + 100 := by
  unfold taxBiz
  rw [if_neg (show ¬ (10000001 ≤ smallBizLimit) by decide), if_pos (show (10000000 ≤ smallBizLimit) by decide)]
  simp only [taxSched, pctH, rh, divR, rate15, sched_ticks_eq, pos, Int.reduceMul]
  omega

/-- **F9 (the 8 580 € social-insurance notch, ZSP § 21 ods. 1)**: an SZČO with receipts of 8 580 € pays no social
contributions; with 8 580,01 € it pays the minimum, 12 × 237,02 € = 2 844,24 € (steady state). -/
theorem f9_notch : seSocialYear 858000 858000 0 = 0 ∧ seSocialYear 858001 858001 0 = 284424 := by decide

/-- **F3 (the § 33 ods. 8 / 11 gap of the 1. 1. 2025 text)**: two children under 15, the claimant's own base 3 000 €
and the other parent's 40 000 €. With the text in force on 1. 1. 2025 (ods. 8 pools the bases "na účely ... odsekov 1 a 6"
only, ods. 11 reduces on the claimant's own base) the bonus is 2 400 €; with the amendment in force from 15. 3. 2025 and
applied to the whole 2025 return by § 52zzzd (ods. 11 also on the "navýšený základ dane") it is 1 080 € (36 % of
3 000 €, pooling no longer pays), and the other parent alone would get nothing. -/
theorem f3_gap : claimBonus [kidU15, kidU15] 300000 4000000 false = 240000 ∧
    claimBonus [kidU15, kidU15] 300000 4000000 true = 108000 ∧ claimBonus [kidU15, kidU15] 4000000 300000 true = 0 := by
  decide

end SkTax
