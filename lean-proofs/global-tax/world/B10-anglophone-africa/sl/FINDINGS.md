# Sierra Leone (SL) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The Redenomination Regulations both convert old amounts (/ 1,000) and 'deem' amounts in earlier Acts to be new leones
- kind: statute-fault
- S.I. 4 of 2024 reg. 3(6): 'all amounts expressed in the existing currency shall automatically be converted into the redenominated currency' (face value divided by one thousand, reg. 1); reg. 10(3): 'any amount expressed in the existing currency provided for in an Act of Parliament enacted prior to the appointed date shall be deemed to be an amount expressed in the redenominated currency'. Read alone, 10(3) would turn the Income Tax Act's Le 7,200,000 exemption into NLe 7,200,000 (a thousand times larger, exempting almost every wage). The model follows reg. 3(6) (NLe 7,200).
- provisions: S.I. 4 of 2024 regs. 1, 3(6), 10(3); ITA First Schedule Part I
- Lean: SlTax.sched
- status: statute fault (reading)

### F2 The Finance Act 2019 printed the 20 % band as starting at 'Le12,000,0000'
- kind: statute-fault
- Finance Act 2019 s. 11 table: '>Le12,000,0000 but not>Le18,000,000 | 20%' (120,000,000 as printed, above the band's own upper limit). Superseded from 1 January 2020 by Finance Act 2020 s. 21; recorded as a drafting error in law then in force for 2019.
- provisions: Finance Act 2019 s. 11
- Lean: -
- status: recorded (historic)

### F3 The individual bands have not moved since 2020 (NLe 7,200 a year exempt)
- kind: statute-fault
- Finance Acts 2021-2026 read: Part I unchanged; the redenomination did not change real values. Statutory top rate 30 % (scanner 30.6 % with whole-leone rounding on a small scale).
- provisions: Finance Acts 2021-2026
- Lean: SlTax.sched
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Contributions to a complying retirement fund deductible up to 30 % of employment income | recreated: input nassitEmployee | ITA s. 38(2) |
| K2 | Shift income to a spouse (individual taxation) | recreated: split gains | ITA s. 4 |
| K3 | Benefits and allowances valued below cost | not modelled | ITA (employment income and benefits provisions) |

## Step 5: what was searched

- kernel scanners with scale NLe 28,800
- Finance Acts 2018-2026 read for First Schedule Part I
- Redenomination Regulations read in full

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (statute)
- provisions: National Social Security and Insurance Trust Act 2001 (Act No. 5 of 2001) s. 25 (1)-(2), s. 2 "earning", s. 20 (2) (sierra-leone.org scan, OCR)
- NASSIT worker 5 % of earnings (no ceiling), deducted (Act s. 20 (2); within ITA s. 38 (2)); input nassitEmployee still overrides. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: NASSIT Act amendments after 2001 not checked. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

### W5S4-1 SaloneHCM payroll engine (spyrate111): monthly bands 800 / 2,200 / 3,600 / 5,000 / 7,500 SLE, top 35 % (W5 review pass 4, 2026-11-20)
- kind: software-error
- `sl_open_salonehcm_spyrate111_grid`: Income Tax Act 2000 First Schedule Part I as replaced by Finance Act 2020 s. 21, / 1,000 by the Redenomination Regulations 2024: 600 / 1,200 / 1,800 / 2,400 NLe a month, 0 / 15 / 20 / 25 / 30 % (F3). Dev: model above by 360-3,960 in 939 of 1,035 cases; the other two SL tools (Melo034, AlphaDumbuya) match the model to 1-2 leones; NASSIT 5 % agrees.
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1, F2, F3 | explained | Redenomination double reading; 2019 typo; unchanged bands: statute faults/records. |
| W5A-1, W5S4-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan bands 'above the top rate' (35-37 % max, 33.5 % avg) are whole-leone rounding. |

<!-- L1-VERIFICATION END -->
