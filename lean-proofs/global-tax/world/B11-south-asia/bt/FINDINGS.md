# Bhutan (BT) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 The top row of the tax table prints Nu 242,499 where the bands give 242,500
- kind: statute-fault
- Part III s. 14 as amended 2020: 'Nu. 242,499.00 plus 30% of the amount by which the total net taxable income exceeds Nu.1,500,000.00'; 117,500 + 25 % x 500,000 = 242,500 (the Dzongkha text prints ༢,༤༢,༤༩༩ too). Read literally, the tax is 242,500 at 1,500,000 and 242,499 at 1,500,001: it falls by one ngultrum. The model uses the band sums by default; `--printed` applies the literal table.
- provisions: ITA 2001 Part III s. 14 (as amended by the Income Tax (Amendment) Act 2020)
- Lean: BtTax.printed (#guard)
- status: model result (build phase)

### F2 Surcharge cliff: 10 % of the whole tax once the tax reaches Nu 1,000,000
- kind: loophole-known
- s. 14 A: 'Surcharge at the rate of 10 percent shall be applicable on Personal Income Tax amount if the annual Personal Income Tax is equal to or more than Nu.1,000,000'. Net taxable income 4,024,998 pays 999,999; 4,024,999 pays 1,000,000 + 100,000. Beyond the scanners' 2.5 x scale grid; proved by #guard.
- provisions: ITA 2001 Part III s. 14 A
- Lean: BtTax.surcharge (#guard)
- status: model result (build phase)

### F3 The 2001 original table referred the 20 % row to the wrong threshold
- kind: statute-fault
- The 2001 text (Global law, OAG copy): 'Nu.52,500 plus 20 percent of the amount by which total taxable income exceeds Nu.250,000' for incomes between 500,000 and 1,000,000; the bands require 500,000. Superseded by the 2020 amendment; recorded as a historical drafting fault.
- provisions: ITA 2001 (original) Part III s. 14 row 4
- Lean: -
- status: model result (build phase)

### F4 Basic exemption written twice
- kind: reading
- s. 4.1: 'Nu. 300,000 per annum of the net taxable amount ... shall be exempted ... as a basic exemption'; s. 14: 'does not exceed Nu.300,000.00 Nil'. Read literally, 600,000 would be untaxed; the model reads one exemption (the nil band), as the 2001 original (100,000 in both places) suggests.
- provisions: ITA 2001 Part III ss. 4.1, 14
- Lean: BtTax.sched
- status: model result (build phase)

### F5 Pensions exempt; dividends exempt up to 30,000; interest outside PIT
- kind: loophole-known
- s. 5.3 (2020) exempts pension income; s. 8.3 exempts dividends to Nu 30,000; interest left the PIT base when s. 4.2 (d) was repealed in 2016. Income in these forms is taxed less than salary (dividends bear 10 % TDS under the corporate rules, not modelled).
- provisions: ITA 2001 Part III ss. 4.2, 5.3, 8.3
- Lean: -
- status: model result (build phase)

### F6 Global law holds only the 2001 original
- kind: record-note
- bhutan/national/acts/act/2001/income-tax-act-of-the-kingdom-of-bhutan is the 2001 text (basic exemption Nu 100,000, top rate 25 %), not the DRC's fourth edition; the 2020 amendments and the ITA 2025 are not in the record.
- provisions: Global law bhutan/national/acts
- Lean: -
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Keep PIT below Nu 1 m (surcharge cliff) | s. 14 A | recreated (guard) |
| Each spouse taxed separately: split income | s. 2.1 | recreated (scanner unit family) |
| Education deduction up to 350,000 per child | s. 12.2, r. 36 (3) | modelled (optional btEducation) |
| Insurance premium deduction (100 % / 50 % up to 50,000) | r. 36 (1) | not modelled |
| Donations up to 5 % of adjusted gross income | s. 12.1, r. 36 (2) | modelled |
| Pension and interest outside the base | ss. 4.2, 5.3 | modelled (excluded) |

Catalogued 6, recreated 2, not modelled 1. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: DRC PIT guides and the 2025 TDS schedule (referee values: deferred), the Rules on the ITA 2025, literature on Bhutan's 2020 reform: not checked. Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

## Round D4 (improvement agent, 2026-11-20): income year 2026 under the Income Tax Act of Bhutan 2025

### D4-1 Income year 2026 added (Income Tax Act of Bhutan 2025 and its Rules); 2025 untouched
- kind: model-extension
- Schedule 1 para 1: nil to 300,000; 5 % to 500,000; 10 % to 750,000; 15 % to 1,200,000; 20 % to 2,000,000; 25 % to
  3,500,000; 30 % above (the printed fixed amounts 10,000 / 35,000 / 102,500 / 262,500 / 637,500 equal the band sums:
  #guards, unlike the 2001 table's 242,499). s. 44 employment deduction min(15 %, Nu 150,000). s. 160 child credit
  1,000 / 1,250 / 5,000 / 10,000 (non-refundable, s. 162; one parent per child, Rules 148-150). Schedule 6: education
  (s. 161 election), donations (5 %), health contribution (para 9). Interest and dividends of individuals: final
  withholding at 10 % above Schedule 3's exemptions (400,000 fixed-deposit interest; 300,000 dividends). No surcharge
  (the 2001 Act's s. 14 A is gone). Rules on the ITA 2025 (DRC, January 2026; law/d4/, sha256 3798a629...): Rules 47-50,
  61-64, 148-150, 153 read; Annexure I (withholding tables) deliberately not opened (referee dataset).
- provisions: ITA 2025 ss. 2, 10, 24 (4), 44, 160-162, 280; Schedules 1, 3, 6; Rules 47-50, 148-150
- Lean: BtTax.sched2026, printed2026, empDeduction, childCredit, person2026, assignCredits, compute2026 (#guards)
- status: model extended (years 2025, 2026)

### D4-2 Statute observations for 2026 (leads)
- kind: fact
- The employee's own NPPF/provident-fund contribution, deductible under the 2001 Act's Rules (r. 35), has no deduction in
  the 2025 Act or its Rules (only the employer's contribution is excluded from income, s. 24 (4)): a rise in taxable
  income for every NPPF member unless a later notification restores it. The threshold for the 10 % band moved from
  400,000 to 500,000 with a new 5 % band, and the top 30 % band from 1.5 m to 3.5 m.
- status: model result (D4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | tax falls by 1 BTN at 1,500,001 under the printed table. exe (--printed) and #guard L1BT.F1. Evidence: exe + Lean `L1BT.F1` (`world/loopholes/rest/lean/L1BT.lean`, 1 #guard): it(b)-it(a) = -1; statute re-read: `law/Rules-on-the-Income-Tax-Act-Fifth-Edition.txt`. |
| F2 | loophole | model-proved | 100,001 BTN for one ngultrum of taxable income at 4,024,999 (2025; the 2025 Act drops the surcharge for 2026). exe and #guard L1BT.F2; re-found by the fresh scan (1,364 %). Evidence: exe + Lean `L1BT.F2` (`world/loopholes/rest/lean/L1BT.lean`, 1 #guard): tot(b)-tot(a) = 100001. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | statute-fault | explained | Recorded statute-fault with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F4 | reading | lead | Reading (reading): open as the builder left it; no amount depends on it in L1. |
| F5 | loophole | explained | Exempt pensions and dividends (published exemptions; income-type scan +30 %). |
| F6 | record | explained | Record (record-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| D4-1 | record | explained | Record (model-extension): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| D4-2 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BT.json`): METR 1,364 %, notch 100,000 and timing 99,850 = F2; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F5).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 22.0 % (Income Tax Act of Bhutan 2025: 'The taxable income of a company for an Income Year is taxed at 22 per cent' (law/Income-Tax-Act-of-Bhutan-2025.txt:14095)); at a profit of 3 AW the best split costs 27.9 % of the profit, all salary 27.9 %, all dividends 40.6 % (employer contributions: not included); dividends beat salary once employer contributions exceed 28 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
