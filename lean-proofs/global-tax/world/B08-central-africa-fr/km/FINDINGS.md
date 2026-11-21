# Comoros (KM) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Art. 97 puts 3 500 000 in two bands
- kind: statute-fault
- '25 % sur la fraction du revenu compris entre 2.500.001 et 3.500.000 FC ; 30 % sur la fraction du revenu compris entre 3.500.000 FC et plus': the franc at 3 500 000 is in both; the model reads 30 % from 3 500 001 (difference: 5 % of one franc).
- provisions: CGI art. 97
- Lean: KmTax.sched
- status: reading recorded

### F2 Social contributions deductible only up to 6 % of gross
- kind: model-fix
- art. 59 a)-b): pension and social-security retentions 'ne peut excéder 6 % du montant brut'; the 30 % frais is then taken on the rest.
- provisions: CGI art. 59
- Lean: KmTax.person
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | 30 % flat professional expenses (or real expenses) | recreated | CGI art. 59 c) |
| K2 | Allowances for job expenses and family allowances exempt | not modelled | CGI art. 56 1°-2° |
| K3 | Benefits in kind at flat %: housing 10 %, others 7 % of gross | not modelled | CGI art. 58 |
| K4 | Split income with a spouse (individual) | recreated: split-gain scanner | CGI art. 97 |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 3.5 M, art. 97 band)
- LF 2024 fiscal part (OCR)

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

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | 3,500,000 in two bands: a one-franc reading difference. |
| F2 | explained | 6 % cap on deductible contributions: modelled. |
| W5R P2-6 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch, no band above the top rate. |

<!-- L1-VERIFICATION END -->
