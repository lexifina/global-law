# Canada (federal + Ontario), 2025: findings

Model: `lean/` (CaTax on TaxKernel), exe `catax`. Lean names refer to `lean/CaTax/Findings.lean`,
`Theorems.lean` and `Checks.lean` (all build; `#guard`s are evaluated at build time). Amounts in CAD, Ontario
residents, 2025; benefits are those for July 2025 to June 2026 with the household's 2025 income as base-year income.

## Round 8 note (improve-anglo, 2026-11-19)
The GST/HST credit now follows S.C. 2026 for base taxation years 2024 and 2025: the January 2026 one-time amount
(ITA s. 122.5(3.004), (4.4)) and, from July 2026, s. 122.5(3.005) in place of (3) ((4.6)). Amounts again shift: F4
$16,824.62 -> $17,125.47, F5 $42,696.50 -> $42,607.50, F6 $10,084.20 -> $10,356.20 (Lean guards updated).

## Round 7 note (improve-anglo, 2026-11-19)
Benefits are now those of the payment period whose base taxation year is the household's year (ITA s. 122.6:
July of the next year to June of the year after), not the July of the same year. Amounts that depend on benefits
shift: F4 $16,651.93 -> $16,824.62; F5 $42,710.50 -> $42,696.50; F6 $10,147.28 -> $10,084.20 (Lean guards updated);
F1 unchanged (-20 cents). F14 (OECD cash transfers) is explained by this pairing (see improve-anglo IMPROVE.md round 7).

## Validation (summary)
* **OECD Taxing Wages 2026, Canada 2025**: 52 of 56 lines exact to the cent (`harness/oecd_ca.py`, wages passed in
  cents); every tax and contribution line exact (CGTC, CGITLETC, CGITFP, SLT, EECSSC incl. the Ontario Health
  Premium) for all 8 family types. Kernel dollar-level check (`oecd_check20.py CA`, map `oecd_map.py`): 47/56 exact,
  52/56 within 1 %. The 4 misses are CTGG (F14).
* **CRA T4127 payroll formulas** (Jan 2025 120th ed. at 15 %, Jul 2025 121st ed. Option 1 at 14 %, six months each):
  federal withholding within $1 of the statute's 2025 liability at 601/601 wage levels ($0-$300,000 by $500);
  Ontario within $1 at 601/601 once LIFT, which payroll does not withhold, is added (540/601 without it) (F13).
* **PolicyEngine-Canada 0.99.2**: not usable as a referee for liabilities (F15); benefits agree where its parameters
  are current: CCB 156/205 within 1 % (exact below the first threshold; the rest is its missing s. 60(e.1)
  deduction), OCB 138/205, GST/HST credit 127/205, OSTC 132/205, CWB 162/205 (stale 2024 maxima).

### F1 Effective marginal rate above 100 % for Ontario families with four or more children at about $48,500
- kind: statute-fault (design: stacked withdrawals)
- households: single parent or one-earner couple, 4 children (ages 2, 4, 7, 9), wages $48,450 to $48,950
- amounts: each extra $100 of wages lowers net income by about 20 cents (METR 100.2 %); with 3 children 96.2 %
- provisions: OTA s. 24(2) para. 4 (Health Premium: 25 % of taxable income between $48,000 and $48,600) stacked on
  ITA s. 122.61(1) Q (CCB 23 % for 4+ children), s. 122.7(2) B (CWB 15 %), OTA s. 104(5) (OCB 8 %), ITA s. 122.5(3)
  B (GST/HST credit 5 %), OTA s. 104.11 (OSTC 4 %), s. 117(2) (14.5 %), CPP 5.95 % and EI 1.64 %
- Lean: `#guard netCents (spWith [2, 4, 7, 9] 48550) - netCents (spWith [2, 4, 7, 9] 48450) = -20`
- known? Ontario METR peaks of 96 % for single parents are published (C.D. Howe Institute e-brief on clawbacks,
  2022); a rate above 100 % for four or more children in the Health Premium step was not found in the 28 sources
  returned by two searches. Benefits follow next July's payments (base-year income): the loss arrives a year later.
- status: confirmed in the model; narrow band ($500), caused by the Premium's 25 % steps

### F2 Pension income splitting is worth up to $19,136 a year to a retired couple (known, recreated)
- kind: loophole-known (CATALOGUE K1)
- household: couple aged 70, pensions $200,000 and $0; gain with the s. 60.03 split: $19,136.47
- provisions: ITA s. 60.03; OTA follows the federal split
- Lean: `#guard netCents pensioners { splitPension := true } - netCents pensioners = 1913647`
- status: confirmed (OAS and its recovery tax are not modelled; the real gain is larger where OAS is clawed back)

### F3 Who owns the capital: up to $13,008 a year on $150,000 of dividends (known, recreated)
- kind: loophole-known (K2)
- household: couple, wages $260,000 / $0, two children; $150,000 eligible dividends held by the non-earner instead
  of half each: +$13,007.50
- provisions: ITA ss. 74.1-74.5 (attribution; s. 74.5(2) prescribed-rate loans), s. 82, s. 121, s. 118(1)(a)
- Lean: `#guard netCents (divCouple 0) - netCents (divCouple 5000) = 1300750`
- status: confirmed; the legal routes are a loan at the prescribed rate or the non-earner's own savings

### F4 Living together as a couple costs up to $16,652 a year in benefits (known, recreated)
- kind: loophole-known (K6; exploiting it by not declaring a common-law partner is evasion)
- household: $35,000 + $60,000, two children: couple (married or cohabiting) $83,246.53 vs two separate households
  $99,898.46. Marriage itself changes nothing: a cohabiting couple is a couple (ITA s. 248(1) "common-law partner"),
  so the penalty is on living together, not on marrying
- provisions: family-income tests of ITA s. 122.61 (CCB), s. 122.5 (GST/HST credit), s. 122.7 (CWB), OTA s. 104
  (OCB), s. 104.11 (OSTC). Since catax reads the kernel's `cohabiting` field (2026-11-19), the kernel's filing-unit
  scanner finds no difference between married and cohabiting couples (0 % of grid points); its earlier report of
  penalties at 72.8 % of couple points compared a couple with two unrelated adults
- Lean: `#guard netCents (coupleKids false) - netCents (coupleKids true) = 1665193`
- status: confirmed

### F5 Spreading a large capital gain over two years saves up to $42,711 (known, recreated; AMT not modelled)
- kind: loophole-known (K4)
- household: single, no other income, $1,000,000 gain in one year vs $500,000 in each of two
- provisions: ITA s. 38(a), s. 117(2), s. 118(1.1); OTA ss. 6, 16 (surtax)
- Lean: `#guard 2 * netCents (gain 500000) - netCents (gain 1000000) - netCents (gain 0) = 4271050`
- status: confirmed in the model; the alternative minimum tax (Division E.1, 100 % of gains in its base since 2024)
  is not modelled and would change both figures

### F6 Bunching income beats smoothing it for families with children (new aspect of K9)
- kind: loophole-new
- household: one-earner couple, children 4 and 9: $117,534 then $36,221 instead of $76,877 twice: +$10,147.28 over
  the two years (benefits +$7,710.42: CCB, OCB, GST/HST credit, OSTC; CWB +$2,024.78; CPP/EI ceilings +$2,620.82;
  Ontario tax -$865.44; Health Premium +$450)
- why: the income-tested benefits are concave in income (nothing withdrawn below their thresholds; the CCB rate
  falls from 13.5 % to 5.7 % above $81,222) and contributions stop at their ceilings, so two unequal years beat two
  equal ones with the same total
- how: whatever timing the household controls: the year an RRSP deduction is claimed (s. 146(5) "may deduct";
  undeducted contributions carry forward), RRSP withdrawals, capital gains, self-employed or owner-manager pay
- provisions: ITA s. 122.61(1) Q, s. 122.5(3), s. 122.7(2), s. 146(5); OTA ss. 104(5), 104.11; CPP Act s. 8; EI Act
  s. 67
- Lean: `#guard netCents (oneEarner2 117534) + netCents (oneEarner2 36221) - 2 * netCents (oneEarner2 76877) = 1014728`
- known? RRSP deductions to raise the CCB are common advice (K5); alternating years to beat smoothing was not found
  in the 18 sources returned by one search. The kernel's `timing` scanner found it blind (gain up to 11 % of AW).
- status: confirmed in the model (the benefits' one-year lag shifts the timing, not the total)

### F7 An RRSP deduction is worth most to middle-income parents, not to high earners (known, recreated)
- kind: loophole-known (K5)
- amounts: $1,000 deducted is worth $693.00 to a single parent of two at $60,000 (20.5 % federal, 18.3 % Ontario in
  the tax-reduction band, CCB 13.5 %, OCB 8 %, GST/HST 5 %, OSTC 4 %), $495.50 to a single person at $37,500,
  $482.76 at $180,000
- provisions: ITA s. 146(5); OTA s. 20 (the reduction doubles the Ontario rate in its band: theorem
  `on_reduction_band`)
- status: confirmed

### F8 The Ontario Health Premium form ignores the split income the statute adds
- kind: gov-error
- provisions: OTA s. 24(0.1) (S.O. 2023, c. 21, Sched. 13, s. 2(1)): for years ending after 2023 the premium is on
  "combined income" = taxable income + split income (s. 12.1). ON428-2025 line 89 chart: "Enter your taxable income
  from line 26000"; 5006-PC (2025) guide: the premium is payable if "taxable income on line 26000 ... is more than
  $20,000". Split income is deducted in computing taxable income (ITA s. 20(1)(ww)), so the form leaves it out.
- households: anyone with tax on split income (T1206); e.g. $20,000 taxable income and $50,000 split income: statute
  $600, form $0
- Lean: `theorem ohp_split_income_gap : ohp (dol 70000) - ohp (dol 20000) = 60000`
- status: error in the published form and guide (CRA's assessing system may add it; not visible in the form)
- draft note (not sent): "ON428 (2025) line 89 and the 5006-PC guide compute the Ontario health premium on line 26000
  taxable income. Since S.O. 2023, c. 21, Sched. 13, Taxation Act, 2007 s. 24(0.1) bases the premium on combined
  income, taxable income plus split income under s. 12.1, for taxation years ending after 2023. Taxpayers with split
  income (Form T1206) are shown a lower premium than the Act imposes. Suggest adding the split income to the chart's
  income."

### F9 The 2025-26 CCB booklet gives the child disability benefit two different thresholds
- kind: gov-error
- source: CRA T4114 (July 2025 to June 2026), "Child disability benefit": "starts being reduced when the adjusted
  family net income (AFNI) is greater than $79,087" (the 2024-25 figure), then "the reduction is 3.2% of the amount
  of AFNI greater than $81,222" (the 2025-26 figure: ITA s. 122.61(1) M, indexed by s. 122.61(5); CRA indexation page
  2025: CDB threshold $81,222)
- status: error in the publication (stale figure beside the updated one)

### F10 CCB amounts indexed separately do not meet: +23 cents (two children), -35 cents (three) at $81,222
- kind: statute-fault (de minimis)
- provisions: ITA s. 122.61(1) Q: "$4,725 and 5.7%" was 13.5 % x ($65,000 - $30,000) when enacted; s. 122.61(5)
  indexes every dollar amount separately and each is rounded to $1, so the fixed amounts ($3,061 / $5,904 / $8,310 /
  $10,059 for 2025-26) differ from the band rate times the indexed band ($3,061.45 / $5,904.23 / $8,309.65 /
  $10,059.05)
- Lean: `theorem ccb_two_children_jump : ccb [8, 12] (ccbT2 + 1) - ccb [8, 12] ccbT2 = 23`;
  `theorem ccb_three_children_notch : ccb [8, 10, 12] ccbT2 - ccb [8, 10, 12] (ccbT2 + 1) = 35`
- fix: define the upper band's fixed amount as "the maximum reduction under the lower band" (as s. 117(2) does for
  the tax brackets) rather than a separately indexed dollar amount
- status: confirmed; harmless in money, but the drafting pattern recurs

### F11 ITA s. 117(3) refers to amounts that s. 117(2) no longer contains
- kind: statute-fault (stale cross-reference, spent)
- provision: s. 117(3) "Each of the amounts of $30,754, $61,509 and $100,000 referred to in subsection (2) is deemed,
  for the purposes of applying subsection (2) to the 2004 taxation year ..."; s. 117(2) was restated in 2016 (c. 11:
  $45,282 ...) and by S.C. 2026, c. 2, s. 2 ($57,375 ...) and contains none of them (Global law: s 117 as in force
  2025-07-01 and 2026-11-19)
- status: spent and harmless; candidate for repeal in a technical bill

### F12 Ontario's unused-tuition carry-forward formula missed the 2017 caregiver credits
- kind: statute-fault (list not updated)
- provision: OTA s. 9(14)(b) "S" sums the credits under "(2), (3), (4), (5), (6), (7), (8), (9), (10), (11), (12) and
  (13)"; S.O. 2017, c. 34, Sched. 40, s. 2 added (6.1) and (7.1) (Ontario caregiver credits) to s. 9(13) "P" and to
  s. 9(14)(a) but not to "S" (Global law compare_dates 2017-12-13 / 2017-12-15)
- effect: for 2017, the only year with both a tuition credit (R > 0) and the new caregiver credits, S overstates the
  tuition credits used, so a caregiver's carry-forward of unused Ontario tuition credits is understated
- status: confirmed in the text; small and historical (R = 0 after 2017)

### F13 Payroll withheld at 15 % and 14 % for a 14.5 % year that Parliament set in 2026 (reading)
- kind: reading / convention
- facts: s. 117(2)(a) said 15 % throughout 2025 (Global law, as in force 2025-07-01); S.C. 2026, c. 2, s. 2(1), (3)
  (assented 2026-03-12) made it 14.5 % for 2025. CRA's July 2025 payroll edition applied 14 % from July ("the
  full-year tax rate for 2025 will be 14.5%"). Averaged, the two editions equal the statute within $1 at all 601
  tested wages; payroll leaves out LIFT (up to $875 over-withheld at 61 of 601 wage levels, all below about $50,000).
- lesson for versioned law: the text in force on any date in 2025 shows 15 %; the 2025 rate sits in an application
  provision of a 2026 Act that the consolidation leaves out ("Application provisions are not included in the
  consolidated text")

### F14 OECD Taxing Wages: cash transfers differ by a constant $255.09 for couples, $627.58 for the single parent
- kind: open (OECD convention, not established)
- facts: every other line matches to the cent; our CTGG is the statute's July 2025 to June 2026 entitlement (CCB +
  OCB + GST/HST credit + OSTC) on the year's income. The OECD's is higher by exactly $255.09 for all three couples
  with children at 1.0-2.0 AW (an income-independent amount) and by $627.58 for the single parent at 0.67 AW. No CCB
  blend of payment years explains it (the January-June / July-December blend is $161 below ours). The OECD's Canada
  country chapter could not be fetched (HTTP 403).
- status: open

### F15 PolicyEngine-Canada 0.99.2 cannot serve as a referee for Ontario liabilities (open-model errors)
- kind: referee error (not government)
- facts (each checked in the package source): (a) `income_tax_before_refundable_credits` subtracts
  `non_refundable_tax_credits`, which adds the credit amounts (basic personal amount $16,129) rather than the amounts
  x 14.5 %; (b) Ontario brackets fixed at the 2022 thresholds ($46,226 / $92,454) although OTA s. 23(1) para. 1, 1.1
  index them ($52,886 / $105,775 in 2025); (c) no ITA s. 60(e.1) deduction for enhanced CPP contributions; (d) the
  CCB is halved unless `full_custody` is set (shared-custody divisor by default); (e) stale amounts: OCB $1,509 per
  child (2025-26: $1,726.92), OSTC $345 ($371), CWB $1,590 ($1,633); (f) the GST/HST credit gives a single adult $184
  instead of $349 at low income and omits the $349 for an eligible dependant (s. 122.5(3)(c))
- draft issue (not filed): "Ontario 2025: non-refundable credits are subtracted as amounts, not credits
  (income_tax_before_refundable_credits); Ontario brackets not indexed after 2022; enhanced CPP deduction (ITA
  60(e.1)) missing; CCB halved when full_custody is unset; OCB/OSTC/CWB amounts not updated for 2025; GST credit
  eligible-dependant amount missing. Reference values: CRA T4127 120th/121st editions, T4114 2025-26, ON428-2025."

### F16 Observation: the dividend gross-up raises the GST/HST credit's single supplement
- kind: observation (tiny; novelty not searched)
- household: single, no other income, $10,000 of eligible dividends: net income rises by about $10,049, a rate of
  -0.49 %: the $13,800 grossed-up income phases in the single supplement (2 % over $11,337)
- provisions: ITA s. 122.5(3)(f) ("the individual's income"), s. 82(1)(b)(ii)
