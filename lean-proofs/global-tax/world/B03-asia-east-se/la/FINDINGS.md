# Laos (LA) findings, B03-asia-east-se (rescue pass, 2026-11-20T11:11Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The amended law is 'in force from 1 September 2025' but reached the Official Gazette on 19 June 2026
- kind: statute-fault
- Art. 74 of the amended Law on Income Tax says it takes effect from 1 September 2025 'after the President issues the decree promulgating it and it is published in the Official Gazette'; the gazette lists its publication on 19 June 2026. Either the effective date is retroactive by nine months or it is the gazette date. The model follows the printed date (1 September 2025) and splits 2025 at month 9; a reader of the gazette's own dates would apply Law 67/NA to all of 2025.
- provisions: Law on Income Tax (amended 2025) art. 74; gazette record id 2597
- Lean: LaTax.monthTax
- status: model result

### F2 The 2025 law cuts every taxpayer's salary tax by at most 60,000 kip a month
- kind: fact
- Raising the zero band from 1,300,000 to 2,500,000 kip while keeping the 5,000,000 edge removes 5 % of 1,200,000 = 60,000 kip a month for every salary of 5,000,000 or more (#guard on the printed cumulative columns: 10,685,000 vs 10,625,000 at 65m).
- provisions: Law 67/NA art. 39(1); amended law art. 38(1)
- Lean: LaTax.sched2019, LaTax.sched2025 (#guard)
- status: model result

### F3 Bands 'adjusted with the minimum wage' without a formula
- kind: statute-fault
- The note under art. 38(1) of the 2025 law says the monthly bands 'will be adjusted according to the minimum wage set by the government from time to time', and art. 34(1) exempts salary at the minimum wage; art. 72 reserves rate changes to an NA Standing Committee edict. Which instrument moves the bands, and by what rule, is not stated.
- provisions: amended law arts. 34(1), 38(1) note, 72
- Lean: -
- status: model result

### F4 Overtime exemption with a hard income limit
- kind: fact
- Overtime pay is exempt only for employees whose basic salary does not exceed 2,000,000 kip (Law 67/NA art. 35(3)) / 3,000,000 kip (2025 law art. 34(3)): one kip more of basic salary makes all overtime taxable. Not modelled (no overtime in the household contract).
- provisions: Law 67/NA art. 35(3); amended law art. 34(3)
- Lean: -
- status: model result

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Recorded statute-fault with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F2 | fact | model-proved | LaTax #guard (model build). |
| F3 | statute-fault | explained | Recorded statute-fault with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F4 | loophole | lead | Overtime exemption cliff not modelled (no overtime in the contract); statute cited by the builder. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/LA.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
