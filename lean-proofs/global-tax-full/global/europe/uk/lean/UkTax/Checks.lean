import UkTax.Household

/-!
# Checks against figures HMRC and GOV.UK publish

Every figure below is quoted from an official page (saved under `cmp/uk/refs/govuk` as GOV.UK content-API JSON
and `refs/govtxt` as text); the page and the passage are cited on each check. Nothing is invented: where a page
gives only part of a calculation, only that part is checked.

`theorem ... := by decide` is checked by the kernel; `#guard` by the compiled evaluator at build time (the full
liability runs the s. 25(2) search over a few hundred candidate allocations, which is slow to unfold in the kernel).
-/

namespace UkTax.Checks
open UkTax

def run (p : Params) (x : Person) (e : Elections := {}) : PersonResult := personCalc p Reading.hmrc x e
/-- The liability, in pence. -/
def liab (p : Params) (x : Person) (e : Elections := {}) : Int := ticksToPence (run p x e).liability

/-! ## 1. Published rates, allowances and thresholds for 2025-26

HMRC, "Income Tax rates and allowances for current and previous tax years" (GOV.UK publication
`rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past`, updated 6 April 2026), column
"2025 to 2026": Personal Allowance £12,570; income limit £100,000; Married Couple's Allowance maximum £11,270, minimum
£4,360; Blind Person's Allowance £3,130; dividend allowance £500; starting rate for savings 0 % "Up to £5,000"; basic
rate 20 % "Up to £37,700"; higher rate 40 % "£37,701 to £125,140"; additional rate 45 %; dividend rates 8.75 %,
33.75 %, 39.35 %. -/

theorem hmrc_income_tax_table_2025 :
    p2025.personalAllowance = 12570 ∧ p2025.paIncomeLimit = 100000 ∧ p2025.mcaAmount = 11270 ∧
    p2025.mcaMinimum = 4360 ∧ p2025.blindAllowance = 3130 ∧ p2025.dividendAllowance = 500 ∧
    p2025.startingRateLimitSavings = 5000 ∧ p2025.basicRateLimit = 37700 ∧ p2025.higherRateLimit = 125140 ∧
    p2025.basicRate = 2000 ∧ p2025.higherRate = 4000 ∧ p2025.additionalRate = 4500 ∧
    p2025.dividendOrdinaryRate = 875 ∧ p2025.dividendUpperRate = 3375 ∧ p2025.dividendAdditionalRate = 3935 := by
  decide

/-- HMRC, "Rates and thresholds for employers 2025 to 2026" (GOV.UK guidance): "Lower earnings limit £125 per week
£542 per month £6,500 per year"; "Primary threshold £242 per week £1,048 per month £12,570 per year"; upper earnings
limit "£967 per week £4,189 per month £50,270 per year". The monthly and annual primary threshold and upper earnings
limit are those of S.I. 2001/1004 reg. 11(3)(a), (b) and (2A)(a), (b). -/
theorem hmrc_employer_rates_2025 :
    p2025.niPrimaryThresholdMonthly = 1048 ∧ p2025.niPrimaryThreshold = 12570 ∧
    p2025.niUpperEarningsLimitMonthly = 4189 ∧ p2025.niUpperEarningsLimit = 50270 ∧
    p2025.niMainRate = 800 ∧ p2025.niAdditionalRate = 200 := by decide

/-- The monthly lower earnings limit is not in regulation 11 as a figure: reg. 11(2)(b) multiplies the weekly £125
(reg. 10(a)) "by 4 1/3" and reg. 11(4) rounds "up to the next whole pound". That gives HMRC's £542. -/
theorem lel_monthly : ceilDiv (125 * 13) 3 = 542 := by decide

/-- SSCBA 1992 s. 5(5) lets a prescribed equivalent exceed "by not more than £1.00" the arithmetical equivalent.
The weekly primary threshold (£242, reg. 10(c)) is £0.27 more than 1/52 of the annual £12,570 (reg. 11(3)(b)), and the
monthly (£1,048) £0.50 more than 1/12 of it: employees paid weekly and monthly have slightly different thresholds
from a director on an annual earnings period (£242 × 52 = £12,584; £1,048 × 12 = £12,576). -/
theorem pt_equivalents :
    242 * 52 = 12584 ∧ 1048 * 12 = 12576 ∧ 100 * 242 * 52 - 100 * 12570 < 100 * 52 ∧ 1048 * 12 - 12570 < 12 := by
  decide

/-- HMRC, "Rates and allowances: National Insurance contributions", tables 3.1 and 3.2, column "2025 to 2026":
Small Profits Threshold £6,845, Class 2 £3.50 a week; Lower Profits Limit £12,570, Upper Profits Limit £50,270;
6 % between them, 2 % above. -/
theorem hmrc_ni_self_employed_2025 :
    p2025.smallProfitsThreshold = 6845 ∧ p2025.class2Weekly = 350 ∧ p2025.class4Lower = 12570 ∧
    p2025.class4Upper = 50270 ∧ p2025.class4MainRate = 600 ∧ p2025.class4AdditionalRate = 200 := by decide

/-- GOV.UK "Capital Gains Tax": "The Capital Gains tax-free allowance is: £3,000". -/
theorem cgt_allowance_2025 : p2025.cgtExemptAmount = 3000 := by decide

/-! ## 2. The personal allowance taper (gov.uk/income-tax-rates)

"Your personal allowance goes down by £1 for every £2 that your adjusted net income is above £100,000. This means
your allowance is zero if your income is £125,140 or above." -/

theorem pa_zero_at_125140 : personalAllowance p2025 (gbp 125140) = 0 ∧ personalAllowance p2025 (gbp 125138) = 1 := by
  decide

/-- An odd pound: the statute halves the excess (s. 35(2)) and rounds the allowance up (s. 35(3)), so £100,001 still
leaves £12,570 (HMRC: "£1 for every £2"). -/
theorem pa_odd_pound :
    personalAllowance p2025 (gbp 100000) = 12570 ∧ personalAllowance p2025 (gbp 100001) = 12570 ∧
    personalAllowance p2025 (gbp 100002) = 12569 := by decide

/- GOV.UK "Income Tax rates and Personal Allowances", previous tax years: "You had £35,000 of taxable income and you
got the standard Personal Allowance of £12,570. You paid basic rate tax at 20% on £22,430". -/
#guard liab p2025 { employment := 35000 } = gbp 22430 * 20 / 100

/-! ## 3. Savings (gov.uk/apply-tax-free-interest-on-savings, "How much is tax free")

"You earn £16,000 of wages and £200 interest on your savings. ... Your remaining starting rate for savings is £1,570
(£5,000 minus £3,430). This means you will not have to pay tax on your £200 savings interest." -/
#guard liab p2025 { employment := 16000, interest := 200 } = liab p2025 { employment := 16000 }
#guard (run p2025 { employment := 16000, interest := 200 }).ch.savStarting = gbp 200
#guard (run p2025 { employment := 16000, interest := 2000 }).ch.savStarting = gbp 1570

/- "If your other taxable income (not including savings interest or dividends) is less than £17,570, you can get the
starter rate for savings." -/
#guard (run p2025 { employment := 17569, interest := 100 }).ch.savStarting = gbp 1
#guard (run p2025 { employment := 17570, interest := 100 }).ch.savStarting = 0

/- "HMRC estimates you earned £1,300 in savings interest ... Your Personal Savings Allowance is £1,000 because you're a
basic rate taxpayer. ... remaining £300 is taxed at 20% ... tax due on your savings interest is £60." (A basic-rate
taxpayer whose wages use up the starting rate band.) -/
#guard liab p2025 { employment := 30000, interest := 1300 } - liab p2025 { employment := 30000 } = gbp 60

/-! ## 4. Dividends

HMRC, "Dividend Allowance factsheet" (2015, for 2016-17), section 2, with its own limits: "Personal Allowance -
£11,000; Basic Rate Limit - £32,000"; dividend allowance £5,000; 7.5 %, 32.5 %, 38.1 %. The higher rate limit for
2016-17 was £150,000 (ITA 2007 s. 10(5A) as at 6 April 2016). Savings allowance and starting rate as in 2025-26. -/
def p2016 : Params :=
  { p2025 with taxYear := "2016-17", personalAllowance := 11000, basicRateLimit := 32000, dividendAllowance := 5000,
               dividendOrdinaryRate := 750, dividendUpperRate := 3250, dividendAdditionalRate := 3810,
               hrlOverride := some 150000 }

/- Example 3: "non-dividend income of £6,500, and a dividend income of £12,000 ... £4,500 of the dividends are under
the threshold for tax. A further £5,000 comes within the Dividend Allowance, leaving tax to pay at Basic Rate (7.5%) on
£2,500." -/
#guard liab p2016 { employment := 6500, dividends := 12000 } = gbp 2500 * 75 / 1000
/- Example 4: "non-dividend income of £20,000, and receive dividends of £6,000 ... will pay tax on £1,000 of dividends
at 7.5%." -/
#guard liab p2016 { employment := 20000, dividends := 6000 } - liab p2016 { employment := 20000 } = gbp 75
/- Example 5: "non-dividend income of £18,000, and receive dividends of £22,000 ... £7,000 to be taxed at Basic Rate
... the remaining £17,000 of dividends to be taxed at the Basic Rate (7.5%)". -/
#guard liab p2016 { employment := 18000, dividends := 22000 } = gbp 7000 * 20 / 100 + gbp 17000 * 75 / 1000
/- Example 6, the s. 25(2) example: "The Personal Allowance should be allocated in the most beneficial way ... Of the
£40,000 non-dividend income, £8,000 is covered by the Personal Allowance, leaving the balance of £32,000 to be taxed at
basic rate ... Of the £9,000 dividend income, £3,000 is covered by the balance of Personal Allowance ... leaving £1,000
of dividends to be taxed at higher rate (32.5%)." Tax £6,725; the usual order (allowance against wages first) would
give £7,100. -/
#guard liab p2016 { employment := 40000, dividends := 9000 } = gbp 32000 * 20 / 100 + gbp 1000 * 325 / 1000
#guard (run p2016 { employment := 40000, dividends := 9000 }).c1 = gbp 32000
#guard (charged p2016 Reading.hmrc { brl := gbp 32000, hrl := gbp 150000 } (gbp 29000) (gbp 29000) (gbp 38000)).tax p2016
  / 10000 = gbp 7100

/-- GOV.UK "Tax on dividends" (2026-27 rates: "Basic rate 10.75%", "Higher rate 35.75%"): "You get £3,000 in dividends
and earn £29,570 in wages ... taxable income of £20,000 ... 20% tax on £17,000 of wages, no tax on £500 of dividends
... 10.75% tax on £2,500 of dividends". The 2026-27 rates are HMRC's table (Finance Act 2026); the rest as 2025-26. -/
def p2026div : Params := { p2025 with taxYear := "2026-27", dividendOrdinaryRate := 1075, dividendUpperRate := 3575 }
#guard liab p2026div { employment := 29570, dividends := 3000 } = gbp 17000 * 20 / 100 + gbp 2500 * 1075 / 10000

/-! ## 5. Marriage allowance (gov.uk/marriage-allowance, "How it works")

"Your income is £11,500 ... Your partner's income is £20,000 ... When you claim Marriage Allowance you transfer
£1,260 ... you will now pay tax on £190, but your partner will only pay tax on £6,170 ... saves you £214 in tax." -/
#guard liab p2025 { employment := 11500 } { maGive := true } = gbp 190 * 20 / 100
#guard liab p2025 { employment := 20000 } { maReceive := true } = gbp 6170 * 20 / 100
#guard (liab p2025 { employment := 11500 } + liab p2025 { employment := 20000 })
      - (liab p2025 { employment := 11500 } { maGive := true } + liab p2025 { employment := 20000 } { maReceive := true })
      = gbp 214
/-- "Marriage Allowance lets you transfer £1,260 ... This reduces their tax by up to £252". -/
theorem ma_252 : p2025.maTransferable * p2025.basicRate / 10000 = 252 := by decide

/-- GOV.UK "Married Couple's Allowance": "For the 2025 to 2026 tax year, it could cut your tax bill by between £436 and
£1,127 a year" (10 % of £4,360 and of £11,270; ss. 43, 45–46). In ticks (£1 = 1,000,000): the full amount up to
adjusted net income £37,700, the minimum from £51,520 (= £37,700 + 2 × (£11,270 − £4,360)). -/
theorem mca_range_2025 :
    mcaReduction p2025 (gbp 37700) = 1127 * 1000000 ∧ mcaReduction p2025 (gbp 51520) = 436 * 1000000 ∧
    mcaReduction p2025 (gbp 200000) = 436 * 1000000 := by decide

/-! ## 6. Adjusted net income (GOV.UK guidance "Personal Allowances: adjusted net income", updated 30 May 2025)

"Bill's taxable income is £115,000, made up of: income from self-employment £85,000, income from property £20,000,
bank interest £10,000. Bill makes private pension contributions without tax relief of £10,000. Bill's net income is
£105,000 ... this is his adjusted net income." (Contributions paid gross are relieved on a claim, FA 2004 s. 194(1).) -/
#guard (run p2025 { trading := 85000, property := 20000, interest := 10000, claimContrib := 10000 }).ani = gbp 105000
#guard (run p2025 { trading := 85000, property := 20000, interest := 10000, claimContrib := 10000 }).pa = 10070

/- "Clara's total taxable income is £70,000, made up of: income from employment £65,000, bank interest £5,000. Clara
makes private pension contributions without tax relief of £4,750. Her net income is £65,250 ... Clara makes Gift Aid
donations of £1,000. She can take £1,250 off ... Clara's adjusted net income is £64,000." -/
#guard (run p2025 { employment := 65000, interest := 5000, claimContrib := 4750, giftAid := 1000 }).netIncome = gbp 65250
#guard (run p2025 { employment := 65000, interest := 5000, claimContrib := 4750, giftAid := 1000 }).ani = gbp 64000

/-! ## 7. High income child benefit charge (gov.uk/child-benefit-tax-charge)

"You'll pay back 1% of your Child Benefit for every £200 you earn over £60,000. If you earn over £80,000 you'll pay
it all back." Clara (above) has adjusted net income £64,000: 20 %. Child benefit for two children for 2025-26:
52 × (£26.05 + £17.25) = £2,251.60, of which the statute charges on £2,251 (s. 681C(3)). -/
theorem hicbc_points :
    hicbc p2025 (gbp 60000) 225160 = 0 ∧ hicbc p2025 (gbp 60199) 225160 = 0 ∧
    hicbc p2025 (gbp 60200) 225160 = gbp 22 ∧ hicbc p2025 (gbp 64000) 225160 = gbp 450 ∧
    hicbc p2025 (gbp 79999) 225160 = gbp 2228 ∧ hicbc p2025 (gbp 80000) 225160 = gbp 2251 ∧
    hicbc p2025 (gbp 200000) 225160 = gbp 2251 := by decide

theorem child_benefit_2025 : childBenefit p2025 [7, 4] = 225160 ∧ childBenefit p2025 [3] = 135460 := by decide

/-! ## 8. Capital gains tax

GOV.UK "Capital Gains Tax" (examples written for 2026-27, whose allowance, band and rates are those of 2025-26:
£3,000, £37,700, 18 % and 24 %). Example 1: "Your taxable income ... is £20,000 and your taxable gains are £12,600 ...
you'll pay £1,728". Example 2: "... £20,000 and your taxable gains are £52,600 ... 18% on £17,700 and then 24% on
£31,900 ... £10,842." (Taxable income £20,000: employment £32,570.) -/
#guard ticksToPence (run p2025 { employment := 32570, gains := 12600 }).cgt = gbp 1728
#guard ticksToPence (run p2025 { employment := 32570, gains := 52600 }).cgt = gbp 10842

/-- HMRC Capital Gains Manual CG21204, "Example – extending the basic rate band" (2018-19): "income after allowances
of £30,000 ... a gain on a painting of £70,000 ... a gift of £40,000 to charity ... that qualifies for gift aid relief.
The annual exempt amount is £11,700 and the basic rate band is £34,500 ... The basic rate band becomes £84,500 ... So
the amount of Capital Gains Tax payable is £6,210 (£54,500 at 10% plus £3,800 at 20%)." -/
def p2018cg : Params :=
  { p2025 with taxYear := "2018-19", basicRateLimit := 34500, cgtExemptAmount := 11700, cgtLowerRate := 1000,
               cgtHigherRate := 2000, hrlOverride := some 150000 }
#guard ticksToPence (run p2018cg { employment := 30000 + 12570, gains := 70000, giftAid := 40000 }).cgt = gbp 6210
#guard (run p2018cg { employment := 30000 + 12570, gains := 70000, giftAid := 40000 }).limits.brl = gbp 84500

/-! ## 9. Relief at source (HMRC Pensions Tax Manual PTM044220)

"A member wants to make a total contribution of £1,000. The member deducts and retains £200 and pays £800 ...
The member is a higher rate taxpayer (40%) and claims the extra £200". -/
#guard ticksToPence (run p2025 { employment := 80000, rasGross := 1000 }).rasRelief = gbp 200
#guard liab p2025 { employment := 80000 } - liab p2025 { employment := 80000, rasGross := 1000 } = gbp 200
/- "Margot who wishes to pay £100 per month ... would only pay a net amount of £80 a month" (basic rate). -/
#guard ticksToPence (run p2025 { employment := 30000, rasGross := 1200 }).rasRelief = gbp 240
#guard liab p2025 { employment := 30000, rasGross := 1200 } = liab p2025 { employment := 30000 }

/-! ## 10. National Insurance

A £50,000 employee: (50,270 is not reached) 8 % of (50,000 − 12,570) = £2,994.40. -/
#guard ticksToPence (run p2025 { employment := 50000 }).class1 = 299440
#guard ticksToPence (run p2025 { employment := 70000 }).class1 = gbp 3016 + 39460

end UkTax.Checks
