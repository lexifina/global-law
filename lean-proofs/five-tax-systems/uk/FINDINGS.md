# UK income tax 2025-26: Lean model vs the statute, HMRC and PolicyEngine-UK — findings

Each finding: what the statute says (text in force on 6 April 2025, legislation.gov.uk point-in-time XML in
`refs/leg`), what HMRC's published guidance or PolicyEngine-UK 2.179.1 (PE) does, who is right and on what authority,
the evidence (a named theorem in `lean/UkTax/Theorems.lean`, or households from the random runs), and the effect.
Counts are from the referee runs in RESULTS.md (mixed 5,000 / investment-heavy 3,000 / threshold edges 3,000 /
wages-only 2,000 households).

## F1. ITA 2007 s. 12B(8): "higher-rate income" leaves out the savings rates
- s. 12B(3)-(4): the savings allowance is £500 if any income is "higher-rate income", else £1,000 (nil with
  "additional-rate income"). s. 12B(8)(b): higher-rate income is "(i) income on which income tax is charged at the
  higher rate, default higher rate or dividend upper rate, (ii) income on which income tax would be charged at the
  higher rate, or default higher rate, but for section 12A ..."; (a) likewise for the additional rates.
- Since 2017-18 savings above the basic rate limit bear the **savings** higher rate (s. 11D, s. 7A), a separate rate.
  FA 2016 s. 6 created the savings rates **and in the same section** amended s. 12B(8)(a)(i), (ii), (b)(i), (ii) to
  add the "default" rates, but not the savings rates (commentary in `refs/txt/ita_p2c2.txt`).
- Read literally, savings never make anyone a higher- (or additional-) rate taxpayer for the allowance, and
  sub-paragraph (ii), written for savings nil-rated "but for section 12A", can never apply (such savings would
  otherwise bear the savings higher rate, not "the higher rate").
- HMRC counts savings ("To work out your tax band, add all the interest you've earned to your other income",
  gov.uk/apply-tax-free-interest-on-savings); so does PE.
- Who is right: the words give the literal result; a provision that is dead letter on its literal reading, amended
  by the very section that created the omitted rates, is the classic case for a rectifying construction (Inco Europe
  v First Choice Distribution [2000] UKHL 15). **Model default = HMRC; `--psa-literal` gives the words.**
- Theorem `f1_psa_literal`: wages £45,000, interest £10,000: HMRC £9,232 (allowance £500); the words £9,032 (£1,000).
- Effect of the words: 36/5,000 mixed, 63/3,000 investment, 198/3,000 edge households pay less, by up to £430.

## F2. FA 2004 s. 192(4): which pension contributions extend the bands
- "If (apart from this section) income tax at the higher rate or the additional rate ... is chargeable in respect of
  any part of the individual's total income for the tax year, on the making of a claim the basic rate limit and the
  higher rate limit ... are increased by the amount of the contribution."
- (a) **The words.** "The higher rate" is a defined rate (ITA 2007 s. 6), distinct from the dividend upper rate (s. 8)
  and, since 2017-18, the savings higher rate. Literally, someone whose only income above the basic rate limit is
  dividends or savings gets no extension: the company director on salary plus dividends, the very case for which
  personal contributions are usually advised. Theorem `f2_ras_literal`: wages £50,000, dividends £10,000, £10,000
  contribution: £8,317.25 with the extension, £10,655.12 on the words. On the words income tax is **not monotone**:
  `f2_literal_not_monotone` (£1 more of wages lets non-savings income reach the higher rate, the extension switches
  on, tax falls from £10,746.25 to £8,371.70). Words vs default: 27/5,000 mixed, 82/3,000 investment (up to
  +£9,893.50), 97/3,000 edge households.
- (b) **The condition itself, generously read** (any rate of the higher or additional band: the model's default): a
  basic-rate taxpayer's contributions do not extend the band, which matters for capital gains tax (TCGA 1992 s. 1J,
  the unused basic rate band). HMRC's Capital Gains Manual CG21204: the band "can be extended ... where relief at
  source is given for a pension contribution (FA04/S192(4))", condition not stated; PE extends always. Who is right:
  the statute; CG21204 cites s. 192(4) and cannot remove its condition; PE is wrong for basic-rate taxpayers with
  gains. Extending always vs default: 14/5,000 mixed, 69/3,000 investment (up to -£1,532.70), 37/3,000 edge.
- (c) **The condition is a cliff.** Crossing into higher-rate liability extends the bands by the whole contribution
  at once: `f2b_condition_cliff` (wages £50,270 to £50,271, gains £30,000, contribution £10,000: income tax + CGT
  **fall by £599.74**; extended always, the pound costs 26p). In the monotonicity scan (RESULTS.md) this is the only
  cause of income tax + CGT falling as an income rises under the default reading (8 of 45,315 perturbations of
  investment and edge households), also via the savings allowance: savings nil-rated above the limit make one
  "higher-rate" for s. 12B but not one on whom higher-rate tax "is chargeable" for s. 192(4).
- Model default: the condition, generously read; `--ras-literal` (main rates only), `--ras-unconditional`
  (CG21204's wording; PE). Open reading question, not asserted as an HMRC error.

## F3. Marriage allowance (ITA 2007 s. 55B-55C): PolicyEngine transfers only the unused allowance
- s. 55B(4)-(6): the transferable amount is 10 % of the s. 35(1) allowance rounded up to £10 (£1,260); the gaining
  spouse's tax falls by 20 % of it (£252, within the tax, s. 29(2)); the relinquishing spouse's allowance "is reduced
  ... by the transferable amount". s. 55C(1): anyone entitled to a personal allowance who stays a basic-rate taxpayer
  after the reduction may elect; the income test of s. 55C(2) applies only to non-residents qualifying under s. 56(3).
- PE: transfers the partner's unused allowance (allowance less net income), capped at 10 %, rounded up to £10; does
  not reduce the transferor's allowance.
- Consequences: (i) same couple total when the transferor's income is non-savings income below the allowance (the
  common case; the gov.uk/marriage-allowance example is reproduced in `Checks.lean`); (ii) PE **misses** elections that
  pay because the transferor's income above the reduced allowance bears 0 % or 8.75 %: theorem `f3_ma_full_transfer`
  (household mixed-144: statute £388.06, PE's rule £529.81: the couple loses £141.75); (iii) PE **over-gives** where
  the recipient cannot use the full £252 (the statutory election would cost the transferor more than it saves;
  mixed-4483: £86.60) and where it rounds the unused part up (mixed-2059: £1.80); (iv) the split between spouses
  differs.
- Who is right: the statute (Lean); HMRC's guidance agrees ("you will now pay tax on £190"; the lower earner "must
  normally have an income below your Personal Allowance").
- Effect: 51/5,000 mixed (-£252 to +£86.60), 58/3,000 investment, 48/3,000 edge households.

## F4. Relief at source: PolicyEngine treats it as a deduction
- FA 2004 s. 192(1): the member pays net of basic-rate tax, which HMRC pays to the scheme, whatever tax the member
  pays; s. 190: up to relevant UK earnings or £3,600; s. 192(4): higher-rate relief through the bands; s. 188(3)(a):
  none after 75; ITA 2007 s. 58: the gross contribution reduces adjusted net income.
- PE deducts relieved contributions from taxable income. For a taxpayer with enough tax this equals band extension +
  relief at source (the contract's `incomeTax` subtracts the relief at source for that reason). It differs (i) for
  non-taxpayers and low earners: no relief beyond the tax otherwise due (up to £720, 20 % of £3,600, per non-earner);
  (ii) a deduction lowers non-savings income and so enlarges the starting rate for savings (an extension does not);
  (iii) CGT (F2b).
- Who is right: the statute. Effect: 429/5,000 mixed (-£3,708.40 to +£642.64), 339/3,000 investment, 251/3,000 edge.

## F5. PolicyEngine has no Gift Aid charge (ITA 2007 s. 424) and no married couple's allowance (ss. 45-46)
- s. 424: if the tax treated as deducted from Gift Aid gifts exceeds the income tax and CGT charged, the difference is
  charged (Step 7, s. 30). PE's Step 7 list omits it. Theorem `giftaid_charge_exceeds_income`: no income, £800 gift:
  £200 charged (tax exceeds income). Effect: 179/5,000 mixed, 103/3,000 investment (up to £4,981), 94/3,000 edge.
- ss. 45-46 (a spouse born before 6 April 1935): 10 % of £11,270, reduced by half the excess of adjusted net income
  over £37,700, not below £4,360. PE's `married_couples_allowance` is an input with no formula: no couple gets it
  unless it is supplied, and PE gives the marriage allowance instead (s. 55B(2)(d) forbids both). Effect: 73/5,000,
  43/3,000, 53/3,000, 29/2,000 households (-£143.62 to -£1,127).

## F6. PolicyEngine's s. 25(2) search misses cheaper allocations
- s. 25(2): "deduct the reliefs and allowances in the way which will result in the greatest reduction in the
  taxpayer's liability". With savings straddling the basic rate limit, setting the allowance against savings instead
  of earnings puts the savings nil-rate band in the higher band, where it saves 40 % instead of 20 % (the idea of
  HMRC's own Dividend Allowance factsheet Example 6, reproduced in `Checks.lean`).
- With PE's conventions switched on in Lean, Lean is £27.80-£100 cheaper than PE in 4 of 11,000 households
  (invest-246, invest-462, edges-1499, edges-2365): PE does not search that allocation. In law this matters for Step 2
  reliefs such as contributions relieved on a claim (FA 2004 s. 194).
- Lean's search is exact (all break points of a piecewise-linear function); checked independently against random
  allocations for 13,587 people with savings or dividends: never beaten.

## F7. HMRC's rates table: the pound from £125,140 to £125,141
- s. 10(3A): additional rate "on an individual's income above the higher rate limit" (£125,140, s. 10(5A)).
- HMRC "Income Tax rates and allowances for current and previous tax years": higher rate "£37,701 to £125,140",
  additional rate "Over £125,141" (also Scotland's top rate); gov.uk/income-tax-rates (previous years): "Over
  £125,141"; HMRC's employer rates page: "Above £125,140". The table leaves the 125,141st pound in no band. Theorem
  `f6_pound_125141`: the statute charges it at 45 %. Who is right: the statute; the table is off by one.

## F8. National Insurance: prescribed equivalents and HMRC's rounding
- S.I. 2001/1004 regs. 10-11 fix weekly, monthly and annual thresholds that are not multiples of each other: primary
  threshold £242 a week (x 52 = £12,584), £1,048 a month (x 12 = £12,576), £12,570 a year (theorem `pt_equivalents`;
  SSCBA s. 5(5) allows up to £1 above the arithmetical equivalent). The same pay bears different NI by pay frequency
  (the model uses the annual earnings period and says so).
- HMRC's 2025-26 NI test data compute the employee's contribution as the rounded total less the rounded employer's
  contribution (weekly pay £242.32: 0.32 x 8 % = 2.56p, employee 2p): see RESULTS.md.

## F9. PolicyEngine presumes relationships from ages
- In a household entered without relationships PE presumes a member 20 or more years younger than the eldest adult is
  their child: a married couple aged 24 and 46 was read as parent and child (no marriage allowance; wrong HICBC
  partner). An input presumption, documented by PE, not a legal error; the harness states the relationships.

## F10. OECD Taxing Wages: three simplifications of the UK statute
- The OECD's 2025 UK figures (Taxing Wages 2026, SDMX dataflow DF_TW_DECOMP) agree with Lean on employee NI in all 804
  cases and on income tax in all, up to three conventions: (a) the tapered allowance is not rounded up to a whole pound
  (s. 35(3)): 24 cases, up to 20p more tax; (b) child benefit is annualised as 365/7 weeks (£2,257.79 for two
  children) where ITEPA s. 681H(3) counts weeks by their Mondays: 52 in 2025-26 (£2,251.60); (c) the HICBC is
  continuous, without s. 681C(3)'s whole-percent and whole-pound rounding (up to £20.23; and at 100 % the statute
  charges £2,251 of £2,251.60, leaving the household 60p).
- Who is right: the statute; the OECD's choices are reasonable modelling simplifications for an international table,
  not errors in its own terms.

## L. Lean errors the referee found (fixed)
- L1. FA 2004 s. 188(3)(a): no relief for contributions after 75 (first version gave it; PE right).
- L2. S.I. 2001/1004 reg. 100: annual maximum of Class 4 for earners also paying Class 1 (first version lacked it;
  PE right; 20 of 500 households, up to £1,508). Now theorem `reg100_cap` (in the capped regime extra wages cost
  2 2/3 % of NI).

## R. Readings where the statute is silent or the household under-specified (model choices, not findings)
- Liability rounded down to the penny (the Income Tax Acts round only in s. 35(3), s. 55B(5), ITEPA s. 681C(3)).
- Age read on 6 April 2025; pensionable age 66 (no Class 1 or Class 4 from 66; reg. 91); born before 6 April 1935 =
  aged 90 or more.
- Class 1 on the annual earnings period; Class 2 nil (treated as paid above £6,845; voluntary below).
- Child benefit 52 weeks (Mondays 7 April 2025 to 30 March 2026, ITEPA s. 681H(3)); children 16-19 assumed qualifying.
- Household: investment income split equally (ITA 2007 s. 836); Gift Aid by the higher-income adult; pension
  contributions pro rata to earnings; elections (marriage allowance either way, married couple's allowance, blind
  person's allowance transfer) chosen to minimise the couple's income tax + CGT.
- s. 423 (extinguishing allowances before the s. 424 charge) not separate: same total except via the CGT band.
- `rentalIncome`, `selfEmployment` taken as profits (no £1,000 property or trading allowance).

## Not modelled
FA 2004 s. 192A (Scottish relief-at-source adjustment; Scottish rates are modelled, with s. 192(4A)); the winter fuel
payment charge (FA 2026 Sch. 10; flagged in `unsupported` for anyone 66+); pension
annual allowance charge; losses; trading and property allowances; BADR; top slicing; employer contributions.
