import TaxKernel.World

/-!
# Eswatini: normal tax on natural persons, year of assessment 1 July 2025 - 30 June 2026

Access tier B (the statute is reached, but its rate clause is dated to a past year and the amending Act's commencement
notice was not reached). Sources served by the Eswatini Revenue Service (ers.org.sz "Tax Legislation", fetched from the
laptop 2026-11-20 because the build server times out; sha256 in `sz/law/SHA256SUMS`):
* Income Tax Order 1975 (King's Order in Council No. 21 of 1975), updated to the Income Tax (Amendment) Acts 2011 and
  2013: s. 8 (1) (a) rebate "not exceeding the sum specified in the Third Schedule"; s. 2 (6) "normal year of
  assessment" means "the period of twelve months ending on 30 June"; s. 12 (1) (qq): interest or dividends "not
  exceeding twenty thousand emalangeni" exempt (for listed sources).
* Income Tax (Amendment) Act, 2023 (Act No. 20 of 2023, assent 14 July 2023; s. 1 (2): in force "on a date to be
  determined by the Minister by Notice in the Gazette", notice not reached), scanned, OCR'd, numbers checked on the page
  image: s. 39 replaces the Third Schedule: Part I para 1: "the rates of tax to be levied for the year of assessment
  ending 30 June 2023 are as follows — ... (b) ... as prescribed in Part II ... reduced by way of a rebate — (i) of an
  amount not exceeding the sum of eight thousand two hundred Emalangeni (E8,200) in any year of assessment; and, (ii)
  of an additional amount not exceeding two thousand seven hundred Emalangeni if the person is over the age of sixty
  (60) years"; "(e) ... for each Lilangeni of dividend income, ten per cent (10%); (f) ... for each Lilangeni of
  taxable interest income, ten per cent (10%)". Part II: "0 – 100 000: 0+20% of the excess over 0; 100 000 – 150 000:
  20 000 + 25% ...; 150 000 – 200 000: 32 500 + 30% ...; 200 000 – 250 000: 47 500 + 33% of taxable income in excess
  of 200 000" (the table stops at E250 000: FINDINGS F1).
* The 1975 Order as updated to 2013 prints the same Part II with an open top row ("200 000 - 47 500 + 33%", replaced
  A. 1/2013) and the same rebate ("two thousand seven emalangeni" in the 2013 text: FINDINGS F2); ERS's "Rates and
  Thresholds" page (official secondary) prints the open top row. The model uses 33 % above E200 000 with no ceiling.
Unit: individual. Not modelled: other pension deductions, the (qq) exemption conditions.
W5 pattern A (2026-11-20): Eswatini National Provident Fund. Eswatini National Provident Fund (Statutory
Contributions) Regulations, 2025 (Legal Notice No. 5 of 2025, made under ss. 14 and 15 of the Swaziland National
Provident Fund Order, 1974; in force 1 January 2025), as reproduced by the Fund (enpf.co.sz public notice, fetched
2026-11-20, `sz/law/w5/`): reg. 2 (1) "(a) Four Thousand Emalangeni (E4,000.00) or less during any calendar month for
2025; (b) Four Thousand Three Hundred Emalangeni (E4,300.00) or less during any calendar month for 2026"; reg. 2 (2)
wages in excess "shall be disregarded". The rate is the Fund's 5 % + 5 %: "the maximum contribution per employee will
increase from E400.00 to E430.00 per month ( 215:215 )" (the Order's rate section itself was not reached). Year
2025/26 = 6 months at E4,000 + 6 at E4,300: annual ceiling E49,800 (even monthly pay). Deductible: the ENPF is a
"provident ... fund established by law", hence a "pension fund" (s. 2), and s. 14 (1) (i) allows "any sum not exceeding
ten per cent of an employee's pensionable salary contributed ... to any pension fund"; Fourth Schedule para 2 (4)
computes employees' tax after the employee's pension-fund contribution. Input `"w5Contrib": false` drops both.
D9 review: the monthly caps are applied month by month (`enpfMonthly`; was an annual cap of E49,800).
-/

namespace SzTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 2000), (100000, 2500), (150000, 3000), (200000, 3300)]

#guard [(100000, 20000), (150000, 32500), (200000, 47500)].all fun (t, b) => sched.ticks t = b * BP

/-- ENPF employee 5 % on wages up to E4,000 a month (Jul-Dec 2025) and E4,300 (Jan-Jun 2026). -/
def enpf : Contribution := Contribution.flatCapped "ENPF" 500 (6 * 4000 + 6 * 4300)

#guard enpf.amount 48000 = 2400 ∧ enpf.amount 49800 = 2490 ∧ enpf.amount 120000 = 2490   -- 6 x 200 + 6 x 215

/- D9 review (2026-11-20): reg. 2 (1) caps each MONTH ("E4,000.00 or less during any calendar month for 2025"; E4,300
for 2026) and reg. 2 (2) disregards the excess month by month. With even monthly pay w / 12 the year 2025/26 is six
months capped at 4,000 and six at 4,300: 5 % x (6 x min (w / 12, 4,000) + 6 x min (w / 12, 4,300))
= 5 % x (min (w, 48,000) + min (w, 51,600)) / 2. The annual cap of `enpf` above (5 % of min (w, 49,800)) equals it
only at or below 48,000 and at or above 51,600; between them it overstates the contribution (49,800: 2,490 against
2,445). Input `"szEnpfAnnualCap": true` restores the pre-review annual cap. -/
def enpfMonthly (w : Int) : Int := divR .down (500 * (min (pos w) 48000 + min (pos w) 51600)) (2 * BP)

#guard enpfMonthly 48000 = 2400 ∧ enpfMonthly 49800 = 2445 ∧ enpfMonthly 51600 = 2490 ∧ enpfMonthly 120000 = 2490
#guard enpfMonthly 30000 = 1500 ∧ enpfMonthly 0 = 0   -- 5 % below the cap
#guard (List.range 200).all fun i => let w : Int := 300 * i; (w ≤ 48000 ∨ w ≥ 51600) → enpfMonthly w = enpf.amount w

def rebate (age : Nat) : Int := 8200 + (if age > 60 then 2700 else 0)
def divIntRate : Int := 1000

def personTax (age : Nat) (ti : Int) : Int := pos (sched.tax Rule.unitDown (pos ti) - rebate age)

/- ERS page: "The rates are applicable on the amount exceeding E41 000" = 8 200 / 20 %. -/
#guard personTax 40 41000 = 0 ∧ personTax 40 41010 > 0

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let w5 := (c.bool? "w5Contrib").getD true
  let annualCap := (c.bool? "szEnpfAnnualCap").getD false
  let fund (a : Adult) : Int := if w5 then (if annualCap then enpf.amount a.wages else enpfMonthly a.wages) else 0
  let rows := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    (a.age, pos (a.wages - fund a + a.selfEmployment + a.pension + share c.rentalIncome i))
  let es := sumInts (c.adults.map fund)
  let it := sumInts (rows.map fun r => personTax r.1 r.2)
  let di := divR .down (divIntRate * (c.dividends + c.interest)) BP
  Out.make c "SZ" "SZL" it (surtaxes := [("dividendAndInterestTax", di)]) (employeeSocial := es)
    (detail := [Out.d "enpf" es, Out.d "taxableIncome" (sumInts (rows.map (·.2))), Out.d "taxBeforeCredits" (sumInts (rows.map fun r => sched.tax Rule.unitDown r.2)),
      Out.dStr "note" "Income Tax Order 1975 Third Schedule (Act 20 of 2023 s. 39 / 2013 text): 20-33 %, rebate E8 200 (+E2 700 over 60); dividends and interest 10 %"])
    (unsupported := (if c.capitalGains ≠ 0 then ["capital gains: not modelled"] else []) ++
      (if c.pensionContributions ≠ 0 then ["pension contribution deduction not modelled"] else []) ++
      [       "s. 12 (1) (qq) exemption of E20 000 of interest/dividends from listed sources not applied",
       "Act 20 of 2023 commencement notice not reached; its rate clause names the year ending 30 June 2023"])

def country : Country := { code := "SZ", name := "Eswatini (year of assessment 2025/26)", currency := "SZL", year := "2025/26", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end SzTax
