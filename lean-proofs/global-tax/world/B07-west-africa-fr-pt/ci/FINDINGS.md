# CI findings (Côte d'Ivoire (ITS 2024 reform, RICF, IRVM, CNPS), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access A (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 2,880,000 XOF: 12 x 240 000 F, the upper limit of the 16 % monthly band; a statutory threshold, not an average wage).

### F1 Marriage is worth 132 000 F a year to each married earner (art. 120)
- kind: loophole-known (design)
- status: proved (reading)

Married without child = 2 parts against 1 for a single person; the RICF is 11 000 F a month (`marriage_bonus`). Two cohabiting earners pay 264 000 F a year more than the same couple married, if both married spouses get the 'marié' row (reading: the article does not say how two earning spouses share parts).

### F2 The CNPS minimum base makes the first franc of pay expensive
- kind: loophole-new (structure)
- status: scanner

Contributions are computed on at least the SMIG (60 000 F a month per the CNPS page): a worker with a tiny wage pays 3 780 F a month. The scanner shows a METR of 787,5 % at the first unit of pay (scale 2 880 000 F). Part-time or occasional work below the SMIG is penalised.

### F3 The CNPS page's retirement ceiling is 45 × an old SMIG
- kind: gov-error (published page inconsistent)
- status: evidence

The page says the ceiling is '45 fois le SMIG soit actuellement : 19 767 780 F par an (... 1 647 315 FCFA par mois)' and, a few lines above, 'SMIG dont le montant actuel est de 60000 FCFA'. 45 × 60 000 = 2 700 000 a month, not 1 647 315 (which is 45 × 36 607). Either the ceiling or the SMIG on the page is stale. The model uses the printed ceiling and flags it.

### F4 Pensions: 320 000 F a month exempt and 75 % off for retirees over 70 (arts. 116 13-, 120)
- kind: loophole-known (design)
- status: modelled

The exempt fraction (320 000 F in the 2023-719 wording; 300 000 in the earlier wording printed beside it) and the 75 % abatement for retired people over 70 make most pensions untaxed; the page prints both wordings, so the model's 320 000 is a reading of which is current.

### F5 Model limits
- kind: model limitation
- status: open

IRC on interest, IRF on rents, BIC/BNC; CMU health contribution; children 18-26 in education (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Employer social-protection contributions exempt up to 10 % of pay and 320 000 F a month (art. 116 9-) | not modelled (no input) | no |
| L2 | Transport, canteen (30 000 F), public transport (20 000 F) and housing benefits exempt (art. 116 10-18) | not modelled | no |
| L3 | Dividends at 17 % (12 % if listed on the BRVM) instead of up to 32 % on pay (arts. 182-183) | modelled (17 %); recreated by the income-type scanner | yes |
| L4 | Marriage and children: RICF by parts (art. 120) | modelled; recreated (F1) | yes |
| L5 | Pension exemption and over-70 abatement (arts. 116 13-, 120) | modelled | yes |
| L6 | Dockers' 1,5 % flat rate (art. 120 bis, LF 2025) | not modelled (occupation not in the contract) | no |
| L7 | Interns and apprentices' allowances exempt up to 150 000 / 100 000 F a month (art. 116 12-) | not modelled | no |

Catalogued 7, recreated 3, not modelled 4.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: CI: ITS (single tax since the 2024 reform, Ord. 2023-719) with the RICF; main statute = CGI as amended by Ord. 2023-719 and the LF 2025 annex.

### W5S-1 payroll_africa (CoaleTech; wronglaw grid): ITS bands not the statute's (W5 review pass 3, 2026-11-20)
- kind: software-error
- `ci_open_payroll_africa_grid`: the app's ITS bands 150,000 / 300,000 / 500,000 / 1,000,000 / 2,000,000 a month are not the barème the model applies (75,000 / 240,000 / 800,000 / 2,400,000 / 8,000,000). Dev: the app charges 0 up to about 3 M a year and stays far below (13,236,000: 1,729,193 vs 2,600,640); 95 / 280 exact.
- provisions: CGI art. 119 bis (ITS barème), art. 120 (RICF)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/CiTax/Verify.lean` (imported by the `CiTax` library and built; each guard evaluates `CiTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/CI.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (reading for two earners) | RICF parts: a married one-earner couple keeps 132,000 a year more than the same earner single; two married earners 264,000 more than two cohabiting earners if each gets the 'marié' row (reading). G: f1_marriage_one_earner, f1_marriage_two_earners; T: CiTax.marriage_bonus. S: src/cgi_its.txt (art. 120 RICF parts, as cited by the model). |
| F2 | confirmed | CNPS on at least the SMIG: 12 F of annual pay (1 F a month) costs 45,360 of contributions (3,780 a month); a part-time or occasional worker below the SMIG pays the full minimum. G: f2_cnps_floor. S: CNPS page (official secondary, as cited by the model: 'SMIG dont le montant actuel est de 60000 FCFA'); not re-found in the code text. Lead for a model fix: PwC's summary (reviewed 2026-09-09) gives a CNPS retirement ceiling of XOF 3,375,000 a month = 45 x 75,000, i.e. a SMIG of 75,000, so the model's floor (60,000) and ceiling (1,647,315) are probably stale and the floor costs 4,725 F a month, not 3,780; the SMIG décret was not reached, so no change (statute-only rule). |
| F3 | explained | Stale CNPS ceiling on the CNPS page: gov record. |
| F4 | explained | Pension exemption and over-70 abatement: design. |
| F5 | explained | Model limits. |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan timing gain 90,720 (two earners at 0.002 'AW') = the F2 floor; marriage bonus 264,000 = F1; the scanner's 0.002-AW grid does not list the first-unit floor as a notch. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: RICF parts: marriage is worth 132,000 F a year to each married earner | household-unit effect | **known**: PwC Côte d'Ivoire (Deductions) prints the RICF parts ('Single ... 1.0, Married without dependent children 2.0 ...'), from which the marriage bonus follows directly. | 2026-11-20: OpenAlex specific queries 'Côte d'Ivoire RICF crédit d'impôt charges de famille parts'; 'Côte d'Ivoire impôt sur les traitements et salaires réforme 2024 RICF' (0 hits, titles checked); OpenAlex broad "Cote d'Ivoire personal income tax", "Cote d'Ivoire income tax wages", "Cote d'Ivoire tax system reform" (75 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (ivory-coast, 5 individual pages): 6 passages with the item's terms; Crossref IMF prefix 10.5089 'Côte d'Ivoire tax policy personal income tax' (9219 records, titles only). Record: world/loopholes/africa_mena/search/CI-F1.json |
| F2: CNPS contributions on at least the SMIG: the first franc of pay costs 3,780 F a month | cliff or notch | **new**: PwC Côte d'Ivoire gives CNPS rates and ceilings (a ceiling implying a SMIG of 75,000) but not the SMIG floor's cost to part-time workers; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Côte d'Ivoire CNPS cotisation assiette minimale SMIG temps partiel'; 'Ivory Coast social security contribution minimum base part-time workers' (3547 hits, titles checked); OpenAlex broad "Cote d'Ivoire personal income tax", "Cote d'Ivoire income tax wages", "Cote d'Ivoire tax system reform" (75 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (ivory-coast, 5 individual pages): 4 passages with the item's terms. Record: world/loopholes/africa_mena/search/CI-F2.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: floor: contribution rate 32 % at 0.05 AW vs 6 % at 0.5 AW. Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
