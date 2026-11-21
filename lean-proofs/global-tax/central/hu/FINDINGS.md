# Hungary 2025: findings

Model: `lean/HuTax` (exe `hutax`). AW = 8 455 487 HUF (OECD Taxing Wages 2025 average wage). Statute copies:
`refs/jogtar/` (net.jogtar.hu versioned texts; njt.hu refused connections from both hosts on 2026-11-19); NAV booklets
`refs/nav/`; NAV calculator source `refs/navcalc/`. Every amount below is proved on the named household in
`lean/HuTax/Findings.lean` or `Tests.lean` (`decide`, no `sorry`) unless marked as a scan result
(`tools/scan_hu.py`, `results/own/`).

### F1 OECD Taxing Wages 2025: 56 of 56 lines exact; the OECD sums six old and six new months of family allowance
- kind: model-fix (referee convention, confirmed). households: the eight TW types at 1 AW = 8 455 487.
- amounts: every line within 1 HUF (`results/oecd_check.md`, `results/oecd_check_HU.md`); the only 1-HUF differences
  come from the OECD's unrounded wages (14 120 663.81) vs the harness's whole forints.
- reading: Szja tv. § 29/A (2) was raised from 2025-07-01 (2024. évi LV. tv. 4. § (1): 66 670 / 133 330 / 220 000 ->
  100 000 / 200 000 / 330 000 per beneficiary per month). The OECD's DCTA for two children, 3 999 960, is
  2 x (6 x 133 330 + 6 x 200 000): month by month, as NAV 73 § 9.4 does. No transitional provision is needed (the
  amount is "jogosultsági hónaponként"); none exists in the Szja tv. (checked §§ 108-109 and the 2024. évi LV. tv.
  references).
- Lean: `Tests.oecd_m100_0`, `famFrame`, `famMonth2025`. status: explained.

### F2 Szja tv. § 29/B (6) says "divided by the tax rate (667 %)": 1/15 % is 666.67 %, and the rounding is against the taxpayer
- kind: statute-fault (amount stated inconsistently within one sentence). households: every family that took the
  family contribution allowance (családi járulékkedvezmény) during the year.
- provision: § 29/B (6): the annual family allowance is reduced by the contribution allowance taken during the year
  "az adó mértékére vonatkozó rendelkezés szerinti mértékkel elosztott része (667 százaléka)". Same words in every
  version fetched (2024.I.1, 2025.I.1, 2025.VII.1, 2026.X.1).
- amounts: 0.15 x 6.67 = 1.0005, so each forint of contribution allowance costs 1.0005 forint of tax
  (`Theorems.grossUp_excess`). NAV 73's own Kedves example: 185 000 taken -> frame 7 016 050 (667 %) instead of
  7 016 667 (exact): 617 HUF of frame, 93 HUF of tax (`Theorems.kedves_667_cost`). Small per family; it applies to
  every family whose allowance exceeds the tax base during the year.
- government material follows the parenthesis: NAV 73 § 13 ("667 százalékával"), and the NAV calculator
  (`refs/navcalc/csaladiKedvezmenyCalcV3_2026-09-01.js`, Step4) multiplies the in-year allowance by 6.67 but divides
  the allowance claimed in the return by 0.15 (two conventions for one quantity in one formula).
- draft fix: "... elosztott része" without the parenthesis, or "(666,67 százaléka)". status: confirmed (text).

### F3 NAV 73's worked example lets Orsi claim 2 000 000 of family allowance against a 1 800 000 base
- kind: gov-error (worked example inconsistent with the statute). households: NAV information booklet 73 (2025-09-16),
  § 13, the Kedves family: Orsi earns 2 400 000, of which 600 000 (October-December) qualifies for the three-children
  mothers' allowance; the couple may claim 7 016 050 "például úgy, hogy Orsi 2 000 000, Oszkár 5 016 050 forintot vesz
  igénybe".
- provisions: Szja tv. § 29/H (1) (mothers' allowance a) before the family allowance g)); § 29/A (1) (the family
  allowance reduces the consolidated base, so at most down to 0); 2025. évi XV. tv. 4. §.
- amounts: Orsi's base after the mothers' allowance is 2 400 000 - 600 000 = 1 800 000 (`Findings.f3_orsi_base`);
  200 000 of the 2 000 000 cannot reduce her tax. The couple loses nothing only if those 200 000 go to Oszkár (his
  wage is not given) or become a contribution allowance (15 % = 30 000 against her TB).
- classification: error in the example (the split is infeasible as stated). Draft text for NAV (not sent): "például
  úgy, hogy Orsi 1 800 000, Oszkár 5 216 050 forintot vesz igénybe (Orsi adóalapja a három gyermeket nevelő anyák
  kedvezménye után 1 800 000 forint)". status: confirmed against the statute.

### F4 Mother of three, 2025: income received after 30 September is exempt; moving receipts into Q4 saves 15 %
- kind: loophole-new (timing). households: mother of three, flat-rate (átalány, 40 %) sole trader with 6 000 000 of
  income after the cost ratio (taxable 4 255 200), husband employed at 1 AW, children 4, 8, 12.
- provisions: 2025. évi XV. törvény (in force 2025-10-01) 1. § (2) ("a jogosultsági időszakban megszerzett"), 4. §
  ("a 2025. szeptember 30. után megszerzett ... jövedelmei"), 1. § (6) (pro rata only "ha ... másként nem állapítható
  meg"; a sole trader's receipts are dated); Szja tv. § 29/H (1).
- amounts: Q4 share 25 % (even receipts) -> family burden 2 590 686; all taxable receipts in Q4 -> 2 111 976:
  **gain 478 710 HUF** (`Findings.f4_mother3_q4`; scan `results/own/mother3_q4.json`). Employed mothers: income
  "elszámolt" for October-December qualifies, so a bonus accounted to Q4 2025 instead of Q1-Q3 does the same.
- known? not found in 26 sources searched (NAV 73 § 3 and § 12, which describe the Q4 start, not shifting; NAV 100;
  2025. évi XV. tv. and its preamble; 3 web searches with 48 results). status: model-proved; a one-off for 2025, and
  the same lever exists at any later start of entitlement.

### F5 Turning 25: income accounted to months up to the birthday month is exempt up to months x 656 785
- kind: loophole-new (timing; probably known to payroll practitioners). households: employee turning 25 in June
  2025, 300 000 a month, 2 000 000 bonus.
- provisions: Szja tv. § 29/F (2) (income "a jogosultsági hónapokra elszámolt", at most months x the July-2024
  average wage), (3) (the last month is the birthday month); NAV 73 § 5.1 ("nincs lehetősége arra, hogy a fennmaradó
  részt a többi hónapban megszerzett jövedelmére érvényesítse").
- amounts: unused cap 6 x 656 785 - 1 800 000 = 2 140 710; bonus accounted to June: tax 270 000; to July or later:
  570 000: **gain 300 000 HUF** (`Findings.f5_birthday_bonus`); in general 15 % x min(bonus, m x (656 785 - monthly
  pay)) (scan `results/own/birthday_bonus.json`).
- known? not found in 23 sources searched (NAV 73, NAV 72, web search 3 with 20 results: NAV 25-év-alatti page,
  adozona.hu, eduline, privatbankar, bank360). status: model-proved.

### F6 2025 -> 2026: families whose 2026 family allowance will not be used up gain by deferring pay to January
- kind: loophole-new (timing across years). households: lone parent of three, 0.6 AW = 5 073 292, 1 000 000 deferred.
- provisions: Szja tv. § 29/A (2) 2025 (<= 330 000 per child per month) and 2026 (440 000; version 2026.X.1); Tbj.
  § 34 (3) (contribution allowance capped at the TB); `Theorems.famBurden_closed_form`: tax + TB - contribution
  allowance = max(0, 33.5 % x wage - 15 % x frame).
- amounts: 2025 burden 214 553 -> 0, 2026 burden stays 0 (2026 frame 15 840 000 absorbs 33.5 % x 6 073 292):
  **gain 214 553 HUF** (`Findings.f6_year_shift`), with 2025 rules other than the family allowance (the 2026 TB and
  Szja rates are unchanged, so only the frame matters for employees). Scan `results/own/year_shift.json`.
- known? not found in 23 sources searched (as F5; NAV's "Családi adókedvezmény-kalkulátor 2026-2029" page does not
  discuss timing). status: model-proved.

### F7 Dividends every second year: the szocho ceiling is annual
- kind: loophole-known (mechanism); found blind by the generic timing scanner.
- households: owner without wages paying 6 979 200 a year vs 13 958 400 every second year.
- provisions: Szocho tv. § 1 (5) c), § 2 (2) (ceiling 24 x minimum wage = 6 979 200 in 2025; wages counted first).
- amounts: **907 296 HUF per two years** (`Findings.f7_dividend_bunching`); generic scanner
  `results/search/timing.md`: couple with 1 AW of dividends, bunching gain up to 464 972 (5.5 % AW).
- known: the ceiling and "no szocho on dividends once wages reach it" are standard adviser material (adozona.hu,
  "Osztalék utáni szocho: mennyi lesz a maximum", web search 2); the bunching corollary was not stated in the 18
  results. status: recreated blind.

### F8 The under-25 allowance is worth nothing to a young lone parent of three below about 0.5 AW
- kind: statute-fault (design interaction; not counted as a fault in summary.json). households: lone parent aged 24,
  three children, 0.5 AW = 4 227 744.
- provisions: Szja tv. § 29/H (1) c) before g); § 29/F (1) ("csökkenti": not optional in the return); Tbj. § 34 (3).
- amounts: same burden at 24 and at 30 (-612 000 = családi pótlék; no tax, no TB) (`Findings.f8_young_parent`): the
  nominal 634 162 under-25 allowance is worth 0; 497 812 at 0.7 AW (scan `results/own/young_parent.json`). A partner
  with income recovers all of it (§ 29/B (1a)-(1b)).
- known: the analogous crowding-out of pension-savings refunds by the under-25 exemption is known (bank360.hu,
  2021-01-26); for the family allowance not found in 23 sources. status: model-proved.

### F9 Interest pays 13 % szocho without ceiling; dividends and fund gains stop at 24 x minimum wage
- kind: loophole-new (lead; income type). households: employee at 1 AW with 5 000 000 of savings income.
- provisions: Szocho tv. § 1 (5) f) (interest, since 2023-07-01) is outside the a)-e) list that § 2 (2) caps.
- amounts: interest 650 000 szocho (28 % in all), gains or dividends 0 (15 %) (`Findings.f9_interest_vs_gains`; scan
  `results/own/interest_vs_gains.json`). Converting interest into a gain (accumulating funds, discount instruments)
  saves 13 % for anyone whose wages reach 6 979 200.
- known? the interest szocho itself is widely reported; the asymmetry not found in 23 sources. status: model-proved
  (statute reading; TBSZ and state-bond exemptions not modelled).

### F10 Flat-rate (átalány) sole trader vs employment: 1 AW of business at 1 655 204 vs 3 479 470
- kind: loophole-known (disguised employment), recreated (owner scan); the generic income-type scanner finds the
  self-employment advantage blind (+8.5 % at 0.75 AW).
- provisions: Szja tv. § 50, § 53 (40 % cost ratio), 1. sz. melléklet 4.48. (tax-free half annual minimum wage);
  minimum bases (NAV 100 § 6); employer szocho 13 % (Szocho tv. § 2 (1)).
- amounts: `Findings.f10_atalany_vs_salary`; owner scan (`results/own/owner.json`), net cash at 1 AW: átalány
  6 800 283, Kft dividends with the active member's minimum bases 4 782 669, KIVA 5 434 561, all salary 4 976 017;
  KATA (B2C customers only) 7 855 487.
- known: KATA concealed employment and its 2021-2022 restrictions (bbj.hu 2021-03-13; trademagazin.hu; CMS note on
  the 2027 overhaul). status: recreated.

### F11 Családi pótlék amounts unchanged since at least 2009 while the family tax allowance was raised
- kind: statute-fault (amounts not updated together). households: families with little or no insured income.
- provisions: Cst. § 11 (1): 12 200 / 13 700 / 13 300 / 14 800 / 16 000 / 17 000 HUF in the version of 2009.I.1 and in
  2025 (`Findings.f11_csp_frozen`); Szja tv. § 29/A (2) raised in 2025 and 2026 (1 child: 66 670 -> 100 000 ->
  133 340 a month).
- effect: the cash benefit for one child is 4.2 % of the 2025 minimum wage (12 200 / 290 800); the tax allowance
  reaches only families with earnings. status: confirmed (text); a policy choice, not a drafting slip.

### F12 NAV family-allowance calculator: 2025 amounts correct; two conventions for the 667 % gross-up
- kind: gov-error (checked; convention only, not counted). The calculator on "Családikedvezmény-kalkulátorok a
  bevalláshoz" (module `csaladiKedvezmenyCalcV3`, last modified 2026-09-01) uses 66 670 / 133 330 / 220 000 to June
  2025, 100 000 / 200 000 / 330 000 from July 2025 and 133 340 / 266 660 / 440 000 from 2026: matches the statute and
  the model. It multiplies in-year contribution allowance by 6.67 and divides return-claimed allowance by 0.15 (F2).
  A legacy module still on the server (`nav-kalkulator-core`, amounts to 2024 only, no upper year limit) is not
  loaded by the page. status: clean.
