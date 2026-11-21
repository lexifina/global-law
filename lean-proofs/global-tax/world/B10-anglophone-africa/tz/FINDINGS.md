# Tanzania (TZ) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The NSSF Act's contribution table heads the employee's 10 % 'Employer's share deductible from wages by Employer'
- kind: statute-fault
- NSSF Act Cap. 50 R.E. 2023 First Schedule 'CONTRIBUTIONS FOR EMPLOYEES': columns 'Employer's share deductible from wages by Employer' (ten cents per shilling) and 'Statutory Contributions for each employee' (twenty cents). The Act defines 'employee's share' as 'that portion of a statutory contribution set out in the First Schedule to be the employee's share'. Read literally the Schedule names no employee's share; the model reads the 10 % column as the employee's share (the definition's sense).
- provisions: NSSF Act Cap. 50 s. 2, First Schedule
- Lean: TzTax.nssfMonth
- status: recorded (reading)

### F2 Gains on shares are taxed at 10 % within the individual's return while wages reach 30 %
- kind: loophole-known
- First Schedule para. 1(2)-(3): where total income includes net gains on shares and securities, 'the balance of the total income shall be taxed at the rate of ten percent'. Not modelled (gains unsupported); visible in the statute.
- provisions: ITA First Schedule para. 1(2)-(3)
- Lean: -
- status: catalogued

### F3 NSSF contributions reduce total income (s. 61): statutory top combined rate 37 % (30 % x 0.9 + 10 %)
- kind: model-fix
- s. 61(1)-(2) allows 'the actual contribution or the statutory amount required whichever is lesser'; scanner top-rate line 37.0 % at 10 x 12 M.
- provisions: ITA s. 61
- Lean: TzTax.person
- status: modelled; scan reproduces

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Realise share gains (10 % in the return) rather than earn wages | not modelled | First Schedule para. 1(2)-(3) |
| K2 | Retirement contributions to an approved fund reduce income up to the statutory amount | recreated: NSSF | ITA s. 61 |
| K3 | Presumptive tax for small businesses instead of the scale | not modelled | First Schedule para. 2 |
| K4 | Shift income to a spouse (individual taxation: 'The total income of each person shall be determined separately') | recreated: split gains | ITA s. 5(2) |

## Step 5: what was searched

- kernel scanners with scale 12,000,000 (start of the 30 % band)
- Finance Acts 2024, 2025 and 2026 read for amendments to the First Schedule
- printed fixed amounts proved with #guard

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
| F1 | explained | Mislabelled NSSF column: statute fault. |
| F2 | lead | 10 % on share gains within the return: not modelled. |
| F3 | explained | NSSF deductible: model fix. |
| Leads | explained | Rescan: no notch. |

<!-- L1-VERIFICATION END -->
