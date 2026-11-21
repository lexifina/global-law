# Georgia (GE) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 A flat 20 % on salary net of the 2 % pension contribution: effective 19.6 % + 2 %
- kind: model-fix
- The funded-pension contribution (Law 3303 art. 3(6)(b)) is exempt (TC art. 82(1)(b3)), so the tax is 20 % of 98 % of the salary; the employee's total is 21.6 % at every wage (scan: METR 21.6 %, 22.5 % only where whole-lari rounding bunches). No notch, no taper, no marriage effect.
- provisions: TC art. 81(1), 82(1)(b3); Law 3303 art. 3(6)
- Lean: GeTax.out, GeTax.sched_mono/convex/no_jump
- status: modelled; scan clean

### F2 Owner-manager: dividends 5 % final against 20 % + 2 % on salary
- kind: loophole-known
- Dividends bear 5 % at source, final (art. 130(1),(3)); salary 21.6 %. The company-side tax on distributed profit (Tax Code profit tax) was not read, so the full comparison is a lead for the owner-manager scan.
- provisions: TC art. 130
- Lean: GeTax.divRate
- status: lead (company side not modelled)

### F3 Pension participation depends on sex and on age in 2019, which the canonical household cannot express
- kind: model-fix
- Law 3303 art. 3(2) excludes employees who were 60 (men) or 55 (women) before 2019; ages 62-66 in 2025 are ambiguous without sex: treated as participants and flagged.
- provisions: Law 3303 art. 3(2)
- Lean: GeTax.participant
- status: flagged in output


### W5S4-1 tax-calc tax_core (dadadance); fastapi-run taxation engine (rgelikoshvili): PIT on the whole gross, the 2 % funded-pension contribution not exempted (W5 review pass 4, 2026-11-20)
- kind: software-error
- `ge_open_tax_calc_dadadance_grid`, `ge_open_fastapi_run_rgelikoshvili_grid`: income tax at 20 % of the whole salary; Tax Code art. 82(1)(ბ³) exempts the funded-pension contribution paid to the participant's individual pension account (law/art80_82_20250701.txt), so the tax is 20 % of 98 % of the salary (F1). Dev: model / tool = 0.980 in 1,063 of 1,068 and 1,028 of 1,033 misses; employeeSocial exact in every case.
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F2 | loophole | model-proved | 5 % final on dividends vs 21.6 % (20 % of 98 % + 2 %) on salary. exe and #guard L1GE.F2; statute pattern not located (Georgian text). Evidence: exe + Lean `L1GE.F2` (`world/loopholes/rest/lean/L1GE.lean`, 2 #guard): tot(a) = 5000; tot(b) = 21600. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/GE.json`): bands 22.5 % above 21.7 % = whole-lari rounding (F1).
