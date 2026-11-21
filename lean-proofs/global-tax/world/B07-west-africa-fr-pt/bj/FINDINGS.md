# BJ findings (Benin (ITS with ORTB levy, IRCM, IRF), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access B (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 6,000,000 XOF: 12 x 500 000 F, the threshold of the top (30 %) monthly ITS band; a statutory threshold, not an average wage).
Scanner leads: single|none: max 35.0 %, average 35.0 % (top 30.0 %) from 720,000 to 732,000 (0.12-0.122 AW); causes: taxableIncome, ortb, its; single|dividends_1AW: max 35.0 %, average 35.0 % (top 30.0 %) from 720,000 to 732,000 (0.12-0.122 AW); causes: taxableIncome, ortb, its; single_parent_2|none: max 35.0 %, average 35.0 % (top 30.0 %) from 720,000 to 732,000 (0.12-0.122 AW); causes: taxableIncome, ortb, its; single_parent_2|dividends_1AW: max 35.0 %, average 35.0 % (top 30.0 %) from 720,000 to 732,000 (0.12-0.122 AW); causes: taxableIncome, ortb, its

### F1 The June ORTB levy is a 3 000 F notch at 60 000 F (art. 125 2))
- kind: loophole-new (structure)
- status: proved

The 3 000 F June levy is waived when the month's pay is within the first band: one more franc costs 3 000 F (`june_notch`; on an even annual wage the notch is at 720 000 F, `annual_notch`). The scanner finds a 35 % METR band and a 2 999 F net fall at 720 001 F.

### F2 No family relief and no deductions in the ITS (arts. 122-125)
- kind: observation (design)
- status: modelled

The 2021 code taxes gross monthly pay; family size and social contributions change nothing. A household's ITS is the sum of its earners' ITS.

### F3 Pensions not listed in art. 119
- kind: reading
- status: reading

Art. 119 lists salaries, end-of-career indemnities and directors' pay; pensions are not mentioned. The model leaves them untaxed (reading).

### F4 Model limits
- kind: model limitation
- status: open

LF 2024-2025 not reached; CNSS employee contribution; IBA (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Employer collective health-insurance premiums and training costs outside the base (art. 124) | not modelled | no |
| L2 | Professional athletes' and artists' pay exempt up to 4 × SMIG (art. 124 4)) | not modelled | no |
| L3 | Dividends 10 % (5 % listed) vs ITS up to 30 % (art. 86) | modelled; income-type scanner | yes |
| L4 | Exceptional pay 'atténuation' (art. 126) | not modelled | no |
| L5 | Keeping June pay at or below 60 000 F (art. 125 2)) | recreated (F1) | yes |

Catalogued 5, recreated 2, not modelled 3.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: BJ: ITS confirmed (CGI Loi 2021-15); no family relief; access B.

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS page "Procédure de recouvrement des cotisations" (cnss.bj, fetched 2026-11-20): "Pension : 10 % dont : 6.4 % à la charge de l'employeur 3.6 % à la charge du salarié", base "l'ensemble des rémunérations"; official secondary (rate décret under Code SS 2003 art. 24 2) not reached); CGI 2023 arts. 120, 122, 124
- CNSS salarié 3,6 % of all remuneration (pension branch, no ceiling), reported, not deducted (ITS base is gross pay, CGI art. 122). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS rate décret (Code de sécurité sociale 2003 art. 24 2)) not reached: rate from the CNSS page. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/BjTax/Verify.lean` (imported by the `BjTax` library and built; each guard evaluates `BjTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/BJ.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | June ORTB levy: on an even annual wage, 12 F more a year above 720,000 (June pay above 60,000) costs 2,988 of net (the 3,000 levy). Below the rescan's 0.05 %-of-scale reporting line (scale 6 M), but the band 720,000-732,000 at 38.6 % METR is it. G: f1_june_ortb_notch; T: BjTax.june_notch, annual_notch. S: src/CGI-2023.txt:2575 (art. 122: '0% pour la tranche inférieure ou égale à 60 000 francs CFA'); art. 125 2) waiver as cited by the model. |
| F2 | explained | No family relief in the ITS: design. |
| F3 | lead | Pensions not listed in art. 119: reading (untaxed in the model). |
| F4 | explained | Model limits. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | CNSS 3.6 % present (25,920 at 720,000). |
| Leads | explained | Rescan: band 720,000-732,000 = F1; split gain 938,000 = individual ITS; income-type wedges for self-employment, pensions and gains are model gaps. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: June ORTB levy of 3,000 F once June pay passes 60,000 | cliff or notch | **new**: Nothing found (no PwC page for the country; OpenAlex: a 2017 'Benin' country report, nothing on the ORTB levy). | 2026-11-20: OpenAlex specific queries 'Bénin impôt sur les traitements et salaires redevance ORTB'; 'Benin wage tax ORTB levy' (1 hits, titles checked); OpenAlex broad 'Benin personal income tax', 'Benin income tax wages', 'Benin tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Benin tax policy' (8367 records, titles only). Record: world/loopholes/africa_mena/search/BJ-F1.json |

<!-- L1-VERIFICATION END -->
