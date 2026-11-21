# DR Congo (CD) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The 40 % band is cancelled by the 30 % cap above 77.9 M: the marginal rate falls from 40 % to 30 %
- kind: statute-fault
- art. 84 §1 taxes the surplus over 43.2 M at 40 %, §2 caps 'l'impôt total' at 30 % of the taxable income. The band tax reaches 30 % of income at 77 932 800 FC; above it the marginal rate is 30 %, below it (from 43.2 M) 40 %. At 100 M the tax is 30 M instead of 32.2 M (#guard). The top bracket only ever applies between 43.2 M and 77.9 M.
- provisions: O.-L. 69/009 art. 84 §§ 1-2
- Lean: CdTax.ipr (#guard)
- status: proved by #guard

### F2 The family reduction is a % of the tax: worth most to the highest earners
- kind: loophole-known
- art. 89: 2 % of the tax per dependant (wife, children, ascendants), up to 9 (18 %). At 12 M three dependants save 94 003 FC; at 100 M they would save 1.8 M. Monthly minimum 2 000 FC after the reduction (art. 84 §4).
- provisions: O.-L. 69/009 arts. 84 §4, 89, 90
- Lean: CdTax.ipr
- status: modelled

### F3 Housing allowances up to 30 % of gross salary are immune
- kind: loophole-known
- art. 48 3°: housing indemnity 'ne dépasse 30% du traitement brut', transport within six fares a day, medical costs: pay restructured into these is untaxed (not in the household contract).
- provisions: O.-L. 69/009 art. 48 3°
- Lean: -
- status: catalogued; not modelled

### F4 2025 is the last year of the cedular IPR
- kind: model-fix
- Loi 23/053 (IS and IRPP) 'entre en vigueur après vingt-quatre mois à compter du 31 décembre de l'année de sa promulgation' (art. 153): 2026. The DGI site already presents the IRPP reform; the 2025 model keeps the IPR.
- provisions: Loi 23/053 art. 153
- Lean: -
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Housing (30 % of gross), transport and medical allowances immune | not modelled: F3 | O.-L. 69/009 art. 48 3° |
| K2 | Dependants' 2 % reductions (up to 9) | recreated: F2 | art. 89 |
| K3 | Family allowances within legal rates immune | not modelled | art. 48 1° |
| K4 | Primes of state agents at a proportional 3 % instead of the barème | not modelled | art. 84 bis |
| K5 | End-of-career indemnities at 10 % | not modelled | art. 86 |
| K6 | Very high earners: the 30 % cap | recreated: F1 | art. 84 §2 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 21.6 M, art. 84 band)
- reform law entry into force (OCR)
- cap and minimum checks (#guard)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round W5 review (W5 fix agent, 2026-11-20)

### W5-1 payroll_africa (CoaleTech) ignores the IPR cap of 30 % of taxable income (software error)
- kind: software-error
- Ordonnance-loi 69/009 art. 84 §2: "En aucun cas, l'impôt total ne peut excéder 30% du revenu imposable". The model
  applies it (binding above about 77.9 M CDF a year); the app's PAYE CD keeps the 40 % band, so on the W5 dev grid it is
  above the model for every wage above the cap (99.6 M: 30.07 M vs 28.40 M). The other misses (1.8 CDF a year) are the
  app's monthly rounding. Grid `cd_open_payroll_africa_grid` (W5 review).

### W5R sweep P2-6: household-total employee-contribution input allotted by wages (W5 review pass 2, 2026-11-20)
- kind: model-fix (cross-country sweep from NI W5R-1)
- The optional household-total employee-contribution input was halved between two adults, so a one-earner couple
  deducted half of the earner's own contributions. The deduction provision this model already cites deducts each
  employee's own contributions from that employee's income; the total is now allotted in proportion to wages (halves
  only when nobody has wages). Checked on 400 random households: outputs change only for two adults with the input and
  unequal wages. Script: world/w5/review2/sweep_alloc.py. Rescanned (scan_world.py).
- status: model changed

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (statute (private reproduction))
- provisions: Décret n° 18/041 du 24 novembre 2018 fixant les taux de cotisations dues à la CNSS, art. 3 (10 % = 5 % + 5 %), art. 10 (transitional 3,5 % only to 1 January 2019); Loi 16/009 du 15 juillet 2016 arts. 13, 16, 18 (Leganet copies via the Internet Archive)
- CNSS worker 5 % of remuneration (pensions branch, no ceiling), deducted (CGI art. 50); input cnssEmployee still overrides. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS base floor at the SMIG (Loi 16/009 art. 13, Décret 18/041 art. 8) not applied. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/CdTax/Verify.lean` (imported by the `CdTax` library and built; each guard evaluates `CdTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/CD.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Hidden middle band: art. 84 §1 taxes income above 43.2 M at 40 % but §2 caps the whole tax at 30 % of taxable income, so the marginal rate is 40 % (38 % of gross) between 43.2 M and 77.9 M and 30 % above. G: f1_middle_band_40pct (1 M more gross at 60 M: 380,000 more tax), f1_cap_30pct_at_100m (28.5 M at 100 M). S: law/CODE-DES-IMPOTS-2023.txt:4031 ('Par. 2. En aucun cas, l'impôt total ne peut excéder 30% du revenu' [imposable]). |
| L1 | confirmed (new from the rescan) | Minimum IPR of 2,000 FC a month from the first franc: 12 FC of annual pay costs 23,988 of net (rescan: first-unit notch 23,999 for single and second earners). G: l1_minimum_ipr_first_franc. S: law/CODE-DES-IMPOTS-2023.txt:4065 ('... ne peut être inférieur à 2.000 Francs congolais par mois'). |
| F2 | explained | Family reduction as a % of the tax: design. |
| F3 | lead | Housing allowances up to 30 % of gross untaxed: not modelled. |
| F4 | explained | 2025 last year of the IPR: record. |
| W5-1, W5R P2-6, W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan bands above the top rate (43 %) on 45.4-82.0 M = F1; timing gain 414,720 = F1 (non-convex at 77.9 M). |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: A 40 % band under a 30 % cap on the whole tax: the marginal rate is 40 % between 43.2 M and 77.9 M and 30 % above | rate above the top rate | **new**: PwC DRC prints both the 40 % band ('43,200,001 And more 40') and 'IPR cannot exceed 30% of the taxable salary' without drawing the consequence (the 40 % rate applies only between 43.2 and 77.9 M); OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'RDC impôt professionnel sur les rémunérations plafond 30% revenu imposable'; 'DRC employment income tax 30% cap 40% bracket' (134 hits, titles checked); OpenAlex broad 'Democratic Republic of the Congo personal income tax', 'Democratic Republic of the Congo income tax wages', 'Democratic Republic of the Congo tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (democratic-republic-of-the-congo, 5 individual pages): 3 passages with the item's terms; Crossref IMF prefix 10.5089 'Democratic Republic of the Congo tax policy' (15520 records, titles only). Record: world/loopholes/africa_mena/search/CD-F1.json |
| L1: Minimum IPR of 2,000 FC a month from the first franc | cliff or notch | **new**: PwC DRC: nothing on the 2,000 FC minimum; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'RDC IPR minimum 2000 francs congolais par mois' (5 hits, titles checked); OpenAlex broad 'Democratic Republic of the Congo personal income tax', 'Democratic Republic of the Congo income tax wages', 'Democratic Republic of the Congo tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (democratic-republic-of-the-congo, 5 individual pages): 2 passages with the item's terms. Record: world/loopholes/africa_mena/search/CD-L1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 30.0 % (Code des impôts (2023 consolidation), impôt professionnel: 'Le taux de l'impôt professionnel est fixé à 30% sur les bénéfices et profits des personnes morales' ); at a profit of 3 AW the best split costs 31.0 % of the profit, all salary 31.0 %, all dividends 44.0 % (employer contributions: not included); dividends beat salary once employer contributions exceed 30 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
