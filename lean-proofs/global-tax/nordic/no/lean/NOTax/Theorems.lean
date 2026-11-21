import NOTax.Household
import TaxKernel.Theorems

/-!
# NOTax.Theorems: the kernel's generic theorems for Norway, and what the Norwegian statute claims

All for every input (no `sorry`). Concrete facts about the 2025 schedules are checked by `decide`.
-/

namespace NOTax
open TaxKernel

/-! ## 1. Trinnskatt (SV 2025 § 3-1): the kernel's Schedule theorems -/

theorem trinn_progressive : trinnskatt.progressive = true := by decide

/-- More personinntekt never lowers the trinnskatt. -/
theorem trinn_mono : Monotone' trinnskatt.ticks := Schedule.ticks_mono_of_progressive trinnskatt trinn_progressive

/-- The marginal trinnskatt on the krone `(x, x+1]` is exactly the rate of its band. -/
theorem trinn_marginal (x : Int) : trinnskatt.ticks (x + 1) - trinnskatt.ticks x = trinnskatt.rate x :=
  Schedule.ticks_succ trinnskatt x

theorem trinn_maxRate : trinnskatt.maxRate = 1770 := by decide

/-- No jump: the trinnskatt rises by at most 17.7 % of any rise in income. -/
theorem trinn_no_jump {x y : Int} (h : x ≤ y) :
    0 ≤ trinnskatt.ticks y - trinnskatt.ticks x ∧ trinnskatt.ticks y - trinnskatt.ticks x ≤ 1770 * (y - x) := by
  have := Schedule.ticks_lipschitz_of_progressive trinnskatt trinn_progressive h
  rw [trinn_maxRate] at this; exact this

/-- The trinnskatt is never more than 17.7 % of personinntekt. -/
theorem trinn_le_top {x : Int} (hx : 0 ≤ x) : trinnskatt.ticks x ≤ 1770 * x := by
  have := Schedule.ticks_le_maxRate_mul trinnskatt trinn_progressive hx
  rw [trinn_maxRate] at this; exact this

theorem trinn_convex : Convex trinnskatt.ticks := Schedule.ticks_convex trinnskatt trinn_progressive

/-- Individual taxation (sktl. § 2-11) of the trinnskatt never costs a couple more than one schedule applied to
their joint personinntekt would (kernel `separate_le_joint`). -/
theorem trinn_separate_le_joint {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate trinnskatt.ticks a b ≤ joint trinnskatt.ticks a b :=
  separate_le_joint _ trinn_convex (by decide) ha hb

/-- The 2025 rates in the five trinn: 1.7, 4.0, 13.7, 16.7, 17.7 %. -/
theorem trinn_rates : trinnskatt.rate 217399 = 0 ∧ trinnskatt.rate 217400 = 170 ∧ trinnskatt.rate 306050 = 400 ∧
    trinnskatt.rate 697150 = 1370 ∧ trinnskatt.rate 942400 = 1670 ∧ trinnskatt.rate 1410750 = 1770 := by decide

/-- The pension-credit taper is NOT a progressive schedule (16.7 % then 6 %): the kernel's `progressive` test
fails, so the credit's withdrawal rate FALLS at 422 950 (a finding about the shape, not an error). -/
theorem pensionTaper_not_progressive : pensionCreditTaper.progressive = false := by decide

/-! ## 2. Trygdeavgift (ftrl. § 23-3): the phase-in cap the statute claims -/

/-- "Avgiften må ikke utgjøre mer enn 25 prosent av den del av inntekten som overstiger 99 650 kroner", for every
person and every mix of wages, pensions and business income. -/
theorem ta_le_cap (p : PersonIn) : taTicks p ≤ taCapRate * pos (personinntekt p - taFloor) := by
  unfold taTicks taCapTicks
  split
  · exact Int.mul_nonneg (by decide) (pos_nonneg _)
  · exact Int.min_le_right _ _

/-- "Det skal ikke betales avgift når inntekten er inntil 99 650 kroner." -/
theorem ta_zero_below (p : PersonIn) (h : personinntekt p ≤ taFloor) : taTicks p = 0 := by
  unfold taTicks; rw [if_pos h]

/-- The trygdeavgift never exceeds the plain rates. -/
theorem ta_le_rates (p : PersonIn) (h : 0 ≤ taRateTicks p) : taTicks p ≤ taRateTicks p := by
  unfold taTicks; split
  · exact h
  · exact Int.min_le_left _ _

/-- No notch at the floor: one krone above it costs at most 25 øre of trygdeavgift (in ticks). -/
theorem ta_no_notch (p : PersonIn) (h : personinntekt p = taFloor + 1) : taTicks p ≤ 2500 := by
  have := ta_le_cap p; rw [h] at this; unfold pos taCapRate taFloor at this
  have e : max 0 (99650 + 1 - 99650 : Int) = 1 := by decide
  rw [e] at this; omega

/-- An ordinary employee aged 17-69 with wages only. -/
def wageEarner (w : Int) : PersonIn := { wages := w }

theorem pi_wageEarner {w : Int} (hw : 0 ≤ w) : personinntekt (wageEarner w) = w := by
  simp [personinntekt, wageEarner, pos]; omega

theorem taRate_wageEarner {w : Int} (hw : 0 ≤ w) : taRateTicks (wageEarner w) = 770 * w := by
  simp [taRateTicks, wageEarner, lowRateAge, pos, taMid, taLow, taHigh]; omega

/-- In the phase-in band (99 650, 144 002] the employee's trygdeavgift is 25 % of the excess: its marginal rate is
25 %, not 7.7 %. -/
theorem ta_phase_in {w : Int} (h1 : taFloor < w) (h2 : w ≤ 144002) :
    taTicks (wageEarner w) = 2500 * (w - taFloor) := by
  have hw : 0 ≤ w := by unfold taFloor at h1; omega
  unfold taTicks
  rw [pi_wageEarner hw, taRate_wageEarner hw]
  unfold taCapTicks taCapRate pos taFloor at *
  have hn : ¬ (w ≤ 99650) := by omega
  simp only [hn, ite_false]
  omega

/-- From 144 003 kroner the plain 7.7 % applies (the trekkrutine's `HOY_GRENSE_TRYGDEAVGIFT` = 144 003). -/
theorem ta_full_rate {w : Int} (h : 144003 ≤ w) : taTicks (wageEarner w) = 770 * w := by
  have hw : 0 ≤ w := by omega
  unfold taTicks
  rw [pi_wageEarner hw, taRate_wageEarner hw]
  unfold taCapTicks taCapRate pos taFloor
  have hn : ¬ (w ≤ 99650) := by omega
  simp only [hn, ite_false]
  omega

/-- The phase-in marginal rate: each extra krone in the band costs 25 øre of trygdeavgift. -/
theorem ta_phase_in_marginal {w : Int} (h1 : taFloor < w) (h2 : w + 1 ≤ 144002) :
    taTicks (wageEarner (w + 1)) - taTicks (wageEarner w) = 2500 := by
  rw [ta_phase_in (by omega) h2, ta_phase_in h1 (by omega)]; omega

/-! ## 3. Minstefradrag (sktl. § 6-32) -/

theorem minst_le_max (w p : Int) : minstefradrag w p ≤ minstWageMax := Int.min_le_left _ _

theorem minst_nonneg (w p : Int) : 0 ≤ minstefradrag w p := by
  unfold minstefradrag cappedDeduction minstWageMax minstWageRate minstPensionMax minstPensionRate pos BP
  simp only [show ¬ ((92000 : Int) < 0) by decide, show ¬ ((73150 : Int) < 0) by decide, ite_false]
  omega

/-- The wage deduction never exceeds the wage (46 % < 100 %). -/
theorem minst_le_wage {w : Int} (hw : 0 ≤ w) : minstefradrag w 0 ≤ w := by
  unfold minstefradrag cappedDeduction minstWageMax minstWageRate minstPensionMax minstPensionRate pos BP
  simp only [show ¬ ((92000 : Int) < 0) by decide, show ¬ ((73150 : Int) < 0) by decide, ite_false]
  omega

/-- Wage less minstefradrag never falls when the wage rises (the deduction grows at 46 % at most). -/
theorem wage_net_mono {w w' : Int} (h : w ≤ w') : w - minstefradrag w 0 ≤ w' - minstefradrag w' 0 := by
  unfold minstefradrag cappedDeduction minstWageMax minstWageRate minstPensionMax minstPensionRate pos BP
  simp only [show ¬ ((92000 : Int) < 0) by decide, show ¬ ((73150 : Int) < 0) by decide, ite_false]
  omega

/-- The cap binds from 200 000 kroner of wages (46 % × 200 000 = 92 000). -/
theorem minst_cap_from (w : Int) (h : 200000 ≤ w) : minstefradrag w 0 = 92000 := by
  unfold minstefradrag cappedDeduction minstWageMax minstWageRate minstPensionMax minstPensionRate pos BP
  simp only [show ¬ ((92000 : Int) < 0) by decide, show ¬ ((73150 : Int) < 0) by decide, ite_false]
  omega

/-! ## 4. The withholding tables (Skatteetaten trekkrutine 2025) against the statute -/

/-- The trekkrutine's minstefradrag (`Fradrag.beregnMinstefradragVanlig`): `Math.round(Y * 40.48 / 100)`, at most
80 960 (= 88 % of the statutory rate and cap). -/
def tableMinst (y : Int) : Int := min 80960 ((2 * 4048 * y + 10000) / 20000)

/-- From 28 kroner of annual income the table's minstefradrag is never larger than the statute's. -/
theorem table_minst_le {y : Int} (h : 28 ≤ y) : tableMinst y ≤ minstefradrag y 0 := by
  unfold tableMinst minstefradrag cappedDeduction minstWageMax minstWageRate minstPensionMax minstPensionRate pos BP
  simp only [show ¬ ((92000 : Int) < 0) by decide, show ¬ ((73150 : Int) < 0) by decide, ite_false]
  omega

/-- From 200 000 kroner it is 11 040 kroner smaller: the table taxes 11 040 kroner too much alminnelig inntekt,
22 % of which (2 428.80 kroner a year) is over-withheld from every such employee. -/
theorem table_minst_gap {y : Int} (h : 200000 ≤ y) : minstefradrag y 0 - tableMinst y = 11040 := by
  rw [minst_cap_from y h]; unfold tableMinst; omega

/-- The over-withholding in ticks of the 22 % taxes: 2200 bp × 11 040 kroner = 2 428.80 kroner. -/
theorem table_overwithholding : 2200 * 11040 = 24288000 := by decide

/-! ## 5. Couples: individual taxation and capital income -/

/-- The flat 22 % on alminnelig inntekt makes moving capital income `x` from one spouse to the other neutral (in
ticks) as long as both stay above the personfradrag: the only gains from splitting capital income are an unused
personfradrag and the rounding of each tax. -/
theorem capital_shift_neutral (a b x r : Int) (ha : personfradrag ≤ a - x) (hb : personfradrag ≤ b) (hx : 0 ≤ x) :
    r * taxableAfter personfradrag (a - x) + r * taxableAfter personfradrag (b + x)
      = r * taxableAfter personfradrag a + r * taxableAfter personfradrag b := by
  unfold taxableAfter pos personfradrag at *
  have e1 : max 0 (a - x - 108550) = a - x - 108550 := by omega
  have e2 : max 0 (b + x - 108550) = b + x - 108550 := by omega
  have e3 : max 0 (a - 108550) = a - 108550 := by omega
  have e4 : max 0 (b - 108550) = b - 108550 := by omega
  rw [e1, e2, e3, e4, ← Int.mul_add, ← Int.mul_add]
  congr 1; omega

/-! ## 6. Owner-manager: wages against dividends at the top rates (SE satser 2025 maximum marginal rates) -/

/-- Dividend route per 10 000 of company profit, in bp × bp: corporate 22 %, then 22 % × 1.72 = 37.84 % on the 78 %
paid out: 51.5152 %. -/
theorem dividend_route : 2200 * 10000 + 7800 * 3784 = 51515200 := by decide

/-- Wage route at the top: the employer's contribution 14.1 % plus 47.4 % personal tax on wages costing 1.141 per
krone: (1410 + 4740) / 11410 = 53.90 %, above the dividend route's 51.52 %. -/
theorem wage_route_top : (1410 + 4740) * 10000 * 10000 > 51515200 * 11410 := by decide

/-- In trinn 3 (43.4 % on wages: 22 + 13.7 + 7.7) the wage route costs (1410 + 4340)/11410 = 50.39 %, BELOW the
dividend route: wages are cheaper up to the trinn 4 threshold (942 400), dividends above it. -/
theorem wage_route_trinn3 : (1410 + 4340) * 10000 * 10000 < 51515200 * 11410 := by decide
theorem wage_route_trinn4 : (1410 + 4640) * 10000 * 10000 > 51515200 * 11410 := by decide

/-! ## 7. New: the sole trader's 47 % band (trygdeavgift phase-in stacked on the 22 % tax) -/

/-- A sole trader (enkeltpersonforetak) with business income only. -/
def soleTrader (s : Int) : PersonIn := { business := s }

theorem grunnlag_soleTrader (s : Int) : grunnlag (soleTrader s) = pos (s - 108550) := by
  simp [grunnlag, alminnelig, alminneligBeforeOpp, oppTillegg, dividendNet, oppjuster, minstefradrag,
    ipsDeduction, giftDeduction, cappedDeduction, soleTrader, taxableAfter, personfradrag, pos, oppNum, oppDen,
    minstWageMax, minstWageRate, minstPensionMax, minstPensionRate, giftMin, ipsMax, BP]
  omega

theorem ta_soleTrader {s : Int} (h1 : 99650 < s) (h2 : s ≤ 176684) :
    taTicks (soleTrader s) = 2500 * (s - 99650) := by
  have hpi : personinntekt (soleTrader s) = s := by simp [personinntekt, soleTrader, pos]; omega
  have hr : taRateTicks (soleTrader s) = 1090 * s := by
    simp [taRateTicks, soleTrader, lowRateAge, pos, taMid, taLow, taHigh]; omega
  unfold taTicks; rw [hpi, hr]; unfold taCapTicks taCapRate taFloor pos
  have hn : ¬ (s ≤ 99650) := by omega
  simp only [hn, ite_false]; omega

/-- Between the personfradrag (108 550) and 176 684 kroner, each extra krone of a sole trader's profit costs
47 øre (in ticks: 2500 trygdeavgift + 2200 tax on alminnelig inntekt), more than the 46.5 % (22 + 13.7 + 10.9)
he pays in trinn 3 and 3.4 points more than an employee's highest rate below 942 400. -/
theorem soleTrader_band {s : Int} (h1 : 108550 ≤ s) (h2 : s + 1 ≤ 176684) :
    (taTicks (soleTrader (s + 1)) + 2200 * grunnlag (soleTrader (s + 1)))
      - (taTicks (soleTrader s) + 2200 * grunnlag (soleTrader s)) = 4700 := by
  rw [ta_soleTrader (by omega) h2, ta_soleTrader (by omega) (by omega), grunnlag_soleTrader, grunnlag_soleTrader]
  unfold pos; omega

/-- Holding company (fritaksmetoden, sktl. § 2-38 (6): 3 % of the dividend is taxed): 22 % × 3 % = 0.66 % on
dividends passed to a holding company, against 37.84 % (22 % × 1.72) on a personal dividend. -/
theorem holding_vs_personal : 2200 * 300 < 2200 * 17200 / 100 * 100 ∧ 2200 * 300 = 660000 := by decide

end NOTax
