# Sri Lanka (LK) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 Dividends are a final 15 % payment while salary reaches 36 % + 8 % EPF
- kind: loophole-known
- s. 88 (1A)(aa) (Act 45 of 2022) makes dividends paid by a resident company final withholding payments; First Schedule para 10 (1)(d)(v): 15 %. A person with 10 m of salary pays 2,472,000 + 800,000 EPF = 3,272,000; with 1.8 m salary (covered by the relief) and 8.2 m dividends: 1,230,000 + 144,000 EPF = 1,374,000 (before company tax at 30 %, para 4, which the household model does not see). Capital gains on investment assets are taxed at 10 % (para 1 (2)(a)).
- provisions: IRA s. 88 (1A)(aa); First Schedule paras 1 (2)(a), 10 (1)(d)(v)
- Lean: lktax households sal10m / sal1.8m+div8.2m
- status: model result (build phase)

### F2 No notches: a smooth schedule with a 1.8 m relief; top marginal 44 %
- kind: fact
- The fine grid and the generic scanners find no net-income falls; the highest METR is 36 % tax + 8 % EPF (no EPF ceiling).
- provisions: First Schedule para 1 (1D); Fifth Schedule para 2 (a)(v)
- Lean: LkTax.sched
- status: model result (build phase)

### F3 A rent band boundary fixed by amendment: 'exceeds or is equal to' vs 'not exceed'
- kind: statute-fault
- Act 45 of 2022 put rent payments 'where the aggregate payment does not exceed Rs. 100,000 per month - 0%' and 'exceeds or is equal to Rs. 100,000 per month - 10% on full amount' side by side (para 10 (1)(d)(i), (iii)): exactly 100,000 fell in both. Act No. 4 of 2023 s. 18 (2) replaced 'exceeds or is equal to' by 'exceeds'. A further all-or-nothing feature remains: rent of 100,001 a month bears 10 % on the full amount.
- provisions: First Schedule para 10 (1)(d)(i), (iii); Act 45/2022 s. 33 (6); Act 4/2023 s. 18 (2)
- Lean: -
- status: model result (build phase)

### F4 The official EPF Act copy still prints 6 % / 9 %
- kind: gov-error
- epf.lk serves 'act_of_1958' (Cap. 623 edition): 'six per centum' (employee) and 'nine per centum' (employer), while the EPF Department's own pages state 8 % and 12 %. A reader of the Act on the Fund's website gets the wrong rates; the amending instruments are not linked.
- provisions: EPF Act No. 15 of 1958 s. 10 (Cap. 623 text) vs epf.lk/?p=171
- Lean: LkTax.epfRate
- status: model result (build phase)

### F5 Act No. 11 of 2026 changes the 2025/26 rules after the year ended
- kind: fact
- Act 11/2026 (certified June 2026) inserts s. 52A (life-insurance receipts excluded) and amends the Fifth Schedule with effect from 1 April 2025, and other sections from 2018, 2023, 2024: retroactive amendments to closed years. None changes the amounts used here.
- provisions: Act 11 of 2026 s. 1 (3) Table
- Lean: -
- status: model result (build phase)

### F6 The 'as in force' record shows the 2017 rates for 2025
- kind: record-note
- Global law's read_law of the First and Fifth Schedules 'as in force on 2025-10-01' returns the 2017 wording (4-24 %, relief 500,000), because the Sri Lankan amending acts are stored as separate acts and not applied to the principal act. Reported for the record keeper (not a government error).
- provisions: Global law sri-lanka/national/acts/act/2017/024/schedule-01.md, schedule-05.md
- Lean: -
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Pay dividends (15 % final) instead of salary | s. 88 (1A)(aa), para 10 | recreated (households) |
| Realise gains on investment assets (10 %) | para 1 (2)(a) | modelled (10 %) |
| Rent relief 25 % of rental income | Fifth Schedule para 2 (c) | modelled |
| Foreign-currency service income capped at 15 % | para 1 (6) | not modelled |
| Terminal benefits at concessionary rates | para 1 (2)(b) | not modelled |
| Donations to approved charities (1/3 of income or 75,000) | Fifth Schedule para 1 (a) | modelled |
| Income splitting with a spouse (individual taxation, two reliefs) | s. 52, Fifth Schedule para 2 (a) | recreated (scanner unit family) |

Catalogued 7, recreated 2, not modelled 2. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: IRD Sri Lanka guides and PAYE tables for 2025/26 (referee values, deferred to the dataset phase), IMF programme documents on the 2025 tax changes, practitioner guides: not checked (no web search). Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 1,898,000 LKR: 10 M of salary costs 3,272,000 (tax + EPF), 1.8 M salary + 8.2 M dividends 1,374,000 (before 30 % company tax). exe and #guard L1LK.F1. Evidence: exe + Lean `L1LK.F1` (`world/loopholes/rest/lean/L1LK.lean`, 2 #guard): tot(a) = 3272000; tot(b) = 1374000. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F2 | fact | explained | Fresh scan: no notch. |
| F3 | statute-fault | explained | Rent withholding all-or-nothing at 100,000 a month (not modelled). |
| F4 | gov-error | explained | Stale EPF Act copy (builder). |
| F5 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F6 | record | explained | Record (record-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/LK.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F1).
