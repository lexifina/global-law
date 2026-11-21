# Burundi (BI) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Up to 43 % of pay can be tax-free as transport and housing allowances
- kind: loophole-known
- art. 33 3°-4°: deductible 'frais de déplacement ne dépassant pas 15% du salaire de base' and 'loyer ou indemnités compensatoires ne dépassant pas 60% du salaire de base'. Paying 6 M as a base of 3 428 572 plus 2 571 428 of allowances (75 % of the base) cuts the tax from 1 080 000 to 325 800 (#guard; exe with input allowances).
- provisions: Loi 1/14 art. 33
- Lean: BiTax.allowedAllowances (#guard)
- status: modelled (input allowances)

### F2 Pensions are listed as employment income and excluded from it in the next article
- kind: statute-fault
- art. 30 6° (restated by LF 2025/2026 art. 138) includes 'les pensions, les rentes ou les indemnités accordées par les fonds de pension qualifiés, les caisses de sécurité sociale de l'Etat ...'; art. 32 5° excludes exactly the same payments. The net effect is exemption; the restatement in 2025 kept the contradiction.
- provisions: Loi 1/14 arts. 30 6°, 32 5°; LF 2025/2026 art. 138
- Lean: BiTax.out (pensions not taxed)
- status: reading recorded

### F3 Rounding to the nearest thousand at the 1.8 M threshold
- kind: model-fix
- art. 21: 'arrondi au millier de francs burundais le plus proche'. 1 800 499 pays 0, 1 800 500 pays 200 (#guard): a 200-franc step, harmless but a rounding-edge effect the scanner would list.
- provisions: Loi 1/14 art. 21
- Lean: BiTax.ire (#guard)
- status: proved by #guard

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay transport and housing allowances within 15 % / 60 % of base salary | recreated: input allowances, F1 | Loi 1/14 art. 33 |
| K2 | Complementary pension contributions deductible up to 20 % of gross | not modelled | Loi 1/14 art. 33 |
| K3 | Employer medical reimbursements excluded | not modelled | Loi 1/14 art. 32 4° |
| K4 | Dividends and interest at 15 % withholding vs 30 % on wages | recreated: income-type scanner | art. 122 (LF 2025/2026 art. 139) |
| K5 | Pensions untaxed (art. 32 5°) | recreated: F2 | Loi 1/14 arts. 30, 32 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 3.6 M, art. 21 band)
- LF 2025/2026 fiscal articles (OCR) for arts. 21, 30, 33, 122
- allowance structuring (#guard)

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

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/BiTax/Verify.lean` (imported by the `BiTax` library and built; each guard evaluates `BiTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/BI.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Transport allowances up to 15 % and housing up to 60 % of base pay are deductible: paying 6 M as 3,428,572 of base + 2,571,428 of allowances cuts the tax from 1,080,000 to 325,800 (754,200 a year). G: f1_allowances_43pct (input allowances). S: law/loi_ir_2013.ocr.txt:694-700 ('les frais de déplacement ne dépassant pas 15% du salaire de base', '... ne dépassant pas 60% du salaire de base'). |
| F2 | explained | Pensions listed and excluded: statute fault (net effect exemption). |
| F3 | explained | Rounding to the thousand (#guard 1,800,499 -> 0, 1,800,500 -> 200). |
| W5R P2-6 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan bands above 'top' (33.3 % max, 30 % avg) are the rounding. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Transport (<= 15 %) and housing (<= 60 % of base) allowances deductible: up to 43 % of pay untaxed | income-type gap | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing on art. 33's allowances). | 2026-11-20: OpenAlex specific queries 'Burundi impôt sur les revenus indemnités logement 60% salaire de base déplacement 15%'; 'Burundi income tax housing allowance exemption' (294 hits, titles checked); OpenAlex broad 'Burundi personal income tax', 'Burundi income tax wages', 'Burundi tax system reform' (75 records, titles and abstracts grepped, 5 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Burundi tax policy' (8308 records, titles only). Record: world/loopholes/africa_mena/search/BI-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 30.0 % (Loi IR 2013 art. 94: 'Le montant des bénéfices imposables ... imposé au taux de trente pour cent (30%)' (law/loi_ir_2013.ocr.txt:1468-1473)); at a profit of 3 AW the best split costs 23.3 % of the profit, all salary 23.3 %, all dividends 40.5 % (employer contributions: not included); dividends beat salary once employer contributions exceed 33 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
