# Uzbekistan (UZ) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 Dividends 5 % against 12 % on salary
- kind: loophole-known
- art. 381 part 2: dividends and interest 5 %; salary 12 % (plus the employer's social tax, not modelled): owner-managers prefer dividends (company profit tax not read).
- provisions: TC art. 381
- Lean: UzTax.divIntRate
- status: lead

### F2 No allowance at all: the flat 12 % starts at the first sum
- kind: model-fix
- No personal or child deduction in Section XI; METR 12 % everywhere.
- provisions: TC art. 381
- Lean: UzTax.sched
- status: modelled

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 5 % on dividends vs 12 % on wages. exe and #guard L1UZ.F1; no current scan (no reference wage). Evidence: exe + Lean `L1UZ.F1` (`world/loopholes/rest/lean/L1UZ.lean`, 2 #guard): tot(a) = 5000; it(b) = 12000. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F2 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/UZ.json`): no current scan: no reference wage; exe checks only.
