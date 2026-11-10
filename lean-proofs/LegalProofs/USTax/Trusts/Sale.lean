import LegalProofs.USTax.Trusts.Rules

/-!
# Selling an asset to a trust, year by year

A grantor holds an appreciating asset. Each year it grows and pays a taxable yield. The grantor can keep it, or sell it
to a trust for a note at the applicable federal rate (interest only, principal due at the end). What happens next
depends only on the trust's two statuses from `Rules.lean`:

* **Income tax.** If the trust is the grantor's for income tax, the grantor and the trust are one taxpayer: the sale
  is not a sale and the interest is not income (Rev. Rul. 85-13), and the grantor pays the tax on the trust's yield.
  Otherwise the sale realises the gain (§1001), the trust takes a cost basis (§1012), the trust pays tax on its own
  yield, and the grantor pays tax on the interest.
* **Estate tax.** At death the estate holds the grantor's cash, the note, and, if the trust is in the estate, the
  trust's property net of the note. Property in the estate takes a basis equal to its value (§1014); property outside
  keeps its basis, so the heirs owe capital-gains tax when they sell.

One further move is allowed when the instrument gives someone a nonfiduciary power to substitute property (§675(4)(C)):
just before death, the grantor takes the asset back in exchange for cash of equal value.

All amounts are whole dollars (`Int`, since a grantor's cash can be borrowed). Rates are in basis points.
-/

namespace Legal.USTax.Trusts

structure Rates where
  afr : Int        -- interest on the note
  yieldTax : Int   -- tax on the yield, whoever pays it
  interestTax : Int -- tax on interest received
  gainTax : Int    -- capital-gains tax
  exclusion : Int  -- exclusion left at death
  deriving Repr

structure St where
  asset : Int      -- the asset's value, wherever it is held
  gCash : Int      -- the grantor's cash
  tCash : Int      -- the trust's cash
  note : Int       -- what the trust owes the grantor
  taxPaid : Int    -- income tax paid by anyone, so far
  deriving DecidableEq, Repr

/-- How the asset is held. `sold = false` is keeping it; otherwise `owner` is the trust's income-tax status. -/
structure Hold where
  sold : Bool
  owner : Bool
  deriving DecidableEq, Repr

def pct (x r : Int) : Int := x * r / 10000

/-- One year: the asset grows by `g` and yields `y` (basis points). -/
def year (R : Rates) (h : Hold) (gy : Int × Int) (s : St) : St :=
  let inc := pct s.asset gy.2
  let tax := pct inc R.yieldTax
  let grown := s.asset + pct s.asset gy.1
  if !h.sold then { s with asset := grown, gCash := s.gCash + inc - tax, taxPaid := s.taxPaid + tax }
  else
    let int := pct s.note R.afr
    if h.owner then
      -- one taxpayer: the grantor pays the tax on the trust's yield; the interest is a transfer within the taxpayer
      { s with asset := grown, gCash := s.gCash - tax + int, tCash := s.tCash + inc - int, taxPaid := s.taxPaid + tax }
    else
      let itax := pct int R.interestTax
      { s with asset := grown, gCash := s.gCash + int - itax, tCash := s.tCash + inc - tax - int,
               taxPaid := s.taxPaid + tax + itax }

def years (R : Rates) (h : Hold) : List (Int × Int) → St → St
  | [], s => s
  | gy :: rest, s => years R h rest (year R h gy s)

/-- The sale itself. -/
def sell (R : Rates) (h : Hold) (basis : Int) (s : St) : St :=
  if !h.sold then s
  else if h.owner then { s with note := s.asset }
  else let g := pct (s.asset - basis) R.gainTax
    { s with note := s.asset, gCash := s.gCash - g, taxPaid := s.taxPaid + g }

/-- Estate tax on an estate worth `e`: 40% above the exclusion (§2001(c)). -/
def estateTaxOn (R : Rates) (e : Int) : Int := if e ≤ R.exclusion then 0 else (e - R.exclusion) * 4000 / 10000

structure End where
  estate : Int
  estateTax : Int
  latentGain : Int   -- capital-gains tax the heirs owe on selling what they receive
  heirs : Int        -- what the heirs keep
  deriving DecidableEq, Repr

/-- Death. `inEst` is the trust's estate-tax status; `swap` is the substitution just before death. -/
def death (R : Rates) (h : Hold) (inEst swap : Bool) (basis : Int) (s : St) : End :=
  if !h.sold then
    let e := s.gCash + s.asset
    ⟨e, estateTaxOn R e, 0, e - estateTaxOn R e⟩
  else
    let trustBasis := if h.owner then basis else s.note  -- carryover, or the price paid
    -- the swap moves the asset into the grantor's hands and an equal amount of cash into the trust
    let (gAsset, tAsset) := if swap then (s.asset, 0) else (0, s.asset)
    let gCash := if swap then s.gCash - s.asset else s.gCash
    let tCash := if swap then s.tCash + s.asset else s.tCash
    let trustNet := tAsset + tCash - s.note
    let e := gCash + gAsset + s.note + (if inEst then trustNet else 0)
    let latent := if inEst || swap then 0 else pct (s.asset - trustBasis) R.gainTax
    let heirs := e - estateTaxOn R e + (if inEst then 0 else trustNet) - latent
    ⟨e, estateTaxOn R e, latent, heirs⟩

def outcome (R : Rates) (h : Hold) (inEst swap : Bool) (basis : Int) (path : List (Int × Int)) (s0 : St) : End :=
  death R h inEst swap basis (years R h path (sell R h basis s0))

/-! ## Theorems over every path of returns -/

/-- Keeping the asset, and selling it to a defective trust, side by side. -/
def Twin (k d : St) : Prop := k.asset = d.asset ∧ k.gCash = d.gCash + d.tCash ∧ k.taxPaid = d.taxPaid

theorem year_twin (R : Rates) (gy : Int × Int) (k d : St) (h : Twin k d) :
    Twin (year R ⟨false, false⟩ gy k) (year R ⟨true, true⟩ gy d) := by
  obtain ⟨ha, hc, ht⟩ := h
  simp only [year, Twin, Bool.not_false, Bool.not_true]
  rw [ha] at *; refine ⟨rfl, ?_, ?_⟩ <;> simp <;> omega

theorem years_twin (R : Rates) (path : List (Int × Int)) :
    ∀ k d, Twin k d → Twin (years R ⟨false, false⟩ path k) (years R ⟨true, true⟩ path d) := by
  induction path with
  | nil => intro k d h; exact h
  | cons gy rest ih => intro k d h; exact ih _ _ (year_twin R gy k d h)

/-- **The defective trust is income-tax neutral.** For every path of growth and yield, selling the asset to a trust
that is the grantor's for income tax leaves the family exactly as rich, after exactly the same income tax, as keeping
it: no gain on the sale, no tax on the interest, and the yield taxed once, to the grantor. -/
theorem defective_neutral (R : Rates) (basis : Int) (path : List (Int × Int)) (s0 : St) (h0 : s0.tCash = 0) :
    Twin (years R ⟨false, false⟩ path (sell R ⟨false, false⟩ basis s0)) (years R ⟨true, true⟩ path (sell R ⟨true, true⟩ basis s0)) :=
  years_twin R path _ _ (by simp [sell, Twin, h0])

/-- **Everything the trust gains leaves the estate.** On the same path, the grantor's estate after a sale to a trust
outside the estate is smaller than after keeping the asset by exactly what the trust holds net of the note. -/
theorem estate_shrinks (R : Rates) (basis : Int) (path : List (Int × Int)) (s0 : St) (h0 : s0.tCash = 0) (swap : Bool) :
    let k := years R ⟨false, false⟩ path (sell R ⟨false, false⟩ basis s0)
    let d := years R ⟨true, true⟩ path (sell R ⟨true, true⟩ basis s0)
    (outcome R ⟨false, false⟩ false false basis path s0).estate =
      (outcome R ⟨true, true⟩ false swap basis path s0).estate + (d.asset + d.tCash - d.note) := by
  obtain ⟨ha, hc, _⟩ := defective_neutral R basis path s0 h0
  simp only [outcome, death, Bool.not_false, Bool.not_true]
  cases swap <;> simp <;> omega

/-- The heirs' share after estate tax never falls when the estate grows. -/
theorem after_tax_mono (R : Rates) (a b : Int) (hab : a ≤ b) : a - estateTaxOn R a ≤ b - estateTaxOn R b := by
  unfold estateTaxOn; split <;> split <;> omega

theorem death_tax (R : Rates) (h : Hold) (inEst swap : Bool) (basis : Int) (s : St) :
    (death R h inEst swap basis s).estateTax = estateTaxOn R (death R h inEst swap basis s).estate := by
  unfold death; split <;> rfl

/-- And the tax itself never falls. -/
theorem tax_mono (R : Rates) (a b : Int) (hab : a ≤ b) : estateTaxOn R a ≤ estateTaxOn R b := by
  unfold estateTaxOn; split <;> split <;> omega

/-- **Sold to a defective trust and swapped back before death, the heirs gain exactly the estate tax saved.** For
every path: the heirs' share exceeds what they would have had if the grantor had kept the asset by the difference
between the two estate-tax bills, and the latent capital-gains tax is zero in both. -/
theorem swap_gain (R : Rates) (basis : Int) (path : List (Int × Int)) (s0 : St) (h0 : s0.tCash = 0) :
    (outcome R ⟨true, true⟩ false true basis path s0).heirs - (outcome R ⟨false, false⟩ false false basis path s0).heirs =
      (outcome R ⟨false, false⟩ false false basis path s0).estateTax - (outcome R ⟨true, true⟩ false true basis path s0).estateTax ∧
    (outcome R ⟨true, true⟩ false true basis path s0).latentGain = 0 := by
  obtain ⟨ha, hc, _⟩ := defective_neutral R basis path s0 h0
  simp only [outcome, death, Bool.not_false, Bool.not_true]
  simp
  try constructor
  all_goals omega

/-- So, whenever the trust ends with anything net of the note, the swap plan never leaves the heirs worse off. -/
theorem swap_never_worse (R : Rates) (basis : Int) (path : List (Int × Int)) (s0 : St) (h0 : s0.tCash = 0)
    (hT : let d := years R ⟨true, true⟩ path (sell R ⟨true, true⟩ basis s0); 0 ≤ d.asset + d.tCash - d.note) :
    (outcome R ⟨false, false⟩ false false basis path s0).heirs ≤ (outcome R ⟨true, true⟩ false true basis path s0).heirs := by
  have hs := estate_shrinks R basis path s0 h0 true
  have ⟨g, _⟩ := swap_gain R basis path s0 h0
  have := tax_mono R (outcome R ⟨true, true⟩ false true basis path s0).estate (outcome R ⟨false, false⟩ false false basis path s0).estate
    (by simp only at hT hs; omega)
  have t1 := death_tax R ⟨true, true⟩ false true basis (years R ⟨true, true⟩ path (sell R ⟨true, true⟩ basis s0))
  have t2 := death_tax R ⟨false, false⟩ false false basis (years R ⟨false, false⟩ path (sell R ⟨false, false⟩ basis s0))
  simp only [outcome] at *
  omega

/-- **Without the swap, the heirs pay for the carried-over basis.** Same path, same trust: the only difference is the
capital-gains tax on the asset's growth over the grantor's original basis. -/
theorem no_swap_cost (R : Rates) (basis : Int) (path : List (Int × Int)) (s0 : St) :
    (outcome R ⟨true, true⟩ false true basis path s0).heirs - (outcome R ⟨true, true⟩ false false basis path s0).heirs =
      (outcome R ⟨true, true⟩ false false basis path s0).latentGain := by
  simp only [outcome, death, Bool.not_true]; simp; omega

/-! ## The trap -/

/-- Keeping the asset, and selling it to a trust that is not the grantor's for income tax: the same asset, and the
family's wealth plus the taxes it has paid is the same. -/
def Trap (k t : St) : Prop := k.asset = t.asset ∧ k.gCash + k.taxPaid = t.gCash + t.tCash + t.taxPaid ∧ k.taxPaid ≤ t.taxPaid
  ∧ t.note = t.note

theorem pct_nonneg (x r : Int) (hx : 0 ≤ x) (hr : 0 ≤ r) : 0 ≤ pct x r :=
  Int.ediv_nonneg (Int.mul_nonneg hx hr) (by decide)

theorem year_trap (R : Rates) (hr : 0 ≤ R.afr ∧ 0 ≤ R.interestTax) (gy : Int × Int) (k t : St) (hn : 0 ≤ t.note)
    (h : Trap k t) : Trap (year R ⟨false, false⟩ gy k) (year R ⟨true, false⟩ gy t) ∧ (year R ⟨true, false⟩ gy t).note = t.note := by
  obtain ⟨ha, hc, ht, _⟩ := h
  have hi := pct_nonneg (pct t.note R.afr) R.interestTax (pct_nonneg _ _ hn hr.1) hr.2
  simp only [year, Trap, Bool.not_false, Bool.not_true]
  rw [ha] at *; simp; omega

theorem years_trap (R : Rates) (hr : 0 ≤ R.afr ∧ 0 ≤ R.interestTax) (path : List (Int × Int)) :
    ∀ k t, 0 ≤ t.note → Trap k t →
      Trap (years R ⟨false, false⟩ path k) (years R ⟨true, false⟩ path t) ∧ (years R ⟨true, false⟩ path t).note = t.note := by
  induction path with
  | nil => intro k t _ h; exact ⟨h, rfl⟩
  | cons gy rest ih =>
    intro k t hn h
    obtain ⟨h1, h2⟩ := year_trap R hr gy k t hn h
    obtain ⟨h3, h4⟩ := ih _ _ (by rw [h2]; exact hn) h1
    exact ⟨h3, by simp only [years]; rw [h4, h2]⟩

/-- **The trap is never better than keeping the asset.** A trust that the estate tax counts as the grantor's but the
income tax does not: for every path, and any basis below the sale price, selling the asset to it leaves the heirs no
better off than if the grantor had simply kept it, because the sale's gain and the interest are taxed while nothing
leaves the estate. -/
theorem trap_never_better (R : Rates) (hr : 0 ≤ R.afr ∧ 0 ≤ R.interestTax ∧ 0 ≤ R.gainTax) (basis : Int)
    (path : List (Int × Int)) (s0 : St) (h0 : s0.tCash = 0) (hb : basis ≤ s0.asset) (hpos : 0 ≤ s0.asset) :
    (outcome R ⟨true, false⟩ true false basis path s0).heirs ≤ (outcome R ⟨false, false⟩ false false basis path s0).heirs := by
  have hg := pct_nonneg (s0.asset - basis) R.gainTax (by omega) hr.2.2
  obtain ⟨⟨ha, hc, ht, _⟩, _⟩ := years_trap R ⟨hr.1, hr.2.1⟩ path (sell R ⟨false, false⟩ basis s0) (sell R ⟨true, false⟩ basis s0)
    (by simp [sell]; exact hpos) (by simp [sell, Trap, h0]; omega)
  simp only [outcome, death, Bool.not_false, Bool.not_true]
  simp
  have := after_tax_mono R
    ((years R ⟨true, false⟩ path (sell R ⟨true, false⟩ basis s0)).gCash + (years R ⟨true, false⟩ path (sell R ⟨true, false⟩ basis s0)).note +
      ((years R ⟨true, false⟩ path (sell R ⟨true, false⟩ basis s0)).asset + (years R ⟨true, false⟩ path (sell R ⟨true, false⟩ basis s0)).tCash -
        (years R ⟨true, false⟩ path (sell R ⟨true, false⟩ basis s0)).note))
    ((years R ⟨false, false⟩ path (sell R ⟨false, false⟩ basis s0)).gCash + (years R ⟨false, false⟩ path (sell R ⟨false, false⟩ basis s0)).asset)
    (by omega)
  omega

end Legal.USTax.Trusts
