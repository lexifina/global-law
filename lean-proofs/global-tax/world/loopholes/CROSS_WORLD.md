# Cross-country synthesis: the 159 world countries (loophole rounds L1, L1-S)

As of 2026-11-21 00:10 UTC. Round L1 found and verified the loopholes; round L1-S (strengthening, `world/loopholes/PROGRESS_STRENGTHEN.md`)
re-searched every weak 'new' and 'unclear' novelty verdict, re-read the statute behind the model-proved findings, closed
the leads and fixed two models from their statutes. Sources, all on the build server: the regional reports
`world/loopholes/AFRICA_MENA.md` (69 countries: Africa, the Middle East and the Gulf, with Israel and Türkiye) and
`world/loopholes/REST.md` (91 countries: Asia, the Americas, Europe and the Pacific, with Taiwan, Kosovo and the Holy See;
Türkiye is in both, with no confirmed loophole in either, so 159 distinct countries), the Verification sections in each
country's `FINDINGS.md`, the scans (`world/<batch>/<cc>/results/search/`), the Lean checks
(`world/loopholes/rest/lean/L1<CC>.lean`; `lean/<Pkg>/Verify.lean` in Africa and the Middle East), the search records
(`world/loopholes/rest/novelty/`, `world/loopholes/africa_mena/search/`, `world/loopholes/strengthen/search/`) and the
merged table `world/loopholes/strengthen/world_table.json` (built by `strengthen/synth.py`; this file by
`strengthen/gen_cross.py`). A finding is cited as `CC Fn` (`CC L1` for those found blind by the re-scans). Only verified
findings are used (confirmed: the amount reproduced by the model's exe and by Lean, and the provision re-read in a text
file; model-proved: reproduced, provision cited by the builder; proved: a Lean theorem). The ranked list is
`USEFUL_WORLD.md`; plain-language material for the blog and film is `BLOG_LOOPHOLES.md`. Everything about the 38 not
repeated here is in `report/CROSS38.md`, which stays valid.

**Counts now:** 151 verified loopholes in 102 countries (145 confirmed, 5 model-proved, 1 proved);
**92 new** (27 with a full recorded search including the country's own-language press, 65 searched in the
databases and practitioner sources but not the press, 0 still 'new (weak)'), **54 known** (24 of them as
instances of a documented pattern), **0 unclear**, 5 drafting faults not searched (no novelty claim). 1 withdrawn by L1-S
(model error). Round L1 had 149: 64 new, 28 known, 53 unclear.

## 1. One kernel, 159 systems

- **All 159 models are built on `TaxKernel` (world entry point 1.3/1.4)**: 21,151 Lean lines, 828 theorems, no `sorry`
  (the word appears only in twelve "(no `sorry`)" headers). Kernel parts named in the sources (a grep of identifiers, so
  indicative): a band `Schedule` in 143, the kernel's rounding in 144, contributions in about 150, the `Unit` theorems in
  125, `perPeriod` (a tax computed on each month or pay period) in 35, printed tariffs checked with `cumJumps` in 11,
  `Table` in 9, family quotients or ranked child amounts in 7, indexed units (UVT, UTM, BPC, UIT) in 3, `Surcharge` in 3,
  `Credit` in 2, and **`Taper` and `Multiplier` in none** (the 38: Taper 15, Multiplier 1).
- **That last count is the world's main finding about design.** Where the 38 withdraw allowances, credits and benefits
  with tapers (and put their highest marginal rates in the middle of the distribution), the 159 switch them off with
  steps: an exemption, rebate, deduction, surcharge or contribution that applies in full on one side of a line and not at
  all on the other. The kernel already states both facts: `Taper.amount_step` (a taper has no jump) and
  `Contribution.floor_notch` (a charge on the whole base from a threshold is a notch). The world's cliffs are the second
  theorem instantiated about 63 times; the first is the fix in every case.
- **Generic theorems that the world's findings instantiate.** `Schedule.rate_le_max`: every marginal rate above a
  schedule's top rate is a withdrawal or a step (IN F2, IN F3, GY F1, BZ F2, SM F1, DZ F2, CD F1). `Schedule.ticks_convex`
  holds for every band tariff, so the timing gains the scanners find are all cliffs, contribution ceilings or period
  taxes. `cumJumps` on printed fixed amounts finds the drafting faults (CO F1, EC-F1, LI F1, SV-F1, SV-F3, BT F1, DO F1, GW
  F1, AO F1, MZ F1, SO F1).
- **Kernel gaps the 159 exposed (written locally, by design).** Dependants defined by having no income (the spouse tests
  of pattern B); pay-period streams (a monthly final tax cannot be seen by an annual contract: `timing_monthly.py` and the
  models' own theorems, e.g. `MeTax.uneven_costs_more`, `RsTax.uneven_costs_more`, `NrTax.periodTaxCents`); employer
  classification (Azerbaijan's state, oil and private sectors, AZ F2); citizenship and residence (PW F1, F3; NR F4; FJ
  F5); several employers (FM F2, SC F1); budget-law and circular amounts outside the code (pattern I); gross versus net
  income tests (Thailand's minimum tax is on gross non-salary income, the model's input is net: TH F1 below).

## 2. What the 159 add, by region

- **Latin America (CL CO CR AR BR PE PY UY BO EC GT HN SV NI PA CU DO VE):** thresholds written in indexed units that
  switch a whole base or a whole rate. Colombia's solidarity fund takes 1 % of the whole pension base from 4 SMMLV (CO L1,
  683,280 pesos a year for one peso a month, new); Uruguay's deduction credit falls from 14 % to 8 % of all deductions one
  peso above 180 BPC (UY-F1, 13,850-30,697 pesos, new); Paraguay's IRP taxes the whole renta neta once gross income passes
  80 M (PY-F1, 6,052,000 guaraníes, new, statute re-read by L1-S); Argentina's spouse deduction is lost at the spouse's
  first peso above the exempt amount (AR L1, 406,707 to 1.6 M pesos, new); Chile's interest exemption (CL F2). Capital
  income is schedular almost everywhere (5-10 %). Brazil's simplified discount makes the first two children worthless to a
  one-earner family (BR F2, known); Costa Rica's salaried and self-employed exempt amounts differ by 6.97 M colones (CR F2,
  known and contested); a Colombian employee gets both dependant reliefs for a child where an independent worker gets one
  (CO F3, confirmed by L1-S from DIAN's own doctrine, known).
- **Caribbean and Pacific (Commonwealth PAYE, Compact states):** drafting holes and stale law. Belize taxes exactly
  BZ$29,000 at 25 % with no deduction (BZ F1, 7,250 dollars, new); Trinidad's low-income relief is a saw-tooth calibrated
  to a repealed scale (TT F1, up to 1,090 TTD for one dollar, new); Palau's citizen refund ends at $15,000 (PW F1, $1,180,
  new (no press search)); the Marshall Islands' exemption ends at one cent (MH F2: **known**, the IMF's 2025 technical-assistance report
  describes the notch and its $666 cost, read by L1-S) and Micronesia's at one dollar (FM F1); FSM's social-security ceiling
  is per employer (FM F2); Nauru's employment tax is final per pay period (NR F1, F2); Suriname taxes overtime on request at
  its own 5-25 % scale (SR F2, confirmed by L1-S). Six of these states publish their rates outside the consolidated law
  (Grenada, Tonga, Guyana, Saint Vincent, Dominica, Barbados).
- **South Asia (PK BD LK NP BT MV AF IN):** surcharges, minimum taxes and tests on the whole income or tax, the design
  Kleven and Waseem studied in Pakistan in 2013 and that is still there: PK F1 (241,290 rupees at 10 M, new), PK F2
  (1,258,000 at 5 M of bank profit, known; s. 7B (3) (b) re-read by L1-S), PK F3 (384,000 at the 75 % salary test, known),
  PK F6 (1.5 M at 150 M), BT F2 (100,001 ngultrum; repealed for 2026), BD F1 (5,000 taka). India's s. 87A relief plus cess
  (IN F2, 104 %, known); Nepal's women's rebate lost with one rupee of other income (NP F1, new (no press search); text re-read in the Kalimati
  file); pensions at 0 % to 10 M in Pakistan (PK F5); Afghanistan's monthly withholding is final for single-employer
  employees (AF F2, confirmed by L1-S: art. 63 (1) requires a return only with a second employer or other income).
- **East and South-east Asia (CN TW KH LA MM TL MN VN TH PH ID SG MY KP):** spouse and rebate cliffs (KH F1, SG F1, MY F1,
  MM F1), a two-zero-band split between wages and fees (TL F1, new), stepped credits (MN F1), China's child-deduction
  allocation (CN W5R-1) and business-income deduction (CN F1). Thailand's 0.5 % minimum tax is **not** a notch at 120,000:
  Royal Decree 480 exempts it up to 5,000 baht (TH F1 withdrawn, model fixed by L1-S).
- **Former USSR (UA BY MD GE AM AZ KZ KG TJ TM UZ):** flat taxes whose only progressivity is a deduction limited by income,
  so the limit is a notch (MD F1, known; BY F1; UA F1, new, doubled for parents of two); Armenia's stamp duty by band
  (AM F1) and its cohort-based pension payment (AM F2, known); Azerbaijan's sector rule (AZ F2, known: 11,700 manat on 60,000 of
  wages by employer class, ended 2025). Dividends exempt or at 5 % (KZ, KG, GE, UZ).
- **Western Balkans and European microstates (AL BA XK ME MK RS AD LI SM MC VA):** deduction steps and spouse tests (AL F1,
  BA F1, SM F2), monthly final taxes (ME F3, RS F1); Liechtenstein and Andorra are smooth (full splitting, proved). Albania's
  first notch (50,000 lek a month) became the minimum wage on 1 January 2026.
- **Africa and the Middle East (69; AFRICA_MENA.md):** the spouse 'sans revenu' trap in every legal family (BF, NE, SN, TG,
  LB, MU, GH), flat levies and minimum taxes from the first unit of pay (TD, MG, CD, CI, KE, CM, SN, BJ, AE), tables with
  inconsistent fixed amounts (GW, AO, MZ, SO), whole-income column tariffs (EG F1, LY F2, MA F1, TN F1, DZ F1), monthly
  final withholding (MR, GN, DJ, RW, ET, SC), the French quotient's marriage bonuses and penalties (CG, CI, GA, NE, CV) and
  schedular capital income (BW, NA, SZ, JO, CM, CF; Chad the reverse, TD F1). Algeria's rent notch is 175,799 dinars, not
  310,799 (DZ F1: L1-S applied the art. 85 abatement of 25 % that the model had left out).

## 3. Which design features cause which loopholes (all 159)

Verified loopholes with money: **151** in 102 countries. By type: **notch or cliff 63** (in 53 countries), income-type gap
39, household unit or claimant 18, second-earner trap 12, timing or bunching 11, rate above the top rate or 100 % band
6, rule set outside the law 2.

**A. One unit crosses a line and a whole relief, base or rate changes (63 notches in 53 countries).**
The commonest design of the world's personal income taxes. Exemptions and rebates limited by income (MD F1, BY F1, UA F1,
MY F1, MM F1, AL F1, SM F2, UY-F1, SV-F2, FM F1, MH F2, PW F1, TN F1, MA F1, CG F2), surcharges and minimum taxes on the
whole tax (PK F1, PK F6, BT F2, BD F1, BD F2, MG F1, CD L1, TD F3), thresholds that move a whole income onto the scale
(PY-F1, PK F2, PK F3, CL F2, FJ F2, DZ F1, GW F3, TG F2), column tariffs (EG F1, LY F2). Largest per unit: Pakistan's
bank-profit test (1,258,000 rupees), Paraguay's IRP (6,052,000 guaraníes), Algeria's rent test (175,799 dinars after
L1-S's correction), Belize's 29,000 (7,250 dollars). The fix is the kernel's: a taper of the same cost (`Taper.amount_step`).
Thailand's minimum tax left this list: the royal decree that exempts it to 5,000 baht was read (section 7).

**B. A dependant spouse is defined by having no income (12 second-earner traps, in every legal family).** MU F2, AR L1, SN F2, LB F1, LC F2, SG F1, BA F1, NE F4, KH F1, BF F2, TG F1, GH F2.
The earner loses the relief at the spouse's first riel, mark, peso, franc, lira, rupee or cedi; the 38 had the same in LV,
SI, HR, RO. Three of the strongest new findings are of this kind (AR L1, LB F1, SN F2), each re-searched in its own language.

**C. Contributions and levies charged on the whole base from a threshold, and floors on any positive wage.** CO L1, TT F2,
KN F1, VU F1, UY-F2, AM F1, MU F1 (CSG), CM F1, SN F1, BJ F1, AE F1; floors: CI F2, KE F1, AE F3, TD F3, MG F1, CD L1.
Contribution **ceilings** produce most of the scanners' timing leads (CL, TR, SG, BR, VN, PH, BS, AG, MC; KW, OM, SA):
explained, not loopholes of the tax, but they make the combined schedule regressive at the top (TR, KZ, AM, MN, AL).

**D. Tables and clauses that contradict themselves.** Belize's 29,000 in neither clause (BZ F1), Trinidad's saw-tooth (TT
F1), Bhutan's 242,499 (BT F1), Guinea-Bissau's 14 % row that subtracts 16,020 F a month too much (GW F1: a windfall of
192,240 F a year to everyone above 400,500 F a month), Angola's two notches (AO F1), Mozambique's gazette and code
disagreeing by 1,000 MT (MZ F1), Somalia's $1,788 for $1,728 (SO F1), El Salvador's fixed amounts (SV-F1, F3), the slab
readings of SB F1, TV F1, SS F1, India's s. 16 (ia) pointing at a superseded clause (IN F1: known and cured by Parliament
in August 2025, closed by L1-S). Concentrated in Portuguese-model tables and in small Commonwealth states.

**E. The same income taxed differently by type (39 income-type gaps).** Dividends exempt or final at 0-20 % beside
progressive wage scales in most of the 159 (FJ F3, TO F3, WS F4, MV F1, KZ F2, KG F2, LK F1, PK F7, CN F2, RU F2, BW F2,
NA F1, SZ F4, CM F4, CF F3, JO F3: known, the owner-manager and dual-income patterns); employees against the self-employed
(CR F2, CN F1, FM F3, ZW F2, MW F1: known, the OECD's 2019 'choice of employment form' pattern; TL F1 and YE F2 are new
because the gain comes from combining the two forms, each with its own zero band); pensions (PK F5); allowances (BI F1);
overtime at its own scale (SR F2, GY F3). Chad's 2023 law reverses the owner-manager pattern: dividends 20 %, salary at
most 18 % (TD F1).

**F. Period taxes without an annual reconciliation (11 timing findings).** Monthly or per-pay-period final taxes make
bunched pay cost more: NR F1, DJ F1, AF F2, ME F3, SC F1, MR F2, RS F1, RW F1, GN F1, ET F3, NR F2. Francophone Sahel and Horn, East-African PAYE, the Balkans, Nauru and
Afghanistan. The 38 had the mirror image (withholding that departs from the annual tax in 16 of 38).

**G. The unit of assessment and who claims (18).** Quotient bonuses and penalties (CG F1, CI F1, GA F1, NE F1, CV F1),
elections the default gets wrong (CN W5R-1, NP F2, BZ F3, TW F2: known, the statutes' own elections), individual
taxation's split gains (LB F5, IQ F3, JO F5), the simplified discount (BR F2), spouse credits for married couples only (CR
F3), residence by marriage (NR F4), double dependant relief for employees (CO F3).

**H. Rates above the top rate (6).** Only where a relief is withdrawn by formula: IN F2 and F3 (104 % bands), GY F1 (a
regressive top: the middle band above the top), BZ F2 (a 100 % phase-in), DZ F2 (58.7 % against 35 %), CD F1 (40 % under a
30 % cap). The 38 had about ten such bands; the 159 have few because they rarely taper.

**I. Rules set outside the law.** Rates by ministerial order or unpublished Orders (GD, TO), contribution rates set by
boards (GY), amounts in budget laws (AO, IQ, ST; BB F1's credit without an amount since 2016), administrative codes that
differ from the gazette (MZ F1), stale consolidations (FJ, VC, SR, VN, BD, LK, NR). As in the 38 (BG, CY, LV): the applied
amount is not the printed one.

## 4. Legal families

| Family | Countries (159) | Dominant loophole types | Strongest verified examples |
|---|---|---|---|
| Latin civil-law codes (Spanish, Portuguese) | 17 Latin American + CU DO | A (indexed thresholds on the whole base), C, E | CO L1, UY-F1, PY-F1, AR L1, CR F2, BR F2 |
| Commonwealth income tax acts (PAYE) | South Asia, Caribbean, Pacific, SG MY, anglophone Africa | A (surcharges, rebates, minimum taxes), D, E, I | PK F1-F6, TT F1, BZ F1, PW F1, MU F2, BW F2 |
| French-model CGI / CIDTA (quotient) | UEMOA, CEMAC, Maghreb, KM DJ MG, HT | B, C, G, F, A | LB F1 (Arabic), SN F2, CG F1, GA F1, MA F1, DZ F2 |
| Portuguese-model códigos | AO MZ CV GW ST TL | D, F | GW F1, AO F1, MZ F1, TL F1 |
| Arabic and Persian codes | EG LY JO LB SY IQ IR YE | A (column tariffs, whole income), B, E | EG F1, LY F2, LB F1, YE F2 |
| Post-Soviet tax codes | UA BY MD GE AM AZ KZ KG TJ TM UZ | A (deductions limited by income), E | MD F1, UA F1, BY F1, AM F1, AZ F2 |
| East and South-east Asian codes | CN TW KH LA MM MN VN TH PH ID | B, A, F | KH F1, MM F1, CN W5R-1, MN F1 |
| Western Balkan / microstate laws | AL BA XK ME MK RS AD LI SM | A, B, F | AL F1, BA F1, ME F3, RS F1 |
| No personal income tax (contributions only) | Gulf, BN BS AG KN MC VA VU KP | C (entry thresholds, floors, ceilings) | KN F1, VU F1, AE F1, AE F3 |

## 5. The 159 against the 38

- **Cliffs move from benefits to the tax itself.** The 38's largest cliffs were cash family benefits withdrawn at a limit
  (15 of 38, up to a month's pay); the 159's models hold almost no cash benefits, and their cliffs sit in exemptions,
  rebates, surcharges, minimum taxes and contribution entry points. Per unit of income they are as large (PK F2, PY-F1, DZ
  F1, BZ F1 each cost more than a month's average pay for one unit).
- **Few hidden bands above the top rate.** The 38's highest marginal rates sat in the middle because allowances were
  tapered (EE, LT, FI, GR, LU, SK, SI); the 159 rarely taper, so they have steps instead of bands (6 such bands against
  about ten in the 38).
- **Spouse tests are commoner.** Four of the 38 (LV, SI, HR, RO) against 12 of the 159: family relief is attached to the
  earner, not to the child, in the French, Arabic and Commonwealth traditions.
- **Owner-managers pay least through dividends in both sets** (the 38: every one of the 18; the 159: wherever a personal
  dividend rate below the wage scale is visible, i.e. most of them; Chad's reversal is the exception). The company side is
  not modelled in the 159, so the gap is the personal side only (round 2 is adding the company side: section 8).
- **The statute and the applied amount part company in both,** but in the 159 the cause is publication more than budget
  laws: consolidations years behind (FJ, SB, VC, BD, LK), rates in unpublished orders (GD, TO), tables that contradict their
  own code (GW, MZ).
- **Novelty.** Of the 151 verified loopholes, 92 are new in the sense of the records (no description of the effect found),
  54 known, 0 unclear and 5 drafting faults not searched. 'New' means 'not found in the recorded search', not 'nobody
  knows': the searches cover OpenAlex, EconBiz, Crossref (all and the IMF's DOI prefix), PwC's Worldwide Tax Summaries, the
  country's tax authority where reachable, and 39 web searches in the countries' own languages (L1 REST 15, L1 Africa 5,
  L1-S 19); Semantic Scholar was asked for every item and answered rate limits (recorded). Known effects were found
  in IMF reports (MH F2), practitioner guides and the press (IN F2, BR F2, CR F2, PK F2, PK F3, MD F1, EG F1), the tax
  authority's own doctrine (CO F3, IN F1) and PwC (AZ F2, AM F2, TW F2, CI F1, JO F5); 24 income-type gaps are counted
  known as instances of documented patterns (owner-manager shifting, dual income taxes, choice of employment form).

## 6. Needs checking

- **New without a press search (65):** CL F2, MN F1, BA F1, ME F3, RS F1, SM F2, BY F1, AM F1, AZ F1, KG F1, PK F4, PK F5, PK F6, BD F1, BD F2, NP F1, NP F3, BT F2, PY-F2, UY-F2, SV-F1, SV-F2, TT F2, BB F2, LC F2, GY F1, FJ F2, SB F1, TV F1, NR F1, NR F2, NR F4, FM F1, FM F2, PW F1, KN F1, VU F1, LY F2, MR F2, YE F2, BJ F1, BF F2, CI F2, NE F1, NE F4, SN F1, TG F1, TG F2, GW F3, CV F1, GN F1, CM F1, TD F3, CG F2, GA F1, CD L1, BI F1, DJ F1, MU F2, SC F1, MZ F1, GH F2, RW F1, ET F3, AE F3.
  Their record is OpenAlex, EconBiz, Crossref (and the IMF prefix) and PwC, without a web search in the country's language
  (the L1-S budget of 20 went to the findings most likely to be cited). Cite them as 'not found in the recorded search'.
  'New (weak)', Crossref only: 0.
- **Unclear (0):** none.
- **Model-proved, statute not re-located (5):** RU F2, KG F2, LK F1, UY-F3, TV F1: the amounts are reproduced by exe and Lean, the
  provision is the builder's citation. Mostly income-type gaps of known patterns; none is used in BLOG_LOOPHOLES.md.
- **Readings that move an edge.** AR L1 ('ingresos netos' before or after the spouse's own contributions), KH F1 (a
  homemaker who earns a little), SB F1 and TV F1 (slab vs graduated), MH F1 (which 2025 schedule ran when), KN F1 (the
  2025 threshold weighted by half-year), BB F2 (the 'prescribed rate' was never found: the 500 BBD shown uses an assumed
  5 %), PW F2 (whether non-wage income counts toward $15,000), GH F2 (the relief may now be GH¢1,200, not 200: the
  Africa round's lead).
- **Leads still open in Africa and the Middle East:** 35 (AFRICA_MENA.md 'Per country'), e.g. CI F2's SMIG, GM F1. REST's
  12 leads are closed (section 7).
- **No current scan:** KG, TM, UZ, VE (no cited reference wage), ER, GM (tier-C stubs), VC, KI (no model). Their findings
  are checked on the exe only.
- **Laws changed after the model year (2025):** Pakistan abolished the salaried surcharge for 2026-27 (PK F1); Bhutan's
  2025 Act drops the surcharge from 2026 (BT F2); Congo replaces the IRPP from 2026 (CG F1); the DRC's IPR is to become an
  IRPP (Law 23/053; CD F1); Albania's minimum wage moved onto the 50,000-lek notch (AL F1); Azerbaijan's private-sector
  zero rate ended in 2025 (AZ F2). The findings are 2025 law.
- **Company side.** No company tax in the 159's models: every owner-manager gap is the personal side only (round 2).

## 7. Round L1-S: what the strengthening pass changed

- **Two model errors fixed from the statute** (provision cited, #guards, rebuilt): **TH F1 withdrawn** (Royal Decree 480
  s. 3 exempts the s. 48 (2) minimum tax up to 5,000 baht; `ThTax.minTax`) and **DZ F1 corrected** (CIDTA art. 85 as
  rewritten by LF 2022 art. 28 gives residential rents a 25 % abatement in the global base: 175,799 DA, not 310,799;
  `DzTax.rentIRG`, Verify regenerated). Backups in `strengthen/backup/`.
- **Statute re-read for 30 model-proved findings, now confirmed:** PY-F1, PY-F2, PK F2, PK F7, RU F1, GE F2, AZ F2, KG F1, UZ F1, MV F1, BD F2, BT F2, NP F1, NP F2, NP F3, LC F2, GY F1, GY F3, BZ F2, UY-F2, NR F1, FM F3, RS F1, BO-F3, PE-F2, SV-F1, SV-F3, ID F2, WS F4, WS F1.
  Texts read in image-OCR and legacy-font files where needed (Bangladesh's Finance Act 2026 OCR, Guyana's Act 2 of 2025 OCR,
  Nepal's Kalimati text, Thai, Georgian, Azerbaijani, Dhivehi and Russian originals), or fetched from the official site
  (IMPO for Uruguay's Ley 18.211, rd.go.th for the Thai decree).
- **The 12 REST leads:** CO F3 confirmed; IN F1 withdrawn; TR F3 withdrawn; TR F4 withdrawn; AL F4 withdrawn; BA F3 withdrawn; SM F3 withdrawn; BT F4 withdrawn; AF F2 confirmed; LA F4 withdrawn; HT F3 withdrawn; SR F2 confirmed.
- **The IMF report on the Marshall Islands** (Technical Assistance Report 25/022, January 2025) was read: paras. 86 and
  94-96 describe the all-or-nothing allowance and its $666 cost, so MH F2 is known.
- **Novelty re-searches:** every REST 'new (weak)' and 'unclear' item and every Africa/Middle East item without an
  OpenAlex answer has a record in `strengthen/search/` (Crossref, IMF prefix, PwC pages; Semantic Scholar asked; OpenAlex
  after its daily budget reset), and 19 web searches went to the items most likely to be cited (list in
  `strengthen/s_overrides.py`, WEB2). One world rule now classifies income-type gaps (section 5).

## 8. Round 2 (new scanners): verified items folded in

Source: `world/loopholes/ROUND2_SCANNERS.md` (the round-2 agent; its checks are in `round2/v/`). New scanners: company
arbitrage on the world models, contribution ceilings and floors, wage versus fee, splitting with a spouse, pensions,
several jobs, pay periods. As of this build it reports 11 verified items or leads (table below, copied as it stands) and
one model fix. They are listed here and not yet added to the counts above: most are instances of pattern E (each kind of
income with its own zero band or rate: KH-R1, TG-R1, AZ-R1, AO-R1, ME-R1, GW-R1, SY-R1, like TL F1 and YE F2), with novelty
records that are still Crossref-only ('new (weak)'). Its ceilings table confirms pattern C's regressive tops (43 statutory
ceilings where the combined marginal rate falls: known pattern), and its company scan adds the company side that section 5
lacked for 20 countries (dividends beat salary at 3 AW in AL, KZ, LI, TG, UA and UY with the statute employer rates).
**Model fix (statute):** AR, LIG art. 30 (c) 2: the special deduction (3.8 x MNI) was given in full to anyone with wages > 0, so one peso of wages sheltered 21.6 M ARS of self-employment income; now capped by the person's net wages (`ArTax/Basic.lean`, 2 #guards, lake build ok; LESSONS.md). Found by `mix.py` (best wage share 1 %).

Exe and Lean: `round2/verify2.py` (copy of `tools/verify.py`; specs `round2/v/spec/<CC>.json`, Lean `round2/v/lean/R2<CC>.lean`, checked with `lake env lean` in each model's folder, results `round2/v/out/`). Known/new: `round2/novelty2.py` (Crossref at 22:55 UTC; OpenAlex after its quota reset, 00:02 UTC) -> `round2/v/novelty/`, plus 3 web searches (KH, TG, GY).

| item | what | money | Lean | provision | status | known/new |
|---|---|---|---|---|---|---|
| AR (model fix) | One peso of wages gave the whole 3.8 x MNI special deduction (21.6 M ARS) to self-employment income | up to 14 % of income at 0.5 AW before the fix (mix.py) | ArTax/Basic.lean #guards (2) | LIG art. 30 (c) 2 'cuando se trate de ganancias netas comprendidas en los incisos a), b) y c) del artículo 82' (law/lig_actualizado.txt:255-259) | statute fault in the model, fixed and rebuilt | n/a (model error) |
| KH-R1 | Salary tax and the tax on a sole proprietor's income are separate taxes, each with its own 0 % band (1.5 M riel a month; 18 M a year): paying half as salary and half as business income | 14,700,000 KHR a year less on 300,000,000 (2 AW): 30.6 M vs 45.3 M either way (4.9 %) | R2KH.R1 (4 #guard) | Law on Taxation 2023 (salary tax); Sub-decree 48/2024 art. 4 bands (model citation; Khmer OCR in law/rescue/sd48_khm_ocr.txt, provision not re-located) | model-proved | new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point; web search 1 (PwC: consulting income outside salary tax and under the tax on income; both 0 % bands) found no description of the doubled band |
| TG-R1 | Wages on the art. 74 barème, business income at a flat 30 % (art. 78): wages up to where the barème passes 30 %, the rest as business income | 2,023,000 XOF a year less on 40,000,000 (4 AW) than all wages; 2,000,000 less than all business income (5 %) | R2TG.R1 (4 #guard) | CGI 2025 art. 74, art. 78 'l'impôt est déterminé par application du taux de 30%' (law/rescue2/otr_cgi_lpf_2025.txt:1650-1657) | confirmed | new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point; web search 2 found no source on the two schedules |
| AZ-R1 | Wages on the art. 101.1 progressive table (14 % / 25 % above 2,500 a month), entrepreneurs' income at 20 % (art. 101.3) | 4,152 AZN a year on 180,000 (6 AW) vs all wages (2.3 %) | R2AZ.R1 (4 #guard) | Tax Code art. 101.1, 101.3 'Hüquqi şəxs yaratmadan sahibkarlıq fəaliyyətini ... 20 faiz' (law/m101_20250701.txt:29) | confirmed | new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point; rate gap itself is published (Tax Code) |
| AO-R1 | IRT Group A (employment table) and Group B (self-employed) taxed separately | 107,952 AOA a year on 3,600,000 (1.5 AW) vs all wages (3 %) | R2AO.R1 (4 #guard) | Código do IRT, Group B arts. 8-9 (law/rescue2/angolex_2820.txt:86-182); Group B rate as the model reads it | model-proved | new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point |
| ME-R1 | Wage tax (monthly, final) and the annual self-employment tariff each run their own bands | 2,276 EUR a year on 18,000 (1 AW) vs all wages; 386 vs all self-employment | R2ME.R1 (4 #guard) | Zakon o porezu na dohodak fizičkih lica član 10 (model citation) | model-proved | new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point |
| GW-R1 | Imposto profissional on wages and the annual tax on self-employment (art. 13 / 27(2) annual column) are separate | 86,400 XOF a year on 7,200,000 (2 AW) vs all wages | R2GW.R1 (4 #guard) | Código do Imposto Profissional arts. 13, 27 (model citation) | model-proved | new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point |
| SY-R1 | Wage tax and the tax on profits (real basis) are separate scales; mixing uses both | 2,373,596 SYP a year on 40,176,000 (4 AW) vs all wages; 557,376 vs all profits | R2SY.R1 (4 #guard) | LD 30/2023 and the profits-tax scale (model citation) | model-proved | unclear: OpenAlex finds a 2025 comparison of Syria's tax on self-employment and on other income (doi 10.32978/sjp.2025.003); its abstract does not describe combining the two scales; Crossref nothing |
| DZ-R1 (lead) | Model taxes salaries (monthly IRG) and BIC (annual barème) each on its own: 106,800 DZD less on 720,000 split | 106,800 DZD in the model | R2DZ.R1 (4 #guard on the model) | CIDTA art. 104 I and II.1 (law/jo/lf2022.txt:626-655): BIC tax 'constitue un crédit d'impôt qui s'impute sur l'imposition du revenu global' | lead: likely a model simplification, statute reading needed before any fix (for the strengthening agent) | not searched as a loophole |
| GY-R2 | Second-job income up to 50,000 a month is deductible (s. 20 as replaced 2025) | 150,000 GYD a year (874,000 of second-job pay at 1 AW) | R2GY.R2 (3 #guard) | Income Tax Act Cap. 81:01 s. 20 as replaced by the 2025 amendment (model citation, GyTax/Basic.lean:10-15) | model-proved | known: Budget 2025 measure, GRA guidance (web search 3); the model does not test the full-time-primary-job condition |
| FM-R2 | Social security ceiling of US$9,000 a quarter per employer: two employers pay more on the same pay | -600 USD a year at 44,000 (4 AW) | R2FM.R2 (3 #guard) | 53 F.S.M.C. 603(15)(a), 901(1)(g) (model citation) | model-proved (a penalty, not a gain) | not searched (refund rule not read) |

## Appendix: every verified loophole, its status and novelty verdict

| finding | type | money | status | novelty | record |
|---|---|---|---|---|---|
| AE F1: ILOE premium doubles at a basic salary of AED 16,000 a month | notch | AED 60 a year | confirmed | known | `africa_mena/search/AE-F1.json` |
| AE F3: Minimum contribution salary AED 3,000 a month for Emirati pension members | notch | AED 4,020 a year on AED 12,000 of pay (33.5 %) | confirmed | new (no press search) | `strengthen/search/AE-F3.json` |
| AO F1: Two notches built into the 2025 IRT table's fixed amounts | notch | 6,000 AOA at 150,001 and 10,750 at 200,001 a month (base) | confirmed | new | `strengthen/search/AO-F1.json` |
| BF F2: The spouse's first franc ends her family charge | second | 21,959 F (5,483 with two children) at 3 M | confirmed | new (no press search) | `africa_mena/search/BF-F2.json` |
| BI F1: Transport (<= 15 %) and housing (<= 60 % of base) allowances deductible: up to 43 % of pay | itype | 754,200 BIF at 6 M | confirmed | new (no press search) | `africa_mena/search/BI-F1.json` |
| BJ F1: June ORTB levy of 3,000 F once June pay passes 60,000 | notch | 2,988 F for 12 F a year | confirmed | new (no press search) | `africa_mena/search/BJ-F1.json` |
| BW F2: Final 10 % on bank interest and dividends against wage rates to 25 % | itype | 17,500 BWP on 100,000 moved at 600,000 | confirmed | known (pattern) | `strengthen/search/BW-F2.json` |
| CD F1: A 40 % band under a 30 % cap on the whole tax: the marginal rate is 40 % between 43.2 M an | phase | 380,000 FC per 1 M FC at 60 M (38 % vs 30 %); up to about 3.5 M FC a year agains | confirmed | new | `strengthen/search/CD-F1.json` |
| CD L1: Minimum IPR of 2,000 FC a month from the first franc | notch | 23,988 FC a year for 12 FC | confirmed | new (no press search) | `africa_mena/search/CD-L1.json` |
| CF F3: Distributions at a final 15 % against wage bands | itype | 110,560 F at 10 M | confirmed | known (pattern) | `strengthen/search/CF-F3.json` |
| CG F1: A wage-earning wife is assessed alone with 2 parts while the husband keeps his parts | unit | 591,800 F at 6 M + 3 M (married vs unmarried) | confirmed | new | `strengthen/search/CG-F1.json` |
| CG F2: Nothing collected below 265,000 of income; 11,750 at the threshold | notch | 11,749 F for 1 F | confirmed | new (no press search) | `africa_mena/search/CG-F2.json` |
| CI F1: RICF parts: marriage is worth 132,000 F a year to each married earner | unit | 132,000 F (264,000 for two earners, reading) | confirmed | known | `africa_mena/search/CI-F1.json` |
| CI F2: CNPS contributions on at least the SMIG: the first franc of pay costs 3,780 F a month | notch | 45,348 F a year for 12 F of pay | confirmed | new (no press search) | `africa_mena/search/CI-F2.json` |
| CM F1: TDL steps by monthly base salary | notch | 6,098 F a year at 250,000 a month (each of 9 edges 3,000-6,000) | confirmed | new (no press search) | `africa_mena/search/CM-F1.json` |
| CM F4: Dividends 16.5 % (11 % from an SME, LF 2025) against wage rates to 38.5 % | itype | 357,530 F at 10 M (907,530 from an SME) | confirmed | known (pattern) | `strengthen/search/CM-F4.json` |
| CV F1: Married splitting and a second mínimo | unit | 146,081 CVE at 3 M (one earner) | confirmed | new (no press search) | `africa_mena/search/CV-F1.json` |
| DJ F1: Monthly ITS without annual reconciliation | timing | 2.4 M FD: 776,000 (one month) vs 348,000 (12 months) | confirmed | new (no press search) | `africa_mena/search/DJ-F1.json` |
| DZ F1: Rent of 1,800,000 DA: 7 % final; one dinar more puts the whole rent on the barème | notch | 175,799 DA for 1 DA of rent at 1,800,000 (7 % final -> the barème on 75 % of the | confirmed | new | `strengthen/search/DZ-F1.json` |
| DZ F2: The 30,000-35,000 DA a month smoothing formula (x 137/51) taxes the first slice at 58.7 %  | phase | 7,044 DA on the first 12,000 DA a year above 360,000 | confirmed | new | `strengthen/search/DZ-F2.json` |
| EG F1: Column tariff: crossing 600k/700k/800k/900k/1.2 M of net income withdraws the lower bands | notch | 5,001 EGP at 937,410 of gross; 10,001 at 1,237,410 | confirmed | known | `africa_mena/search/EG-F1.json` |
| ET F3: Monthly final employment tax: bunched pay is taxed at 35 % at once | timing | 240,000 ETB: 81,950 (one month) vs 59,400 | confirmed | new (no press search) | `strengthen/search/ET-F3.json` |
| GA F1: An unmarried parent's first child gives 2 parts: marriage costs a two-earner family | unit | 243,198 F at 14 M + 6 M with two children | confirmed | new (no press search) | `africa_mena/search/GA-F1.json` |
| GH F2: The GH¢200 relief for a dependant spouse ends at her first cedi | second | GH¢50-70 of tax | confirmed | new (no press search) | `strengthen/search/GH-F2.json` |
| GN F1: Final monthly ITS: uneven pay costs more | timing | 24 M GNF: 2,120,000 (2 months) vs 600,000 (12 months) | confirmed | new (no press search) | `africa_mena/search/GN-F1.json` |
| GW F1: The 2021 table's 14 % row subtracts 37,947 instead of 21,927: tax falls 16,020 a month at  | outside | 192,240 F a year less for everyone above 400,500 a month | confirmed | new | `africa_mena/search/GW-F1.json` |
| GW F3: Pensions up to 200,000 F a month are outside income; above, the whole pension is taxed | notch | 146,988 F a year for 12 F | confirmed | new (no press search) | `africa_mena/search/GW-F3.json` |
| IQ F3: Individual taxation with personal allowances: two earners pay less than one | unit | 155,000 IQD at 10 M | confirmed | known | `africa_mena/search/IQ-F3.json` |
| JO F3: Bank interest at a final 5 % against wage rates to 30 % | itype | 2,100 JOD on 10,000 moved from pay to interest at 30,000 | confirmed | known (pattern) | `strengthen/search/JO-F3.json` |
| JO F5: Dependants' 9,000 JOD whatever their number; couple cap 23,000: further children add nothi | unit | first child 1,050 JOD (two earners), others 0 | confirmed | known | `africa_mena/search/JO-F5.json` |
| KE F1: SHIF minimum of KES 300 a month: 6 % of pay at KES 5,000 a month | notch | KES 3,600 a year from the first shilling | confirmed | new | `strengthen/search/KE-F1.json` |
| LB F1: Married supplement (225 M LBP) lost when the wife earns her first lira | second | 15.75 M LBP (18.9 M with two children) | confirmed | new | `strengthen/search/LB-F1.json` |
| LB F5: Individual taxation: splitting the same income between spouses | unit | 38.25 M LBP at 2.4 B | confirmed | known | `africa_mena/search/LB-F5.json` |
| LY F2: Jihad tax: 1 / 2 / 3 % of the whole income at 50 and 100 a month (1970 amounts) | notch | 11 LYD for 1 LYD at 1,212 a year | confirmed | new (no press search) | `africa_mena/search/LY-F2.json` |
| MA F1: Professional expenses fall from 35 % to 25 % at 78,000 MAD of gross pay | notch | 779 MAD for 1 MAD; dead zone to about 78,880 | confirmed | new | `strengthen/search/MA-F1.json` |
| MG F1: IRSA never below Ar 3,000 a month: an entry cost and a flat tax to about 410,000 a month | notch | 35,988 Ar a year for 12 Ar | confirmed | known | `africa_mena/search/MG-F1.json` |
| MR F2: Final monthly withholding without reconciliation: uneven pay is taxed more | timing | 180,000 MRU: 33,300 (6 months) vs 16,200 (12 months) | confirmed | new (no press search) | `africa_mena/search/MR-F2.json` |
| MU F1: CSG at 3 % of the whole wage above Rs 50,000 a month (1.5 % below) | notch | 8,989 MUR for 12 MUR | confirmed | new | `strengthen/search/MU-F1.json` |
| MU F2: Spouse dependant deduction ends when her income exceeds Rs 110,000 | second | 21,999 MUR for 1 MUR | confirmed | new (no press search) | `strengthen/search/MU-F2.json` |
| MW F1: Two schedules: employment income to 40 %, other personal income at most 30 % | itype | 5,058,000 MWK of tax at 120 M | confirmed | known | `africa_mena/search/MW-F1.json` |
| MZ F1: The gazetted top row prints 27,275 for three dependants; the AT's code prints 28,275 | outside | 12,000 MZN a year charged above the enacted table (and on the gazette a 4th depe | confirmed | new (no press search) | `strengthen/search/MZ-F1.json` |
| NA F1: Final 10 % on bank and unit-trust interest, exempt dividends, against 37 % | itype | 27,000 NAD on 100,000 moved at 1.7 M | confirmed | known (pattern) | `strengthen/search/NA-F1.json` |
| NE F1: The seventh charge doubles the family abatement (15 % -> 30 %) | unit | 216,000 F a year at 6 M (the sixth: 14,400) | confirmed | new (no press search) | `africa_mena/search/NE-F1.json` |
| NE F4: The spouse's first franc ends her charge | second | 38,999 F at 3.6 M | confirmed | new (no press search) | `strengthen/search/NE-F4.json` |
| RW F1: Monthly PAYE is final for employees: bunched pay is taxed at 30 % at once | timing | 3.6 M RWF: 1,044,000 (one month) vs 648,000 | confirmed | new (no press search) | `strengthen/search/RW-F1.json` |
| SC F1: Each source of employment has its own monthly bands | timing | SR 1,783 a month at SR 20,000 split over two employers | confirmed | new (no press search) | `strengthen/search/SC-F1.json` |
| SN F1: TRIMF steps by gross-income band; the earner pays the spouse's TRIMF too | notch | 2,699 F at 600,000; 18,369 F (36,313 one-earner couple) at 12 M | confirmed | new (no press search) | `africa_mena/search/SN-F1.json` |
| SN F2: Half-part for a sole-earning spouse and the spouse's TRIMF end at her first franc | second | 185,549 F at 12 M; 42,899 F at 3 M with two children | confirmed | new | `strengthen/search/SN-F2.json` |
| SO F1: The First Schedule prints $1,788 at $18,000 where its bands give $1,728 | notch | $59 for $1; $60 a year more for everyone above $18,000 | confirmed | new | `strengthen/search/SO-F1.json` |
| SZ F4: Dividends and interest at 10 % against wage rates to 33 % | itype | 23,000 SZL on 100,000 moved at 600,000 | confirmed | known | `africa_mena/search/SZ-F4.json` |
| TD F1: Since 2023 dividends pay 20 % flat, salary at most 18 % of gross: pay yourself a salary | itype | 2,374,200 F at 30 M (salary cheaper) | confirmed | known (pattern) | `strengthen/search/TD-F1.json` |
| TD F3: PSA of 400 F a month on every salary from the first franc | notch | 4,788 F a year for 12 F | confirmed | new (no press search) | `africa_mena/search/TD-F3.json` |
| TG F1: 'Conjoint ne disposant pas de ressource' as a dependant: lost at her first franc | second | 17,999 F at 10 M | confirmed | new (no press search) | `africa_mena/search/TG-F1.json` |
| TG F2: 50 % of the whole pension taxable above 3.6 M | notch | 26,999 F for 1 F | confirmed | new (no press search) | `africa_mena/search/TG-F2.json` |
| TN F1: CSS exemption for wage/pension-only incomes up to 5,000 TND of net income ends all at once | notch | 24 TND for 1 TND (wage 6,117 TND) | confirmed | new | `strengthen/search/TN-F1.json` |
| YE F2: Each income category gets its own exemption and bands | itype | 42,000 YER at 1.2 M (half wages, half business) | confirmed | new (no press search) | `africa_mena/search/YE-F2.json` |
| ZW F2: Individuals' trade income at a flat 25 % against employment bands to 40 % | itype | 193,063 ZWG at 2 M | confirmed | known (pattern) | `strengthen/search/ZW-F2.json` |
| AF F2: Monthly salary withholding is final for single-employer employees: bunched pay costs more | timing | 1,200,000 AFN paid in one month: 228,900 vs 106,800 spread | confirmed | not searched (drafting fault) | `strengthen/search/AF_F2.json` |
| AL F1: Two notches from the bracketed personal deduction (neni 22) | notch | 23,400 ALL for one lek above 600,000; 7,800 above 720,000 | confirmed | new | `strengthen/search/AL_F1.json` |
| AM F1: The stamp duty is a step function: one dram more than 1 000 000 a month costs 78 000 dram  | notch | 78,000 AMD a year for one dram of monthly pay above 1,000,000 (6,500 a month); s | confirmed | new (no press search) | `strengthen/search/AM_F1.json` |
| AM F2: The social payment depends on the year of birth: an employee born in 1973 pays nothing, on | itype | 300,000 AMD a year on 6 M of wages by year of birth (1973 vs 1974 cohorts) | confirmed | known | `strengthen/search/AM_F2.json` |
| AR L1: The spouse deduction (cargas de familia) is lost in full once the spouse's income passes t | second | 406,707 ARS of tax for one peso of the spouse's pay with the main earner at 40 M | confirmed | new | `strengthen/search/AR_L1.json` |
| AZ F1: State-sector notch at 2 500 manat a month: the 200-manat exemption stops all at once | notch | 336 AZN a year for one manat a month above 2,500 (state and oil sector) | confirmed | new (no press search) | `strengthen/search/AZ_F1.json` |
| AZ F2: Most private-sector wages are free of income tax until the end of 2025 (a 7-year temporary | itype | 11,700 AZN a year on 60,000 of wages (0 in the private non-oil sector, 11,700 in | confirmed | known | `strengthen/search/AZ_F2.json` |
| BA F1: Dependent-spouse cliff | second | 180 BAM for one mark of the spouse's pay at 5,218 (the 1,800 spouse deduction at | confirmed | new (no press search) | `strengthen/search/BA_F1.json` |
| BB F2: The compensatory income credit depends on a 'prescribed rate' that was not found, and stop | notch | up to 1,250 BBD at 35,001 (500 at an assumed 5 % rate: the prescribed rate is no | confirmed | new (no press search) | `strengthen/search/BB_F2.json` |
| BD F1: Minimum tax of 5,000 taka from the first taka above the exempt limit | notch | 5,000 BDT for one taka of salary at 600,000 (total income just over the 400,000  | confirmed | new (no press search) | `strengthen/search/BD_F1.json` |
| BD F2: Net-wealth surcharge: 10 % of the whole tax from one taka above 4 crore of net wealth (or  | notch | 41,500 BDT of surcharge on a 3 M salary for one taka of net wealth above 4 crore | confirmed | new (no press search) | `strengthen/search/BD_F2.json` |
| BO-F3: Dividends are outside the RC-IVA while wages pay 13 % | itype | 0 RC-IVA on dividends vs 13 % on wages | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| BR F2: Children are worth nothing to a one-earner family with one or two children | unit | the first two children are worth 0 to a one-earner family at R$ 60k, 100k and 20 | confirmed | known | `rest/novelty/BR_F2.json` |
| BT F1: The top row of the tax table prints Nu 242,499 where the bands give 242,500 | notch | tax falls by 1 BTN at 1,500,001 under the printed table | confirmed | not searched (drafting fault) | `` |
| BT F2: Surcharge cliff: 10 % of the whole tax once the tax reaches Nu 1,000,000 | notch | 100,001 BTN for one ngultrum of taxable income at 4,024,999 (2025; the 2025 Act  | confirmed | new (no press search) | `strengthen/search/BT_F2.json` |
| BY F1: The standard deduction stops at 1 164 rubles a month: 1 ruble more costs 25 rubles of tax | notch | 301 BYN a year (24.96 a month) for 1 BYN a month above 1,164 | confirmed | new (no press search) | `strengthen/search/BY_F1.json` |
| BZ F1: A total income of exactly BZ$29,000 is chargeable with no basic deduction: tax BZ$7,250, a | notch | 7,250 BZD of tax at exactly 29,000 (0 at 28,999, 1 at 29,001) | confirmed | new | `strengthen/search/BZ_F1.json` |
| BZ F2: Between BZ$29,000 and BZ$32,000 of income every extra dollar is taxed at 100 % | phase | 2,999 BZD of tax on 2,999 more income between 29,001 and 32,000 (100 %) | confirmed | known | `rest/novelty/BZ_F2.json` |
| BZ F3: Wives are taxed as part of their husbands' income unless both elect: aggregation would cos | unit | 5,000 BZD more tax for a 40,000 + 40,000 couple if aggregated | confirmed | known | `strengthen/search/BZ_F3.json` |
| CL F2: The art. 57 interest exemption is all-or-nothing: one peso more costs the whole exemption | notch | 55,822 CLP of global complementario for one peso of interest at 24 M of wages; 1 | confirmed | new (no press search) | `strengthen/search/CL_F2.json` |
| CN F1: Business income of a person with wages gets no 60,000 deduction | itype | 6,420 CNY on 300,000 (37,500 as business income vs 31,080 as wages) | confirmed | known (pattern) | `strengthen/search/CN_F1.json` |
| CN F2: Flat 20 % on dividends, rent and gains beside a 45 % top rate | itype | 200,000 CNY of tax on 1 M of dividends vs 243,080 on 1 M of wages | confirmed | known (pattern) | `rest/novelty/ZZ_dual.json` |
| CN W5R-1: 专项附加扣除 for children (education and infant care) applied (W5 review pass 2, 2026-11-20) | unit | 9,600 CNY a year for a couple 300,000 + 50,000 with two children when the lower  | confirmed | known | `strengthen/search/CN_W5R_1.json` |
| CO F3: An employee gets both dependant reliefs for the same child (10 % of labour income and 72 U | unit | 3,072,501 COP less tax at 120 M of wages with two children | confirmed | known | `strengthen/search/CO_F3.json` |
| CO L1: The pension solidarity contribution (FSP) is 1 % of the whole base from 4 SMMLV: one peso  | notch | 683,280 COP a year at 68,328,000 (4 SMMLV x 12); 366,238 at 16 SMMLV (273,312,00 | confirmed | new | `strengthen/search/CO_L1.json` |
| CR F2: Salaried and self-employed people with the same income pay very different tax | itype | 987,650 CRC a year: the same 11,064,000 is untaxed as salary and taxed as self-e | confirmed | known | `rest/novelty/CR_F2.json` |
| CR F3: The spouse credit is a marriage bonus | unit | 31,200 CRC a year (2025; Ley 7092 now prints 31,080 for 2026) | confirmed | known | `rest/novelty/CR_F3.json` |
| FJ F2: Bank interest is exempt only while gross income is at most $30,000: one dollar more makes  | notch | 100 FJD (10 % of 1,000 of interest) for one dollar of wages at 29,000 | confirmed | new (no press search) | `strengthen/search/FJ_F2.json` |
| FJ F3: Dividends are exempt for individuals while wages bear up to 39 % plus 8 % FNPF: an owner-m | itype | 63,601 FJD on 250,000 of wages vs 0 on 250,000 of dividends (company 25 %) | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| FM F1: The $1,000 deduction of 54 F.S.M.C. 122 is withdrawn in full at $5,000 of wages: $1 more w | notch | 61 USD for one dollar at 5,000 of wages | confirmed | new (no press search) | `strengthen/search/FM_F1.json` |
| FM F2: The social security ceiling is per employer per quarter: an employee with two jobs pays up | unit | 1,050 USD more social security on 50,000 split over two employers | confirmed | new (no press search) | `strengthen/search/FM_F2.json` |
| FM F3: Employee or business? Contractors who are 'a business' pay 3 % of gross revenue (and $80 b | itype | 1,180 USD: 1,560 wage tax vs 380 gross revenue tax on 20,000 | confirmed | known (pattern) | `strengthen/search/FM_F1.json` |
| GE F2: Owner-manager: dividends 5 % final against 20 % + 2 % on salary | itype | 5 % final on dividends vs 21.6 % (20 % of 98 % + 2 %) on salary | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| GY F1: Above GY$4.68 million the marginal income-tax rate falls from 25 % to 23.3 %: the one-thir | phase | marginal income-tax rate 23.33 % above 4.68 M vs 23.6-25 % below: 233,334 GYD pe | confirmed | new (no press search) | `strengthen/search/GY_F1.json` |
| GY F3: The child deduction goes to one parent only and must be elected; the second-job and overti | itype | 150,000 GYD less tax on 3.6 M when 600,000 of it is overtime | confirmed | known | `strengthen/search/GY_F3.json` |
| ID F2: Married women employed by one employer are taxed apart with a single PTKP | unit | the employed wife's own PTKP: her 54 M of wages adds 0 tax to the household | confirmed | known | `strengthen/search/ZZ_withhold.json` |
| IN F2: The 12-lakh rebate's marginal relief band costs 104 % per rupee | phase | net income falls by 2,822 INR when salary rises from 12,75,000 to 13,45,588 (s.  | confirmed | known | `rest/novelty/IN_F2.json` |
| IN F3: Surcharge marginal relief at 50 L / 1 Cr / 2 Cr (/ 5 Cr old regime) | phase | tax rises by 1,040 INR for 1,000 more income just above 50 lakh (104 % band) | confirmed | known | `rest/novelty/IN_F3.json` |
| KG F1: Wages below the district average are taxed as if they were the average (art. 187(2)) | notch | 24,000 KGS a year on 120,000 of wages with a district average of 30,000 a month | confirmed | new (no press search) | `strengthen/search/KG_F1.json` |
| KG F2: Dividends, deposit interest and pensions are exempt | itype | 0 tax on dividends vs 10 % + 10 % on salary | model-proved | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| KH F1: A spouse's first riel of earnings removes the homemaker-spouse relief | second | 180,000 KHR a year for an earner in the 10 % band, 360,000 in the 20 % band, for | confirmed | new | `strengthen/search/KH_F1.json` |
| KN F1: The HSDL charges the whole wage once it passes the threshold | notch | 946 XCD a year at the 27,040 threshold on a full-year reading; 473 at 27,040 and | confirmed | new (no press search) | `strengthen/search/KN_F1.json` |
| KZ F2: Dividends from a resident company are tax-free up to 30 000 MRP (118 m tenge) a year | itype | 0 tax on 10 M KZT of dividends from a resident company (within 30,000 MRP) | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| LC F2: The spouse allowance (EC$1,500) is withdrawn dollar for dollar above EC$1,500 of the spous | second | 450 XCD more tax on the main earner when the spouse's income rises from 1,500 to | confirmed | new (no press search) | `strengthen/search/LC_F2.json` |
| LK F1: Dividends are a final 15 % payment while salary reaches 36 % + 8 % EPF | itype | 1,898,000 LKR: 10 M of salary costs 3,272,000 (tax + EPF), 1.8 M salary + 8.2 M  | model-proved | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| MD F1: Personal exemption withdrawn in full at 360,000 lei: a 3,565-lei notch | notch | 3,565 MDL for one leu at 360,000 | confirmed | known | `rest/novelty/MD_F1.json` |
| ME F3: Monthly taxation without reconciliation | timing | 1,353 EUR: 18,000 paid in one month pays 2,577, evenly 1,224 | proved | new (no press search) | `strengthen/search/ZZ_withhold.json` |
| MH F2: The low-wage exemption is all or nothing: $693.33 a month pays nothing, one cent more pays | notch | 665 USD a year for one dollar at 8,320 (693.33 a month) | confirmed | known | `strengthen/search/MH_F2.json` |
| MM F1: All-or-nothing salary exemption: one kyat over 4,800,000 costs 92,000 kyat | notch | 92,000 MMK for one kyat above 4,800,000 of salary | confirmed | new | `strengthen/search/MM_F1.json` |
| MN F1: Stepped wage-tax credit makes take-home pay fall at six thresholds | notch | 24,001 MNT of tax + SI for 10 more of pay at 6,779,650 (the credit step); 28,827 | confirmed | new (no press search) | `strengthen/search/MN_F1.json` |
| MV F1: Dividends from resident companies are exempt; salary is taxed at up to 15 % plus 7 % pensi | itype | 204,900 MVR of tax on 3 M of salary (plus 7 % pension) vs 0 on 3 M of dividends | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| MY F1: s. 6A rebate cliff at RM35,000 of chargeable income | notch | RM400 (RM800 with a non-earning spouse) for one ringgit; after the W5 EPF/SOCSO  | confirmed | new | `strengthen/search/MY_F1.json` |
| NP F1: A woman with only remuneration loses her 10 % rebate with one rupee of other income | notch | 23,500 NPR for one rupee of business income (woman with 1.5 M of remuneration) | confirmed | new (no press search) | `strengthen/search/NP_F1.json` |
| NP F2: Couple election (s. 50) pays for one-earner couples | unit | 29,000 NPR for a one-earner couple on 1.5 M electing joint assessment | confirmed | known | `strengthen/search/NP_F2.json` |
| NP F3: The 1 % social security tax falls only on employment income | itype | 5,000 NPR on 500,000 as wages, 0 as business income | confirmed | new (no press search) | `strengthen/search/NP_F3.json` |
| NR F1: The employment tax is final for each pay period with no annual reconciliation: $120,000 pa | timing | 20,328 AUD: 120,000 paid in one month costs 22,152, evenly 1,824 | confirmed | new (no press search) | `strengthen/search/NR_F1.json` |
| NR F2: The three printed pay-period bands are three different annual allowances: $110,880 monthly | timing | 39 AUD at 120,000 (fortnightly vs monthly) | confirmed | new (no press search) | `strengthen/search/NR_F1.json` |
| NR F4: Residents keep a $110,880 tax-free band; a non-resident employee pays 20 % from the first  | unit | 22,176 AUD at 110,880 (resident band vs 20 % flat) | confirmed | new (no press search) | `strengthen/search/NR_F1.json` |
| PE-F2: Deposit interest exempt to 31-12-2026, capital income flat 6,25 %, dividends 5 % against 3 | itype | 5 % on dividends, 0 on deposit interest, vs up to 30 % on labour | confirmed | known (pattern) | `rest/novelty/ZZ_dual.json` |
| PK F1: Surcharge cliff at 10 million: one rupee of taxable income costs 241,290 rupees (salaried) | notch | 241,290 PKR for one rupee above 10 M (salaried, 9 %); 359,000 non-salaried | confirmed | new | `strengthen/search/PK_F1.json` |
| PK F2: Profit on debt above 5 million leaves the 20 % separate tax and moves all of it into the p | notch | 1,258,000 PKR for one rupee of bank profit above 5 M (salary 2.4 M) | confirmed | known | `rest/novelty/PK_F2.json` |
| PK F3: The 75 % salary test switches the whole income between two tables | notch | 384,000 PKR for one rupee of business income (3 M salary + 999,999 vs 1,000,000) | confirmed | known | `rest/novelty/PK_F3.json` |
| PK F4: One rupee of salary cuts the surcharge on a business income from 10 % to 9 % | itype | 80,900 PKR less surcharge on 20 M of business income with one rupee of salary | confirmed | new (no press search) | `strengthen/search/PK_F4.json` |
| PK F5: Pensions up to 10 million pay nothing; the same amount as salary pays 2,681,000 | itype | 2,681,000 PKR: 10 M of pension pays 0, 10 M of salary pays 2,681,000 | confirmed | new (no press search) | `strengthen/search/PK_F5.json` |
| PK F6: Super tax is a rate on the whole income: 1.5 million at 150 million | notch | 1.5 M PKR for one rupee above 150 M | confirmed | new (no press search) | `strengthen/search/PK_F6.json` |
| PK F7: Dividends at 15 % flat versus 35 % salary: owner-managers | itype | 371,000 PKR at 5 M (931,000 all salary vs 560,000 half dividends) before the 29  | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| PW F1: Citizens earning $15,000 or less get all wage tax back; at $15,001 they keep none of it: a | notch | 1,180 USD for one dollar above 15,000 (citizens) | confirmed | new (no press search) | `strengthen/search/PW_F1.json` |
| PY-F1: The IRP is due on the whole renta neta once gross income passes G 80.000.000: G 6.052.000  | notch | 6,052,000 PYG for one guaraní of income above 80,000,000 | confirmed | new | `strengthen/search/PY_F1.json` |
| PY-F2: Personal and family consumption is deductible without cap: the IRP is close to a tax on sa | itype | 0 IRP on 500 M of income with 500 M of documented personal spending | confirmed | new (no press search) | `strengthen/search/PY_F2.json` |
| RS F1: Monthly salary tax without annual reconciliation | timing | 31,262 RSD: 600,000 paid in one month pays 57,158, evenly 25,896 | confirmed | new (no press search) | `strengthen/search/ZZ_withhold.json` |
| RU F1: Child deduction cliff at 450,000 of cumulative income | notch | 548 RUB of tax for 12 rubles more at 450,000 a year with two children (the twelf | confirmed | known | `strengthen/search/RU_F1.json` |
| RU F2: Separate scale for investment income | itype | 260,000 RUB on 2 M of dividends (13 %) beside an 18 % marginal wage rate at 6 M | model-proved | known (pattern) | `rest/novelty/ZZ_dual.json` |
| SB F1: The Fifth Schedule gives a rate per 'Income Bracket' without saying 'on the excess': read  | notch | 1,800 SBD at the 15,000 bracket edge under the slab reading | confirmed | new (no press search) | `strengthen/search/SB_F1.json` |
| SG F1: Spouse relief cliff at $8,000 of the spouse's income | second | 196 SGD (FINDINGS said 197) for one dollar of the spouse's income above 8,000 wi | confirmed | new | `strengthen/search/SG_F1.json` |
| SM F2: The 100 € credit for incomes up to 15 000 € is a cliff | notch | 100 EUR for one euro at 16,129-16,130 of pay (taxable income crossing 15,000) | confirmed | new (no press search) | `strengthen/search/SM_F2.json` |
| SR F2: Overtime (and lump sums) on request at their own 5/15/25 % monthly scale against 8-38 % on | itype | SRD 303 a month on SRD 1,100 of overtime for a 38 % earner (3,636 a year), by ha | confirmed | not searched (drafting fault) | `strengthen/search/SR_F2.json` |
| SV-F1: Entering tramo II costs US$ 212,12 at once (fixed amount at the first cent above US$ 6.600 | notch | 212 USD for one dollar at 8,200 of pay | confirmed | new (no press search) | `strengthen/search/SV_F1.json` |
| SV-F2: The US$ 1.600 deduction is lost in full one dollar above US$ 9.100 of salary: US$ 160 more | notch | 160 USD for one dollar at 9,100 of salary | confirmed | new (no press search) | `strengthen/search/SV_F2.json` |
| SV-F3: At US$ 10.742,86 the printed fixed amount (720,00) is US$ 93,59 above the tramo II sum | notch | 94 USD at 10,742-10,743 | confirmed | not searched (drafting fault) | `` |
| TL F1: Two separate zero bands: wages and other income each get one | itype | 600 USD a year on 12,000 (two zero bands: 500 a month for wages, 6,000 a year fo | confirmed | new | `strengthen/search/TL_F1.json` |
| TO F3: Dividends are exempt (s 21) while salary is taxed up to 25 % plus NRBF 5 % | itype | 0 tax on 150,000 of dividends vs 38,000 on wages | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| TT F1: The Third Schedule's low-income relief (para. 2) no longer fits the rates: tax falls when  | notch | 1,090 TTD for one dollar at 101,743-101,744 of pay; 440 at 98,397 | confirmed | new | `strengthen/search/TT_F1.json` |
| TT F2: Earning TT$200 a week instead of TT$199 costs about TT$1,048 a year: NIS and the health su | notch | 1,048 TTD a year at 200 a week (10,399 -> 10,400 a year) | confirmed | new (no press search) | `strengthen/search/TT_F2.json` |
| TV F1: Schedule 6 states its rates as '% of taxable income' against bands of the whole taxable in | notch | 1,500 AUD at 10,000 of taxable income (11,494-11,495 of pay after the 13 % provi | model-proved | new (no press search) | `strengthen/search/TV_F1.json` |
| TW F1: Dividend credit refunded in cash to low-income households | itype | 37,160 TWD refunded to a household with only 900,000 of dividends | confirmed | known | `strengthen/search/TW_F1.json` |
| TW F2: Salary computed separately: the joint return is close to separate taxation for two earners | unit | tax 50,600 TWD for 1.5 M + 0.8 M with two children under the cheapest of the art | confirmed | known | `strengthen/search/TW_F2.json` |
| UA F1: The tax social benefit is all-or-nothing: 1 hryvnia over 4 240 a month costs 272.5 hryvnia | notch | 3,273 UAH a year for 1 UAH a month above 4,240; 6,543 for a parent of two above  | confirmed | new | `strengthen/search/UA_F1.json` |
| UY-F1: The deduction credit falls from 14 % to 8 % of all deductions one peso above 180 BPC | notch | 13,850 UYU for one peso at 1,183,680 (single); 30,697 with two children | confirmed | new | `strengthen/search/UY_F1.json` |
| UY-F2: FONASA moves from 3 % to 4,5 % (6 % with children) of the whole wage above 2,5 BPC a month | notch | 2,959 UYU a year for one peso at 197,292 (2.5 BPC a month) | confirmed | new (no press search) | `strengthen/search/UY_F2.json` |
| UY-F3: Labour is taxed up to 36 %, dividends at 7 %, interest at 0,5-12 % | itype | 7 % on dividends vs up to 36 % on labour | model-proved | known (pattern) | `rest/novelty/ZZ_dual.json` |
| UZ F1: Dividends 5 % against 12 % on salary | itype | 5 % on dividends vs 12 % on wages | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |
| VU F1: The VT 3,000 monthly floor is a notch | notch | 2,160 VUV a year (180 a month) at VT 3,000 a month | confirmed | new (no press search) | `strengthen/search/VU_F1.json` |
| WS F1: The fortnightly wage-tax bands are not the annual bands: 576 x 26 = 14,976 and 962 x 26 =  | notch | 2,273 WST on 26,000 under the fortnightly tax vs 2,270 on the annual scale | confirmed | not searched (drafting fault) | `` |
| WS F4: Dividends from resident companies are exempt and interest is not on the annual return: inv | itype | 0 tax on dividends vs 27 % top rate | confirmed | known (pattern) | `rest/novelty/ZZ_ownermgr.json` |

Withdrawn by L1-S: TH F1 (MODEL FIX (L1-S): Royal Decree No. 480 (B.E. 2552) s. 3, read on rd.go.th (th/law/rd_40923_rd480.html, dc480.pdf), exempts the s. 48 (2) tax 'เฉพาะกรณีผู้มีเงิน)
