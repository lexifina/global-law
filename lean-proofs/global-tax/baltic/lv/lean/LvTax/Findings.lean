import LvTax.Basic
import LvTax.Theorems

/-!
# The findings of `FINDINGS.md`, proved on named households (`decide` on the model's own computation)

Amounts in cents. `burdenP p r` = the person's income taxes + contributions with reliefs `r`.
-/

namespace LvTax
open TaxKernel

set_option maxRecDepth 200000

def burdenP (p : Person) (rel : Int) : Int := (personRes p rel).taxes + (personRes p rel).social

/-- F1: the self-employed minimum-wage notch (VSAOI 14.1 pants): one more euro of profit at 8 880 euro a year
(740 a month) costs between 1 390 and 1 400 euro of VSAOI net of IIN. -/
theorem f1_se_notch :
    139000 ≤ burdenP { se := eur 8880 } 0 - burdenP { se := eur 8879 } 0 ∧
    burdenP { se := eur 8880 } 0 - burdenP { se := eur 8879 } 0 ≤ 140000 := by decide

/-- F2: the same 12 000 euro profit received in one month instead of twelve saves more than 1 270 euro (the
31,07 % rate on the minimum wage is charged per month with income at or above it). -/
theorem f2_se_months : burdenP { se := eur 12000, seMonths := 12 } 0 - burdenP { se := eur 12000, seMonths := 1 } 0 ≥ 127000 := by
  decide

/-- F3: the non-working spouse relief (13. panta 1. daļas 1. punkts l)): a spouse at home with a child under 3
earns one euro; the family's income tax rises by 765 euro (3 000 × 25,5 %). -/
def f3Hh (sw : Int) (married : Bool) : Canon :=
  { id := "f3", married := married, adults := [{ wages := 21321 }, { wages := sw }], children := [{ age := 1 }] }
def hhTax (c : Canon) : Int := totalTaxes (splitRes c (bestJ c))
theorem f3_spouse_notch : hhTax (f3Hh 1 true) - hhTax (f3Hh 0 true) = 76500 := by decide
/-- F3 (marriage): the same couple unmarried pays the same 765 euro more ("laulāto"). -/
theorem f3_marriage_bonus : hhTax (f3Hh 0 false) - hhTax (f3Hh 0 true) = 76500 := by decide

/-- F4: three children's reliefs claimed by the parent earning 7 000 euro instead of the one earning 30 000 lose
more than 2 250 euro a year (the reliefs are not transferable once claimed in the tax book). -/
def f4Hh : Canon :=
  { id := "f4", married := true, adults := [{ wages := 7000 }, { wages := 30000 }],
    children := [{ age := 5 }, { age := 6 }, { age := 7 }] }
theorem f4_allocation : totalTaxes (splitRes f4Hh 3) - hhTax f4Hh ≥ 225000 := by decide

/-- F5: a payment costing 50 000 euro: as wages (40 456 euro + 23,59 % employer VSAOI) the state takes more than
21 400 euro; as an author's royalty (PN 164, 25 %) 12 500 euro. -/
theorem f5_royalty_vs_wage :
    (eur 50000 - eur 40456) + burdenP { wages := eur 40456 } 0 ≥ 2140000 ∧
    burdenP { se := eur 50000, regime := 2 } 0 = 1250000 := by decide

/-- F6: own company, all profit distributed: 20 % CIT on the gross-up (UIN 3(1), 4(9)) and no IIN on the dividend
up to 200 000 euro (9. panta 1. daļas 2.1 punkts); above it only the 3 % additional rate (15.1 pants). -/
theorem f6_dividends : burdenP { divs := eur 160000 } 0 = 0 ∧ (personRes { divs := eur 250000 } 0).surtax = 150000 := by
  decide

/-- F7: monthly withholding vs the annual return for a 150 000 euro wage: more than 4 400 euro is due with the
return (7,5 % of the wage above 105 300 plus 25,5 % of the solidarity-tax IIN share no longer deductible). -/
theorem f7_settlement :
    let w := eur 150000
    (personRes { wages := w } 0).iin - withheld w ntmMonth 0 ≥ 449000 := by decide

/-- F8: VID's information material reads the 33 % as applying to "apliekamajam ienākumam virs 105 300 eiro"; the
statute applies it to income above 105 300 with the deductions at 25,5 %. For income 110 000 and deductions
18 000 euro the difference is 352,50 euro. -/
theorem f8_vid_reading : iinTicks (eur 18000) (eur 110000) - iinSched.ticks (eur 110000 - eur 18000) = 352500000 := by
  rw [lowband_cost (by decide) (by decide) (by decide)]; decide

/-- F10: 12. panta 1. daļa (2025 text) says 570 euro a month; the 2025 amount is 510 (PN 197). Read alone, the
article overstates the year's minimum by 720 euro, worth 183,60 euro of tax. -/
theorem f10_ntm_text : 12 * (eur 570 - ntmMonth) = 72000 ∧ cents (wageRate * 72000) = 18360 := by decide

end LvTax
