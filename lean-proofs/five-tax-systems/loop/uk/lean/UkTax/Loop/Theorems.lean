import UkTax.Household

/-!
# Loopholes as theorems (2025-26, extended model of `~/cmp/loop/uk`)

Each statement compares the household burden (income tax less relief at source + CGT + employee NI − child benefit
net of HICBC, pence) with and without the technique. Proved by evaluation (`decide`), as in `UkTax/Theorems.lean`.
-/

set_option maxRecDepth 100000

namespace UkTax.Loop
open UkTax

def burden (h : Household) : Int :=
  let r := householdCalc p2025 Reading.hmrc h
  r.incomeTax + r.cgt + r.employeeSocial - r.benefits

def one (x : Person) (k : Nat := 0) : Household :=
  { adults := [{ wages := x.employment }], children := List.replicate k 5, personsOverride := some [x] }
def two (x y : Person) (married : Bool := true) : Household :=
  { adults := [{ wages := x.employment }, { wages := y.employment }], married, personsOverride := some [x, y] }

/-- C01: salary sacrifice of £25,140 at £125,140 saves £15,586.80 = 62 % (ITA s. 35(2) taper + 40 % + 2 % NI). -/
theorem sacrifice_taper :
    burden (one { employment := 125140 }) - burden (one { employment := 100000 }) = 1558680 := by decide

/-- C03: two children, £80,000: sacrificing £20,000 saves £10,651 (42 % + the whole HICBC of £2,251). -/
theorem sacrifice_hicbc :
    burden (one { employment := 80000 } 2) - burden (one { employment := 60000 } 2) = 1065100 := by decide

/-- C12: moving £6,000 interest and £6,000 dividends from a £90,000 earner to a spouse with no income saves
£4,456.25 (spouse's allowance, starting rate, PSA £1,000, dividend allowance). -/
theorem spouse_transfer :
    burden (two { employment := 90000, interest := 6000, dividends := 6000 } {})
      - burden (two { employment := 90000 } { interest := 6000, dividends := 6000 }) = 445625 := by decide

/-- C34: a buy-to-let (£40,000 before £20,000 of interest, ITTOIA s. 272A) held by the non-earning spouse instead of
a £50,000 earner saves £10,460. -/
theorem btl_spouse :
    burden (two { employment := 50000, property := 40000, financeCosts := 20000 } {})
      - burden (two { employment := 50000 } { property := 40000, financeCosts := 20000 }) = 1046000 := by decide

/-- C40: Gift Aid of £1,600 keeps a £52,000 earner basic-rate (s. 414(2)(b)), so the marriage allowance (s. 55B(2)(b))
is available: marrying saves £252; without the gift it saves nothing. -/
theorem giftaid_unlocks_ma :
    burden (two {} { employment := 52000, giftAid := 1600 } false)
      - burden (two {} { employment := 52000, giftAid := 1600 } true) = 25200 ∧
    burden (two {} { employment := 52000 } false) - burden (two {} { employment := 52000 } true) = 0 := by decide

/-- A Scottish taxpayer (ITA s. 11A) with one adult's figures. -/
def oneS (x : Person) : Household :=
  { adults := [{ wages := x.employment }], scottish := true, personsOverride := some [{ x with scottish := true }] }

/-- **N1 (novel).** Scottish taxpayer, dividends £55,000, wages £47,000 (adjusted net income £102,000): £1,000 more
wages raises income tax + Class 1 by £1,085 (108.5 %); the same person in the rest of the UK pays £755 more (75.5 %).
Cause: non-savings income is taxed at the Scottish higher rate (42 %, from £31,092 of taxable income) while
dividends use the UK basic rate limit (£37,700, ITA s. 10, s. 13, stacked on top, s. 16); each £1 of income inside
the allowance taper (s. 35(2)) adds £1.50 of taxable income, so 1.5 × (42 % + 25 % dividend upper-ordinary) =
100.5 %, plus 8 % NI. -/
theorem n1_scot_dividend_straddle :
    burden (oneS { employment := 47000, dividends := 55000 }) - burden (oneS { employment := 46000, dividends := 55000 }) = 108500 ∧
    burden (one { employment := 47000, dividends := 55000 }) - burden (one { employment := 46000, dividends := 55000 }) = 75500 := by decide

/-- **N1b (novel).** The same Scottish taxpayer: a £1,000 Gift Aid payment (£1,250 to the charity) cuts income tax by
£1,006.25, and a £1,000 gross relief-at-source contribution (the member pays £800) cuts the burden by £1,005
(£805 off the liability, £200 into the pension). Both leave the giver/saver with more cash than before. -/
theorem n1b_scot_free_relief :
    burden (oneS { employment := 47000, dividends := 55000 }) - burden (oneS { employment := 47000, dividends := 55000, giftAid := 1000 }) = 100625 ∧
    burden (oneS { employment := 47000, dividends := 55000 }) - burden (oneS { employment := 47000, dividends := 55000, rasGross := 1000 }) = 100500 := by decide

end UkTax.Loop
