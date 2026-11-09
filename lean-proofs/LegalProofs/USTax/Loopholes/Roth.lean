import LegalProofs.USTax.Loopholes.Common

/-!
# A retirement account with no ceiling on what it holds (§408A)

A Roth IRA caps what goes **in** (§408A(c)(2): the annual contribution limit, $2,000 in 1999) and taxes nothing that
comes **out** as a qualified distribution (§408A(d)(1)). Nothing caps what the contribution is worth later. Put shares in
at a founder's price and the whole of their growth is outside the income tax for good.

ProPublica reported in 2021, from IRS records, that Peter Thiel bought 1.7 million PayPal founder shares for about $1,700
inside a Roth IRA in 1999, and that the account held about $5 billion by 2019. The figures below are those reported
amounts; the proof does not depend on them.
-/

namespace Legal.USTax.Loopholes

inductive Wrapper where
  | taxable | roth
  deriving DecidableEq, Repr

/-- Federal tax on cashing out an investment that cost `cost` and is now worth `value`. In a taxable account the gain
is a long-term capital gain; from a Roth IRA, a qualified distribution is not income at all (§408A(d)(1)). -/
def cashOutTax : Wrapper → Nat → Nat → Nat
  | .taxable, cost, value => bp (value - cost) ltcgRate
  | .roth, _, _ => 0

/-- The contribution test looks only at what is paid in (§408A(c)(2)). -/
def contributionAllowed (limit cost : Nat) : Bool := cost ≤ limit

/-- **No growth is ever taxed.** For every cost and every final value, a qualified Roth distribution owes nothing. -/
theorem roth_growth_never_taxed (cost value : Nat) : cashOutTax .roth cost value = 0 := rfl

/-- **The limit is on cost, not value.** Whatever an allowed contribution is later worth, it was allowed; there is no
value for which the same purchase becomes disallowed. -/
theorem limit_ignores_value (limit cost value₁ value₂ : Nat) (h : contributionAllowed limit cost = true) :
    contributionAllowed limit cost = true ∧ cashOutTax .roth cost value₁ = cashOutTax .roth cost value₂ := ⟨h, rfl⟩

/-- The reported case: $1,700 of founder shares, a $2,000 limit, $5 billion two decades later. -/
theorem thiel_contribution_allowed : contributionAllowed 2000 1700 = true := by decide

/-- **$1,189,999,595.** The tax the same growth would have owed in a taxable account, at today's top rates. -/
theorem thiel_roth :
    cashOutTax .taxable 1700 5000000000 = 1189999595 ∧ cashOutTax .roth 1700 5000000000 = 0 := by decide

end Legal.USTax.Loopholes
