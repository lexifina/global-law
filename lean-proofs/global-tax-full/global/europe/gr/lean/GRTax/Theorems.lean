import GRTax.Country

/-! # The kernel's generic theorems instantiated for Greece, and properties the statute claims -/

namespace GRTax
open TaxKernel

/-! ## Art. 15 scale (2020-2025) -/

theorem scale_progressive : scale2020.progressive = true := by decide
theorem scale_mono : Monotone' scale2020.ticks := Schedule.ticks_mono_of_progressive _ scale_progressive
theorem scale_convex : Convex scale2020.ticks := Schedule.ticks_convex _ scale_progressive
theorem scale_no_jump {x y : Int} (h : x ≤ y) : scale2020.ticks y - scale2020.ticks x ≤ scale2020.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ scale_progressive h).2
/-- The average rate never exceeds the 44 % top rate. -/
theorem scale_le_top {x : Int} (h : 0 ≤ x) : scale2020.ticks x ≤ 4400 * x := by
  have := Schedule.ticks_le_maxRate_mul _ scale_progressive h
  have e : scale2020.maxRate = 4400 := by decide
  rwa [e] at this
/-- Spouses are assessed separately (art. 67 par. 4(α)): aggregating a couple's income on one scale would never
cost less (kernel `separate_le_joint`). -/
theorem separate_le_aggregate {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate scale2020.ticks a b ≤ joint scale2020.ticks a b :=
  separate_le_joint _ scale_convex (by decide) ha hb

/-- The 2026 scales (ν. 5246/2025) are still progressive for every number of children up to eight and for the
under-25, 26-30 and older brackets. -/
theorem scale2026_progressive :
    (List.range 9).all (fun k => [20, 28, 40].all fun a => (scale2026 k a).progressive) = true := by decide

/-! ## Art. 40 par. 4: the separate rent scale -/

theorem rent_progressive : rentScale2020.progressive = true := by decide
theorem rent_convex : Convex rentScale2020.ticks := Schedule.ticks_convex _ rent_progressive
/-- Splitting a rent between co-owning spouses never costs more than one spouse holding it all (kernel
`splitting_le_separate` read the other way: separate taxation of halves ≤ one owner). -/
theorem rent_split_le_one_owner {r : Int} (h : 0 ≤ r) :
    rentScale2020.ticks (r - r / 2) + rentScale2020.ticks (r / 2) ≤ rentScale2020.ticks r + rentScale2020.ticks 0 := by
  have := separate_le_joint _ rent_convex (by decide) (show 0 ≤ r - r / 2 by omega) (show 0 ≤ r / 2 by omega)
  have h0 : rentScale2020.ticks 0 = 0 := by decide
  unfold separate joint at this; rw [show r - r / 2 + r / 2 = r by omega] at this; omega

/-! ## Art. 16: the reduction and its taper -/

def taper0 : Taper := { full := eur 777, start := eur 12000, num := 2, den := 100 }
theorem taper0_eq : creditTaper 2025 0 = taper0 := rfl
theorem taper0_wf : taper0.WellFormed := by unfold Taper.WellFormed taper0; decide
theorem credit_le_full (x : Int) : (creditTaper 2025 0).amount x ≤ eur 777 := by
  rw [taper0_eq]; exact Taper.amount_le_full _ taper0_wf x
theorem credit_antitone {x y : Int} (h : x ≤ y) : (creditTaper 2025 0).amount y ≤ (creditTaper 2025 0).amount x := by
  rw [taper0_eq]; exact Taper.amount_antitone _ taper0_wf h

/-- The METR band of art. 16 par. 2: between 12,000 € and 20,000 € of taxable wages (the 22 % band), one more
euro of wages costs 22 % on the scale plus 2 % of lost reduction = 24 % (in ticks: 100 cents × 2,400 bp). -/
theorem taper_band_24 {x : Int} (h1 : eur 12000 ≤ x) (h2 : x + 100 ≤ eur 20000) :
    (scale2020.ticks (x + 100) - BP * (creditTaper 2025 0).amount (x + 100))
      - (scale2020.ticks x - BP * (creditTaper 2025 0).amount x) = 2400 * 100 := by
  have hc : scale2020.ticks (x + (100 : Nat)) - scale2020.ticks x = 2200 * (100 : Nat) := by
    apply Schedule.ticks_const_rate
    intro i hi1 hi2
    simp only [eur] at h1 h2
    simp only [Schedule.rate, scale2020, eur, Schedule.ofList, bandsRate, List.map]
    repeat (first | split | omega)
  have hs : taper0.start ≤ x := by simp only [taper0]; exact h1
  have hin : taper0.floor < taper0.amount (x + taper0.den) := by
    simp only [taper0, Taper.amount, Taper.reduction, divR, pos, eur] at h1 h2 ⊢; omega
  have ha : taper0.amount (x + 100) = taper0.amount x - 2 := Taper.amount_step taper0 taper0_wf hs hin
  rw [taper0_eq]
  simp only [BP]; push_cast at hc; omega

/-- Where the reduction is used up: at 50,850 € of taxable wages without children (12,000 + 777 / 2 %). -/
theorem taper0_end : taper0.amount (eur 50850) = 0 ∧ taper0.amount (eur 50850 - 100) = 2 := by decide

/-- F2 (statute fault): the art. 16 par. 1 list gives 1,780 € for five children, while the unchanged next sentence
("+220 for each child after the fourth") gives 1,580 + 220 = 1,800 €. -/
theorem five_children_conflict : credit2024 5 = eur 1780 ∧ credit2024literal 5 = eur 1800 := by decide

/-- F3: the 2024 reform raised the one-child amount by 90 € (810 → 900) and the four-child amount by 240 € (1,340 →
1,580). -/
theorem credit_2023_vs_2024 :
    (List.range 6).map (fun k => credit2024 k - credit2020 k) = [0, 9000, 22000, 22000, 24000, 22000] := by decide

/-- With five or more children the reduction is not withdrawn at all (art. 16 par. 2, last sentence). -/
theorem five_no_taper (x : Int) : (creditTaper 2025 5).amount x = eur 1780 := by
  simp [creditTaper, Taper.fixed, Taper.amount, Taper.reduction, divR, pos, credit2024, creditFull, eur] <;> omega

/-! ## EFKA -/

/-- Above the ceiling (14 × 7,572.62 €) the employee pays exactly 13.37 % of the ceiling. -/
theorem efka_above_ceiling {x : Int} (h : payments * monthlyCeiling ≤ x) :
    (efka 2025).ticks x = 1337 * (payments * monthlyCeiling) := by
  have := Contribution.ticks_above_ceiling (efka 2025) (by decide) h (by simp [efka, payments, monthlyCeiling] at h ⊢; omega)
  rw [this]; decide

/-! ## Child benefit: a notch -/

/-- F4: a married couple with two children whose income before tax after contributions passes 30,000 € by one
cent (two cents, at the model's cent resolution) loses the whole 672 € a year of child benefit (equivalised 15,000 € at weight 1 + 1/2 + 1/4 + 1/4). -/
theorem benefit_cliff : childBenefit 2 2 (eur 30000) = eur 672 ∧ childBenefit 2 2 (eur 30000 + 2) = 0 := by decide

/-- The lone-parent weight (first child 1/2) moves a lone parent of two to the 10,000 € category limit at
17,500 €, a couple of two at 20,000 €. -/
theorem benefit_category_edges :
    childBenefit 1 2 (eur 17500) = eur 1008 ∧ childBenefit 1 2 (eur 17500 + 2) = eur 672 ∧
    childBenefit 2 2 (eur 20000) = eur 1008 ∧ childBenefit 2 2 (eur 20000 + 2) = eur 672 := by decide

end GRTax
