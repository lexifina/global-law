# GN findings (Guinea (ITS, pensions tax, IRCM), 2025)
Batch B07-west-africa-fr-pt, built 2026-11-20 03:57 UTC. Status: built, access B (no referee values used). Scanner output: `results/search/SUMMARY.md` (scale 60,000,000 GNF: 12 x 5 000 000 GNF, the upper limit of the 8 % monthly band; a statutory threshold, not an average wage).

### F1 Final monthly withholding: uneven pay is taxed more (arts. 63-64)
- kind: loophole-known (timing)
- status: proved

24 000 000 GNF paid as twelve months of 2 000 000 bear 600 000 GNF; paid in two months of 12 000 000 they bear 2 120 000 GNF (`uneven_pay`). Spreading pay evenly (or the reverse, for the State) matters.

### F2 No family relief (arts. 57-63)
- kind: observation (design)
- status: modelled

Family size changes nothing in the ITS.

### F3 Model limits
- kind: model limitation
- status: open

LF 2022-2024 not read; CNSS contributions and the art. 58 deduction; rents, business income (each listed in the exe's `unsupported`).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue)

| # | item (provision) | in the model | recreated by model/scanner |
|---|---|---|---|
| L1 | Interest on savings accounts and term deposits over 3 months exempt (art. 190 II) | not distinguishable in the contract | no |
| L2 | Final 15 % on dividends vs up to 20 % on pay (arts. 189-191) | modelled | yes |
| L3 | Spreading pay evenly across months (final monthly withholding) | recreated (F1) | yes |

Catalogued 3, recreated 2, not modelled 1.

## Step 5: what was searched

Literature NOT checked (no web-search budget this session): IMF Article IV / TADAT reports, the OECD 'Revenue Statistics in Africa' country notes, ATAF/FERDI and ICTD working papers on West African PIT, UEMOA directive commentaries, the West African tax-planning guides of the Big Four, and any official guidance (instructions, notes de service) beyond the texts cited. Searched instead: the statute text listed under Sources (every article on wages, pensions, family relief, investment income and rents), the kernel's generic scanners (results/search/), and the proved Lean statements in lean/*Tax/Theorems.lean. Novelty is never claimed: 'not found in the 0 external sources searched'.

Registry correction: GN: ITS under the 2021 CGI (L/2021/032/AN), not 'RTS'; access B.

### W5S-1 payroll_africa (CoaleTech; wronglaw grid): annual bands applied to the monthly wage (W5 review pass 3, 2026-11-20)
- kind: software-error
- `gn_open_payroll_africa_grid`: the app applies annual band limits to 12 x the monthly wage where the ITS is a monthly withholding on the month's pay (24,000,000 not in the texts). Dev: the app is 4-7 times the model (15,384,000: 2,434,440 vs 130,740; 271,680,000: 103.7 M vs 33.2 M); 0 / 289 exact.
- provisions: CGI 2021 arts. 58, 61-64 (monthly ITS)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS page "Cotisations sociales employeurs" (cnss.gov.gn, fetched 2026-11-20): plafond 2 500 000, plancher 550 000, 23 % = employeur 18 % + salarié 5 %; official secondary (the rate / plafond décrets under the Code 1994 arts. 32-33 not reached)
- CNSS employee 5 % of the monthly wage up to the 2 500 000 GNF plafond, deducted from the ITS base (art. 58). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS plancher (550 000 GNF a month) not applied; the rate / plafond décrets not reached. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/GnTax/Verify.lean` (imported by the `GnTax` library and built; each guard evaluates `GnTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/GN.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Final monthly withholding: 24 M as 12 x 2 M bears 600,000, as 2 x 12 M 2,120,000 (barème before the W5 CNSS deduction). G: f1_uneven_pay; T: GnTax.uneven_pay. S: src/Loi-2021-32.txt:780 (art. 64: 'application au revenu mensuel imposable des taux fixés à l'article 63'). Rescan timing_monthly: paying 4 'AW' in one month costs 17,965,000 more. |
| F2 | explained | No family relief: design. |
| F3 | explained | Model limits. |
| W5S-1, W5A-1 | explained (record of model/test work, not a loophole; kept as written) | CNSS 5 % to 2.5 M a month present. |
| Leads | explained | Rescan annual timing gain 528,000 = CNSS ceiling; F1 is in timing_monthly. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Final monthly ITS: uneven pay costs more | timing or bunching | **new**: Nothing found (no PwC page for the country; OpenAlex: nothing on Guinea's ITS). | 2026-11-20: OpenAlex specific queries 'Guinée impôt sur les traitements et salaires retenue mensuelle barème'; 'Guinea wage tax monthly withholding progressive' (318 hits, titles checked); OpenAlex broad 'Guinea personal income tax', 'Guinea income tax wages', 'Guinea tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Guinea tax policy' (8853 records, titles only). Record: world/loopholes/africa_mena/search/GN-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.5033 AW (contribution rate 5.0 -> 0.0 %, combined marginal 9 -> 5 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
