import LegalProofs.USTax.Schedule

/-!
# Loopholes: shared rates and arithmetic

The cliffs in `Cliffs.lean` hurt the households that meet them. The files under `Loopholes/` are the other side: lawful
structures, each reported in practice, that let a taxpayer arrange the same economics so that much less tax, or none,
falls due. Each file models the provisions involved, proves the general fact the structure rests on (for all amounts,
not for one example), and then evaluates the structure on reported or illustrative figures.

Rates are the 2025–2026 federal rates. Every figure is in whole dollars; `bp x r` is `r` basis points of `x`, rounded
down.
-/

namespace Legal.USTax.Loopholes

/-- `rate` basis points of `x`, rounded down. -/
def bp (x rate : Nat) : Nat := x * rate / 10000

/-- Top rate on long-term capital gains (§1(h)(1)(D), 20%) plus the net investment income tax (§1411, 3.8%). -/
def ltcgRate : Nat := 2380

/-- Top ordinary rate (§1(j)(2), 37%). -/
def topRate : Nat := 3700

/-- Estate tax rate above the exclusion (§2001(c), 40%). -/
def estateRate : Nat := 4000

/-- Basic exclusion amount for 2026, per person: $15,000,000 (§2010(c)(3) as amended by Pub. L. 119-21 §70106). -/
def estateExemption : Nat := 15000000

/-- Floor division never loses by being taken on a sum: `a/c + b/c ≤ (a+b)/c`. -/
theorem div_add_div_le (a b c : Nat) : a / c + b / c ≤ (a + b) / c := by
  rcases Nat.eq_zero_or_pos c with h | h
  · subst h; simp
  · rw [Nat.le_div_iff_mul_le h, Nat.add_mul]
    exact Nat.add_le_add (Nat.div_mul_le_self a c) (Nat.div_mul_le_self b c)

/-- `bp` is superadditive: taxing two amounts together never costs less than taxing them apart. -/
theorem bp_add_ge (a b r : Nat) : bp a r + bp b r ≤ bp (a + b) r := by
  unfold bp; rw [Nat.add_mul]; exact div_add_div_le _ _ _

theorem bp_mono {a b : Nat} (r : Nat) (h : a ≤ b) : bp a r ≤ bp b r := by
  unfold bp; exact Nat.div_le_div_right (Nat.mul_le_mul_right r h)

end Legal.USTax.Loopholes
