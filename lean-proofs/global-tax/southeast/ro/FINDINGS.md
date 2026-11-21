# RO Romania 2025: FINDINGS

Model: `~/cmp20/southeast/ro/lean` (RoTax, exe `rotax`). Lean statements: `lean/RoTax/Findings.lean` (F1-F10),
`lean/RoTax/Theorems.lean`. Statute: Codul fiscal (Legea 227/2015) read in Global law at the dates named; texts in
`law/`. Amounts in lei (RON). "Monthly" = the art. 78 final monthly wage tax (each month stands alone; no annual
reconciliation for wages).

Sources searched before calling anything new (7): Codul fiscal and HG 1/2016 norms (Global law); EUROMOD Country
Report Romania 2022-2025 (Y16, JRC); Eurostat earn_nt_net (EC-OECD model) 2023-2025; OUG 156/2024 and Legea
141/2025 texts; Newsweek Romania 6 Aug 2026 (ImpozitSalariu.ro figures); one web search (payroll worked examples
2025: curs-valutar-bnr.ro, folositor.ro, contzilla.ro, profit.ro snippets); danielgp/salariu (open code, 2018).

### F1 Forty points where one leu more gross pay lowers take-home pay (deducere personală steps)
- kind: loophole-new (METR > 100 %; not found in the 7 sources searched: EUROMOD and the EC model describe the taper as linear)
- households: any employee at the main job with gross monthly pay at minimum wage + 50 k -> + 50 k + 1 lei, k = 0..39 (4.050 -> 4.051, 4.100 -> 4.101, ..., 6.000 -> 6.001), 0 to 4+ dependants, under 26 or not
- amounts: -1 to -2 lei a month at each step (the deduction falls by 0,5 % of the minimum wage = 20,25 lei, costing ~2 lei of tax, while the leu adds 0,65 lei); inside a row the marginal rate is the ordinary 41,5 % (49 lei more give 28 lei more net, 4.101 -> 4.150)
- provisions: art. 77 alin. (3)-(4) (wording of OG 16/2022, in force 2023-01-01), art. 78 alin. (2) lit. a)
- Lean: `F1_step_metr_over_100` (all 40 x 5 x 2 cases, `decide`), `F1_inside_row`; scan `results/search/wage_metr.json` (`harness/scan_wage.py`, monthly gross 1-7.000, 20 household variants: exactly these points and the F2/F3 points, nothing else)
- status: proved

### F2 Cliff at 2.001 lei above the minimum wage for parents and under-26s
- kind: loophole-new (not found in the 7 sources searched)
- households: gross 6.050 -> 6.051 lei a month; 1, 2, 3, 4+ dependants: -19, -39, -60, -100 lei a month; under 26 without dependants -60; under 26 with 4+ dependants -161 lei a month (-1.932 a year) for one leu
- why: the table's last row is still 5 %-25 % with dependants (0 % only without) and the under-26 deduction (15 % of the minimum wage = 608 lei) is all-or-nothing at the same line (alin. (10) lit. a) refers to the level of alin. (3))
- provisions: art. 77 alin. (3), (4) last row, (10) lit. a)
- Lean: `F2_cliff`, `table_last_dependants`, `base_ded_zero_above` (for all inputs: nothing above the band)
- status: proved

### F3 The 300 lei of OUG 156/2024: notch at 4.300 lei and at any raise of a minimum base salary
- kind: loophole-known (the 2026 analogue at 200 lei is the subject of the Newsweek 6 Aug 2026 article; the 300 lei rule is widely reported)
- households: base salary 4.050 (minimum wage), gross 4.300 -> 4.301: -126 lei a month; raising the base salary from 4.050 to 4.051 lei: -125 lei a month; the base must reach 4.279 lei (+229) to leave the worker as well off. Incentive recreated blind: keep the contractual base at exactly the minimum wage and pay the rest as bonuses up to 4.300 lei (art. LXVI alin. (2) only bars cutting an existing base)
- provisions: OUG 156/2024 art. LXVI alin. (1)-(6) (outside the Codul fiscal); art. 77, 78, 146, 168
- Lean: `F3_notch_4300`, `F3_notch_base`, `F3_break_even`; `untaxed_le`, `untaxed_zero_above`, `untaxed_zero_off_minimum` (all inputs)
- status: proved

### F4 The dependent-spouse test is a cross-person notch
- kind: loophole-new (the statutory threshold is well known; the cross-person METR was not found in the 7 sources)
- household: married couple, one child, earner at the minimum wage; the spouse's own income 810 lei a month (20 % of the minimum wage: a dependant, art. 77 alin. (5)) vs 811 lei: +12 lei a year for the spouse cost the household 240 lei of tax (the earner's deduction falls from 30 % to 25 % of the minimum wage). The test counts all income, taxable and not
- provisions: art. 77 alin. (4), (5), (6)
- Lean: `F4_spouse_notch` (`native_decide`, through the full household function `out`)
- status: proved

### F5 CASS on investment and rental income: three notches and a cap
- kind: loophole-known (bands are statutory; described by EUROMOD for property/IP income)
- households: dividends (2025, 10 % withheld) 26.999 -> 27.000 lei: +2.430 lei CASS (24.300 net = 6 minimum wages); 54.000: +2.430; 108.000: +4.860; above 108.000 the CASS is 9.720 lei whatever the amount (marginal CASS 0, average falling: regressive). Interest, rents (80 %) and gains count in the same bands (art. 170 alin. (4))
- provisions: art. 155 alin. (1) lit. c)-h), art. 170 alin. (2)-(5), art. 156
- Lean: `F5_notches`, `F5_cap` (for every amount >= 108.000), `invCassBase_top`
- status: proved

### F6 Splitting investment income with a spouse or across years
- kind: loophole-known below the threshold (per-person bands); loophole-new above it: splitting doubles the cap (not found in the 7 sources)
- households: 53.998 lei of dividends in one hand: 2.430 CASS; 26.999 + 26.999 (two spouses, or two years): 0. But 400.000 lei in one hand: 9.720; split 200.000 + 200.000: 19.440. Owner-manager scan: sharing dividends with the spouse helps up to ~250.000 lei of profit and costs ~2,4 points of profit above ~400.000 (`results/search/owner_ro.json`)
- provisions: art. 170 alin. (2)-(4), art. 97 alin. (7)
- Lean: `F6_split`, `F6_split_high`
- status: proved

### F7 Timing: dividends paid in 2025 at 10 % rather than in 2026 at 16 %
- kind: loophole-known (widely reported in 2025; sanctioned by Legea 141/2025 art. VII alin. (2) for interim dividends)
- amounts: 6.000 lei per 100.000 lei of dividends (10.000 vs 16.000); 2024 -> 2025 was 8 % -> 10 %. Interim dividends distributed in 2025 keep 10 % "fără recalcularea impozitului" even after the 2025 annual accounts. CASS bands apply per year, so bringing several years of dividends into one year can also save CASS (F5 cap)
- provisions: art. 97 alin. (7) (OUG 156/2024; Legea 141/2025 art. II pct. 5), art. 43 alin. (2), Legea 141/2025 art. VII alin. (1) lit. a), c) and alin. (2)
- Lean: `F7_timing`; model option `"roDividendYear"`
- status: proved

### F8 Independent activities: the 12- and 24-minimum-wage CAS notches
- kind: loophole-known (statutory thresholds)
- households: PFA net income 48.599 -> 48.600 lei: CAS of 12.150 lei becomes due, take-home -10.934 lei; again at 97.200 (-10.934)
- provisions: art. 148 alin. (1)-(2), art. 118 alin. (2) lit. b)
- Lean: `F8_cas_notch`
- status: proved

### F9 Pensions: the law changed in August 2025 (modelled month by month)
- kind: model-fix (the year needs two laws)
- household: pension 5.000 lei a month: January-July 200 lei tax a month; August-December 200 lei CASS and 180 lei tax: 2025 totals CASS 1.000, tax 2.300 (a full year under either rule would be wrong)
- provisions: art. 100 alin. (1) and art. 157^6 (Legea 141/2025 art. II pct. 7, 25; art. VII alin. (1) lit. e), alin. (3): August 2025 - December 2027)
- Lean: `F9_pension_2025`; `pensionMonth`
- status: proved

### F10 Owner-manager: PFA in sistem real overtakes micro-enterprise + minimum salary + dividends
- kind: loophole-new (as a ranking; the caps themselves are known; not found in the 7 sources)
- households: one owner, profit P, revenue = P. Take-home as % of P (2025): P = 250.000: salary 57,2, SRL + CIT + dividends 71,7, micro + minimum salary + dividends 79,7, PFA 72,5; P = 600.000: 57,2 / 74,0 / 83,4 / 82,7; P = 1.000.000: 57,2 / 74,6 / 85,0 / 85,6. PFA >= micro from P ~ 760.000 lei (2025 dividends) and ~ 300.000 lei with the 2026 16 % dividend rate (and the micro ceiling falls to 100.000 EUR ~ 509.850 lei in 2026). Why: CAS on a PFA is capped at 24 and CASS at 60 minimum wages, so its marginal rate at the top is 10 %, against 3 % of revenue + 10 % (16 % in 2026) of dividends
- provisions: art. 47, 51, 53, 220^3; art. 68, 118 alin. (2), 148, 170 alin. (1); art. 97 alin. (7)
- Lean: `F10_crossover`, `microRoute`, `pfaNet`; scan `harness/owner_ro.py` -> `results/search/owner_ro.json`
- status: proved (ordering at 400.000 and 1.000.000)

### F11 Micro-enterprise schemes recreated blind (minimum salary + dividends; two micros between spouses)
- kind: loophole-known
- amounts: P = 250.000: micro route 79,7 % vs salary 57,2 % (+56.000 lei a year). Above the 250.000 EUR ceiling (1.243.525 lei at 4,9741), two micros each owned and staffed by one spouse: 84,2 % at P = 1.500.000 vs 75,0 % for one SRL paying CIT + dividends. The anti-split rules (art. 47 alin. (1) lit. h): one micro per >25 % holder; alin. (1^1), new in 2025: revenues of enterprises linked through the same holder are added) reach a second company held by the same person, not one held by the spouse, on their words; the spouse has to be the real owner and employee
- provisions: art. 47 alin. (1) lit. c), g), h), (1^1), (4); art. 51; art. 52 alin. (5^1), (7)
- Lean: `microRoute`; scan rows `two_micros_spouses`
- status: recreated (company side in Python; personal side through rotax)

### F12 Eurostat / EC tax-benefit model gives the 100-lei child deduction once per earning parent, not per child
- kind: gov-error (EC/Eurostat model; authority: art. 77 alin. (10) lit. b) "100 de lei lunar pentru fiecare copil")
- households: Eurostat earn_nt_net 2025: single parent 67 % AW with two children, and one-earner couple at 100 % AW with two children: income tax 120 lei a year too high (5.089,28 vs 4.968; 7.655,04 vs 7.536); two-earner couples get 200 lei a month (100 per parent), which hides the error there. Same pattern in the 2024 data
- evidence: `harness/eurostat_check.py`, `results/eurostat_check_2025.json`
- draft note (not sent): "Eurostat earn_nt_net, RO 2023-2025: the supplementary deduction of art. 77(10)(b) Codul fiscal is 100 lei a month for each child under 18 in education; the series applies it once per earning parent (P1_CH2_AW67 and CPL_CH2_AW100 income tax exceed the statute by 120 lei a year)."
- status: open

### F13 EUROMOD and the EC model describe/compute the deduction taper as linear; the statute has 50-lei steps
- kind: gov-error (convention; small)
- evidence: EUROMOD CR RO Y16 §2.5.3 "the personal deduction is decreasing linearly with income"; Eurostat 2025 single at 50 % AW (4.984 lei a month): tax 3.369,44 = a linear deduction of 431,7 lei; statute 10,5 % x 4.050 = 425 lei -> tax 3.384 lei a year (+14,56)
- status: open (the linear reading also hides F1)

### F14 EUROMOD Country Report 2025 does not describe the 300-lei minimum-wage facility
- kind: gov-error (omission in the referee's description; searched for "300", "200 RON", "non-taxable", "untaxed")
- effect: a full-time minimum-wage earner pays 125 lei a month less than the rules described (F3)
- status: open

### F15 Provisions annulled by the Constitutional Court stayed in the Code for 31 months
- kind: statute-fault (versioned law)
- evidence: CCR Decizia 650/2022 (15 Dec 2022, `law/ccr-650-2022.txt`) found unconstitutional the OUG 130/2021 points that inserted CASS on pensions above 4.000 lei: art. 153 alin. (1) lit. f^2), art. 154 alin. (1) lit. h) "de până la suma de 4.000 lei lunar inclusiv", art. 155 alin. (1) lit. a^1), art. 157^3. Global law (following the consolidated text) keeps them in force until Legea 141/2025 repealed f^2), h), a^1) and 157^3 from 1 Aug 2025 (art. II pct. 11, 16, 20, 23) and re-enacted the mechanism by law at 3.000 lei (art. 157^6). Under Constitution art. 147 alin. (1) annulled texts cease to apply 45 days after publication; the Code as read Jan-Jul 2025 says pensions over 4.000 lei owe CASS. The model applies no pension CASS before August 2025
- status: documented

### F16 The consolidated Code shows 16 % on dividends from 1 August 2025; it applies only from 1 January 2026
- kind: statute-fault (reading trap in the consolidated text; Global law shows the same, with its "commencement rules not held" caveat)
- evidence: art. 97 alin. (7) and art. 43 alin. (2) read on 2025-09-01: "16%"; Legea 141/2025 art. VII alin. (1) lit. a), c): applies to dividends "distribuite începând cu data de 1 ianuarie 2026"; alin. (2): 2025 interim dividends stay at 10 %
- status: documented (model uses 10 % for 2025)

### F17 A procedure order for a repealed exemption is still in force
- kind: statute-fault (minor, orphaned secondary law)
- evidence: Ordin MF 1528/2022 (procedure for the construction-sector exemption of art. 60 pct. 5) is in force in the record on 2025-09-01; art. 60 pct. 5 reads "Abrogat" from 1 Jan 2025 (OUG 156/2024)
- status: documented (record-level; no effect on tax)

### F18 The table's lei steps were not updated when the minimum wage rose: the implicit taper keeps steepening
- kind: statute-fault (amount not updated when a related amount changed)
- evidence: art. 77 alin. (4) fixes the band (2.000 lei) and the steps (50 lei) in lei but the deduction in % of the minimum wage; each step removes 0,5 % of the minimum wage: 15 lei per 50 lei in 2023 (minimum wage 3.000: an implicit 30 % taper) and 20,25 lei in 2025 (4.050: 40,5 %), so F1's losses and F2's cliff grow with every minimum-wage rise while the band covers a shrinking share of wages (up to minimum wage +67 % in 2023, +49 % in 2025)
- Lean: `table_eq_formula_lo`, `table_eq_formula_hi`, `euromod_2025_amounts`
- status: documented
