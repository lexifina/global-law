import LegalProofs.USTax.Loopholes.Common

/-!
# Stacking the startup-stock exclusion (§1202, §643(f))

§1202 excludes from income the gain on qualified small business stock held five years, up to a per-taxpayer, per-company
cap: for stock issued after 4 July 2025, the greater of $15 million or ten times the taxpayer's basis (§1202(b)(1) as
amended by Pub. L. 119-21 §70431). The cap is per **taxpayer**. A non-grantor trust is a separate taxpayer, and a gift
carries the stock's holding period and status with it (§1202(h)(2)). So a founder who gives shares to several trusts
before a sale multiplies the cap: each trust takes its own $15 million.

The limit is §643(f): trusts with substantially the same grantor and the same primary beneficiary, made with a principal
purpose of avoiding tax, are treated as one. This file models both: the cap per taxpayer, and the §643(f) merge.
-/

namespace Legal.USTax.Loopholes.QSBS
open Legal.USTax.Loopholes

/-- The §1202(b)(1) cap for one taxpayer and one company. -/
def cap (basis : Nat) : Nat := max 15000000 (10 * basis)

/-- Federal tax on one taxpayer's gain: nothing up to the cap, long-term rates above it. -/
def taxOn (gain basis : Nat) : Nat := bp (gain - cap basis) ltcgRate

/-- **Under the cap, no tax.** -/
theorem under_cap_free (gain basis : Nat) (h : gain ≤ cap basis) : taxOn gain basis = 0 := by
  simp [taxOn, Nat.sub_eq_zero_of_le h, bp]

/-- **Merging never helps, splitting never hurts.** Taxed as one, two holdings owe at least as much as taxed apart:
this is why each extra separate taxpayer is worth money, and why §643(f) merging costs it. -/
theorem merge_costs (g₁ g₂ : Nat) : taxOn g₁ 0 + taxOn g₂ 0 ≤ taxOn (g₁ + g₂) 0 := by
  unfold taxOn
  have : (g₁ - cap 0) + (g₂ - cap 0) ≤ g₁ + g₂ - cap 0 ∨ g₁ + g₂ < cap 0 := by omega
  rcases this with h | h
  · exact Nat.le_trans (bp_add_ge _ _ _) (bp_mono _ h)
  · have h1 : g₁ - cap 0 = 0 := by omega
    have h2 : g₂ - cap 0 = 0 := by omega
    simp [h1, h2, bp]

/-! ## Holders and the §643(f) merge -/

/-- Who holds shares: a person (`grantor = beneficiary = self`, not a trust) or a non-grantor trust. -/
structure Holder where
  isTrust : Bool
  grantor : Nat
  beneficiary : Nat
  gain : Nat
  deriving DecidableEq, Repr

/-- §643(f): trusts with the same grantor and primary beneficiary are one taxpayer. -/
def key (h : Holder) : Bool × Nat × Nat := (h.isTrust, h.grantor, h.beneficiary)

/-- Add up each taxpayer's gain after merging. -/
def merge (hs : List Holder) : List ((Bool × Nat × Nat) × Nat) :=
  hs.foldl (fun acc h =>
    if acc.any (·.1 == key h) then acc.map (fun (k, g) => if k == key h then (k, g + h.gain) else (k, g))
    else acc ++ [(key h, h.gain)]) []

/-- Tax on a sale of founder stock (basis zero) held this way. -/
def saleTax (hs : List Holder) : Nat := ((merge hs).map (fun (_, g) => taxOn g 0)).foldl (· + ·) 0

def person (id gain : Nat) : Holder := ⟨false, id, id, gain⟩
def trust (grantor beneficiary gain : Nat) : Holder := ⟨true, grantor, beneficiary, gain⟩

/-- A $150 million exit. Founder (1), spouse (2), three children (3, 4, 5). -/
def alone : List Holder := [person 1 150000000]
def stacked : List Holder :=
  [person 1 15000000, person 2 15000000, trust 1 3 15000000, trust 1 4 15000000, trust 1 5 15000000,
   trust 2 3 15000000, trust 2 4 15000000, trust 2 5 15000000, trust 1 6 15000000, trust 2 6 15000000]
/-- The same ten slices, but every trust names the same child: §643(f) folds them into two trusts. -/
def naive : List Holder :=
  [person 1 15000000, person 2 15000000, trust 1 3 15000000, trust 1 3 15000000, trust 1 3 15000000,
   trust 1 3 15000000, trust 2 3 15000000, trust 2 3 15000000, trust 2 3 15000000, trust 2 3 15000000]

/-- **$32,130,000 to $0.** Held alone, $150 million of founder stock owes $32.13 million. Spread across the founder, the
spouse, and eight trusts, each with its own grantor–beneficiary pair (beneficiary 6 a grandchild), it owes nothing. Drawn
carelessly, with every trust for one child, §643(f) merges them and $21.42 million is owed after all. -/
theorem stacking : saleTax alone = 32130000 ∧ saleTax stacked = 0 ∧ saleTax naive = 21420000 := by decide

end Legal.USTax.Loopholes.QSBS
