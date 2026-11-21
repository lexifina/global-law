# ML findings (Mali (ITS, IRF, IRVM), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access B (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 3,494,130 XOF: threshold of the top (37 %) annual ITS band; a statutory threshold, not an average wage).

### F1 The two-point reduction of art. 12-A is ambiguous
- kind: statute-fault (wording)
- status: reading

'l'impôt calculé est réduit de deux points de pourcentage' and art. 12-B 'multipliant le montant des droits liquidés ... par le taux réel amputé de la réduction de deux points' can be read as tax − 2 % of income (model) or as a 2 % cut of the tax. Under the model's reading nobody pays below about 550 000 F (`two_point_zero`).

### F2 The DGI's 'current' code is a 2017 consolidation
- kind: gov-error (publication)
- status: evidence

The DGI site serves https://www.dgi.gouv.ml/CGI/ as the CGI in 2026; its own metadata dates it 2017 and no later finance law is shown. Every 2025 amount is therefore uncertain (access B).

### F3 Odd band limits (art. 10)
- kind: observation
- status: proved

Limits 578 400, 1 789 733, 2 384 195, 3 494 130 F: indexed amounts left unrounded; tax at the top threshold 693 219 F (`tax_top_threshold`).

### F4 Model limits
- kind: model limitation
- status: open

LF 2018-2025 not reached; INPS/AMO contributions; IBIC/IBNC (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Benefits in kind taxed for half their value (arrêté 99-0894, art. 4) | not modelled | no |
| L2 | Representation, cash, equipment, transport (≤ 10 % of base) and expatriation (15 %) allowances exempt (arrêtés 99-0892/0894) | not modelled | no |
| L3 | Dividends 10 %, deposit interest 9 %, rents 12 % instead of up to 37 % on pay (arts. 22, 42) | modelled; income-type scanner | yes |
| L4 | Family reduction shared between spouses on request (art. 11) | modelled (to the higher earner) | yes |

Catalogued 4, recreated 2, not modelled 2.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: ML: ITS confirmed (CGI, Loi 2016-10 barème); access B.

### W5S-1 payroll_africa (CoaleTech; wronglaw grid): monthly thresholds not the statute's (W5 review pass 3, 2026-11-20)
- kind: software-error
- `ml_open_payroll_africa_grid`: the app's monthly thresholds (175,000 / 1,800,000 / 3,500,000) are not the ITS barème. Dev: the app charges 0 up to about 3 M a year and is far below beyond (14,580,000: 1,108,255 vs 4,503,391); 72 / 283 exact.
- provisions: ITS arts. 9-12 (annual barème, art. 11 family reduction)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: INPS "Guide du cotisant" (PDF of 10 August 2013, Internet Archive capture 2021-09-23): AMO salarié 3,06 %, vieillesse salarié 3,6 %; Code de prévoyance sociale art. 187 (base); official secondary; CGI art. 7 a)
- INPS assurance vieillesse 3,6 % and AMO 3,06 % of all remuneration, reported; the 3,6 % pension retention deducted (CGI art. 7 a), limit 4 %). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: INPS / AMO rates from the INPS guide of 2013 (official secondary; later changes not checked). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | Ambiguous two-point reduction (art. 12-A): reading. |
| F2 | explained | 2017 consolidation served as current: gov record. |
| F3 | explained | Unrounded band limits (T: tax_top_threshold). |
| F4 | explained | Model limits. |
| W5S-1, W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch; 19 dips in the edge windows are rounding; marriage bonus 438,554 = family reduction to the higher earner (art. 11). |

<!-- L1-VERIFICATION END -->

### D9S-1 TaxDev EITD v2.0, row MLI 2020: ITS on gross pay, without the art. 7 a) deduction or the arts. 12-A / 12-B reduction (D9 review, 2026-11-20)
- Referee: `world_ml_taxdev_eitd_2020` (TaxDev Employment Income Taxes Dataset, ODI / IFS; research secondary). Its MLI
  2020 row sets soc_contr_ded = 0 and has no reduction, so the converter's values are the art. 10 barème applied to the
  gross wage (conversion checked: correct for the row as printed).
- The CGI (DGI online code) requires two more steps for a salaried employee:
  - art. 7 a): "Les retenues faites par l'employeur en vue de la constitution de pensions ou de retraites dans la limite
    de 4 % des salaires bruts" are deducted from gross pay: the INPS old-age retention of 3,6 % (W5 pattern A);
  - art. 12-A (Loi n° 2008-002): "l'impôt calculé est réduit de deux points de pourcentage au profit de l'employé";
    art. 12-B: the tax due is computed with "le taux réel amputé de la réduction de deux points de pourcentage" (taux
    réel = impôt liquidé / revenu imposable), i.e. the tax less 2 % of taxable income.
- Dev evidence (28 / 28 cases): with `"w5Contrib": false` (no art. 7 a) deduction) the model equals the referee less
  2 % of the wage, floored at 0, on every case; the remaining gap is the barème rate on the 3,6 % retention. The model
  is below the referee on all 28 (ratio 0.62 at 0.99 M rising to 0.90 at 14 M).
- Not a model error. Category S (referee omits statutory steps), recorded; no change to the model.
- provisions: CGI art. 7 a), art. 10 (Loi 2016-10), arts. 12-A, 12-B (Loi 2008-002)
