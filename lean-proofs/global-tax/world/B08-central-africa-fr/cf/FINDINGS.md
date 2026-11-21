# Central African Republic (CF) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The 30 % deduction has no cap: a third of every salary is untaxed at all levels
- kind: loophole-known
- art. 38: 'frais strictement professionnels ... évalués à 30%' with no ceiling (Cameroon caps the same 30 % at 4.8 M, Gabon its 20 % at 10 M). The top statutory rate on gross is therefore 28 % (40 % x 70 %; scan: statutory top 27.4 %).
- provisions: CGI art. 38, 86
- Lean: CfTax.person
- status: modelled

### F2 The first threshold is printed '378.0000' in the official 2023 edition
- kind: gov-error
- art. 86's table reads '0- 378.0000 / 378.001-1.680.000 ...'. The next row starting at 378.001 shows the limit is 378 000; the extra zero is a typesetting error in the DGID's official consolidation (not a different law). Model: 378 000.
- provisions: CGI art. 86 (édition 2023)
- Lean: CfTax.sched
- status: reading recorded

### F3 Capital income at a final 15 % against up to 28 % on gross salary
- kind: loophole-known
- art. 84: 15 % of the gross distributed income, against the art. 86 bands on 70 % of salary. Owner-managers gain from about 2 M of salary upward (company-side tax not modelled).
- provisions: CGI arts. 84, 86
- Lean: CfTax.out
- status: modelled (personal side)

### F4 The wage base may not be below the minimum wage
- kind: statute-fault
- art. 36 second sentence: 'En aucun cas le montant ... à retenir ne peut être inférieur au salaire minimum interprofessionnel garanti': a part-time worker is taxed on the full SMIG. The SMIG amount was not reached and the 0 % first band (378 000) makes it irrelevant at the SMIG level unless it exceeds 540 000 a year; not modelled.
- provisions: CGI art. 36
- Lean: -
- status: catalogued

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Uncapped 30 % professional-expense deduction | recreated: F1 | CGI art. 38 |
| K2 | Benefits in kind at flat %: housing 10 %, food 25 % capped 60 000 a month, vehicle 10 % | not modelled | CGI art. 37 |
| K3 | Retirement and severance indemnities exempt within 15 % (min. 1 M) | not modelled | CGI art. 37 |
| K4 | Pay in dividends at 15 % final | recreated: income-type scanner, F3 | CGI art. 84 |
| K5 | Split income with a spouse (individual taxation) | recreated: split-gain scanner: up to 1.1 M | CGI art. 86 |
| K6 | Retirement-savings plan annuities taxed on 50 % | not modelled | CGI art. 40 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 3.36 M, art. 86 band)
- LF 2025 fiscal part (OCR) for wage articles
- collectif 2024 (OCR) for wage articles

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5R sweep P2-6: household-total employee-contribution input allotted by wages (W5 review pass 2, 2026-11-20)
- kind: model-fix (cross-country sweep from NI W5R-1)
- The optional household-total employee-contribution input was halved between two adults, so a one-earner couple
  deducted half of the earner's own contributions. The deduction provision this model already cites deducts each
  employee's own contributions from that employee's income; the total is now allotted in proportion to wages (halves
  only when nobody has wages). Checked on 400 random households: outputs change only for two adults with the input and
  unequal wages. Script: world/w5/review2/sweep_alloc.py. Rescanned (scan_world.py).
- status: model changed

### W5S-1 payroll_africa (CoaleTech; wronglaw grid): not the art. 86 barème (W5 review pass 3, 2026-11-20)
- kind: software-error
- `cf_open_payroll_africa_grid`: the app's bands (10 / 20 / 30 % with a 1,800,000 threshold, absent from the statute texts on file) are not the CGI art. 86 barème. Dev, single earners, current exe: equal to about 700,000 a year, then the app is far above (2,476,800: 240,499 vs the model's 112,110; 16,800,000: 4,375,199 vs 3,514,560); 60 / 296 exact.
- provisions: CGI art. 86 (barème annuel on the revenu global net)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/CfTax/Verify.lean` (imported by the `CfTax` library and built; each guard evaluates `CfTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/CF.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Uncapped 30 % frais: design. |
| F2 | explained | '378.0000' typo: gov record. |
| F3 | confirmed (personal side) | 10 M as distributions keeps 110,560 more than as salary (15 % final vs the bands on 70 % of salary). G: f3_dividends_vs_salary. S: law/cgi2023.raw.txt:726-733 (distributions 'assujettis à une retenue à la source de l'IRPP, libératoire dont le taux est fixé par l'article 84'). |
| F4 | lead | SMIG floor on the wage base (art. 36): not modelled; irrelevant below the 378,000 zero band unless the SMIG exceeds it. |
| W5R P2-6, W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan bands above 'top' (29.8 % max, 28.0 % avg) are rounding; no notch. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F3: Distributions at a final 15 % against wage bands | income-type gap | **new**: Nothing found (no PwC page for the country; OpenAlex returned South African and generic papers). | 2026-11-20: OpenAlex specific queries 'Centrafrique IRPP revenus de capitaux mobiliers 15% salaires'; 'Central African Republic personal income tax dividends' (9050 hits, titles checked); OpenAlex broad 'Central African Republic personal income tax', 'Central African Republic income tax wages', 'Central African Republic tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country. Record: world/loopholes/africa_mena/search/CF-F3.json |

<!-- L1-VERIFICATION END -->
