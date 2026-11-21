# Lithuania (LT) 2025: findings

Model: `lean/LtTax` (exe `lttax`), cents internally. Sources and their limits: `lean/LtTax/Params.lean` header (e-TAR,
e-seimas, vmi.lt and lrv.lt answer HTTP 403 / Cloudflare challenges to scripts; the statute text used is the archived
consolidated GPMĮ of 2023-01-01; 2025 amounts from EUROMOD, PwC 2025, Sodra, OECD, VMI). Numbers below are from
`results/studies.md`, `results/search/`, `results/owner_*/` and the Lean theorems named.

### F1 One euro more can cost a two-child family 1 730 € of child benefit (the additional benefit's income test is a notch)
- kind: loophole-new (notch; the planning is to keep net income per family member at or under 2 VRP).
- households: single parent with 2 children at 25 440 € of wages (0,893 AW); couple, one earner, 2 children at
  35 067 €; two equal earners with 2 children at 29 958 € in total; single parent with 1 child at 14 979 € (865 €);
  couple with 1 child at 25 440 € (865 €). METR at the notch above 3 000 % (`results/search/metr.md`).
- amounts: the additional benefit is 1,03 BSI = 72,10 € per child per month; it stops when net income per family
  member passes 2 VRP = 442 € a month; one euro more loses 1 730,40 € a year (2 children); the wage must rise by
  2 901-3 451 € to recover the net income (`studies.md` §4).
- provisions: Išmokų vaikams įstatymas (via EUROMOD §2.6.4: "monthly income per each family member can't exceed the
  threshold of 2 SSI"; "1.03 BSA, which equals to 72.1 EUR in 2025"); BSI 70 €, VRP 221 € (EUROMOD Table 1.2). The
  OECD's 2025 CTGG lines (4 670,40 € for SP67 and M100_0, 2 940 € for M100_67) agree with this test.
- Lean: `cb_notch_2025` (lose 173 040 cents at one cent above 12 × 2 × 221 € × 3).
- novelty: the test is described by EUROMOD; the size and location of the notch for each family type and the METR were
  not found in 7 sources searched (EUROMOD CR, PwC 2025/2026, KPMG 08/2025, VMI RM-5567, two search result sets).
- status: confirmed in the model; the test's income definition (net, all members, monthly) follows EUROMOD's summary,
  not the act's text (unreachable).

### F2 Dividends, rent, interest and individual-activity income withdraw the NPD on wages: dividends cost 24,8 %, not 15 %
- kind: loophole-new (hidden marginal rate; the owner-manager's "minimum salary + dividends" loses the NPD).
- households: any employee whose GMP is between 12 456 € and 34 370,67 €.
- amounts: 1 000 € of dividends, rent or taxable interest on top of 12 456-25 000 € of wages raises GPM by 248 € (15 %
  + 0,49 × 20 % = 24,8 %), at 30 000 € by 186 € (15 % + 0,18 × 20 %); 1 000 € of individual-activity income adds
  148 € GPM (5 % + 9,8 %) and 323 € with contributions (`studies.md` §5). A worker on the MMA (12 456 €) with
  20 000 € of dividends is withheld 698 € on wages but owes 2 422 € at the annual return: a bill of 1 724 € on top of
  the 3 000 € withheld on the dividends (23,6 % on the dividends in all).
- provisions: GPMĮ 20 str. 7 d. ("GMP yra lygios gyventojo mokestinio laikotarpio apmokestinamųjų pajamų ... sumai",
  excluding only 5 %-rate, business-certificate and some insurance income) with 20 str. 1 d. ("NPD ... taikomas tik su
  darbo santykiais ... susijusioms pajamoms"); 6 str. 1 d. (15 %).
- Lean: `other_income_withdraws_npd` (2000 × 49 ticks per 100 cents of other income in band 1), `mnpd2025_band1`.
- novelty: the mechanism is in the statute; a land-rent guide (finonamai.lt) mentions a year-end top-up for salary +
  rent; the 24,8 % dividend rate and the owner-manager consequence were not found in 7 sources searched.
- status: confirmed (statute text 2023; 2025 amounts).

### F3 Bunching income in alternate years beats smoothing: the NPD makes GPM concave between 12 456 € and 126 533 €
- kind: loophole-new (timing).
- households: single employee, two years at 2025 rules: 30 000 + 30 000 € pays 1 478,11 € more GPM than
  12 000 + 48 000 €; for 80 000-120 000 € over two years the best split (x / 12 000 €) saves 1 793 € (`studies.md` §3);
  the kernel timing scanner finds up to 1 796 € (6,3 % AW) for a single and 3 526 € (12,4 % AW) for a single parent
  with 2 children (with F1).
- provisions: GPMĮ 20 str. 1 d. (annual NPD by GMP), 6 str. 1¹ d. (20 % to 60 VDU). The marginal GPM rate falls from
  29,8 % (band 1) to 23,6 % (band 2) to 20 % (to 126 532,80 €), so the function is concave there.
- Lean: `bunching_2025`; `band1_2025` (2000 × 149), `band2_2025` (2000 × 118); `emp2025_convex` holds for the rate
  schedule alone, not after the NPD.
- who can use it: anyone who can move pay between years (bonuses, owner-managers' salaries, fixed-term contracts).
- novelty: not found in 7 sources searched.
- status: confirmed.

### F4 The individual-activity credit is withdrawn so fast that the marginal GPM rate reaches 38,3 % just below 35 000 €
- kind: loophole-new (planning: keep each person's individual-activity income at or under 20 000 € and split activity
  between spouses).
- amounts: effective GPM 5 % up to 20 000 €, 15 % from 35 000 €; marginal 5 % below 20 000 €, then rising from 11,7 %
  to 38,3 % (`ia_marginal_top`: 38,27 € on the last 100 €); with contributions on 90 % of profit (17,55 %) the combined
  marginal rate is 55,8 % at 34 900 € (the highest in the system).
- provisions: GPMĮ 18² str. 2-4 d. ("× (0,1 – 2/300 000 × (... – 20 000))", "laikoma, kad jis lygus 0"); Sodra 90 % base.
- Lean: `ia_5pct`, `ia_15pct`, `ia_marginal_top`, `ia_credit_continuous`.
- novelty: PwC states the 5-15 % effective range; the 38 % marginal rate was not found in 7 sources searched.
- status: confirmed (2025; the regime changes in 2026).

### F5 The 32 % rate starts exactly where the 12,52 % VSD stops: the top band's combined rate (38,98 %) is lower than the band below (39,50 %), and the highest combined rate on wages (49,3 %) is paid between 12 456 € and 28 647 €
- kind: loophole-new (design: for the high earner the rate step is invisible).
- households: single employees; the METR scan's peak (single, no children) 50,9 % at 0,448 AW is the 49,3 % band-1
  rate plus whole-euro output rounding.
- provisions: GPMĮ 6 str. 1¹ d. (60 VDU); Sodra/EUROMOD §2.7.1 (60 AMS ceiling for VSD only).
- Lean: `edge_below` (3950 bp), `edge_above` (3898 bp), `edge_falls`, `band1_2025`.
- novelty: the rates are public; that the ceiling cancels the top rate was not found stated in 7 sources searched.
- status: confirmed.

### F6 Owner-manager: all dividends beats any salary from 1 AW of profit; the classic minimum salary is beaten by F2
- kind: loophole-known (K2, K3) with a new detail.
- amounts (`results/owner_standard/`, CIT 16 %): total tax 28,6 % all dividends vs 40,6 % all salary at 2-10 AW of
  profit (gain 6 806 € at 2 AW); at 1 AW the best salary is only 2 797 € (sheltered by the NPD that the dividends
  leave); small company (6 %, `results/owner_small/`): 20,1 % all dividends at every level (gain 11 645 € at 2 AW).
- provisions: GPMĮ 6 str. 1 d., 20 str. 7 d.; CIT 16 % / 6 % (PwC 2025); employer 1,77 % (Sodra).
- Lean: via `lttax`; `other_income_withdraws_npd`.
- status: confirmed; the small-company rate needs revenue < 300 000 € (not checked by the scan).

### F7 The 2025 → 2026 reform window
- kind: loophole-new (timing across a versioned law).
- amounts (`studies.md` §2): an employee at 3-4 AW who takes a 20 000 € payment in December 2025 rather than January
  2026 saves 1 000 € GPM (the 25 % band between 36 and 60 VDU, 83 237-138 729 € in 2026); at 1 AW the gain is 135-167 €
  (the 2026 NPD differs); none between 1,25 and 2 AW. Individual-activity income above 42 500 € moves from at most 15 %
  (2025) to the 20-32 % scale (PwC 2026): not modelled, likely the largest window for the self-employed.
- provisions: 2026 GPMĮ (XV-343/XV-352, via PwC 2026 and KPMG); the 2026 NPD is one formula (`mnpd2026_single`) and
  reaches 0 at 32 129,88 € instead of 34 370,67 € (`mnpd2026_zero`, `mnpd2025_zero`).
- Lean: `reform_rate_90k`, `mnpd2026_single`, `mnpd2026_zero`.
- status: confirmed for employees; individual activity open.

### F8 Monthly withholding vs the annual return: who gets a refund, who gets a bill
- kind: model finding (statute design).
- amounts (`studies.md` §1): equal pay settles to 0; part-year work (6 months × 2 000 €) is refunded 1 462 €; a
  6 000 € December bonus on 1 500 € a month gives a bill of 484 €, a 10 000 € bonus on 2 000 € a month 593 €; seasonal
  pay (4 × 3 000 + 8 × 1 000 €) 142 €; any non-wage income gives a bill (F2).
- provisions: GPMĮ 20 str. 1-2 d. (annual vs monthly NPD), 20 str. 4 d. (NPD at one workplace), 20 str. 8 d.
- Lean: `npdMonth`, `mnpd` (and `vmi_rm5567` for the monthly rule).
- status: confirmed.

### F9 EUROMOD's Table 2.16 gives the 2022 NPD coefficient as 0,26; the text and the OECD say 0,34
- kind: gov-error (official referee publication: a JRC external study, not the Lithuanian government).
- evidence: EUROMOD CR LT 2022-2025 §2.8.1 text "540 – 0.34 × (monthly employment income – 730)"; Table 2.16 "0.26".
  OECD 2022 S67 NPD 4 630,04 € = 6 480 – 0,34 × (14 201,05 – 8 760); 0,26 would give 5 065 € (`oecd_2022_S67_npd`).
- status: confirmed. Draft note to the EUROMOD team: "Table 2.16 (and 2.17), 2022 column: coefficient 0.26 should be
  0.34 as in the text of §2.8.1 (the OECD Taxing Wages 2022 figures confirm 0.34)."

### F10 EUROMOD says the 2025 NPD "is not paid for incomes equal or higher than the 2387.29 EUR threshold"
- kind: gov-error (same publication). §2.2.3 and the executive summary say so; §2.8.1 says the NPD reaches 0 at
  2 864,22 € a month, and the second formula (400 – 0,18 × (P – 642)) applies above 2 387,29 €. The OECD 2025 lines
  agree with §2.8.1. Lean: `mnpd2025_band2`, `mnpd2025_zero`.
- status: confirmed (internal contradiction; the model follows the formula).

### F11 EUROMOD: the 2025 NPD for 0-25 % work capacity is 1 127 € in the text and 1 124 € in Table 2.16
- kind: gov-error (same publication); which is right is unresolved (the 2025 statute text was not reachable). Not used
  by the model (disability NPD unsupported).

### F12 Sodra's 2025 rate table: "Motinystės – 1,1" for fixed-term contracts in budget institutions
- kind: gov-error (typo on sodra.lt; archived 2026-10-09, `refs/sodra_samdomi_wb.txt`, "Įmokų tarifų lentelės 2025
  metams", "Asmenys, dirbantys pagal darbo sutartį Lietuvos banke, biudžetinėse įstaigose", "Terminuota").
- evidence: the same row's employee total is "19,5"; 8,72 + 1,99 + 1,1 + 6,98 = 18,79; every other row reads
  "Motinystės – 1,81" (8,72 + 1,99 + 1,81 + 6,98 = 19,5). Draft issue text: "In the 2025 table for fixed-term contracts
  in budget institutions the maternity rate reads 1,1 %; it should read 1,81 % (the row total 19,5 % and all other rows)."
- status: confirmed.

### F13 OECD 2022: the additional child benefit for the whole year where the income test fails in January-May
- kind: classification: convention (unresolved). SP67 and M100_0 have net income per member of 264 € / 277 € a month,
  above 2 VRP = 258 € before June 2022 (VRP 129 €) and below 294 € after (VRP 147 €). The OECD gives the benefit for 12
  months (2 957,92 €), the model for 7 (2 525 €): −432,92 € on 2 of 32 lines of 2022. The OECD may apply the June
  parameters to the whole year (as the 2022 NPD rules of June applied to the whole year).
- status: open.

### F14 The NPD switch thresholds are fixed euro amounts tied to a MMA set elsewhere
- kind: statute-fault (latent; classification: fragility, not an error in 2022-2025).
- evidence: 20 str. 1-2 d. take the MMA "galiojusios einamųjų kalendorinių metų sausio 1 dieną" (set by Government
  resolution) but write the switch amounts into the law (2023 text "1 926 eurų", "23 112 eurų per metus"; 2025
  2 387,29 €). The two formulas meet exactly at the switch only if both are updated together; they were in every year
  2022-2025 (`switch_2024_meets`, `switch_2025_meets`, `mnpd2023_max`, `mnpd2025_max`: the statute equals the larger
  of the two tapers for every income). A VMI answer (RM-5567, 2024) calls the 2024 switch "2 167 eurų" the
  "projektuojamo vidutinio darbo užmokesčio suma". Had the MMA changed without the law, the NPD would jump at the
  switch. The 2026 law removes the second formula (`mnpd2026_single`), and the fragility with it.
- status: confirmed (as a property proved for 2022-2025).

### F15 21 str. 3 d.: the 25 % cap's base literally includes income taxed at 6 str. 1 d. (15 %), dividends included
- kind: statute-fault? classification: reading. EUROMOD: "No deductions can be made to the income from distributed
  profit (dividends)"; 21 str. 3 d. takes "25 procentų apmokestinamųjų pajamų, kurioms taikomi šio Įstatymo 6
  straipsnio 1, 1¹ ir 1² dalyse nustatyti pajamų mokesčio tarifai". The model excludes dividends from the 25 % base and
  deducts the expenses from wages only. Matters only with large dividends and small wages (cap 1 500 €).
- status: open (reading).

### F16 The 32 % rate's first version was applied unconstitutionally (versioned law)
- kind: statute-fault (historical, known). TAR note under 6 str. 1¹ d.: "Nuostata, kad ... 6 straipsnio 1¹ dalis
  (2019 m. gruodžio 12 d. redakcija) įsigaliojo 2020 m. sausio 1 d., prieštarauja Lietuvos Respublikos Konstitucijos 5
  straipsnio 2 daliai, 70 straipsnio 1 daliai ..."; the current text applies "apskaičiuojant ir deklaruojant 2022 metų
  ir vėlesnių mokestinių laikotarpių pajamas". Recorded for the versioned-law record; no 2025 effect.

### F17 PwC 2025 says individual-activity contributions are paid on "90% individual activity income overall (not profit)"
- kind: reading (secondary source vs Sodra). Sodra: "VSD – 90 % nuo apmokestinamųjų pajamų" (taxable income, after
  deductible expenses). The model follows Sodra.

### F18 OECD lines off by 1 € (CGTC)
- kind: model-fix (convention). The harness enters whole euros (AW 28 474 for 28 473,62) and the model rounds each
  person's taxable income to the euro: CGTC +1 € on M100_100 (2025) and on 3 lines in 2024. Everything else exact.
