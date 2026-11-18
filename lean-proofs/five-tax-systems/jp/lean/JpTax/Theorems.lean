import JpTax.Household

/-!
# Theorems for all inputs

No `sorry`, no `native_decide`; `#print axioms` at the end. Kernel-checked facts about particular households are in
`Walls.lean`; the statute's tables against the closed forms are in `Beppyo5.lean` and `Withholding.lean`.
-/

namespace JpTax

/-! ## The salary schedule with the 所得金額調整控除 -/

/-- 給与所得 after the 所得金額調整控除 of 措置法第41条の3の11第1項 is non-decreasing in the salary: above 8,500,000 yen
the 10 % (rounded up) taken back never exceeds the extra salary. -/
theorem kyuyoAdj_mono (e : Bool) {a b : Int} (h : a ≤ b) :
    kyuyoShotoku a - adjust1 a e ≤ kyuyoShotoku b - adjust1 b e := by
  have hk := @kyuyoShotoku_mono a b h
  cases e with
  | false => simp [adjust1]; omega
  | true =>
    unfold adjust1 cdiv
    by_cases ha : a > 8500000
    · have hb : b > 8500000 := by omega
      have hka : kyuyoShotoku a = a - 1950000 := by
        unfold kyuyoShotoku kyuyoFormula kyuyoKojo10 pos
        repeat (first | split | omega)
      have hkb : kyuyoShotoku b = b - 1950000 := by
        unfold kyuyoShotoku kyuyoFormula kyuyoKojo10 pos
        repeat (first | split | omega)
      simp only [Bool.true_and, decide_eq_true_eq, ha, hb, ite_true]
      rw [hka, hkb]
      omega
    · simp only [Bool.true_and, decide_eq_true_eq, ha, ite_false]
      by_cases hb : b > 8500000
      · simp only [hb, ite_true]
        have hkb : kyuyoShotoku b = b - 1950000 := by
          unfold kyuyoShotoku kyuyoFormula kyuyoKojo10 pos
          repeat (first | split | omega)
        have hka : kyuyoShotoku a ≤ 6550000 := by
          have := @kyuyoShotoku_mono a 8500000 (by omega)
          have h85 : kyuyoShotoku 8500000 = 6550000 := by decide
          omega
        rw [hkb]
        omega
      · simp only [hb, ite_false]; omega

/-- `g − 基礎控除(g)` is non-decreasing: the 基礎控除 only ever shrinks as income grows (`kisoKojo_antitone`). -/
theorem afterKiso_mono {a b : Int} (h : a ≤ b) : a - kisoKojo a ≤ b - kisoKojo b := by
  have := @kisoKojo_antitone a b h
  omega

/-- The income tax (第89条, before 配当控除) of an employee with salary `w`, other deductions `d` (social insurance,
dependants, ...), and the 所得金額調整控除 condition `e`. -/
def salaryTax (w d : Int) (e : Bool) : Int :=
  let g := pos (kyuyoShotoku w - adjust1 w e)
  tax89 (trunc1000 (g - d - kisoKojo g))

/-- **Monotonicity of the income tax in the salary**, for fixed other deductions: the 4,000-yen rows, the 所得金額調整控除
and the shrinking 基礎控除 never make the tax fall when the salary rises. -/
theorem salaryTax_mono (d : Int) (e : Bool) {a b : Int} (h : a ≤ b) : salaryTax a d e ≤ salaryTax b d e := by
  unfold salaryTax
  apply tax89_mono
  apply trunc1000_mono
  have h1 := kyuyoAdj_mono e h
  have h2 := @afterKiso_mono (pos (kyuyoShotoku a - adjust1 a e)) (pos (kyuyoShotoku b - adjust1 b e))
    (pos_mono h1)
  omega

/-- The same for the claimant's spouse deductions: the 配偶者控除 and 配偶者特別控除 never grow with the claimant's
income (the 9,000,000 / 9,500,000 / 10,000,000 yen tiers), for any spouse income `s`. -/
theorem spouseDeduction_antitone (s : Int) (old : Bool) {a b : Int} (h : a ≤ b) :
    haigushaKojo b s old + haigushaTokubetsu b s ≤ haigushaKojo a s old + haigushaTokubetsu a s := by
  have hb : 30000 ≤ tokubetsuBase s := by unfold tokubetsuBase step5; repeat (first | split | omega)
  have hb2 : tokubetsuBase s ≤ 380000 := by unfold tokubetsuBase step5; repeat (first | split | omega)
  generalize hB : tokubetsuBase s = B at hb hb2
  unfold haigushaKojo haigushaTokubetsu douitsuLimit cdiv
  simp only [hB]
  repeat (first | split | omega)

/-! ## The exact top marginal rate -/

/-- National and local tax on a 課税総所得金額 `t` for a person whose 合計所得金額 is above 25,000,000 yen (no 基礎控除,
no 調整控除 in either tax): 所得税 (第89条) + 復興特別所得税 (2.1 %, 復興財源確保法第13条) + 都民税 4 % + 特別区民税 6 %, each
所得割 cut to 100 yen. -/
def topCombined (t : Int) : Int :=
  tax89 t + fukko (tax89 t) + trunc100 (t * 4 / 100) + trunc100 (t * 6 / 100)

/-- Above 40,000,000 yen the 速算表 is one line: 45 % less 4,796,000 yen (in hundredths). -/
theorem quick_top (x : Int) (hx : 40000000 ≤ x) : quick x = 45 * x - 479600000 := by
  unfold quick
  repeat (first | split | omega)

/-- **The exact top combined marginal rate is 55.945 % = 45 % × 1.021 + 10 %**: above 40,000,000 yen of taxable income,
every further 20,000 yen (the smallest step on which the 2.1 % comes out in whole yen) costs exactly 11,189 yen. -/
theorem top_marginal_rate (t k : Int) (ht : 40000000 ≤ t) (h1000 : t % 1000 = 0) (hk : 0 ≤ k) :
    topCombined (t + 20000 * k) - topCombined t = 11189 * k ∧ (11189 : Int) * 100000 = 55945 * 20000 := by
  refine ⟨?_, by decide⟩
  unfold topCombined tax89 fukko trunc100 pos
  rw [tax89c_eq_quick, tax89c_eq_quick, quick_top t ht, quick_top (t + 20000 * k) (by omega)]
  have hx : 0 ≤ (45 * t - 479600000) / 100 := by omega
  have e1 : (45 * (t + 20000 * k) - 479600000) / 100 = (45 * t - 479600000) / 100 + 9000 * k := by omega
  rw [e1]
  generalize hX : (45 * t - 479600000) / 100 = X at hx ⊢
  have e2 : max 0 (X + 9000 * k) * 21 / 1000 = max 0 X * 21 / 1000 + 189 * k := by
    rw [show max 0 (X + 9000 * k) = X + 9000 * k by omega, show max 0 X = X by omega]; omega
  have e3 : max 0 ((t + 20000 * k) * 4 / 100) / 100 * 100 = max 0 (t * 4 / 100) / 100 * 100 + 800 * k := by
    rw [show max 0 ((t + 20000 * k) * 4 / 100) = (t + 20000 * k) * 4 / 100 by omega,
      show max 0 (t * 4 / 100) = t * 4 / 100 by omega]
    omega
  have e4 : max 0 ((t + 20000 * k) * 6 / 100) / 100 * 100 = max 0 (t * 6 / 100) / 100 * 100 + 1200 * k := by
    rw [show max 0 ((t + 20000 * k) * 6 / 100) = (t + 20000 * k) * 6 / 100 by omega,
      show max 0 (t * 6 / 100) = t * 6 / 100 by omega]
    omega
  rw [e2, e3, e4]
  omega

/-! ## The 4,000-yen rows and the marginal rate -/

/-- **At every row boundary of 別表第五 between 1,904,000 and 6,596,000 yen one more yen of salary adds 2,800 or
3,200 yen of 給与所得**, so the marginal rate on that yen is 2,800 or 3,200 times the rate on income; inside a row it is
nil. (`beppyo5_step` in `Beppyo5.lean` is the same fact for every row; here for the income tax itself: on the yen
crossing into the row at 2,000,000 yen, an employee whose other deductions leave him in the 5 % band pays 150 yen
more tax.) -/
theorem row_notch_tax :
    salaryTax 2000000 100000 false - salaryTax 1999999 100000 false = 150 := by decide

/-! ## The walls, for every income

The 2025 reform's design, stated for all incomes rather than on example households (those are in `Walls.lean`). -/

/-- **No spouse wall below 950,000 yen of the spouse's income (salary 1,600,000)**: for a claimant with at most
9,000,000 yen, 配偶者控除 + 配偶者特別控除 is 380,000 yen for every spouse income from nothing to 950,000 — the 103万 and
123万 walls are gone; the first step down is at 950,001. -/
theorem spouseDeduction_flat (g s : Int) (hg : g ≤ 9000000) (hs : s ≤ 950000) :
    haigushaKojo g s false + haigushaTokubetsu g s = 380000 := by
  unfold haigushaKojo haigushaTokubetsu tokubetsuBase douitsuLimit
  have hg10 : g ≤ 10000000 := by omega
  by_cases h : s ≤ 580000
  · have hn : ¬ (580000 < s) := by omega
    simp [h, hn, hg, hg10]
  · have hlt : 580000 < s := by omega
    have hle : s ≤ 1330000 := by omega
    simp [h, hlt, hle, hg, hg10, hs]

/-- **No student wall below 850,000 yen (salary 1,500,000)**: for a relative aged 19–22, 扶養控除 + 特定親族特別控除 is
630,000 yen for every income up to 850,000. -/
theorem studentDeduction_flat (age i : Int) (h1 : 19 ≤ age) (h2 : age < 23) (hi : i ≤ 850000) :
    fuyoKojo ⟨age, i⟩ + tokuteiShinzokuKojo ⟨age, i⟩ = 630000 := by
  have a16 : (16 : Int) ≤ age := by omega
  have a70 : ¬ ((70 : Int) ≤ age) := by omega
  by_cases h : i ≤ 580000
  · have hn : ¬ (580000 < i) := by omega
    simp [fuyoKojo, tokuteiShinzokuKojo, Relative.kojoTaisho, Relative.tokutei, Relative.rojin, Relative.fuyo,
      h, a16, a70, h1, h2, hn]
  · have hgt : (580000 : Int) < i := by omega
    have hle : i ≤ 1230000 := by omega
    simp [fuyoKojo, tokuteiShinzokuKojo, Relative.kojoTaisho, Relative.tokutei, Relative.rojin, Relative.fuyo,
      h, h1, h2, hgt, hle, hi]

/-- **The high-school cliff**: for a relative aged 16–18 the deduction is 380,000 yen up to an income of 580,000 and
nothing one yen above; no 特定親族特別控除 softens it. -/
theorem highschool_cliff (age : Int) (h1 : 16 ≤ age) (h2 : age ≤ 18) :
    fuyoKojo ⟨age, 580000⟩ + tokuteiShinzokuKojo ⟨age, 580000⟩ = 380000 ∧
    ∀ i, 580000 < i → fuyoKojo ⟨age, i⟩ + tokuteiShinzokuKojo ⟨age, i⟩ = 0 := by
  have a19 : ¬ ((19 : Int) ≤ age) := by omega
  have a70 : ¬ ((70 : Int) ≤ age) := by omega
  constructor
  · simp [fuyoKojo, tokuteiShinzokuKojo, Relative.kojoTaisho, Relative.tokutei, Relative.rojin, Relative.fuyo,
      h1, a19, a70]
  · intro i hi
    have hn : ¬ (i ≤ 580000) := by omega
    simp [fuyoKojo, tokuteiShinzokuKojo, Relative.kojoTaisho, Relative.tokutei, Relative.rojin, Relative.fuyo,
      hn, a19]

/-! ## Axioms -/
#print axioms kyuyoAdj_mono
#print axioms salaryTax_mono
#print axioms spouseDeduction_antitone
#print axioms top_marginal_rate
#print axioms tax89c_eq_quick
#print axioms teateTable_eq_rank
#print axioms chosei_row7_dead
#print axioms spouseDeduction_flat
#print axioms studentDeduction_flat
#print axioms highschool_cliff

end JpTax
