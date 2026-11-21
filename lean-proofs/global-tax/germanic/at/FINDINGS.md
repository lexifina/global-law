# Austria (Veranlagung 2025): findings

Model: `lean/` (lib `AtTax`, exe `attax`, on `TaxKernel`). Amounts in euros. Statute texts: `law/` (RIS consolidated
"Fassung vom 01.07.2025", plus 2005, 2010, 2024-07-01, 2025-01-01 and 2026-01-01 versions for history). Runs:
`results/`, `runs/`. Lean names refer to `lean/AtTax/Theorems.lean` unless stated. Kinds as in CONTRACT20.

## Validation and conventions

### F1 The model reproduces the OECD's Austrian Taxing Wages 2025 lines to the euro, except family benefits
- kind: model-fix (validation)
- households: the eight OECD types at the OECD AW 63 053,95 € (family `check.py`, wages rounded to the euro)
- amounts: 48/56 lines within 1 €; every CGTC, CGITLETC, CGITFP, EECSSC, SLT line within 1 € (taxable income incl.
  the 13th/14th salary after SV; tariff tax 9 252,33 € + 6 % on the sonstige Bezüge 411,01 € = 9 663,34 € at S100;
  SP67's refundable −1 015,70 €). With `--oecd` (F2): 55/56 within 1 €, 56/56 within 1 % (`results/oecd_check_oecdconv.md`).
- provisions: EStG § 33, § 67 Abs. 1, § 16 Abs. 3; ASVG § 51, § 54; AMPFG § 2; AKG § 61; WBFG 2018 § 2; FLAG § 8
- status: done. The OECD pays the wage in 14 instalments (12 + 2 sonstige Bezüge); the model does the same by default.

### F2 The OECD pays the 6-year-old child the Familienbeihilfe of a child aged 10 or more (+285,60 €)
- kind: gov-error, classified convention (OECD Taxing Wages 2025, AUT, CTGG of SP67, M100_0, M100_100, M100_67)
- amounts: OECD 6 274,00 €; statute 5 988,40 € = 12 × (148,00 + 171,80) Familienbeihilfe (FLAG § 8 Abs. 2 Z 3 lit. b-c,
  2025 amounts per BGBl. II Nr. 314/2024) + 12 × 2 × 8,60 Geschwisterstaffel (§ 8 Abs. 3) + 2 × 121,40 Schulstartgeld
  (§ 8 Abs. 8) + 12 × 2 × 70,90 Kinderabsetzbetrag (EStG § 33 Abs. 3). 6 274,00 is reproduced exactly when both
  children get 171,80 € (the amount from "dem Kalendermonat, in dem es das 10. Lebensjahr vollendet"): the difference
  is 12 × 23,80 = 285,60 €. The OECD's household has children aged 6 and 11.
- Lean: `AtTax.familyBenefits` (option `oecd`), exe `--oecd`
- status: OECD convention or error; immaterial to taxes. Draft note to the OECD: "Taxing Wages 2025, Austria: for
  children aged 6 and 11, FLAG § 8 Abs. 2 gives 148,00 € a month for the 6-year-old (3-9 band), so CTGG is
  5 988,40 €, not 6 274,00 € (SP67, M100_0, M100_100, M100_67), unless the OECD assumes both children are 10 or older."

### F3 OECD: Familienbonus Plus 4 000 € for couples, 4 000,32 € for the single parent
- kind: gov-error (OECD, internal inconsistency, 0,32 €)
- amounts: § 33 Abs. 3a Z 1 lit. a: 166,68 € × 12 = 2 000,16 € per child. OECD CTC = 4 000,32 for SP67 but 4 000,00 for
  M100_0, M100_100, M100_67 (CGITFP 4 363,34 vs statute 4 363,02 at M100_0). Assessed tax is rounded to whole euros
  (§ 39 Abs. 3), so the assessed amounts agree.
- status: immaterial.

### F4 The BMF Brutto-Netto-Rechner agrees with the statute to the cent for employees
- kind: model-fix (validation)
- referee: the official BMF calculator (onlinerechner.haude.at/BMF-Brutto-Netto-Rechner, linked from
  bmf.gv.at/services/berechnungsprogramme.html), its own public JSON endpoint, 120 queries 2 s apart
  (`harness/bmf_grid.py`, cache `refs/bmf_bnr/`): single, one-earner couple with AVAB and Familienbonus, single parent,
  pensioner; monthly pay 300-30 000 € (14 payments).
- amounts: employees 90/90 SV to the cent and Lohnsteuer within 0,12 € (`attax --withholding`). One model fix was
  needed: contributions use the total rate on the base, rounded once per payment (18,07 % on 6 450 € = 1 165,52 €, not
  the sum of separately rounded branches).
- status: done. The calculator computes withholding: no VAB-Zuschlag, no SV-Rückerstattung, no Kindermehrbetrag (these
  come only in the Veranlagung, the model's default output).

### F5 BMF Brutto-Netto-Rechner: KV on the April 2025 pension Sonderzahlung at 6 % instead of 5,1 %
- kind: gov-error (official calculator)
- households: every pensioner (0/30 grid points to the cent; 30/30 with `--bmf-pension-april`, which charges 6 % in April)
- amounts: 0,9 % of one monthly pension: 13,50 € at 1 500 €/month, 58,05 € at the ceiling; Lohnsteuer +0,8 to +3,5 €
  through the SZ base. The calculator also caps pension KV at 6 450 € a month, which agrees in amount with the annual
  refund of ASVG § 70a (35 × 215 € × 12 = 90 300 €; the model nets that refund).
- provisions: ASVG § 73 Abs. 1 Z 1 ("5,1%", Fassung 01.01.2025; "6%" from 1 June 2025, § 809 Abs. 1 Z 2, BGBl. I
  Nr. 20/2025); § 105 Abs. 1 (Sonderzahlung "in den Monaten April bzw. Oktober")
- status: error (the April payment predates the rate change). Draft issue text: "BMF-Brutto-Netto-Rechner 2025,
  Beitragsgruppe Pensionist: the Urlaubszuschuss (April Sonderzahlung) is charged 6 % KV; § 73 Abs. 1 Z 1 ASVG gave
  5,1 % until 31 May 2025 (§ 809 Abs. 1 Z 2). Example: 1 500 € monthly pension, KV 1 192,50 € shown, 1 179,00 € due."

### F6 BMF guidance: the Kindermehrbetrag income limits for one and two children are 5 € too low
- kind: gov-error (published guidance; immaterial)
- amounts: BMF page "Familienbonus Plus" (2025) and Steuerbuch 2026 p. 42: 16 803 € (1 child, tax under 700 €),
  20 303 € (2), 23 077 € (3), 25 410 € (4). With the § 33 Abs. 1 tariff the tax reaches 700 € at 16 808 € and 1 400 € at
  20 308 €; 23 077 and 25 410 are right (tax 2 099,80 / 2 799,70 €). 2 of 4 published limits are off by 5 € (the
  Steuerbuch says "ca."). Files `refs/bmf_familienbonus-plus.txt`, `refs/steuerbuch2026_de.txt`.
- status: reading/rounding; immaterial.

### F7 § 33 Abs. 7 (Kindermehrbetrag) says "unter 700 Euro"; the BMF applies 700 € per child
- kind: statute-fault (drafting) with an administrative reading
- text: "Ergibt sich … nach Abs. 1 eine Einkommensteuer unter 700 Euro … Die Differenz zwischen 700 Euro und der
  Einkommensteuer … Dieser Betrag erhöht sich für jedes weitere Kind … um den Betrag von 700 Euro." Read literally,
  a family with two children gets 1 400 − T while T < 700 and nothing from T = 700: a 700,01 € notch per further child
  (`kmb_literal_notch`). The BMF (page and Steuerbuch) applies "Einkommensteuer unter 1.400 Euro" for two children,
  i.e. 700 n − T whenever positive, with no notch (`kmb_bmf_lipschitz`).
- status: the model follows the BMF (default); `--kmb-literal` gives the text. The statute should say "unter dem
  Betrag von 700 Euro je Kind".

### F8 13th/14th salary: Freigrenze read on the gross amount (Veranlagung has no notch, withholding does)
- kind: reading (model choice with authority)
- § 41 Abs. 4: recomputed "wenn diese sonstigen Bezüge 2 570 Euro übersteigen"; the next sentence defines the
  Bemessungsgrundlage after SV separately, and the Steuerbuch 2026 (p. 67) says SZ up to a monthly gross pay of about
  1 285 € (2 × 1 285 = 2 570) are tax-free. With the 30 % glide from 2 447 € of Bemessungsgrundlage the assessed tax is
  continuous at the Freigrenze for employees (`sz_no_notch_assessed`); withholding jumps by 90,66 €
  (`sz_notch_withheld`), refunded in the Arbeitnehmerveranlagung.

## Loopholes, cliffs, statute faults

### F9 Kindermehrbetrag partner cliff: a two-earner couple loses up to 1 400 € for one euro of the partner's pay
- kind: loophole-new (NOVEL N1)
- households: married, two children 6 and 11, the Familienbeihilfe recipient with low pay; METR scanner: total pay
  46 824 € split 60/40 (28 094 € / 18 730 €): one more euro costs 1 362 € (`results/search/metr.md`).
- provisions: § 33 Abs. 7 lit. b ("wenn … sich auch beim (Ehe)Partner … eine Einkommensteuer nach Abs. 1 unter 700
  Euro ergibt; in diesem Fall hat nur der Familienbeihilfeberechtigte Anspruch"): all-or-nothing on the *partner's* tax.
- Lean: `kmb_partner_cliff`
- status: confirmed in the statute and the BMF's description; not found in the sources searched (NOVEL).

### F10 Social-insurance notches: Geringfügigkeitsgrenze and the AV steps
- kind: loophole-known
- amounts: 551,10 € → 551,11 € a month: 83,33 € of contributions a month (`geringfuegig_notch`); a year at 14 × 551,11 €
  costs 606 € net for one euro (`runs/recreate.json` K14). AMPFG § 2a: at 2 074 / 2 262 / 2 451 € a month the employee
  AV rate steps 0 → 1 → 2 → 2,95 % on the whole base (`av_notches`, `av_net_falls`); 217-300 € a year net for one euro
  (K15; scanner notches at 29 036, 31 668, 34 314 €).
- status: known (structure of the statutes); the METR scanner finds all four blind.

### F11 Alleinverdienerabsetzbetrag cliff at 7 284 € of partner income
- kind: loophole-known
- amounts: partner pay 10 192 → 10 194 € (Einkünfte 7 283 → 7 285 €): −813 € (two children), K16; scanner: second
  earner at 10 193 €, 813 € lost.
- provisions: § 33 Abs. 4 Z 1. status: known ("Zuverdienstgrenze").

### F12 Mehrkindzuschlag: all-or-nothing at 55 000 €, a limit frozen while the benefit is indexed
- kind: statute-fault (amount not updated) + loophole-known (notch)
- amounts: three children: one euro of family Einkommen above 55 000 € costs 292,80 € a year (`mkz_notch`).
- history: FLAG § 9a Abs. 1, Fassung 2005: the limit was "das Zwölffache der Höchstbeitragsgrundlage" (dynamic);
  Fassung 2010 and 2025: "55 000 €". Twelve times the 2025 monthly ceiling would be 77 400 €. The Mehrkindzuschlag
  itself is indexed (§ 9 Anm. 1: 21,2 / 23,3 / 24,4 € for 2023-2025).

### F13 Werbungskostenpauschale 132 € unchanged since at least 2005 while the Absetzbeträge are indexed
- kind: statute-fault (amount left behind; policy)
- § 16 Abs. 3 "132 Euro" in the Fassungen 2005, 2024, 2025, 2026; § 33 Abs. 1a lists the amounts indexed under § 33a
  and does not include it; the Verkehrsabsetzbetrag went from 291 € (2005) to 487 € (2025).

### F14 Taper bands raise marginal rates above the bracket rates
- kind: loophole-known (structure), with one notable band
- VAB-Zuschlag (§ 33 Abs. 5 Z 3): 790 € over 10 319 € = +7,66 points between 19 424 € and 29 743 € of Einkommen
  (`zuschlag_step`). Erhöhter Pensionistenabsetzbetrag (§ 33 Abs. 6 Z 2): 1 476 € over 6 761 € = +21,8 points: a 51,8 %
  income-tax rate on laufende pensions of 24 196-30 957 € for a pensioner with a low-income spouse, above the 50 % rate
  of the 103 072 € band (`pabHigh_step`); measured 48 % of gross pension at 34 000 € (single pensioner 39 %, employee
  37 % at 30 000 €). Veranlagungsfreibetrag (§ 39 Abs. 5): taxable income rises by 2 € per euro between 730 and 1 460 €
  of side income (`vfb_band`).

### F15 Owner-manager: salary of about 34 000 € plus dividends; GSVG on dividends decides the gain
- kind: loophole-known (K3)
- amounts (`results/recreate.md`): profit 2 AW (126 108 €): all salary 60 289 € of taxes and contributions, all dividends
  57 526 €, best 52 334 € (salary 34 275 €: the Gewinnfreibetrag base of 33 000 € plus GSVG) if dividends are free of
  GSVG; 58 695 € if they are in the GSVG base (GSVG § 25 Abs. 1 last sentence, SVS practice). At 5 AW the gain over
  all-salary is 24 616 € (i) / 18 286 € (ii).
- provisions: KStG § 22 Abs. 1 (23 %), EStG § 27a Abs. 1 Z 2 (27,5 %; combined 44,175 %), § 22 Z 2, § 10; FLAG § 41
  Abs. 2 and 5 (DB 3,7 % on § 22 Z 2 pay), KommStG § 9 (3 %); GSVG § 25.

### F16 Kernel: contribution rates chosen by the size of the whole base
- kind: model-fix / kernel gap
- AMPFG § 2a sets the rate by the monthly base and applies it to the whole base; ASVG § 5 Abs. 2 switches all
  contributions on at 551,11 €. The kernel `Contribution` applies a `Schedule` marginally; AtTax writes `avRate` and the
  Geringfügigkeit test itself. INBOX line sent. No generic theorem fails for the tariff or the § 67 schedule.

### F17 AMPFG § 2a: the consolidated text still shows the 2018 amounts with no note of the current ones
- kind: gov-error (publication; reading)
- RIS (Fassung 01.07.2025) prints "bis 1 648 €", "1 798 €", "1 948 €" with no "Anm." of the 2025 values, unlike EStG
  § 33, FLAG § 8 or ASVG § 5; a reader must chain the Aufwertungszahlen 2019-2025 (§ 2a Abs. 2) to get 2 074 / 2 262 /
  2 451 € (`harness/ampfg_chain.py`). Classified reading/presentation, not an error in the law.
