# Ireland 2025: findings

Model: `lean/IeTax` (TaxKernel 1.0). Lean names in `IeTax/Findings.lean`, `Theorems.lean`, `Checks.lean`. Scans in
`results/search/` (from `harness/scan.py`). Amounts in euro, year of assessment 2025 unless stated.

### F1 OECD's own table books USC inside "income tax before credits" for one household type only
- kind: gov-error (OECD data, classification inconsistency)
- households: OECD Taxing Wages, Ireland, S67 (single, 67 % AW = €40,372.71), years 2024 and 2025.
- amounts: CGITLETC S67 2025 = €8,831.72 = 20 % x €40,372.71 (€8,074.54) + USC €757.18. For every other type
  (S100, S167, SP67, couples) CGITLETC is income tax only (S100: €15,303.11 = €8,800 + 40 % x €16,257.78). 2024
  likewise (S67: €8,635.20 = €7,775.48 + USC €859.72).
- provisions: none (classification); USC is TCA Part 18D, separate from income tax (s. 531AM(1)).
- Lean: `harness/oecd_ie.py` lines; the model's CGITLETC matches the OECD on 7 of 8 types to €0.20 (wage rounding).
- status: open; draft note to the OECD Taxing Wages team: "Ireland, family type S67 (single, 67 % AW), measure
  CGITLETC, 2024 and 2025: the value includes USC (equals CGITLETC + USC), while the other seven family types exclude
  it. CGITFP is consistent for all eight."

### F2 OECD charges employee PRSI at 4.1 % for all of 2025; the rate was 4.2 % from 1 October 2025
- kind: gov-error (OECD model)
- households: all eight OECD types (every earner is above €424 a week).
- amounts: OECD EECSSC / gross = 4.1000 % for 2025 (S100: €2,470.57 on €60,257.78); statute: 39 Friday pay days at
  4.1 % and 13 at 4.2 % = 4.125 %: S100 €2,485.63 (+€15.06), M100_100 +€30.12. The OECD's own 2024 figures use the
  blended 4.025 % (4 % to September, 4.1 % from 1 October 2024), so 2025 is inconsistent with its own method.
- provisions: SWCA 2005 s. 13(2)(db)(ii); Social Welfare (Miscellaneous Provisions) Act 2024 s. 3(2) and Table
  amendment 4, col. (5) ("on and from 1 October 2025 ... 4.2 per cent").
- Lean: `prsiA` (39 x 4.1 % + 13 x 4.2 %); `--prsi41` reproduces the OECD exactly (31 of 32 lines within €1).
- status: open; draft note to the OECD: "Ireland 2025: employee PRSI (Class A1) rose from 4.1 % to 4.2 % on
  1 October 2025 (S.W.(M.P.) Act 2024 s. 3(2)); TW 2026 applies 4.1 % for the whole year, whereas TW 2025 blended
  the October 2024 increase (4.025 %). Blended 2025 rate: 4.125 %."

### F3 Class S PRSI for a contribution year in which the rate changes: the statute is silent; 4.125 % is a reading
- kind: statute-fault (reading)
- households: self-employed and people with unearned income of €5,000 or more.
- amounts: €100,000 of trading income: 4.1 % = €4,100; 4.2 % = €4,200; blended 4.125 % = €4,125 (the published
  practice for 2025, as 4.025 % for 2024; Saffery "Upcoming PRSI rate changes effective 1 October 2025").
- provisions: SWCA s. 21(1)(a) charges "4.2 per cent of the reckonable income" of the contribution year (an annual
  base), and SW(MP)A 2024 s. 3 changes the words on 1 October; nothing says how an annual charge is apportioned.
- Lean: `prsiS` (rate `prsiClassSNum/Den` = 4.125 %).
- status: reading adopted; a transitional apportionment rule in the Act would settle it.

### F4 OECD does not round the working family payment up to the euro
- kind: gov-error (OECD model; convention)
- households: SP67 (lone parent, 2 children, €40,372.71).
- amounts: weekly WFP = 60 % x (€806 - €688.19) = €70.69; s. 229(2): "any fraction of €1 shall be treated as €1" ->
  €71 a week: €3,692 a year v OECD €3,675.78 (+€16.22). (The model's family income also uses PRSI at 4.125 %.)
- provisions: SWCA s. 229(1)-(2); s. 228 as substituted by SWA 2024 s. 13 (€806 for 2 children from 2 Jan 2025).
- Lean: `hhCalc` WFP; `--wfp-exact` reproduces the OECD.
- status: open (minor).

### F5 Revenue's Employers' Guide to PAYE: the USC worked example is wrong by €4.99 a week
- kind: gov-error (official guidance)
- households: "Mary earns €52,000 per annum (€1000 per week)", TDM Part 42-04-35A para. 9.3 (last reviewed
  September 2026), https://www.revenue.ie/en/tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-42/42-04-35A.pdf
- amounts: the guide's own 2026 weekly cut-off points (€231.00 / €551.92 / €1,347.00) give €1.155 + €6.42 + €13.44 =
  €21.01 (= 1/52 of the 2026 annual USC on €52,000, €1,092.82, TDM 18D-00-01 bands). The guide prints €26.00: its
  lines use the 2025 cut-off €526.58 ("€295.58 (€526.58 - €231) @ 2%") and "€473.42 @ 3% = €18.94", which is 4 %
  (the 2024 rate); 3 % is €14.20. An employer copying it would over-deduct about €259 a year. Also a typo in the
  weekly table: "COP 2: 1,1655.76" (week 3; 3 x €551.92 = €1,655.76).
- provisions: TCA s. 531AN Table Part 1 (2026 bands, FA 2025); USC Regulations 2018 reg. 14 (cumulative basis).
- Lean: `Checks.lean`: `uscWeek 23100 55192 134700 (eur 1000) = 2101`; the guide's lines `= 591`, `= 1894` (4 %)
  v `= 1420` (3 %).
- status: open. Draft to Revenue (feedback on TDM 42-04-35A): "Para. 9.3, USC example (Mary, €1,000 a week): with
  the 2026 cut-off points shown in the same example the week-1 USC is €21.01 (€231 x 0.5 % + €320.92 x 2 % +
  €448.08 x 3 %), not €26.00; the printed lines use the 2025 cut-off point €526.58 and 4 % on €473.42. Also in
  Example 1 (weekly), week 3, 'COP 2: 1,1655.76' should read 1,655.76."

### F6 The Law Reform Commission's revised Social Welfare Consolidation Act shows the wrong employer PRSI threshold from 1 October 2026
- kind: gov-error (official consolidation; versioned law)
- households: every employer (employer PRSI rate split); not 2025 (the error is in the text from 1 Oct 2026).
- amounts: SWCA s. 13(2)(d) employer threshold €527 -> €552 from 1 January 2026 (Social Welfare and Automatic
  Enrolment Retirement Savings System (Amendment) Act 2025 (No. 19 of 2025) s. 2(1): "“€552” for “€527”"). The LRC
  revised act updated to 21 January 2026 shows "F115[€552]"; the current revision (with the 1 October 2026 rate
  substitutions, banner "as of 11 November 2026") shows "F115[€527]" while its annotation F115 still says
  "Substituted (1.01.2026) by ... Act 2025 (19/2025), s. 2(1)(a)". The October 2026 change (SW(MP)A 2024 s. 3(3),
  Table amendments 2-3) substitutes only the rate words ("8 per cent" -> "8.15 per cent"), so €552 should remain.
  The prospective (future-dated) versions in the January edition already carried €527 (drafted before Act 19/2025):
  the editors appear to have switched in that stale prospective text. Global law inherits the error
  (`compare_dates` 2026-01-21 -> 2026-10-01 shows "€552" -> "€527").
- provisions: SWCA s. 13(2)(d)(i)-(ii); Act 19/2025 s. 2; SW(MP)A 2024 s. 3(3).
- Lean: not in the 2025 model (employer side); evidence `refs/swca_rev.txt` line 4281 (€552) and
  `refs/swca_rev_oct2026.txt` line 4287 (€527).
- status: open. Draft to the LRC Revised Acts team: "Social Welfare Consolidation Act 2005 (revised), s. 13(2)(d)(i)
  and (ii): the current revision shows €527 at F115/F117, but those annotations cite s. 2(1) of Act 19/2025, which
  substituted €552 for €527 from 1 January 2026; the 1 October 2026 amendments (Act 24/2024 s. 3(3)) change only
  the percentages. The prospective versions of s. 13(2)(d) in the January 2026 revision also show €527."

### F7 Revenue's notes for guidance quote a basic personal tax credit years out of date
- kind: gov-error (official guidance; minor)
- households: widowed persons (s. 461A).
- amounts: Notes for Guidance TCA 1997 Part 15 (Finance Act 2025 edition), s. 461A summary: "€540 in addition to the
  basic personal tax credit of €1,650"; the credit is €2,000 for 2025 (s. 461(c), FA 2024 s. 3(b)(iii)); €1,650 applied
  up to 2021 (Revenue's chart shows €1,700 for 2022).
- provisions: TCA s. 461, 461A.
- status: open (minor). Draft: "NfG Part 15, s. 461A summary: '€1,650' should read '€2,000' (2025 and 2026)."

### F8 Revenue's weekly tax table figures round up, its USC cut-offs round down
- kind: statute-fault (table v statute: convention)
- households: weekly-paid employees on the cumulative basis.
- amounts: TDM 42-04-35A: weekly cut-off point €846.16 (44,000/52 = 846.1538, rounded up) and credit €76.93
  (76.923, up): over 52 weeks €0.32 more band and €0.36 more credit than the statute's annual amounts (about €0.42
  less tax a year, corrected only on a year-end review); the USC cut-off €551.92 (28,700/52 = 551.923) is rounded
  down. Rounding in the guide's lines is also mixed (€1.155 -> €1.15; €41.536 -> €41.54).
- provisions: TCA s. 15, 461, 472 (annual amounts); Income Tax (Employments) Regulations 2018 (cumulative basis);
  the Acts state no rounding.
- Lean: `Checks.lean` `weeklyOf`, `payeWeek` (the guide's €133.84 reproduced), `52 * weeklyOf (eur 44000) - eur 44000 = 32`.
- status: convention; harmless but undocumented.

### F9 The PRSI credit (€12) has not moved with five rate rises: the €352.01 notch grows from €2.08 to €4.54 a week
- kind: statute-fault (amounts not updated together)
- households: employees on €352-€424 a week (part-time workers).
- amounts: one cent above €352 a week the contribution jumps from 0 to rate x €352.01 - €12: €2.08 at 4 % (2016-Sep
  2024), €2.43 at 4.1 %, €2.78 at 4.2 % (from Oct 2025), €4.54 at 4.7 % (Oct 2028, already enacted). Annual effect at
  €18,304: €122 net loss, €170 dead zone (S1). Inside the band the marginal PRSI rate is rate + 1/6 (20.77 %).
  The €2.43 residual is described by payslipiq.co.uk ("PRSI credit taper"); a 2024 Department circular says "no
  change to the employee PRSI Credit" with the 4.1 % rate. The growth to €4.54 under the enacted schedule was not
  found in the 15 results of 1 search.
- provisions: SWCA s. 13(2)(a)-(b) (€352, €424, €12, €352.01, unchanged since SWPA 2015 s. 10, 1 Jan 2016); SW(MP)A
  2024 s. 3 and Table (rates 4.1 -> 4.7 %).
- Lean: `prsi_notch_400/410/420/470`, `prsi_notch_352`, `prsi_credit_band_marginal`, `prsi_step_424`.
- status: open. Fix: make the maximum credit rate x €352 (e.g. "the rate of the reckonable earnings up to €352"), so
  the notch is 0 at any rate.

### F10 USC €13,000 notch (known)
- kind: loophole-known (K5)
- amounts: €0 at €13,000, €79.82 at €13,000.01; dead zone €90 (S1); timing: €30,000 over two years as 13,000 +
  17,000 instead of 15,000 + 15,000 saves €79.82 (S5).
- provisions: TCA s. 531AM(2).
- Lean: `usc_notch`, `usc_above_exempt`, `usc_floor_notch` (kernel `Contribution.floor_notch`).
- status: known (Revenue TDM 18D-00-01 para. 1).

### F11 Weekly PRSI floor rewards keeping a second earner at €352 a week (known)
- kind: loophole-known (K6)
- households: married couple, €60,000 of earnings: best split 30 % / 70 % (€18,000 to the second earner = €346 a
  week, no PRSI) rather than 50/50 (S2).
- provisions: SWCA s. 13(2)(a). Lean: `prsi_notch_352`; S2. status: known.

### F12 Investment income in the lower earner's name: €9,954 a year on €50,000 (known; recreated blind)
- kind: loophole-known (K2)
- households: married, one earner €100,000; €50,000 of dividends or rent held by the earner v by the spouse.
- amounts: income tax -€7,000 (band +€35,000 at 20 points); USC and Class S PRSI -€2,954; total €9,954 (S3). With
  €150,000 of investment income the best split is 40/60 (€12,456).
- provisions: TCA s. 15(3)-(4) ("specified income" = total income from any source except DIRT interest); TDM
  44-01-01 Example 5 (investment income raises the band); s. 1028(5) (no CGT between spouses); s. 531AM (USC
  individual).
- Lean: `Findings.lean` `f12a`/`f12b` (`#guard`: €7,000 and €9,954).
- status: known (Irish News 2019 "What's yours is mine"; Business Post "Tax tips for employees").

### F13 Marriage bonus €3,800 for one-earner couples; a second earner worth up to €12,956 (known)
- kind: loophole-known (K1, K4)
- amounts: €60,000 one earner: married €3,800 less tax than unmarried (band €53,000 v €44,000; credit €4,000 v
  €2,000 + a wasted €2,000). At equal earnings married = unmarried (S2). Splitting €150,000 50/50 saves €12,956
  (married) / €16,756 (unmarried) against one earner.
- provisions: TCA s. 15 Table Parts 1/3, s. 15(3), s. 461.
- Lean: `#guard (hhCalc f13u).it - (hhCalc f13m).it = eur 3800`; `joint_gross_le_single` (all incomes);
  `married_cap_two_singles`; S6: in 3,966 couples (ages 40 and 67) single treatment never beats joint.
- status: known.

### F14 Home carer credit v band increase (known)
- kind: loophole-known (K3). amounts: the one-earner OECD couple with children gets the €1,950 credit (matches the
  OECD's TC €7,950). provisions: TCA s. 466A(2), (6), (8). Lean: `jointIT` option B; `homeCarer_le_full`,
  `homeCarer_antitone`, `homeCarer_zero`. status: known.

### F15 Owner-manager: salary beats dividends by €4,744-€20,523; Class S saves the employer PRSI (known)
- kind: loophole-known (K7)
- households: single owner-manager, company profit €30,000-€250,000, all paid out.
- amounts: salary as a 50 %+ proprietary director (Class S, no employer PRSI, earned income credit) v dividend after
  12.5 % CT: +€4,744 (€30,000) to +€20,523 (€250,000); Class S rather than Class A employer PRSI: +€2,021 to
  +€11,053 (S4).
- provisions: TCA s. 21(1), s. 472(1), s. 472AB; SWCA s. 13(2)(d), s. 21(1)(c).
- Lean: `ieDirector` in `Household.lean`; S4. status: known; employer pension contributions (usually the best
  route) not modelled.

### F16 USC 70+ cliff at €60,000: €326.18 in 2025 (known)
- kind: loophole-known (K8)
- amounts: single, 71, occupational pension: USC €1,019.82 at €60,000; €1,346.00 at €60,000.01; dead zone €580 (S1).
  (Dáil PQ 1 Oct 2013: about €1,320 then; the 3 % band of 2025 makes it much smaller.)
- provisions: TCA s. 531AN(1), Table Part 2. Lean: `usc70_cliff` (theorem, `decide`). status: known.

### F17 Working family payment: €1,035 cliff where the €20 minimum stops; €52 saw-teeth from rounding (known)
- kind: loophole-known (K9)
- amounts: lone parent, 2 children: WFP €20 a week up to €49,090 of wages, nothing at €49,100: net falls €1,035;
  regained only at €51,060 (dead zone €1,970). 1 child: €41,580 / €43,010; one-earner couple, 2 children: €45,980 /
  €47,410. Below that, rounding the weekly rate up to €1 makes a €52 step every ~€87 of annual income. Over €1,000
  steps the METR peaks at 78 % (lone parent, €48,000).
- provisions: SWCA s. 228 (SWA 2024 s. 13), s. 229(1)-(2); the €20 prescribed amount (INOU, One Family guides).
- Lean: `#guard (hhCalc (lp 49090)).wfp = 52 * eur 20`, `#guard (hhCalc (lp 49100)).wfp = 0`.
- status: known (the €20 minimum is published); the dead-zone size is computed here.

### F18 WFP timing: bunching income into one of two years (known)
- kind: loophole-known (K9). amounts: lone parent, 2 children, €120,000 over two years: €15,250 + €104,750 instead of
  €60,000 + €60,000 gains €5,492 (S5); in law the award is fixed for 52 weeks on income at claim, so the real effect
  is larger. provisions: SWCA s. 229, s. 230. status: known.

### F19 Class S €650 minimum: a €650 notch at €5,000 of income (known)
- kind: loophole-known (K10). amounts: €4,999 of trading income: no PRSI; €5,000: €650 (13 %); dead zone €650; €650 is
  due on any income up to €15,758 (650 / 4.125 %). provisions: SWCA s. 21(1)(a); Sch. 1 Pt 3 (€5,000).
  Lean: `classS_notch` (theorem). status: known (a deliberate minimum giving a year's contributions).

### F20 Model fixes made while validating
- kind: model-fix
- (a) WFP €20 minimum added after the METR scan showed WFP fading to €1 a week (s. 229(2) "prescribed amount").
- (b) The owner-manager scan first charged Class A employer PRSI on a Class S director's salary; corrected.
- (c) The timing scan first let a lone parent claim WFP on €250 of earnings; years below €15,000 now excluded (WFP
  needs 38 hours' work a fortnight).

## Versioned-law checks with no fault found
- s. 531AN(3) medical-card amount moved with the end of the 2 % band every year 2020-2025 (FA 2020 s. 2: €20,484;
  FA 2022 s. 2: €22,920; FA 2024 s. 2: €27,382): `usc_medical_card_aligned`.
- Two-earner married band = 2 x single band, 2022-2025 (Revenue chart): `married_cap_two_singles`.
- SW(MP)A 2024 Table rows 6-7 update the quoted words in SWCA s. 13(8) together with s. 13(2)(d): no stale quotation.

## New loopholes
None claimed. Every household-level effect the scans found is described in the statute, Revenue guidance or the
secondary sources named above (web searches: 6 of 7 used). F9 (the growing PRSI notch) is a drafting finding, not a
planning opportunity.
