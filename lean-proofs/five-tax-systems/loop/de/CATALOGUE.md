# German individual tax planning (VZ 2025): catalogue, triage, recreation

Model: the DeTax exe (`../../de/lean/.lake/build/bin/detax`, unchanged; assumptions in `../../de/EXAMPLE.md`).
Script: `recreate.py` (helpers `de.py`), output `runs/recreate.json`. Headline theorems: `lean/LoopDe/Loopholes.lean`
(builds clean, no `sorry`).

**"Burden"** = income tax + Soli + Kirchensteuer + employee contributions − Kindergeld kept (contract net-income terms).
**Saving** = burden without − burden with (or the household cash difference, where stated). Single = one adult aged 40,
childless, no church tax, unless stated.

**Triage**: (a) expressible with the exe as it stands; (b) a small statute-faithful step in this folder: either a
post-step on the exe's output (§ 32b, § 34, § 34g, § 35a, BEEG via the exe's `--pap` mode) or **proxy P1**: a deduction
the exe has no input for (Werbungskosten above the Pauschbetrag, Sonderausgaben, außergewöhnliche Belastungen,
Pauschbeträge, § 23 gains) entered as negative (or positive) `rentalIncome`, which has the same effect on the zvE via
§ 2 (3)-(5) EStG (the only differences: the § 10b 20 % cap and the § 24a base, neither binding in these cases); (c) out
of scope.

Sources: statute sections are cited as in force for VZ 2025 (copies in `../../de/law/2025/`; the other pages, fetched
from gesetze-im-internet.de 2026-11-18, are listed in `../../refs/README.md`). § 9 (1) Nr. 4 in its current text is the 2026 version (0,38 € from the first
km); for 2025 the 0,30 € (km 1-20) / 0,38 € (from km 21) rule is used.

## (a) and (b): recreated (41 techniques)

| ID | Technique | Source | T | Scenario | Without | With | Saving € | Statutory cause |
|---|---|---|---|---|---|---|---|---|
| L01 | Ehegattensplitting vs individual assessment | EStG §§ 26, 26b, 32a (5); BVerfGE 61, 319 | a | married, one earner 80 000 € | 31 838 | 25 549 | **6 289** | tariff applied to half the joint zvE, doubled: the second Grundfreibetrag and the lower zones are used twice (`marriage_bonus_90k` for the 90 000 € case) |
| L02 | Steuerklassen III/V vs IV/IV | EStG §§ 38b, 39b (2); § 46 (2) Nr. 3a | a | 5 000 + 2 000 €/month, LSt+Soli withheld per year (PAP 2025) | 10 697 | 8 678 | 2 019 (cash flow only) | **withholding only**: class III carries both basic allowances, V none; assessment gives 9 974 € either way (III/V owes 1 296 €, IV/IV gets 723 € back) |
| L04 | Marry by 31 December | EStG § 26 (1) Satz 1 | a | 90 000 € + 0 €, unmarried vs married | 36 676 | 29 327 | **7 349** | one day of marriage in the VZ gives whole-year splitting (Lean `marriage_bonus_90k`) |
| L05 | Separation year: stay jointly assessed | § 26 (1): "nicht dauernd getrennt" at any time in the VZ | a | 70 000 + 15 000 € | 29 748 | 27 691 | 2 057 | splitting for the year of separation if living together on 1 January |
| L06 | Witwensplitting | § 32a (6) Nr. 1 | a | widow(er), 70 000 € wages (proxy: joint with 0-income spouse) | 27 248 | 21 917 | 5 331 | splitting for the year after the death |
| L07 | Choose Einzelveranlagung (§ 26a) | §§ 26 (2), 26a | a | see N2 in NOVEL.md and L29 | | | ≤ 1 tariff € (S3); more only with § 32b | |
| L08 | Minijob for the second earner | § 40a (2); SGB IV § 8 (1a); SGB VI § 6 (1b) | a | primary 70 000 €, spouse 6 672 € vs 6 673 € | 23 461 | 21 917 | 1 544 | the Minijob wage leaves the joint assessment (employer's 2 % flat tax, 133 €) and is contribution-free for the employee; one euro more puts the whole wage at the couple's marginal rate (known cliff, BLOG_NOTES) |
| L09 | Employ the spouse (Minijob) in one's practice | § 4 (4), § 40a (2); R 4.8 EStR; BFH X R 31/12 | a | freelancer 90 000 €; spouse Minijob 6 672 € (employer cost 8 772 €) | net 62 857 | net 63 433 | 576 | profit falls by the full employer cost at ~44 % + voluntary KV, the wage is taxed at 2 %; needs a real arm's-length job |
| L10 | Midijob (Übergangsbereich) | SGB IV § 20 (2); SGB VI § 163 (10), § 70 (1a) | a | 1 200 €/month, childless, 30 | 3 103 | 2 321 | 782 | reduced employee base up to 2 000 €/month, pension points on the full wage |
| L11 | Günstigerprüfung child by child | § 31 Satz 4; WD 4-3000-065/24 | a | OECD couple 100 % + 67 % AW, 2 children | 34 028 | 33 974 | 54 | Freibeträge for the 1st child, Kindergeld for the 2nd (= FINDINGS O1; automatic) |
| L12 | Entlastungsbetrag Alleinerziehende (no other adult at home) | § 24b | a | single parent 40 000 €, 1 child | 9 912 | 8 719 | 1 193 | 4 260 € deduction lost when another adult lives in the household (§ 24b (3)) |
| L13 | Give capital to a child | §§ 20 (9), 32a, 32d (6); SGB V § 10 (1) Nr. 5 | a | parent 90 000 €, 7 400 € dividends | 38 364 | 36 676 | 1 688 | child's own Sparer-Pauschbetrag and Grundfreibetrag via § 32d (6); kept ≤ 7 420 € so the child stays family-insured |
| L14 | Realise gains yearly (Sparer-Pauschbetrag) | § 20 (9) | a | 2 000 € of gains over 2 years | 45 264 | 45 000 | 264 | 1 000 € allowance is annual and lapses |
| L15 | Günstigerprüfung § 32d (6) | § 32d (6) | a | pensioner 70, 22 000 € pension, 10 000 € dividends | 5 598 | 5 179 | 419 | tariff below 26,375 % incl. Soli (FINDINGS S7); automatic on application |
| L16 | Equity fund instead of bond fund | InvStG § 20 (1) | b | 10 000 € fund gain (70 % taxable) | 24 874 | 24 083 | 791 | 30 % Teilfreistellung for Aktienfonds |
| L17 | Realsplitting | § 10 (1a) Nr. 1, § 22 Nr. 1a, § 9a Nr. 3 | b | payer 80 000 €, recipient 15 000 €, 13 805 € maintenance (both returns) | 34 338 | 31 991 | 2 347 | deduction at the payer's ~44 % rate, income at the recipient's lower rate; payer must make good her extra tax |
| L18 | Claim childcare costs | § 10 (1) Nr. 5 (80 %, ≤ 4 800 €/child, 2025) | b | couple 70 000 + 20 000 €, 2 children, 6 000 € each | 23 634 | 20 802 | 2 832 | Sonderausgabe |
| L19 | Employer Kita subsidy instead of a raise | § 3 Nr. 33; SvEV § 1 (1) Nr. 1 | a | 6 000 € fees: raise (fees 80 % deductible) vs subsidy | cash 65 534 | cash 66 366 | 832 | tax- and contribution-free (unlimited) vs taxed raise minus Sonderausgabe |
| L20 | Bunch Werbungskosten into one year | § 9a Nr. 1 a (1 230 €) | b | 1 000 €/yr vs 2 000 € in one year | | | 263 | costs below the Pauschbetrag are worthless; bunched, 770 € count |
| L21 | Homeoffice-Tagespauschale + commuting | § 4 (5) Nr. 6c, § 9 (1) Nr. 4 | b | 138 HO days + 92 days × 25 km = 1 555 € | | | 111 | only the excess over 1 230 € counts |
| L22 | Entfernungspauschale (any transport) | § 9 (1) Nr. 4, (2) | b | 40 km, 220 days = 2 992 € | | | 599 | flat per km whatever the real cost (cyclists, car pools) |
| L23 | bAV Entgeltumwandlung | § 3 Nr. 63; SvEV § 1 (1) Nr. 9; BetrAVG § 1a (1a) | a | 60 000 €, converts 3 864 € (4 % BBG), contract gets 4 444 € | net cost 1 985 | 4 444 saved | 2 459 | tax- and SV-free conversion + 15 % employer top-up; **deferral**: payouts taxed (§ 22 Nr. 5) and KV/PV-liable; lower state pension |
| L24 | Sachbezug 50 €/month instead of a raise | § 8 (2) Satz 11 | a | 600 €/year | 306 net | 600 | 294 | Freigrenze: tax- and SV-free (a cliff at 50,01 €) |
| L25 | Übungsleiter-/Ehrenamtspauschale | § 3 Nr. 26 (3 000 €), Nr. 26a (840 €) | a | 50 000 € wages + 3 000 € coaching | 18 669 | 17 708 | 961 | tax-free (Subventionsbericht: Steuervergünstigung) |
| L26 | Tax-free night/Sunday/holiday supplements | § 3b; SvEV § 1 (1) Nr. 1 | a | 45 000 € + 6 000 € supplements | 18 177 | 15 398 | 2 779 | supplements on a base ≤ 50 €/h tax-free, ≤ 25 €/h SV-free |
| L27a | Fünftelregelung for a severance payment | § 34 (1), (2) Nr. 2, § 24 Nr. 1 | b | 70 000 € wages + 100 000 € Abfindung, same year | 57 259 | 55 947 | 1 312 | 5 × tax on one fifth: small when the other income is already in the 42 % zone (Lean `severance_*`) |
| L27b | **Severance paid in a year without other income** | § 34 (1) Satz 3, § 11 (1) | b | same, paid next January | 55 947 | 20 770 | **35 177** | with no other income the fifth (19 993 €) sits in zone 3: 5 × 1 637 € instead of 41 160 €; Abfindung SV-free (BSG 21.2.1990, 12 RK 20/88); health cover in year 2 not costed (Lean `severance_timing_saving`: 32 260 € of ESt) |
| L28 | **Steuerklasse III for the mother before Elterngeld** | BEEG §§ 2, 2c (3), 2e (3), 2f; BSG 25.6.2009, B 10 EG 3/08 R | b | mother 3 000 €/month, 12 months Basiselterngeld | 12 702 | 17 323 | **4 620** | Elterngeld = 65-67 % of net pay after the *withholding* of her Steuerklasse; III (held most of the 12 months) cuts the notional tax; partner's extra withholding in V comes back at assessment |
| L29 | Progressionsvorbehalt: test Einzelveranlagung | § 32b (1) Nr. 1 j, (2); § 26a | b | 14 000 € wages + 21 600 € Elterngeld, partner 14 000 € | 1 948 | 1 611 | 337 | separately, the Elterngeld raises only the recipient's rate on her small zvE; jointly it raises the rate on both incomes. Joint wins in 4 of 6 grids (by up to 3 573 €) |
| L30 | Riester: Sonderausgabe on top of the Zulage | § 10a (1), (2); §§ 84, 85 | b | single 80 000 € (Zulage 175 €) / single parent 50 000 €, 2 children (775 €) | | | 668 / 0 | deduction of 2 100 € worth 843 € at 80 000 €, extra over the Zulage 668 €; with child Zulagen it does not beat them |
| L31 | Basisrente (Rürup) | § 10 (1) Nr. 2 b, (3) | a | single 80 000 €, 10 000 € paid | 31 838 | 27 963 | 3 875 | deductible within 29 344 € minus RV; **deferral**: pension taxed later |
| L32 | Put side earnings on the spouse past 64 | § 24a (Satz 4: each spouse) | a | 15 000 € wages; spouse 66 with pension vs spouse 60 | 5 214 | 5 118 | 96 | Altersentlastungsbetrag (12,8 %, ≤ 608 €) only on the older spouse's non-pension income |
| L33 | Work past the Regelaltersgrenze drawing a full pension | SGB VI § 5 (4) Nr. 1; SGB III § 28 (1) Nr. 1 | a | 40 000 € wages, age 66 vs 68 | 8 620 | 4 380 | 4 240 | no employee RV (9,3 %) or AV (1,3 %); opting in raises the pension |
| L34 | Donation | § 10b (1) | a | single 80 000 €, 1 000 € | 31 838 | 31 449 | 389 | Sonderausgabe up to 20 % of GdE |
| L35 | Party donation credit | § 34g (50 %, ≤ 825 €) | b | single 60 000 €, 1 650 € | 9 570 | 8 745 | 825 | credit beats the § 10b deduction of the same sum (550 €) |
| L36 | Split craftsman invoices over two years | § 35a (3) (20 %, ≤ 1 200 €/yr) | b | 12 000 € of labour: one year vs December/January | 1 200 credit | 2 400 credit | 1 200 | annual cap |
| L36b | (trap) § 35a credit is not refundable | § 35a | b | pensioner 19 000 €, 4 000 € credit due | 4 000 | 0 | −4 000 | tariff tax 0 €: the credit lapses |
| L37 | Bunch medical costs into one year | § 33 (3); BFH 19.1.2017, VI R 75/14 | b | couple 70 000 €, 2 children: 2 000 €/yr vs 4 000 € once (zumutbare Belastung 2 135 €) | | | 526 | zumutbare Belastung is per year |
| L38 | Leave the church | KiStG der Länder; § 51a; § 10 (1) Nr. 4 | a | single 60 000 €, 9 % | 23 063 | 22 500 | 563 | 9 % of the ESt, net of its own Sonderausgabe deduction (iterated) |
| L39 | Time a bonus to smooth income | § 11, § 38a (1) Satz 3; SolZG § 4 | a | 60k + 100k vs 80k + 80k | 64 280 | 63 677 | 603 | convex tariff + Soli Milderungszone + contribution ceilings |
| L40 | Book a rental repair in the high-income year | §§ 11 (2), 21, 2 (3) | a | 20 000 € Erhaltungsaufwand; incomes 120k / 30k | 57 645 | 50 584 | **7 061** | deduction at 44,3 % instead of ~25 % (timing via payment date, § 11 (2)) |
| L41 | Hold crypto/gold more than one year | § 23 (1) Nr. 2, (3) Satz 5 | b | 60 000 € wages, 5 000 € gain | 24 261 | 22 500 | 1 761 | private sale tax-free after 1 year; below 1 000 € Freigrenze also free (cliff, NOVEL.md) |
| L42 | Claim the Behinderten-Pauschbetrag | § 33b (3) | b | 45 000 €, GdB 50 (1 140 €) | 15 398 | 15 057 | 341 | flat allowance without receipts |

## (c) Out of scope (one line each)

| ID | Technique | Source | Why out |
|---|---|---|---|
| C01 | Faktorverfahren | § 39f | withholding only; the PAP interface has no factor input; final tax as L02 |
| C02 | Kirchensteuer-Kappung (2,75-4 % of zvE on application) | KiStG der Länder | Land-level rules, discretionary (Erlass) |
| C03 | Kirchgeld / glaubensverschiedene Ehe | KiStG der Länder | model applies KiSt to the whole household |
| C04 | Investitionsabzugsbetrag | § 7g | business accounts, multi-year |
| C05 | Thesaurierungsbegünstigung | § 34a | business, multi-year |
| C06 | GmbH / holding (Teileinkünfte, § 8b KStG) | § 3 Nr. 40, KStG | corporate level |
| C07 | Gewerbesteuer-Anrechnung | § 35 | Gewerbesteuer not modelled |
| C08 | Denkmal-/Sanierungsgebiet-AfA | §§ 7h, 7i, 10f | multi-year depreciation |
| C09 | Sonder-AfA Mietwohnungsneubau | § 7b | multi-year depreciation |
| C10 | Energetische Sanierung | § 35c | 3-year credit, building data |
| C11 | Kettenschenkung, Nießbrauch, Familienheim | ErbStG §§ 13, 16 | Erbschaftsteuer |
| C12 | Selbstgenutzte Immobilie sale tax-free | § 23 (1) Nr. 1 Satz 3 | multi-year holding history |
| C13 | Verlustrücktrag / -vortrag | § 10d | multi-year (within-year timing: L40) |
| C14 | Aktienverlust-Verrechnungstopf | § 20 (6) Satz 4 | one capital-income line, no loss pots |
| C15 | Altbestand funds (pre-2009) | InvStG § 56 (6) | historical holdings |
| C16 | Kapitallebensversicherung half-taxation (12 years, 62) | § 20 (1) Nr. 6 Satz 2 | multi-year contract |
| C17 | PKV Beitragsvorauszahlung (2,5 × annual) | § 10 (1) Nr. 3 Satz 4 | private health insurance not modelled |
| C18 | Werkstudentenprivileg | SGB V § 6 (1) Nr. 3; SGB III § 27 (4) | SV status not modelled |
| C19 | Dienstwagen / E-Auto 0,25 % | § 6 (1) Nr. 4 Satz 2 | needs vehicle cost and private-use valuation |
| C20 | Kindergeld for children 18-24 in a second education | § 32 (4) Satz 2, 3 | child status rules not modelled |
| C21 | Rentenbeginn timing (Besteuerungsanteil) | § 22 Nr. 1 Satz 3 a aa | model fixes the start at 65 |
| C22 | Arbeitnehmersparzulage / Wohnungsbauprämie | VermBG, WoPG | outside the EStG assessment |

**Counts**: 63 techniques catalogued: 41 recreated (26 (a), 15 (b); 44 result rows incl. variants and the L36b trap), 22 out of scope (c).
