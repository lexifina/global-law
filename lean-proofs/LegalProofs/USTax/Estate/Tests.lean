import LegalProofs.USTax.Estate.Transfer

/-!
# Tests against the IRS's own figures, then hand computations from the statute

Sources: 2026 Instructions for Form 706, "Table of Basic Exclusion and Credit Amounts" (column "Credit Equivalent at
2026 Rates"); 2025 Instructions for Form 709, Table for Computing Gift Tax and the Worksheet for Schedule B, line 1,
column (c), Examples 1 and 3; the Rev. Procs listed in `Rates.lean`. Where the IRS gives no worked numbers the expected
value is computed by hand in the comment above the test.
-/

namespace Legal.USTax.Estate.Tests
open Legal.USTax.Estate

/-! ## The Form 706 table: every exclusion amount since 1977, and its credit at 2026 rates

Each row is the tentative tax at today's rates on that period's exclusion: it exercises every bracket of §2001(c). -/

def table706 : List (Nat × Int × Int) := [
  (1977, 120667, 30000), (1978, 134000, 34000), (1979, 147333, 38000), (1980, 161563, 42500),
  (1981, 175625, 47000), (1982, 225000, 62800), (1983, 275000, 79300), (1984, 325000, 96300),
  (1985, 400000, 121800), (1986, 500000, 155800), (1987, 600000, 192800), (1997, 600000, 192800),
  (1998, 625000, 202050), (1999, 650000, 211300), (2000, 675000, 220550), (2001, 675000, 220550),
  (2002, 1000000, 345800), (2010, 1000000, 345800), (2011, 5000000, 1945800), (2012, 5120000, 1993800),
  (2013, 5250000, 2045800), (2014, 5340000, 2081800), (2015, 5430000, 2117800), (2016, 5450000, 2125800),
  (2017, 5490000, 2141800), (2018, 11180000, 4417800), (2019, 11400000, 4505800), (2020, 11580000, 4577800),
  (2021, 11700000, 4625800), (2022, 12060000, 4769800), (2023, 12920000, 5113800), (2024, 13610000, 5389800),
  (2025, 13990000, 5541800), (2026, 15000000, 5945800)]

/-- Every row: the model's exclusion for the year is the table's, and its credit at 2026 rates is the table's. -/
theorem form706_table : table706.all (fun (y, e, c) => bea y == e && credit 2026 e == c) = true := by decide

/-- 1977, first two quarters: a $30,000 exemption-equivalent, a $6,000 credit. -/
theorem early_1977 : tentative 2026 30000 = 6000 := by decide

/-- 2025 Instructions for Form 709: "The basic credit amount for 2025 is $5,541,800." -/
theorem credit_2025 : credit 2025 (bea 2025) = 5541800 := by decide

/-- 2026 Instructions for Form 706, line 9e: "enter $5,945,800". -/
theorem credit_2026 : credit 2026 (bea 2026) = 5945800 := by decide

/-- Under the 2012 table (35% over $500,000) the 2012 credit was $1,772,800, and 2011's $1,730,800
(2012 and 2011 Instructions for Form 706). -/
theorem credit_2012_own_rates : credit 2012 (bea 2012) = 1772800 ∧ credit 2011 (bea 2011) = 1730800 := by decide

/-- The annual exclusion and the basic exclusion, year by year, as the Rev. Procs publish them. -/
theorem revproc_amounts :
    [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026].map
      (fun y => (bea y, annualExclusion y)) =
    [(5120000, 13000), (5250000, 14000), (5340000, 14000), (5430000, 14000), (5450000, 14000), (5490000, 14000),
     (11180000, 15000), (11400000, 15000), (11580000, 15000), (11700000, 15000), (12060000, 16000),
     (12920000, 17000), (13610000, 18000), (13990000, 19000), (15000000, 19000)] := by decide

/-! ## Form 709 Schedule B worksheet (2025 Instructions)

Example 1: gifts of $800,000 (2004), $300,000 (2007) and $200,000 (2009). Credit allowable $267,800, $78,000 and $0;
$345,800 in all. -/

def ex1 : List Period := [⟨2004, 800000, 0⟩, ⟨2007, 300000, 0⟩, ⟨2009, 200000, 0⟩]

theorem schedB_example1 : (schedule 2025 ex1).map Row.credit = [267800, 78000, 0] ∧
    ((schedule 2025 ex1).map Row.credit).sum = 345800 := by decide

/-- Example 3: a $10,000,000 gift in 2011 with $4,000,000 of DSUE available to it: applicable exclusion $9,000,000,
credit allowable $3,545,800. -/
theorem schedB_example3 : (schedule 2025 [⟨2011, 10000000, 4000000⟩]).map Row.credit = [3545800] := by decide

/-! ## Hand computations from the statute -/

/-- §2503(b), §2513: a married couple gives a child $38,000 in 2025; split, each spouse's $19,000 is excluded. -/
theorem split_gift : taxableGifts 2025 (split [{ value := 38000 }]) = 0 ∧ taxableGifts 2025 [{ value := 38000 }] = 19000 := by
  decide

/-- A gift in trust of a future interest gets no exclusion; a gift to a spouse or to charity is deducted. -/
theorem future_spouse_charity :
    taxableGifts 2025 [{ value := 19000, present := false }, { value := 5000000, spouse := true },
      { value := 1000000, charity := true }] = 19000 := by decide

/-- A parent gives a child $14,000,000 in 2025 and $2,000,000 more in 2026. 2025: taxable $13,981,000, tentative tax
$5,538,200, all absorbed by the $5,541,800 credit. 2026: taxable $1,981,000 (after the $19,000 exclusion), tax on it
$792,400; the 2026 credit, $5,945,800, less $5,538,200 used, leaves $407,600: $384,800 to pay, which is 40% of the
$962,000 by which lifetime taxable gifts exceed $15,000,000. -/
theorem gifts_into_2026 :
    giftTax [⟨2025, taxableGifts 2025 [{ value := 14000000 }], 0⟩] = 0 ∧
    giftTax [⟨2025, 13981000, 0⟩, ⟨2026, taxableGifts 2026 [{ value := 2000000 }], 0⟩] = 384800 := by decide

/-- A 2025 death: gross estate $20,000,000, §2053 expenses $500,000, $1,000,000 to charity. Taxable estate
$18,500,000; tax 40% of ($18,500,000 − $13,990,000) = $1,804,000. -/
def estateA : Death := { year := 2025, gross := 20000000, expenses := 500000, charitable := 1000000 }
theorem estate_a : estateA.taxableEstate = 18500000 ∧ estateA.tax = 1804000 := by decide

/-- The same estate after a $3,000,000 taxable gift in 2020. The gift's tax at 2025 rates ($1,145,800) was covered by
the credit, so nothing is subtracted; the base is $21,500,000 and the tax 40% of $7,510,000 = $3,004,000. The gift
used exclusion; it did not escape the tax. -/
def estateB : Death := { estateA with gifts := [⟨2020, 3000000, 0⟩] }
theorem estate_b : estateB.giftTaxPayable = 0 ∧ estateB.base = 21500000 ∧ estateB.tax = 3004000 := by decide

/-- Portability. A husband dies in 2016 leaving a $2,000,000 taxable estate and everything else to his wife: his DSUE
is $5,450,000 − $2,000,000 = $3,450,000. She dies in 2026 with $20,000,000: exclusion $18,450,000, tax 40% of
$1,550,000 = $620,000. Without the election she would pay 40% of $5,000,000 = $2,000,000. -/
def husband : Death := { year := 2016, gross := 9000000, marital := 7000000 }
def wife : Death := { year := 2026, gross := 20000000, dsue := husband.dsueOut }
theorem portability_example : husband.dsueOut = 3450000 ∧ wife.exclusion = 18450000 ∧ wife.tax = 620000 ∧
    ({ wife with dsue := 0 } : Death).tax = 2000000 := by decide

/-- GST: a 2025 direct skip of $1,000,000 to a grandchild with $600,000 of exemption allocated. Applicable fraction
0.600, inclusion ratio 0.400, rate 40% × 0.4 = 16%: $160,000. Fully exempt: nothing. In 2012 the rate was 35%. -/
theorem gst_example : gstTax 2025 1000000 600000 = 160000 ∧ gstTax 2025 1000000 1000000 = 0 ∧
    gstTax 2012 1000000 0 = 350000 := by decide

end Legal.USTax.Estate.Tests
