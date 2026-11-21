# Norway (Oslo), income year 2025: findings

Model: `lean/NOTax` on the shared kernel `TaxKernel` (Schedule, Rounding, Allowance, Credit parts), exe `notax`
(contract JSONL). Parameters and sources: `refs/PARAMS.md` (P1-P26). Theorems: `lean/NOTax/Theorems.lean` (no
`sorry`). Runs: `runs/`. Harness: `harness/` (`oecd_check.py`, `trekkrutine2025.py`, `table_vs_statute.py`,
`worked_examples.py`, `scan_metr.py`, `scan_owner.py`, `scan_couples.py`, `xref_check.py`). Known-loophole
catalogue: `CATALOGUE.md`.

## Validation (summary; details in `runs/*.json`)

| Referee | Cases | Agreement | Notes |
|---|---|---|---|
| OECD Taxing Wages 2025, NOR, 8 family types × 6 lines (CGTC, CGITFP, SLT, EECSSC, CTGG, THP) | 48 | 48 within 1 %; 45 within 5 NOK; 24 below 1 NOK; largest gap 6.3 NOK (THP of a two-earner couple) | Every gap is the statute's round-down of each tax to the krone (skattebetalingsforskriften § 10-4-4) against the OECD's unrounded figures and fractional wages. Same 2025 parameters (the OECD splits the 22 % into 6.6 % central + 15.4 % local, as SV 2025 §§ 3-2, 3-8 do; standard allowance STA 200 550 = 92 000 + 108 550). No OECD error found. |
| Official worked examples and published figures (Skatteetaten satser 2025: 37.84 % on gains, dividends and losses; maximum marginal rates 47.4 / 44.8 / 50.6 / 47.8 %; skjermingsrente 3.6 % and 4.6 %; trekkrutine test value 144 003; OECD STA) | 11 | 11 exact | `runs/worked_examples.json` |
| Skatteetaten's open withholding code (github.com/Skatteetaten/trekktabell, 2025 commit aeaaf08), ported to Python | 909 996 published table rows | 909 996 exact | The port reproduces Skatteetaten's published 2025 table file row for row: tables 8000-8400 and 9010-9110 (576 496 rows) and 9120-9400 (333 500 rows, see F2) |
| The withholding tables against the statute (table 8000, monthly bases 0-200 000 by 100) | 2 001 | 150 within 2 NOK, 1 457 within 1 %, 0 under-withheld | All differences are the tables' reduced minstefradrag (F1); after removing it the residual is within 5 NOK except where the statute's base floors at 0 |

## Government publications and the statute

### F1 The withholding tables deduct only 88 % of the minstefradrag: about 2 430 NOK a year over-withheld from every employee above 200 000
- kind: gov-error (classification: convention: deliberate in the code, no reason given in the routine or its README)
- households: any employee on table 8000 (the 2025 base table) with annual pay of 200 000 or more; e.g. at the OECD average wage (annualised base 801 738): statute 225 472, table 227 904.
- amounts: the trekkrutine's `Konstanter` use `ANV_MINSTE_FRAD_PROSENT = 40.48` and `MAX_ANV_MINSTE_FRADRAG = 80960`, i.e. 88 % of the statutory 46 % and 92 000 (sktl. § 6-32 (1) a; SV 2025 § 6-1). From 200 000 the deduction is 11 040 NOK short; 22 % of that = 2 428.80 NOK more tax withheld a year (measured 2 426-2 434 NOK). The same 0.88 ratio appears every year in the git history since 2016 (e.g. 39.6 % of 45 % in 2019).
- provisions: sktl. § 6-32; SV 2025 § 6-1; Skatteetaten trekkrutine 2025 `Konstanter.java`, `Fradrag.java`.
- Lean: `table_minst_le` (from 28 NOK of income the table's deduction is never larger than the statute's), `table_minst_gap` (exactly 11 040 NOK smaller from 200 000), `table_overwithholding`.
- status: certain (code + statute + proofs). The tables never under-withhold an ordinary employee (0 of 2 001 bases). Withholding is a prepayment, so the excess comes back at assessment; the cost is an interest-free loan to the state.

### F2 The open 2025 withholding code cannot produce 36 of the published 2025 tables
- kind: gov-error (omission in public code)
- detail: Skatteetaten's published 2025 table file (`alleTabelleneIEnFilTilSkatteetatenNo.txt`, linked from skatteetaten.no/satser/trekktabeller-i-tekstformat) holds tables 0100, 0101, 6300, 6350, 6500, 6550, 6700, 7150, 7160, 7170, 7300, 7350, 7500, 7550, 7700, 8000-8400 and 9010-9400. The 2025 code (`Tabellnummer.java`) defines 8000-8400, 9010-9110, 6500, 6550, 6700, 0100, 0101, 7150, 7160, 7170 only: 9120-9400 (29 tables) and 6300, 6350, 7300, 7350, 7500, 7550, 7700 (7 tables) are missing. For 9120-9400 the published values follow the code's formula with table additions of 120 000-400 000 NOK (333 500 rows, 0 mismatches), so the code is incomplete rather than different; the other seven cannot be checked.
- Draft issue text (NOT filed): `drafts/ISSUE_trekktabell_2025.md`.
- status: certain.

### F3 Skatteetaten's 2025 maximum-marginal-rate page cites a stale trygdeavgift rate (11.1 % instead of 10.9 %)
- kind: gov-error (text)
- source: skatteetaten.no/satser/maksimale-effektive-marginale-skattesatser/?year=2025, footnote **: "differansen mellom 7,7 prosent og 11,1 prosent trygdeavgift". The 2025 high rate is 10.9 % (TA 2025 § 8 "med 10,9 pst."; Skatteetaten's trygdeavgift page 2025 "Annen næringsinntekt 10,9 %"), and the same page's 50.6 % for business income is 22 + 17.7 + 10.9.
- status: certain; cosmetic (the headline rate is right).

### F4 The same page omits the 55 % band of the low-income limit (§ 17-1) for pension recipients
- kind: gov-error (classification: reading: the page may intend top-of-scale rates, but it does list the 47.8 % low-income band of the pension credit)
- households: a pension recipient outside the § 16-1 credit (e.g. aged 64 with an early occupational or survivor's pension; `scan_metr.py` "pension64"): from about 230 600 to 318 000 NOK of pension each extra krone costs 55 øre (sktl. § 17-1 (2): "ikke utgjøre mer enn 55 prosent av overstigende beløp"), above the 44.8 % / 47.8 % the page gives for pensions.
- status: certain for the statute; whether the page meant to cover it is a reading.

### F5 sktl. § 10-12 (1) points to the wrong paragraph of § 10-11 since 2015
- kind: statute-fault (reference not updated after renumbering)
- text: § 10-12 (1) 5th sentence (written by Lov 10. des 2004 nr. 77, aksjonærmodellen): "Fremføringsretten omfatter ikke skjermingsfradrag som ikke er benyttet som følge av at utbyttet er fritatt for skatteplikt etter § 10-11 syvende ledd."
- history (Lovdata LTI texts, read): Lov 6. juni 2003 nr. 36 inserted § 10-11 (3) ("Nåværende tredje til syvende ledd blir fjerde til åttende ledd"); Lov 18. des 2015 nr. 115 III inserted new (4)-(6) on credit to shareholders ("Nåværende fjerde til åttende ledd blir syvende til nytt ellevte ledd") and did not touch § 10-12. Today § 10-11 (7) reads "Som innbetalt aksjekapital ... regnes ikke aksjer som er utstedt ved forhøyelse av aksjekapitalen uten nytegning" (no exemption). The only exemption-like rule in § 10-11 is (11) (small samvirke distributions that "ikke skal skattlegges som utbytte"), the 8th paragraph before 2015. Whatever the 2004 target was, it moved three places in 2015.
- effect: small (the carry-forward exclusion only matters for exempt distributions), but the sentence now cites a rule that exempts nothing.
- method: the Global law record holds skatteloven as one consolidated version (2026-07-01), so provision_history could not be used; we read the amending laws on Lovdata (LTI). A search of all Norwegian acts in Global law finds no other reference to a § 10-11 paragraph above the third.
- status: certain that the reference is stale; which paragraph was meant is a reading.

### F6 The lists of "oppjustering" exclusions were not updated when § 5-22 got one in 2021
- kind: statute-fault (list not updated when a category was added)
- text: sktl. § 17-1 (6) and § 16-21: "medtas ikke oppjustering etter § 10-11, § 10-21, § 10-31, § 10-42 og § 10-44". Lov 21. des 2020 nr. 164 added § 5-22 (2) 3rd sentence ("Skattepliktig inntekt etter denne bestemmelsen skal oppjusteres med 1,44", now 1,72) from income year 2021. SV 2025 § 3-2 (3) lists § 5-22 among the upjusted owner incomes; the two lists in the act do not.
- effect: for the low-income limit (§ 17-1) and the foreign-tax-credit computation (§ 16-21), excess interest on a personal shareholder's loan to his company counts with its 72 % upjustment, unlike every other owner income.
- method: `harness/xref_check.py` lists every "oppjusteres" sentence in the act (§§ 5-22, 10-11, 10-21 ×2, 10-31 ×2, 10-42, 10-44).
- status: certain.

### F7 Dead references to repealed særfradrag provisions
- kind: statute-fault (minor; lists not updated)
- § 6-3 ("særfradrag etter §§ 6-80 til 6-85") and § 6-90 ("særfradrag etter §§ 6-80 til 6-83") cite ranges in which § 6-80 (repealed by Lov 20. des 2022 nr. 105, in force 1 March 2023), § 6-81 (from 2015), § 6-83 (from 2012) and § 6-84 (from 2011) are repealed; only § 6-82 and § 6-85 remain. No effect on tax. Found by `xref_check.py` (4 references to repealed targets in the act; one is F8, one a note).
- status: certain.

### F8 Lovdata links "samme lov §§ 3-5 og 3-6" in sktl. § 5-15 to skatteloven § 3-6 (repealed)
- kind: gov-error (publisher markup)
- the sentence refers to skadeserstatningsloven; Lovdata's consolidated text links "3-6" to `lov/1999-03-26-14/§3-6` (skatteloven, opphevet).
- status: certain (Lovdata public data gjeldende-lover, 2026-11).

### F9 The 2025 low-income limits were raised retroactively in December 2025
- kind: statute-fault (amount set too low and corrected after the year)
- SV 2025 § 6-4 originally fixed 147 450 / 135 550 / 271 100 NOK (Lovdata LTI FOR-2024-12-13-3203); FOR-2025-12-18-2746 (Innst. 3 S (2025–2026) II) raised them by 10 000 / 10 000 / 20 000 "fra inntektsåret 2025". Prepayments during 2025 used the old limits. The reason is given in Prop. 1 LS (2025–2026) point 3.2.6, which we could not read (regjeringen.no is behind bot protection). The model uses the amended amounts.
- status: the amendment is certain; its cause is not verified.

## Loopholes and traps

### F10 A sole trader earning 108 550-176 684 NOK pays 47 % on each extra krone (more than in trinn 3)
- kind: loophole-new (a METR band, a trap rather than a saving)
- households: single sole trader (enkeltpersonforetak), business profit 108 550-176 684 NOK, no other income.
- mechanism: business income gets no minstefradrag (sktl. § 6-32 covers wages and pensions), so alminnelig inntekt passes the personfradrag (108 550) at once, while the trygdeavgift is still in its 25 % phase-in (ftrl. § 23-3 (4)) until 10.9 % × S = 25 % × (S − 99 650), i.e. S = 176 684. Each krone: 25 øre trygdeavgift + 22 øre tax = 47 %, above the 46.5 % on business income in trinn 3 (697 150-942 400) and 3.6 points above an employee's highest rate below 942 400 (43.4 %). An employee never meets the overlap: the minstefradrag keeps alminnelig inntekt below the personfradrag until about 201 000 NOK, after the phase-in ends at 144 003.
- Lean: `soleTrader_band` (each krone in the band costs exactly 4 700 ticks = 47 øre, for every profit in the band), `ta_soleTrader`, `grunnlag_soleTrader`; scan `runs/scan_metr.json` (business 0.47 from 109 000 to 176 000).
- novelty: the government notes that the marginal-tax difference for sole traders matters most at low returns to labour (regjeringen faktaark enkeltpersonforetak, seen as a search snippet), but the 47 % band itself was not found in 5 sources searched (Skatteetaten satser maksimale-effektive-marginale-skattesatser and trygdeavgift 2025; Innst. 3 S (2024–2025); regjeringen skattesatser pages; NOU 2026: 9 ch. 8 listing).

### F11 Owner-manager: wages up to the trinn 4 threshold (942 400), dividends above
- kind: loophole-known (recreated blind by the income-type scan)
- households: sole owner of an AS in Oslo, profit before pay 0.3-5.0 MNOK, no skjerming.
- result (`scan_owner.py`): all-wage is best up to about 1.1 MNOK of profit; above that the best wage is 942 000 (grid 2 000) for every profit; gain against all-wage 6 399 (1.5 M), 29 289 (2.5 M), 88 912 (5 M); against all-dividend about 110 000.
- Lean: `dividend_route` (51.52 % = 22 % + 78 % × 37.84 %), `wage_route_top` (53.90 % with 14.1 % arbeidsgiveravgift), `wage_route_trinn3` (50.39 % < 51.52 %), `wage_route_trinn4` (53.02 % > 51.52 %).
- sources: Skatteetaten satser 2025 (51.5 % and 53.9 %); Alstadsæter (2006) SSB DP 474; Thoresen & Alstadsæter (2010) FinanzArchiv / CESifo WP 2273; Alstadsæter, Kopczuk & Telle, SSB DP 764 / NBER w19609.
- not modelled: wages also earn folketrygd pension and sickness rights, which favour wages.

### F12 Capital income owned by a spouse with an unused personfradrag
- kind: loophole-known (recreated)
- married, wages 800 000 and 0, interest 300 000: deposits in the second spouse's name save 23 883 NOK (22 % × 108 550); with the second spouse at 150 000 of wages 6 063; at 400 000 nothing.
- Lean: `capital_shift_neutral` (above the personfradrag, moving capital income between spouses changes nothing but rounding).
- provisions: sktl. § 2-11 (1), § 15-4.

### F13 A spouse working in the other's sole proprietorship (§ 2-11 (2))
- kind: loophole-known (recreated): profit split 50/50 with a working spouse saves 34 340 (600 k), 65 722 (1 M), 119 863 (1.5 M), 144 621 (3 M) (trinnskatt progression and a second personfradrag); requires real work ("svarer til arbeidsinnsats"). Lean: `trinn_convex`, `trinn_separate_le_joint`.

### F14 Foreldrefradrag claimed by the spouse who can use it (§ 6-48 (3))
- kind: loophole-known (recreated): 40 000 childcare costs, second spouse without income: all on the earner saves 4 400 against the default half-each split.

### F15 Spreading income over two years
- kind: loophole-known (recreated): 1.6 MNOK of wages over two years instead of one saves 144 103 (two personfradrag, two minstefradrag, trinnskatt progression); 800 000: 64 834.

### F16 Living together costs a single parent the utvidet barnetrygd
- kind: loophole-known (recreated): a single parent of two (500 000 wages) who marries or moves in with a 500 000 earner loses 30 192 NOK a year (2 516 a month; nav.no).

### F17 Holding company (fritaksmetoden)
- kind: loophole-known (rate only; not in the household model): dividends into a holding company are taxed 22 % × 3 % = 0.66 % (sktl. § 2-38 (6)) against 37.84 % personally (`holding_vs_personal`); personal tax waits until paid out. Holding companies quadrupled after the 2006 reform (Berzins, Bøhren & Stacescu, ECGI working paper).

### F18 Gifts to charity below 500 NOK per giver earn nothing; a couple should give from one spouse
- kind: loophole-new (minor; follows directly from the wording; not searched for in the literature)
- sktl. § 6-50 (5): "bare når gaven utgjør minst 500 kroner". A couple giving 900 split equally (450 each, the contract's default) gets no deduction; from one spouse, 900 is deducted: 197 NOK less tax.

### F19 Separate round-down of five taxes: one more krone can cost up to 4 NOK
- kind: model-fix (a reading of skattebetalingsforskriften § 10-4-4 "avrundes beløpet ned til nærmeste hele krone")
- if municipal, county, fellesskatt, trinnskatt and trygdeavgift are each rounded down (our reading), a 1-krone raise costs 2-4 NOK in 76 410 of 1.5 million steps (`runs/scan_metr.json`); rounding the total would cap it at 1 NOK. Harmless in money; the regulation does not say which "krav" is rounded.

### F20 BSU and pension credits are lost where tax is low
- kind: loophole-known (recreated): the BSU credit (§ 16-10 (4), limited to the tax, no carry-forward) is wasted below about 118 000 NOK of wages (used: 0 at 80 000, 87 at 100 000, the full 2 750 at 120 000); the pension credit is wasted where tax is below 36 000 (pensions below about 276 000).

### F21 The pension credit ignores wages, and trygdeavgift falls after 69
- kind: loophole-known (recreated): pension 300 000 at 70, with or without 1 MNOK of wages: credit 32 059 in both (§ 16-1 (3) tapers on pension income only; Skatteetaten 2025: "Arbeidsinntekt ... inngår ikke i beregningsgrunnlaget"). 600 000 of wages at 70 pays 15 600 less than at 69 (5.1 % instead of 7.7 %, ftrl. § 23-3 (2) nr. 1 c).

## Model notes

### F22 The Global law record holds the 2026 text of skatteloven, not 2025
- kind: model-fix
- one consolidated version per act (skatteloven as in force 2026-07-01). Its § 6-47 (1) d (IPS cap 25 000) and § 16-1 (3) (taper 19.1 %) are 2026 law; 2025 had 15 000 and 16.7 %. With 19.1 % the pension-credit band would read 50.2 % instead of Skatteetaten's 47.8 % (worked example 7). 2025 values from SV 2025 and Skatteetaten's 2025 pages (PARAMS P13, P15).
