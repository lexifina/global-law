# Kyrgyzstan (KG) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 Wages below the district average are taxed as if they were the average (art. 187(2))
- kind: loophole-known
- If the monthly salary does not exceed the district average monthly wage published by the National Statistical Committee, the tax base is that average (except state-funded employers, part-timers, junior service staff and disabled workers, art. 187(4)): low-paid private employees pay tax on income they did not receive. The 2025 averages were not reached; input `avgMonthlyWage` switches the rule on.
- provisions: TC art. 187(2)-(4)
- Lean: KgTax.out (avg?)
- status: modelled as an option; amount not reached

### F2 Dividends, deposit interest and pensions are exempt
- kind: loophole-known
- art. 191: dividends from resident companies to resident citizens, bank interest and statutory pensions are not taxed: owner-managers prefer dividends to salary (10 % + 10 %).
- provisions: TC art. 191
- Lean: KgTax.out
- status: modelled


### W5R4-1 The art. 194 deductions stay off by default: the RP value is still not reached (W5 review pass 4, 2026-11-20)
- kind: model gap (open)
- `kg_open_pn_dashboard_fourpi4_grid`: model incomeTax above the tool by 10 % x (650 + 100 per dependant) x 12 in every case, i.e. the 6.5 RP + 1 RP per dependant deductions at RP = 100 som, which the model applies only with the input `rp`. The instrument fixing the RP was not found in the Global law Kyrgyz corpus (code search on "размер расчетного показателя") or by web search; never taken from the tool.
- status: open (text still to find)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 24,000 KGS a year on 120,000 of wages with a district average of 30,000 a month. exe and #guard L1KG.F1 with the input avgMonthlyWage (the 2025 averages not reached). It raises tax: a trap, not a way to pay less. Evidence: exe + Lean `L1KG.F1` (`world/loopholes/rest/lean/L1KG.lean`, 1 #guard): it(b)-it(a) = 24000. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | loophole | model-proved | 0 tax on dividends vs 10 % + 10 % on salary. exe and #guard L1KG.F2. No current scan: no reference wage (scale.json). Evidence: exe + Lean `L1KG.F2` (`world/loopholes/rest/lean/L1KG.lean`, 1 #guard): tot(a) = 0. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| W5R4-1 | record | explained | Record (model gap (open)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/KG.json`): no current scan: no reference wage (scale.json); exe checks only.
