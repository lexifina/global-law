import LegalProofs.USTax.Retirement.Rules

/-!
# What the retirement rules allow, proved for every sequence of moves

The four results:

1. **The income limit binds directly** (`direct_blocked`): above $165,000 no Roth IRA contribution of any size is
   allowed.
2. **A conservation law for pre-tax money** (`pretax_conservation`): across *any* sequence of moves, pre-tax money in
   the IRAs can only leave by being taxed or by being rolled into the 401(k). With no roll-in, every pre-tax dollar that
   leaves the IRAs is taxed, whatever the order, size or number of contributions and conversions (`no_escape`): the
   pro-rata rule cannot be split, timed or sequenced around.
3. **The income limit does not bind** (`income_limit_void`): for *every* income at which the Roth limit is zero, and
   every starting set of accounts, there is a sequence of permitted moves that puts $7,000 into the Roth at no tax, the
   same end as the contribution §408A(c)(3) forbids.
4. **The ceiling** (`roth_ceiling`): no sequence of moves, of any length, can put more than $77,000 a year of new
   after-tax money into Roth accounts for this person. The search finds a plan that reaches it.
-/

namespace Legal.USTax.Retirement

/-! ## Arithmetic of the pro-rata rule -/

theorem prorata_key (a b i : Nat) (ha : a ≤ i) (hb : b ≤ i) : (a + b - i) * i ≤ a * b := by
  obtain ⟨c, rfl⟩ := Nat.exists_eq_add_of_le ha
  by_cases h : b ≤ c
  · have : a + b - (a + c) = 0 := by omega
    rw [this, Nat.zero_mul]; exact Nat.zero_le _
  · obtain ⟨e, rfl⟩ := Nat.exists_eq_add_of_le (Nat.le_of_lt (Nat.lt_of_not_le h))
    have h1 : a + (c + e) - (a + c) = e := by omega
    have he : e ≤ a := by omega
    rw [h1, Nat.mul_add, Nat.mul_add, Nat.mul_comm e a]
    have : e * c ≤ a * c := Nat.mul_le_mul_right c he
    omega

/-- Converting `a` of an IRA worth `i` with basis `b` never treats more than the pre-tax part as taxable. -/
theorem taxable_le_pretax (a b i : Nat) (ha : a ≤ i) (hb : b ≤ i) : a - a * b / i ≤ i - b := by
  rcases Nat.eq_zero_or_pos i with h | hi
  · subst h; omega
  · have := (Nat.le_div_iff_mul_le hi).2 (prorata_key a b i ha hb); omega

/-- ... and never recovers more basis than there is. -/
theorem recovered_le_basis (a b i : Nat) (ha : a ≤ i) : a * b / i ≤ b := by
  rcases Nat.eq_zero_or_pos i with h | hi
  · subst h; simp
  · exact Nat.div_le_of_le_mul (Nat.mul_le_mul_right b ha)

/-- ... nor more than is converted. -/
theorem recovered_le_amount (a b i : Nat) (hb : b ≤ i) : a * b / i ≤ a := by
  rcases Nat.eq_zero_or_pos i with h | hi
  · subst h; simp
  · exact Nat.div_le_of_le_mul (by rw [Nat.mul_comm i a]; exact Nat.mul_le_mul_left a hb)

/-! ## 1. The limit, read alone -/

theorem direct_blocked (magi : Nat) (s : Acct) (a : Nat) (h : rothHi ≤ magi) : step magi s (.rothContrib a) = none := by
  have h1 : ¬ magi ≤ rothLo := by unfold rothLo; unfold rothHi at h; omega
  have : rothLimit magi = 0 := by simp [rothLimit, h1, h]
  simp only [step, this]; split <;> simp_all; omega

/-! ## 2. Conservation of pre-tax money -/

/-- The well-formedness every account keeps: basis never exceeds the IRA. -/
def WF (s : Acct) : Prop := s.basis ≤ s.ira

/-- The conserved quantity, as an equation between before and after: pre-tax money in the IRAs, plus what has been
taxed, plus the 401(k), changes only by what was deducted or deferred going in. -/
def Conserves (s s' : Acct) : Prop :=
  (s'.ira - s'.basis) + s'.taxed + s'.plan + s.deducted + s.deferrals =
    (s.ira - s.basis) + s.taxed + s.plan + s'.deducted + s'.deferrals ∧
  s.deducted ≤ s'.deducted ∧ s.taxed ≤ s'.taxed ∧ s.deferrals ≤ s'.deferrals

theorem step_conserves {magi : Nat} {s s' : Acct} {a : Act} (wf : WF s) (h : step magi s a = some s') :
    WF s' ∧ Conserves s s' := by
  unfold WF at *; unfold Conserves
  cases a with
  | rothContrib x => simp only [step] at h; split at h <;> simp_all; subst h; simp; omega
  | tradContrib x =>
    simp only [step] at h; split at h <;> simp_all
    subst h; simp
    have : min x (dedLimit magi - min (dedLimit magi) s.deducted) ≤ x := Nat.min_le_left _ _
    omega
  | convert x =>
    simp only [step] at h; split at h <;> simp_all
    subst h; simp
    have h1 := taxable_le_pretax x s.basis s.ira (by omega) wf
    have h2 := recovered_le_basis x s.basis s.ira (by omega)
    have h3 := recovered_le_amount x s.basis s.ira wf
    omega
  | rollIn x => simp only [step] at h; split at h <;> simp_all; subst h; simp; omega
  | defer x => simp only [step] at h; split at h <;> simp_all; subst h; simp; omega
  | afterTax x => simp only [step] at h; split at h <;> simp_all; subst h; simp; omega
  | inPlanRoth x => simp only [step] at h; split at h <;> simp_all; subst h; simp; omega

/-- **Conservation of pre-tax money**, for every sequence of moves of any length. -/
theorem pretax_conservation (magi : Nat) (acts : List Act) :
    ∀ s s', WF s → run magi s acts = some s' → WF s' ∧ Conserves s s' := by
  induction acts with
  | nil => intro s s' wf h; simp [run] at h; subst h; exact ⟨wf, by unfold Conserves; omega⟩
  | cons a as ih =>
    intro s s' wf h
    simp only [run] at h
    cases hs : step magi s a with
    | none => simp [hs] at h
    | some m =>
      simp [hs] at h
      obtain ⟨wm, cm⟩ := step_conserves wf hs
      obtain ⟨w', c'⟩ := ih m s' wm h
      refine ⟨w', ?_⟩; unfold Conserves at *; omega

/-- Moves that never touch the 401(k)'s pre-tax side. -/
def noPlanIn : Act → Bool
  | .rollIn _ | .defer _ => false
  | _ => true

theorem step_plan_fixed {magi : Nat} {s s' : Acct} {a : Act} (ha : noPlanIn a = true) (h : step magi s a = some s') :
    s'.plan = s.plan ∧ s'.deferrals = s.deferrals := by
  cases a <;> simp [noPlanIn] at ha <;> simp only [step] at h <;> split at h <;> simp_all <;> subst h <;> simp

theorem run_plan_fixed (magi : Nat) (acts : List Act) (ha : acts.all noPlanIn = true) :
    ∀ s s', run magi s acts = some s' → s'.plan = s.plan ∧ s'.deferrals = s.deferrals := by
  induction acts with
  | nil => intro s s' h; simp [run] at h; subst h; simp
  | cons a as ih =>
    intro s s' h; simp [List.all] at ha
    simp only [run] at h
    cases hs : step magi s a with
    | none => simp [hs] at h
    | some m =>
      simp [hs] at h
      have := step_plan_fixed ha.1 hs; have := ih (by simpa [List.all_eq_true] using ha.2) m s' h; omega

/-- **No escape from the pro-rata rule.** Without moving money into the 401(k), every pre-tax dollar that leaves the
IRAs is taxed, in every possible sequence of contributions and conversions: if the IRAs end empty, the amount taxed is
exactly the pre-tax money there was, plus whatever was deducted on the way in. -/
theorem no_escape (magi : Nat) (acts : List Act) (ha : acts.all noPlanIn = true) (s s' : Acct) (wf : WF s)
    (h : run magi s acts = some s') (empty : s'.ira = 0) :
    s'.taxed - s.taxed = (s.ira - s.basis) + (s'.deducted - s.deducted) := by
  obtain ⟨w', c⟩ := pretax_conservation magi acts s s' wf h
  have := run_plan_fixed magi acts ha s s' h
  unfold Conserves WF at *; omega

/-! ## 3. The income limit does not bind -/

/-- From any accounts, for any income at which neither a Roth contribution nor a deduction is allowed: roll the pre-tax
IRA money into the 401(k) (if there is any), contribute $7,000 to a traditional IRA, and convert all of it. -/
def plan (s : Acct) : List Act :=
  (if s.ira - s.basis = 0 then [] else [.rollIn (s.ira - s.basis)]) ++ [.tradContrib iraLimit, .convert (s.basis + iraLimit)]

/-- **The income limit is void in effect.** For every income above both phase-outs and every starting set of accounts
(with $7,000 of cash and no IRA contribution yet this year), the plan is permitted at every step and ends with the Roth
up by the whole basis plus $7,000, and **no** additional tax. -/
theorem income_limit_void (magi : Nat) (s : Acct) (hm : dedHi ≤ magi) (wf : WF s) (hc : iraLimit ≤ s.cash)
    (h0 : s.iraContrib = 0) :
    ∃ s', run magi s (plan s) = some s' ∧ s'.roth = s.roth + s.basis + iraLimit ∧ s'.taxed = s.taxed := by
  have h1 : ¬ magi ≤ dedLo := by unfold dedLo; unfold dedHi at hm; omega
  have hd : dedLimit magi = 0 := by simp [dedLimit, h1, hm]
  unfold WF at wf
  unfold plan
  by_cases hp : s.ira - s.basis = 0
  · have hi : s.ira = s.basis := by omega
    have hpos : 0 < s.basis + 7000 := by omega
    have hc' : 7000 ≤ s.cash := hc
    simp [run, step, hd, h0, iraLimit, hi, hc', Nat.mul_div_cancel _ hpos]; omega
  · have hpos : 0 < s.basis + 7000 := by omega
    have e : s.ira - (s.ira - s.basis) = s.basis := by omega
    have hp' : 0 < s.ira - s.basis := by omega
    have hc' : 7000 ≤ s.cash := hc
    simp [hp, hp', e, run, step, hd, h0, iraLimit, hc', Nat.mul_div_cancel _ hpos]; omega

/-! ## 4. The ceiling -/

/-- After-tax money: the Roth, IRA basis, and after-tax money in the plan. -/
def afterTaxMoney (s : Acct) : Nat := s.roth + s.basis + s.planAfterTax

/-- The year's limits are never exceeded, and after-tax money grows only by what goes in under a limit, or by tax. -/
def Bounded (s s' : Acct) : Prop :=
  afterTaxMoney s' + s.iraContrib + s.additions + s.taxed ≤ afterTaxMoney s + s'.iraContrib + s'.additions + s'.taxed ∧
  afterTaxMoney s' + s.iraContrib + s.additions + s.taxed ≥ afterTaxMoney s + s.iraContrib + s.additions + s.taxed ∧
  s'.iraContrib ≤ iraLimit ∧ s'.additions ≤ additionsLimit

theorem step_bounded {magi : Nat} {s s' : Acct} {a : Act} (wf : WF s) (hl : s.iraContrib ≤ iraLimit)
    (ha : s.additions ≤ additionsLimit) (h : step magi s a = some s') : Bounded s s' := by
  unfold Bounded afterTaxMoney; unfold WF at wf
  cases a with
  | convert x =>
    simp only [step] at h; split at h <;> simp_all; subst h; simp
    have := recovered_le_basis x s.basis s.ira (by omega)
    have := recovered_le_amount x s.basis s.ira wf; omega
  | tradContrib x =>
    simp only [step] at h; split at h <;> simp_all; subst h; simp
    have : min x (dedLimit magi - min (dedLimit magi) s.deducted) ≤ x := Nat.min_le_left _ _
    omega
  | _ => simp only [step] at h; split at h <;> simp_all <;> subst h <;> simp <;> omega

/-- **No plan does better.** For every sequence of moves in a year that starts with no contributions made, the gain in
the Roth, less any tax incurred, is at most $77,000 (the IRA limit plus the §415(c) limit) plus the after-tax money
already held in IRAs and the plan. -/
theorem roth_ceiling (magi : Nat) (acts : List Act) :
    ∀ s s', WF s → s.iraContrib ≤ iraLimit → s.additions ≤ additionsLimit → run magi s acts = some s' →
      s'.roth + s.iraContrib + s.additions + s.taxed ≤
        s.roth + s.basis + s.planAfterTax + iraLimit + additionsLimit + s'.taxed := by
  induction acts with
  | nil => intro s s' _ hl ha h; simp [run] at h; subst h; omega
  | cons a as ih =>
    intro s s' wf hl ha h
    simp only [run] at h
    cases hs : step magi s a with
    | none => simp [hs] at h
    | some m =>
      simp [hs] at h
      obtain ⟨b1, b2, b3, b4⟩ := step_bounded wf hl ha hs
      have wm := (step_conserves wf hs).1
      have := ih m s' wm b3 b4 h
      unfold afterTaxMoney at b1 b2
      have : s.taxed ≤ m.taxed := by
        have := (step_conserves wf hs).2; unfold Conserves at this
        cases a <;> simp only [step] at hs <;> split at hs <;> simp_all <;> subst hs <;> simp <;> omega
      omega

end Legal.USTax.Retirement
