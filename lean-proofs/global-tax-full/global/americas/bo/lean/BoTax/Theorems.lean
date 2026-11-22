import BoTax.Basic

namespace BoTax
open TaxKernel

/-- **BO-F1.** The minimo no imponible (art. 26: 2 SMN deducted from the base) and the pago a cuenta of 13 % of 2 SMN
(D.S. 21531 art. 8 c) 2) together exempt a wage of 4 SMN a month: the effective threshold is twice the printed one. -/
theorem exempt_up_to_four_smn (m : Int) (h0 : 0 ≤ m) (h : m ≤ 4 * smn) : (person (12 * m) 0 0 0 0).wageTax = 0 := by
  simp only [person, smn, mniSMN, rcivaRate, pos, divR, BP] at *
  omega

/-- Above 4 SMN a month the RC-IVA is a flat 13 % of the excess (no invoices, no contributions). -/
theorem flat_above (k : Int) (hk : 0 ≤ k) :
    (person (12 * (4 * smn + 100 * k)) 0 0 0 0).wageTax = 12 * 13 * k := by
  simp only [person, smn, mniSMN, rcivaRate, pos, divR, BP] at *
  omega

end BoTax
