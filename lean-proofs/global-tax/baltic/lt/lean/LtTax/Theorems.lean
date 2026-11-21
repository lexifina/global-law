import LtTax.Tax

/-!
# Lithuania: kernel theorems instantiated, and the properties the findings rely on (no `sorry`)
-/

namespace LtTax
open TaxKernel

/-! ## Rate schedules (6 str.) -/

theorem emp2025_progressive : y2025.emp.progressive = true := by decide
theorem emp2026_progressive : y2026.emp.progressive = true := by decide
theorem other_progressive : (otherSched 210888).progressive = true := by decide
theorem emp2025_mono : Monotone' y2025.emp.ticks := Schedule.ticks_mono_of_progressive _ emp2025_progressive
theorem emp2025_convex : Convex y2025.emp.ticks := Schedule.ticks_convex _ emp2025_progressive
theorem emp2026_convex : Convex y2026.emp.ticks := Schedule.ticks_convex _ emp2026_progressive
theorem emp2025_no_jump {x y : Int} (h : x ≤ y) : y2025.emp.ticks y - y2025.emp.ticks x ≤ y2025.emp.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ emp2025_progressive h).2
theorem emp2025_le_top {x : Int} (h : 0 ≤ x) : y2025.emp.ticks x ≤ 3200 * x := by
  have := Schedule.ticks_le_maxRate_mul _ emp2025_progressive h
  have e : y2025.emp.maxRate = 3200 := by decide
  rwa [e] at this
/-- Individual taxation: a couple's tax is the sum of two separate schedules; a joint (aggregated) schedule would
cost more (`separate_le_joint`), splitting less: Lithuania has neither. -/
theorem split_would_help (a b : Int) : splitting y2025.emp.ticks a b ≤ separate y2025.emp.ticks a b :=
  splitting_le_separate _ emp2025_convex emp2025_mono a b

/-! ## NPD (20 str.) -/

theorem t1Y_wf : (t1Y y2025).WellFormed := by unfold Taper.WellFormed t1Y y2025; decide
theorem t2Y_wf : t2Y.WellFormed := by unfold Taper.WellFormed t2Y; decide
theorem t1Y23_wf : (t1Y y2023).WellFormed := by unfold Taper.WellFormed t1Y y2023; decide
theorem t1Y26_wf : (t1Y y2026).WellFormed := by unfold Taper.WellFormed t1Y y2026; decide

/-- The statute's three cases (switch at 28 647,48 €) are exactly the larger of the two tapers, for every GMP: the
switch point is where the two formulas meet (to the cent, after rounding). -/
theorem mnpd2025_max (g : Int) : mnpd y2025 g = max ((t1Y y2025).amount g) (t2Y.amount g) := by
  simp only [mnpd, y2025, t1Y, t2Y, Taper.amount, Taper.reduction, divR, pos, if_true]
  (repeat' split) <;> omega

/-- The same for the archived 2023 text (switch at "23 112 eurų per metus"). -/
theorem mnpd2023_max (g : Int) : mnpd y2023 g = max ((t1Y y2023).amount g) (t2Y.amount g) := by
  simp only [mnpd, y2023, t1Y, t2Y, Taper.amount, Taper.reduction, divR, pos, if_true]
  (repeat' split) <;> omega

/-- 2026: one formula only. -/
theorem mnpd2026_single (g : Int) : mnpd y2026 g = (t1Y y2026).amount g := by
  simp only [mnpd, y2026, t1Y, Taper.amount, Taper.reduction, divR, pos, Bool.false_eq_true, if_false]
  (repeat' split) <;> omega

theorem mnpd2025_antitone {x y : Int} (h : x ≤ y) : mnpd y2025 y ≤ mnpd y2025 x := by
  rw [mnpd2025_max, mnpd2025_max]
  have h1 := Taper.amount_antitone _ t1Y_wf h
  have h2 := Taper.amount_antitone _ t2Y_wf h
  omega

theorem mnpd2025_nonneg (g : Int) : 0 ≤ mnpd y2025 g := by
  rw [mnpd2025_max]; have := Taper.floor_le_amount (t1Y y2025) g; have := Taper.floor_le_amount t2Y g
  simp only [t1Y, t2Y] at *; omega

/-- The annual NPD is 0 from 34 370,67 € (cents 3 437 067) in 2022-2025. -/
theorem mnpd2025_zero {g : Int} (h : 3437067 ≤ g) : mnpd y2025 g = 0 := by
  rw [mnpd2025_max]; simp only [t1Y, t2Y, y2025, Taper.amount, Taper.reduction, divR, pos]; omega

/-- In 2026 it is 0 from 32 129,88 € (12 × 1 153 + 8 964 / 0,49): earlier than in 2025. -/
theorem mnpd2026_zero {g : Int} (h : 3212988 ≤ g) : mnpd y2026 g = 0 := by
  rw [mnpd2026_single]; simp only [t1Y, y2026, Taper.amount, Taper.reduction, divR, pos]; omega

theorem mnpd2025_band1 {g : Int} (h1 : 1245600 < g) (h2 : g ≤ 2864748) : mnpd y2025 g = (t1Y y2025).amount g := by
  unfold mnpd; simp only [y2025]; rw [if_neg (by omega), if_pos h2]

theorem mnpd2025_band2 {g : Int} (h1 : 2864748 < g) : mnpd y2025 g = t2Y.amount g := by
  unfold mnpd; simp only [y2025]; rw [if_neg (by omega), if_neg (by omega)]; rfl

/-- **Taper band 1** (`Taper.taper_marginal`): between 12 456 € and 28 647,48 € of annual income, 1 € more wages
costs 20 % × (1 + 0,49) = 29,8 % in GPM (plus 19,5 % contributions: 49,3 %). -/
theorem band1_2025 {inc : Int} (h1 : 1245600 ≤ inc) (h2 : inc + 100 ≤ 2864748) :
    y2025.emp.ticks (taxableAfter ((t1Y y2025).amount (inc + 100)) (inc + 100))
      - y2025.emp.ticks (taxableAfter ((t1Y y2025).amount inc) inc) = 2000 * 149 := by
  have hw := t1Y_wf
  have hin : (t1Y y2025).floor < (t1Y y2025).amount (inc + (t1Y y2025).den) := by
    simp only [t1Y, y2025, Taper.amount, Taper.reduction, divR, pos]; omega
  have hpos : (t1Y y2025).amount inc ≤ inc := by
    have := Taper.amount_le_full _ hw inc; simp only [t1Y, y2025] at this ⊢; omega
  have := Taper.taper_marginal (t1Y y2025) hw y2025.emp 2000 (by simp only [t1Y, y2025]; omega) hin hpos (by
    intro i hi1 hi2
    simp only [t1Y, y2025, Taper.amount, Taper.reduction, divR, taxableAfter, pos] at hi1 hi2
    simp only [Schedule.rate, y2025, empSched2, Schedule.ofList, bandsRate, List.map]
    (repeat' split) <;> omega)
  simpa [t1Y, y2025] using this

/-- **Taper band 2**: between 28 647,48 € and 34 370,67 €, 1 € more costs 20 % × 1,18 = 23,6 % in GPM. -/
theorem band2_2025 {inc : Int} (h1 : 2864748 ≤ inc) (h2 : inc + 100 ≤ 3437000) :
    y2025.emp.ticks (taxableAfter (t2Y.amount (inc + 100)) (inc + 100))
      - y2025.emp.ticks (taxableAfter (t2Y.amount inc) inc) = 2000 * 118 := by
  have hw := t2Y_wf
  have hin : t2Y.floor < t2Y.amount (inc + t2Y.den) := by
    simp only [t2Y, Taper.amount, Taper.reduction, divR, pos]; omega
  have hpos : t2Y.amount inc ≤ inc := by
    have := Taper.amount_le_full _ hw inc; simp only [t2Y] at this ⊢; omega
  have := Taper.taper_marginal t2Y hw y2025.emp 2000 (by simp only [t2Y]; omega) hin hpos (by
    intro i hi1 hi2
    simp only [t2Y, Taper.amount, Taper.reduction, divR, taxableAfter, pos] at hi1 hi2
    simp only [Schedule.rate, y2025, empSched2, Schedule.ofList, bandsRate, List.map]
    (repeat' split) <;> omega)
  simpa [t2Y] using this

/-- **Non-wage income withdraws the NPD on wages** (20 str. 7 d.): for an employee whose GMP is in band 1, 1 € of
dividends, interest, rent or individual-activity income adds 0,49 € of taxable wages, i.e. 9,8 % on top of its own
15 % rate. `w` = wages (cents), `g` = GMP (wages + other income). -/
theorem other_income_withdraws_npd {w g : Int} (h1 : 1245600 ≤ g) (h2 : g + 100 ≤ 2864748) (hw : w ≤ g)
    (ha : (t1Y y2025).amount g ≤ w) :
    y2025.emp.ticks (taxableAfter ((t1Y y2025).amount (g + 100)) w)
      - y2025.emp.ticks (taxableAfter ((t1Y y2025).amount g) w) = 2000 * 49 := by
  simp only [t1Y, y2025, Taper.amount, Taper.reduction, divR, taxableAfter, pos, Schedule.ticks, empSched2,
    Schedule.ofList, List.map, bandsTicks] at ha ⊢
  (repeat' split) <;> omega

/-! ## The 60 VDU point: the 32 % rate starts where the 12,52 % VSD stops -/

/-- GPM + VSD + PSD on wages, in ticks (bp × cents). -/
def combTicks (x : Int) : Int := y2025.emp.ticks x + (vsd y2025).ticks x + psd.ticks x

theorem edge_below {x : Int} (h0 : 0 ≤ x) (h : x + 1 ≤ 60 * 210888) : combTicks (x + 1) - combTicks x = 3950 := by
  simp only [combTicks, y2025, empSched2, vsd, psd, vsdRate, psdRate, Schedule.ticks, Schedule.ofList,
    Schedule.flat, List.map, bandsTicks, Contribution.ticks, Contribution.base, pos]
  (repeat' split) <;> omega

theorem edge_above {x : Int} (h : 60 * 210888 ≤ x) : combTicks (x + 1) - combTicks x = 3898 := by
  simp only [combTicks, y2025, empSched2, vsd, psd, vsdRate, psdRate, Schedule.ticks, Schedule.ofList,
    Schedule.flat, List.map, bandsTicks, Contribution.ticks, Contribution.base, pos]
  (repeat' split) <;> omega

/-- The top statutory rate band has a LOWER combined marginal rate (38,98 %) than the band below it (39,5 %). -/
theorem edge_falls : (3898 : Int) < 3950 := by decide

/-! ## Individual activity (18² str.) -/

theorem ia_5pct : iaTax 2000000 = 100000 := by decide
theorem ia_15pct : iaTax 3500000 = 525000 := by decide
/-- The credit's withdrawal makes the marginal GPM rate on individual-activity income 38,27 % just below 35 000 €. -/
theorem ia_marginal_top : iaTax 3500000 - iaTax 3490000 = 3827 := by decide
/-- The credit is continuous at 20 000 € but falls right above it. -/
theorem ia_credit_continuous : iaCredit 2000000 = 200000 ∧ iaCredit 2000100 = 199997 := by decide

/-! ## Child benefit: the additional benefit's income test is a notch -/

/-- A family of 1 adult and 2 children (3 members): net income of 15 912 € a year (2 × 221 € × 3 × 12) keeps the
additional benefit; one cent more loses 1 730,40 €. -/
theorem cb_notch_2025 :
    (childBenefit y2025 2 3 (12 * 2 * 22100 * 3)).additional
      - (childBenefit y2025 2 3 (12 * 2 * 22100 * 3 + 1)).additional = 173040 := by decide

theorem cb_universal_2025 : (childBenefit y2025 2 3 0).universal = 294000 := by decide

end LtTax

namespace LtTax

/-! ## Worked examples (to the cent)

* VMI written answer RM-5567 of 2024-02-13 (Mokesčių informacijos departamentas; published by an accounting firm,
  `refs/vmi_rm5567_2024_excerpt.txt`): December 2023 pay of 1 700 € and January 2024 pay of 700 €, both paid in
  January, take the January NPD on 2 400 €: "83,56 eurų NPD ... (400 - 0,18 x (2400 – 642))".
* OECD Taxing Wages (`~/cmp20/baltic/oecd/tw_cou_baltic.json`, line STA = the annual NPD): 2025 S67 5 719,55 €,
  S100 1 115,37 €; 2024 S100 1 516,20 €; 2023 S100 1 901,50 € (second formula); 2022 S67 4 630,04 € (ours 4 630,05:
  the reduction is rounded down to the cent, the OECD does not round). -/

theorem vmi_rm5567 : npdMonth y2024 240000 = 8356 := by decide
theorem oecd_2025_S67_npd : mnpd y2025 1907733 = 571955 := by decide
theorem oecd_2025_S100_npd : mnpd y2025 2847362 = 111537 := by decide
theorem oecd_2024_S100_npd : mnpd y2024 2598360 = 151620 := by decide
theorem oecd_2023_S100_npd : mnpd y2023 2380680 = 190150 := by decide
theorem oecd_2022_S67_npd : mnpd y2022 1420105 = 463005 := by decide

/-- The 2024 VMI answer's footnote: the 2 167 € switch is "2024 m. projektuojamo vidutinio darbo užmokesčio suma";
it is also exactly where 747 – 0,5 × (P – 924) meets 400 – 0,18 × (P – 642). -/
theorem switch_2024_meets : (t1M y2024).amount 216700 = t2M.amount 216700 := by decide
theorem switch_2025_meets : (t1M y2025).amount 238729 = t2M.amount 238729 := by decide

end LtTax

namespace LtTax
open TaxKernel

/-- GPM on wages alone (ticks), with the annual NPD. -/
def gpmWage (yp : YP) (w : Int) : Int := yp.emp.ticks (taxableAfter (min (mnpd yp w) w) w)

/-- **Bunching beats smoothing** (FINDINGS F3): the NPD makes GPM on wages concave between 12 456 € and the 60 VDU
point, so 12 000 € + 48 000 € over two years pays 1 478,11 € less than 30 000 € + 30 000 € (ticks = basis points × cents). -/
theorem bunching_2025 : 2 * gpmWage y2025 3000000 - (gpmWage y2025 1200000 + gpmWage y2025 4800000) = 1478112000 := by
  decide

/-- **The reform window** (FINDINGS F7): at 90 000 € of employment income the marginal rate is 20 % in 2025 and
25 % in 2026. -/
theorem reform_rate_90k : y2025.emp.rate 9000000 = 2000 ∧ y2026.emp.rate 9000000 = 2500 := by decide

end LtTax
