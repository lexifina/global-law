import LvTax.Basic

/-!
# Official worked examples, checked by the kernel (`decide`)

**VID, "Algas nodoklis" (2025), pp. 4-6** (https://www.vid.gov.lv/lv/media/27996/download, saved as
`refs/vid/m_27996.txt`): eight monthly withholding examples. Amounts in cents. `monthTax` is the monthly wage-tax
step of `withheld` (IIN 15. panta 3. daļa; 10. panta 2. daļa; 12. panta 1. daļa; 13. panta 1.2 daļa).

**VID, "Attaisnotie izdevumi" (2025 income, January 2026), examples 1, 5 and 9**
(https://www.vid.gov.lv/lv/media/33101/download, `refs/vid/m_33101.txt`).
-/

namespace LvTax
open TaxKernel

/-- One month's wage tax: wage `w`, contribution rate `r`, monthly minimum `ntm`, reliefs `rel` (all cents). -/
def monthTax (w r ntm rel : Int) : Int := cents (wageRate * pos (w - cents (r * w) - ntm - rel))

/-- Example 1: 900 euro, no tax book: VSAOI 94,50; "(900 – 94,50) x 25,5 % = 205,40 eiro". -/
theorem vid_ex1 : cents (eeRate * 90000) = 9450 ∧ monthTax 90000 eeRate 0 0 = 20540 := by decide
/-- Example 2: 1 000 euro, minimum 510: "(1000 – 105 – 510) X 25,5 % = 98,18 eiro". -/
theorem vid_ex2 : monthTax 100000 eeRate ntmMonth 0 = 9818 := by decide
/-- Example 3: 800 euro, three dependants (750 euro): negative base, tax 0,00. -/
theorem vid_ex3 : monthTax 80000 eeRate ntmMonth (3 * depMonth) = 0 := by decide
/-- Example 4: 9 000 euro, two dependants: "(9000 – 945 – 510 – 500) x 25,5 % likme = 1796,48 eiro" (the monthly
rate is 25,5 % whatever the wage: the 33 % band waits for the annual return). -/
theorem vid_ex4 : monthTax 900000 eeRate ntmMonth (2 * depMonth) = 179648 := by decide
/-- Example 5: a non-resident (third country), 1 000 euro, no minimum: "(1000 – 105) x 25,5 %=228,23 eiro". -/
theorem vid_ex5 : monthTax 100000 eeRate 0 0 = 22823 := by decide
/-- Example 6: a Polish-insured non-resident, 9 500 euro, Polish contributions 855 euro (15. panta 16. daļa: 33 %
on the month's income above 8 775 euro = 1/12 of 105 300): 2 019,60 + 239,25 = 2 258,85 euro. -/
theorem vid_ex6 : maxObject / 12 = 877500 ∧
    cents (wageRate * (877500 - 85500)) + cents (3300 * (950000 - maxObject / 12)) = 225885 := by decide
/-- Example 7: a working pensioner, wage 1 000 euro (VSAOI 9,25 % = 92,50), half the pensioner's minimum (500),
one dependant (250), group III disability (120): 9,56 euro; pension 550 euro less 500: 12,75 euro. -/
theorem vid_ex7 : cents (eeRatePensioner * 100000) = 9250 ∧
    monthTax 100000 eeRatePensioner (ntmPensioner / 24) (depMonth + 12000) = 956 ∧
    cents (wageRate * (55000 - ntmPensioner / 24)) = 1275 := by decide
/-- Example 8: an izdienas pensija recipient, wage 1 200 euro, no tax book, VSAOI 9,76 % (117,12): 276,13 euro. -/
theorem vid_ex8 : cents (976 * 120000) = 11712 ∧ monthTax 120000 976 0 0 = 27613 := by decide

/-- Attaisnotie izdevumi, example 1/5: the 600 euro cap is worth "153 eiro (25,5 % no 600 eiro)" to a basic-rate
taxpayer. Household: wages 20 000 euro with and without 600 euro of donations (same cap, 10. panta 1.3 daļa). -/
def ad1 (don : Int) : Person := { wages := eur 20000, donations := don }
theorem vid_ad_ex1 : (personRes (ad1 0) 0).iin - (personRes (ad1 (eur 600)) 0).iin = 15300 := by decide
/-- Attaisnotie izdevumi, example 9: income 5 000 euro, 600 euro paid to a private pension fund: only "10 % no
apliekamā ienākuma, t.i., 500 eiro" is deductible (10. panta 1.9 daļa). -/
theorem vid_ad_ex9 : min (eur 600) (min pensionCap (cents (pensionPct * eur 5000))) = eur 500 := by decide

end LvTax
