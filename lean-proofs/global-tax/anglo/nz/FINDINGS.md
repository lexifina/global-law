# New Zealand (income year 2025-26; 2024-25 composite year): findings

Model: `lean/` (NzTax on TaxKernel, exe `nztax`); sources: `refs/SOURCES.md`. The Income Tax Act 2007 itself could not
be read: it is not in the Global law corpus (whose New Zealand record holds 50 other acts), and legislation.govt.nz
and NZLII refuse automated fetches (AWS WAF / Cloudflare challenges), which were not bypassed. Every provision is
therefore cited through Inland Revenue's own publications, which name the sections. Lean names refer to
`lean/NzTax/Theorems.lean`, `Checks.lean`, `Loopholes.lean` (all build, no `sorry`).

### F1 The OECD's New Zealand take-home pay leaves out the ACC earners' levy
- kind: gov-error (classification: convention of the OECD model; material)
- households: all eight OECD Taxing Wages family types, 2025 (= income year 2025-26) and 2024 (= 2024-25)
- amounts: every mapped line agrees exactly (CGTC, CGITLETC, IETC, CGITFP, CTGG: 40/40 in 2025), but the OECD's
  take-home pay exceeds ours by exactly the levy: 1.67 % of each earner's pay up to $152,790 (S67 $929.50, S100
  $1,387.32, S167 $2,316.82, M100_100 $2,774.64). Net of the levy, take-home pay agrees 8/8 (2025) and 8/8 (2024).
- provisions: Accident Compensation Act 2001 s 219 ("An earner must pay ... levies to fund the Earners' Account"),
  s 221 (collected "by deduction from employee earnings"); rate 1.67 % and maximum $2,551.59 (IRD payroll
  specification 2025-26 s. 2.1; IRD "ACC earners' levy rates")
- Lean: `accLevy`; `#guard accLevy p2025 (nzd 200000) = 255159`
- status: confirmed (results/oecd_nz.md). New Zealand therefore shows no employee contribution in OECD comparisons
  although every employee pays a compulsory, earnings-related, capped levy withheld from pay with PAYE.

### F2 The OECD computes 2024-25 tax by day-weighting the two schedules, not with the Act's composite rates
- kind: gov-error (classification: convention/approximation of the OECD model; immaterial)
- households: OECD 2024 (= income year 2024-25), all types
- amounts: OECD tax = (121/365) x old schedule + (244/365) x new schedule, exactly (difference 0.00 on S67, S100,
  S167). The Act's composite rates (12.82 %, 21.64 %, 30.99 %) are those weighted rates rounded down, so the statutory
  tax is $0.22 (S67) to $0.59 (S100) per earner lower; 3 of 8 couples miss "exact" by $1.02-$1.17.
- provisions: ITA 2007 sch 1 pt A, composite rates for 2024-25 (IRD Special report, Taxation (Budget Measures) Act
  2024, p. 8; IRD "Tax rates for individuals")
- Lean: `composite_rates_round_down`, `composite_le_dayweighted` (for every income: 365 x composite tax <= 121 x old +
  244 x new, and less than 1 bp of income below it)
- status: confirmed (harness/oecd_nz.py; the 121/365 hypothesis gives 0.00, 4/12 gives +1.46 to +1.90, 122/365 +2.19
  to +2.86).

### F3 IRD's July 2025 Working for Families chart divides the family tax credit by 365/7 weeks; IRD's rule divides by 52
- kind: gov-error (official guidance contradicts itself)
- households: every cell of IR271 (July 2025, 1 April 2025 - 31 March 2026): 53 income bands x 1-6 children
- amounts: the chart is reproduced exactly (636/636 cells) by "entitlement at the top of the band / (365/7), rounded
  down" for the FTC and "/ 52" for the IWTC. IRD's rule ("Your instalments will be equal to your full-year entitlement
  divided by ... 52 for weekly payments. We round your instalments down") gives a higher FTC in 185 of 318 FTC cells,
  by $1-$2 a week. IRD's own example contradicts the chart: Sarah, 2 children, $37,800: "$13,654 (full year
  entitlement) / 52 = $262"; the chart says $261. The two 2024-25 charts (April and July 2024) follow / 52 exactly
  (228/228 cells each).
- provisions: IRD "Family tax credit" (archived 14 Oct 2025); IR271 July 2025, July 2024, April 2024
- Lean: `#guard (wff p2025 2 0 0 (nzd 37800) true false 0).ftc = nzd 13654`
- status: confirmed (harness/ir271_chart.py, results/ir271_chart.json). The chart says its amounts are estimates, so
  the effect is understated published entitlements, not payments; still an inconsistency to fix.
- draft note to IRD (not sent): "IR271 (July 2025): the FTC columns equal the annual entitlement at the top of each
  band divided by 52.14 (365/7) and rounded down; the IWTC columns and your web guidance divide by 52. E.g. 2
  children, $0-$42,700: $13,654 / 52 = $262.58, so $262 (your Sarah example); the chart shows $261."

### F4 IRD's 2025-26 minimum family tax credit example states a stale entitlement
- kind: gov-error (guidance; corrected in the 2026-27 page)
- households: IRD example "Casey" (salary $31,000 + self-employed $2,000, 3 children)
- amounts: page (archived 8 Oct 2025): "Her full-year entitlement is $7,111" and then "$35,316 - Family income after
  tax: $28,317 = minimum family tax credit for the full year: $6,999". $6,999 is right (tax on $33,000 = $4,683).
  $7,111 = $35,316 - $28,205, the after-tax income under the rates before 31 July 2024: the threshold in the
  sentence was updated, the tax behind it was not.
- provisions: s ME 1 (MFTC threshold $35,316: Special report p. 4)
- Lean: `#guard tax25 33000 = 468300`, `#guard (wff p2025 3 0 0 (nzd 33000) true true (tax25 33000)).mftc = nzd 6999`
- status: confirmed; the 2026-27 page is consistent ($36,604 - $28,317 = $8,287).

### F5 IRD's 2025-26 in-work tax credit example states the pre-Budget amount
- kind: gov-error (guidance; corrected in the 2026-27 page)
- households: IRD example "Jaimee" (5 children, $41,600)
- amounts: page (archived 17 Aug 2025): "In her case, it totals $5,330" above a table whose total is $6,630
  ($5,070 + $780 + $780). $5,330 = $3,770 + 2 x $780: the IWTC base before 31 July 2024. The table is also headed
  "Full family tax credit" although it lists in-work tax credit amounts.
- provisions: s MD 10 (IWTC base $3,770 -> $5,070 from 31 July 2024; Special report p. 3)
- Lean: `#guard (wff p2025 5 0 0 (nzd 41600) true false 0).iwtc = nzd 6630`
- status: confirmed; the 2026-27 page is consistent ($9,230).

### F6 Arithmetic and wording errors in IRD's special report on the Taxation (Budget Measures) Act 2024
- kind: gov-error (guidance)
- households: "Alvien" (2025-26, $66,000, 11 eligible months)
- amounts: "($520 - 0) x (11/12) = $477.66"; 520 x 11/12 = 476.666..., i.e. $476.67 (or $476.66 truncated), not
  $477.66. The same example calls $66,000 "the new maximum threshold"; it is where abatement starts (the maximum is
  $70,000, as p. 11 of the same report says).
- provisions: ss LC 13-LC 15 (Special report pp. 11-12)
- Lean: `#guard ietc p2025 (nzd 66000) * 11 / 12 = 47666`
- status: confirmed.

### F7 The special report's composite IETC formula, as printed, goes negative
- kind: gov-error (classification: reading; the Act's own text could not be read)
- households: 2024-25, net income $48,001-$70,000
- amounts: "((($P - X) x 121/365) + (($P - Y) x 244/365)) x EM/12" with $P = $0 when income is "more than the maximum
  threshold of the applicable setting" ($48,000 for the old setting) but X (13 c per dollar over $44,000) still
  charged and nothing floored: at $60,000 the printed formula gives -$341.92 (`ietc2024Printed`), against $347.61 if
  each period's amount is floored at nil (`ietc2024`, the model's reading, which reproduces the report's Elizabeth
  example $476.90 and the OECD's 2024 IETC on all eight types).
- provisions: ss LC 13-LC 15, composite calculation (Special report pp. 12-13)
- Lean: `ietc2024Printed`, `ietc2024`; `#guard ietc2024 (nzd 45000) = 47690`
- status: open (the Act's wording needed; not retrievable here).

### F8 The personal-services attribution threshold ($70,000) no longer matches the rate thresholds it protects
- kind: statute-fault (classification: reading; possibly deliberate)
- households: a contractor providing personal services through an associated company or trust
- amounts: the attribution rule applies when the working person "earns net income of more than $70,000" (IRD
  "Attribution rule for income from personal services", saved in refs/). $70,000 was the start of the 33 % band
  until 30 July 2024 (Special report p. 6, "Previous threshold ... $70,001 - $180,000"); since 31 July 2024 the 33 %
  band starts at $78,100 and 39 % at $180,000. The rule exists so that "people do not avoid the higher income tax
  rates by diverting employment income to an associated entity" (IRD), yet its threshold did not move with them.
- provisions: ITA 2007 attribution rule for personal services (IRD page; section not named there); sch 1 pt A
- Lean: none (outside the household model)
- status: open (the threshold is in the Act; not read). A "thresholds not updated together" candidate.

### F9 Working for Families blocks the IETC: a notch of up to $1,040 where the last dollar of WFF abates
- kind: loophole-new (notch; an election under one reading)
- households: couple, 1 child, $44,672 each (family income $89,344): WFF is $0.12, so neither partner gets the IETC;
  at $44,673 + $44,672 WFF is nil and both get $520: net income rises by more than $1,040 for $1 more pay. With 2
  children the point is $112,048 (equal earners $56,024 each, both in the $24,000-$66,000 full-credit range); with 3
  children $134,752 (IETC $341.12 each).
- provisions: ss LC 13-LC 15 (no IETC for a month in which the person is "eligible to receive Working for Families
  tax credits": Special report p. 11; IRD's IETC page: "you or your partner are entitled to and receive Working for
  Families"); WFF abatement (subpart MD)
- Lean: `wff_ietc_notch : coupleNet 44673 44672 1 - coupleNet 44672 44672 1 > 104000`
- status: under IRD's web wording ("entitled to and receive"), a family whose WFF entitlement is below $520 per
  eligible partner gains by not claiming WFF (up to $1,040 less the WFF given up); under the special report's
  ("eligible"), the notch cannot be avoided. Not found in 1 web search (20 results) or IRD's IETC/WFF pages.

### F10 The minimum family tax credit band has an effective marginal rate above 100 % (101.67 %; 113.67 % with a student loan)
- kind: loophole-known (METR; partly known)
- households: sole parent or one-earner couple with children, salary up to $41,483 a year (MFTC hours test: 20 h
  sole parent, 30 h couple)
- amounts: the MFTC tops income *after income tax* up to $35,316, so income tax and MFTC together take 100 % of each
  extra dollar; the ACC earners' levy (1.67 %) is not part of "after tax" (IRD's examples deduct only income tax:
  Jeremy "$27,000 - tax payable: $3,633"), so net income falls by 1.67 c per dollar; a student loan adds 12 % above
  $24,128. $30,000 -> $30,100: net -$1.67 (-$13.67 with a student loan). Found blind by the kernel's METR scan
  (101.8 %, 0-0.5 AW) and by harness/scan_nz.py; the same in 2024-25 (101.60 % / 113.60 %).
- provisions: s ME 1; ACC Act s 219; Student Loan Scheme Act 2011 (12 % above $24,128: IRD payroll spec s. 2.2)
- Lean: `mftc_tops_up` (all inputs: after-tax income + MFTC = threshold), `mftc_acc_over_100`, `mftc_sl_over_100`
- status: the 100 % withdrawal is the MFTC's design (Special report p. 4: "for every dollar a family earns over the
  MFTC threshold, their MFTC entitlement reduces by a dollar"); rates above 100 % from stacking with the ACC levy and
  WFF abatement are discussed in New Zealand commentary (Newstalk ZB, "how some lower income households could end up
  with a 128 per cent tax rate", about a later year); the 101.67 % across the whole 2025-26 band was not found stated.

### F11 "Help with household expenses" counts as family income all-or-nothing at $5,000
- kind: statute-fault (notch; from IRD guidance, the Act not read)
- households: family with 2 children, family income $60,000, grandparents pay household bills
- amounts: IRD: "If the total for the year is more than $5,000, the total amount must be included as family income.
  If the total is less than $5,000, none of it is included." $5,001 of help costs $1,350.27 of WFF (27 % of $5,001);
  $5,000 costs nothing (and exactly $5,000 is in neither sentence).
- provisions: family scheme income adjustments (IRD "Working out your family income"; form IR215)
- Lean: `help_notch`
- status: open; excluding only the first $5,000 (as the $500 rule for children's passive income already does) would
  remove the notch.

### F12 The IETC starts with a $520 notch at $24,000
- kind: loophole-known (design notch)
- households: any individual not on WFF, a main benefit or NZ Super; net income $23,999.99 vs $24,000
- amounts: one cent more income gives $520; at the top the credit abates smoothly to nil at $70,000 (no jump).
- provisions: ss LC 13-LC 15; IRD IETC page ("between $24,000 and $66,000 - you get $10 per week")
- Lean: `ietc_notch`, `ietc_top_continuous`, `ietc_abatement_step`, `ietc_le_max`, `ietc_nonneg`
- status: known (published eligibility floor). The credit is also paid on passive income (K05 in CATALOGUE.md).

### F13 Table = statute: IRD's PAYE tables and payroll formulas reproduce the schedule
- kind: model-fix (validation result; no error found)
- amounts: IR340 (April 2025) weekly and fortnightly tables, codes M, ME, SL, SB, S, SH, ST, SA: 15,384 rows, 69,228
  cells, all equal to IRD's Payroll Calculations & Business Rules Specification 2025-26 (ss. 5.2-5.6); the spec's
  "rate x income - constant" formula equals sch 1 pt A for every whole-dollar income (Lean, all inputs); weekly PAYE
  x 52 is within 1 cent a week of the statutory annual tax + ACC levy (truncation only).
- Lean: `spec_eq_statute` (for all a, specTicks a = sched2025.ticks (nzd a))
- status: confirmed (harness/paye_tables.py, results/paye_tables.json).

### F14 OpenFisca-Aotearoa's tax parameters stop in 2010
- kind: gov-error (public open-source model; classification: error, stale)
- amounts: github.com/ServiceInnovationLab/openfisca-aotearoa (last commit 2025-03-14):
  `parameters/taxes/income_tax/individual_income_tax_rate.yaml` ends at 2010-10-01 (no 39 % band above $180,000,
  none of the 2024 thresholds); FTC eldest/subsequent child $5,878 / $4,745 from 2018-07-01 (2025-26: $7,524 /
  $6,130); WFF abatement rate 25 % from 2018-07 (2025-26: 27 %). It cannot serve as a 2025-26 referee.
- draft issue (not filed): "Income tax and Working for Families parameters are out of date:
  individual_income_tax_rate.yaml has no values after 2010-10-01 (missing the 39 % rate above $180,000 and the
  thresholds 15,600 / 53,500 / 78,100 in force from 31 July 2024); family_tax_credit eldest_child /
  subsequent_child and full_year_abatement_rate stop in 2018 (IRD, 2025-26: $7,524 / $6,130; 27 % above $42,700)."
- status: confirmed (clone in ext/openfisca-aotearoa).

### F15 The Act's 2024-25 composite rates are rounded down (in the taxpayer's favour)
- kind: statute-fault (observation; immaterial)
- amounts: 12.82 % vs 12.8205 %, 21.64 % vs 21.6438 %, 30.99 % vs 30.9945 % (day-weighted); at most 1 bp of income in
  the composite bands (about $0.67 for incomes above $78,100).
- Lean: `composite_rates_round_down`, `composite_le_dayweighted`
- status: confirmed.

### F16 Owner-managers: dividends avoid the ACC levy; at lower profits they cost more because excess imputation credits are not refunded
- kind: loophole-known
- households: owner-manager with profit $300,000 (a fully imputed dividend instead of salary saves $2,551.59, the
  whole ACC levy) and $150,000 (the dividend route costs $117.50 more: credits at 28 % exceed the tax on the dividend
  and the excess becomes a loss carried forward, not a refund)
- provisions: ACC Act ss 219-221 (levy on earnings only); IRD "Maximum imputation ratio" (28:72)
- Lean: model scenarios (harness/loopholes_nz.py K03, K03b); `imputationCreditToLoss` in the output
- status: known practice.

### W5S-1 nz-netpay: no independent earner tax credit (W5 review pass 2, 2026-11-20)
- kind: software-error
- `nz_open_nz_netpay_grid`: -520 per eligible earner on 236 of 263 dev misses; the tool has no IETC (no reference in its code; PAYE at tax code M). ITA 2007 ss LC 13-LC 15: $520 for net income 24,000-66,000, abated to 70,000, for 2025-26. Software omission (an earner without the ME code gets it at year end).
- status: recorded (world/IMPROVE_W5.md pass 2)
