import UkTax.Basic

/-!
# The numbers Parliament fixed for the tax year 2025-26

Every amount below is copied from the provision that fixes it, in its text as in force on 6 April 2025
(legislation.gov.uk point-in-time XML, saved in `cmp/uk/refs/leg/`), or from the Finance Act or statutory
instrument that sets it for the year. Money in whole pounds, rates in basis points.

Where a number lives (this is part of the answer to "how are tax systems written"):

| Number | Provision | Set by |
|---|---|---|
| personal allowance £12,570 | ITA 2007 s. 35(1) | FA 2021 s. 5(2) (frozen 2022-23 to 2027-28) |
| income limit £100,000 | ITA 2007 s. 35(2) | FA 2009 s. 4 (never indexed) |
| blind person's allowance £3,130 | ITA 2007 s. 38(1) | S.I. 2025/53 (CPI indexation, s. 57) |
| basic rate limit £37,700 | ITA 2007 s. 10(5) | FA 2021 s. 5(1) (frozen) |
| higher rate limit £125,140 | ITA 2007 s. 10(5A) | a formula: 2 × s. 35(1) + s. 35(2) |
| starting rate limit for savings £5,000 | ITA 2007 s. 12(3) | FA 2025 s. 4 (frozen for the year) |
| savings allowance £1,000 / £500 / nil | ITA 2007 s. 12B(2)–(4) | FA 2016 s. 4 |
| dividend allowance £500 | ITA 2007 s. 13A(2) | FA 2023 s. 7 |
| basic / higher / additional rate 20 / 40 / 45 % | ITA 2007 s. 6(2) | FA 2025 s. 2 (annual charge) |
| savings rates 20 / 40 / 45 % | ITA 2007 s. 7A | FA 2025 s. 3(2) |
| dividend rates 8.75 / 33.75 / 39.35 % | ITA 2007 s. 8 | FA 2022 s. 4 |
| marriage allowance 10 % of s. 35(1), up to £10 | ITA 2007 s. 55B(4)(b), (5) | FA 2015 |
| married couple's allowance £11,270 / £4,360 / £37,700 | ITA 2007 ss. 43, 45, 46 | S.I. 2025/53 |
| HICBC threshold £60,000, step £200 | ITEPA 2003 s. 681B(1)(a), 681C(2) | F(No. 2)A 2024 s. 5 |
| child benefit £26.05 / £17.25 a week | S.I. 2006/965 reg. 2(1) | S.I. 2025/292 (from 7 April 2025) |
| CGT annual exempt amount £3,000 | TCGA 1992 s. 1K(2) | FA 2023 s. 8 |
| CGT rates 18 / 24 % | TCGA 1992 s. 1H(3) | FA 2025 s. 7 (disposals from 30 October 2024) |
| Class 1 primary 8 % / 2 % | SSCBA 1992 s. 8(2) | NICs (Reduction in Rates) Act 2024 s. 1 |
| primary threshold £242 / £1,048 / £12,570 | S.I. 2001/1004 regs. 10(c), 11(3) | NICs (Increase of Thresholds) Act 2022 |
| upper earnings limit £967 / £4,189 / £50,270 | S.I. 2001/1004 regs. 10(b), 11(2A) | S.I. 2021/157 |
| Class 4 6 % / 2 %, £12,570 / £50,270 | SSCBA 1992 s. 15(3), (3ZA) | NICs (Reduction in Rates) Act 2024; NICs (Increase of Thresholds) Act 2022 |
| small profits threshold £6,845, Class 2 £3.50 | SSCBA 1992 s. 11(4), (6) | S.I. 2025/288 |
| basic amount £3,600 (pension relief) | FA 2004 s. 190(2), (3) | FA 2004 |
-/

namespace UkTax

structure Params where
  taxYear : String
  /-- ITA 2007 s. 35(1): "a personal allowance of £12,570". -/
  personalAllowance : Int
  /-- s. 35(2): "adjusted net income exceeds £100,000 ... reduced by one-half of the excess". -/
  paIncomeLimit : Int
  /-- s. 38(1): "a blind person's allowance of £3,130". -/
  blindAllowance : Int
  /-- s. 10(5): "The basic rate limit is £37,700." -/
  basicRateLimit : Int
  /-- s. 12(3): "The starting rate limit for savings is £5,000." -/
  startingRateLimitSavings : Int
  /-- s. 12B(4), (3), (2): the savings allowance, £1,000 / £500 / nil. -/
  psaBasic : Int
  psaHigher : Int
  psaAdditional : Int
  /-- s. 13A(2), Step 1: "the first £500 of D is charged at the dividend nil rate". -/
  dividendAllowance : Int
  /-- s. 6(2) with FA 2025 s. 2: "the basic rate is 20%, the higher rate is 40%, the additional rate is 45%". -/
  basicRate : Int
  higherRate : Int
  additionalRate : Int
  /-- s. 7A with FA 2025 s. 3(2): the savings basic, higher and additional rates. -/
  savingsBasicRate : Int
  savingsHigherRate : Int
  savingsAdditionalRate : Int
  /-- s. 8(1)–(3): "The dividend ordinary rate is 8.75%", upper 33.75 %, additional 39.35 %. -/
  dividendOrdinaryRate : Int
  dividendUpperRate : Int
  dividendAdditionalRate : Int
  /-- s. 55B(4)(b): the transferable amount is "10% of the amount of personal allowance specified in section
  35(1)" (in basis points). -/
  maTransferRate : Int
  /-- s. 45(3)(a) / 46(3)(a): married couple's allowance "£11,270"; s. 43: "the minimum amount" £4,360;
  s. 45(4) / 46(4): reduced by half the excess of adjusted net income over £37,700. -/
  mcaAmount : Int
  mcaMinimum : Int
  mcaIncomeLimit : Int
  /-- s. 45(1) / 46(1): "a tax reduction ... of 10%" of the amount (basis points). -/
  mcaRate : Int
  /-- FA 2004 s. 190(2), (3): relief for contributions up to the greater of £3,600 ("the basic amount") and
  relevant UK earnings. -/
  pensionBasicAmount : Int
  /-- ITEPA 2003 s. 681B(1)(a) and s. 681C(2): "L is £60,000", "X is £200". -/
  hicbcThreshold : Int
  hicbcStep : Int
  /-- S.I. 2006/965 reg. 2(1) as substituted by S.I. 2025/292: £26.05 (the enhanced rate) and £17.25, in pence. -/
  cbEnhancedWeekly : Int
  cbOtherWeekly : Int
  /-- ITEPA 2003 s. 681H(3): "a week is in a tax year if (and only if) the Monday with which it begins is in the
  tax year": 7 April 2025 to 30 March 2026 are 52 Mondays. -/
  cbWeeks : Int
  /-- TCGA 1992 s. 1K(2): "The annual exempt amount for a tax year is £3,000." -/
  cgtExemptAmount : Int
  /-- TCGA 1992 s. 1H(3): "charged to capital gains tax at a rate of 18% or 24%". -/
  cgtLowerRate : Int
  cgtHigherRate : Int
  /-- S.I. 2001/1004 reg. 11(3)(b), (2A)(b): the prescribed equivalents of the primary threshold and upper
  earnings limit for an annual earnings period: £12,570 and £50,270. -/
  niPrimaryThreshold : Int
  niUpperEarningsLimit : Int
  /-- reg. 11(3)(a), (2A)(a): for a monthly earnings period, £1,048 and £4,189. -/
  niPrimaryThresholdMonthly : Int
  niUpperEarningsLimitMonthly : Int
  /-- SSCBA 1992 s. 8(2): "the main primary percentage is 8%", "the additional primary percentage is 2 per cent". -/
  niMainRate : Int
  niAdditionalRate : Int
  /-- SSCBA 1992 s. 15(3): Class 4 on profits that exceed £12,570 but do not exceed £50,270. -/
  class4Lower : Int
  class4Upper : Int
  /-- s. 15(3ZA): "the main Class 4 percentage is 6%", "the additional Class 4 percentage is 2 per cent". -/
  class4MainRate : Int
  class4AdditionalRate : Int
  /-- SSCBA 1992 s. 11(4)(b): "the small profits threshold is £6,845"; s. 11(6): voluntary £3.50 a week (pence). -/
  smallProfitsThreshold : Int
  class2Weekly : Int
  /-- Pensions Act 1995 Sch. 4 as amended: pensionable age is 66 for everyone reaching it before 6 May 2026. -/
  statePensionAge : Nat
  /-- Before 2023-24 the higher rate limit was a figure (s. 10(5A): "£150,000"), not the formula below. -/
  hrlOverride : Option Int := none
  /-- Days in the tax year (6 April to 5 April): 366 when it contains 29 February (2023-24), else 365. Used only by
  the `--oecd` child benefit convention (weekly rate x days / 7). -/
  taxYearDays : Int := 365
  /-- **Scottish taxpayers** (ITA 2007 s. 11A; Scotland Act 1998 s. 80C; the Scottish rate resolution for 2025-26).
  HMRC, "Income Tax rates and allowances", Scotland, "Income after allowances 2025 to 2026": starter 19 % "Up to
  £2,827", basic 20 % "£2,828 to £14,921", intermediate 21 % "£14,922 to £31,092", higher 42 % "£31,093 to £62,430",
  advanced 45 % "£62,431 to £125,140", top 48 % above. -/
  scotStarterLimit : Int := 2827
  scotBasicLimit : Int := 14921
  scotIntermediateLimit : Int := 31092
  scotHigherLimit : Int := 62430
  scotStarterRate : Int := 1900
  scotBasicRate : Int := 2000
  scotIntermediateRate : Int := 2100
  scotHigherRate : Int := 4200
  scotAdvancedRate : Int := 4500
  scotTopRate : Int := 4800
  deriving Repr

/-- ITA 2007 s. 10(5A): "The higher rate limit for a tax year is equal to (a) twice the amount specified in
subsection (1) of section 35 ... plus (b) the amount specified in subsection (2) of that section". -/
def Params.higherRateLimit (p : Params) : Int := p.hrlOverride.getD (2 * p.personalAllowance + p.paIncomeLimit)

/-- The tax year 2025-26 (6 April 2025 to 5 April 2026), England, Wales and Northern Ireland. -/
def p2025 : Params where
  taxYear := "2025-26"
  personalAllowance := 12570
  paIncomeLimit := 100000
  blindAllowance := 3130
  basicRateLimit := 37700
  startingRateLimitSavings := 5000
  psaBasic := 1000
  psaHigher := 500
  psaAdditional := 0
  dividendAllowance := 500
  basicRate := 2000
  higherRate := 4000
  additionalRate := 4500
  savingsBasicRate := 2000
  savingsHigherRate := 4000
  savingsAdditionalRate := 4500
  dividendOrdinaryRate := 875
  dividendUpperRate := 3375
  dividendAdditionalRate := 3935
  maTransferRate := 1000
  mcaAmount := 11270
  mcaMinimum := 4360
  mcaIncomeLimit := 37700
  mcaRate := 1000
  pensionBasicAmount := 3600
  hicbcThreshold := 60000
  hicbcStep := 200
  cbEnhancedWeekly := 2605
  cbOtherWeekly := 1725
  cbWeeks := 52
  cgtExemptAmount := 3000
  cgtLowerRate := 1800
  cgtHigherRate := 2400
  niPrimaryThreshold := 12570
  niUpperEarningsLimit := 50270
  niPrimaryThresholdMonthly := 1048
  niUpperEarningsLimitMonthly := 4189
  niMainRate := 800
  niAdditionalRate := 200
  class4Lower := 12570
  class4Upper := 50270
  class4MainRate := 600
  class4AdditionalRate := 200
  smallProfitsThreshold := 6845
  class2Weekly := 350
  statePensionAge := 66

/-- s. 10(5A) gives £125,140 for 2025-26, the figure HMRC publishes ("additional rate ... over £125,140"). -/
theorem hrl_2025 : p2025.higherRateLimit = 125140 := by decide

/-- s. 55B(4)(b), (5): 10 % of £12,570 is £1,257, "rounded up to the nearest amount which is a multiple of £10":
£1,260, the figure on gov.uk/marriage-allowance ("transfer £1,260 of your Personal Allowance"). -/
def Params.maTransferable (p : Params) : Int :=
  10 * ceilDiv (p.personalAllowance * p.maTransferRate) 100000

theorem ma_transferable_2025 : p2025.maTransferable = 1260 := by decide

/-! ## Tax years 2022-23, 2023-24 and 2024-25 (round 2)

Each year differs from 2025-26 only in the fields set below; every other field (personal allowance £12,570 and its
£100,000 limit, basic rate limit £37,700, the main rates, savings bands, personal savings allowance, pension basic
amount) is the same in all four years. Sources (dated texts, saved with sha256 in `cmp20/improve-anglo/refs/uk/`):
* ITA 2007 s. 10(5) as in force on 6 April 2022 (legislation.gov.uk point in time): the higher rate limit "£150,000"
  (2022-23); from 2023-24 the s. 10(5A) formula (£125,140), HMRC "Income Tax rates and allowances for current and
  past years" (2023-24 and 2024-25 columns: "£37,701 to £125,140").
* ITA 2007 s. 13A dividend nil rate: "£2000" (6 April 2022), "£1,000" (6 April 2023); 2024-25 £500 (HMRC page above).
  Dividend rates 8.75 / 33.75 / 39.35 % in all three years (HMRC page above; 2022-23 the same since the Health and
  Social Care Levy Act 2021 raised them from 6 April 2022).
* Blind person's allowance and married couple's allowance (HMRC page above): 2024-25 £3,070, MCA £11,080 / £4,280;
  2023-24 £2,870, £10,375 / £4,010; 2022-23 £2,600, £9,415 / £3,640 (HMRC's previous-years table); MCA income limits
  £37,000 / £34,600 / £31,400.
* Child benefit: S.I. 2006/965 reg. 2(1) as in force on 11 April 2022 "£21.80" / "£14.45", 10 April 2023 "£24.00" /
  "£15.90", 8 April 2024 "£25.60" / "£16.95". Weeks counted by their Mondays (ITEPA s. 681H(3)): 52 in each year
  (11 Apr 2022 - 3 Apr 2023, 10 Apr 2023 - 1 Apr 2024, 8 Apr 2024 - 31 Mar 2025).
* HICBC: ITEPA 2003 ss. 681B-681C as in force on 6 April 2023 (and 2022): "£50,000", 1 % for each "£100" of the
  excess; 2024-25 £60,000 and £200 (as for 2025-26).
* Class 1 primary contributions, annual earnings period (the model's period, as for 2025-26), HMRC "Rates and
  thresholds for employers" 2022-23 / 2023-24 / 2024-25 (Directors, annual earnings period, category A):
  2022-23: primary threshold £11,908 a year, 12.73 % to the UEL £50,270, 2.73 % above (the annual equivalents the
  Social Security (Contributions) Regulations prescribe for the year of the Health and Social Care Levy (13.25 % to
  5 November 2022) and the Primary Threshold rise of 6 July 2022, National Insurance Contributions (Increase of
  Thresholds) Act 2022 and Social Security (Contributions) (Rates) ... 2022); 2023-24: 11.5 % / 2 % on £12,570 -
  £50,270 (12 % to 5 January 2024, 10 % from 6 January 2024, National Insurance Contributions (Reduction in Rates)
  Act 2023); 2024-25: 8 % / 2 % (National Insurance Contributions (Reduction in Rates) Act 2024). Class 4: 2022-23
  9.73 % / 2.73 % from £11,908; 2023-24 9 % / 2 % from £12,570; 2024-25 6 % / 2 % (same Acts).
* Capital gains tax annual exempt amount £12,300 (2022-23), £6,000 (2023-24), £3,000 (2024-25), rates 10 % / 20 %
  (2024-25: 18 % / 24 % from 30 October 2024 is a mid-year change; the household output flags gains in 2024-25).
* Scottish rates for these years are not set here (the output flags a Scottish household in another year).
-/

def p2024 : Params :=
  { p2025 with
    taxYear := "2024-25"
    blindAllowance := 3070
    mcaAmount := 11080
    mcaMinimum := 4280
    mcaIncomeLimit := 37000
    cbEnhancedWeekly := 2560
    cbOtherWeekly := 1695
    cgtLowerRate := 1000
    cgtHigherRate := 2000 }

def p2023 : Params :=
  { p2025 with
    taxYear := "2023-24"
    taxYearDays := 366
    blindAllowance := 2870
    mcaAmount := 10375
    mcaMinimum := 4010
    mcaIncomeLimit := 34600
    dividendAllowance := 1000
    hicbcThreshold := 50000
    hicbcStep := 100
    cbEnhancedWeekly := 2400
    cbOtherWeekly := 1590
    cgtExemptAmount := 6000
    cgtLowerRate := 1000
    cgtHigherRate := 2000
    niMainRate := 1150
    class4MainRate := 900 }

def p2022 : Params :=
  { p2025 with
    taxYear := "2022-23"
    hrlOverride := some 150000
    blindAllowance := 2600
    mcaAmount := 9415
    mcaMinimum := 3640
    mcaIncomeLimit := 31400
    dividendAllowance := 2000
    hicbcThreshold := 50000
    hicbcStep := 100
    cbEnhancedWeekly := 2180
    cbOtherWeekly := 1445
    cgtExemptAmount := 12300
    cgtLowerRate := 1000
    cgtHigherRate := 2000
    niPrimaryThreshold := 11908
    niMainRate := 1273
    niAdditionalRate := 273
    class4Lower := 11908
    class4MainRate := 973
    class4AdditionalRate := 273 }

/-- The parameters of the tax year that begins on 6 April of `year` (2022-2025; later years use 2025-26, earlier
years 2022-23, and the output says so). -/
def paramsFor (year : Nat) : Params :=
  if year ≤ 2022 then p2022 else if year = 2023 then p2023 else if year = 2024 then p2024 else p2025

theorem hrl_2022 : p2022.higherRateLimit = 150000 := by decide
theorem hrl_2023 : p2023.higherRateLimit = 125140 := by decide

end UkTax
