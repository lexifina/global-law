# Liberia (LR) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The table is in Liberian dollars while wages are often paid in US dollars
- kind: statute-fault
- s. 200(a)(3)(A) prints 'Taxable Income of— (Liberian Dollars)'; the Code's other amounts (e.g. 'US$500 or its Liberian Dollar equivalent') mix both currencies. Conversion of a US-dollar salary into the LRD table is left to an exchange rate outside the table; the household contract carries one currency (LRD).
- provisions: Revenue Code s. 200(a)
- Lean: LrTax.sched
- status: recorded

### F2 The standard deduction is built into the table as a zero bracket (s. 205(a)): no other personal or family allowance exists
- kind: model-fix
- s. 205(a): 'An annual standard deduction for a natural person, in an amount of up to $70,000, is reflected in the tax table ... as a zero bracket amount. No additional amount shall be deducted as a standard deduction.' Families with children pay the same as single persons (scanner: no unit effects).
- provisions: Revenue Code s. 205(a)
- Lean: LrTax.person
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Charitable contributions to qualifying organisations deductible | not modelled: charitable field not mapped | Revenue Code s. 205(b) |
| K2 | Shift income to a spouse (individual taxation) | recreated: split gains | Revenue Code s. 200(a) |

## Step 5: what was searched

- kernel scanners with scale 800,000 LRD
- all LRA-listed amending Acts 2024-2025 (OCR) checked for s. 200

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
| F1 | explained | LRD table for USD wages: statute fault (conversion outside the table). |
| F2 | explained | Standard deduction as a zero bracket: design. |
| Leads | explained | Rescan: nothing. |

<!-- L1-VERIFICATION END -->
