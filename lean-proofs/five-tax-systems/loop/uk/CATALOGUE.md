# UK individual tax planning techniques, 2025-26: catalogue, triage, recreation

Model: `lean/` (the statute-faithful 2025-26 model of `../../../official-checks/uk-model/lean`, with its findings in `../../uk/FINDINGS.md` and
`../../uk/RESULTS.md`) with one addition (`LOOP EXTENSION` in `Person.lean`, `Household.lean`, `Main.lean`, 49 lines):
per-person incomes (`"persons": [...]`), `bik` (employment income outside Class 1: a benefit in kind, or a negative
net-pay deduction), `vct`/`eis`/`seis` subscriptions (ITA 2007 s. 263 / s. 158 / s. 257AB, Step 6 reductions in
the s. 27(4)-(5) order before the married couple's allowance) and `financeCosts` (ITTOIA 2005 s. 272A disallowed,
s. 274A/274AA 20 % reduction; no carry-forward). On the 3,503 households of the UK model's runs the extended exe's
output is byte-identical to the original's.

Scoring (`ukrun.burden`): income tax (s. 23 liability, incl. the s. 424 Gift Aid charge) less basic-rate relief at
source + CGT + employee Class 1/4 − (child benefit − HICBC). "Saving" = burden without − burden with, for the same
pre-tax position unless the note says otherwise. Numbers: `runs/scenarios.json`, `runs/owner_manager.json`;
theorems: `lean/UkTax/Loop/Theorems.lean` (all pass, `decide`).

Sources used throughout: legislation.gov.uk (sections cited), HMRC manuals, GOV.UK guidance, HMRC "Tax relief
statistics (January 2026)" (gov.uk/government/statistics/tax-reliefs/tax-relief-statistics-january-2026: pensions
income tax relief £33.5bn and NIC relief £25.6bn in 2025-26), HMRC annual savings statistics (ISA cost ~£9.7bn),
HMRC UK charity tax relief statistics (Gift Aid £1.88bn; higher-rate donor relief £0.92bn), IFS "Income tax
explained" (ifs.org.uk/taxlab, the 60 % band), HMT/HMRC "Salary sacrifice reform for pension contributions
effective from 6 April 2029" (gov.uk), HMRC "Low earners anomaly: pensions relief relating to net pay
arrangements" (gov.uk).

Triage: **a** = expressible with the model (scenario run); **b** = needed the small extension above; **c** = out of
scope (reason given).

## Summary

| | count |
|---|---|
| catalogued | 50 |
| recreated (a + b) | 38 (a 33, b 5) |
| out of scope (c) | 12 |
| headline theorems | 7 (`sacrifice_taper`, `sacrifice_hicbc`, `spouse_transfer`, `btl_spouse`, `giftaid_unlocks_ma`, `n1_scot_dividend_straddle`, `n1b_scot_free_relief`) |
| PolicyEngine-UK cross-check | 10 canonical scenarios, savings equal to the penny (`runs/pe_cross_summary.txt`) |

## Pensions

| id | technique | source | tri | scenario → result | statutory cause |
|---|---|---|---|---|---|
| C01 | Salary sacrifice into a pension out of the £100k–£125,140 allowance taper | ITEPA 2003 s. 308 (employer contributions not earnings); ITA 2007 s. 35(2), s. 58; NI: employer pension contributions are not earnings (SS(C)R 2001 Sch. 3 Pt. 6); IFS taxlab; GOV.UK 2029 reform (NI on sacrifice above £2,000 from 6 April 2029, income tax unchanged) | a | £125,140 → £100,000 + £25,140 pension: **saves £15,586.80 = 62 %**; value (pay − tax + pension) £93,697.40 vs £78,110.60. Theorem `sacrifice_taper` | 40 % + the taper's 20 % + 2 % NI |
| C02 | Relief-at-source personal contribution, same purpose | FA 2004 s. 192(1), (4); ITA s. 58(2) (adjusted net income less grossed-up contributions) | a | £25,140 gross: saves £15,084 (60 %; £5,028 at source + £10,056 by band extension and restored allowance); £502.80 less than C01 (the 2 % NI) | s. 192(4) band extension + s. 58 |
| C03 | Pension (sacrifice or RAS) out of the HICBC | ITEPA s. 681B-681H (ANI, s. 681H) | a | 2 children, £80,000 → £60,000: **saves £10,651 (53.3 %)**: 42 % + the whole £2,251 charge. Theorem `sacrifice_hicbc` | charge on ANI, 1 % per £200 |
| C04 | Pension contribution: higher-rate relief and the £1,000 personal savings allowance back | ITA s. 12B; FA 2004 s. 192(4) | a | £52,000 + £1,000 interest: £2,000 gross saves £800 (40 %: £400 at source + £400 band); at £2,860 gross all income is within the extended band and the PSA goes £500 → £1,000 (a further £100 step: £2,860 saves £1,118, 39.1 %) | s. 12B test after band extension |
| C05 | Pension / Gift Aid to extend the band for CGT at 18 % | TCGA 1992 s. 1J; ITA s. 414(2)(b); FA 2004 s. 192(4); HMRC CG21204 | a | £40,000 wages, £30,000 gains: RAS £10,000 gross saves only the £2,000 at source (**no CGT effect**: no higher-rate tax "apart from" s. 192, UK F2b), Gift Aid £8,000 cuts CGT by £600 (6 % of £10,000) | s. 192(4) condition vs s. 414 (unconditional) |
| C06 | Net pay vs relief at source for a low earner | FA 2004 s. 191-193; GOV.UK low-earners anomaly (top-up payments from 2024-25, paid from 2026) | a (`bik` −) | £11,000 earner, £1,000 gross: net pay £0 relief, RAS £200 (20 %) | net pay relieves only tax actually due |
| C07 | Contributions for a non-earner / child: £2,880 → £3,600 | FA 2004 s. 190(2)-(5) (basic amount £3,600), s. 192 | a | £720 added with no tax paid | relief at source given whether or not taxed |
| C36 | Phased drawdown, 25 % tax-free each time | ITEPA s. 636A, FA 2004 Sch. 29 (PCLS/UFPLS); ITA s. 35 | a | £100,000 in one year: £17,432; as 6 × £16,760 (each £12,570 taxable): £0 | personal allowance per year; progressive bands |
| C44 | Carry-forward of unused annual allowance | FA 2004 s. 228A | c | multi-year | — |
| C45 | Pensions outside IHT; recycling lump sums | FA 2004 Sch. 29 para 3A; IHTA 1984 | c | IHT / anti-avoidance rule | — |

## Charity

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C08 | Gift Aid by a higher-rate donor | ITA s. 414(2)(b) | a | £70,000, £8,000 paid: saves £2,000 (20 % of £10,000 gross) beyond the charity's £2,000 | band extension |
| C09 | Gift Aid to restore the allowance / cut the HICBC | ITA s. 58; ITEPA s. 681H | a | £110,000, £8,000: saves £4,000 (40 % of gross; 50 % of the gift paid); £70,000 and 3 children: £3,574 (45 % of the gift paid) | ANI |
| C10 | Gift Aid carried back to the previous year | ITA s. 426 | c | multi-year (needs 2024-25) | — |
| C46 | Gifts of shares or land to charity | ITA s. 431; TCGA s. 257 | c | needs a Step 2 deduction and gain exemption not in the model; lower payoff | — |

## Married couples and civil partners (and partners for the HICBC)

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C11 | Marriage allowance | ITA s. 55A-55C | a | A no income, B £40,000: £252 (cliff at £50,271: UK `ma_cliff`) | 10 % of the allowance |
| C12 | Move income-producing assets to the lower-income spouse | TCGA s. 58 (no gain/no loss); ITTOIA s. 626 (outright gifts between spouses outside the settlements rules); ITA s. 836-837 | a | £90,000 earner moves £6k interest + £6k dividends: **saves £4,456.25**. Theorem `spouse_transfer` | spouse's allowance, starting rate, PSA, dividend allowance, basic band |
| C13 | Bed-and-spouse: two CGT exempt amounts and the spouse's 18 % band | TCGA s. 58, s. 1K, s. 1J | a | £20,000 gains, half to the £10,000 spouse: £1,140 | second £3,000 exempt + 18 % vs 24 % |
| C34 | Buy-to-let held by the lower earner (or Form 17 unequal shares) | ITA s. 836-837; ITTOIA s. 272A, 274A | b (`financeCosts`) | £40,000 before £20,000 interest: by the non-earner **saves £10,460**; 50:50 saves £6,000. Theorem `btl_spouse` | interest disallowed (s. 272A), credit only 20 % |
| C38 | Employ the spouse in the business | ITTOIA s. 34 (wholly and exclusively); SSCBA s. 9 | a | sole trader £70,000 pays spouse £12,570: £5,756.52 less employer NI £1,136 = £4,620.52 (£5,756.52 if the Employment Allowance covers it) | spouse's allowance, NI thresholds |
| C39 | Earnings split vs one earner (HICBC single-earner design) | ITEPA s. 681B (charge on the higher ANI) | a | 2 children, £80,000 + £0 vs £40,000 + £40,000: £9,932.80 (HICBC £2,251, income tax £8,460, NI −£778.20) | individual taxation + charge on the higher partner |
| C40 | Gift Aid or pension keeps a recipient over £50,270 basic-rate → marriage allowance | ITA s. 55B(2)(b), s. 414(2)(b); FA 2004 s. 192(4) | a | B £52,000, £1,600 paid: marrying saves £252; without the gift £0. Theorem `giftaid_unlocks_ma` | the condition is a rate test, not an income limit (known: Tax Adviser magazine, RSM; NOVEL.md) |
| C41 | Transfer of unused blind person's allowance | ITA s. 38-39 | a | £626 (20 % of £3,130) | s. 39 transfer |
| C43 | Dividends to a non-earning spouse shareholder | ITTOIA s. 624-626; *Jones v Garnett* [2007] UKHL 35 (Arctic Systems) | a | £100,000 company profit: +£8,654.38 to the household vs owner-only dividends (owner_manager.json) | spouse's allowances and bands |

## Savings, investments and gains

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C14 | Starting rate for savings (£5,000 at 0 %) | ITA s. 7, s. 12 | a | £18,570 of interest: £0 (as wages: £1,680) | 0 % band below £17,570 non-savings |
| C15 | Personal savings allowance | ITA s. 12A-12B | a | in C04, C12; cliffs `psa_cliff` (UK Theorems) | — |
| C16 | Dividend allowance £500 | ITA s. 13A | a | £13,070 dividends £0 (as wages £140) | 0 % dividend nil rate + no NI |
| C17 | Allocation of allowances against the most expensive income | ITA s. 25(2) | a | already proved: UK `s25_allowance_against_dividends` (£606.37 vs £1,043.87; F6) | — |
| C19 | ISA | ITTOIA s. 694-701; SI 1998/1870; TCGA s. 151 | a | £800 of interest sheltered by a £60,000 earner: £320 | exemption |
| C20 | Bed-and-ISA | TCGA s. 1K, s. 104-106A | a | gains up to £3,000 realised tax-free and re-bought inside the ISA: £720 a year of later CGT avoided (24 %) | exempt amount + ISA wrapper |
| C21 | Harvest the CGT exempt amount every year (bed-and-spouse / -breakfast after 30 days) | TCGA s. 1K, s. 106A | a | £3,000 realised now: £0; deferred onto other gains: £720 | annual, use-it-or-lose-it |
| C22 | Time gains into a low-income year | TCGA s. 1H-1J | a | £40,000 of gains: CGT £8,880 in a £60,000 year, £6,660 with no income (−£2,220) | unused basic band at 18 % |
| C23 | EIS | ITA s. 156-158 (30 %, £1m); TCGA Sch. 5B deferral | b | £150,000 earner, £50,000: £15,000 | Step 6 reduction |
| C24 | SEIS | ITA s. 257AB (50 %, £200,000); TCGA Sch. 5BB | b | £25,000 | Step 6 reduction |
| C25 | VCT | ITA s. 261-263 (30 %, £200,000); ITTOIA s. 709; TCGA s. 151A | b | £15,000 (dividends and gains then exempt); a VCT relief that removes all the tax makes Gift Aid chargeable (s. 424-425: £1,000 charge on £4,000 paid at £30,000) | Step 6 reduction |
| C37 | Gifts to grandchildren (child's own allowances; parents' gifts caught above £100) | ITTOIA s. 629 | a | £2,000 interest: £600 with a higher-rate grandparent, £0 for the child | separate taxation |
| C47 | Business asset disposal relief (14 %) | TCGA s. 169H-169S | c | qualifying business disposals not in the model | — |
| C48 | Main residence relief | TCGA s. 222-226 | c | the gain never reaches the computation | — |

## Property and small incomes

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C26 | Rent-a-room (£7,500) | ITTOIA s. 784-802 (s. 789, s. 800 alternative basis) | a (script) | £9,000 rent, £1,500 costs: £1,200 | receipts − £7,500 instead of profit |
| C27 | Trading allowance (£1,000) | ITTOIA s. 783A-783AR | a (script) | £3,000 receipts, £200 costs: £160; £900 receipts: £180 (full relief) | allowance instead of costs |
| C28 | Property allowance (£1,000) | ITTOIA s. 783B-783BR | a (script) | £2,500, £100 costs: £360 | same |
| C35 | Joint ownership of let property 50:50 | ITA s. 836 | b | see C34: £6,000 | — |
| C49 | Incorporating the lettings / family investment company | CTA 2010; TCGA s. 162 | c | entity level | — |

## Employment

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C32 | Electric car by salary sacrifice | ITEPA s. 114-120, s. 139 (3 % for zero-emission cars in 2025-26); s. 69A (OpRA excludes ULEVs) | b (`bik`) | £7,000 of £60,000 for a £50,000 car: £2,340 (40 % on £5,500 + 2 % NI on £7,000) | low appropriate percentage; no Class 1 on the benefit |
| C33 | Exempt benefits by sacrifice (cycle to work) | ITEPA s. 244, s. 69A | a | £1,000: £280 (28 %) | exemption |
| C50 | Tax-advantaged share schemes (SIP, SAYE, CSOP, EMI) | ITEPA Part 7 | c | not in the model | — |

## Owner-managers and the self-employed

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C42 | Salary vs dividends | ITTOIA s. 383; ITA s. 8, 13A; CTA 2010 s. 18A-18E; SSCBA s. 9 (15 % above £5,000) | a (company side in script) | profit £100,000: all salary nets £61,370.04; £12,570 + dividends £66,542.85 (+£5,172.81); £5,000 + dividends £65,767.07; at £150,000 the £5,000 salary is best (£87,517.67) | no NI on dividends; CT 19-26.5 % < combined NI |
| C30 | Class 4 annual maximum with Class 1 | SS(C)R 2001 reg. 100 | a | employee £60,000 + profits £30,000: Class 4 £348.60 instead of £1,045.80 (−£697.20); proved `reg100_cap` | above the UEL only 2 % |
| C51 | Voluntary Class 2/3 for state pension | SSCBA s. 11, 13 | c | benefit entitlement, not tax | — |
| C52 | Loss relief against general income | ITA s. 64, 72 | c | losses not modelled; multi-year | — |

## Residence

| id | technique | source | tri | scenario → result | cause |
|---|---|---|---|---|---|
| C29 | Scottish vs rest-of-UK taxpayer | ITA s. 11A; Scotland Act 1998 s. 80D-80F | a | £50,000: £1,527.80 more as a Scottish taxpayer; taper band 69.5 % vs 62 % (`scot_vs_ruk_marginal`); with dividends straddling the UK basic rate limit 108.5 % and Gift Aid / pension contributions that pay for themselves (NOVEL.md N1) | Scottish rates on non-savings income |
| C53 | Non-dom / FIG regime, temporary non-residence | FA 2025 Sch. 9-10; TCGA s. 10A | c | residence | — |
| C54 | IHT: annual exemption, gifts out of income, PETs, BPR/APR | IHTA 1984 s. 19, 21, 3A, 104, 116 | c | IHT | — |

Counts: pensions 10, charity 4, couples 9, savings 14, property 5, employment 3, owner/self-employed 4, residence 3 =
52 rows, of which C15 and C35 point at other rows; catalogued as 50 distinct techniques.
