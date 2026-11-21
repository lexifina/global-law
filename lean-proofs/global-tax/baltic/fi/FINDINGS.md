# Finland (Helsinki), tax year 2025: findings

Model: `lean/FiTax` (statute provision by provision on TaxKernel; exe `fitax`; cents). Validation: OECD Taxing Wages
2025 for FIN, 48/48 mapped lines and 8/8 take-home pays exact at the OECD's average municipal rate 7,54 %
(`results/oecd_check_FI.md`, `runs/referees.json` "oecd754_thp"); Veronmaksajat's 2025 wage-earner table 287/287
within 1 EUR (max 0,50); Kela's 2025 pension tax table 32/32 to the cent per month; Verohallinto's published 2025
thresholds (4 of 4) as theorems (`FiTax/Tests.lean`). Theorems: `FiTax/Theorems.lean`, `FiTax/Tests.lean`,
`FiTax/Loopholes.lean` (53 theorems, no `sorry`; `#print axioms` at most propext, Classical.choice, Quot.sound).
Scans: the kernel's generic scanners (`results/search/SUMMARY.md`), `harness/fi_scan.py` (`runs/fi_scan.json`),
`harness/owner_fi.py` (`runs/owner/owner.md`). Amounts in euros, Helsinki 5,30 %, no church tax, age 40 unless
stated; "net" = gross - all taxes and employee contributions + lapsilisä.

Kinds: loophole-known | loophole-new | gov-error | statute-fault | model-fix | reading. Known-ness: "known" cites
where; otherwise "not found in N sources searched" lists them. Sources searched for novelty (the Finland web
searches were spent on parameters; these were read in full or grepped): HE 108/2024, HE 98/2025, Verohallinto's
deduction and contribution pages, Veronmaksajat's "Palkansaajan veroprosentit 2025" and Verotietoa 98, Kela's
pension tax page, ETK 2025, the OECD country table, the kernel's FINDINGS/LEADS, and the Swedish, Norwegian and
Danish FINDINGS (11 sources).

### F1 Päivärahamaksu floor: one cent of pay at 16 861,99 € costs 141,64 €; 160 € of dead zone
- kind: loophole-known (notch); the dead zone's size: not found in 11 sources searched
- households: any person with wages + self-employment income around 16 862 € (a part-time job, a second earner, an
  owner-manager's salary). The generic METR scanner found it blind ("141 at 16,861", peak METR 138,7 % on its
  0,002 AW grid); the owner-manager scan's optimal salary at 0,5 and 1 AW of profit is exactly 16 861 €.
- amounts: below 16 862 € no päivärahamaksu; at 16 862 € 0,84 % of the whole base, 141,64 €. Deductible (TVL 96 §),
  but in this band the income tax is wholly absorbed by the work credit, so the deduction saves nothing. The worker
  is as well off as at 16 861,99 € again only at 17 022 € of pay (160 € later).
- provisions: sairausvakuutuslaki 18:15 3 mom ("Päivärahamaksua ei peritä, jos vuotuisen palkka- ja yrittäjätulon
  yhteismäärä alittaa" the indexed limit); Verohallinto 2025: "0,00 %, jos tulot ovat alle 16 862 euroa"; kernel
  `Contribution.floor_notch`.
- Lean: `FiTax.daily_floor_notch`, `FiTax.daily_notch`, `FiTax.f1_daily_notch`
- status: certain. Known: the threshold is published by Verohallinto (with the 1,06 % / 1,90 % "minipidätys").
  Advice: keep a small job's annual pay at or below 16 861 € or above 17 022 €.

### F2 The 2025 work credit is withdrawn up to 125 240 € of pay: the marginal rate is above the top rate there
- kind: loophole-known (statute design; acknowledged and removed for 2026)
- households: single wage earner, Helsinki: METR 55,9-56,0 % from 97 300 to 125 240 € of pay, against the statutory
  top rate of 54,85 % (above 164 900 €); between 125 240 and 164 900 € the METR falls to 52,6 % (`runs/fi_scan.json`
  S1/S4; generic scanner: "56.0 % average (max 57.7 %) from 97,502 to 125,122", all five family types).
- amounts: state 41,75 % + municipal 5,30 % + sairaanhoitomaksu 1,06 % on taxable income (x 0,9142 after the
  deductible contributions) + 8,58 % contributions + the work credit's 3,44 % withdrawal.
- provisions: TVL 125 § 2 mom (702/2024): "Siltä osin kuin ... puhdas ansiotulo ylittää 42 550 euroa, vähennyksen
  määrä kuitenkin pienenee 3,44 prosentilla"; Asteikkolaki 701/2024.
- Lean: `FiTax.f2_hump`
- status: certain. Known: HE 98/2025 removes "työtulovähennyksen toinen poistuma" so that "marginaaliveroasteet
  rajautuisivat enimmillään noin 52 prosenttiin" (`refs/he_98_2025.txt:535,562`); for 2026 TVL 125 § reads
  "Vähennyksen määrä ei pienene puhtaan ansiotulon 50 550 euroa ylittävältä osalta".

### F3 Because of F2, bunching pay pays in 2025: 155 000 + 97 000 € costs 950 € less than 126 000 € twice
- kind: loophole-new (timing)
- households: a single earner on about 126 000 € a year who can move pay between years (bonus, holiday pay, option
  exercise, fee timing). Found blind by the generic timing scanner (963 € on its grid: 156 958 + 97 281 vs 127 119
  twice; bunching pays at 12,8 % of its grid points); `fi_scan.py` S4 grid optimum 950,36 €.
- amounts: on a progressive (convex) tax smoothing is always best (kernel `splitting_le_separate`); the 2025 tax is
  not convex where the work credit's withdrawal stops (125 240 €), so moving income from the 56 % band to the 52,6 %
  band is cheaper than keeping it.
- provisions: TVL 125 § 2 mom (702/2024); Asteikkolaki 701/2024.
- Lean: `FiTax.f3_bunching` (= 950,36 € exactly); the convex counterpart for the scale alone: `state_convex`,
  `state_split_le_separate`.
- status: certain with 2025 rules in both years (in reality the other year's law applies; with the 2026 credit no
  longer withdrawn above 50 550 €, deferring pay from 2025 into 2026 is worth more still). Not found in 11 sources
  searched (HE 98/2025 discusses the marginal rates, not timing).

### F4 Unlisted dividends: the 8 % capital-income band can raise the tax (the earned-income part carries the basic deduction and the work credit, and no contributions)
- kind: loophole-new (income-type conversion; the tax is not monotone in the company's net assets)
- households: an owner-manager of an unlisted company (`fiUnlistedDividends`, `fiNetAssets`), no other income.
- amounts: a dividend of 20 000 € with no net assets is 15 000 € of earned income (TVL 33 b § 2 mom): the
  perusvähennys and the work credit (18 % of "ansiotulona verotettavan osingon") wipe out the state, municipal and
  health-care taxes and no TyEL, unemployment or daily-allowance contribution is due: 0 € of personal tax. The same
  dividend with 250 000 € or more of net assets is 5 000 € of capital income (25 %): 1 500 €. In the owner scan with
  the salary optimised (`runs/fi_scan.json` S8): 0,5 AW of profit costs 20,1 % with no net assets and 23,9 % with
  250 000 € or more; 1 AW: 23,0 % at 250 000 € but 25,1 % at 500 000 €. Above about 2 AW of profit more net assets
  always help (10 AW: 47,5 % with none, 39,1 % with 2 MEUR): the well-known lever K2.
- provisions: TVL 33 b § 1-2 mom, 106 §, 125 § 1 mom; sairausvakuutuslaki 18:15 (daily-allowance base = wages and
  YEL income only).
- Lean: `FiTax.f4_owner_zero_assets`, `FiTax.f4_split_zero`, `FiTax.f4_split_250k`
- status: certain on the statute as modelled (the owner's YEL obligation, if over 30 % and managing, is not modelled
  and does not touch the dividend). Not found in 11 sources searched; the income-shifting literature (Pirttilä &
  Selin 2011, Harju & Matikka 2016) treats the 8 % band as the favourable route.

### F5 Capital gains: two years instead of one saves 1 040 € on 60 000 €
- kind: loophole-known (timing across the 30/34 % threshold)
- households: single, 60 000 € of capital gains (or any capital income), no other income.
- amounts: 19 360 € in one year vs 2 x 9 160 € = 18 320 € (`fi_scan.py` S5); 4 % of the part above 30 000 €.
- provisions: TVL 124 § 2 mom.
- Lean: `FiTax.f5_capital_timing`, `FiTax.capital_spread_le` (generic: never worse to spread, by convexity)
- status: certain; known (spreading realisations; K6 for spouses).

### F6 The same 25 000 € costs a pensioner 750 € more than a worker
- kind: loophole-known (income-type difference)
- households: single, 25 000 € of pension at 70 vs 25 000 € of pay at 40 (`fi_scan.py` S3: the pensioner pays more
  from about 17 000 to 80 000 €, most around 25 000 €; less below 15 000 €, where the worker's 7,74 % contributions
  dominate).
- amounts: 3 865,38 € vs 3 115,15 €. The pensioner gets the eläketulovähennys (withdrawn at 51 % from 11 030 €, then
  19,6 %) but no work credit, and pays 1,45 % health-care contribution; the pensioner's METR is 37 % at 16 000-20 000 €
  and falls to 27 % at 24 000 € (the withdrawal is not progressive: `pensionReduction_not_progressive`).
- provisions: TVL 100 §, 125 §; sairausvakuutuslaki 18:20 3 mom.
- Lean: `FiTax.f6_pension_vs_pay`, `FiTax.pensionReduction_not_progressive`
- status: certain; known (Veronmaksajat publishes separate pensioner tables; HE 98/2025 on pension taxation).

### F7 A single parent who marries loses 1 859 € a year (two children)
- kind: loophole-known (marriage penalty from the benefit side)
- households: one parent with two children (5 and 9) marrying a partner with no income (`fi_scan.py` S7).
- amounts: the lapsilisä single-parent supplement 2 x 73,30 € x 12 = 1 759,20 € and the doubled work-credit child
  increase (4 x 50 € to 2 x 50 €) 100 €. Moving in with a partner (no common child, not married) loses the lapsilisä
  supplement ("avioliitonomaisissa olosuhteissa") but not the doubled work-credit increase, because TVL 7 § treats
  such partners as unmarried: two laws, two definitions of a single parent (R2).
- provisions: lapsilisälaki 7 § 3 mom; TVL 125 § 4 mom; TVL 7 §.
- Lean: `FiTax.f7_marriage_cb`, `FiTax.f7_marriage_wc`
- status: certain; the lapsilisä part is known (Kela's yksinhuoltaja definition). The generic unit scanner reports no
  marriage penalty because it compares married with cohabiting couples, which this model (and the lapsilisä law)
  treats alike.

### F8 A low earner's capital-deficit credit is not usable that year (600 € per 2 000 € of deficit)
- kind: loophole-known (spouse transfer)
- households: 12 000 € of pay and a 2 000 € rental loss (`fi_scan.py` S9).
- amounts: the 30 % credit (600 €) finds no tax: the work credit has already wiped out the state, municipal and
  health-care taxes (TVL 125 §: "Vähennys tehdään ennen muita tuloverosta tehtäviä vähennyksiä"). It becomes a capital
  loss carried forward (TVL 60 § 2 mom); a spouse can use it at once on request (134 §): 1 200 € saved on a
  2 x 2 000 € deficit of a 12 000 / 60 000 € couple.
- provisions: TVL 125 § 2 mom, 131-134 §, 60 § 2 mom.
- Lean: `FiTax.f8_deficit_lost`
- status: certain; known (134 § transfer).

### G1 HE 98/2025 gives the 2025 work credit's end as a puhdas ansiotulo of "noin 125 300 euroa"; it is 124 490 €
- kind: gov-error (explanatory text of a government proposal; no effect on assessments)
- text: "Kun puhdas ansiotulo ylittää noin 125 300 euroa, työtulovähennystä ei enää myönnetä." (`refs/he_98_2025.txt:357`)
- the statute (TVL 125 § 2 mom, 702/2024): 3 225 - 2,22 % x (42 550 - 24 250) - 3,44 % x (x - 42 550) = 0 at
  x = 124 490,12 € of puhdas ansiotulo. A person with a puhdas ansiotulo of 124 500 € gets nothing. 125 240 € is the
  corresponding pay (puhdas ansiotulo + the 750 € tulonhankkimisvähennys); with one child the end is 125 943 €. A pay
  threshold labelled as a net-income threshold.
- Lean: `FiTax.g1_he98_threshold`
- status: certain (arithmetic of the quoted statute).

### G2 HE 108/2024 gives the 2024 ansiotulovähennys's end as a puhdas ansiotulo of "noin 94 084 euroa"; it is 93 333 €
- kind: gov-error (same pattern as G1)
- text: "Ansiotulovähennystä ei myönnetä osittaisenakaan, jos verovelvollisen puhtaan ansiotulon määrä ylittää noin
  94 084 euroa." (`refs/he_108_2024.txt:361`)
- the statute (TVL 105 a § as in 1123/2022, in force to 2024): max 3 570 €, "pienenee 4,5 prosentilla puhtaan
  ansiotulon 14 000 euroa ylittävältä osalta": zero at 14 000 + 3 570 / 0,045 = 93 333,33 € of puhdas ansiotulo;
  94 083,33 € is again the pay. (The same proposal's "noin 55 927 euroa" for the eläketulovähennys is right, pensions
  having no 750 € deduction; its "noin 168 000 euroa" for the 2024 work credit is right to rounding.)
- Lean: `FiTax.g2_he108_threshold`
- status: certain. Suggested correction (draft, not filed): state such thresholds either as pay ("palkkatulo") or as
  puhdas ansiotulo, consistently, in the proposals' descriptions of current law.

### R1 Verohallinto's summary of the 2025 work-credit withdrawal reads as cumulative
- kind: reading (guidance wording; the assessment follows the statute)
- text: "Vähennyksen määrää pienennetään 2,22 %:lla puhtaan ansiotulon 24 250 euroa ylittävältä osalta ja 3,44 %:lla
  42 550 euroa ylittävältä osalta." (`refs/vero_automaattiset_vahennykset.txt:78`). Read literally both rates apply
  above 42 550 € (5,66 %); the statute says "kuitenkin" (3,44 % instead of 2,22 %). The OECD's figures (BTC 2 400,36
  at the average wage) and Veronmaksajat's 287 rows agree with the statute; the cumulative reading would give
  2 399,70 € at the average wage and end the credit near 93 000 €.
- Lean: `FiTax.oecd_s100` (work credit 2 400,36)

### R2 Two definitions of a single parent
- kind: reading (statute design; not counted as a fault)
- TVL 125 § 4 mom doubles the child increase if "verovelvolliseen ei sovelleta tämän lain puolisoita koskevia
  säännöksiä" and for children "joiden ainoa huoltaja hän on"; TVL 7 § counts cohabiting partners as spouses only
  with a common child. Lapsilisälaki 7 § 3 mom denies the supplement to a parent who "elää yhteisessä taloudessa
  avioliitonomaisissa olosuhteissa". A parent living with a new partner keeps the tax doubling and loses the benefit
  supplement; a divorced parent with joint custody (both guardians) gets no doubling although Vero's page says
  "Yksinhuoltajalle korotus myönnetään kaksinkertaisena". Model: `spouses` treats cohabiting partners with children as
  spouses (the contract cannot say whose child it is).

### M1 OECD convention: average municipal rate, YLE tax in central tax
- kind: model-fix / convention (not an error)
- The OECD computes Finland's municipal tax at the weighted average 7,54 % and books the yleisradiovero (160 €) in
  CGITFP. `oecd_map.py` reads the exe's lines recomputed at 7,54 % (`oecd754_*`); the contract's own take-home pay
  (Helsinki 5,30 %) differs from the OECD's by 2,24 % of taxable income (+1 119 € for S100), and equals it within
  2 cents when the household is run at 7,54 % (`runs/referees.json` "oecd754_thp", 8/8).

### M2 The harness's generic FI owner-manager entry taxes the owner's dividend as a listed dividend
- kind: model-fix (harness, for the kernel/family lead; not edited here)
- `~/cmp20/harness/search/company.json` has an "FI" entry (OECD effective employer rate 20,46 %, dividends entered as
  the contract's `dividends`, i.e. 85 % capital income) and `b38.py` keeps it in preference to
  `~/cmp20/baltic/fi/company.json`. An owner's dividend from an unlisted company is taxed under TVL 33 b § (25 % /
  75 % earned). `harness/owner_fi.py` runs the same owner.py with Finland's cited entry (`runs/owner/owner.md`): at
  1 AW of profit the best split is 16 861 € salary + dividends, 25,1 % (generic entry: 33,2 %).

### Not errors (checked)
- No provision in TVL, sairausvakuutuslaki, yleisradioverolaki, ennakkoperintälaki, VML or the act on limited tax
  liability (627/1978) still refers to the repealed ansiotulovähennys (TVL 105 a §, repealed from 2025 by 702/2024).
- The 2025 scale's published "Vero alarajan kohdalla" column equals its rates on every band (`state_table_eq_formula`).
- Verohallinto's 2025 figures for the eläketulovähennys (max 11 030 €, none above 48 930 €), the perusvähennys (none
  above 26 976 €) and the 65+ work credit (4 425 €) follow from the statute (`FiTax/Tests.lean`).
- Kela's 2025 pension tax table (32 rows) agrees with the statute to the cent per month.
