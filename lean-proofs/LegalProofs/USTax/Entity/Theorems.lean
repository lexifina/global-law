import LegalProofs.USTax.Entity.Driver

/-!
# What holds for every input: the entity rules the search results rest on

Facts about `Partnership.lean` and `Corp.lean`, proved for all amounts (no `sorry`, no `native_decide`).
-/

namespace Legal.USTax.Entity.Theorems
open Legal.USTax.Entity TaxCode.Individual

/-! ## §704(c): the methods move income between partners; they never create or destroy it -/

/-- Every method, every year: the partners' tax items add up to the partnership's tax income (other income less tax
depreciation). Curative and remedial allocations are zero-sum. -/
theorem yearAlloc_conserves (m : Method) (c : Contributed) (sC other : Int) (t : Nat) :
    (yearAlloc m c sC other t).cTax + (yearAlloc m c sC other t).nTax = other - taxDep c t := by
  simp only [yearAlloc]; omega

/-- On a sale, the partners' tax items add up to the tax gain plus the year's other income. -/
theorem saleAlloc_conserves (m : Method) (c : Contributed) (sC other : Int) (t : Nat) (price : Int) :
    (saleAlloc m c sC other t price).cTax + (saleAlloc m c sC other t price).nTax
      = (price - taxBasis c t) + other := by
  simp only [saleAlloc]; omega

/-- The remedial method removes every ceiling-rule distortion for the non-contributing partner: its tax items equal
its book items in every year (Reg. §1.704-3(d)(1)). -/
theorem remedial_matches_book (c : Contributed) (sC other : Int) (t : Nat) :
    (yearAlloc .remedial c sC other t).nTax = (yearAlloc .remedial c sC other t).nBook := by
  simp only [yearAlloc, cure]; omega

/-- Under the traditional method the non-contributing partner never gets more tax depreciation than book depreciation
(the ceiling rule): its tax income is at least its book income whenever book depreciation is non-negative. -/
theorem traditional_ceiling (c : Contributed) (sC other : Int) (t : Nat) (h : 0 ≤ taxDep c t) :
    (yearAlloc .traditional c sC other t).nBook ≤ (yearAlloc .traditional c sC other t).nTax := by
  simp only [yearAlloc, cure]; omega

/-! ## §1202 -/

theorem qsbsPct_le (n : Bool) (h : Nat) : qsbsPct n h ≤ 100 := by
  unfold qsbsPct; split <;> split <;> (try split) <;> (try split) <;> omega

theorem qsbsPct_nonneg (n : Bool) (h : Nat) : 0 ≤ qsbsPct n h := by
  unfold qsbsPct; split <;> split <;> (try split) <;> (try split) <;> omega

/-- §1202(a): nothing is excluded from new stock held less than 3 years. -/
theorem qsbs_under3 (s : QsbsSale) (hn : s.newStock = true) (h : s.heldYears < 3) : (qsbsSplit s).excluded = 0 := by
  have hp : qsbsPct s.newStock s.heldYears = 0 := by simp [qsbsPct, hn]; omega
  simp [qsbsSplit, hp]

/-- The arithmetic core: `p` percent (0 ≤ p ≤ 100) of a non-negative amount is at most the amount. -/
theorem pct_le (e p : Int) (he : 0 ≤ e) (h0 : 0 ≤ p) (h1 : p ≤ 100) : 0 ≤ e * p / 100 ∧ e * p / 100 ≤ e := by
  have hx : e * p ≤ e * 100 := Int.mul_le_mul_of_nonneg_left h1 he
  have hy : 0 ≤ e * p := Int.mul_nonneg he h0
  generalize e * p = x at *
  omega

/-- The exclusion never exceeds the gain, nor the per-issuer limit of §1202(b)(1). -/
theorem qsbs_excluded_le (s : QsbsSale) (hb : 0 ≤ s.basisSold) :
    (qsbsSplit s).excluded ≤ max 0 s.gain ∧
    (qsbsSplit s).excluded ≤ max (max 0 ((if s.newStock then 15000000 else 10000000) / (if s.separate then 2 else 1)
      - s.priorUsed)) (10 * s.basisSold) := by
  have h1 := qsbsPct_le s.newStock s.heldYears
  have h0 := qsbsPct_nonneg s.newStock s.heldYears
  by_cases hc : qsbsPct s.newStock s.heldYears = 0 ∨ s.gain ≤ 0
  · simp only [qsbsSplit, hc, if_true]; constructor <;> omega
  · simp only [qsbsSplit, hc, if_false]
    have hL0 : 0 ≤ max (max 0 ((if s.newStock then 15000000 else 10000000) / (if s.separate then 2 else 1)
      - s.priorUsed)) (10 * s.basisSold) := by omega
    generalize max (max 0 ((if s.newStock then 15000000 else 10000000) / (if s.separate then 2 else 1)
      - s.priorUsed)) (10 * s.basisSold) = L at *
    generalize qsbsPct s.newStock s.heldYears = p at *
    have := pct_le (min s.gain L) p (by omega) h0 h1
    constructor <;> omega

/-- Held 5 years, new stock, a gain within the taxpayer's remaining dollar limit or within 10 times the basis sold:
all of it is excluded. -/
theorem qsbs_all_excluded (s : QsbsSale) (hn : s.newStock = true) (h5 : 5 ≤ s.heldYears) (hs : s.separate = false)
    (hg : 0 < s.gain) (hlim : s.gain ≤ 15000000 - s.priorUsed ∨ s.gain ≤ 10 * s.basisSold) :
    (qsbsSplit s).excluded = s.gain ∧ (qsbsSplit s).g28 = 0 ∧ (qsbsSplit s).ltcg = 0 := by
  have hp : qsbsPct true s.heldYears = 100 := by simp [qsbsPct]; omega
  have hne : ¬ (qsbsPct true s.heldYears = 0 ∨ s.gain ≤ 0) := by omega
  have hm : min s.gain (max (max 0 (15000000 / 1 - s.priorUsed)) (10 * s.basisSold)) = s.gain := by omega
  have hc : s.gain * 100 / 100 = s.gain := Int.mul_ediv_cancel _ (by decide)
  have hg' : ¬ ((100 : Int) = 0 ∨ s.gain ≤ 0) := by omega
  simp only [qsbsSplit, hn, hs, if_true, Bool.false_eq_true, if_false, hp, hm, hc, hg']
  exact ⟨trivial, by omega, by omega⟩

/-- **Stacking.** Split a gain among `k` taxpayers who each hold the stock 5 years (a gift carries the holding period,
§1202(h)) and each have a fresh dollar limit: every one excludes its whole part as long as the part is at most
$15,000,000, so the family's exclusion grows with the number of taxpayers, without any limit in the statute. -/
theorem qsbs_stacking (sales : List QsbsSale)
    (h : ∀ s ∈ sales, s.newStock = true ∧ 5 ≤ s.heldYears ∧ s.separate = false ∧ 0 < s.gain ∧ s.gain ≤ 15000000 ∧
      s.priorUsed = 0) :
    (sales.map fun s => (qsbsSplit s).excluded).sum = (sales.map (·.gain)).sum := by
  induction sales with
  | nil => rfl
  | cons s rest ih =>
    simp only [List.map_cons, List.sum_cons]
    have ⟨hn, h5, hs, hg, hle, hp⟩ := h s (by simp)
    rw [(qsbs_all_excluded s hn h5 hs hg (Or.inl (by omega))).1, ih (fun x hx => h x (by simp [hx]))]

/-- **The 10-times-basis prong.** The §1202(i) basis of stock received for property is at least the property's value;
a gain up to 10 times that basis is excluded in full after 5 years, whatever the $15,000,000 limit has left. -/
theorem qsbs_tenx (s : QsbsSale) (hn : s.newStock = true) (h5 : 5 ≤ s.heldYears) (hs : s.separate = false)
    (hg : 0 < s.gain) (h10 : s.gain ≤ 10 * s.basisSold) : (qsbsSplit s).excluded = s.gain :=
  (qsbs_all_excluded s hn h5 hs hg (Or.inr h10)).1

/-! ## §1374 and §11 -/

/-- After the 5-year recognition period the built-in gains tax is zero, whatever the gain. -/
theorem bigTax_after (y : Nat) (r t n : Int) (h : 5 ≤ y) : bigTax y r t n = 0 := by
  simp [bigTax]; omega

theorem corpTax_nonneg (x : Int) : 0 ≤ corpTax x := by
  unfold corpTax; have : 0 ≤ max 0 x := Int.le_max_left 0 x; omega


/-! ## The payroll wedge between a proprietor and an S corporation's owner -/

/-- §§1401, 1402(a)(12), (b)(1): a proprietor with profit `P` of at least $200,000 (so net earnings exceed the 2025
wage base) and no wages pays 12.4 percent of $176,100 plus 2.9 percent of 92.35 percent of `P` (to the dollar). Every
dollar of profit above the base costs 2.678 cents, all of it Medicare tax. -/
theorem seTax_above_base (P : Int) (h : 200000 ≤ P) :
    TaxCode.Individual.A.seTaxCore P 0 = roundDollar (124 * 1761000000 + 29 * (P * 9235)) 10000000 := by
  simp only [TaxCode.Individual.A.seTaxCore, TaxCode.Individual.A.oasdiBase10k, TaxCode.Individual.A.seIncome10k,
    TaxCode.Individual.A.nese10k, TaxCode.Individual.A.wageBase2025]
  have h1 : ¬ (P * 9235 < 400 * 10000) := by omega
  simp only [h1, if_false]
  have h2 : min (P * 9235) (10000 * max 0 (176100 - 0)) = 1761000000 := by omega
  rw [h2]

/-- An S corporation's owner paid a wage `w` below the base pays (employee and employer together) 15.3 percent of `w`
in payroll tax (to the dollar each side) and none on the rest of the profit. -/
theorem fica_below_base (w : Int) (h0 : 0 ≤ w) (h : w ≤ 176100) :
    ficaEmployee w + ficaEmployer w = 2 * (w * 620 / 10000 + w * 145 / 10000) := by
  simp only [ficaEmployee, ficaEmployer, bps]
  have : min w 176100 = w := by omega
  rw [this]; omega

/-! ## The gift at a low value (the driver's estate-tax formula) -/

/-- The estate tax as `finish` computes it, before the gift-tax credit: 40 percent of the estate plus adjusted taxable
gifts above the two exclusions `X`. -/
def estateTaxOf (estate gifts X : Int) : Int := max 0 (estate + gifts - X) * 40 / 100

/-- Giving away a part of the business worth `v0` now that will be worth `vH ≥ v0` at death takes `vH` out of the
estate and adds only `v0` to the gifts added back (§2001(b)(1)(B): adjusted taxable gifts are taken at their value
when given). The estate tax never rises, and when the estate stays above the exclusions it falls by exactly 40 percent
of the growth `vH − v0` (up to a dollar of rounding), whatever the amounts. -/
theorem freeze_never_costs (E G X v0 vH : Int) (h : v0 ≤ vH) :
    estateTaxOf (E - vH) (G + v0) X ≤ estateTaxOf E G X := by
  unfold estateTaxOf; omega

theorem freeze_saves (E G X v0 vH : Int) (h : v0 ≤ vH) (hx : X ≤ E - vH + G + v0) :
    estateTaxOf E G X - estateTaxOf (E - vH) (G + v0) X ≥ (vH - v0) * 40 / 100 - 1 ∧
    estateTaxOf E G X - estateTaxOf (E - vH) (G + v0) X ≤ (vH - v0) * 40 / 100 + 1 := by
  unfold estateTaxOf; omega

end Legal.USTax.Entity.Theorems
