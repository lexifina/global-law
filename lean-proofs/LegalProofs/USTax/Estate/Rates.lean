/-!
# Federal estate and gift tax: the rate table and the amounts that change by year

* **§2001(c), the unified rate table.** One table serves the estate tax (§2001), the gift tax (§2502(a)) and, through
  its top rate, the generation-skipping transfer tax (§2641). From 2013 on (the American Taxpayer Relief Act of 2012,
  Pub. L. 112-240, §101(c)) the top bracket is 40% over $1,000,000. For 2011 and 2012 (Pub. L. 111-312, §302(a)(2))
  the table stopped at 35% over $500,000.
* **§2010(c)(3), the basic exclusion amount.** $5,000,000 for 2011, indexed for inflation; doubled for 2018–2025
  (Pub. L. 115-97, §11061, §2010(c)(3)(C)); $15,000,000 for 2026 (Pub. L. 119-21, §70106, which rewrote
  §2010(c)(3)(A) and indexes it from 2027 with 2025 as the base year).
* **§2503(b), the annual exclusion.** $10,000 indexed in $1,000 steps (§2503(b)(2)).

The yearly amounts are those the IRS published:

| year | basic exclusion | annual exclusion | source |
|------|-----------------|------------------|--------|
| 2012 | 5,120,000 | 13,000 | Rev. Proc. 2011-52 |
| 2013 | 5,250,000 | 14,000 | Rev. Proc. 2013-15 (exclusion), Rev. Proc. 2012-41 (annual) |
| 2014 | 5,340,000 | 14,000 | Rev. Proc. 2013-35 |
| 2015 | 5,430,000 | 14,000 | Rev. Proc. 2014-61 |
| 2016 | 5,450,000 | 14,000 | Rev. Proc. 2015-53 |
| 2017 | 5,490,000 | 14,000 | Rev. Proc. 2016-55 |
| 2018 | 11,180,000 | 15,000 | Rev. Proc. 2018-18 (exclusion), Rev. Proc. 2017-58 (annual) |
| 2019 | 11,400,000 | 15,000 | Rev. Proc. 2018-57 |
| 2020 | 11,580,000 | 15,000 | Rev. Proc. 2019-44 |
| 2021 | 11,700,000 | 15,000 | Rev. Proc. 2020-45 |
| 2022 | 12,060,000 | 16,000 | Rev. Proc. 2021-45 |
| 2023 | 12,920,000 | 17,000 | Rev. Proc. 2022-38 |
| 2024 | 13,610,000 | 18,000 | Rev. Proc. 2023-34 |
| 2025 | 13,990,000 | 19,000 | Rev. Proc. 2024-40 |
| 2026 | 15,000,000 | 19,000 | §2010(c)(3)(A) as amended by Pub. L. 119-21; Rev. Proc. 2025-32 |

Years before 2011 appear only as *prior periods* of a gift-tax history, which §2505(a) and §2001(g) recompute at the
current year's rates; their exclusion amounts are the "Table of Basic Exclusion and Credit Amounts" in the 2025
Instructions for Form 709 and the 2026 Instructions for Form 706. The estate tax of a decedent who died before 2011 is
not modelled, and neither is the inflation adjustment for years after 2026 (those years use the 2026 figures).

All amounts are whole dollars; each percentage is rounded to the nearest dollar, halves up, as the forms do.
-/

namespace Legal.USTax.Estate

/-- `x` percent of `r`, to the nearest dollar. -/
def pct (x r : Int) : Int := (x * r + 50) / 100

/-- §2001(c) as in force from 2013. -/
def tent40 (x : Int) : Int :=
  if x ≤ 0 then 0
  else if x ≤ 10000 then pct x 18
  else if x ≤ 20000 then 1800 + pct (x - 10000) 20
  else if x ≤ 40000 then 3800 + pct (x - 20000) 22
  else if x ≤ 60000 then 8200 + pct (x - 40000) 24
  else if x ≤ 80000 then 13000 + pct (x - 60000) 26
  else if x ≤ 100000 then 18200 + pct (x - 80000) 28
  else if x ≤ 150000 then 23800 + pct (x - 100000) 30
  else if x ≤ 250000 then 38800 + pct (x - 150000) 32
  else if x ≤ 500000 then 70800 + pct (x - 250000) 34
  else if x ≤ 750000 then 155800 + pct (x - 500000) 37
  else if x ≤ 1000000 then 248300 + pct (x - 750000) 39
  else 345800 + pct (x - 1000000) 40

/-- §2001(c) for 2011 and 2012: the same rows up to $500,000, then 35%. -/
def tent35 (x : Int) : Int :=
  if x ≤ 0 then 0
  else if x ≤ 10000 then pct x 18
  else if x ≤ 20000 then 1800 + pct (x - 10000) 20
  else if x ≤ 40000 then 3800 + pct (x - 20000) 22
  else if x ≤ 60000 then 8200 + pct (x - 40000) 24
  else if x ≤ 80000 then 13000 + pct (x - 60000) 26
  else if x ≤ 100000 then 18200 + pct (x - 80000) 28
  else if x ≤ 150000 then 23800 + pct (x - 100000) 30
  else if x ≤ 250000 then 38800 + pct (x - 150000) 32
  else if x ≤ 500000 then 70800 + pct (x - 250000) 34
  else 155800 + pct (x - 500000) 35

/-- §2001(c) for 2007–2009 (Pub. L. 107-16, §511): the same rows up to $1,000,000, then 41% to $1,250,000, 43% to
$1,500,000 and 45% above. Used for gift years in that range (one Tax Court case below is a 2007 gift). -/
def tent45 (x : Int) : Int :=
  if x ≤ 1000000 then tent40 x
  else if x ≤ 1250000 then 345800 + pct (x - 1000000) 41
  else if x ≤ 1500000 then 448300 + pct (x - 1250000) 43
  else 555800 + pct (x - 1500000) 45

def top35 (y : Nat) : Bool := y == 2011 || y == 2012
def top45 (y : Nat) : Bool := 2007 ≤ y && y ≤ 2009

/-- The tentative tax under the table in force in year `y`. Other years before 2013 use the 2013 table: they are
outside the model except as prior periods of a gift history, which the law recomputes at current rates anyway. -/
def tentative (y : Nat) (x : Int) : Int := if top35 y then tent35 x else if top45 y then tent45 x else tent40 x

/-- The top rate of §2001 in year `y` (the GST rate under §2641(b)), in percent. -/
def maxRate (y : Nat) : Int := if top35 y then 35 else if top45 y then 45 else 40

/-- §2010(c)(3) basic exclusion amount (for years before 2011, the gift-tax exclusion the Form 709 table gives). -/
def bea (y : Nat) : Int :=
  if y ≤ 1976 then 0
  else if y ≤ 1977 then 120667   -- 1977, third and fourth quarters
  else if y ≤ 1978 then 134000
  else if y ≤ 1979 then 147333
  else if y ≤ 1980 then 161563
  else if y ≤ 1981 then 175625
  else if y ≤ 1982 then 225000
  else if y ≤ 1983 then 275000
  else if y ≤ 1984 then 325000
  else if y ≤ 1985 then 400000
  else if y ≤ 1986 then 500000
  else if y ≤ 1997 then 600000
  else if y ≤ 1998 then 625000
  else if y ≤ 1999 then 650000
  else if y ≤ 2001 then 675000
  else if y ≤ 2010 then 1000000
  else if y ≤ 2011 then 5000000
  else if y ≤ 2012 then 5120000
  else if y ≤ 2013 then 5250000
  else if y ≤ 2014 then 5340000
  else if y ≤ 2015 then 5430000
  else if y ≤ 2016 then 5450000
  else if y ≤ 2017 then 5490000
  else if y ≤ 2018 then 11180000
  else if y ≤ 2019 then 11400000
  else if y ≤ 2020 then 11580000
  else if y ≤ 2021 then 11700000
  else if y ≤ 2022 then 12060000
  else if y ≤ 2023 then 12920000
  else if y ≤ 2024 then 13610000
  else if y ≤ 2025 then 13990000
  else 15000000

/-- §2503(b) annual exclusion per donee. -/
def annualExclusion (y : Nat) : Int :=
  if y ≤ 2001 then 10000
  else if y ≤ 2005 then 11000
  else if y ≤ 2008 then 12000
  else if y ≤ 2012 then 13000
  else if y ≤ 2017 then 14000
  else if y ≤ 2021 then 15000
  else if y ≤ 2022 then 16000
  else if y ≤ 2023 then 17000
  else if y ≤ 2024 then 18000
  else 19000

/-- §2010(c)(1): the applicable credit amount is the tentative tax on the applicable exclusion amount. -/
def credit (y : Nat) (exclusion : Int) : Int := tentative y exclusion

end Legal.USTax.Estate
