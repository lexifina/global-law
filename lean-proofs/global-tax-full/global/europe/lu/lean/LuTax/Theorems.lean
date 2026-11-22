import LuTax.Basic

/-!
# Luxembourg 2025: proofs

Kernel one-liners (API §5) for the tarif (art. 118), the derived class-1a schedule (art. 120bis), splitting (art. 121),
the fonds pour l'emploi majoration (loi 1976 art. 6); country statements: the class-1a schedule equals the statute's
own formula; the 1a advantage is a constant above 54 090; the cote nil-rule notch (art. 124 (2)); the CIS / CIM / CISSM
edges; the marriage penalty of class 1a (unmarried parents) against class 2. No `sorry`.
-/

set_option maxRecDepth 20000

namespace LuTax
open TaxKernel

/-! ## Tarif (art. 118) -/
theorem tarif_progressive : tarif.progressive = true := by decide
theorem tarif_mono : Monotone' tarif.ticks := Schedule.ticks_mono_of_progressive _ tarif_progressive
theorem tarif_convex : Convex tarif.ticks := Schedule.ticks_convex _ tarif_progressive
theorem tarif_no_jump {x y : Int} (h : x ≤ y) : tarif.ticks y - tarif.ticks x ≤ tarif.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ tarif_progressive h).2
theorem tarif_maxRate : tarif.maxRate = 4200 := by decide
theorem tarif_le_top {x : Int} (h : 0 ≤ x) : tarif.ticks x ≤ 4200 * x := by
  have := Schedule.ticks_le_maxRate_mul _ tarif_progressive h
  rwa [tarif_maxRate] at this
theorem tarif_zero : tarif.ticks 0 = 0 := by decide
/-- The marginal rate on each euro is the band's (kernel `Schedule.ticks_succ`). -/
theorem tarif_marginal (x : Int) : tarif.ticks (x + 1) - tarif.ticks x = tarif.rate x := Schedule.ticks_succ _ _

/-! ## Class 2 = splitting (art. 121): never more than two class-1 returns on the same split -/
theorem split_ok (a b : Int) : splitting tarif.ticks a b ≤ separate tarif.ticks a b :=
  splitting_le_separate _ tarif_convex tarif_mono a b
theorem split_equal (a : Int) : splitting tarif.ticks a a = separate tarif.ticks a a :=
  splitting_eq_of_equal _ a
/-- Aggregation without splitting (one class-1 return on the couple's income) would be a marriage penalty. -/
theorem joint_ge_separate (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate tarif.ticks a b ≤ joint tarif.ticks a b :=
  separate_le_joint _ tarif_convex tarif_zero ha hb

/-! ## Class 1a (art. 120bis) -/
theorem tarif1a_progressive : tarif1a.progressive = true := by decide
theorem tarif1a_mono : Monotone' tarif1a.ticks := Schedule.ticks_mono_of_progressive _ tarif1a_progressive
theorem tarif1a_convex : Convex tarif1a.ticks := Schedule.ticks_convex _ tarif1a_progressive
theorem tarif1a_maxRate : tarif1a.maxRate = 4200 := by decide

/-- The derived schedule equals the statute's formula "revenu imposable ajusté réduit d'un quart de son complément à
79 380 euros" (in quarter-euro ticks) at every threshold of either schedule below the cap (both are affine between
consecutive thresholds, so this fixes them on [0, 51 804]); the full check at every multiple of 50 against the ACD's
official formulas is in `results/validate.json` (24 003 / 24 003 exact). -/
theorem c1a_eq_formula_points :
    [0, 15876, 26460, 28224, 29988, 31752, 33516, 35280, 37116, 38952, 40788, 42624, 44460, 46296, 48132, 49968,
      51804].all (fun x => 4 * tarif1a.ticks x == c1aFormulaQ x) = true := by decide

/-- Above the cap the class-1a tax is the class-1 tax less a constant 2 321,46 euros (ticks 23 214 600): the 1a
advantage does not fade out at high incomes. Shown at the band edges above 54 090 and far out. -/
theorem c1a_advantage_const :
    [54090, 60000, 117450, 150000, 176160, 234870, 300000, 1000000].all
      (fun x => tarif.ticks x - tarif1a.ticks x == 23214600) = true := by decide

/-! ## Rounding and the nil-cote rule (art. 124, 126) -/
/-- Art. 124 (2): the class-1 cote is 0 at a RIA of 13 350 and 13 at 13 400: the 50 euros of income cost 13 euros,
of which 9,6 would be the tarif's own increment had the cote of 9 not been treated as nil. -/
theorem nil_cote_notch : cote .c1 13350 = 0 ∧ cote .c1 13400 = 13 := by decide
theorem roundRIA_bounds (r : Int) (h : 0 ≤ r) : roundRIA r ≤ r / 100 ∧ r / 100 < roundRIA r + 50 := by
  unfold roundRIA incomeStep
  rw [pos_of_nonneg h]
  have := toMultiple_down_bounds 50 (r / 100) (by decide)
  omega

/-! ## Fonds pour l'emploi (loi du 30 juin 1976, art. 6) -/
theorem fe_mono (k : TaxClass) : Monotone' (feTicks k) := by
  intro x y h
  have h1 := Surcharge.ticks_mono feBase (by decide) (by decide) h
  have h2 := Surcharge.ticks_mono (feHigh k) (by simp [feHigh, Surcharge.above, feRateHigh, feRate])
    (by simp [feHigh, Surcharge.above]) h
  unfold feTicks; omega
/-- The cotes at the thresholds the ACD's constants come from: 931,8 = 2 % of 46 590; 885,36 = 2 % of 44 268;
1 863,6 = 2 % of 93 180. -/
theorem fe_thresholds : coteAtThreshold .c1 = 46590 ∧ coteAtThreshold .c1a = 44268 ∧ coteAtThreshold .c2 = 93180 := by
  decide
/-- No notch at 150 000: the majoration is continuous across the threshold (7 % below, 9 % on the increment above). -/
theorem fe_continuous : taxWithFE .c1 150000 = 49851 ∧ taxWithFE .c1 150050 = 49873 := by decide

/-! ## Crédits d'impôt -/
/-- CIS: the last euro before 80 000 still carries 0,02 euros of credit, 80 000 none (art. 154quater (2)). -/
theorem cis_end : cisC 79999 = 2 ∧ cisC 80000 = 0 := by decide
/-- CIS: the two pieces meet with a rounding step of 0,45 euros between 11 265 and 11 266. -/
theorem cis_kink : cisC 11265 = 59955 ∧ cisC 11266 = 60000 := by decide
/-- CIM: continuous at 60 000 and at 105 000 (3 504 − 45 000 × 0,0612 = 750). -/
theorem cim_continuous : cimC 6000000 = 350400 ∧ cimC 10500000 = 75000 ∧ cimC 10500100 = 75000 := by decide
/-- CISSM: 81 euros a month between 1 800 and 3 000 of monthly wage, nothing from 3 600; withdrawn at 81/600 = 13,5 %
of the monthly wage between 3 000 and 3 600 (annual wages 36 000 to 43 200). -/
theorem cissm_band : cissmC 36000 = 97200 ∧ cissmC 43200 = 0 ∧ cissmC 39600 = 48600 := by decide

/-- N2 (CISSM and non-periodic pay): art. 139quater (2) leaves non-periodic pay out of the monthly wage "tant que leur
somme ... ne dépasse pas le montant de 3 000 euros". A wage of 3 250 a month (39 000 a year) earns 47,25 euros of CISSM a
month; the same 39 000 paid as 3 000 a month + a 3 000 bonus earns 81 euros a month: 405 euros a year more. -/
theorem cissm_bonus_shift : 12 * cissmMonthC 300000 - 12 * cissmMonthC 325000 = 40500 := by decide
/-- The largest possible gain of that shift is 3 000 × 81/600 = 405 euros (the taper's slope times the 3 000 cap):
shown at monthly wages 3 250 → 3 000 and 3 600 → 3 350. -/
theorem cissm_bonus_shift_top : 12 * cissmMonthC 335000 - 12 * cissmMonthC 360000 = 40500 := by decide
/-- N3 (spouse mini-job): from 936 euros of annual wage, a spouse earns the CIS (300) and the CI-CO2 (192), both
refundable (art. 154quater (2)): 492 euros of credits on 936 euros of pay. -/
theorem minijob_credits : cisC 936 + co2C 936 = 49200 ∧ cisC 935 + co2C 935 = 0 := by decide

/-! ## Unit of assessment: class 1a and unmarried parents (known: K3) -/
/-- A couple with children, each partner with a RIA of 60 000: married (class 2, art. 121) pays 2 321,46 euros more
tarif than the same partners unmarried, where the partner whose household the children belong to is in class 1a
(art. 119 2. b), 120bis) and the other in class 1. Partners under art. 3bis can choose between the two. -/
theorem married_vs_unmarried_parents :
    classTicks .c2 120000 - (classTicks .c1a 60000 + classTicks .c1 60000) = 23214600 := by decide
/-- The same at any equal split above the 1a cap: shown at RIA 2 × 54 090 .. 2 × 300 000. -/
theorem married_penalty_const :
    [54090, 80000, 117450, 200000, 300000].all
      (fun x => classTicks .c2 (2 * x) - (classTicks .c1a x + classTicks .c1 x) == 23214600) = true := by decide

/-! ## Social contributions -/
/-- The annual ceiling of the capped contributions in 2025: 4 × 13 188,96 + 8 × 13 518,68 = 160 905,28 euros. -/
theorem social_ceiling : cappedBaseC 200000 = 16090528 := by decide

end LuTax
