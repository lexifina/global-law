import LegalProofs.USTax.Loopholes.Common

/-!
# Buy, borrow, die (§§61, 1001, 1014)

Three rules, each ordinary on its own:

* a gain is taxed when property is **sold** (§1001); a rise in value is not income;
* a **loan** is not income (it must be repaid), so borrowing against shares to live on is not taxed;
* property inherited takes as its basis its **value at death** (§1014(a)): the heirs can sell at once with no gain.

Together: hold appreciated shares, borrow against them to spend, never sell. The gain is never taxed by anyone. The
loans are repaid from the estate, and are deducted from it (§2053(a)(4)), so they lower the estate tax too.

This file proves both halves for every holding and every borrowing plan, then runs a founder's life both ways.
-/

namespace Legal.USTax.Loopholes

structure Holding where
  basis : Nat
  value : Nat
  deriving Repr

def gainOnSale (h : Holding) : Nat := h.value - h.basis

/-- §1014(a)(1): basis of property acquired from a decedent is its fair market value at death. -/
def inherit (h : Holding) : Holding := ⟨h.value, h.value⟩

/-- **The step-up erases every gain.** Whatever the shares cost and whatever they are worth, the heirs' gain on an
immediate sale is zero. -/
theorem step_up_erases (h : Holding) : gainOnSale (inherit h) = 0 := by
  simp [gainOnSale, inherit]

/-! ## A life, lived two ways

Each year the owner needs `spend` dollars. The shares grow by `growth` basis points a year.

* **Sell:** sell enough shares each year to net `spend` after capital-gains tax (founder's shares: basis zero).
* **Borrow:** borrow `spend` each year against the shares; the debt compounds at `rate` basis points; nothing is sold.
-/

structure Life where
  value : Nat        -- the shares
  debt : Nat         -- what is owed against them
  incomeTax : Nat    -- income tax paid so far
  deriving Repr

def sellYear (spend growth : Nat) (s : Life) : Life :=
  let gross := spend * 10000 / (10000 - ltcgRate)
  let tax := gross - spend
  let left := s.value - gross
  { s with value := left + bp left growth, incomeTax := s.incomeTax + tax }

def borrowYear (spend growth rate : Nat) (s : Life) : Life :=
  let debt := s.debt + spend
  { s with value := s.value + bp s.value growth, debt := debt + bp debt rate }

def live (step : Life → Life) : Nat → Life → Life
  | 0, s => s
  | n + 1, s => live step n (step s)

/-- **Borrowing is never taxed.** For every spending need, growth rate, interest rate and length of life, the borrowing
plan pays no income tax at all. -/
theorem borrow_plan_no_income_tax (spend growth rate years : Nat) (s : Life) (h : s.incomeTax = 0) :
    (live (borrowYear spend growth rate) years s).incomeTax = 0 := by
  induction years generalizing s with
  | zero => simpa [live]
  | succ n ih => simp only [live]; exact ih _ (by simp [borrowYear, h])

/-- At death: the estate repays the debt (deductible, §2053(a)(4)), pays estate tax on what is left above the
exclusion, and the heirs receive the rest with a stepped-up basis. -/
structure Death where
  estateTax : Nat
  toHeirs : Nat
  totalTax : Nat   -- income tax over the life + estate tax
  deriving Repr

def die (s : Life) : Death :=
  let net := s.value - s.debt
  let et := bp (net - estateExemption) estateRate
  { estateTax := et, toHeirs := net - et, totalTax := s.incomeTax + et }

def founderStart : Life := ⟨1000000000, 0, 0⟩

/-- A founder with $1 billion of shares (basis zero) who spends $20 million a year for 30 years; shares grow 7% a year,
the securities-backed loan costs 5%. -/
def sold : Death := die (live (sellYear 20000000 700) 30 founderStart)
def borrowed : Death := die (live (borrowYear 20000000 700 500) 30 founderStart)

end Legal.USTax.Loopholes
