# Solomon Islands (SB) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The Fifth Schedule gives a rate per 'Income Bracket' without saying 'on the excess': read as a slab tariff it jumps $1,800 at 15,000 above the exemption
- kind: statute-fault
- Fifth Schedule 'Income Bracket | Rate | $1 to $15,000.00 | $0.11 | $15,001.00 to $30,000.00 | $0.23 ...'; s 32 'charged at the rates specified in the Fifth Schedule'. Graduated (default): 1,650 at 15,000; slab: 1,650 at 15,000 and 3,450 at 15,001; +3,000 at 60,001 (#guard).
- provisions: ITA ss 32, Fifth Schedule
- Lean: SbTax.sched, slabTax (#guard)
- status: modelled (switch sbReading)

### F2 For 27 years the 1996 and 1998 amending Acts pointed at section and Schedule numbers of the superseded Cap. 61, so parts of them failed; the Legislation Amendment, Repeal and Validation Act 2023 repaired them only from 5 February 2024
- kind: gov-error
- Reprint endnotes: the two Amendment Acts of 1996 and the Amendment Act of 1998 'made reference to sections and Schedules in the version of the Income Tax Act (Cap. 61) which predated the 1996 Consolidated version ... Therefore, not all amendments were valid'; LN 84 of 1997 'the substitution fails'; LN 16 of 2018 'the amendment of the Sixth and Seventh Schedule by this LN fails'; corrected by Act No. 17 of 2023 (commenced 5 February 2024).
- provisions: ITA reprint 2024 endnotes; Act No. 17 of 2023
- Lean: -
- status: recorded (official reprint)

### F3 The personal exemption is 'entitled ... for a year' but 'applies only to payments made under tax deduction provisions other than section 38'
- kind: statute-fault
- s 28(1), (1A): the exemption is tied to the deduction (PAYE) provisions; an individual with business or rental income only and no PAYE payments may be read as having no exemption. Model: exemption applied to all chargeable income of resident individuals.
- provisions: ITA s 28(1), (1A)
- Lean: SbTax.person
- status: documented reading

### F4 NPF contributions are on complete dollars and stop below $20 a month
- kind: statute-fault
- SINPF Act s 13(1) proviso (a)(i) 'earned less than $20.00'; Second Schedule 'five cents in respect of each complete dollar' (#guard). Minor notch ($1 at $20 a month).
- provisions: SINPF Act s 13(1), Second Schedule
- Lean: SbTax.npfMonthCents (#guard)
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Split income with a spouse (two $30,080 exemptions) | recreated: filing-unit scanner: 17,440 at 4 x scale | ITA s 28 |
| K2 | Income outside PAYE may lose the exemption (s 28(1A)) | not modelled: reading | ITA s 28(1A) |
| K3 | Dividends taxed with a credit for company tax (s 36) | not modelled | ITA s 36 |
| K4 | Business income at 0.5 % of turnover for s 19(1) persons (s 35) | not modelled | ITA s 35 |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 30,080, the personal exemption)
- #guard on both readings and the NPF rules
- reprint endnotes (list of legislation and amendments) read in full for s 28, s 32 and the Fifth Schedule
- Internet Archive listing of PacLII sb consolidated and numbered acts (SINPF Acts 1988, 1990, 1993, 2018)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 1,800 SBD at the 15,000 bracket edge under the slab reading. exe (sbReading slab) and #guard L1SB.F1. Evidence: exe + Lean `L1SB.F1` (`world/loopholes/rest/lean/L1SB.lean`, 1 #guard): it(b)-it(a) = 1800; statute re-read: `law/ita.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | gov-error | explained | Recorded gov-error with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F3 | reading | explained | Reading. |
| F4 | statute-fault | model-proved | SbTax #guard (model build); minor. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/SB.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
