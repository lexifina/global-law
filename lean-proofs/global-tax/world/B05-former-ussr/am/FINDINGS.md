# Armenia (AM) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 The stamp duty is a step function: one dram more than 1 000 000 a month costs 78 000 dram a year
- kind: statute-fault
- HO-245-N art. 12(1)(1) charges 1 500 / 3 000 / 5 500 / 8 500 / 15 000 a month by band of the monthly base. Each band edge is a notch: +1 dram above 100 000 costs 1 500 a month (18 000 a year), above 200 000 2 500 a month, above 500 000 3 000, above 1 000 000 6 500 a month = 78 000 a year (scan: METR 290 % at 12 m a year, largest notch 77 999). The entrepreneur table (12(1)(2)) has the same shape on annual bases. A graduated charge would remove the notches.
- provisions: Law HO-245-N art. 12(1)
- Lean: AmTax.stampMonth, stampSelf
- status: modelled; scan reproduces

### F2 The social payment depends on the year of birth: an employee born in 1973 pays nothing, one born in 1974 pays 5-10 %
- kind: loophole-known
- HO-244-N art. 5(1)(1)-(2): compulsory for those born on or after 1 January 1974; earlier cohorts only by application. Two employees on 500 000 a month differ by 300 000 dram a year.
- provisions: HO-244-N art. 5, 6
- Lean: AmTax.participant
- status: modelled

### F3 Marginal rate 30 % between 500 000 and 1 125 000 a month, then back to 20 % above the ceiling
- kind: model-fix
- Social payment 10 % on top of 20 % tax in that band; above 15 x the minimum wage (1 125 000) no social payment (art. 6(6)): the system is regressive at the top.
- provisions: HO-244-N art. 6(2)(1), 6(6); HO-66-N art. 1
- Lean: AmTax.socWage (#guard)
- status: modelled

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 78,000 AMD a year for one dram of monthly pay above 1,000,000 (6,500 a month); smaller steps at 100,000, 200,000, 500,000. exe and #guard L1AM.F1 (the step lands at 12,000,006 a year because the exe rounds monthly pay). Evidence: exe + Lean `L1AM.F1` (`world/loopholes/rest/lean/L1AM.lean`, 1 #guard): tot(b)-tot(a) = 78000; statute re-read: `law/stamp_11_12_20250701.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | loophole | confirmed | 300,000 AMD a year on 6 M of wages by year of birth (1973 vs 1974 cohorts). exe and #guard L1AM.F2 (age 53 vs 50). Evidence: exe + Lean `L1AM.F2` (`world/loopholes/rest/lean/L1AM.lean`, 1 #guard): soc(b)-soc(a) = 300000; statute re-read: `law/funded_5_6_20250701.txt`. Known/new: **unclear**: Crossref only; the cohort rule was the subject of public protests against the funded pension (2014), not searched. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AM.json`): notches 77,999 / 35,999 / 29,999 and METR 125-290 % = F1 (stamp-duty steps; couple multiples).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- mix.py (wage vs fee split): explained: the funded-pension social payment has separate caps for wages and self-employment; it is paid into the person's own account.
<!-- R2-SCANNERS:END -->
