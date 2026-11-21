import IsTax.Basic

/-!
# Iceland 2025: kernel theorems instantiated, and the country's own properties (no `sorry`)
-/

namespace IsTax
open TaxKernel

/-! ## The three-band state schedule (66. gr. 1. mgr.) -/

theorem state_progressive : stateSched.progressive = true := by decide
theorem state_mono : Monotone' stateSched.ticks := Schedule.ticks_mono_of_progressive _ state_progressive
theorem state_convex : Convex stateSched.ticks := Schedule.ticks_convex _ state_progressive
theorem state_no_jump {x y : Int} (h : x ≤ y) :
    stateSched.ticks y - stateSched.ticks x ≤ stateSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ state_progressive h).2
theorem state_le_top {x : Int} (h : 0 ≤ x) : stateSched.ticks x ≤ 3135 * x := by
  have := Schedule.ticks_le_maxRate_mul _ state_progressive h
  have e : stateSched.maxRate = 3135 := by decide
  rwa [e] at this
theorem state_marginal (x : Int) : stateSched.ticks (x + 1) - stateSched.ticks x = stateSched.rate x :=
  Schedule.ticks_succ stateSched x
theorem state_split_ok (a b : Int) : splitting stateSched.ticks a b ≤ separate stateSched.ticks a b :=
  splitting_le_separate _ state_convex state_mono a b

/-- The withholding schedule (state + average útsvar) is progressive too. -/
theorem withhold_progressive : withholdSched.progressive = true := by decide
/-- State tax plus Reykjavík útsvar: 31,52 / 38,02 / 46,32 %, progressive. -/
def combinedSched : Schedule := Schedule.ofList [(0, 3152), (T1, 3802), (T3, 4632)]
theorem combined_progressive : combinedSched.progressive = true := by decide
theorem combined_top : combinedSched.maxRate = rate3 + utsvarReykjavik := by decide

/-! ## The spouses' band transfer (66. gr. 1. mgr. 4. tölul.) -/

theorem bandShift_nonneg (hi lo : Int) : 0 ≤ bandShift hi lo := by
  unfold bandShift pos bandTransferCap; omega

theorem bandShift_le_cap (hi lo : Int) : bandShift hi lo ≤ bandTransferCap := by
  unfold bandShift; omega

/-- The 2025 cap equals half of the middle band (rounded down): the cap binds exactly when the lower spouse is
below T1, so the transfer is "half of the lower spouse's unused middle band", never any of its first band. -/
theorem cap_is_half_middle : bandTransferCap = (T3 - T1) / 2 := by decide

theorem bandShift_half_middle (hi lo : Int) :
    bandShift hi lo = min (pos (hi - T3)) (pos (T3 - max lo T1) / 2) := by
  unfold bandShift pos bandTransferCap T3 T1; omega

/-- The transfer never raises the higher spouse's tax. -/
theorem shifted_le (hi lo : Int) : stateTaxShifted hi lo ≤ stateTax hi := by
  unfold stateTaxShifted stateTax Schedule.tax
  apply Rule.ofTicks_mono
  all_goals first
    | (have := bandShift_nonneg hi lo; unfold rate3 rate2; omega)
    | (simp [Rule.unitHalfUp, Round.isMonotoneMode])
    | decide

/-- Joint taxation of the bands never costs a couple anything. -/
theorem pair_le_separate (a b : Int) :
    (stateTaxPair true a b).1 + (stateTaxPair true a b).2 ≤ stateTax a + stateTax b := by
  unfold stateTaxPair
  simp only [Bool.not_true, Bool.false_eq_true, ↓reduceIte]
  split
  · have := shifted_le a b; simp only; omega
  · have := shifted_le b a; simp only; omega

/-- The largest gain from the transfer: 8,30 % of 5.118.730 kr. = 424.854,59 kr. (ticks: kr × bp). -/
theorem max_transfer_gain_ticks : (rate3 - rate2) * bandTransferCap = 4248545900 := by decide

/-- Example: one spouse 30 M kr., the other nothing: the shift is the cap. -/
theorem shift_one_earner : bandShift 30000000 0 = 5118730 := by decide

/-! ## The personal credit (67. gr. A) -/

/-- Nothing is created or lost in the ordering: used against state tax + used against útsvar + left = credit. -/
theorem useCredit_conserves (c st ut : Int) :
    (useCredit c st ut).state + (useCredit c st ut).utsvar + (useCredit c st ut).left = pos c := by
  unfold useCredit usedCredit pos; simp only; omega

/-- The credit is non-refundable: it never takes the state tax or the útsvar below zero. -/
theorem useCredit_le (c st ut : Int) :
    (useCredit c st ut).state ≤ pos st ∧ (useCredit c st ut).utsvar ≤ pos ut := by
  unfold useCredit usedCredit pos; simp only; omega

/-- The transfer between spouses never reduces the credit a couple can use against tax on earned income. -/
theorem transfer_never_costs (cA cB stA stB utA utB : Int) :
    let n := coupleCredits false cA cB stA stB utA utB
    let t := coupleCredits true cA cB stA stB utA utB
    n.1.state + n.1.utsvar + n.2.1.state + n.2.1.utsvar ≤ t.1.state + t.1.utsvar + t.2.1.state + t.2.1.utsvar := by
  simp only [coupleCredits, useCredit, usedCredit, pos, Bool.not_false, Bool.not_true, Bool.false_eq_true,
    ↓reduceIte]
  omega

/-- A one-earner couple uses the whole second credit (100 % transferable in 2025): at the OECD average wage the
second credit (824.288 kr.) is used in full against the earner's state tax. -/
theorem one_earner_full_transfer :
    let t := coupleCredits true persCredit persCredit (stateTax 11936186) 0 (utsvarOf utsvarReykjavik 11936186) 0
    t.1.state = 2 * persCredit ∧ t.2.2 = 0 := by decide

/-- Withholding gives 12 × 68.691 = 824.292 kr. of credit, 4 kr. more than the year's 824.288 (F6). -/
theorem withholding_credit_excess : 12 * persCreditMonth - persCredit = 4 := by decide
/-- The monthly first band (12 × 472.005 = 5.664.060) is 2 kr. short of the annual one (F6). -/
theorem withholding_band_gap : T1 - 12 * wM1 = 2 := by decide

/-- 67. gr. A, 22/31 rule: a person with no earned income and only capital income pays no capital income tax on up
to 300.000 + 2.658.990 kr.: 22 % of 2.658.990 = 584.977,8 ≤ 22/31 of 824.288 = 584.978,8 (F10). -/
theorem capital_free_single :
    capTaxOf (capBase { interest := 2958990 } capExemption) ≤ capCredit persCredit (capTaxOf (capBase { interest := 2958990 } capExemption)) := by
  decide

/-! ## The levies (lög 23/2013, 14. gr.; lög 125/1999, 10. gr.): a notch at the floor -/

theorem levy_notch (amt floor : Int) (age : Nat) (h1 : 16 ≤ age) (h2 : age ≤ 69) :
    levyDue amt floor age floor - levyDue amt floor age (floor - 1) = amt := by
  unfold levyDue
  have h3 : ¬ (floor ≤ floor - 1) := by omega
  simp [h1, h2, h3]

/-- One more króna of tekjustofn at 2.617.618 kr. costs 22.200 + 14.614 = 36.814 kr. of levies (F3). -/
theorem levies_cliff_2025 :
    (levyDue levies2025.utvarp levies2025.floor 40 2617618 + levyDue levies2025.aldradra levies2025.floor 40 2617618)
    - (levyDue levies2025.utvarp levies2025.floor 40 2617617 + levyDue levies2025.aldradra levies2025.floor 40 2617617)
    = 36814 := by decide

/-- The floor is the point where income tax starts at the withholding rate: 31,49 % of 2.617.618 ≈ 824.288 (F3). -/
theorem levy_floor_is_taxfree_point : persCredit * BP / 3149 = levies2025.floor := by decide

/-! ## Barnabætur (68. gr. A, brbákv. LXXXII) -/

/-- The base part is the kernel's `Taper` (full amount, start, 4/100, floor 0, reduction rounded half up). -/
def bbTaper (couple : Bool) (n : Nat) : Taper :=
  { full := (if couple then bbCouple else bbSingle) * n, start := if couple then bbStartCouple else bbStartSingle,
    num := 4, den := 100, round := .halfUp }

theorem bb_base_is_taper (couple : Bool) (n : Nat) (inc : Int) :
    pos ((if couple then bbCouple else bbSingle) * n - bbReduce (inc - (if couple then bbStartCouple else bbStartSingle)))
      = (bbTaper couple n).amount inc := by
  unfold bbTaper Taper.amount Taper.reduction bbReduce divR pos bbPct
  cases couple <;> simp <;> omega

/-- Withdrawal never raises the benefit. (The kernel's `Taper.amount_antitone` needs `round = .down`; RSK rounds the
reduction half up, so this is proved directly: kernel gap.) -/
theorem bb_base_antitone (couple : Bool) (n : Nat) {x y : Int} (h : x ≤ y) :
    (bbTaper couple n).amount y ≤ (bbTaper couple n).amount x := by
  unfold bbTaper Taper.amount Taper.reduction divR pos
  cases couple <;> simp <;> omega

/-- Stacked withdrawal: a single parent with three children under 7 inside the band loses 4 + 3 × 4 = 16 % of each
extra króna (4 kr. per 25 kr.), on top of 38,02 % tax: a 54,02 % marginal rate (F4). -/
theorem bb_single_three_under7 {x : Int} (h1 : 5844000 ≤ x) (h2 : x + 25 ≤ 9094000) :
    bbGross false 3 3 (x + 25) = bbGross false 3 3 x - 4 := by
  unfold bbGross bbReduce bbReduce7 divR pos bbStartSingle bbSingle bbUnder7 bbPct
  have e1 : max 0 (x + 25 - 5844000) = x + 25 - 5844000 := by omega
  have e2 : max 0 (x - 5844000) = x - 5844000 := by omega
  have hc : (2 * (4 * (x + 25 - 5844000)) + 100) / 200 = (2 * (4 * (x - 5844000)) + 100) / 200 + 1 := by
    have : 2 * (4 * (x + 25 - 5844000)) + 100 = (2 * (4 * (x - 5844000)) + 100) + 1 * 200 := by omega
    rw [this, Int.add_mul_ediv_right _ _ (by decide)]
  have hb : (2 * (12 * (x + 25 - 5844000)) + 100) / 200 = (2 * (12 * (x - 5844000)) + 100) / 200 + 3 := by
    have : 2 * (12 * (x + 25 - 5844000)) + 100 = (2 * (12 * (x - 5844000)) + 100) + 3 * 200 := by omega
    rw [this, Int.add_mul_ediv_right _ _ (by decide)]
  simp [e1, e2]
  omega

/-- A couple with two children, one under 7, inside both withdrawal bands: 8 kr. per 100 kr. (4 % + 4 %). -/
theorem bb_couple_two_one {x : Int} (h1 : 11688000 ≤ x) (h2 : x + 100 ≤ 14938000) :
    bbGross true 2 1 (x + 100) = bbGross true 2 1 x - 8 := by
  unfold bbGross bbReduce bbReduce7 divR pos bbStartCouple bbCouple bbUnder7 bbPct
  have e1 : max 0 (x + 100 - 11688000) = x + 100 - 11688000 := by omega
  have e2 : max 0 (x - 11688000) = x - 11688000 := by omega
  have hc : (2 * (4 * (x + 100 - 11688000)) + 100) / 200 = (2 * (4 * (x - 11688000)) + 100) / 200 + 4 := by
    have : 2 * (4 * (x + 100 - 11688000)) + 100 = (2 * (4 * (x - 11688000)) + 100) + 4 * 200 := by omega
    rw [this, Int.add_mul_ediv_right _ _ (by decide)]
  simp [e1, e2]
  omega

/-- The 5.000 kr. per-carer rule is a notch: a single parent of one child gets 5.000 kr. at 18.581.500 kr. and
nothing 25 kr. later (F8). -/
theorem bb_min_notch : barnabaetur false 1 0 18581500 = 5000 ∧ barnabaetur false 1 0 18581525 = 0 := by decide

/-- For a couple each half lapses on its own: 10.000 kr., then 5.000 kr. 25 kr. later (the odd króna goes to the
first half in this model), then nothing 25 kr. after that. -/
theorem bb_min_notch_couple : barnabaetur true 1 0 20063000 = 10000 ∧ barnabaetur true 1 0 20063025 = 5000 ∧
    barnabaetur true 1 0 20063050 = 0 := by
  decide

/-! ## Owner-manager arithmetic (company.json) -/

/-- A króna of company profit paid as a dividend from an ehf.: 20 % corporate tax (71. gr. 1. mgr.), then 22 % on
the dividend with no exemption (unlisted): 37,6 % in all, exactly the rate 71. gr. 2. mgr. sets for partnerships. -/
theorem dividend_route_rate : 10000 - (10000 - 2000) * (10000 - capRate) / 10000 = 3760 := by decide

/-! ## Findings stated in Lean -/

/-- F2: 67. gr. A 2. mgr. still tests the credit against the tax "skv. 1. tölul. 1. mgr. 66. gr.", i.e. (since
L. 128/2009) the first band only. In 2025 a full first band already costs more than the credit, so the stale reference
changes nothing for anyone: 16,55 % of 5.664.062 = 937.403 > 824.288. -/
theorem firstBandTax_gt_credit : stateTax T1 > persCredit := by decide

/-- F11: the second earner's penalty inside the band transfer. When the higher spouse is far enough above T3, every
2 kr. the lower spouse earns between T1 and T3 removes 1 kr. of transfer (worth 8,30 %): 4,15 % on top of 38,02 %. -/
theorem shift_secondary {hi lo : Int} (h1 : T1 ≤ lo) (h2 : lo + 2 ≤ T3) (h3 : T3 + bandTransferCap ≤ hi) :
    bandShift hi (lo + 2) = bandShift hi lo - 1 := by
  unfold bandShift pos T1 T3 bandTransferCap at *; omega

/-- F12: two parents who each earn 6.000.000 kr. (taxable 5.760.000) with two children (one under 7): as a couple
690.000 + 130.000 = 820.000 kr. of barnabætur; living apart with a shared-residence agreement each gets half of a
single parent's amount, 2 × 579.500 = 1.159.000 kr.: 339.000 kr. a year more. -/
theorem shared_residence_bonus :
    2 * divR .halfUp (bbGross false 2 1 5760000) 2 - barnabaetur true 2 1 11520000 = 339000 := by decide

end IsTax
