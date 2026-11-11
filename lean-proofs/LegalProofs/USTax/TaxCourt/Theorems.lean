import LegalProofs.USTax.TaxCourt.Case

/-!
# Theorems over all inputs, every year 2012–2024

Proved elsewhere and collected here by name:
* `rateSched_ok` — every printed bracket base in the nine revenue procedures is the exact tax at the row's start;
* `eic_max_consistent`, `eic_completed_consistent` — the printed EIC maxima and completed phase-outs agree with the
  percentages and amounts;
* `tieBreak_claims`, `tieBreak_parent`, `tieBreak_no_parent` — §152(c)(4) picks at most one claimant, always one who
  claims; exactly one, a parent, whenever a parent claims; exactly one whenever nobody is a parent;
* `determineStatus_allowed`, `married_separate_only` — filing status;
* `substantial_iff`, `substantial_iff_5pct`, `not_substantial_le_5000`, `substantial_mono` — §6662(d)(1);
* `accuracyPenalty_le` — the §6662 penalty is at most 20% of the underpayment;
* `lateFiling_le` — §6651(a)(1) is at most 25% (75% fraud) or the minimum;
* `earlyDistTax_no_exception`, `earlyDistTax_bounds` — §72(t);
* `seTaxY_eq_2025`, `seTaxY_mono` — SE tax;
* `eicTabY_rounded` — the year-generic EIC Table rule is the 2025 model's rule when it uses the rounded maximum.
-/

namespace Legal.USTax.TaxCourt.Theorems
open Legal.USTax.TaxCourt TaxCode.Individual

/-- The schedule's seven rates are the pre-TCJA ones or the §1(j) ones. -/
def oldRatesP (s : RateSched) : Prop :=
  s.r1 = 100 ∧ s.r2 = 150 ∧ s.r3 = 250 ∧ s.r4 = 280 ∧ s.r5 = 330 ∧ s.r6 = 350 ∧ s.r7 = 396
def tcjaRatesP (s : RateSched) : Prop :=
  s.r1 = 100 ∧ s.r2 = 120 ∧ s.r3 = 220 ∧ s.r4 = 240 ∧ s.r5 = 320 ∧ s.r6 = 350 ∧ s.r7 = 370
/-- 2012: six rates, the top one repeated in the seventh slot (`rates2012`). -/
def rates2012P (s : RateSched) : Prop :=
  s.r1 = 100 ∧ s.r2 = 150 ∧ s.r3 = 250 ∧ s.r4 = 280 ∧ s.r5 = 330 ∧ s.r6 = 350 ∧ s.r7 = 350
instance (s : RateSched) : Decidable (rates2012P s) := by unfold rates2012P; infer_instance
instance (s : RateSched) : Decidable (oldRatesP s) := by unfold oldRatesP; infer_instance
instance (s : RateSched) : Decidable (tcjaRatesP s) := by unfold tcjaRatesP; infer_instance

theorem rates_2012 : ∀ f ∈ filings, rates2012P (rateSched 2012 f) := by decide
theorem rates_old : ∀ y ∈ [2013, 2014, 2015, 2016, 2017], ∀ f ∈ filings, oldRatesP (rateSched y f) := by decide
theorem rates_tcja : ∀ y ∈ [2018, 2019, 2020, 2021, 2022, 2023, 2024], ∀ f ∈ filings, tcjaRatesP (rateSched y f) := by
  decide

set_option maxHeartbeats 4000000 in
/-- A well-formed schedule with either set of rates: one more dollar costs between 10 cents and the top rate. -/
theorem sched_step (s : RateSched) (hok : s.Ok) (hr : oldRatesP s ∨ tcjaRatesP s ∨ rates2012P s) (x : Int) (hx : 0 ≤ x) :
    s.r1 ≤ s.mills (x + 1) - s.mills x ∧ s.mills (x + 1) - s.mills x ≤ s.r7 := by
  unfold RateSched.Ok at hok
  unfold RateSched.mills
  rcases hr with ⟨h1, h2, h3, h4, h5, h6, h7⟩ | ⟨h1, h2, h3, h4, h5, h6, h7⟩ | ⟨h1, h2, h3, h4, h5, h6, h7⟩ <;>
    simp only [h1, h2, h3, h4, h5, h6, h7] at hok ⊢ <;> (repeat' split) <;> omega

/-- **One more dollar of taxable income costs at least 10 cents and at most the top rate** (35 cents in 2012, 39.6
cents 2013–2017, 37 cents from 2018), in exact mills, in every year and filing status. -/
theorem schedule_marginal (y : Nat) (hy : y ∈ years) (f : Filing) (x : Int) (hx : 0 ≤ x) :
    100 ≤ (rateSched y f).mills (x + 1) - (rateSched y f).mills x ∧
    (rateSched y f).mills (x + 1) - (rateSched y f).mills x ≤
      (if y ≤ 2012 then 350 else if y ≤ 2017 then 396 else 370) := by
  have hf : f ∈ filings := by cases f <;> decide
  have hok := rateSched_ok y hy f hf
  by_cases h12 : y ≤ 2012
  · have hy12 : y = 2012 := by simp [years] at hy; omega
    subst hy12
    have ho := rates_2012 f hf
    have := sched_step _ hok (Or.inr (Or.inr ho)) x hx
    simp only [rates2012P] at ho
    simp only [h12, ↓reduceIte]; omega
  by_cases h17 : y ≤ 2017
  · have ho := rates_old y (by simp [years] at hy; simp; omega) f hf
    have := sched_step _ hok (Or.inl ho) x hx
    simp only [oldRatesP] at ho
    simp only [h12, h17, ↓reduceIte]; omega
  · have ht := rates_tcja y (by simp [years] at hy; simp; omega) f hf
    have := sched_step _ hok (Or.inr (Or.inl ht)) x hx
    simp only [tcjaRatesP] at ht
    simp only [h12, h17, ↓reduceIte]; omega

/-- **The regular-tax schedule never falls as taxable income rises**, in any year, for any filing status. -/
theorem schedule_mono (y : Nat) (hy : y ∈ years) (f : Filing) (x : Int) (n : Nat) :
    (rateSched y f).mills x ≤ (rateSched y f).mills (x + n) := by
  induction n with
  | zero => simp
  | succ n ih =>
    have hz : (rateSched y f).mills x = 0 ∨ 0 ≤ x := by
      by_cases hx : x ≤ 0
      · left; unfold RateSched.mills; simp [hx]
      · right; omega
    by_cases hxn : 0 ≤ x + n
    · have := (schedule_marginal y hy f (x + n) hxn).1
      have e : x + ((n + 1 : Nat) : Int) = x + n + 1 := by omega
      rw [e]; omega
    · have h1 : (rateSched y f).mills x = 0 := by unfold RateSched.mills; simp; omega
      have h2 : (rateSched y f).mills (x + ((n + 1 : Nat) : Int)) = 0 := by unfold RateSched.mills; simp; omega
      omega

/-- The EIC Table rule never exceeds the maximum credit, given that the phase-out maximum `M` rounds to it. -/
theorem eicTabY_bounds (cp pp eia thr mx M co x : Int) (_hM : 0 ≤ M) (hmx : 0 ≤ mx) (hpp : 0 ≤ pp)
    (hMx : 2 * M + 10000 < 20000 * (mx + 1)) :
    0 ≤ eicTabY cp pp eia thr mx M co x ∧ eicTabY cp pp eia thr mx M co x ≤ mx := by
  unfold eicTabY
  split
  · omega
  · simp only
    split
    · omega
    · have hB := Int.mul_nonneg hpp (Int.le_max_left 0 (x / 50 * 50 + min (x / 50 * 50 + 50) co - 2 * thr))
      generalize cp * _ = A
      generalize pp * _ = B at hB
      omega

def eicBoundOk (p : Params) (k : Nat) : Bool :=
  let e := p.eic k
  let M := if p.eicUnroundedMax then e.cp * e.eia else 10000 * e.maxCredit
  0 ≤ M && 0 ≤ e.maxCredit && 0 ≤ e.pp && 2 * M + 10000 < 20000 * (e.maxCredit + 1)

theorem eicBound_years : ∀ y ∈ years, ∀ k ∈ [0, 1, 2, 3], eicBoundOk ((params? y).getD default) k = true := by
  decide

theorem Params.eic_ge3 (p : Params) (k : Nat) (h : 3 ≤ k) : p.eic k = p.eic 3 := by
  match k, h with
  | k + 3, _ => rfl

/-- **The EIC Table never gives more than the year's maximum credit, nor less than zero**, for any number of
children, any filing status and any income. -/
theorem eicTable_bounds (y : Nat) (hy : y ∈ years) (k : Nat) (j : Bool) (x : Int) :
    0 ≤ eicTableAmount ((params? y).getD default) k j x ∧
    eicTableAmount ((params? y).getD default) k j x ≤ (((params? y).getD default).eic k).maxCredit := by
  generalize hp : (params? y).getD default = p
  have hk : ∃ k' ∈ [0, 1, 2, 3], p.eic k = p.eic k' := by
    by_cases h : k < 3
    · exact ⟨k, by simp; omega, rfl⟩
    · exact ⟨3, by simp, Params.eic_ge3 p k (by omega)⟩
  obtain ⟨k', hk', he⟩ := hk
  have hb := eicBound_years y hy k' hk'
  rw [hp] at hb
  unfold eicTableAmount
  rw [he]
  unfold eicBoundOk at hb
  simp only [Bool.and_eq_true, decide_eq_true_eq] at hb
  exact eicTabY_bounds _ _ _ _ _ _ _ _ hb.1.1.1 hb.1.1.2 hb.1.2 hb.2

/-- **Outside 2021, a taxpayer with no qualifying child who is under 25 gets no EIC** (on a separate or unmarried
return); in 2021 the floor was 19 (§32(n)). -/
theorem eic_childless_under25 (p : Params) (f : EicFacts) (h21 : p.year ≠ 2021) (hage : f.taxpayerAge < 25)
    (hj : f.filing ≠ .mfj) : (eicAmount p f (0, 0)).1 = 0 := by
  unfold eicAmount childlessAgeOk
  have : (p.year == 2021) = false := by simp [h21]
  have hj' : (f.filing == .mfj) = false := by cases hf : f.filing <;> simp_all
  simp [this, hj', Nat.not_le.mpr hage]

/-- **A return recomputed on the facts as filed has no deficiency.** -/
theorem no_deficiency_on_same_facts (p : Params) (r : ReturnFacts) :
    deficiencyOf (computeReturn p r) (computeReturn p r).netTax = 0 := by
  unfold deficiencyOf; omega

end Legal.USTax.TaxCourt.Theorems
