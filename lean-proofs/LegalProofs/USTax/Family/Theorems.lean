import LegalProofs.USTax.Family.Driver

/-!
# What holds for every input: the kiddie tax and the trust

Facts about the rules in `Kiddie.lean` and `Trust.lean` that the search results rest on, proved for all amounts.
-/

namespace Legal.USTax.Family.Theorems
open Legal.USTax.Family TaxCode.Individual

/-! ## §1(g) -/

/-- §1(g)(1): the kiddie tax never lowers a child's tax below what the child's own rates give (line 18 is the larger
of lines 16 and 17). -/
theorem kiddie_ge_own (pf : Filing) (pti pcg : Int) (all : List ChildLine) (c : ChildLine) :
    C.regularTax .single c.ti c.cg ≤ kiddieTax pf pti pcg all c := by
  unfold kiddieTax
  split
  · exact Int.le_refl _
  · exact Int.le_max_right _ _

/-- §1(g)(4)(A)(i): earned income is never unearned income. Wages paid to a child do not enter the base that §1(g)
taxes at the parent's rate, whatever their amount. -/
theorem wages_not_unearned (h : Household) (w : Int) : unearnedIncome { h with wages := w } = unearnedIncome h := by
  simp [unearnedIncome, A.capitalGainLine]

/-- §1(g)(2)(A)(ii)(II): a child of 18, or a full-time student under 24, is outside §1(g) exactly when earned income
is more than half of support. The test compares two numbers and nothing else: it does not ask where the earned income
came from, what it was spent on, or how large the unearned income is. -/
theorem support_test (c : ChildFacts) (h18 : 18 ≤ c.age) (hs : c.age < 19 ∨ (c.student = true ∧ c.age < 24))
    (hp : c.parentAlive = true) (hj : c.joint = false) :
    c.subject = false ↔ c.support < 2 * c.earned := by
  have h1 : decide (c.age < 18) = false := by simp; omega
  have h2 : (decide (c.age < 19) || (c.student && decide (c.age < 24))) = true := by
    rcases hs with h | ⟨hst, h⟩ <;> simp [*]
  simp only [ChildFacts.subject, h1, h2, hp, hj, Bool.false_or, Bool.true_and, Bool.and_true, Bool.not_false]
  constructor
  · intro h; simp at h; omega
  · intro h; simp; omega

/-- Past the student years nothing of §1(g) is left: at 24, or at 19 when not a student, the child pays at the
child's own rates whatever the income. -/
theorem adult_outside (c : ChildFacts) (h : 24 ≤ c.age ∨ (19 ≤ c.age ∧ c.student = false)) : c.subject = false := by
  rcases h with h | ⟨h, hs⟩
  · simp [ChildFacts.subject]; omega
  · simp [ChildFacts.subject, hs]; omega

/-! ## The trust -/

/-- §§641, 661(a), 662(a): no income disappears. Whenever the trust keeps at least its $100 exemption of taxable
income, the trust's taxable income plus the taxable amounts the beneficiaries include is exactly the trust's gross
income less the exemption. Distributing moves income to another taxpayer; it never removes any. -/
theorem trust_conserves (g : Bool) (t : TrustIncome) (ds : List Int)
    (h : 100 ≤ t.interest + t.ordDiv + t.ltGain - ((ds.map fun d =>
      character g t (inclusion (dni g t) ds.sum d)).map Carry.taxable).sum) :
    (trustReturn g t ds).taxableIncome + (trustReturn g t ds).distributionDeduction
      = t.interest + t.ordDiv + t.ltGain - 100 := by
  simp only [trustReturn]
  omega

/-- §662(b): each beneficiary's inclusion is split into classes that add up to it exactly. -/
theorem character_total (g : Bool) (t : TrustIncome) (x : Int) (h : 0 < dni g t) :
    (character g t x).total = x := by
  simp only [character, Carry.total, Carry.taxable]
  have : ¬ dni g t ≤ 0 := by omega
  simp only [this, if_false]
  omega

/-- §662(a)(2): when distributions do not exceed DNI each beneficiary includes exactly what it was paid. -/
theorem inclusion_exact (D total d : Int) (h : total ≤ D) : inclusion D total d = d := by
  simp [inclusion, h]

/-- The trust's own §1 tax and §1411 tax are zero when its taxable income is zero and it keeps no net investment
income. -/
theorem trustTax_zero (g : Int) : trustTax 0 g = 0 := by
  have h : trustTaxCents 0 g = 0 := by
    simp only [trustTaxCents, trustScheduleCents]
    have e1 : max (0 : Int) 0 = 0 := by decide
    simp only [e1]
    have e2 : max 0 ((0 : Int) - max 0 g) = 0 := by omega
    have e3 : min (max 0 g) (0 : Int) = 0 := by omega
    simp only [e2, e3]
    split <;> decide
  simp [trustTax, h, roundDollar]

/-- **A trust that distributes everything pays nothing.** With gains allocated to income (in DNI) and no tax-exempt
interest, paying one beneficiary the whole of DNI carries all the income out: the trust's taxable income is zero and
its §1 and §1411 taxes are zero, for every amount of interest, dividends and gain. -/
theorem trust_all_out (t : TrustIncome) (he : t.taxExempt = 0) (hpos : 0 < dni true t) :
    (trustReturn true t [dni true t]).taxableIncome = 0 ∧ (trustReturn true t [dni true t]).total = 0 := by
  have hD : dni true t = t.interest + t.ordDiv + t.ltGain := by simp [dni, he]
  have hc : (character true t (dni true t)).taxable = t.interest + t.ordDiv + t.ltGain := by
    have := character_total true t (dni true t) hpos
    simp only [Carry.total] at this
    have hte : (character true t (dni true t)).taxExempt = 0 := by
      simp only [character]; have : ¬ dni true t ≤ 0 := by omega
      simp [this, he]
    omega
  have hti : (trustReturn true t [dni true t]).taxableIncome = 0 := by
    simp only [trustReturn, inclusion, List.sum_cons, List.sum_nil, List.map_cons, List.map_nil, Int.add_zero,
      Int.le_refl, if_true]
    omega
  refine ⟨hti, ?_⟩
  simp only [TrustReturn.total]
  have ht : ∃ x, (trustReturn true t [dni true t]).regularTax = trustTax (trustReturn true t [dni true t]).taxableIncome x :=
    ⟨_, rfl⟩
  obtain ⟨x, ht⟩ := ht
  rw [hti] at ht
  have hn : (trustReturn true t [dni true t]).niit = 0 := by
    simp only [trustReturn, inclusion, List.sum_cons, List.sum_nil, List.map_cons, List.map_nil, Int.add_zero,
      Int.le_refl, if_true, roundDollar]
    omega
  rw [ht, hn, trustTax_zero]; rfl

/-! ## Roth conversions, over every path of returns

An account's value after a path of yearly returns, each in basis points; kept exact by not dividing (the unit is
10000^years of a dollar). A traditional IRA balance `x` is either converted now at tax rate `tc` (basis points) or kept
and withdrawn at the end at rate `tw`. -/

def growPath : List Int → Int → Int
  | [], x => x
  | g :: gs, x => growPath gs (x * (10000 + g))

theorem growPath_mul (p : List Int) (a x : Int) : growPath p (a * x) = a * growPath p x := by
  induction p generalizing x with
  | nil => rfl
  | cons g gs ih => simp only [growPath]; rw [Int.mul_assoc, ih]

/-- **Converting is worth exactly the rate difference, on every path.** Paying the conversion tax out of the account,
the Roth ends with `(10000 − tc)/10000` of what the traditional IRA would have held; keeping it, the heirs net
`(10000 − tw)/10000` of the same amount. The difference is `(tw − tc)` times the grown balance: positive exactly when
the rate at conversion is below the rate at withdrawal, whatever the returns, including losses. -/
theorem conversion_rate_difference (p : List Int) (x tc tw : Int) :
    growPath p (x * (10000 - tc)) - growPath p x * (10000 - tw) = (tw - tc) * growPath p x := by
  rw [Int.mul_comm x, growPath_mul]
  rw [Int.mul_comm (growPath p x), ← Int.sub_mul]
  congr 1; omega

/-- **Paying the tax from outside the account is never worse.** Convert `x`, paying `x · tc` from a taxable account
whose after-tax growth factor `Q` is at most the sheltered factor `G` (every unit in 10000ths). Against keeping both,
the gain is at least `x · G · (tw − tc)`: the rate difference, plus the sheltering of the money used to pay the tax. -/
theorem conversion_outside (x tc tw G Q : Int) (hx : 0 ≤ x) (htc : 0 ≤ tc) (hQ : Q ≤ G) :
    x * G * (tw - tc) ≤ 10000 * (x * G) - (x * G * (10000 - tw) + x * tc * Q) := by
  have h1 : x * tc * Q ≤ x * tc * G := Int.mul_le_mul_of_nonneg_left hQ (Int.mul_nonneg hx htc)
  have e1 : x * G * (tw - tc) = x * G * tw - x * tc * G := by
    rw [Int.mul_sub]; congr 1; rw [Int.mul_assoc, Int.mul_assoc, Int.mul_comm G tc]
  have e2 : 10000 * (x * G) - (x * G * (10000 - tw) + x * tc * Q) = x * G * tw - x * tc * Q := by
    rw [Int.mul_sub]; rw [Int.mul_comm 10000 (x * G)]; omega
  rw [e1, e2]; omega

end Legal.USTax.Family.Theorems
