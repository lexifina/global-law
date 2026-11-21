# Tajikistan (TJ) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 Two rates by job: 12 % at the main job with a deduction, 15 % without it elsewhere
- kind: loophole-known
- art. 183(1) 12 % above the personal deduction at the main place of work; 183(3) 15 % for other natural persons' income without art. 191 deductions. A second job or a civil contract costs 3 points more.
- provisions: TC art. 183, 191
- Lean: TjTax.out
- status: modelled (secondary jobs not in the contract)

### F2 Small personal deduction: 150 TJS a month
- kind: model-fix
- 2 indicators x 75 TJS (budget law 2025 art. 23): METR 13.76 % (2 % social tax + 12 % of the remaining 98 %); scan bands above the top rate are whole-somoni rounding only.
- provisions: TC art. 191(1),(6); art. 332(2)
- Lean: TjTax.personalYear
- status: modelled

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | explained | Rate difference by job (12 % vs 15 %); secondary jobs are not in the contract. Statute cited by the builder. |
| F2 | fact | explained | Fresh scan: bands 15.6-16.7 % above 13.9 % are whole-somoni rounding. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TJ.json`): bands 14.4-16.7 % above 13.9 % = whole-somoni rounding (F2).
