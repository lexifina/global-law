# Republic of the Congo (CG) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 A wage-earning wife is taxed separately with two parts: two-earner married couples pay far less than unmarried ones
- kind: loophole-known
- art. 4 1°: the wife 'bénéficiaire des revenus salariaux uniquement' is assessed alone 'considérée comme mariée sans enfants' (2 parts), while her husband keeps the married parts and the children. Couple 6 M + 3 M, no child: married 1 420 400; the same two people unmarried 2 012 200; one earner on 9 M married 1 972 600 (exe). The scanner's marriage bonus reaches 671 000 (27 % of the scale wage) and 96 % of tested couples gain from marriage.
- provisions: CGI arts. 4, 91
- Lean: CgTax.out (wifeSeparate)
- status: modelled; scan reproduces

### F2 The 265 000 rule is all-or-nothing: 264 999 of income pays nothing, 265 000 pays 11 750
- kind: statute-fault
- art. 95 I: 'Lorsque le revenu global du contribuable est inférieur à 265.000 francs, la cotisation n'est pas mise en recouvrement.' At the threshold the tariff gives 2 000 + 9 750: one franc of income costs 11 750 (scan: METR 107 % peak; notch 11 749 at 355 494 of gross for a single person).
- provisions: CGI art. 95 I
- Lean: CgTax.irpp (#guard)
- status: proved by #guard; scan reproduces

### F3 A 50 % top rate per part from 8 M, on 80 % of net pay
- kind: model-fix
- art. 95: 45 % from 2.5 M and 50 % from 8 M per part; with the 20 % deduction and 6.8 % contributions the top combined rate on gross is 42.8 % (scan). The bands have not been indexed since the 1992 law the CGI cites (Loi 005/92).
- provisions: CGI arts. 41, 95; Loi 005/92
- Lean: CgTax.sched
- status: modelled

### F4 The CNSS employee rate sits in the annual finance law, not in a social-security code
- kind: model-fix
- LF 2025 art. 9 sets CNSS 4.55 % / 20.28 % and CAMU 2.27 % / 4.55 % (employee / employer), and takes over the IRPP of the first 50 000 newly registered informal employers' declarants for 2025.
- provisions: Loi 47-2024 art. 9
- Lean: CgTax.person
- status: modelled (rates; no ceiling)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Marriage of two wage earners: the wife's separate 2-part assessment | recreated: filing-unit scanner, F1 | CGI art. 4 1° |
| K2 | Keep household taxable income below 265 000 (nothing collected) | recreated: METR scanner, F2 | CGI art. 95 I |
| K3 | Benefits in kind at flat % (logement 20 %, domesticité 7 %, voiture 3 %...) instead of their real value | not modelled | CGI art. 39 |
| K4 | Pension contributions deductible up to 6 % | not modelled: input not in the household | CGI art. 40 |
| K5 | Extra half-part for public agents posted outside the communes | not modelled | CGI art. 92 3) |
| K6 | State takes over the 2025 IRPP of newly declared informal employers' staff | not modelled: first 50 000 declarants only | LF 2025 art. 9 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 2.5 M, art. 95 band)
- married two-earner vs two singles vs one earner (exe)
- JO special issues 2022-2025 for finance-law changes to arts. 4, 39-41, 89-95

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S-1 payroll_africa (CoaleTech; wronglaw grid): an older barème (W5 review pass 3, 2026-11-20)
- kind: software-error
- `cg_open_payroll_africa_grid`: the app's barème (with a 464,000 threshold not in the texts) is not the CGI tome I art. 95 I barème (1 / 15 / 30 / 45 / 50 %) with the art. 89 quotient. Dev: the app charges 0 up to about 850,000 where the model taxes from about 370,000, is above to about 2 M and below beyond (11,665,200: 3,837,676 vs 3,424,500); 64 / 273 exact.
- provisions: CGI tome I art. 95 I; art. 89
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/CgTax/Verify.lean` (imported by the `CgTax` library and built; each guard evaluates `CgTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/CG.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | A wage-earning wife is assessed alone with 2 parts while the husband keeps his parts: married 6 M + 3 M pays 591,800 less than the same two people unmarried (and 552,200 less than one earner on 9 M). G: f1_wife_separate_two_parts. S: law/cgi_tome1.raw.txt:133 (art. 4: '1° Lorsqu'elle est bénéficiaire des revenus salariaux uniquement; en ce cas, elle est' [imposée séparément]). |
| F2 | confirmed | The 265,000 rule: below 265,000 of income nothing is collected; at the threshold the tariff gives 11,750: one franc of gross at 355,495 costs 11,749 of net. G: f2_265000_rule. S: law/cgi_tome1.txt:2263 (art. 95 I: 'Lorsque le revenu global du contribuable est inférieur à 265.000 francs, la cotisation n'est pas mise en recouvrement'). |
| F3 | explained | Unindexed 1992 bands: record. |
| F4 | explained | CNSS rate in the finance law: record. |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: notches at 355,494 (single) = F2 and 592,490 / 888,736 (two earners) = F2 for each spouse; marriage bonus 671,000 = F1. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: A wage-earning wife is assessed alone with 2 parts while the husband keeps his parts | household-unit effect | **new**: PwC Congo says 'PIT is assessed on family groups ... a father's return must normally include any income earned by his wife', omitting CGI art. 4 1° (a wife with only wages is assessed alone with two parts); OpenAlex: nothing. The guide's omission is itself worth a note to its authors. | 2026-11-20: OpenAlex specific queries 'Congo Brazzaville IRPP épouse imposée séparément deux parts'; 'Republic of Congo income tax married woman separate taxation' (369 hits, titles checked); OpenAlex broad 'Congo personal income tax', 'Congo income tax wages', 'Congo tax system reform' (75 records, titles and abstracts grepped, 5 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (republic-of-congo, 5 individual pages): 7 passages with the item's terms; Crossref IMF prefix 10.5089 'Republic of Congo tax policy' (15512 records, titles only). Record: world/loopholes/africa_mena/search/CG-F1.json |
| F2: Nothing collected below 265,000 of income; 11,750 at the threshold | cliff or notch | **new**: PwC Congo: no 265,000 rule; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Congo IRPP revenu global inférieur à 265 000 francs'; 'Republic of Congo personal income tax 265,000 threshold' (25 hits, titles checked); OpenAlex broad 'Congo personal income tax', 'Congo income tax wages', 'Congo tax system reform' (75 records, titles and abstracts grepped, 5 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (republic-of-congo, 5 individual pages): 0 passages with the item's terms. Record: world/loopholes/africa_mena/search/CG-F2.json |

<!-- L1-VERIFICATION END -->
