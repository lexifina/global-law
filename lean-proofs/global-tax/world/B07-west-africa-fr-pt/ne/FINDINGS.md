# NE findings (Niger (ITS, IRCM), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access B (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 3,600,000 XOF: 12 x 300 000 F, the upper limit of the 25 % monthly ITS band; a statutory threshold, not an average wage).
Scanner leads: single|none: max 58.3 %, average 27.4 % (top 23.3 %) from 2,080,800 to 14,400,000 (0.578-4.0 AW); causes: taxableIncome, its; single|dividends_1AW: max 58.3 %, average 27.4 % (top 23.3 %) from 2,080,800 to 14,400,000 (0.578-4.0 AW); causes: taxableIncome, its; single_parent_2|none: max 56.7 %, average 24.3 % (top 23.3 %) from 2,311,200 to 14,392,800 (0.642-3.998 AW); causes: taxableIncome, its; single_parent_2|dividends_1AW: max 56.7 %, average 24.3 % (top 23.3 %) from 2,311,200 to 14,392,800 (0.642-3.998 AW); causes: taxableIncome, its

### F1 The seventh dependant doubles the family abatement (art. 65)
- kind: loophole-new (structure)
- status: proved

Abatements are 5, 10, 12, 13, 14, 15 % for 1-6 charges and 30 % for 7: at 500 000 F a month the 7th charge saves 19 500 F a month, the 6th 1 500 F (`seventh_charge`).

### F2 No zero band: the ITS starts at the first franc (art. 66)
- kind: observation
- status: proved

The barème starts at 1 % from 0; a 2 000 F monthly pay pays 10 F (`no_zero_band`).

### F3 Rounding the monthly net to the thousand creates small net-income falls (art. 61)
- kind: loophole-new (rounding)
- status: scanner

Each 1 000 F step of the rounded base adds up to 350 F a month at once; on the annual grid the scanner finds net-income falls of up to 319 F (couple with two earners: 34 bands above 100 % METR).

### F4 A spouse who starts earning is no longer a charge (art. 64 2))
- kind: loophole-new (structure)
- status: scanner

The second-earner family loses 14 999 F at the first franc (METR 208 %).

### F5 Model limits
- kind: model limitation
- status: open

LF 2023-2024 not reached; CNSS employee contributions and the art. 60 1) deduction; IRF, BIC/BNC, capital gains (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Pensions of any kind exempt (art. 54 4)-7)) | modelled | yes |
| L2 | Long list of exempt allowances (art. 54 1)-32): desert-zone, mining bonuses, judicial allowance, ... | not modelled | no |
| L3 | Separate monthly taxation of exceptional pay on up to three supplementary payslips (art. 62) | not modelled (one even year) | no |
| L4 | Children counted up to 21 (25 if students) as charges (art. 64) | modelled (≤ 21) | yes |
| L5 | Dividends 10 % / bank interest 10 % instead of up to 35 % on pay (arts. 74, 80) | modelled; income-type scanner | yes |

Catalogued 5, recreated 3, not modelled 2.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: NE: ITS confirmed (CGI Loi 2012-37 as amended; LF 2025 Ord. 2024-59); access B.

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS "Guide de l'employeur" (Décembre 2019, cnss.ne): retraite 11,50 % = 5,25 % worker + 6,25 % employer, plafond annuel 6 000 000 F; official secondary (rate décret not reached); CGI arts. 60 1), 4)
- CNSS worker 5,25 % (retraite) of pay up to 6 000 000 F a year, deducted first under CGI art. 60 1) (6 % limit) before the 13 % abatement. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS SMIG floor (30 047 F a month) not applied; the rate décret not reached. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/NeTax/Verify.lean` (imported by the `NeTax` library and built; each guard evaluates `NeTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/NE.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (clarified) | The family abatement is 15 % for 6 charges and 30 % for 7: at 6 M a year the 7th charge saves 216,000 against 14,400 for the 6th. Children count 'dans la limite de six', so the 7th charge needs a spouse without income plus six children (a single parent cannot reach it). G: f1_seventh_charge, f1_sixth_charge; T: NeTax.seventh_charge. S: src/CGI-2013-MAJ-LF2022.txt:2456 ('ses enfants, dans la limite de six (6)'), :2463 ('un conjoint ne disposant pas de revenu'), :2474 ('7 charges 30%'). |
| F2 | explained | No zero band (T: no_zero_band): design. |
| F3 | explained | Rounding to 1,000 (art. 61): rescan bands above the top rate (58.5 % max, 28.5 % average from 2.2 M) are this rounding; falls up to a few hundred francs; not a loophole of money. |
| F4 | confirmed | Second-earner trap: the spouse's first franc ends her charge: 38,999 of household net at a 3.6 M earner (rescan with two children 14,999). G: f4_spouse_charge_lost. S: src/CGI-2013-MAJ-LF2022.txt:2463. |
| F5 | explained | Model limits. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | CNSS 5.25 % to 6 M present. |
| Leads | explained | Rescan notch at the second earner's first unit = F4; timing gain 42,360 = F3's rounding; split gain 359,520 = individual ITS. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: The seventh charge doubles the family abatement (15 % -> 30 %) | household-unit effect | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing on the 30 % abatement). | 2026-11-20: OpenAlex specific queries 'Niger impôt sur les traitements et salaires abattement pour charges de famille 30%'; 'Niger personal income tax family allowance seven dependents' (655 hits, titles checked); OpenAlex broad 'Niger personal income tax', 'Niger income tax wages', 'Niger tax system reform' (75 records, titles and abstracts grepped, 2 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Niger tax policy' (8377 records, titles only). Record: world/loopholes/africa_mena/search/NE-F1.json |
| F4: The spouse's first franc ends her charge | second-earner trap | **new**: Nothing found (no PwC page for the country; OpenAlex not answered for this item). | 2026-11-20: OpenAlex queries 'Niger impôt sur les traitements et salaires conjoint sans revenu charge de famille'; 'Niger personal income tax spouse dependent' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Niger tax policy' (8377 records, titles only). Record: world/loopholes/africa_mena/search/NE-F4.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 30.0 % (CGI art. 27: 'Le taux de l'impôt sur les bénéfices est fixé à 30%' (src/CGI-2013-MAJ-LF2022.txt:1592)); at a profit of 3 AW the best split costs 24.5 % of the profit, all salary 24.5 %, all dividends 37.0 % (employer contributions: not included); dividends beat salary once employer contributions exceed 22 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- ceilings.py: ceiling at 1.67 AW (contribution rate 5.3 -> 0.0 %, combined marginal 33 -> 28 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
