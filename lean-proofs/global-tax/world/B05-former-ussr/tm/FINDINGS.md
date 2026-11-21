# Turkmenistan (TM) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 Dividends taxed more than wages: 15 % against 10 %
- kind: loophole-known
- art. 172(2) 15 % on dividends; wages 10 % with no employee contribution (pension contributions are the insurer's): an owner-manager is better off with salary (company profit tax 8 %/20 %, art. 172(1), also argues for salary, which is deductible).
- provisions: TC art. 172, 192
- Lean: TmTax.divRate
- status: lead

### F2 The basic deduction is defined by reference to a value outside the Code
- kind: model-fix
- art. 188(1)(a): one base value a month; the amount is fixed by separate act. Without it the model overstates tax by 10 % of 12 base values a year; input `baseValue` switches it on.
- provisions: TC art. 188
- Lean: TmTax.out
- status: flagged

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | model-proved | 15 % on dividends vs 10 % on wages. exe and #guard L1TM.F1; no current scan (no reference wage). Dividends cost more: not a loophole. Evidence: exe + Lean `L1TM.F1` (`world/loopholes/rest/lean/L1TM.lean`, 2 #guard): tot(a) = 15000; tot(b) = 10000. |
| F2 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TM.json`): no current scan: no reference wage; exe checks only.
