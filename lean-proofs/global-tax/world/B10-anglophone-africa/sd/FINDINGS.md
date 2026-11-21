# Sudan (SD) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The personal income tax thresholds in the published Act (9,090 + 120 + 240 pounds) are tiny: nearly every wage is taxed at 15 %
- kind: statute-fault
- Schedule III Sector (B) as printed with the note 'Act No. 25, 2013'. Whatever their unit (the table does not say monthly or annual), 9,450 pounds is a small amount of 2025 pay; either later laws changed them (not reached) or the exemption has eroded to nothing. Scanner: top rate 15 % (14.9 % with whole-pound rounding).
- provisions: Income Tax Act 1986 s. 30, Schedule III Sector (B)
- Lean: SdTax.sched
- status: recorded

### F2 Sector (B) does not state whether its amounts are monthly or annual
- kind: statute-fault
- The table reads 'For the 9,090 pounds | Nill | For the next 120 pounds | 5% ...'; s. 2 defines a twelve-month assessment year while employers withhold monthly (s. 41). Model: annual.
- provisions: Income Tax Act 1986 ss. 2, 30, 41, Schedule III
- Lean: SdTax.sched
- status: reading

### F3 When non-wage income exceeds a quarter of personal income, it is taxed on the business scale (Sector A: 15 % top) separately
- kind: loophole-known
- s. 30 proviso (ii): 'where the amount of income, other than personal income exceeds one-quarter of the amount of personal income, the tax due shall be calculated at the rates set forth in Sector (B) ... on the personal income, and at the rates set forth in Sector (A) ... on the income other than the personal income'. Not modelled.
- provisions: Income Tax Act 1986 s. 30
- Lean: -
- status: catalogued

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Split income so that non-wage income exceeds a quarter of personal income (two scales, two thresholds) | not modelled: F3 | s. 30 proviso |
| K2 | Industrial business income at 10 % | not modelled | Schedule III Sector (A)(c)(3) |

## Step 5: what was searched

- kernel scanners with scale 9,450 pounds
- English consolidation read for s. 30 and Schedule III

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1, F2 | explained | Tiny thresholds; monthly/annual unit unclear: statute faults. |
| F3 | lead | Non-personal income above a quarter on Sector A: not modelled. |
| Leads | explained | Rescan bands 'above the top rate' (22 % max, 15 % avg) are whole-pound rounding. |

<!-- L1-VERIFICATION END -->
