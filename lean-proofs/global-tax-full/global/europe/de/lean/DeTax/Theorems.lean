import DeTax.Assess
import DeTax.Pap

/-!
# Theorems about the 2025 tariff, the splitting, the Soli and the PAP

General theorems hold for every input (no `sorry`, no `native_decide`; `#print axioms` at the end). Concrete ones are
checked by the kernel on the numbers they name (`decide`).

`N x` is the statute's formula of § 32a (1) for VZ 2025 before its single rounding, in 10⁻¹⁰ euro, and
`t2025.est x = N x / 10¹⁰` (`est_eq`).
-/

set_option linter.deprecated false

namespace DeTax.Th

/-- Induction upwards from `m` over the integers. -/
theorem int_induction {P : Int → Prop} (m : Int) (h0 : P m) (hs : ∀ n, m ≤ n → P n → P (n + 1)) :
    ∀ n, m ≤ n → P n := by
  intro n hn
  obtain ⟨k, hk⟩ : ∃ k : Nat, n = m + k := ⟨(n - m).toNat, by omega⟩
  subst hk
  induction k with
  | zero => simpa using h0
  | succ k ih =>
    have e : m + ((k + 1 : Nat) : Int) = m + (k : Int) + 1 := by omega
    rw [e]; exact hs _ (by omega) (ih (by omega))

/-- § 32a (1) Satz 2 for VZ 2025, in 10⁻¹⁰ euro, with literal coefficients. -/
def N (x : Int) : Int :=
  if x ≤ 12096 then 0
  else if x ≤ 17443 then (93230 * (x - 12096) + 1400000000) * (x - 12096)
  else if x ≤ 68480 then (17664 * (x - 17443) + 2397000000) * (x - 17443) + 10151300000000
  else if x ≤ 277825 then (42 * x - 1091192) * 100000000
  else (45 * x - 1924667) * 100000000

theorem num_eq (x : Int) : t2025.num x = N x := by
  simp only [Tarif.num, t2025, N]; rfl

theorem est_eq (x : Int) : t2025.est x = N x / 10000000000 := by
  simp only [Tarif.est, num_eq]

/-! ## The five formulas -/

theorem N_z1 {x : Int} (h : x ≤ 12096) : N x = 0 := by unfold N; rw [if_pos h]
theorem N_z2 {x : Int} (h1 : 12096 < x) (h2 : x ≤ 17443) :
    N x = (93230 * (x - 12096) + 1400000000) * (x - 12096) := by
  unfold N; rw [if_neg (by omega), if_pos h2]
theorem N_z3 {x : Int} (h1 : 17443 < x) (h2 : x ≤ 68480) :
    N x = (17664 * (x - 17443) + 2397000000) * (x - 17443) + 10151300000000 := by
  unfold N; rw [if_neg (by omega), if_neg (by omega), if_pos h2]
theorem N_z4 {x : Int} (h1 : 68480 < x) (h2 : x ≤ 277825) : N x = (42 * x - 1091192) * 100000000 := by
  unfold N; rw [if_neg (by omega), if_neg (by omega), if_neg (by omega), if_pos h2]
theorem N_z5 {x : Int} (h1 : 277825 < x) : N x = (45 * x - 1924667) * 100000000 := by
  unfold N; rw [if_neg (by omega), if_neg (by omega), if_neg (by omega), if_neg (by omega)]

/-- Zone 2: one more euro adds `1 400 000 000 + 93 230·(2d + 1)` (in 10⁻¹⁰ €), `d` euros above the Grundfreibetrag. -/
theorem sq_step (a b d : Int) : (a * (d + 1) + b) * (d + 1) - (a * d + b) * d = a * (2 * d + 1) + b := by
  grind

/-- **The marginal rate inside zone 2 is linear-progressive**: it starts at 14 % and rises by 2 × 932,30 / 10⁸ per
euro (exact identity for every `x` with `x` and `x + 1` in zone 2). -/
theorem N_step_z2 {x : Int} (h1 : 12096 < x) (h2 : x + 1 ≤ 17443) :
    N (x + 1) - N x = 1400000000 + 93230 * (2 * (x - 12096) + 1) := by
  rw [N_z2 h1 (by omega), N_z2 (by omega) h2]
  have := sq_step 93230 1400000000 (x - 12096)
  have e : x + 1 - 12096 = x - 12096 + 1 := by omega
  rw [e]; omega

/-- **Inside zone 3** the marginal rate starts at 23,97 % and rises by 2 × 176,64 / 10⁸ per euro. -/
theorem N_step_z3 {x : Int} (h1 : 17443 < x) (h2 : x + 1 ≤ 68480) :
    N (x + 1) - N x = 2397000000 + 17664 * (2 * (x - 17443) + 1) := by
  rw [N_z3 h1 (by omega), N_z3 (by omega) h2]
  have := sq_step 17664 2397000000 (x - 17443)
  have e : x + 1 - 17443 = x - 17443 + 1 := by omega
  rw [e]; omega

theorem N_step_z4 {x : Int} (h1 : 68480 < x) (h2 : x + 1 ≤ 277825) : N (x + 1) - N x = 4200000000 := by
  rw [N_z4 h1 (by omega), N_z4 (by omega) h2]; omega

theorem N_step_z5 {x : Int} (h1 : 277825 < x) : N (x + 1) - N x = 4500000000 := by
  rw [N_z5 h1, N_z5 (by omega)]; omega

/-! ## The zone boundaries: where the statute's formulas meet -/

/-- At 12 096 € the formulas of zones 1 and 2 meet exactly (both 0). At 277 825 € those of zones 4 and 5 meet
exactly. At 17 443 € the zone-3 formula starts 0,16 cent *above* where zone 2 ends (1 015,13 € against
1 015,1283831070 €). At 68 480 € the zone-4 line passes 9,41 cent *below* the end of zone 3 (17 849,68 € against
17 849,7741118016 €): the coefficients are rounded to the cent, so the published formula is not continuous. -/
theorem boundaries :
    (93230 * 0 + 1400000000) * 0 = N 12096 ∧
    (17664 * 0 + 2397000000) * 0 + 10151300000000 - N 17443 = 16168930 ∧
    (42 * 68480 - 1091192) * 100000000 - N 68480 = -941118016 ∧
    (45 * 277825 - 1924667) * 100000000 - N 277825 = 0 := by decide

/-- The steps across the boundaries: from 17 443 to 17 444 € the tax rises by 24,13 cent, from 68 480 to 68 481 €
by only 32,59 cent (a marginal rate of 32,6 % for that one euro, between 42 % on both sides). -/
theorem boundary_steps :
    N 12097 - N 12096 = 1400093230 ∧ N 17444 - N 17443 = 2413186594 ∧
    N 68481 - N 68480 = 3258881984 ∧ N 277826 - N 277825 = 4500000000 := by decide

/-! ## Monotone, with marginal rates between 14 % and 45 % -/

/-- **One more euro of income costs between 14 and 45 cent** (exact formula, any income from the Grundfreibetrag
on, across every zone boundary). -/
theorem N_step_bounds {x : Int} (h : 12096 ≤ x) :
    1400000000 ≤ N (x + 1) - N x ∧ N (x + 1) - N x ≤ 4500000000 := by
  rcases (by omega : x = 12096 ∨ (12096 < x ∧ x + 1 ≤ 17443) ∨ x = 17443 ∨ (17443 < x ∧ x + 1 ≤ 68480) ∨
      x = 68480 ∨ (68480 < x ∧ x + 1 ≤ 277825) ∨ x = 277825 ∨ 277825 < x) with
    h | ⟨h1, h2⟩ | h | ⟨h1, h2⟩ | h | ⟨h1, h2⟩ | h | h
  · subst h; decide
  · rw [N_step_z2 h1 h2]; omega
  · subst h; decide
  · rw [N_step_z3 h1 h2]; omega
  · subst h; decide
  · rw [N_step_z4 h1 h2]; omega
  · subst h; decide
  · rw [N_step_z5 h]; omega

theorem N_step_low {x : Int} (h : x + 1 ≤ 12096) : N (x + 1) - N x = 0 := by
  rw [N_z1 h, N_z1 (by omega)]; rfl

theorem N_step_nonneg (x : Int) : 0 ≤ N (x + 1) - N x := by
  by_cases h : 12096 ≤ x
  · exact Int.le_trans (by omega) (N_step_bounds h).1
  · rw [N_step_low (by omega)]; exact Int.le_refl 0

/-- `N` is non-decreasing. -/
theorem N_mono {x y : Int} (h : x ≤ y) : N x ≤ N y :=
  int_induction (P := fun y => N x ≤ N y) x (Int.le_refl _)
    (fun n _ ih => by have := N_step_nonneg n; omega) y h

/-- **The 2025 tariff is monotone**: more taxable income never means less tax (§ 32a (1), rounding included). -/
theorem est_mono {x y : Int} (h : x ≤ y) : t2025.est x ≤ t2025.est y := by
  rw [est_eq, est_eq]; exact Int.ediv_le_ediv (by decide) (N_mono h)

/-- **No cliff anywhere**: one more euro of taxable income raises the tax by 0 or 1 euro, never more, never less,
at every income including the zone boundaries. -/
theorem est_step (x : Int) : t2025.est (x + 1) = t2025.est x ∨ t2025.est (x + 1) = t2025.est x + 1 := by
  rw [est_eq, est_eq]
  have h0 := N_step_nonneg x
  have h1 : N (x + 1) - N x ≤ 4500000000 := by
    by_cases h : 12096 ≤ x
    · exact (N_step_bounds h).2
    · rw [N_step_low (by omega)]; decide
  omega

/-- The marginal rate over any stretch `h ≥ 0` above the Grundfreibetrag lies between 14 % and 45 % (exact). -/
theorem N_marginal {x : Int} (hx : 12096 ≤ x) {h : Int} (hh : 0 ≤ h) :
    1400000000 * h ≤ N (x + h) - N x ∧ N (x + h) - N x ≤ 4500000000 * h :=
  int_induction (P := fun h => 1400000000 * h ≤ N (x + h) - N x ∧ N (x + h) - N x ≤ 4500000000 * h) 0
    (by simp)
    (fun n hn ih => by
      have := N_step_bounds (x := x + n) (by omega)
      rw [show x + (n + 1) = x + n + 1 by omega]
      constructor <;> omega) h hh

/-- The same for the rounded tax: `h` more euros cost at least `0,14·h − 1` and at most `0,45·h + 1` euros. -/
theorem est_marginal {x : Int} (hx : 12096 ≤ x) {h : Int} (hh : 0 ≤ h) :
    14 * h - 100 < 100 * (t2025.est (x + h) - t2025.est x) ∧
    100 * (t2025.est (x + h) - t2025.est x) < 45 * h + 100 := by
  rw [est_eq, est_eq]
  have := N_marginal hx hh
  omega

/-- **Below the Grundfreibetrag nothing is due — and, because the result is rounded down, nothing up to 12 103 €.**
The first euro of tax is due at 12 104 € of taxable income. -/
theorem est_eq_zero_iff (x : Int) : t2025.est x = 0 ↔ x ≤ 12103 := by
  rw [est_eq]
  constructor
  · intro h
    by_cases hc : x ≤ 12103
    · exact hc
    · have h1 : N 12104 ≤ N x := N_mono (by omega)
      have h2 : N 12104 = 11205966720 := by decide
      omega
  · intro h
    have h1 : N x ≤ N 12103 := N_mono h
    have h2 : N 12103 = 9804568270 := by decide
    have h3 : 0 ≤ N x := by
      by_cases hx : x ≤ 12096
      · rw [N_z1 hx]; exact Int.le_refl 0
      · have := N_mono (show (12096 : Int) ≤ x by omega); rw [N_z1 (Int.le_refl _)] at this; exact this
    omega

end DeTax.Th

namespace DeTax.Th

/-! ## The BMF's PAP computes exactly § 32a -/

/-- **The tariff routine `UPTAB25` of the BMF's Programmablaufplan 2025 equals § 32a (1) for every whole-euro
income** (including negative ones): the BMF's BigDecimal pseudo-code with its scales and ROUND_DOWN modes adds no
rounding of its own. -/
theorem uptab25_eq_est (X : Int) : Pap.uptab25 (100 * X) = t2025.est X := by
  rw [est_eq]
  unfold Pap.uptab25 Pap.down
  by_cases h1 : X ≤ 12096
  · rw [if_pos (by omega), N_z1 h1]; rfl
  · rw [if_neg (by omega)]
    by_cases h2 : X ≤ 17443
    · rw [if_pos (by omega), N_z2 (by omega) h2]
      have e1 : 100 * X - 1209600 = 100 * (X - 12096) := by omega
      rw [e1]
      have key : (100 * (X - 12096) * 93230 + 1400 * 100000000) * (100 * (X - 12096))
          = 10000 * ((93230 * (X - 12096) + 1400000000) * (X - 12096)) := by grind
      have pos : 0 ≤ (93230 * (X - 12096) + 1400000000) * (X - 12096) := Int.mul_nonneg (by omega) (by omega)
      dsimp only; rw [key, Int.tdiv_eq_ediv_of_nonneg (by omega)]
      omega
    · rw [if_neg (by omega)]
      by_cases h3 : X ≤ 68480
      · rw [if_pos (by omega), N_z3 (by omega) h3]
        have e1 : 100 * X - 1744300 = 100 * (X - 17443) := by omega
        rw [e1]
        have key : (100 * (X - 17443) * 17664 + 2397 * 100000000) * (100 * (X - 17443)) + 101513 * 1000000000000
            = 10000 * ((17664 * (X - 17443) + 2397000000) * (X - 17443) + 10151300000000) := by grind
        have pos : 0 ≤ (17664 * (X - 17443) + 2397000000) * (X - 17443) := Int.mul_nonneg (by omega) (by omega)
        dsimp only; rw [key, Int.tdiv_eq_ediv_of_nonneg (by omega)]
        omega
      · rw [if_neg (by omega)]
        by_cases h4 : X ≤ 277825
        · rw [if_pos (by omega), N_z4 (by omega) h4, Int.tdiv_eq_ediv_of_nonneg (by omega)]
          omega
        · rw [if_neg (by omega), N_z5 (by omega), Int.tdiv_eq_ediv_of_nonneg (by omega)]
          omega

/-- **Steuerklassen I to IV in the PAP are the statute's tariff** on the zu versteuernder Jahresbetrag, and
Steuerklasse III (`KZTAB = 2`) is the Splitting-Verfahren of § 32a (5) (§ 39b (2) Satz 6). -/
theorem pap_mlst (i : Pap.In) (hs : i.STKL < 5) (ZVEc KZTAB : Int) (_hk : 0 < KZTAB) (hz : 100 ≤ ZVEc) :
    Pap.mlst i ZVEc KZTAB = t2025.est (ZVEc / (100 * KZTAB)) * KZTAB := by
  unfold Pap.mlst Pap.down
  have h1 : ¬ ZVEc < 100 := by omega
  simp only [h1, hs, ↓reduceIte]
  rw [Int.tdiv_eq_ediv_of_nonneg (by omega), Int.mul_comm _ 100, uptab25_eq_est]

theorem pap_class3_is_splitting (i : Pap.In) (hs : i.STKL < 5) (ZVEc : Int) (hz : 100 ≤ ZVEc) :
    Pap.mlst i ZVEc 2 = t2025.estSplit (euroDown ZVEc) := by
  rw [pap_mlst i hs ZVEc 2 (by decide) hz]
  unfold Tarif.estSplit euroDown
  have : ZVEc / (100 * 2) = ZVEc / 100 / 2 := by omega
  rw [this, Int.mul_comm]

/-- **The PAP departs from the words of § 39b (2) Satz 7 in Steuerklassen V and VI.** The statute takes "den
Steuerbetrag für das Eineinviertelfache und ... das Dreiviertelfache des zu versteuernden Jahresbetrags nach § 32a
Absatz 1", and § 32a (1) Satz 1 measures the tax on the amount "auf volle Euro abgerundet"; `UP5_6` evaluates the
formula at 1,25·ZX and 0,75·ZX with their cents. For ZX = 13 803 € the PAP gives 1 940 €, the statute's words
1 938 €. (Over ZX = 0 … 299 999, `UP5_6` differs on 71 770 amounts, by 2 €; the annual Lohnsteuer of classes V and
VI, `MST5_6`, which uses `UP5_6` up to 13 785 € and at its thresholds, on 1 677 amounts, by ±2 €; FINDINGS P2.) -/
theorem pap_class5_cents :
    Pap.up56 13803 = 1940 ∧
    (let ST1 := t2025.est ((13803 * 125) / 100); let ST2 := t2025.est ((13803 * 75) / 100);
     max ((13803 * 14) / 100) ((ST1 - ST2) * 2)) = 1938 := by decide

end DeTax.Th

namespace DeTax.Th

/-! ## Sums of steps -/

/-- If every step on `[a, b)` is at most `c`, the rise over `[a, b]` is at most `c·(b − a)`; likewise from below. -/
theorem N_rise_le {a b c : Int} (hab : a ≤ b) (h : ∀ k, a ≤ k → k < b → N (k + 1) - N k ≤ c) :
    N b - N a ≤ c * (b - a) :=
  int_induction (P := fun y => y ≤ b → N y - N a ≤ c * (y - a)) a (by intro _; simp)
    (fun n hn ih hnb => by
      have := h n hn (by omega)
      have := ih (by omega)
      rw [show n + 1 - a = (n - a) + 1 by omega, Int.mul_add, Int.mul_one]; omega) b hab (Int.le_refl _)

theorem N_rise_ge {a b c : Int} (hab : a ≤ b) (h : ∀ k, a ≤ k → k < b → c ≤ N (k + 1) - N k) :
    c * (b - a) ≤ N b - N a :=
  int_induction (P := fun y => y ≤ b → c * (y - a) ≤ N y - N a) a (by intro _; simp)
    (fun n hn ih hnb => by
      have := h n hn (by omega)
      have := ih (by omega)
      rw [show n + 1 - a = (n - a) + 1 by omega, Int.mul_add, Int.mul_one]; omega) b hab (Int.le_refl _)

/-- In zone 3 the rise over a window of `h` euros is linear in its end: `h·(17 664·(2e − h) + 2 397 000 000)`. -/
theorem N_window_z3 {x h : Int} (h1 : 17443 < x - h) (h2 : x ≤ 68480) (hh : 0 ≤ h) :
    N x - N (x - h) = h * (17664 * (2 * (x - 17443) - h) + 2397000000) := by
  rw [N_z3 (by omega) h2, N_z3 h1 (by omega)]
  have e : x - h - 17443 = (x - 17443) - h := by omega
  rw [e]; grind

/-! ## Kindergeld against the Freibeträge (§ 31): where the Günstigerprüfung turns -/

/-- What the Freibeträge of one child (9 600 €) save a jointly assessed couple with Einkommen `E`, against the
3 060 € of Kindergeld (§ 31 Satz 4: the Freibeträge are deducted when the Kindergeld does not achieve the
exemption, i.e. when they save more). -/
def kgSavingJoint (E : Int) : Int := t2025.estSplit E - t2025.estSplit (E - 9600)

theorem kgSavingJoint_eq (E : Int) :
    kgSavingJoint E = 2 * (N (E / 2) / 10000000000) - 2 * (N (E / 2 - 4800) / 10000000000) := by
  unfold kgSavingJoint Tarif.estSplit
  rw [est_eq, est_eq, show (E - 9600) / 2 = E / 2 - 4800 by omega]

theorem step_le_low {k : Int} (h : k ≤ 22242) : N (k + 1) - N k ≤ 2600000000 := by
  rcases (by omega : k + 1 ≤ 12096 ∨ k = 12096 ∨ (12096 < k ∧ k + 1 ≤ 17443) ∨ k = 17443 ∨
      (17443 < k ∧ k + 1 ≤ 68480)) with h' | h' | ⟨h1, h2⟩ | h' | ⟨h1, h2⟩
  · rw [N_step_low h']; decide
  · subst h'; decide
  · rw [N_step_z2 h1 h2]; omega
  · subst h'; decide
  · rw [N_step_z3 h1 h2]; omega

theorem step_ge_high {k : Int} (h : 58000 ≤ k) : 3258881984 ≤ N (k + 1) - N k := by
  rcases (by omega : (k + 1 ≤ 68480) ∨ k = 68480 ∨ (68480 < k ∧ k + 1 ≤ 277825) ∨ k = 277825 ∨ 277825 < k) with
    h' | h' | ⟨h1, h2⟩ | h' | h'
  · rw [N_step_z3 (by omega) h']; omega
  · subst h'; decide
  · rw [N_step_z4 h1 h2]; omega
  · subst h'; decide
  · rw [N_step_z5 h']; omega

/-- **The crossover for a married couple with one child.** Up to an Einkommen of 84 439 € the Kindergeld is always
better; from 84 558 € the Freibeträge always are. In between, because each tariff amount is rounded down to the
euro, the result of § 31 changes back and forth: it turns to the Freibeträge at 84 462 €, back at 84 464 €, … (29
turns, the last at 84 548 €; `kg_flips`). -/
theorem kg_crossover_joint (E : Int) :
    (E ≤ 84439 → kgSavingJoint E ≤ 3060) ∧ (84558 ≤ E → 3060 < kgSavingJoint E) := by
  rw [kgSavingJoint_eq]
  constructor
  · intro hE
    by_cases hu : E / 2 ≤ 22243
    · -- the window lies at or below 22 243 €: every step is at most 0,26 €
      have := N_rise_le (a := E / 2 - 4800) (b := E / 2) (c := 2600000000) (by omega)
        (fun k _ hk => step_le_low (by omega))
      have := N_mono (show E / 2 - 4800 ≤ E / 2 by omega)
      omega
    · have hw := N_window_z3 (x := E / 2) (h := 4800) (by omega) (by omega) (by decide)
      omega
  · intro hE
    by_cases hu : E / 2 ≤ 68480
    · have hw := N_window_z3 (x := E / 2) (h := 4800) (by omega) hu (by decide)
      omega
    · have := N_rise_ge (a := E / 2 - 4800) (b := E / 2) (c := 3258881984) (by omega)
        (fun k hk _ => step_ge_high (by omega))
      omega

/-- The turns inside the band, checked one by one. -/
theorem kg_flips :
    kgSavingJoint 84461 ≤ 3060 ∧ 3060 < kgSavingJoint 84462 ∧ 3060 < kgSavingJoint 84463 ∧
    kgSavingJoint 84464 ≤ 3060 ∧ 3060 < kgSavingJoint 84468 ∧ kgSavingJoint 84547 ≤ 3060 ∧
    3060 < kgSavingJoint 84548 := by decide

/-! ## Splitting against separate assessment -/

/-- **Splitting can cost a couple one euro more than two separate assessments**, because each half is taxed and
rounded down on its own and then doubled: spouses with 99 999 € and 100 001 € of taxable income pay 62 176 €
jointly (2 × 31 088 €) but 31 087 € + 31 088 € = 62 175 € by the single tariff. -/
theorem splitting_costs_one_euro :
    t2025.estSplit (99999 + 100001) = 62176 ∧ t2025.est 99999 + t2025.est 100001 = 62175 := by decide

end DeTax.Th

namespace DeTax.Th

/-! ## Solidaritätszuschlag (SolZG 1995 § 3 (3), § 4, 2025) -/

/-- The Soli on a tariff tax of `A` whole euros with Freigrenze `F`, in cents, as `assessUnit` computes it (no
§ 32d tax): 5,5 % of `A`, but not more than 11,9 % of `A − F`, nothing up to `F`, cents truncated. -/
def soliC (F A : Int) : Int :=
  if 100 * A > 100 * F then min (55 * (100 * A)) (119 * (100 * A - 100 * F)) / 1000 else 0

/-- **The Soli never exceeds 5,5 % of the tax.** -/
theorem soli_le_rate (F A : Int) (hA : 0 ≤ A) : 10 * soliC F A ≤ 55 * A := by
  unfold soliC; split <;> omega

/-- **A Freigrenze softened by the Milderungszone**: nothing is due up to the Freigrenze; one euro of tax above it
costs 11 cents, not 5,5 % of the whole tax (which a bare Freigrenze would charge: 1 097 € at 19 951 €). -/
theorem soli_freigrenze (F A : Int) (hF : 2 ≤ F) :
    (A ≤ F → soliC F A = 0) ∧ soliC F (F + 1) = 11 := by
  unfold soliC
  constructor
  · intro h; rw [if_neg (by omega)]
  · rw [if_pos (by omega)]; omega

/-- **In the Milderungszone each euro of income tax adds 11,9 cent of Soli** (11 or 12 after truncation). -/
theorem soli_milderung_step (F A : Int) (h1 : F < A) (h2 : 64 * (A + 1) ≤ 119 * F) :
    soliC F (A + 1) - soliC F A = 11 ∨ soliC F (A + 1) - soliC F A = 12 := by
  unfold soliC
  rw [if_pos (by omega), if_pos (by omega)]
  omega

/-- From `64·A ≥ 119·F` on, the full 5,5 % applies. -/
theorem soli_full (F A : Int) (hF : 0 < F) (h : 119 * F ≤ 64 * A) : soliC F A = (55 * (100 * A)) / 1000 := by
  unfold soliC
  rw [if_pos (by omega)]
  omega

/-- 2025: the Milderungszone runs from 19 951 € to 37 094 € of tax for a single person (39 901 € to 74 189 €
jointly, where 74 190 = ⌈2 × 37 094,53⌉); at 37 095 € (74 190 €) the full 5,5 % is reached. -/
theorem soli_zone_2025 :
    soliC 19950 37094 = (119 * (100 * 37094 - 100 * 19950)) / 1000 ∧ 119 * (37094 - 19950) < 55 * 37094 ∧
    119 * 19950 ≤ 64 * 37095 ∧ 64 * 37094 < 119 * 19950 ∧
    119 * 39900 ≤ 64 * 74190 ∧ 64 * 74189 < 119 * 39900 := by decide

/-- **The famous 47 %**: for a single person with taxable income in zone 4 whose tax lies in the Milderungszone,
income tax plus Soli rise by 46,998 cent per euro of taxable income (0,42 × 1,119), up to the rounding of two
amounts: over `h` euros, within 1,13 € of 0,46998·h. -/
theorem soli_band_rate {x h : Int} (h1 : 68480 < x) (hh : 0 ≤ h) (h2 : x + h ≤ 277825)
    (hA : 19950 < t2025.est x) (hB : 64 * t2025.est (x + h) ≤ 119 * 19950) :
    46998 * h - 113000 < 1000 * (100 * (t2025.est (x + h) - t2025.est x)
        + (soliC 19950 (t2025.est (x + h)) - soliC 19950 (t2025.est x))) ∧
    1000 * (100 * (t2025.est (x + h) - t2025.est x)
        + (soliC 19950 (t2025.est (x + h)) - soliC 19950 (t2025.est x))) < 46998 * h + 113000 := by
  have hm := est_mono (show x ≤ x + h by omega)
  have e1 : N (x + h) - N x = 4200000000 * h := by
    rw [N_z4 h1 (by omega), N_z4 (by omega) h2]; omega
  have ex := est_eq x
  have exh := est_eq (x + h)
  unfold soliC
  rw [if_pos (by omega), if_pos (by omega)]
  omega

end DeTax.Th

namespace DeTax.Th

/-! ## The highest combined marginal rate below the contribution ceilings

For a childless employee aged 40, single, with wages `w` only (above the Übergangsbereich), the model's burden
(income tax + Soli + employee contributions, in cents) is, step by step as `svPerson` and `assessUnit` compute it
(`burden_matches_model` in `Tests.lean` checks it against `assess` for every wage from 24 001 to 140 000 €): -/

def burdenSingle (w : Int) : Int :=
  let rv := bpOf 930 (min (ct w) (ct 96600))
  let av := bpOf 130 (min (ct w) (ct 96600))
  let kv := bpOf 855 (min (ct w) (ct 66150))
  let pv := bpOf 240 (min (ct w) (ct 66150))
  let kvBasis := kv - bpOf 400 kv
  let rvEmp := bpOf 1860 (min (ct w) (ct 96600)) - rv
  let nr2 := min (rv + rvEmp) (ct 29344) - rvEmp
  let nr3 := kvBasis + pv
  let nr3a := av + (kv - kvBasis)
  let vors := pos nr2 + max nr3 (min (nr3 + nr3a) (ct 1900))
  let eink := ct (w - 1230) - vors - ct 36
  let zve := euroDown eink
  let tax := t2025.est zve
  ct tax + soliC 19950 tax + rv + av + kv + pv

/-- The burden in the band, piece by piece: RV 9,3 % and AV 1,3 % of the wage (rounded to the cent), KV and PV at
their ceiling (5 655,83 € and 1 587,60 €), taxable income `w − 1 230 − 36 − RV − 7 017,20` rounded down, the zone-4
tax and the Soli of the Milderungszone. -/
def bandForm (w : Int) : Int :=
  let rv := (93 * w + 5) / 10
  let av := (13 * w + 5) / 10
  let zve := (100 * w - rv - 828320) / 100
  let tax := (42 * zve - 1091192) / 100
  100 * tax + (119 * (100 * tax - 1995000)) / 1000 + rv + av + 565583 + 158760

theorem burdenSingle_band {w : Int} (h1 : 90300 ≤ w) (h2 : w ≤ 96600) : burdenSingle w = bandForm w := by
  have erv : bpOf 930 (min (ct w) (ct 96600)) = (93 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have eav : bpOf 130 (min (ct w) (ct 96600)) = (13 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have ekv : bpOf 855 (min (ct w) (ct 66150)) = 565583 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_right (by omega)]; decide
  have epv : bpOf 240 (min (ct w) (ct 66150)) = 158760 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_right (by omega)]; decide
  have ecut : bpOf 400 565583 = 22623 := by decide
  have eemp : bpOf 1860 (min (ct w) (ct 96600)) = (186 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  unfold burdenSingle bandForm
  simp only [erv, eav, ekv, epv, ecut, eemp]
  have hz : 68480 < (100 * w - (93 * w + 5) / 10 - 828320) / 100 := by omega
  have hz2 : (100 * w - (93 * w + 5) / 10 - 828320) / 100 ≤ 277825 := by omega
  have evors : pos (min ((93 * w + 5) / 10 + ((186 * w + 5) / 10 - (93 * w + 5) / 10)) (ct 29344)
      - ((186 * w + 5) / 10 - (93 * w + 5) / 10))
      + max (565583 - 22623 + 158760) (min (565583 - 22623 + 158760 + ((13 * w + 5) / 10 + (565583 - (565583 - 22623)))) (ct 1900))
      = (93 * w + 5) / 10 + 701720 := by
    unfold pos ct; omega
  rw [evors]
  have ezve : euroDown (ct (w - 1230) - ((93 * w + 5) / 10 + 701720) - ct 36)
      = (100 * w - (93 * w + 5) / 10 - 828320) / 100 := by
    unfold euroDown ct; omega
  rw [ezve, est_eq, N_z4 hz hz2]
  have et : (42 * ((100 * w - (93 * w + 5) / 10 - 828320) / 100) - 1091192) * 100000000 / 10000000000
      = (42 * ((100 * w - (93 * w + 5) / 10 - 828320) / 100) - 1091192) / 100 := by omega
  rw [et]
  unfold soliC ct
  have hpos : 100 * ((42 * ((100 * w - (93 * w + 5) / 10 - 828320) / 100) - 1091192) / 100) > 100 * 19950 := by omega
  rw [if_pos hpos]
  have hmin : min (55 * (100 * ((42 * ((100 * w - (93 * w + 5) / 10 - 828320) / 100) - 1091192) / 100)))
      (119 * (100 * ((42 * ((100 * w - (93 * w + 5) / 10 - 828320) / 100) - 1091192) / 100) - 100 * 19950))
      = 119 * (100 * ((42 * ((100 * w - (93 * w + 5) / 10 - 828320) / 100) - 1091192) / 100) - 100 * 19950) := by
    rw [Int.min_eq_right (by omega)]
  rw [hmin]
  omega

/-- **The peak combined marginal rate: 53,23 %.** Between 90 300 € and 96 600 € of wages (above the health-insurance
ceiling of 66 150 €, below the pension ceiling of 96 600 €, taxable income in zone 4, tax in the Soli
Milderungszone), each euro of wages costs 9,3 % RV + 1,3 % AV + 42 % × 90,7 % income tax (RV is deductible, AV
is not: § 10 (4) Satz 4) + 11,9 % of that as Soli: 0,106 + 0,907 × 0,42 × 1,119 = 0,53227186. Over `h` euros the
burden rises by 53,227186 cent per euro, within 1,70 € in all. -/
theorem marginal_peak {w h : Int} (hw : 90300 ≤ w) (hh : 0 ≤ h) (hwh : w + h ≤ 96600) :
    53227186 * h - 170000000 < 1000000 * (burdenSingle (w + h) - burdenSingle w) ∧
    1000000 * (burdenSingle (w + h) - burdenSingle w) < 53227186 * h + 170000000 := by
  rw [burdenSingle_band hw (by omega), burdenSingle_band (by omega) hwh]
  unfold bandForm
  dsimp only
  omega

end DeTax.Th

namespace DeTax.Th

/-- **"Dauerhaft günstiger" — the BMF's threshold is a theorem.** The BMF's Datensammlung zur Steuerpolitik 2026,
Tabelle 2.8.3, gives for 2025 the income "ab dem der Kinderfreibetrag dauerhaft günstiger ist als das Kindergeld":
for married couples with one child 84 548 € (Bruttolohn 101 455 €). From 84 548 € on the Freibeträge win for every
income; at 84 547 € the Kindergeld still does. -/
theorem kg_permanent_joint :
    kgSavingJoint 84547 ≤ 3060 ∧ ∀ E, 84548 ≤ E → 3060 < kgSavingJoint E := by
  refine ⟨by decide, fun E hE => ?_⟩
  by_cases h : 84558 ≤ E
  · exact (kg_crossover_joint E).2 h
  · have : E = 84548 ∨ E = 84549 ∨ E = 84550 ∨ E = 84551 ∨ E = 84552 ∨ E = 84553 ∨ E = 84554 ∨
        E = 84555 ∨ E = 84556 ∨ E = 84557 := by omega
    rcases this with h | h | h | h | h | h | h | h | h | h <;> subst h <;> decide

/-- The same for a single parent who has both parents' Freibeträge (9 600 €) and the whole Kindergeld; no
splitting. -/
def kgSavingSingle (E : Int) : Int := t2025.est E - t2025.est (E - 9600)

theorem step_le_low2 {k : Int} (h : k ≤ 27042) : N (k + 1) - N k ≤ 2740000000 := by
  rcases (by omega : k + 1 ≤ 12096 ∨ k = 12096 ∨ (12096 < k ∧ k + 1 ≤ 17443) ∨ k = 17443 ∨
      (17443 < k ∧ k + 1 ≤ 68480)) with h' | h' | ⟨h1, h2⟩ | h' | ⟨h1, h2⟩
  · rw [N_step_low h']; decide
  · subst h'; decide
  · rw [N_step_z2 h1 h2]; omega
  · subst h'; decide
  · rw [N_step_z3 h1 h2]; omega

/-- **Single parent with one child (Tabelle 2.8.3: 44 644 €, Bruttolohn 62 175 €).** -/
theorem kg_permanent_single :
    kgSavingSingle 44643 ≤ 3060 ∧ ∀ E, 44644 ≤ E → 3060 < kgSavingSingle E := by
  refine ⟨by decide, fun E hE => ?_⟩
  unfold kgSavingSingle
  rw [est_eq, est_eq]
  by_cases hu : E ≤ 68480
  · by_cases hlo : 44700 ≤ E
    · have hw := N_window_z3 (x := E) (h := 9600) (by omega) hu (by decide)
      omega
    · have : 44644 ≤ E ∧ E < 44700 := ⟨hE, by omega⟩
      -- the 56 incomes 44 644 … 44 699, one by one
      have key : ∀ k : Nat, k < 56 → 3060 < N (44644 + k) / 10000000000 - N (44644 + k - 9600) / 10000000000 := by
        decide
      have := key (E - 44644).toNat (by omega)
      rw [show (44644 : Int) + ((E - 44644).toNat : Int) = E by omega] at this
      exact this
  · have := N_rise_ge (a := E - 9600) (b := E) (c := 3258881984) (by omega)
      (fun k hk _ => step_ge_high (by omega))
    omega

/-- With two children the Günstigerprüfung runs child by child (Bundestag, Wissenschaftliche Dienste,
WD 4 - 3000 - 065/24: "für jedes Kind, beginnend mit dem ältesten ..."): the second child's Freibeträge are tested
on the income left after the first child's. So the two-children thresholds of Tabelle 2.8.3 are the one-child ones
plus 9 600 €: 94 148 € (couples) and 54 244 € (single parents) — the BMF's printed values. Comparing all the
children's Freibeträge with all the Kindergeld at once (GETTSIM's reading) does not give them. -/
theorem kg_two_children :
    (∀ E, 94148 ≤ E → 3060 < kgSavingJoint (E - 9600)) ∧ kgSavingJoint (94147 - 9600) ≤ 3060 ∧
    (∀ E, 54244 ≤ E → 3060 < kgSavingSingle (E - 9600)) ∧ kgSavingSingle (54243 - 9600) ≤ 3060 := by
  refine ⟨fun E hE => kg_permanent_joint.2 _ (by omega), by decide,
    fun E hE => kg_permanent_single.2 _ (by omega), by decide⟩

end DeTax.Th

namespace DeTax.Th

/-- Within zone 4 (68 481 – 277 825 € each), splitting costs at most one euro more than two separate tariffs: the
formula is linear there, so only the rounding of each half can make the difference. -/
theorem splitting_zone4 {a b : Int} (ha : 68480 < a) (hab : a ≤ b) (hb : b ≤ 277825) :
    t2025.estSplit (a + b) ≤ t2025.est a + t2025.est b + 1 := by
  unfold Tarif.estSplit
  rw [est_eq, est_eq, est_eq, N_z4 (by omega) (by omega), N_z4 ha (by omega), N_z4 (by omega) hb]
  omega

/-- Within zone 3 (17 444 – 68 480 € each), likewise: the formula is convex there, so splitting saves on the exact
amounts and the two roundings can cost at most one euro. -/
theorem splitting_zone3 {a b : Int} (ha : 17443 < a) (hab : a ≤ b) (hb : b ≤ 68480) :
    t2025.estSplit (a + b) ≤ t2025.est a + t2025.est b + 1 := by
  unfold Tarif.estSplit
  have hm1 : 17443 < (a + b) / 2 := by omega
  have hm2 : (a + b) / 2 ≤ 68480 := by omega
  rw [est_eq, est_eq, est_eq, N_z3 hm1 hm2, N_z3 ha (by omega), N_z3 (by omega) hb]
  -- with u = m − a ≥ 0 and r = (a + b) − 2m ∈ {0, 1}: Q(a) + Q(b) − 2·Q(m) ≥ 0
  obtain ⟨u, hu, hua⟩ : ∃ u, 0 ≤ u ∧ a = (a + b) / 2 - u := ⟨(a + b) / 2 - a, by omega, by omega⟩
  obtain ⟨r, hr, hrb⟩ : ∃ r, (r = 0 ∨ r = 1) ∧ b = (a + b) / 2 + u + r := ⟨b - (a + b) / 2 - u, by omega, by omega⟩
  generalize hm : (a + b) / 2 = m at *
  subst hua
  subst hrb
  have key : (17664 * (m - u - 17443) + 2397000000) * (m - u - 17443)
      + (17664 * (m + u + r - 17443) + 2397000000) * (m + u + r - 17443)
      - 2 * ((17664 * (m - 17443) + 2397000000) * (m - 17443))
      = 17664 * (2 * (u * u) + 2 * (u * r) + r * r + 2 * (m - 17443) * r) + 2397000000 * r := by grind
  have h1 : 0 ≤ u * u := Int.mul_nonneg hu hu
  have h2 : 0 ≤ u * r := Int.mul_nonneg hu (by omega)
  have h3 : 0 ≤ r * r := Int.mul_nonneg (by omega) (by omega)
  have h4 : 0 ≤ (m - 17443) * r := Int.mul_nonneg (by omega) (by omega)
  have h5 : 2 * (m - 17443) * r = 2 * ((m - 17443) * r) := by grind
  omega

end DeTax.Th

namespace DeTax.Th

/-! ## Splitting against separate tariffs, for all incomes -/

/-- Every step of the formula, in closed form. -/
theorem step_val (k : Int) : N (k + 1) - N k =
    if k + 1 ≤ 12096 then 0
    else if k + 1 ≤ 17443 then 1400000000 + 93230 * (2 * (k - 12096) + 1)
    else if k = 17443 then 2413186594
    else if k + 1 ≤ 68480 then 2397000000 + 17664 * (2 * (k - 17443) + 1)
    else if k = 68480 then 3258881984
    else if k + 1 ≤ 277825 then 4200000000
    else 4500000000 := by
  by_cases h1 : k + 1 ≤ 12096
  · rw [if_pos h1, N_step_low h1]
  rw [if_neg h1]
  by_cases h2 : k + 1 ≤ 17443
  · rw [if_pos h2]
    by_cases h0 : k = 12096
    · subst h0; decide
    · exact N_step_z2 (by omega) h2
  rw [if_neg h2]
  by_cases h3 : k = 17443
  · rw [if_pos h3]; subst h3; decide
  rw [if_neg h3]
  by_cases h4 : k + 1 ≤ 68480
  · rw [if_pos h4]; exact N_step_z3 (by omega) h4
  rw [if_neg h4]
  by_cases h5 : k = 68480
  · rw [if_pos h5]; subst h5; decide
  rw [if_neg h5]
  by_cases h6 : k + 1 ≤ 277825
  · rw [if_pos h6]; exact N_step_z4 (by omega) h6
  rw [if_neg h6]
  by_cases h7 : k = 277825
  · subst h7; decide
  · exact N_step_z5 (by omega)

/-- **The steps of the formula almost never decrease.** A later step is at least an earlier one, except for three
defects: the step at 17 443 € (the 0,16-cent jump) is 1,6 mio. units (0,16 cent) above the next ones, zone 3's last
step (68 479 €) is 0,0000017 € above zone 4's, and the step at 68 480 € (the 9,41-cent jump) is up to 9,41 cent below
earlier ones. -/
theorem step_cmp {p q : Int} (hpq : p < q) :
    N (p + 1) - N p - (if p = 17443 then 16133602 else 0) - (if p = 68479 then 17472 else 0)
      - (if q = 68480 then 941135488 else 0) ≤ N (q + 1) - N q := by
  rw [step_val p, step_val q]
  repeat' split
  all_goals omega

/-- **Discrete convexity up to 9,57 cent.** For every income `m` and every `j ≥ 0`,
`N(m − j) + N(m + j) ≥ 2·N(m)` minus at most the three defects that lie in the window. -/
theorem conv_defect (m : Int) {j : Int} (hj : 0 ≤ j) :
    2 * N m - N (m - j) - N (m + j) ≤
      (if m - j ≤ 17443 ∧ 17443 < m then 16133602 else 0) + (if m - j ≤ 68479 ∧ 68479 < m then 17472 else 0)
        + (if m ≤ 68480 ∧ 68480 < m + j then 941135488 else 0) :=
  int_induction (P := fun j => 2 * N m - N (m - j) - N (m + j) ≤
      (if m - j ≤ 17443 ∧ 17443 < m then 16133602 else 0) + (if m - j ≤ 68479 ∧ 68479 < m then 17472 else 0)
        + (if m ≤ 68480 ∧ 68480 < m + j then 941135488 else 0)) 0
    (by simp only [Int.sub_zero, Int.add_zero]; rw [if_neg (by omega), if_neg (by omega), if_neg (by omega)]; omega)
    (fun j hj ih => by
      have hs := step_cmp (p := m - j - 1) (q := m + j) (by omega)
      rw [show m - j - 1 + 1 = m - j by omega] at hs
      rw [show m - (j + 1) = m - j - 1 by omega, show m + (j + 1) = m + j + 1 by omega]
      split at ih <;> split at ih <;> split at ih <;> split at hs <;> split at hs <;> split at hs <;>
        split <;> split <;> split <;> omega) j hj

/-- **Splitting never costs more than two euros against two separate tariffs**, for all taxable incomes `a ≤ b` of
the spouses: the exact formula is convex up to 9,57 cent (`conv_defect`), and the two roundings add the rest.
(Two euros is a bound, not attained in the scans: the largest excess found is one euro, `splitting_costs_one_euro`;
within a zone the bound is one euro, `splitting_zone3`, `splitting_zone4`.) -/
theorem splitting_le_two {a b : Int} (hab : a ≤ b) :
    t2025.estSplit (a + b) ≤ t2025.est a + t2025.est b + 2 := by
  unfold Tarif.estSplit
  rw [est_eq, est_eq, est_eq]
  have hc := conv_defect ((a + b) / 2) (j := (a + b) / 2 - a) (by omega)
  rw [show (a + b) / 2 - ((a + b) / 2 - a) = a by omega] at hc
  have hm := N_mono (show (a + b) / 2 + ((a + b) / 2 - a) ≤ b by omega)
  have hd : (if a ≤ 17443 ∧ 17443 < (a + b) / 2 then (16133602 : Int) else 0)
      + (if a ≤ 68479 ∧ 68479 < (a + b) / 2 then 17472 else 0)
      + (if (a + b) / 2 ≤ 68480 ∧ 68480 < (a + b) / 2 + ((a + b) / 2 - a) then 941135488 else 0) ≤ 957286562 := by
    split <;> split <;> split <;> omega
  omega

end DeTax.Th

namespace DeTax.Th

/-! ## Below the contribution ceilings the peak is the highest -/

/-- One euro more of tax never costs more than 11,9 cent of Soli (and nothing below the Freigrenze). -/
theorem soli_step_le (F A B : Int) (hF : 0 ≤ F) (hAB : A ≤ B) :
    soliC F B - soliC F A ≤ (119 * (100 * (B - A))) / 1000 + 1 := by
  unfold soliC
  split <;> split <;> omega

/-- The burden of `burdenSingle` below the health-insurance ceiling (24 001 – 66 150 €), piece by piece. -/
theorem burdenSingle_low {w : Int} (h1 : 24001 ≤ w) (h2 : w ≤ 66150) :
    burdenSingle w =
      100 * (N ((100 * w - 123000 - ((93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50)
        + (24 * w + 5) / 10) - 3600) / 100) / 10000000000)
      + (93 * w + 5) / 10 + (13 * w + 5) / 10 + (171 * w + 10) / 20 + (24 * w + 5) / 10 := by
  have erv : bpOf 930 (min (ct w) (ct 96600)) = (93 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have eav : bpOf 130 (min (ct w) (ct 96600)) = (13 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have ekv : bpOf 855 (min (ct w) (ct 66150)) = (171 * w + 10) / 20 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have epv : bpOf 240 (min (ct w) (ct 66150)) = (24 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have ecut : ∀ k : Int, bpOf 400 k = (2 * k + 25) / 50 := by intro k; unfold bpOf rndHalf; omega
  have eemp : bpOf 1860 (min (ct w) (ct 96600)) = (186 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  unfold burdenSingle
  simp only [erv, eav, ekv, epv, ecut, eemp]
  -- the tax stays below the Soli Freigrenze: taxable income at most 68 480 €
  have hz : (100 * w - 123000 - ((93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50)
        + (24 * w + 5) / 10) - 3600) / 100 ≤ 68480 := by omega
  have evors : pos (min ((93 * w + 5) / 10 + ((186 * w + 5) / 10 - (93 * w + 5) / 10)) (ct 29344)
      - ((186 * w + 5) / 10 - (93 * w + 5) / 10))
      + max ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50 + (24 * w + 5) / 10)
        (min ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50 + (24 * w + 5) / 10
          + ((13 * w + 5) / 10 + ((171 * w + 10) / 20 - ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50))))
          (ct 1900))
      = (93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50) + (24 * w + 5) / 10 := by
    unfold pos ct; omega
  rw [evors]
  have ezve : euroDown (ct (w - 1230) - ((93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50)
        + (24 * w + 5) / 10) - ct 36)
      = (100 * w - 123000 - ((93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50)
        + (24 * w + 5) / 10) - 3600) / 100 := by
    unfold euroDown ct; omega
  rw [ezve, est_eq]
  have hlow : N ((100 * w - 123000 - ((93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50)
        + (24 * w + 5) / 10) - 3600) / 100) / 10000000000 ≤ 17849 := by
    have := est_mono hz; rw [est_eq, est_eq] at this
    have h68 : N 68480 / 10000000000 = 17849 := by decide
    omega
  have hsoli : soliC 19950 (N ((100 * w - 123000 - ((93 * w + 5) / 10 + ((171 * w + 10) / 20
      - (2 * ((171 * w + 10) / 20) + 25) / 50) + (24 * w + 5) / 10) - 3600) / 100) / 10000000000) = 0 := by
    unfold soliC; rw [if_neg (by omega)]
  unfold ct at hsoli ⊢
  rw [hsoli]
  omega

/-- The taxable income below the health-insurance ceiling, in cents before the rounding (`zvC`), rises by 79,7 to
80,5 cent per euro of wages (RV 9,3 %, KV 8,55 % less 4 %, PV 2,4 % are deducted). -/
def zvC (w : Int) : Int :=
  100 * w - 123000 - ((93 * w + 5) / 10 + ((171 * w + 10) / 20 - (2 * ((171 * w + 10) / 20) + 25) / 50)
    + (24 * w + 5) / 10) - 3600

theorem zvC_rise (w h : Int) (hh : 0 ≤ h) : 7970 * h - 400 ≤ 100 * (zvC (w + h) - zvC w) ∧
    100 * (zvC (w + h) - zvC w) ≤ 8060 * h + 400 := by
  unfold zvC
  have a1 : 10 * ((93 * (w + h) + 5) / 10 - (93 * w + 5) / 10) ≤ 93 * h + 9 := by omega
  have a2 : 93 * h - 9 ≤ 10 * ((93 * (w + h) + 5) / 10 - (93 * w + 5) / 10) := by omega
  have b1 : 20 * ((171 * (w + h) + 10) / 20 - (171 * w + 10) / 20) ≤ 171 * h + 19 := by omega
  have b2 : 171 * h - 19 ≤ 20 * ((171 * (w + h) + 10) / 20 - (171 * w + 10) / 20) := by omega
  have c1 : 50 * ((2 * ((171 * (w + h) + 10) / 20) + 25) / 50 - (2 * ((171 * w + 10) / 20) + 25) / 50)
      ≤ 2 * ((171 * (w + h) + 10) / 20 - (171 * w + 10) / 20) + 49 := by omega
  have c2 : 2 * ((171 * (w + h) + 10) / 20 - (171 * w + 10) / 20) - 49
      ≤ 50 * ((2 * ((171 * (w + h) + 10) / 20) + 25) / 50 - (2 * ((171 * w + 10) / 20) + 25) / 50) := by omega
  have d1 : 10 * ((24 * (w + h) + 5) / 10 - (24 * w + 5) / 10) ≤ 24 * h + 9 := by omega
  have d2 : 24 * h - 9 ≤ 10 * ((24 * (w + h) + 5) / 10 - (24 * w + 5) / 10) := by omega
  constructor <;> omega

theorem burdenSingle_low' {w : Int} (h1 : 24001 ≤ w) (h2 : w ≤ 66150) :
    burdenSingle w = 100 * (N (zvC w / 100) / 10000000000)
      + (93 * w + 5) / 10 + (13 * w + 5) / 10 + (171 * w + 10) / 20 + (24 * w + 5) / 10 := by
  rw [burdenSingle_low h1 h2]; rfl

/-- **Below the health-insurance ceiling (24 001 – 66 150 € of wages) the combined marginal rate is at most 50,7 %**
(21,55 % contributions + at most 36,08 % × 80,6 % income tax; 50,45 % at the top), under the peak of 53,23 %:
over `h` euros the burden rises by at most 50,70 cent per euro plus 4 €. -/
theorem marginal_low {w h : Int} (hw : 24001 ≤ w) (hh : 0 ≤ h) (hwh : w + h ≤ 66150) :
    100 * (burdenSingle (w + h) - burdenSingle w) ≤ 5070 * h + 40000 := by
  rw [burdenSingle_low' (w := w + h) (by omega) hwh, burdenSingle_low' hw (by omega)]
  have hr := zvC_rise w h hh
  have lo : 1744400 ≤ zvC w := by unfold zvC; omega
  have hi : zvC (w + h) < 51717 * 100 := by unfold zvC; omega
  have hz12 : zvC w / 100 ≤ zvC (w + h) / 100 := by
    rcases (by omega : h = 0 ∨ 1 ≤ h) with h0 | h0
    · subst h0; simp
    · exact Int.ediv_le_ediv (by decide) (by omega)
  have hrise := N_rise_le (a := zvC w / 100) (b := zvC (w + h) / 100) (c := 3607814208) hz12
    (fun k hk hk2 => by rw [N_step_z3 (by omega) (by omega)]; omega)
  have m1 : 10 * ((13 * (w + h) + 5) / 10 - (13 * w + 5) / 10) ≤ 13 * h + 9 := by omega
  have m2 : 10 * ((93 * (w + h) + 5) / 10 - (93 * w + 5) / 10) ≤ 93 * h + 9 := by omega
  have m3 : 20 * ((171 * (w + h) + 10) / 20 - (171 * w + 10) / 20) ≤ 171 * h + 19 := by omega
  have m4 : 10 * ((24 * (w + h) + 5) / 10 - (24 * w + 5) / 10) ≤ 24 * h + 9 := by omega
  have f1 := ediv_bounds (N (zvC (w + h) / 100)) 10000000000 (by decide)
  have f2 := ediv_bounds (N (zvC w / 100)) 10000000000 (by decide)
  have g1 := ediv_bounds (zvC (w + h)) 100 (by decide)
  have g2 := ediv_bounds (zvC w) 100 (by decide)
  omega

end DeTax.Th


namespace DeTax.Th

/-- Between the two ceilings (66 150 – 96 600 €): KV and PV fixed at their ceiling, RV and AV on the wage. -/
theorem burdenSingle_mid {w : Int} (h1 : 66150 ≤ w) (h2 : w ≤ 96600) :
    burdenSingle w =
      100 * (N ((100 * w - (93 * w + 5) / 10 - 828320) / 100) / 10000000000)
      + soliC 19950 (N ((100 * w - (93 * w + 5) / 10 - 828320) / 100) / 10000000000)
      + (93 * w + 5) / 10 + (13 * w + 5) / 10 + 565583 + 158760 := by
  have erv : bpOf 930 (min (ct w) (ct 96600)) = (93 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have eav : bpOf 130 (min (ct w) (ct 96600)) = (13 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  have ekv : bpOf 855 (min (ct w) (ct 66150)) = 565583 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_right (by omega)]; decide
  have epv : bpOf 240 (min (ct w) (ct 66150)) = 158760 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_right (by omega)]; decide
  have ecut : bpOf 400 565583 = 22623 := by decide
  have eemp : bpOf 1860 (min (ct w) (ct 96600)) = (186 * w + 5) / 10 := by
    unfold bpOf rndHalf ct; rw [Int.min_eq_left (by omega)]; omega
  unfold burdenSingle
  simp only [erv, eav, ekv, epv, ecut, eemp]
  have evors : pos (min ((93 * w + 5) / 10 + ((186 * w + 5) / 10 - (93 * w + 5) / 10)) (ct 29344)
      - ((186 * w + 5) / 10 - (93 * w + 5) / 10))
      + max (565583 - 22623 + 158760) (min (565583 - 22623 + 158760 + ((13 * w + 5) / 10 + (565583 - (565583 - 22623)))) (ct 1900))
      = (93 * w + 5) / 10 + 701720 := by
    unfold pos ct; omega
  rw [evors]
  have ezve : euroDown (ct (w - 1230) - ((93 * w + 5) / 10 + 701720) - ct 36)
      = (100 * w - (93 * w + 5) / 10 - 828320) / 100 := by
    unfold euroDown ct; omega
  rw [ezve, est_eq]
  unfold ct
  omega

theorem step_le_42 {k : Int} (h : 17443 < k) : N (k + 1) - N k ≤ 4200017472 ∨ 277825 ≤ k := by
  rcases (by omega : k + 1 ≤ 68480 ∨ k = 68480 ∨ (68480 < k ∧ k + 1 ≤ 277825) ∨ 277825 ≤ k) with
    h' | h' | ⟨h1, h2⟩ | h'
  · left; rw [N_step_z3 h h']; omega
  · left; subst h'; decide
  · left; rw [N_step_z4 h1 h2]; omega
  · right; exact h'

/-- **Between the ceilings (66 150 – 96 600 € of wages) the combined marginal rate never exceeds the peak**:
10,6 % contributions + 42 % × 90,7 % tax + 11,9 % of that as Soli at most, 53,2272 cent per euro plus 2 €. With
`marginal_low` (at most 50,7 % below 66 150 €) and `marginal_peak` (exactly 53,227186 % from 90 300 €), the peak is
the highest combined marginal rate of a childless single employee anywhere between 24 001 € and the pension ceiling. -/
theorem marginal_mid {w h : Int} (hw : 66150 ≤ w) (hh : 0 ≤ h) (hwh : w + h ≤ 96600) :
    1000000 * (burdenSingle (w + h) - burdenSingle w) ≤ 53227200 * h + 200000000 := by
  rw [burdenSingle_mid (w := w + h) (by omega) hwh, burdenSingle_mid hw (by omega)]
  generalize hz1 : (100 * w - (93 * w + 5) / 10 - 828320) / 100 = z1
  generalize hz2 : (100 * (w + h) - (93 * (w + h) + 5) / 10 - 828320) / 100 = z2
  have m2 : 10 * ((93 * (w + h) + 5) / 10 - (93 * w + 5) / 10) ≤ 93 * h + 9 := by omega
  have m2' : 93 * h - 9 ≤ 10 * ((93 * (w + h) + 5) / 10 - (93 * w + 5) / 10) := by omega
  have m1 : 10 * ((13 * (w + h) + 5) / 10 - (13 * w + 5) / 10) ≤ 13 * h + 9 := by omega
  have hz12 : z1 ≤ z2 := by
    rcases (by omega : h = 0 ∨ 1 ≤ h) with h0 | h0
    · subst h0; rw [← hz1, ← hz2]; simp
    · rw [← hz1, ← hz2]; exact Int.ediv_le_ediv (by decide) (by omega)
  have hdz : 100 * (z2 - z1) ≤ 9070 * h / 100 + 200 := by omega
  have lo : 17443 < z1 := by omega
  have hi : z2 ≤ 80000 := by omega
  have hrise := N_rise_le (a := z1) (b := z2) (c := 4200017472) hz12
    (fun k hk hk2 => by rcases step_le_42 (k := k) (by omega) with h' | h'; exact h'; omega)
  have hmono := N_mono hz12
  have f1 := ediv_bounds (N z2) 10000000000 (by decide)
  have f2 := ediv_bounds (N z1) 10000000000 (by decide)
  have hs := soli_step_le 19950 (N z1 / 10000000000) (N z2 / 10000000000) (by decide)
    (Int.ediv_le_ediv (by decide) hmono)
  omega

end DeTax.Th

/-! ## Axioms used (standard ones only: propext, Classical.choice, Quot.sound) -/
#print axioms DeTax.Th.est_mono
#print axioms DeTax.Th.est_step
#print axioms DeTax.Th.est_marginal
#print axioms DeTax.Th.est_eq_zero_iff
#print axioms DeTax.Th.N_step_z2
#print axioms DeTax.Th.boundaries
#print axioms DeTax.Th.uptab25_eq_est
#print axioms DeTax.Th.pap_class3_is_splitting
#print axioms DeTax.Th.pap_class5_cents
#print axioms DeTax.Th.splitting_costs_one_euro
#print axioms DeTax.Th.splitting_zone3
#print axioms DeTax.Th.soli_band_rate
#print axioms DeTax.Th.kg_permanent_joint
#print axioms DeTax.Th.kg_permanent_single
#print axioms DeTax.Th.kg_two_children
#print axioms DeTax.Th.marginal_peak
#print axioms DeTax.Th.splitting_le_two
#print axioms DeTax.Th.marginal_low
#print axioms DeTax.Th.marginal_mid
