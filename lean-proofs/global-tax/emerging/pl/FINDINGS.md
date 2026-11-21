# Poland (PL) 2025: findings

Model: `lean/PlTax` (Lean 4.35 + TaxKernel), exe `pltax`. Amounts in PLN (zł). "Net" = gross − income tax − employee
contributions (social + health + Fundusz Pracy) + 800+ and Dobry start. Every Lean name below builds with no `sorry`
and no `native_decide` (`#print axioms`: propext, Quot.sound only). Statute: PIT = ustawa o podatku dochodowym od osób
fizycznych, t.j. Dz.U. 2025 poz. 163 (https://api.sejm.gov.pl/eli/acts/DU/2025/163/text.pdf; Global law
`poland/national/acts/ustawa/1991/350/`); Zdrowotna = t.j. Dz.U. 2025 poz. 1461; Ryczałt act = t.j. Dz.U. 2025 poz. 843;
SUS = t.j. Dz.U. 2025 poz. 350. Scans: `runs/scan.py` → `runs/scan_results.json`; generic kernel scanners →
`results/search/`.

Sources searched for "is it known" (N = 4): podatki.gov.pl relief pages (ulga na dziecko, dla młodych, 4+, IKZE;
fetched 2026-11-19), J. Florek & D. Czerwińska-Kayzer, "Profitability of Self-Employment in Poland after the
Introduction of the Polish Deal Regulations", European Research Studies Journal XXVIII(3) 2025 pp. 316-333
(`refs/ersj.txt`), and two web searches (OECD Taxing Wages note on the subkonto; OECD/EU/literature on B2B and the flat
regimes).

### F1 OECD leaves the 3,65 % subkonto share out of employee contributions
- kind: gov-error (checked) — classification: **convention**, not an error
- households: all eight OECD Taxing Wages types (AW = 105 738 zł)
- amounts: S100 statutory employee contributions 14 496,61 + health 8 211,68 = 22 708,29 zł; OECD EECSSC 18 848,62 zł.
  The difference 3 859,67 zł = 3,65 % of gross (EECSSC_PGE 10 636,94 = 13,71 % − 3,65 %; EECSSC_PTI 8 211,68 = the 9 %
  health contribution on gross less the full 13,71 %).
- provisions: SUS art. 22 ust. 3 pkt 2 ("7,3 % podstawy wymiaru składki jest ewidencjonowana ... na subkoncie"; half
  paid by the employee, art. 16 ust. 1); Zdrowotna art. 79 ust. 1, art. 81 ust. 1.
- authority: the OECD excludes inheritable ZUS sub-account contributions as private-like savings (summary of Taxing
  Wages 2026 at https://xyz.pl/?p=196917; the country note itself was not reached within the search budget). The 9 %
  health contribution IS in EECSSC (booked as "payable on taxable income", EECSSC_PTI) and is NOT subtracted from the
  income tax: correct since the Polski Ład (Dz.U. 2021 poz. 2105) ended its 7,75 % deduction. So health is wholly in
  EECSSC; the gap against 13,71 % + 9 % of gross is the subkonto (3 860 zł) plus the health base (9 % of gross less
  contributions, not of gross).
- model: `employeeSocial` keeps the statutory amount (the contract counts compulsory contributions); `oecd_map.py`
  subtracts `subkontoEmployeeHalf_OECDexcluded` for EECSSC. With that, 48/48 compared lines agree within 1 zł; the
  THP line of the check script differs by exactly the subkonto (−2 587 to −7 719 zł).
- status: explained.

### F2 OECD does not round to whole złoty
- kind: gov-error (checked) — classification: **convention**
- households: S167, M100_100, M100_67(nc): differences of 1 zł on CGTC/EECSSC
- provisions: Ordynacja podatkowa art. 63 § 1 ("końcówki kwot wynoszące mniej niż 50 groszy pomija się, a końcówki kwot
  wynoszące 50 i więcej groszy podwyższa się do pełnych złotych"), applied by the model to the base and the tax; the
  OECD works to the grosz on a gross of 105 737,51 zł.
- Lean: `PlTax.zl`, `zl_mono`. status: explained, immaterial.

### F3 The one-child relief limit is a notch with a 1 632 zł band of METR > 100 %
- kind: loophole-new (the limit is published; the >100 % band and its width not found in 4 sources searched)
- households: single parent with one child aged 5 (art. 6 ust. 4c), or a married one-earner couple with one child
- amounts: salary 133 271 → 133 272 zł moves the art. 27f ust. 2a income from 111 999,54 to 112 000,41 zł: the whole
  relief (1 112,04 zł) goes; net income falls 1 112 zł and recovers only at 134 903 zł (band 1 632 zł). For an unmarried
  parent who is not a single parent (limit 56 000 zł) the notch is at 68 375 zł. An IKZE payment does NOT help
  (ust. 2a counts income before it); moving pay across 31 December does.
- provisions: PIT art. 27f ust. 2 pkt 1 ("nie przekroczyły w roku podatkowym kwoty 112 000 zł" / "56 000 zł"), ust. 2a.
- Lean: `PlTax.oneChild_notch`, `oneChildCouple_notch`, `oneChild_band` (Findings.lean).
- status: confirmed by the model, the statute and podatki.gov.pl ("Obowiązuje Was wspólny limit 112 000 zł").

### F4 Ryczałt health-contribution bands are notches (60 000 / 300 000 zł of revenue after ZUS)
- kind: loophole-known (bands published by ZUS) with a new quantification of the >100 % bands
- households: sole trader on ryczałt 12 %, standard ZUS
- amounts: revenue 79 757 → 79 758 zł (revenue less social contributions crosses 60 000 zł): health +3 694 zł a year,
  net −3 472 zł after the 50 % deduction; net income recovers at 83 703 zł (band 3 946 zł). At 319 758 zł: health
  +7 386 zł, net −6 942 zł, band 7 889 zł. The thresholds are on revenue less social contributions (art. 81 ust. 2g),
  so a trader on standard ZUS meets them at about 79 758 / 319 758 zł of revenue, not 60 000 / 300 000.
- provisions: Zdrowotna art. 81 ust. 2e, 2f, 2g; Ryczałt act art. 11 ust. 1a; GUS M.P. 2025 poz. 84 (8 549,18 zł).
- Lean: `PlTax.rycz60_notch`, `rycz60_health`, `rycz300_notch`, `ryczalt_bands`.
- status: confirmed. Advice: defer December invoices when revenue is just above a band.

### F5 A flat-rate business of one spouse removes joint filing for both
- kind: loophole-known (art. 6 ust. 8 is explicit) — cost quantified
- households: married; A salary 300 000 zł; B sole trader 40 000 zł
- amounts: B on the scale: joint filing, net 220 483 zł. B on liniowy: separate, net 196 034 zł (−24 449 zł). B on
  ryczałt: 195 013 zł.
- provisions: PIT art. 6 ust. 8 pkt 1 ("nie ma zastosowania, w przypadku gdy chociażby jeden z małżonków ... stosuje
  przepisy art. 30c lub ustawy o zryczałtowanym podatku"), art. 6 ust. 2.
- Lean: `PlTax.flatSpouse_cost`. status: confirmed.

### F6 Joint filing: up to 27 600 zł, reached with a non-earning spouse from 240 000 zł of base
- kind: loophole-known (statutory option)
- households: one earner; gain 3 600 zł at a salary of 100 000 zł, 13 516 at 200 000, 27 600 from about 280 000 zł
- provisions: PIT art. 6 ust. 2, 3; art. 27 ust. 1
- Lean: `PlTax.joint_le_separate` (all bases), `joint_gain_le` (≤ 27 600 zł), `joint_gain_max` (= 27 600 zł when one
  base is 0 and the other ≥ 240 000 zł), `joint_no_gain_same_band`, `joint_gain_300k`; kernel `KernelLink.split_ok`.
- status: proved for all inputs.

### F7 B2B self-employment instead of employment
- kind: loophole-known (ERSJ 2025; IBS Policy Paper 01/2014; PIT art. 5b is the statutory test against it)
- households: one person, the same amount as salary or as invoiced revenue, no costs
- amounts (net, zł): 200 000: employee 130 382, B2B skala 133 040, liniowy 137 664, ryczałt 12 % 148 404 (+18 022);
  500 000: employee 299 047, ryczałt 12 % 405 461 (+106 414). Below about 150 000 zł B2B loses (fixed ZUS and FP
  21 287 zł a year). Employer contributions, which make the saving larger for the employer, are outside the contract.
- provisions: PIT art. 5b, 9a, 30c; Ryczałt act art. 12 ust. 1 pkt 2b; Zdrowotna art. 79, 79a, 81.
- Lean: `PlTax.b2b_200k`. status: recreated.

### F8 Under-26: the employer withholds up to 2 641 zł more than the annual tax
- kind: gov-error (checked: withholding vs statute) — classification: **design of art. 32**, refunded in the return
- households: employee aged 24, salary 89 000–148 000 zł
- amounts: at 125 000 zł the advances are 2 768 zł, the annual tax 127 zł. The exemption takes the first 85 528 zł of
  the year; the PIT-2 reduction (300 zł a month) is lost in the exempt months, while the annual return gives the full
  3 600 zł against the taxable remainder. For other single employees advances and annual tax differ by at most 7 zł
  (rounding of twelve advances; 1 581 salaries from 5 000 to 400 000 zł).
- provisions: PIT art. 32 ust. 2-4 and the 1/12 kwota zmniejszająca rule; art. 21 ust. 1 pkt 148; Ordynacja art. 63.
- Lean: `PlTax.young_overwithheld`, `young_120k_no_tax`; `Withholding.lean`.
- status: confirmed in the model; an interest-free loan to the state of about 2 % of pay for young middle earners.

### F9 The child-relief payout refunds contributions: METR 0 at low pay
- kind: loophole-new (follows from art. 27f ust. 9; the zero-METR band not described in 4 sources searched)
- households: single parent, 1 child: wages 0-5 100 zł; 3 children: 0-19 600 zł; married, 4 children: 0-32 200 zł
- amounts: single parent of three on 19 000 zł: income tax −4 080 zł = −(contributions 4 080 zł): every złoty of
  contributions comes back until contributions reach the relief (4 224,12 zł).
- provisions: PIT art. 27f ust. 8, 9 pkt 1-2 (the cap includes the health contribution, which is otherwise no longer
  deductible).
- Lean: `PlTax.relief_refunds_contributions`, `relief_refund_le_cap`, `relief_full`.
- status: confirmed.

### F10 Ryczałt income is outside the one-child income test
- kind: loophole-new (statutory gap; not found in 4 sources searched)
- households: married, one child; A ryczałt revenue 300 000 zł, B salary 60 000 zł
- amounts: on ryczałt the couple keeps the 1 112,04 zł relief (counted income = B only); the same A on liniowy loses
  it. The test counts income taxed under art. 27, 30b (even share gains) and 30c, but not ryczałt revenue, so high
  earners on ryczałt keep a relief meant for incomes up to 112 000 zł.
- provisions: PIT art. 27f ust. 2a ("dochody ... do których mają zastosowanie zasady opodatkowania określone w art. 27,
  art. 30b i art. 30c").
- Lean: `PlTax.ryczalt_keeps_relief`. status: confirmed; small amount, but a list not updated when the ryczałt was
  opened to most professions (2021-2022).

### F11 85 528 zł in the zero-PIT exemptions is the old bracket threshold, kept on purpose
- kind: statute-fault (checked) — classification: **deliberate, not an error**; unindexed amount
- evidence: Global law phrase_history "85 528": the number was the first-bracket threshold of art. 27 ust. 1 until
  2021 (in the record from 2010-03-12); pkt 148 (Dz.U. 2019 poz. 1394, in force 2019-08-01) set the youth limit equal
  to it. The Polski Ład (Dz.U. 2021 poz. 2105, `refs/DU_2021_2105.txt` lines 277-393 and 1401) added pkt 152-154 and
  art. 21 ust. 44 with 85 528 zł in the same act that moved the threshold to 120 000 zł, so the figure was not
  overlooked. Not indexed since 2019; 85 528 zł is now 0,81 AW.
- Lean: `zeroPitLimit`; `young_120k_no_tax` (stacked with the 30 000 zł kwota wolna a young earner pays no PIT up to a
  salary of about 120 000 zł).
- record note: the Global law record of the PIT act holds consolidated texts only after 2010; the 2022 changes appear on
  2022-12-15 (t.j. Dz.U. 2022 poz. 2647), not on their in-force dates (2022-01-01, 2022-07-01).

### F12 The one-child limits 112 000 / 56 000 zł have not changed since 2013
- kind: statute-fault (amount not updated when the related amounts changed)
- evidence: Global law phrase_history "112 000 zł": added by Dz.U. 2012 poz. 1278 (in force 2013-01-01), unchanged
  since; meanwhile the kwota wolna went from 3 091 to 30 000 zł and the threshold from 85 528 to 120 000 zł (2022).
  112 000 zł is 1,06 OECD AW in 2025, so the F3 notch now bites a one-earner family at 1,26 AW of salary.
- Lean: `oneChild_notch`. status: draft for the Ministry in USEFUL.md: index or taper the limit.

### F13 Government figures for 2025 re-derived: all correct
- kind: gov-error (checked) — no error found
- checks: liniowy health cap 12 900 zł = 11 600 × 260 190 / 234 720 rounded up to 100 zł (art. 30c ust. 2b; M.P. 2023
  poz. 1456, M.P. 2024 poz. 1051, M.P. 2023 poz. 1342, M.P. 2024 poz. 1084); IKZE 10 407,60 / 15 611,40 = 1,2 / 1,8 ×
  8 673 zł (M.P. 2024 poz. 1055); ceiling 260 190 = 30 × 8 673; health minimum 314,96 = 9 % × 75 % × 4 666; ryczałt
  bands 461,66 / 769,43 / 1 384,97 from 8 549,18 zł; podatki.gov.pl three-children example 4 224,12 zł.
- Lean: `liniowy_cap_formula`, `ikze_limits`, `ceiling_formula`, `health_minimum`, `ryczalt_bands`,
  `relief_three_children`.

### F14 Regime choice for a sole trader: scale below about 150 000 zł, ryczałt or liniowy above
- kind: loophole-known (ERSJ 2025; PIT art. 9a, 30c; Ryczałt act art. 12)
- amounts (no costs, standard ZUS; tax + contributions): skala cheapest to 145 000 zł; ryczałt 12 % from 150 000 zł
  (8,5 %: 125 000; 15 %: 165 000); skala vs liniowy only: liniowy from 175 000 zł. At 500 000 zł: skala 189 960,
  liniowy 133 248, ryczałt 12 % 94 539 zł. Top METR on the scale is 41 % (32 % + non-deductible 9 % health), on
  liniowy 23 % (19 % + 4,9 % less its deduction), on ryczałt 12 % between the health bands.
- Lean: `liniowy_health_ded_le`; scans `runs/scan_results.json` (regime). status: recreated.

### F15 Rental income split between spouses
- kind: loophole-known (Ryczałt act art. 12 ust. 1 pkt 4, ust. 6 default split)
- amounts: 200 000 zł of rent: split 17 000 zł, one spouse 21 000 zł (+4 000 zł); 400 000: 42 000 vs 46 000 zł.
- status: recreated (`plRentalOnePerson`).

### F16 Timing across the 30× contribution ceiling: bunching pay into one year saves up to 7 020 zł
- kind: loophole-new (the ceiling is well known; the two-year bunching gain not found in 4 sources searched) — found
  blind by the kernel timing scanner (`results/search/timing.md`), confirmed in Lean
- households: single employee; two years at 260 114 zł vs 365 852 + 154 377 zł; also second earners (5 371 zł) and
  single parents / one-earner couples (1 688 zł)
- amounts: +7 020 zł (6,6 % of AW) over the two years. Above 260 190 zł emerytalne (9,76 %) and rentowe (1,5 %) stop
  for the rest of the year; that saving outweighs the extra pay taxed at 32 % instead of 12 % and the slightly larger
  health base (health has no ceiling). An employer who pays a
  bonus in the year when pay already passes the ceiling, or a contractor who invoices two years of work in one, gains.
- provisions: SUS art. 19 ust. 1 ("nie może być wyższa od kwoty odpowiadającej trzydziestokrotności prognozowanego
  przeciętnego wynagrodzenia"); M.P. 2024 poz. 1051; Zdrowotna art. 81 (no ceiling on health).
- Lean: `PlTax.ceiling_bunching`, `emp_social_above_ceiling`. status: confirmed. The generic METR scanner also finds the
  49,1-49,8 % band from 142 534 to 260 326 zł above the statutory top rate at 10 AW (42,3 %): employee contributions
  stop at the ceiling, so the combined rate falls above it (a regressive ceiling, known).
