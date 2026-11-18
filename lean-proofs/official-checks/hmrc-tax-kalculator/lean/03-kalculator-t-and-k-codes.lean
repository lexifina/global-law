/-!
# tax-kalculator: the PAYE "£9" for T-suffix and K-prefix codes

HMRC, Specification for PAYE tax table routines (v24.0), para 4.3.1(b): Free Pay (suffix codes) or Additional Pay
(prefix K, SK, CK codes) is calculated "from the numeric part of the codes": "the annual value which is
[(numeric part of code) x £10] + £9" (codes above 500 are split into 500s, each worth exactly £5,000 a year).
Para 15.1: "The suffix plays no part in the actual tax calculations".

tax-kalculator 2.16.1 adds the £9 for L, M, N and emergency codes (`LCode.taxFreeAmount = n * 10 + 9`), not for
T codes (`TCode.taxFreeAmount = n * 10`) or K codes (`KCode.amountToAddToWages = n * 10`), while
`getTrueTaxFreeAmount()` subtracts £9 from every positive tax-free amount. Consequences, annual pay £50,000, 2025-26,
rest of the UK (20 % to £37,700 of taxable pay, then 40 %):

* 1257L: tax-free shown £12,570, tax £7,484.20;
* 1257T: tax-free shown £12,561, tax £7,486.00 (the same code number under PAYE gives £7,484.20);
* K475: tax £14,360.00; PAYE's Additional Pay of £4,759 gives £14,363.60.

Amounts in pence; proofs by kernel computation (`decide`). Lean 4 core only.
-/

namespace KalcCodes

set_option maxRecDepth 100000

/-- Para 4.3.1: the annual Free Pay / Additional Pay (pounds) for the numeric part `n` of a code:
⌊(n − 1)/500⌋ blocks of £5,000 plus £10 × (remainder) + £9, for n ≥ 1; nothing for n = 0. -/
def annualValue (n : Nat) : Nat :=
  if n = 0 then 0 else ((n - 1) / 500) * 5000 + 10 * ((n - 1) % 500 + 1) + 9

/-- Annual tax (pence) on taxable pay `t` (pounds), rest of the UK 2025-26 (ITA 2007 ss. 6, 10: basic rate 20 % to
£37,700, higher rate 40 % to £125,140, additional rate 45 % above). -/
def tax (t : Nat) : Nat :=
  20 * min t 37700 + 40 * (min t 125140 - min t 37700) + 45 * (t - min t 125140)

theorem free_pay_1257 : annualValue 1257 = 12579 := by decide
theorem additional_pay_475 : annualValue 475 = 4759 := by decide

/-- The amount a code number stands for is 10 × the number (gov.uk/tax-codes: 1257L = £12,570); the PAYE routine's
annual Free Pay adds £9. What tax-kalculator reports as `taxFree` for 1257T is neither. -/
theorem t_code_tax_free_shown : 10 * 1257 - 9 = 12561 ∧ 12561 ≠ 10 * 1257 ∧ 12561 ≠ annualValue 1257 := by decide

/-- PAYE, any suffix letter: (50,000 − 12,579) × 20 % = £7,484.20. The kalculator's 1257T: (50,000 − 12,570) × 20 %
= £7,486.00. -/
theorem suffix_code_50000 : tax (50000 - annualValue 1257) = 748420 ∧ tax (50000 - 12570) = 748600 := by decide

/-- PAYE, K475: (50,000 + 4,759) → £14,363.60; the kalculator (50,000 + 4,750) → £14,360.00. -/
theorem k_code_50000 : tax (50000 + annualValue 475) = 1436360 ∧ tax (50000 + 4750) = 1436000 := by decide

/-- The general rule over £12,600 … £200,000 (step £100), for the code number used as given (no taper): the T-code
result exceeds the PAYE-style result by £9 at the marginal rate(s), between £1.80 and £4.05, never 0. -/
theorem t_code_gap :
    ∀ i, i < 1875 →
      180 ≤ tax (12600 + 100 * i - 12570) - tax (12600 + 100 * i - annualValue 1257) ∧
      tax (12600 + 100 * i - 12570) - tax (12600 + 100 * i - annualValue 1257) ≤ 405 := by
  decide

end KalcCodes
