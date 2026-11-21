# Trinidad and Tobago (TT) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The Third Schedule's low-income relief (para. 2) no longer fits the rates: tax falls when income rises and jumps by up to TT$1,090 for one dollar
- kind: statute-fault
- Para. 2 limits or reduces the tax for resident individuals with chargeable income 5,000-8,500 using amounts calibrated to an old graduated scale ('limited to $280 plus 31.2 per cent', '$736 plus 59.8 per cent'); with today's flat 25 % it produces a saw-tooth: tax 247.50 at 5,500 then 687.62 at 5,501 (+440), 750 at 6,000 then 280.31 at 6,001 (-470), 592 at 7,000 then 1,400.20 at 7,001 (+808), 1,600 at 8,000 then 736.59 at 8,001 (-863), 1,035 at 8,500 then 2,125.25 at 8,501 (+1,090). After the 90,000 allowance and 70 % of NIS, this hits wage earners on about TT$95,000-101,750 a year. The schedule's amendment list ends '10 of 2016 and 16 of 2021' and still carries the relief. Scanner: METR 128.6 % around 0.61 'AW' (100,000), notch 1,089 at 101,743.
- provisions: ITA Third Schedule Part I paras. 1-2; s. 18
- Lean: TtTax.taxCents (#guard at each step)
- status: modelled; reproduced by the scanner

### F2 Earning TT$200 a week instead of TT$199 costs about TT$1,048 a year: NIS and the health surcharge both start in full at the insurability threshold
- kind: statute-fault
- NIS Act s. 20(2)(a)(iv): remuneration below $200 a week is uninsurable (no contribution); at $200 the employee pays class I $11.90 a week, and the Health Surcharge Act s. 3(1)(a) applies only to employed persons liable to NIS, at $8.25 a week once weekly emoluments exceed $109. Net income: 10,399 -> 10,399; 10,400 -> 9,352 (exe). Continuing employees below $200 pay class I under s. 20(3)(d) (a reading: the model treats a new employee).
- provisions: NIS Act ss. 20(2)(a)(iv), 20(3)(d), Table A9; Health Surcharge Act s. 3(1),(4)
- Lean: TtTax.person, TtTax.nisWeek
- status: modelled; scanner METR 128 % at 0.06-0.065 AW

### F3 Only 70 % of NIS contributions is deductible, and the deduction shares one TT$60,000 cap with pension contributions
- kind: loophole-known
- s. 31(1)(c) 'seventy per cent of the annual amount of the contribution'; s. 28(15) caps deductions under ss. 27(1)(c)-(e), 31(1) and 28 at 60,000 in aggregate. Approved pension contributions are a tax shelter up to that cap (not modelled: no input).
- provisions: ITA ss. 27, 28(15), 31(1)(c)
- Lean: TtTax.person
- status: modelled (NIS part)

### F4 The total-income exemption of TT$60,000 (s. 8(1)(k)) is dead letter beside the TT$90,000 personal allowance
- kind: statute-fault
- s. 8(1)(k) exempts the income of a resident individual whose total income does not exceed 60,000; since Act 21 of 2022 the s. 18 allowance alone is 90,000, so the exemption never changes the tax (kept in the model). A cross-reference left behind when the allowance rose.
- provisions: ITA ss. 8(1)(k), 18
- Lean: TtTax.person
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Contribute to an approved pension plan or deferred annuity (deductible within the 60,000 aggregate cap) | not modelled: no input | ITA ss. 28, 28(15) |
| K2 | Tertiary education expenses up to 72,000 (60,000 for spouses together) | not modelled | ITA (tertiary education deduction: 'not exceeding the sum of seventy-two thousand dollars'; 60,000 for both spouses) |
| K3 | First-time home acquisition allowance 30,000 a year for five years | not modelled | ITA s. 18A |
| K4 | Shift income to a spouse (each spouse has a 90,000 allowance; individual returns) | recreated: filing-unit scanner | ITA ss. 17, 18 |
| K5 | Take distributions (8 % withholding) rather than salary as an owner-manager | not modelled | Third Schedule Part II |
| K6 | Keep chargeable income just below 5,500 / 7,000 / 8,500 or just above 6,000 / 8,000 (para. 2 saw-tooth) | recreated: F1 | Third Schedule Part I para. 2 |

## Step 5: what was searched

- kernel scanners via world/tools/scan_world.py with scale 163,200 (NIS maximum insurable monthly earnings x 12)
- direct household checks with the exe at the NIS threshold and the para. 2 steps
- Global law provision history of the Third Schedule, s. 18 and the NIS First/Second Schedules; the NIS Act's own notes (LN 31/32 of 2006 anomalies)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 1,090 TTD for one dollar at 101,743-101,744 of pay; 440 at 98,397. exe and #guard L1TT.F1; re-found by the fresh scan. Evidence: exe + Lean `L1TT.F1` (`world/loopholes/rest/lean/L1TT.lean`, 2 #guard): tot(b)-tot(a) = 1090; tot(d)-tot(c) = 440; statute re-read: `law/ita_75-01_2025-06-03.txt`; model Lean: TtTax.taxCents (#guards). Known/new: **new**: Web search 10 found only the Act (laws.gov.tt, ird.gov.tt); no description of the para. 2 saw-tooth; Crossref none. |
| F2 | statute-fault | confirmed | 1,048 TTD a year at 200 a week (10,399 -> 10,400 a year). exe and #guard L1TT.F2. Evidence: exe + Lean `L1TT.F2` (`world/loopholes/rest/lean/L1TT.lean`, 1 #guard): tot(b)-tot(a) = 1048; statute re-read: `law/nis.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | fact | explained | 70 % deductibility (fact). |
| F4 | statute-fault | explained | Dead exemption (builder). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TT.json`): METR 128 % and notches 1,089 / 807 = F1; METR 128 % at 0.06 scale and notch 1,047 = F2; couple multiples.
