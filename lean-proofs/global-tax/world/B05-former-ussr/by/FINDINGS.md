# Belarus (BY) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 The standard deduction stops at 1 164 rubles a month: 1 ruble more costs 25 rubles of tax
- kind: loophole-known
- art. 209(1)(1.1): 192 rubles a month 'при получении дохода ... в сумме, не превышающей 1164 белорусских рублей в месяц'. Above the limit the whole deduction goes: 13 % x 192 = 24.96 a month (299.5 a year; scan METR 227 %, notch 299).
- provisions: TC SP art. 209(1)(1.1)
- Lean: ByTax.deductions (#guard)
- status: modelled; scan reproduces

### F2 A second rate of 25 % on aggregate wages and dividends above 220 000 rubles (2025)
- kind: model-fix
- art. 214(8) (Law 47-З): the excess over 220 000 of wages + dividends + service contracts is taxed at 25 %, computed by the tax authority after the year (art. 219). From 2026 (Law 127-З) the thresholds become 350 000 / 600 000 with 30 % on top (not modelled: 2026).
- provisions: TC SP art. 214(1), (8)
- Lean: ByTax.sched
- status: modelled

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 301 BYN a year (24.96 a month) for 1 BYN a month above 1,164. exe and #guard L1BY.F1. Evidence: exe + Lean `L1BY.F1` (`world/loopholes/rest/lean/L1BY.lean`, 2 #guard): it(b)-it(a) = 301; it(b)-it(a) = 301; statute re-read: `law/pravo_tc_sp_wb20250614.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BY.json`): METR 227 % and notches 299 = F1 (couple multiples); timing 302-603 = F1.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 20.0 % (Tax Code (special part) art. 184 p. 1: 'Ставка налога на прибыль устанавливается в размере двадцать (20) процентов' (law/pravo_hk0900071_20261120.html:3839)); at a profit of 3 AW the best split costs 13.0 % of the profit, all salary 13.0 %, all dividends 30.4 % (employer contributions: not included); dividends beat salary once employer contributions exceed 26 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
