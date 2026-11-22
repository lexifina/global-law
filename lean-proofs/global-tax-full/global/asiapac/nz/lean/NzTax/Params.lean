import TaxKernel

/-!
# New Zealand: the numbers for the income years 2025-26 (main) and 2024-25 (composite year)

**Unit of account.** New Zealand tax is computed in dollars and cents (returns, PAYE and Working for Families all
carry cents), so money here is `Int` **cents** and rates are basis points; a tick is cents × bp. The canonical
household arrives in whole dollars and is multiplied by 100.

**Which year.** The OECD's "2025" for New Zealand is the income year 1 April 2025 - 31 March 2026: its S100 income
tax (17,291.59 at the average wage 83,073) is exactly the full-year 2025-26 schedule below, and not the 2024-25
composite schedule (17,636.60). 2025-26 is the main year; 2024-25 (thresholds changed on 31 July 2024, so a year of
composite rates, IETC composite formula and part-year Working for Families rates) is modelled for the versioned-law
findings (`year: 2024` in the household).

**Sources.** The Income Tax Act 2007 is not in the Global law corpus (its New Zealand record holds 50 acts, not the
tax Acts), and legislation.govt.nz and NZLII refuse automated fetches (AWS WAF challenge, HTTP 202/403; Cloudflare
challenge), which this project does not bypass. Every number below is therefore cited to Inland Revenue's own
publications, saved in `cmp20/anglo/nz/refs/` with their URLs in `refs/SOURCES.md`, and to the section of the Act
those publications name. The Accident Compensation Act 2001 (ss. 219-221) is read in Global law.

| Number | Provision (as IRD names it) | Source in refs/ |
|---|---|---|
| rates 10.5 / 17.5 / 30 / 33 / 39 %, thresholds 15,600 / 53,500 / 78,100 / 180,000 | ITA 2007 sch 1 pt A (Taxation (Budget Measures) Act 2024, from 31 July 2024; full year from 2025-26) | ird_rates.txt; sr_budget_2024.txt p. 6 |
| 2024-25 composite rates 10.5 / 12.82 / 17.5 / 21.64 / 30 / 30.99 / 33 / 39 % | ITA 2007 sch 1 (composite, 2024-25 only) | sr_budget_2024.txt p. 8; ird_rates.txt |
| IETC $520, from $24,000, abated 13 c above $66,000, nil above $70,000 | ss LC 13-LC 15 | sr_budget_2024.txt p. 11; ird_ietc.txt; spec2026_v8.txt s. 5.3 |
| IETC 2024-25: old settings 44,000 / 48,000 for 121 days, new for 244 days | ss LC 13-LC 15 (composite) | sr_budget_2024.txt pp. 12-14 |
| FTC $7,524 eldest, $6,130 each other child | ITA 2007 subpart MD (section not named by IRD) | wb_ftc_2025.txt (IRD page as archived 14 Oct 2025) |
| IWTC $5,070 (1-3 children) + $780 each further child | s MD 10 | wb_iwtc_2025.txt; sr_budget_2024.txt p. 3 |
| IWTC 2024-25: $3,770 to 30 July 2024, $5,070 after | ss MD 10, MF 4J, MF 4K | sr_budget_2024.txt p. 3 |
| FTC/IWTC abatement 27 % above $42,700 of family scheme income | ITA 2007 subpart MD (section not named by IRD) | wb_ftc_2025.txt; ir271-2026.txt |
| MFTC: family income after tax topped up to $35,316 | s ME 1 | wb_mftc_2025.txt; sr_budget_2024.txt p. 4 |
| Best Start $3,838 a year (73 a week); years 2-3 abated 21 % above $79,000 | ITA 2007 subpart MD (section not named by IRD) | ir271-2026.txt p. 2 |
| ACC earners' levy 1.67 % (incl. GST) to $152,790 (max $2,551.59); 2024-25 1.60 % to $142,283 | Accident Compensation Act 2001 ss 219-221; levy regulations | spec2026_v8.txt s. 2.1 |
| student loan 12 % above $24,128 | Student Loan Scheme Act 2011 | spec2026_v8.txt s. 2.2 |
-/

namespace NzTax
open TaxKernel

/-- Dollars to cents. -/
def nzd (x : Int) : Int := 100 * x

structure Params where
  year : String
  /-- ITA 2007 sch 1 pt A: the basic rates on taxable income (cents thresholds, bp). -/
  sched : Schedule
  /-- ss LC 13-LC 15 (one setting; 2024-25 has two, see `ietc2024`). Dollars. -/
  ietcMax : Int
  ietcFloor : Int
  ietcAbateStart : Int
  ietcMaxIncome : Int
  /-- 13 cents a dollar (bp). -/
  ietcAbateRate : Int
  /-- Working for Families (dollars a year). -/
  ftcEldest : Int
  ftcOther : Int
  iwtcBase : Int
  iwtcExtra : Int
  wffAbateStart : Int
  /-- 2700 bp = 27 %. -/
  wffAbateRate : Int
  mftcThreshold : Int
  bestStart : Int
  bestStartAbateStart : Int
  bestStartAbateRate : Int
  /-- ACC earners' levy (bp, incl. GST) and maximum liable earnings (dollars). -/
  accRate : Int
  accMaxEarnings : Int
  /-- Student loan repayment threshold (dollars) and rate (bp). -/
  slThreshold : Int
  slRate : Int
  deriving Repr

/-- 2025-26: ITA 2007 sch 1 pt A as amended by the Taxation (Budget Measures) Act 2024 (IRD, "Tax rates for
individuals": "From 1 April 2025 ... 0 - $15,600 10.5% ... $15,601 - $53,500 17.5% ... $53,501 - $78,100 30% ...
$78,101 - $180,000 33% ... $180,001 and over 39%"). Thresholds in cents. -/
def sched2025 : Schedule :=
  Schedule.ofUpper [(nzd 15600, 1050), (nzd 53500, 1750), (nzd 78100, 3000), (nzd 180000, 3300)] 3900

/-- 2024-25: the composite rates for the year of the 31 July 2024 change (Special report, Taxation (Budget Measures)
Act 2024, p. 8: "0 – $14,000 10.5% ... $14,001 – $15,600 12.82% ... $15,601 – $48,000 17.5% ... $48,001 – $53,500
21.64% ... $53,501 – $70,000 30% ... $70,001 – $78,100 30.99% ... $78,101 – $180,000 33% ... $180,001+ 39%"). -/
def sched2024 : Schedule :=
  Schedule.ofUpper [(nzd 14000, 1050), (nzd 15600, 1282), (nzd 48000, 1750), (nzd 53500, 2164),
    (nzd 70000, 3000), (nzd 78100, 3099), (nzd 180000, 3300)] 3900

/-- The schedule before 31 July 2024 (2021-22 to the old part of 2024-25; Special report p. 6 "Previous threshold"). -/
def schedOld : Schedule :=
  Schedule.ofUpper [(nzd 14000, 1050), (nzd 48000, 1750), (nzd 70000, 3000), (nzd 180000, 3300)] 3900

def p2025 : Params :=
  { year := "2025-26", sched := sched2025,
    -- IETC: Special report p. 11 "13 cents per dollar earned over $66,000 ... $70,000"; IRD IETC page "$24,000
    -- and $66,000 – you get $10 per week ... reduces by 13 cents for every dollar you earn over $66,000".
    ietcMax := 520, ietcFloor := 24000, ietcAbateStart := 66000, ietcMaxIncome := 70000, ietcAbateRate := 1300,
    -- FTC: IRD "Family tax credit" (archived 2025-10-14): "Oldest child $7,524 Every other child $6,130";
    -- "subtracting $42,700, then multiplying the difference by 27%".
    ftcEldest := 7524, ftcOther := 6130,
    -- IWTC: IRD "In-work tax credit" (archived 2025-08-17): "If you have 1, 2, or 3 children, your in-work tax
    -- credit will be $5,070 ... plus $780 for every child after that".
    iwtcBase := 5070, iwtcExtra := 780,
    wffAbateStart := 42700, wffAbateRate := 2700,
    -- MFTC: IRD "Minimum family tax credit" (archived 2025-10-08): "top up your income to ensure you earn $ 35,316
    -- a year (after tax)".
    mftcThreshold := 35316,
    -- Best Start: IR271 (July 2025) p. 2: "$73 per week (up to $3,838 per year) per child"; "For every dollar over
    -- $79,000 your family's annual entitlement will be reduced by 21 cents".
    bestStart := 3838, bestStartAbateStart := 79000, bestStartAbateRate := 2100,
    -- ACC: IRD Payroll calculations and business rules specification 2025-26 (v0.8) s. 2.1: "levy rate per $100
    -- of liable earnings (incl. GST) at $1.67"; maximum liable earnings $152,790; maximum levy $2,551.59.
    accRate := 167, accMaxEarnings := 152790,
    -- Student loan: same specification s. 2.2: "annual repayment threshold $24,128 ... 12% per $ over".
    slThreshold := 24128, slRate := 1200 }

/-- 2024-25: the composite schedule; IETC new settings (the composite IETC is computed separately, `ietc2024`);
WFF rates as 2025-26 except the IWTC ($3,770 to 30 July 2024, then $5,070: s MD 10 with ss MF 4J-MF 4K) and the MFTC
threshold ($35,204 then $35,316) which are pro-rated by days; ACC 1.60 % to $142,283 (spec 2025-26 s. 2.1, "2024/25
(From) $142,283 ... Maximum ACC Earner Levy $2,276.52"). -/
def p2024 : Params :=
  { p2025 with year := "2024-25", sched := sched2024, accRate := 160, accMaxEarnings := 142283 }

/-- Days of the old and new settings in 2024-25 (Special report p. 13: "121/365 ... 244/365"). -/
def daysOld : Int := 121
def daysNew : Int := 244
def daysYear : Int := 365

/-- IWTC and MFTC before 31 July 2024 (Special report pp. 3-4). -/
def iwtcBaseOld : Int := 3770
def mftcThresholdOld : Int := 35204

/-- IETC old settings (to 30 July 2024): "$24,000 and $48,000 ... 13 cents per dollar earned over $44,000". -/
def ietcOldAbateStart : Int := 44000
def ietcOldMaxIncome : Int := 48000

/-- Imputation: IRD "Maximum imputation ratio": "Companies can attach up to 28 cents of imputation credit to each $1
of gross dividend ... written using the format '28:72'" (refs/ird_max_imputation.txt). A fully imputed cash dividend
`d` carries a credit of `28 d / 72`. Credits above the tax on the dividend are not refunded (they become a loss
carried forward; reported as `imputationCreditToLoss`). -/
def companyRate : Int := 2800

/-- Donation tax credit: IRD "Donation tax credits": "claim 1/3rd of the value of eligible donations ... You can only
claim donation receipts that add up to your total taxable income" (refs/ird_donation.txt). -/
def donationNum : Int := 1
def donationDen : Int := 3

/-! ## Income years 2022-23 and 2023-24 (round 3; OECD years 2022 and 2023)

Both years use the schedule before 31 July 2024 (`schedOld`) for the whole year and the IETC's old settings for the
whole year ($520 from $24,000, abated 13 cents above $44,000, nil above $48,000: `ietcOldAbateStart`,
`ietcOldMaxIncome`, Special report p. 11). Working for Families (sources saved with sha256 in
`cmp20/improve-anglo/refs/nz/`):
* family tax credit: Tax Information Bulletin Vol 34 No 11 (December 2022), "Income Tax (Tax Credit) Order 2022"
  (made under s MF 7, in force 1 April 2023): "Eldest child $6,642 $7,121; Subsequent child $5,412 $5,802; Best
  Start Tax Credit $3,388 $3,632" (2022-23 amounts, then 2023-24 amounts);
* in-work tax credit $3,770 for 1-3 children plus $780 for each further child (`iwtcBaseOld`; IR271 April 2022 and
  April 2023 tables: $72 a week, $87 with four children), abatement from $42,700 at 27 % (IR271 tables, unchanged);
* minimum family tax credit: IR271 (April 2022) "If your family income is below $32,864 a year, after tax"; IR271
  (April 2023) "below $34,216 a year, after tax";
* Best Start abatement from $79,000 at 21 cents (IR271 both years).
ACC earners' levy: IRD "ACC earners' levy rates" (`nz/refs/ird_acc_rates.txt`): 1 April 2022 - 31 March 2023 "$1.46
per $100", maximum earnings $136,544; 1 April 2023 - 31 March 2024 "$1.53", $139,384. The student loan threshold of
these years is not set (the 2025-26 one is kept; the output says so). -/

def p2023 : Params :=
  { p2025 with
    year := "2023-24"
    sched := schedOld
    ietcAbateStart := ietcOldAbateStart
    ietcMaxIncome := ietcOldMaxIncome
    ftcEldest := 7121
    ftcOther := 5802
    iwtcBase := iwtcBaseOld
    mftcThreshold := 34216
    bestStart := 3632
    accRate := 153
    accMaxEarnings := 139384 }

def p2022 : Params :=
  { p2023 with
    year := "2022-23"
    ftcEldest := 6642
    ftcOther := 5412
    mftcThreshold := 32864
    bestStart := 3388
    accRate := 146
    accMaxEarnings := 136544 }

/-- `year` is the year the income year starts (2025 = 2025-26, as the OECD's 2025); 2024 is the composite year. -/
def paramsFor (year : Nat) : Params :=
  if year == 2024 then p2024 else if year == 2023 then p2023 else if year ≤ 2022 then p2022 else p2025

end NzTax
