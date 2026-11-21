# Bulgaria (BG) 2025: FINDINGS

Model: `lean/` (BgTax, exe `bgtax`), stotinki inside, leva with two decimals out. Lean statements: `lean/BgTax/Findings.lean`
(concrete households, `native_decide`) and `lean/BgTax/Theorems.lean` (general proofs). Scanner output:
`results/search/*.json` (`harness/scan.py`). Validation: `results/validation_eurostat_2025.json`
(`harness/eurostat_check.py`). Money in BGN; 1 EUR = 1.95583 BGN.

### F1 Eurostat/EC tax-benefit model applies the April ceiling (4 130 лв.) to January-March 2025
- kind: gov-error (referee; error against the statute, or an annual-parameter convention of the EU-OECD model)
- households: single at 125 % and 167 % of the average wage (Eurostat `earn_nt_net` P1_NCH_AW125, P1_NCH_AW167, 2025).
- amounts: employee contributions overstated by 18.17 лв. (125 % AW) and 157.22 лв. (167 % AW: Eurostat 3 491.85 EUR = 6 829.46 лв.
  = 13.78 % x 12 x 4 130; statute 13.78 % x (3 x 3 750 + 9 x 4 130) = 6 672.28 лв.); income tax understated by 1.84 / 15.70 лв.;
  net income understated by 16.64 / 141.21 лв.
- provisions: ЗБДОО 2025 чл. 9, т. 1, б. "в" ("от 1 януари до 31 март ... максимален месечен размер на осигурителния доход -
  3 750 лв.") and т. 2, б. "в" (4 130 лв. from 1 April); КСО чл. 6, ал. 2, т. 1 (the ceiling is monthly).
- Lean: `BgTax.Tests` (`aw167` = 6 672.24 лв.), `Theorems.max_year` (48 420 лв.).
- status: confirmed (statute explicit). Draft note to Eurostat/EC (not filed): "earn_nt_net 2025, BG: employee SSC for
  P1_NCH_AW125/AW167 use a 4 130 BGN monthly ceiling for all 12 months; the 2025 DOO budget act sets 3 750 BGN for
  January-March. Also: the NAC series for BG equals the EUR series for 2023-2025 (BGN was the national currency then);
  if intended (euro-fixed back-conversion), a footnote would avoid misreading."

### F2 Eurostat/EC model applies the April limit of the child allowance (760 лв.) to January-March 2025
- kind: gov-error (referee; same classification as F1)
- households: one-earner couple, two children, 100 % AW (CPL_CH2_AW100): income per member 758.75 лв./month.
- amounts: Eurostat FAM 828.31 EUR = 1 620.03 лв. (12 x 110 лв. + 300 лв. school grant); statute 3 x 88 + 9 x 110 + 300 = 1 554 лв.
  (January-March: 758.75 > 710, so 80 %). Difference 66.03 лв.
- provisions: ЗДБРБ 2025 чл. 64, ал. 2, т. 1 ("от 1 януари до 31 март - 710 лв.") and ал. 3, ал. 5 (80 %).
- Lean: `BgTax.Tests` (`cpl` benefits = 1 554 лв.).
- status: confirmed. All other 44 Eurostat lines agree within 1 лв. (input wages rounded to whole leva).

### F3 The codified child relief is a thirtieth of the real one; the real amount lives only in each year's budget act
- kind: statute-fault
- households: every parent (2025: 6 000 / 12 000 / 18 000 лв. deducted from the annual tax bases = 600 / 1 200 / 1 800 лв. of tax).
- amounts: ЗДДФЛ чл. 22в, ал. 1 (in force since 1 Jan 2015, never amended) reads "двеста лв. / четиристотин лв. / шестстотин
  лв."; the State Budget Acts override it every year in their transitional provisions: 2022 § 2 (4 500 / 9 000 / 13 500 лв.),
  2023 § 2, 2024 § 2, 2025 § 3, 2026 § 3 (6 000 / 12 000 / 18 000 лв.; 2026: 3 067.75 / 6 135.50 / 9 203.25 EUR). Same for the
  disabled-child relief (чл. 22г: "2000 лв." vs 12 000 лв.) and the sole-trader carry-over (чл. 28, ал. 2, т. 5: "разликата между
  2000 лв. ..."), patched by § 3, ал. 3. The monthly advance relief through the employer (§ 3, ал. 4: 500 / 1 000 / 1 500 лв. a
  month) exists only in the budget acts: the codified чл. 42, ал. 3 knows only the reliefs of чл. 18 and 19.
- consequence: when the budget is late the relief has no statutory basis in the meantime. The 2025 act was promulgated on
  27 March 2025 (ДВ 26/2025, retroactive to 1 January), the 2026 act in ДВ 69/2026; the extension acts (2025: ДВ 6/2025; 2026:
  ДВ 113/2025, 52/2026, 57/2026) contain no child-relief provision (searched for "22в" / "облекчение за деца": none). From January
  to March 2025 and January to July 2026 employers had no legal basis for the monthly relief, and had a budget act failed the
  codified 200 лв. (600 лв. for three children) would have applied. The 2023 act (in force August 2023) shows the same gap.
- check of the 2026 euro conversion of § 3 (1.95583): 6 000 -> 3 067.75, 12 000 -> 6 135.50, 18 000 -> 9 203.25, 500 -> 255.65,
  1 000 -> 511.29, 1 500 -> 766.94, 150 -> 76.69 EUR: all correct to the cent (no slip found).
- provisions: ЗДДФЛ чл. 22в, ал. 1; чл. 22г, ал. 1; чл. 28, ал. 2, т. 4-5; чл. 42, ал. 3; ЗДБРБ 2022 § 2; 2023 § 2; 2024 § 2;
  2025 § 3; 2026 § 3 (corpus paths in PROGRESS.md).
- Lean: `Theorems.childRelief_30x`, `Findings.F3_relief`.
- status: confirmed from the texts. Fix: write the amounts (and the monthly advance relief) into ЗДДФЛ чл. 22в/22г/42.

### F4 Child allowance: four all-or-nothing income limits, METR above 100 % over bands of up to 1 540 лв.
- kind: loophole-new (notches / METR > 100 %; the cliff design is visible in the statute, its size and location for the standard
  households were not found quantified in the 3 sources searched: ЗСПД and ЗДБРБ 2025 texts, Eurostat earn_nt_net)
- households (one earner, wage grid step 10 лв.; `results/search/metr.json`):
  * single parent, 1 child: notches at 17 040 / 18 240 / 19 440 / 20 640 лв.; the last costs 352 лв. (dead zone 470 лв.)
  * single parent, 2 children (= couple with 1 child): 25 560 / 27 360 / 29 160 / 30 960 лв.: -58, -190, -256, -784 лв.
    (dead zones 90-1 030 лв.); one-earner couple, 2 children: 34 080 / 36 480 / 38 880 / 41 280 лв., same losses.
  * 3 children: losses up to 1 180 лв. for 10 лв. of gross wage (dead zone 1 540 лв.).
  The one-earner couple with two children at the 2025 average wage (36 420 лв., Eurostat) sits 60 лв. below the 36 480 лв. notch.
- mechanism: ЗДБРБ 2025 чл. 64, ал. 2-5: full allowance up to 710 лв. (Jan-Mar) / 760 лв. (from April) per member a month, 80 %
  up to 810 / 860 лв., nothing above; no taper. The test uses the previous 12 months' gross income (ЗСПД чл. 4а), so one raise or
  bonus moves the family across the limit for 12 months.
- Lean: `Theorems.allowance_notch_full` (198 лв. for one stotinka), `Theorems.allowance_notch_part` (792 лв.),
  `Findings.F5_single_parent_notch` (-784.29 лв. of net for +10 лв. gross).
- status: confirmed in the model. Fix: a taper instead of the two cliffs.

### F5 The contribution ceiling: the marginal wedge falls from 34.7 % of labour cost to 10 % above 4 130 лв. a month
- kind: loophole-known (regressivity of capped contributions: CATALOGUE K1)
- households: single employee. Below the ceiling 1 000 лв. more wage costs the employee 223.98 лв. and the employer 189.20 лв.:
  413.18 / 1 189.20 = 34.7 % of labour cost. Above 48 420 лв. a year (2025) it costs 100 лв. and the employer nothing: 10 %.
  Employee METR 22.4 % -> 19.3 % (between the Jan-Mar and April ceilings) -> 10 %.
- provisions: КСО чл. 6, ал. 2, т. 1, ал. 3, ал. 11; ЗБДОО 2025 чл. 9; ЗДДФЛ чл. 48.
- Lean: `Findings.F6_above_ceiling` (= 100 лв.), `Findings.F6_below_ceiling` (= 223.98 лв.), `Theorems.fund_above_ceiling`.
- status: recreated by the METR scan without being told.

### F6 Owner-manager: minimum insurance + dividends beats salary for profits of about 25 000-240 000 лв.; salary wins above
- kind: loophole-known (recreated blind: CATALOGUE K2); the crossover above the ceiling was not found in the sources searched
- households: one-person company (ЕООД), profit P before the owner's pay (`results/search/owner.json`; company side: CIT 10 %
  ЗКПО чл. 20, dividend tax 5 % ЗДДФЛ чл. 46, ал. 3, employer 18.92 % capped; PROGRESS.md). Net to the owner: P = 60 000: salary
  39 749, minimum self-insurance + dividends 47 827, management contract at the minimum wage + dividends 48 187 (+8 438 vs salary);
  P = 120 000: 93 749 / 99 127 / 99 487. Above the ceiling a lev of salary costs 10 % and a lev of dividend 14.5 % (10 % CIT + 5 % of
  90 %), so a full salary overtakes dividends from P ~ 240 000 лв. (P = 500 000: salary 435 749 vs dividends 424 027). A free
  profession (25 % statutory expenses, чл. 29, ал. 1, т. 3) beats both at P = 15 000-25 000 and P >= 200 000 (500 000: 450 385).
- caveats: the minimum insurable income for managers by activity (ЗБДОО 2025 прил. 1/1А) exceeds the minimum wage in many
  activities (not modelled); practitioners report NRA scrutiny of minimum pay (CATALOGUE K2).
- Lean: personal side = the model; the company arithmetic is in `harness/scan.py owner`.
- status: recreated.

### F7 Spouses: concentrating wages in one spouse saves up to 6 005 лв. a year (each person has a ceiling, the tax is flat)
- kind: loophole-new (not found in the 3 sources searched; relevant to family companies that choose whom to pay)
- households: couple with 120 000 лв. of wages: 120 000 + 0 pays 6 005.02 лв. less than 60 000 + 60 000; 96 840: 5 792.96 лв. The
  10 % tax is additive (`Theorems.pit_ticks_additive`): splitting never saves tax, and the per-person ceiling makes it cost money.
  The child relief can be used by either parent (`Theorems.splitRelief_total`, `splitRelief_symm`).
- Lean: `Findings.F8_concentrate`.
- status: confirmed.

### F8 Second income above the ceiling: civil contract / free profession 7.5 % instead of 10 %
- kind: loophole-known (CATALOGUE K3)
- households: employee earning 60 000 лв. with 12 000 лв. more: as employment 1 200 лв. of tax, as a civil contract or free
  profession 900 лв. (25 % statutory expenses, no contribution room left under the shared ceiling, КСО чл. 6, ал. 11).
- Lean: `Findings.F9_civil`, `Findings.F9_employment`.
- status: recreated.

### F9 Pay bunched into one month escapes contributions; in 2025 a January-March bonus escapes more
- kind: loophole-known (the monthly ceiling: CATALOGUE K4), 2025-specific twist not found in the sources searched
- households (`results/search/timing.json`): monthly 2 000 лв. + a 12 000 лв. bonus in one month saves 1 360 лв. employee and
  1 867 лв. employer contributions against even pay; paid in January-March (ceiling 3 750 лв.) it saves 52.36 + 71.90 лв. more.
- anti-avoidance: КСО чл. 6, ал. 2: "Възнагражденията, отнасящи се за положен труд за минало време, се разпределят за
  отработените дни, през които трудът е положен"; whether an annual bonus is pay "за минало време" decides the lever.
- Lean: mechanism `Theorems.fund_above_ceiling`; the bunching itself is outside the canonical household (wages paid evenly).
- status: lead with the anti-avoidance caveat.

### F10 The first lev of registered free-profession income costs 3 472.78 лв. of contributions
- kind: loophole-new (notch; the minimum base is well known, the notch was not found quantified in the sources searched)
- households: no other income: income 1 лв. -> contributions 3 472.78 лв. (27.8 % x 12 492 лв.); an employee earning 20 000 лв.
  with 1 лв. of registered free-profession income pays the same extra. Income below 16 656 лв. a year pays on the minimum.
  Not for civil contracts (КСО чл. 4, ал. 3, т. 5-6: insured on the actual amount); pensioners may opt out (чл. 4, ал. 6).
- provisions: КСО чл. 6, ал. 8-9; ЗБДОО 2025 чл. 9, т. 1-2, б. "б" (933 / 1 077 лв.).
- Lean: `Findings.F11_first_lev`.
- status: confirmed in the model.

### F11 The allowance's family is defined by the current address: unmarried parents living apart on paper get it in full
- kind: loophole-new (lever; legal only if the addresses are true. Not found in the 3 sources searched)
- households: unmarried parents earning 22 500 лв. each, two children: one current address -> 300 лв. (school grant only); the
  parent with the children at a separate address -> 1 620 лв. (+1 320 лв.). At 20 000 лв. each: +528 лв. Tax unchanged.
- provisions: ЗСПД § 1, т. 1, б. "б" ("съвместно живеещи родители без сключен граждански брак, които съжителстват на един
  настоящ адрес"), б. "в"; married parents are one family wherever they live (б. "а").
- Lean: `Findings.F12_separate_address`.
- status: confirmed in the model (cohabiting parents are modelled as one family).

### F12 Global law holds Bulgaria's ЗДДФЛ only as promulgated in 2006
- kind: model-fix (tool limitation, reported; not a government error)
- the entry `bulgaria/national/acts/zakon/2006/dv095-2858/` reads "1 versions, from 2007-01-01": none of the ~100 amending acts is
  applied, so чл. 22в (2015) is absent and provision_history / compare_dates cannot show its history; the amending and budget acts
  are in the corpus as separate acts (used here). КСО, ЗЗО and ЗСПД are not in the corpus. Consolidated texts: NRA (КСО docx
  08/2026), Ciela free zone (ЗДДФЛ, ЗЗО, ЗСПД, ЗКПО), dated amendment notes read back to 2025.
