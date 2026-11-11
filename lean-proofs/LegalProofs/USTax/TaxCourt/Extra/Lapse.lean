import LegalProofs.USTax.TaxCourt.Basic

/-!
# Lapse or surrender of a life insurance contract with an outstanding policy loan: §72(e)

A cash-value life insurance contract that lapses or is surrendered while a policy loan is outstanding is a
non-annuity amount received under the contract: §72(e)(5)(A), (C) (surrender, redemption or maturity) apply §72(e)(2)
"to the extent it exceeds the investment in the contract". The loan extinguished by applying the cash value is an
amount received (the policyholder is relieved of the debt), so

  income = (cash value applied to the loan, including capitalized loan interest + cash received)
           − investment in the contract,

where §72(e)(6) investment in the contract = premiums and other consideration paid − amounts previously received
under the contract that were excluded from gross income (e.g. policy dividends and earlier tax-free withdrawals).
Income is never negative: a loss on a life insurance contract is not deductible (§262 personal; London Shoe Co.).
The income is ordinary, reported on Form 1099-R (code 7 or L), and is not an early distribution (§72(t) does not
apply to life insurance).
-/

namespace Legal.USTax.TaxCourt.Extra
open Legal.USTax.TaxCourt

/-- Findings about one contract's lapse or surrender. Amounts are whole dollars. -/
structure LapseFacts where
  /-- Cash value applied to repay the outstanding policy loan (principal and accrued/capitalized interest). -/
  loanExtinguished : Int
  /-- Cash paid to the policyholder on surrender (net surrender value after the loan). -/
  cashReceived : Int := 0
  /-- Premiums and other consideration paid (§72(e)(6)(A)). -/
  premiumsPaid : Int
  /-- Amounts received before, under the contract, excluded from gross income (§72(e)(6)(B)): dividends, tax-free
  withdrawals. -/
  nontaxableReceived : Int := 0
  deriving Repr, Inhabited

/-- §72(e)(6): investment in the contract (not below zero). -/
def investmentInContract (l : LapseFacts) : Int := pos (l.premiumsPaid - l.nontaxableReceived)

/-- Total amount received on lapse or surrender. -/
def lapseAmountReceived (l : LapseFacts) : Int := l.loanExtinguished + l.cashReceived

/-- §72(e)(2)(A), (e)(5): gross income on the lapse or surrender. -/
def lapseIncome (l : LapseFacts) : Int := pos (lapseAmountReceived l - investmentInContract l)

theorem lapseIncome_le_received (l : LapseFacts) (h : 0 ≤ lapseAmountReceived l) :
    lapseIncome l ≤ lapseAmountReceived l := by
  unfold lapseIncome investmentInContract pos; omega

/-! ## Tests -/

-- Pub. 525 ("Life insurance … Surrender of policy for cash"): income is what is received over the cost.
-- A policy lapses with a $60,000 loan (incl. capitalized interest) outstanding; premiums $40,000, dividends $5,000
-- received tax-free: investment $35,000; income $25,000, though no cash changed hands.
#guard lapseIncome { loanExtinguished := 60000, premiumsPaid := 40000, nontaxableReceived := 5000 } = 25000
-- Surrender: $20,000 loan repaid from the value plus $8,000 cash, premiums $30,000: no income (no deductible loss).
#guard lapseIncome { loanExtinguished := 20000, cashReceived := 8000, premiumsPaid := 30000 } = 0
-- Earlier tax-free withdrawals reduce the investment: $50,000 premiums, $20,000 withdrawn, $45,000 loan: $15,000.
#guard lapseIncome { loanExtinguished := 45000, premiumsPaid := 50000, nontaxableReceived := 20000 } = 15000

end Legal.USTax.TaxCourt.Extra
