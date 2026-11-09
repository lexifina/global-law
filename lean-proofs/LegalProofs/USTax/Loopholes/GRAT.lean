import LegalProofs.USTax.Loopholes.Common

/-!
# The zeroed-out GRAT (§2702, §7520; *Walton v. Commissioner*, 115 T.C. 589 (2000))

A grantor retained annuity trust takes assets now and pays the grantor a fixed annuity for a term; whatever is left at
the end goes to the heirs. The gift is valued on the day the trust is made, as the assets minus the present value of the
annuity, discounted at the §7520 rate (120% of the federal mid-term rate; 5.6% for October 2026). In *Walton* the Tax
Court accepted a GRAT whose annuity was worth the whole contribution, so the gift was zero, and the IRS later accepted it
(Notice 2003-72). That is the zeroed-out GRAT.

The result is a free option. If the assets beat the §7520 rate, the excess passes to the heirs with no gift tax and no
estate tax. If they do not, the annuity drains the trust, everything comes back to the grantor, and nothing is lost but
fees. Rolling short GRATs, one after another, catch every good year and shrug off every bad one.

This file proves, for every amount and every §7520 rate, that a two-year GRAT with the annuity below is a gift of zero;
that nothing leaks (the grantor's annuities plus the heirs' remainder are everything the trust paid out); and evaluates it.
-/

namespace Legal.USTax.Loopholes.GRAT

/-- Discounting at `r` basis points for a two-year term: the present value of an annuity `A` is `A * K / M`. -/
def K (r : Nat) : Nat := 10000 * (20000 + r)
def M (r : Nat) : Nat := (10000 + r) * (10000 + r)

/-- The annuity that zeroes the gift: the smallest whole-dollar annuity whose present value covers the contribution. -/
def annuity (P r : Nat) : Nat := (P * M r + K r - 1) / K r

/-- §2702: the gift is the contribution less the present value of the retained annuity (never below zero). -/
def gift (P r : Nat) : Nat := (P * M r - annuity P r * K r) / M r

theorem ceil_div_mul_ge (X k : Nat) (hk : 0 < k) : X ≤ (X + k - 1) / k * k := by
  have h1 := Nat.div_add_mod (X + k - 1) k
  have h2 := Nat.mod_lt (X + k - 1) hk
  generalize (X + k - 1) / k = q at *
  generalize (X + k - 1) % k = m at *
  rw [Nat.mul_comm] at h1
  omega

/-- **Zeroed out.** For every contribution and every §7520 rate, the taxable gift is exactly zero. -/
theorem zero_gift (P r : Nat) : gift P r = 0 := by
  have hk : 0 < K r := by unfold K; omega
  have := ceil_div_mul_ge (P * M r) (K r) hk
  unfold gift annuity
  rw [Nat.sub_eq_zero_of_le this]; simp

/-! ## Two years in the trust

`f₁`, `f₂` are the growth factors of the two years in basis points (14000 = +40%, 8000 = −20%). The annuity is paid from
what the trust holds; if it holds less, the grantor takes all of it. -/

structure Outcome where
  toGrantor : Nat   -- annuities actually paid back
  toHeirs : Nat     -- what is left at the end, passing free of gift and estate tax
  deriving DecidableEq, Repr

def run (P r f₁ f₂ : Nat) : Outcome :=
  let A := annuity P r
  let v₁ := P * f₁ / 10000
  let p₁ := min A v₁
  let v₂ := (v₁ - p₁) * f₂ / 10000
  let p₂ := min A v₂
  ⟨p₁ + p₂, v₂ - p₂⟩

/-- **Nothing leaks.** In every outcome, what the grantor gets back plus what the heirs get is exactly what the trust
had to pay out: the first year's value less the first annuity, grown, plus the first annuity. -/
theorem nothing_leaks (P r f₁ f₂ : Nat) :
    let A := annuity P r; let v₁ := P * f₁ / 10000
    (run P r f₁ f₂).toGrantor + (run P r f₁ f₂).toHeirs = min A v₁ + (v₁ - min A v₁) * f₂ / 10000 := by
  simp only [run]; omega

/-- **Heads.** $100 million of stock, the October 2026 rate (5.6%), two good years (+40%, +30%). The grantor takes back
two annuities of $54,238,133; $57,252,294 passes to the heirs, and with it $22.9 million of estate tax is never owed. -/
theorem heads : run 100000000 560 14000 13000 = ⟨108476266, 57252294⟩ ∧ gift 100000000 560 = 0 := by decide

/-- **Tails.** The same trust in two bad years (−20%, −10%): the heirs get nothing, the grantor gets everything back,
and the gift was still zero. Nothing was risked. -/
theorem tails : run 100000000 560 8000 9000 = ⟨77423813, 0⟩ := by decide

end Legal.USTax.Loopholes.GRAT
