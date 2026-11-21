# BF findings (Burkina Faso (IUTS, IRF, IRCM, CNSS), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access B (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 3,000,000 XOF: 12 x 250 000 F, the threshold of the top (25 %) monthly IUTS band; a statutory threshold, not an average wage).
Scanner leads: second_earner_2|none: max 96.8 %, average 96.8 % (top 22.8 %) from 0 to 6,000 (0.0-0.002 AW); causes: iuts, taxableIncome; second_earner_2|dividends_1AW: max 96.8 %, average 96.8 % (top 22.8 %) from 0 to 6,000 (0.0-0.002 AW); causes: iuts, taxableIncome

### F1 The family reduction is a share of the tax, so it is worth most to the best paid (art. 113)
- kind: loophole-known (design)
- status: proved

Four charges save 14 % of the tax: 718 F a month at a 100 000 F wage and 45 420 F at 2 000 000 F (`charges_regressive`). A fixed amount per charge (as CI's RICF) would give the same relief to every family.

### F2 A spouse who starts earning costs the household one charge (art. 113 2) c))
- kind: loophole-new (structure)
- status: scanner

A spouse without income is a charge of the earner; once she earns, the charge goes. The scanner's second-earner family shows a METR of 96,8 % on the first 6 000 F and a 5 483 F loss at the first franc.

### F3 Lower abattement for higher grades (art. 111)
- kind: observation
- status: modelled (option)

The professional abattement is 25 % of the base salary, 20 % for categories P, A, B and 1, 2, 6: the same pay is taxed more for a higher-grade employee (`"bfCategory": "superior"`).

### F4 The barème's printed gaps of 100 F (art. 112)
- kind: reading
- status: reading

Bands are printed '0 à 30.000', '30.100 à 50.000' ...: income between 30 001 and 30 099 F falls in no printed band. The model reads the limits as 30 000, 50 000, ... (continuous); a rounding of the monthly net to 100 F would also explain the print but no such rule is in arts. 109-113.

### F5 Model limits
- kind: model limitation
- status: open

LF 2025 not reached; CNSS ceiling not read; BIC/BNC, capital gains (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Housing, function and transport allowances exempt up to 20 %/5 %/5 % of pay with monthly caps of 75 000/50 000/30 000 F (art. 106 1)) | not modelled (no input) | no |
| L2 | Pensions exempt (art. 106 3)) | modelled | yes |
| L3 | Retirement and severance payments exempt (art. 106 5)-6)) | not modelled | no |
| L4 | Rents: 50 % flat abattement then 18/25 % (arts. 125-126) | modelled | yes |
| L5 | Investment income at 12,5 % (IRCM) against up to 25 % IUTS: pay the owner-manager in dividends (art. 140) | modelled; income-type scanner | yes |
| L6 | Family charges to the spouse with the higher tax (art. 113 3)) | modelled (to the higher earner) | yes |

Catalogued 6, recreated 4, not modelled 2.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: BF: IUTS confirmed (CGI loi 058-2017, édition 2023); access B (LF 2025 not reached).

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/BfTax/Verify.lean` (imported by the `BfTax` library and built; each guard evaluates `BfTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/BF.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Family reduction as a share of the tax (T: charges_regressive): a design choice (regressive in money), not a loophole. |
| F2 | confirmed | Second-earner trap: the spouse's first franc ends her charge: 21,959 of household net at a 3 M earner without children, 5,483 with two children (rescan second-earner notch). G: f2_spouse_charge_lost, f2_spouse_charge_lost_2kids. S: src/CGI-LF2023-b.txt:3533 (art. 113 1): 'il est pratiqué une réduction d'impôt pour charges de famille'); 113 2) c) (spouse without income) as cited by the model. |
| F3 | explained | Grade-dependent abattement (option bfCategory). |
| F4 | lead | Printed 100-F gaps in the barème: reading. |
| F5 | explained | Model limits. |
| Leads | explained | Rescan: the second earner's first-unit notch (5,483) = F2; marriage bonus 144,648 at 4 'AW' = the spouse charge; split gain 201,264 = individual taxation. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: The spouse's first franc ends her family charge | second-earner trap | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing on the IUTS family charge). | 2026-11-20: OpenAlex specific queries 'Burkina Faso IUTS charges de famille conjoint réduction'; 'Burkina Faso personal income tax family charges spouse' (553 hits, titles checked); OpenAlex broad 'Burkina Faso personal income tax', 'Burkina Faso income tax wages', 'Burkina Faso tax system reform' (75 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Burkina Faso tax policy' (8414 records, titles only). Record: world/loopholes/africa_mena/search/BF-F2.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 27.5 % (CGI art. 87: 'Le taux de l'impôt sur les sociétés est de 27,5 %' (src/CGI-LF2023-b.txt:2519)); at a profit of 3 AW the best split costs 19.8 % of the profit, all salary 19.8 %, all dividends 36.6 % (employer contributions: not included); dividends beat salary once employer contributions exceed 28 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
