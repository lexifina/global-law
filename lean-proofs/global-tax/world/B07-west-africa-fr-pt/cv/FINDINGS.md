# CV findings (Cabo Verde (IRPS), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access B (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 1,800,000 CVE: threshold of the top (27,5 %) IRPS rate; a statutory threshold, not an average wage).

### F1 Married splitting and a second mínimo (art. 45.º 2., 46.º 2.)
- kind: loophole-known (design)
- status: proved

A one-earner married couple with 3 000 000 CVE pays 157 300 CVE less than the same earner single (`marriage_bonus`); splitting never costs more than separate assessment (`split_ok`).

### F2 Art. 46.º 1. can be read as a step tariff
- kind: statute-fault (ambiguity)
- status: proved (alternative reading)

'16,5% para rendimentos até 960.000$00; 23,1% para rendimentos superiores a 960.000$00 e até 1.800.000$00' does not say the rates apply by slice. Read on the whole income, one escudo above 960 000 costs 63 360 CVE (`whole_rate_notch`). The model uses band rates; the withholding tables (not read) would show which reading the administration applies.

### F3 Dependant credit capped at five persons (art. 54.º)
- kind: observation
- status: proved

5 000 CVE each, at most 25 000 (`dependant_cap`).

### F4 Model limits
- kind: model limitation
- status: open

category A withholding tables; INPS contributions; OE 2022-2024 not read (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Liberatory withholding on category A with optional englobamento (art. 28.º, 47.º): choose whichever is lower | partly modelled (englobamento only; tables not read) | no |
| L2 | Non-habitual residents: 10 % on high-value activities (art. 46.º 1. d)) | not modelled | no |
| L3 | Category D liberatory 20 % / 10 % instead of englobamento (art. 50.º) | modelled (20 %) | yes |
| L4 | Married splitting (art. 45.º 2.) | modelled; recreated (F1) | yes |
| L5 | Health and housing deductions of 10 % up to 25 000 / 12 500 CVE (art. 55.º) | not modelled (no input) | no |

Catalogued 5, recreated 2, not modelled 3.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: CV: IRPS (Lei 78/VIII/2014, republished by Lei 116/IX/2021) confirmed; access B.

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Portaria Conjunta nº 28/2024 (B.O. I Série nº 66, 16/07/2024) art. 2.º 1. a)
- INPS quotização 8,5 % of gross remuneration, deducted from category A (art. 28.º 2. a)). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/CvTax/Verify.lean` (imported by the `CvTax` library and built; each guard evaluates `CvTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/CV.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (amount updated by W5) | Married splitting and a second mínimo: a one-earner married couple with 3,000,000 keeps 146,081 more than the earner single (157,300 before the W5 INPS deduction; T: CvTax.marriage_bonus still proves 157,300 on the IRPS function). G: f1_marriage_bonus. S: src/CIRPS-Lei-78-VIII-2014.txt (arts. 45.º 2., 46.º 2., as cited by the model). |
| F2 | lead | Art. 46.º 1. readable as a step tariff (T: whole_rate_notch, 63,360 at 960,000): S: src/CIRPS-Lei-78-VIII-2014.txt:913 ('a) 16,5% para rendimentos até 960.000$00'). Needs the withholding tables. |
| F3 | explained | Dependant credit cap (T: dependant_cap). |
| F4 | explained | Model limits. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | INPS 8.5 % present. |
| Leads | explained | Rescan marriage bonus 203,061 = F1; no notch. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Married splitting and a second mínimo | household-unit effect | **new**: PwC Cabo Verde: no passage on married couples or joint taxation; OpenAlex: nothing on Cabo Verde's IRPS. | 2026-11-20: OpenAlex specific queries 'Cabo Verde IRPS casados tributação conjunta quociente'; 'Cape Verde personal income tax married couples joint taxation' (64 hits, titles checked); OpenAlex broad 'Cabo Verde personal income tax', 'Cabo Verde income tax wages', 'Cabo Verde tax system reform' (75 records, titles and abstracts grepped, 4 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (cabo-verde, 5 individual pages): 0 passages with the item's terms; Crossref IMF prefix 10.5089 'Cabo Verde tax policy' (8285 records, titles only). Record: world/loopholes/africa_mena/search/CV-F1.json |

<!-- L1-VERIFICATION END -->
