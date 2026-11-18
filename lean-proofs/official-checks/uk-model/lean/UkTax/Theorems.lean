import UkTax.Household

/-!
# Theorems

General theorems hold for every input (no `sorry`, no `native_decide`; `#print axioms` at the end). Concrete ones
are checked by the kernel on the numbers they name (`decide`), and record cliffs, notches and the findings.

The general theorems about income tax are about individuals whose only income is non-savings income (employment,
trading, pension, property) and who make no gifts or pension contributions. For them the s. 25(2) search is forced
(`allocate_ns`) and the model's liability reduces to a closed form (`liability_nsOnly`), about which the rest is
proved. Savings, dividends, elections and the household are covered by the concrete theorems and by the referee
runs (RESULTS.md).
-/

namespace UkTax

/-! ## 1. The s. 25(2) search -/

theorem bestStep_cases (f : Int → Int → Int) (ok : Int → Int → Bool) (d c : Int × Int) :
    (bestStep f ok d c = c ∧ ok c.1 c.2 = true) ∨ bestStep f ok d c = d := by
  unfold bestStep
  split
  · next hc => simp only [Bool.and_eq_true, decide_eq_true_eq] at hc; exact Or.inl ⟨rfl, hc.1⟩
  · exact Or.inr rfl

/-- The search returns the usual-order allocation or a feasible candidate. -/
theorem bestSlices_mem (f : Int → Int → Int) (ok : Int → Int → Bool) (cs : List (Int × Int)) :
    ∀ dflt : Int × Int, bestSlices f ok dflt cs = dflt ∨
      (bestSlices f ok dflt cs ∈ cs ∧ ok (bestSlices f ok dflt cs).1 (bestSlices f ok dflt cs).2 = true) := by
  unfold bestSlices
  induction cs with
  | nil => intro d; simp
  | cons c cs ih =>
    intro d
    simp only [List.foldl_cons]
    rcases ih (bestStep f ok d c) with h | ⟨hm, hok⟩
    · rw [h]
      rcases bestStep_cases f ok d c with ⟨h1, h2⟩ | h1
      · rw [h1]; exact Or.inr ⟨List.mem_cons_self .., h2⟩
      · exact Or.inl h1
    · exact Or.inr ⟨List.mem_cons_of_mem _ hm, hok⟩

theorem bestSlices_forced (f : Int → Int → Int) (ok : Int → Int → Bool) (cs : List (Int × Int))
    (v dflt : Int × Int) (hd : dflt = v) (hall : ∀ c : Int × Int, ok c.1 c.2 = true → c = v) :
    bestSlices f ok dflt cs = v := by
  rcases bestSlices_mem f ok cs dflt with h | ⟨_, hok⟩
  · rw [h, hd]
  · exact hall _ hok

/-- With only non-savings income the allocation is forced: everything left after the deductions is non-savings. -/
theorem allocate_ns (p : Params) (r : Reading) (l : Limits) (sc : Option ScotLimits) (N ded g : Int) (_hN : 0 ≤ N) :
    allocate p r l sc N 0 0 ded g = (N - min (pos ded) N, N - min (pos ded) N, N - min (pos ded) N) := by
  unfold allocate
  simp only []
  rw [bestSlices_forced (v := (N - min (pos ded) N, N - min (pos ded) N))]
  · simp only [Int.add_zero]
  · unfold defaultSlices pos; simp only [Prod.mk.injEq]; omega
  · intro c hc
    unfold feasible at hc
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
    obtain ⟨c1, c2⟩ := c
    simp only [Prod.mk.injEq] at hc ⊢
    unfold pos at hc ⊢
    omega

theorem savingsAllowance_nonneg (p : Params) (r : Reading) (l : Limits) (c1 c2 t : Int)
    (h0 : 0 ≤ p.psaBasic) (h1 : 0 ≤ p.psaHigher) (h2 : 0 ≤ p.psaAdditional) :
    0 ≤ savingsAllowance p r l c1 c2 t := by
  unfold savingsAllowance gbp; split <;> (try split) <;> omega

/-- With no savings and no dividends, Step 4 charges the non-savings slice only. -/
theorem charged_ns_tax (p : Params) (r : Reading) (l : Limits) (t : Int)
    (h0 : 0 ≤ p.psaBasic) (h1 : 0 ≤ p.psaHigher) (h2 : 0 ≤ p.psaAdditional) (hd : 0 ≤ p.dividendAllowance) :
    (charged p r l t t t).tax p = p.basicRate * overlap 0 t 0 l.brl + p.higherRate * overlap 0 t l.brl l.hrl
      + p.additionalRate * above 0 t l.hrl := by
  have hpsa := savingsAllowance_nonneg p r l t t t h0 h1 h2
  unfold charged Charged.tax
  simp only []
  generalize savingsAllowance p r l t t t = psa at hpsa ⊢
  have e1 : overlap (max t (gbp p.startingRateLimitSavings) + min (pos (t - max t (gbp p.startingRateLimitSavings))) psa) t 0 l.brl = 0 := by
    unfold overlap pos; omega
  have e2 : overlap (max t (gbp p.startingRateLimitSavings) + min (pos (t - max t (gbp p.startingRateLimitSavings))) psa) t l.brl l.hrl = 0 := by
    unfold overlap pos; omega
  have e3 : above (max t (gbp p.startingRateLimitSavings) + min (pos (t - max t (gbp p.startingRateLimitSavings))) psa) t l.hrl = 0 := by
    unfold above pos; omega
  have e4 : overlap (t + min (pos (t - t)) (gbp p.dividendAllowance)) t 0 l.brl = 0 := by
    unfold overlap pos gbp; omega
  have e5 : overlap (t + min (pos (t - t)) (gbp p.dividendAllowance)) t l.brl l.hrl = 0 := by
    unfold overlap pos gbp; omega
  have e6 : above (t + min (pos (t - t)) (gbp p.dividendAllowance)) t l.hrl = 0 := by
    unfold above pos gbp; omega
  rw [e1, e2, e3, e4, e5, e6]
  simp only [Int.mul_zero, Int.add_zero]

/-! ## 2. The liability of an individual with non-savings income only (the bridge) -/

/-- Step 3 income (pence) of an individual whose only income is `N` pence of non-savings income. -/
def nsStep3 (p : Params) (N : Int) : Int := pos (N - gbp (personalAllowance p N))

/-- The Step 5 tax (ticks) on it. -/
def nsTax (p : Params) (N : Int) : Int :=
  p.basicRate * overlap 0 (nsStep3 p N) 0 (gbp p.basicRateLimit)
  + p.higherRate * overlap 0 (nsStep3 p N) (gbp p.basicRateLimit) (gbp p.higherRateLimit)
  + p.additionalRate * above 0 (nsStep3 p N) (gbp p.higherRateLimit)

/-- An individual with non-savings income only, and no gifts, pension contributions or blindness. -/
structure NsOnly (x : Person) : Prop where
  i : x.interest = 0
  d : x.dividends = 0
  g : x.gains = 0
  ga : x.giftAid = 0
  ras : x.rasGross = 0
  cc : x.claimContrib = 0
  bl : x.blind = false
  sc : x.scottish = false

theorem relieved_zero (p : Params) (x : Person) (hc : x.claimContrib = 0) (hr : x.rasGross = 0) :
    relievedContributions p x = (0, 0) := by
  unfold relievedContributions
  split
  · rfl
  · simp only [hc, hr, Prod.mk.injEq]
    unfold Person.relevantEarnings pos; omega

theorem nsTax_nonneg (N : Int) : 0 ≤ nsTax p2025 N := by
  unfold nsTax
  exact Int.add_nonneg (Int.add_nonneg (Int.mul_nonneg (by decide) (overlap_nonneg ..))
    (Int.mul_nonneg (by decide) (overlap_nonneg ..))) (Int.mul_nonneg (by decide) (above_nonneg ..))

@[simp] theorem pos_zero : pos 0 = 0 := rfl
@[simp] theorem min_zero_pos (a : Int) : min 0 (pos a) = 0 := by unfold pos; omega

/-- **Bridge.** For an individual with non-savings income only (and no elections), under any reading, the model's
liability (Steps 1–7) is `nsTax` of that income. -/
theorem liability_nsOnly (r : Reading) (x : Person) (hx : NsOnly x) :
    (personCalc p2025 r x {}).liability = nsTax p2025 (pos x.nonSavings) := by
  unfold personCalc
  rw [relieved_zero p2025 x hx.cc hx.ras]
  simp only [Person.savings, Person.divs, hx.i, hx.d, hx.g, hx.ga, hx.bl, hx.sc, stepTax, gbp, Int.mul_zero, Int.add_zero,
    pos_zero, Int.sub_zero, min_zero_pos, Bool.false_eq_true, ite_false, Option.getD_none, Int.zero_add,
    decide_false, Bool.and_false, Bool.false_and, Int.lt_irrefl, ite_self, Bool.not_false, ite_true]
  rw [allocate_ns p2025 r _ _ _ _ _ (pos_nonneg _)]
  rw [charged_ns_tax p2025 r _ _ (by decide) (by decide) (by decide) (by decide)]
  have hT := nsTax_nonneg (pos x.nonSavings)
  unfold nsTax nsStep3 at hT ⊢
  have hN0 : 0 ≤ pos x.nonSavings := pos_nonneg _
  generalize pos x.nonSavings = N at *
  have hP0 : 0 ≤ personalAllowance p2025 N := by unfold personalAllowance; exact pos_nonneg _
  generalize personalAllowance p2025 N = P at *
  have ht : N - min (pos (min (100 * P) N)) N = pos (N - gbp P) := by unfold pos gbp; omega
  simp only [ht, gbp]
  generalize hX : p2025.basicRate * overlap 0 (pos (N - 100 * P)) 0 (100 * p2025.basicRateLimit) +
      p2025.higherRate * overlap 0 (pos (N - 100 * P)) (100 * p2025.basicRateLimit) (100 * p2025.higherRateLimit) +
      p2025.additionalRate * above 0 (pos (N - 100 * P)) (100 * p2025.higherRateLimit) = X at *
  have hX0 : 0 ≤ X := by rw [← hX]; unfold gbp at hT; exact hT
  have hcgt : pos (0 - 100 * p2025.cgtExemptAmount) = 0 := by decide
  rw [hcgt]
  simp only [show min 0 X = 0 by omega, Int.sub_zero, Int.zero_mul, Int.zero_sub]
  have hU : ∀ (b : Bool) (A B : Int), min 0 (if b = true then pos A else pos B) = 0 := by
    intro b A B; split <;> exact min_zero_pos _
  simp only [hU, ite_self, Int.mul_zero, Int.neg_zero, Int.add_zero]
  have h0 : pos (-X) = 0 := by unfold pos; omega
  simp only [h0, ite_self, Int.add_zero]

/-- Primary Class 1 (ticks) for wages `y` pounds below pensionable age, 2025-26 (8 % from £12,570 to £50,270, 2 %
above). -/
def class1Of (y : Int) : Int := 800 * overlap 0 (100 * y) 1257000 5027000 + 200 * above 0 (100 * y) 5027000

/-- Primary Class 1 contributions, as the model computes them (annual earnings period). -/
theorem class1_eq (r : Reading) (x : Person) (e : Elections) :
    (personCalc p2025 r x e).class1 = if x.age < 66 then class1Of (pos x.employment) else 0 := by
  unfold personCalc class1Of
  by_cases h : x.age < 66 <;> simp [h, p2025, gbp]

/-! ## 3. The closed form for 2025-26 -/

/-- Step 3 income (pence) for `N` pence of non-savings income, the 2025-26 numbers written out:
personal allowance £12,570 reduced by half the excess over £100,000, rounded up (s. 35). -/
def step3 (N : Int) : Int := pos (N - 100 * pos (-((-(2514000 - pos (N - 10000000))) / 200)))

/-- Tax on Step 3 income `t` at 20 / 40 / 45 % (limits £37,700 and £125,140), in ticks. -/
def bandTax (t : Int) : Int :=
  2000 * overlap 0 t 0 3770000 + 4000 * overlap 0 t 3770000 12514000 + 4500 * above 0 t 12514000

theorem nsTax_2025 (N : Int) : nsTax p2025 N = bandTax (step3 N) := rfl

theorem step3_mono (N N' : Int) (h : N ≤ N') : step3 N ≤ step3 N' := by
  unfold step3 pos; omega

theorem step3_le (N : Int) (h : 0 ≤ N) : 0 ≤ step3 N ∧ step3 N ≤ N := by
  unfold step3 pos; omega

theorem overlap0_mono (lo hi t t' : Int) (h : t ≤ t') : overlap 0 t lo hi ≤ overlap 0 t' lo hi := by
  unfold overlap pos; omega
theorem above0_mono (lo t t' : Int) (h : t ≤ t') : above 0 t lo ≤ above 0 t' lo := by
  unfold above pos; omega

theorem bandTax_mono (t t' : Int) (h : t ≤ t') : bandTax t ≤ bandTax t' := by
  unfold bandTax
  have h1 := Int.mul_le_mul_of_nonneg_left (overlap0_mono 0 3770000 t t' h) (show (0:Int) ≤ 2000 by decide)
  have h2 := Int.mul_le_mul_of_nonneg_left (overlap0_mono 3770000 12514000 t t' h) (show (0:Int) ≤ 4000 by decide)
  have h3 := Int.mul_le_mul_of_nonneg_left (above0_mono 12514000 t t' h) (show (0:Int) ≤ 4500 by decide)
  omega

/-- The three bands add up to the Step 3 income. -/
theorem bands_sum (t : Int) (h : 0 ≤ t) :
    overlap 0 t 0 3770000 + overlap 0 t 3770000 12514000 + above 0 t 12514000 = t := by
  unfold overlap above pos; omega

/-- Between two Step 3 incomes the tax rises by at most 45 % of the difference... -/
theorem bandTax_lip45 (t t' : Int) (h0 : 0 ≤ t) (h : t ≤ t') : bandTax t' - bandTax t ≤ 4500 * (t' - t) := by
  unfold bandTax
  have s := bands_sum t h0
  have s' := bands_sum t' (by omega)
  have m1 := overlap0_mono 0 3770000 t t' h
  have m2 := overlap0_mono 3770000 12514000 t t' h
  have m3 := above0_mono 12514000 t t' h
  generalize overlap 0 t 0 3770000 = a at *
  generalize overlap 0 t 3770000 12514000 = b at *
  generalize above 0 t 12514000 = c at *
  generalize overlap 0 t' 0 3770000 = a' at *
  generalize overlap 0 t' 3770000 12514000 = b' at *
  generalize above 0 t' 12514000 = c' at *
  omega

/-- ...and by at most 40 % of it when the higher Step 3 income is within the higher rate limit. -/
theorem bandTax_lip40 (t t' : Int) (h0 : 0 ≤ t) (h : t ≤ t') (hh : t' ≤ 12514000) :
    bandTax t' - bandTax t ≤ 4000 * (t' - t) := by
  have e : above 0 t 12514000 = 0 := by unfold above pos; omega
  have e' : above 0 t' 12514000 = 0 := by unfold above pos; omega
  unfold bandTax
  rw [e, e']
  have s := bands_sum t h0
  have s' := bands_sum t' (by omega)
  rw [e] at s; rw [e'] at s'
  have m1 := overlap0_mono 0 3770000 t t' h
  have m2 := overlap0_mono 3770000 12514000 t t' h
  generalize overlap 0 t 0 3770000 = a at *
  generalize overlap 0 t 3770000 12514000 = b at *
  generalize overlap 0 t' 0 3770000 = a' at *
  generalize overlap 0 t' 3770000 12514000 = b' at *
  omega

/-- In the higher-rate band the tax is a fixed amount plus 40 % of the Step 3 income above £37,700. -/
theorem bandTax_higher (t : Int) (h1 : 3770000 ≤ t) (h2 : t ≤ 12514000) :
    bandTax t = 2000 * 3770000 + 4000 * (t - 3770000) := by
  have e1 : overlap 0 t 0 3770000 = 3770000 := by unfold overlap pos; omega
  have e2 : overlap 0 t 3770000 12514000 = t - 3770000 := by unfold overlap pos; omega
  have e3 : above 0 t 12514000 = 0 := by unfold above pos; omega
  unfold bandTax; rw [e1, e2, e3]; omega

theorem bandTax_additional (t : Int) (h1 : 12514000 ≤ t) :
    bandTax t = 2000 * 3770000 + 4000 * (12514000 - 3770000) + 4500 * (t - 12514000) := by
  have e1 : overlap 0 t 0 3770000 = 3770000 := by unfold overlap pos; omega
  have e2 : overlap 0 t 3770000 12514000 = 12514000 - 3770000 := by unfold overlap pos; omega
  have e3 : above 0 t 12514000 = t - 12514000 := by unfold above pos; omega
  unfold bandTax; rw [e1, e2, e3]

/-! ## 4. Monotonicity -/

/-- **Income tax is non-decreasing in income** for every individual with non-savings income only. -/
theorem nsTax_mono (N N' : Int) (h : N ≤ N') : nsTax p2025 N ≤ nsTax p2025 N' := by
  rw [nsTax_2025, nsTax_2025]
  exact bandTax_mono _ _ (step3_mono N N' h)

/-- The same, stated on the model: two individuals with non-savings income only, the one with more pays no less. -/
theorem liability_mono_nsOnly (r : Reading) (x x' : Person) (hx : NsOnly x) (hx' : NsOnly x')
    (h : x.nonSavings ≤ x'.nonSavings) :
    (personCalc p2025 r x {}).liability ≤ (personCalc p2025 r x' {}).liability := by
  rw [liability_nsOnly r x hx, liability_nsOnly r x' hx']
  apply nsTax_mono
  unfold pos; omega

/-! ## 5. The personal allowance taper: the 60 % band, exactly -/

/-- **The 60 % band.** For income from £100,000 to £125,140, every £2 more costs exactly £1.20 of income tax (60 %):
£2 of income plus £1 of personal allowance lost, all at 40 %. In ticks (1/10 000 penny). -/
theorem taper_60 (y : Int) (h1 : 100000 ≤ y) (h2 : y + 2 ≤ 125140) :
    nsTax p2025 (100 * (y + 2)) - nsTax p2025 (100 * y) = 1200000 := by
  rw [nsTax_2025, nsTax_2025]
  have a1 : 3770000 ≤ step3 (100 * y) := by unfold step3 pos; omega
  have a2 : step3 (100 * (y + 2)) ≤ 12514000 := by unfold step3 pos; omega
  have a3 : step3 (100 * (y + 2)) = step3 (100 * y) + 300 := by unfold step3 pos; omega
  have e1 := bandTax_higher (step3 (100 * y)) a1 (by omega)
  have e2 := bandTax_higher (step3 (100 * (y + 2))) (by omega) a2
  rw [e1, e2, a3]
  omega

/-- Pound by pound the 60 % is 40 % and 80 % in turn: the allowance is "rounded up" to a whole pound (s. 35(3)), so
it falls by £1 on every second pound. -/
theorem taper_one_pound (y : Int) (h1 : 100000 ≤ y) (h2 : y + 1 ≤ 125140) :
    nsTax p2025 (100 * (y + 1)) - nsTax p2025 (100 * y) = 400000 ∨
    nsTax p2025 (100 * (y + 1)) - nsTax p2025 (100 * y) = 800000 := by
  rw [nsTax_2025, nsTax_2025]
  have a1 : 3770000 ≤ step3 (100 * y) := by unfold step3 pos; omega
  have a2 : step3 (100 * (y + 1)) ≤ 12514000 := by unfold step3 pos; omega
  have a3 : step3 (100 * (y + 1)) = step3 (100 * y) + 100 ∨ step3 (100 * (y + 1)) = step3 (100 * y) + 200 := by
    unfold step3 pos; omega
  have e1 := bandTax_higher (step3 (100 * y)) a1 (by omega)
  have e2 := bandTax_higher (step3 (100 * (y + 1))) (by omega) a2
  rw [e1, e2]
  omega

/-- Below the taper (£50,270 to £100,000) each £1 costs 40p. -/
theorem below_taper_40 (y : Int) (h1 : 50270 ≤ y) (h2 : y + 1 ≤ 100000) :
    nsTax p2025 (100 * (y + 1)) - nsTax p2025 (100 * y) = 400000 := by
  rw [nsTax_2025, nsTax_2025]
  have a1 : step3 (100 * y) = 100 * y - 1257000 := by unfold step3 pos; omega
  have a2 : step3 (100 * (y + 1)) = 100 * y - 1257000 + 100 := by unfold step3 pos; omega
  have e1 := bandTax_higher (step3 (100 * y)) (by omega) (by omega)
  have e2 := bandTax_higher (step3 (100 * (y + 1))) (by omega) (by omega)
  rw [e1, e2, a1, a2]
  omega

/-- From £125,140 (no allowance left) each £1 costs 45p. -/
theorem above_taper_45 (y : Int) (h1 : 125140 ≤ y) :
    nsTax p2025 (100 * (y + 1)) - nsTax p2025 (100 * y) = 450000 := by
  rw [nsTax_2025, nsTax_2025]
  have a1 : step3 (100 * y) = 100 * y := by unfold step3 pos; omega
  have a2 : step3 (100 * (y + 1)) = 100 * y + 100 := by unfold step3 pos; omega
  have e1 := bandTax_additional (step3 (100 * y)) (by omega)
  have e2 := bandTax_additional (step3 (100 * (y + 1))) (by omega)
  rw [e1, e2, a1, a2]
  omega

/-- **The band is exactly £100,000 to £125,140**: the £2 below it cost 80p (40 %), the £2 from £125,140 cost 90p
(45 %), and the allowance is £12,570 at £100,000 and nil at £125,140. -/
theorem taper_band_exact :
    nsTax p2025 (100 * 100000) - nsTax p2025 (100 * 99998) = 800000 ∧
    nsTax p2025 (100 * 125142) - nsTax p2025 (100 * 125140) = 900000 ∧
    personalAllowance p2025 (100 * 100000) = 12570 ∧ personalAllowance p2025 (100 * 125140) = 0 ∧
    personalAllowance p2025 (100 * 125138) = 1 := by
  refine ⟨?_, ?_, by decide, by decide, by decide⟩
  · have u := below_taper_40 99998 (by decide) (by decide)
    have v := below_taper_40 99999 (by decide) (by decide)
    simp only [show (99998 : Int) + 1 = 99999 by decide, show (99999 : Int) + 1 = 100000 by decide] at u v
    omega
  · have u := above_taper_45 125140 (by decide)
    have v := above_taper_45 125141 (by decide)
    simp only [show (125140 : Int) + 1 = 125141 by decide, show (125141 : Int) + 1 = 125142 by decide] at u v
    omega

/-- **s. 10(5A) is drafted so the additional rate starts where the allowance ends**: for any year whose higher rate
limit is the formula (twice the allowance plus the income limit), the allowance is nil at the higher rate limit and £1
two pounds below it. -/
theorem hrl_is_taper_end (p : Params) (h : p.hrlOverride = none) (hpa : 0 < p.personalAllowance) (_hl : 0 ≤ p.paIncomeLimit) :
    personalAllowance p (gbp p.higherRateLimit) = 0 ∧ personalAllowance p (gbp p.higherRateLimit - 200) = 1 := by
  unfold personalAllowance Params.higherRateLimit
  rw [h]
  simp only [Option.getD_none]
  unfold gbp pos ceilDiv
  constructor <;> omega

/-- **No notches for a wage earner**: each extra £1 of non-savings income adds between 0 and 80p of income tax, for
every income. (The 80p is the taper band's every second pound.) -/
theorem nsTax_step_le_80p (y : Int) (hy : 0 ≤ y) :
    0 ≤ nsTax p2025 (100 * (y + 1)) - nsTax p2025 (100 * y) ∧
    nsTax p2025 (100 * (y + 1)) - nsTax p2025 (100 * y) ≤ 800000 := by
  rw [nsTax_2025, nsTax_2025]
  have hm : step3 (100 * y) ≤ step3 (100 * (y + 1)) := step3_mono (100 * y) (100 * (y + 1)) (by omega)
  have m := bandTax_mono (step3 (100 * y)) (step3 (100 * (y + 1))) hm
  have h0 : 0 ≤ step3 (100 * y) := (step3_le (100 * y) (by omega)).1
  have d : step3 (100 * (y + 1)) - step3 (100 * y) ≤ 100 ∨
      (step3 (100 * (y + 1)) - step3 (100 * y) ≤ 200 ∧ step3 (100 * (y + 1)) ≤ 12514000) := by
    unfold step3 pos; omega
  have l45 := bandTax_lip45 (step3 (100 * y)) (step3 (100 * (y + 1))) h0 hm
  rcases d with d | ⟨d, dh⟩
  · generalize bandTax (step3 (100 * y)) = B at *
    generalize bandTax (step3 (100 * (y + 1))) = B2 at *
    constructor <;> omega
  · have l40 := bandTax_lip40 (step3 (100 * y)) (step3 (100 * (y + 1))) h0 hm dh
    generalize bandTax (step3 (100 * y)) = B at *
    generalize bandTax (step3 (100 * (y + 1))) = B2 at *
    constructor <;> omega

/-- **Income tax never exceeds 45 % of income** for an individual with non-savings income only. -/
theorem nsTax_le_45pct (N : Int) (h : 0 ≤ N) : nsTax p2025 N ≤ 4500 * N := by
  rw [nsTax_2025]
  have s := step3_le N h
  have l := bandTax_lip45 0 (step3 N) (Int.le_refl 0) s.1
  have e : bandTax 0 = 0 := by decide
  omega

/-! ## 6. With National Insurance: the combined marginal rate -/

theorem class1Of_step (y : Int) (h : 50270 ≤ y) : class1Of (y + 1) - class1Of y = 20000 := by
  have e1 : overlap 0 (100 * y) 1257000 5027000 = 3770000 := by unfold overlap pos; omega
  have e2 : overlap 0 (100 * (y + 1)) 1257000 5027000 = 3770000 := by unfold overlap pos; omega
  have e3 : above 0 (100 * y) 5027000 = 100 * y - 5027000 := by unfold above pos; omega
  have e4 : above 0 (100 * (y + 1)) 5027000 = 100 * y + 100 - 5027000 := by unfold above pos; omega
  unfold class1Of; rw [e1, e2, e3, e4]; omega

/-- **62 %**: in the taper band an employee's income tax and Class 1 together take £1.24 of every £2. -/
theorem taper_62_with_ni (y : Int) (h1 : 100000 ≤ y) (h2 : y + 2 ≤ 125140) :
    (nsTax p2025 (100 * (y + 2)) + class1Of (y + 2)) - (nsTax p2025 (100 * y) + class1Of y) = 1240000 := by
  have t := taper_60 y h1 h2
  have c1 := class1Of_step y (by omega)
  have c2 := class1Of_step (y + 1) (by omega)
  rw [show y + 1 + 1 = y + 2 by omega] at c2
  omega

/-- Below the taper an employee above the upper earnings limit pays 42 % (40 + 2), above it 47 % (45 + 2). -/
theorem combined_42_47 (y : Int) :
    (50270 ≤ y → y + 1 ≤ 100000 →
      (nsTax p2025 (100 * (y + 1)) + class1Of (y + 1)) - (nsTax p2025 (100 * y) + class1Of y) = 420000) ∧
    (125140 ≤ y →
      (nsTax p2025 (100 * (y + 1)) + class1Of (y + 1)) - (nsTax p2025 (100 * y) + class1Of y) = 470000) := by
  constructor
  · intro h1 h2; have := below_taper_40 y h1 h2; have := class1Of_step y h1; omega
  · intro h1; have := above_taper_45 y h1; have := class1Of_step y (by omega); omega

/-! ## 7. The high income child benefit charge -/

theorem hicbc_le_cb (a cb : Int) (hcb : 0 ≤ cb) : hicbc p2025 a cb ≤ cb := by
  unfold hicbc
  split
  · omega
  · simp only [p2025, gbp]
    have hq : 0 ≤ cb / 100 := Int.ediv_nonneg hcb (by decide)
    have hc : cb / 100 * 100 ≤ cb := Int.ediv_mul_le cb (by decide)
    generalize cb / 100 = C at *
    have hm : min 100 ((a - 100 * 60000) / (100 * 200)) * C ≤ 100 * C :=
      Int.mul_le_mul_of_nonneg_right (Int.min_le_left _ _) hq
    have := Int.ediv_le_ediv (show (0:Int) < 100 by decide) hm
    have e : 100 * C / 100 = C := by omega
    omega

/-- The charge never falls as adjusted net income rises. -/
theorem hicbc_mono (a a' cb : Int) (hcb : 0 ≤ cb) (h : a ≤ a') : hicbc p2025 a cb ≤ hicbc p2025 a' cb := by
  unfold hicbc
  have hq : 0 ≤ cb / 100 := Int.ediv_nonneg hcb (by decide)
  generalize cb / 100 = C at *
  simp only [p2025, gbp]
  by_cases ha : a ≤ 100 * 60000 <;> by_cases ha' : a' ≤ 100 * 60000 <;> simp only [ha, ha', if_true, if_false]
  · omega
  · have : 0 ≤ min 100 ((a' - 100 * 60000) / (100 * 200)) := by omega
    have := Int.mul_nonneg this hq
    have := Int.ediv_nonneg this (show (0:Int) ≤ 100 by decide)
    omega
  · omega
  · have hp : min 100 ((a - 100 * 60000) / (100 * 200)) ≤ min 100 ((a' - 100 * 60000) / (100 * 200)) := by
      have := Int.ediv_le_ediv (show (0:Int) < 100 * 200 by decide) (show a - 100 * 60000 ≤ a' - 100 * 60000 by omega)
      omega
    have := Int.mul_le_mul_of_nonneg_right hp hq
    have := Int.ediv_le_ediv (show (0:Int) < 100 by decide) this
    omega

/-- Child benefit for 2025-26 by number of children (pence): 52 weeks × (£26.05 + £17.25 × (k − 1)). -/
theorem child_benefit_k :
    childBenefit p2025 [5] = 135460 ∧ childBenefit p2025 [5, 3] = 225160 ∧
    childBenefit p2025 [5, 3, 1] = 314860 ∧ childBenefit p2025 [5, 3, 1, 0] = 404560 := by decide

/-- The charge (pounds) at adjusted net income £60,000 + £200 j, for child benefit `cb` (pence). -/
def hicbcAt (cb : Int) (j : Nat) : Int := hicbc p2025 (100 * (60000 + 200 * (j : Int))) cb / 100

/-- **Each £200 step of the charge.** Across £60,000–£80,000 the charge rises at each £200 by ⌊C/100⌋ or that plus £1,
C being child benefit in whole pounds: £13 or £14 for one child, £22 or £23 for two, £31 or £32 for three, £40 or
£41 for four; and the hundredth step completes the whole child benefit. -/
theorem hicbc_steps :
    (∀ j : Fin 100, hicbcAt 135460 (j + 1) - hicbcAt 135460 j ∈ [13, 14]) ∧
    (∀ j : Fin 100, hicbcAt 225160 (j + 1) - hicbcAt 225160 j ∈ [22, 23]) ∧
    (∀ j : Fin 100, hicbcAt 314860 (j + 1) - hicbcAt 314860 j ∈ [31, 32]) ∧
    (∀ j : Fin 100, hicbcAt 404560 (j + 1) - hicbcAt 404560 j ∈ [40, 41]) ∧
    hicbcAt 135460 100 = 1354 ∧ hicbcAt 404560 100 = 4045 ∧ hicbcAt 404560 0 = 0 := by
  decide

/-- The largest step is reached: £14, £23, £32 and £41 each occur. -/
theorem hicbc_max_steps :
    (∃ j : Fin 100, hicbcAt 135460 (j + 1) - hicbcAt 135460 j = 14) ∧
    (∃ j : Fin 100, hicbcAt 225160 (j + 1) - hicbcAt 225160 j = 23) ∧
    (∃ j : Fin 100, hicbcAt 314860 (j + 1) - hicbcAt 314860 j = 32) ∧
    (∃ j : Fin 100, hicbcAt 404560 (j + 1) - hicbcAt 404560 j = 41) := by
  decide

/-- Income tax and Class 1 over any £200 inside £60,000–£80,000: £84 (40 % + 2 %). -/
theorem it_ni_200_in_hicbc_band (y : Int) (h1 : 60000 ≤ y) (h2 : y + 200 ≤ 80000) :
    (nsTax p2025 (100 * (y + 200)) + class1Of (y + 200)) - (nsTax p2025 (100 * y) + class1Of y) = 84000000 := by
  rw [nsTax_2025, nsTax_2025]
  have a1 : step3 (100 * y) = 100 * y - 1257000 := by unfold step3 pos; omega
  have a2 : step3 (100 * (y + 200)) = 100 * y - 1257000 + 20000 := by unfold step3 pos; omega
  have b1 := bandTax_higher (step3 (100 * y)) (by omega) (by omega)
  have b2 := bandTax_higher (step3 (100 * (y + 200))) (by omega) (by omega)
  have e1 : overlap 0 (100 * y) 1257000 5027000 = 3770000 := by unfold overlap pos; omega
  have e2 : overlap 0 (100 * (y + 200)) 1257000 5027000 = 3770000 := by unfold overlap pos; omega
  have e3 : above 0 (100 * y) 5027000 = 100 * y - 5027000 := by unfold above pos; omega
  have e4 : above 0 (100 * (y + 200)) 5027000 = 100 * y + 20000 - 5027000 := by unfold above pos; omega
  unfold class1Of; rw [b1, b2, a1, a2, e1, e2, e3, e4]; omega

/-- **The highest marginal rate an employee family faces, averaged over £200** (income tax + Class 1 + HICBC on
the earner's wages, no other income): in the taper band £124 per £200 (62 %); in the HICBC band at most £84 + the
largest charge step: £98 (49 %) with one child, £107 (53.5 %) with two, £116 (58 %) with three, **£125 (62.5 %) with
four** — above the taper band. Stated: the taper band's £200 steps cost £124 and the HICBC band's largest step for
four children costs £125. -/
theorem highest_marginal_four_children (y : Int) (h1 : 100000 ≤ y) (h2 : y + 200 ≤ 125140) :
    (nsTax p2025 (100 * (y + 200)) + class1Of (y + 200)) - (nsTax p2025 (100 * y) + class1Of y) = 124000000 ∧
    ∃ j : Fin 100, 84 + (hicbcAt 404560 (j + 1) - hicbcAt 404560 j) = 125 := by
  refine ⟨?_, ?_⟩
  · rw [nsTax_2025, nsTax_2025]
    have a1 : 3770000 ≤ step3 (100 * y) := by unfold step3 pos; omega
    have a2 : step3 (100 * (y + 200)) ≤ 12514000 := by unfold step3 pos; omega
    have a3 : step3 (100 * (y + 200)) = step3 (100 * y) + 30000 := by unfold step3 pos; omega
    have b1 := bandTax_higher (step3 (100 * y)) a1 (by omega)
    have b2 := bandTax_higher (step3 (100 * (y + 200))) (by omega) a2
    have e1 : overlap 0 (100 * y) 1257000 5027000 = 3770000 := by unfold overlap pos; omega
    have e2 : overlap 0 (100 * (y + 200)) 1257000 5027000 = 3770000 := by unfold overlap pos; omega
    have e3 : above 0 (100 * y) 5027000 = 100 * y - 5027000 := by unfold above pos; omega
    have e4 : above 0 (100 * (y + 200)) 5027000 = 100 * y + 20000 - 5027000 := by unfold above pos; omega
    unfold class1Of; rw [b1, b2, a3, e1, e2, e3, e4]; omega
  · obtain ⟨j, hj⟩ := hicbc_max_steps.2.2.2
    exact ⟨j, by omega⟩

/-- **The £1 notch of the charge**: one child, adjusted net income £60,199 → £60,200: the charge goes from nil to £13
(0 % → 1 % of £1,354). With four children the step at £79,999 → £80,000 is £41. -/
theorem hicbc_notches :
    hicbc p2025 (100 * 60199) 135460 = 0 ∧ hicbc p2025 (100 * 60200) 135460 = 1300 ∧
    hicbc p2025 (100 * 79999) 404560 - hicbc p2025 (100 * 79998) 404560 = 0 ∧
    hicbc p2025 (100 * 80000) 404560 - hicbc p2025 (100 * 79999) 404560 = 4100 := by
  decide

/-! ## 8. Tax never exceeds income — and when it does -/

/-- **An employee's income tax, Class 1 and child benefit charge never exceed the wages**, for any wages and up to
30 children (pence; HICBC on the employee's own adjusted net income). -/
theorem burden_le_wages (y : Int) (hy : 0 ≤ y) (cb : Int) (hcb0 : 0 ≤ cb) (hcb : cb ≤ 2800000) :
    nsTax p2025 (100 * y) / 10000 + class1Of y / 10000 + hicbc p2025 (100 * y) cb ≤ 100 * y := by
  have t1 := nsTax_le_45pct (100 * y) (by omega)
  have t2 : class1Of y ≤ 800 * (100 * y) := by
    unfold class1Of overlap above pos; omega
  have t3 := hicbc_le_cb (100 * y) cb hcb0
  have t4 : hicbc p2025 (100 * y) cb = 0 ∨ 6000000 < 100 * y := by
    unfold hicbc; split
    · left; rfl
    · right; simp only [p2025, gbp] at *; omega
  rcases t4 with t4 | t4 <;> omega

/-- 30 children's child benefit is within that bound (52 × (26.05 + 29 × 17.25) = £27,367.60). -/
theorem cb_30_children : childBenefit p2025 (List.replicate 30 3) = 2736760 := by decide

set_option maxRecDepth 100000

/-- **But the Gift Aid charge can exceed income** (s. 424): someone with no income who gives £800 under Gift Aid
(£1,000 gross, £200 "treated as deducted") is charged £200. -/
theorem giftaid_charge_exceeds_income :
    (personCalc p2025 Reading.hmrc { giftAid := 800 } {}).totalIncome = 0 ∧
    ticksToPence (personCalc p2025 Reading.hmrc { giftAid := 800 } {}).liability = 20000 := by
  decide

/-! ## 9. Cliffs and notches (where net income falls as gross income rises) -/

/-- **The savings allowance cliff** (s. 12B): £1,000 of interest, wages £49,270 → £49,271. Step 3 income goes over
the basic rate limit (£37,700); the allowance falls from £1,000 to £500; £1 more of wages costs £100.20 of tax. -/
theorem psa_cliff :
    ticksToPence (personCalc p2025 Reading.hmrc { employment := 49271, interest := 1000 } {}).liability
    - ticksToPence (personCalc p2025 Reading.hmrc { employment := 49270, interest := 1000 } {}).liability = 10020 := by
  decide

/-- **The savings allowance cliff at the additional rate**: £1,000 of interest, wages £124,140 → £124,141 (no personal
allowance left): the allowance falls from £500 to nil; £1 more costs £200.45. -/
theorem psa_cliff_additional :
    ticksToPence (personCalc p2025 Reading.hmrc { employment := 124141, interest := 1000 } {}).liability
    - ticksToPence (personCalc p2025 Reading.hmrc { employment := 124140, interest := 1000 } {}).liability = 20045 := by
  decide

/-- **The marriage allowance cliff** (s. 55B(2)(b)): a married couple, one with no income; the other earns £50,270
(basic-rate taxpayer: £252 off) or £50,271 (one pound charged at the higher rate: no allowance). The couple's income
tax rises by £252.40 for £1. -/
theorem ma_cliff :
    ((householdCalc p2025 Reading.hmrc
        { adults := [{ wages := 50271 }, { wages := 0 }], married := true }).incomeTax)
    - ((householdCalc p2025 Reading.hmrc
        { adults := [{ wages := 50270 }, { wages := 0 }], married := true }).incomeTax) = 25240 := by
  decide

/-! ## 10. Findings as theorems -/

/-- **F1 (ITA 2007 s. 12B(8))**: wages £45,000 and interest £10,000. Only savings lie above the basic rate limit
(s. 25(2) puts the allowance against savings so that non-savings income fills the basic band exactly). HMRC's
reading: a higher-rate taxpayer, savings allowance £500, tax £9,232. The words ("charged at the higher rate, default
higher rate or dividend upper rate" — not the savings higher rate): allowance £1,000, tax £9,032. -/
theorem f1_psa_literal :
    ticksToPence (personCalc p2025 Reading.hmrc { employment := 45000, interest := 10000 } {}).liability = 923200 ∧
    (personCalc p2025 Reading.hmrc { employment := 45000, interest := 10000 } {}).ch.psa = 50000 ∧
    ticksToPence (personCalc p2025 { psaLiteral := true } { employment := 45000, interest := 10000 } {}).liability
      = 903200 ∧
    (personCalc p2025 { psaLiteral := true } { employment := 45000, interest := 10000 } {}).ch.psa = 100000 := by
  decide

/-- **F2 (FA 2004 s. 192(4))**: wages £50,000, dividends £10,000, a £10,000 gross pension contribution. HMRC's
reading: the bands are extended and the dividends stay in the basic band: £8,317.25. The words (only "income tax at
the higher rate or the additional rate" triggers the extension; the s. 25(2) search keeps the non-savings income
within the basic band, so only dividends are above it): no extension, £10,655.12. -/
theorem f2_ras_literal :
    ticksToPence (personCalc p2025 Reading.hmrc { employment := 50000, dividends := 10000, rasGross := 10000 } {}).liability
      = 831725 ∧
    ticksToPence (personCalc p2025 { ras := .mainRatesOnly } { employment := 50000, dividends := 10000, rasGross := 10000 } {}).liability
      = 1065512 := by
  decide

/-- **Under the literal s. 192(4) income tax is not monotone**: with £37,700 of Step 3 non-savings income,
£10,000 of dividends and a £10,000 contribution, £1 more of wages makes the non-savings income reach the higher rate,
the extension switches on, and the tax falls from £10,746.25 to £8,371.70. -/
theorem f2_literal_not_monotone :
    ticksToPence (personCalc p2025 { ras := .mainRatesOnly } { employment := 50271, dividends := 10000, rasGross := 10000 } {}).liability
    < ticksToPence (personCalc p2025 { ras := .mainRatesOnly } { employment := 50270, dividends := 10000, rasGross := 10000 } {}).liability := by
  decide

/-- **F2b: the s. 192(4) condition is a cliff even on the generous reading.** Wages £50,270 (Step 3 income exactly
the basic rate limit), gains £30,000, a £10,000 gross contribution. No income is charged at a higher rate, so the
bands are not extended and all £27,000 of taxable gains bear 24 %. One more pound of wages is charged at the higher
rate "apart from this section", the bands extend by £10,000 at once, £9,999 of gains fall to 18 %: income tax and CGT
together fall by £599.74. Extending unconditionally (CG21204's wording; PolicyEngine) there is no cliff: the extra
pound costs 20p of income tax and 6p of CGT. -/
theorem f2b_condition_cliff :
    let a := personCalc p2025 Reading.hmrc { employment := 50270, gains := 30000, rasGross := 10000 } {}
    let b := personCalc p2025 Reading.hmrc { employment := 50271, gains := 30000, rasGross := 10000 } {}
    let a' := personCalc p2025 { ras := .unconditional } { employment := 50270, gains := 30000, rasGross := 10000 } {}
    let b' := personCalc p2025 { ras := .unconditional } { employment := 50271, gains := 30000, rasGross := 10000 } {}
    ticksToPence (b.liability + b.cgt) - ticksToPence (a.liability + a.cgt) = -59974 ∧
    ticksToPence (b'.liability + b'.cgt) - ticksToPence (a'.liability + a'.cgt) = 26 := by
  decide

/-- **s. 25(2) matters**: interest £5,000 and dividends £20,000. Setting the personal allowance against the dividends
keeps all the interest in the starting rate band: tax £606.37; the usual order (allowance against savings first) would
charge £1,043.87. -/
theorem s25_allowance_against_dividends :
    ticksToPence (personCalc p2025 Reading.hmrc { interest := 5000, dividends := 20000 } {}).liability = 60637 ∧
    ticksToPence ((charged p2025 Reading.hmrc { brl := 3770000, hrl := 12514000 } 0 0 1243000).tax p2025) = 104387 := by
  decide

/-- **F3 (marriage allowance, s. 55B–55C)**: transferor with wages £1,603 and dividends £12,219, recipient wages
£6,155 and dividends £12,218 (household `mixed-144`). Transferring the full £1,260 costs the transferor £110.25
(at 8.75 %) and saves the recipient £252: the couple saves £141.75. The statute allows the election (no income test
for a UK resident, s. 55C(2) applies only under s. 56(3)); PolicyEngine's unused-allowance rule gives nothing. -/
theorem f3_ma_full_transfer :
    ((householdCalc p2025 Reading.hmrc
        { adults := [{ wages := 1603 }, { wages := 6155 }], married := true, dividends := 24437 }).incomeTax) = 38806 ∧
    ((householdCalc p2025 { peMaUnused := true }
        { adults := [{ wages := 1603 }, { wages := 6155 }], married := true, dividends := 24437 }).incomeTax) = 52981 := by
  decide

/-- **F6 (HMRC's rates table)**: the statute charges the pound between £125,140 and £125,141 at the additional rate
(s. 10(3A): "above the higher rate limit"); HMRC's table has the higher rate ending at "£125,140" and the additional
rate starting "Over £125,141". -/
theorem f6_pound_125141 : bandTax 12514100 - bandTax 12514000 = 450000 := by decide

/-- **Class 4 annual maximum (S.I. 2001/1004 reg. 100)**: an earner with wages £30,000 and profits £40,000 pays
£1,127 of Class 4 instead of £1,645.80; there, £3 more of wages adds 24p of Class 1 and takes 16p off Class 4 — a
marginal rate of 2 2/3 % on wages. -/
theorem reg100_cap :
    ticksToPence (personCalc p2025 Reading.hmrc { employment := 30000, trading := 40000 } {}).class4 = 112700 ∧
    ticksToPence ((personCalc p2025 Reading.hmrc { employment := 30003, trading := 40000 } {}).class1
      + (personCalc p2025 Reading.hmrc { employment := 30003, trading := 40000 } {}).class4)
    - ticksToPence ((personCalc p2025 Reading.hmrc { employment := 30000, trading := 40000 } {}).class1
      + (personCalc p2025 Reading.hmrc { employment := 30000, trading := 40000 } {}).class4) = 8 := by
  decide

/-- **Gains and income interact**: a basic-rate taxpayer with £30,000 of taxable gains (more than the unused basic
band): £1 more of wages costs 20p of income tax and moves £1 of gains from 18 % to 24 % (6p of CGT): 26 % in all. -/
theorem cgt_income_26 :
    let a := personCalc p2025 Reading.hmrc { employment := 30000, gains := 33000 } {}
    let b := personCalc p2025 Reading.hmrc { employment := 30001, gains := 33000 } {}
    ticksToPence (b.liability + b.cgt) - ticksToPence (a.liability + a.cgt) = 26 := by
  decide

/-! ## 11. Scottish taxpayers (ITA 2007 s. 11A; the 2025-26 Scottish rate resolution) -/

/-- An employee's income tax + Class 1 (pence) for wages `y`, Scottish or not. -/
def burdenPence (scottish : Bool) (y : Int) : Int :=
  let r := personCalc p2025 Reading.hmrc { employment := y, scottish } {}
  ticksToPence (r.liability + r.class1)

/-- **A Scottish taxpayer earning £50,000 pays £9,013.80** (£2,827 at 19 %, £12,094 at 20 %, £16,171 at 21 %, £6,338
at 42 %; HMRC's Scottish bands for 2025-26). -/
theorem scot_50000 :
    ticksToPence (personCalc p2025 Reading.hmrc { employment := 50000, scottish := true } {}).liability = 901380 := by
  decide

/-- **Marginal rates of income tax + Class 1, pence per £1 (the taper: per £2).** Scotland: 28 (basic), 29
(intermediate), **50 between £43,663 and £50,270** (Scottish higher rate 42 % while Class 1 is still 8 %), 44, 47
(advanced), **139 per £2 = 69.5 % in the taper band**, 50 at the top. Rest of the UK: 28, 28, 28, 42, 42, 124 per £2
(62 %), 47. -/
theorem scot_vs_ruk_marginal :
    [burdenPence true 20000 - burdenPence true 19999, burdenPence true 40001 - burdenPence true 40000,
     burdenPence true 45001 - burdenPence true 45000, burdenPence true 60001 - burdenPence true 60000,
     burdenPence true 80001 - burdenPence true 80000, burdenPence true 110002 - burdenPence true 110000,
     burdenPence true 130001 - burdenPence true 130000] = [28, 29, 50, 44, 47, 139, 50] ∧
    [burdenPence false 20000 - burdenPence false 19999, burdenPence false 40001 - burdenPence false 40000,
     burdenPence false 45001 - burdenPence false 45000, burdenPence false 60001 - burdenPence false 60000,
     burdenPence false 80001 - burdenPence false 80000, burdenPence false 110002 - burdenPence false 110000,
     burdenPence false 130001 - burdenPence false 130000] = [28, 28, 28, 42, 42, 124, 47] := by
  decide

end UkTax

#print axioms UkTax.liability_nsOnly
#print axioms UkTax.nsTax_mono
#print axioms UkTax.taper_60
#print axioms UkTax.nsTax_step_le_80p
#print axioms UkTax.hicbc_mono
#print axioms UkTax.burden_le_wages
#print axioms UkTax.ma_cliff
#print axioms UkTax.f2_literal_not_monotone
