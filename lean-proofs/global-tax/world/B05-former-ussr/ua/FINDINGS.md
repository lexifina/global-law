# Ukraine (UA) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 The tax social benefit is all-or-nothing: 1 hryvnia over 4 240 a month costs 272.5 hryvnias of tax
- kind: loophole-known
- art. 169.4.1: the benefit applies only to a month's wage not above 1.4 x the subsistence minimum rounded to 10 (4 240 in 2025). Above it the whole 1 514 is lost: 18 % x 1 514 = 272.52 a month (3 270 a year; scan METR 364 %). For a parent of two or more children the limit and the benefit are multiplied by the number of children: losing 2 x 1 514 costs 545 a month (scan METR 704 %, notch 6 540 a year). Bunching pay into alternate months gains up to 3.4 % of the scale wage (timing scan).
- provisions: TC art. 169.1.1, 169.1.2, 169.4.1; Budget law 2025 art. 7
- Lean: UaTax.psp (#guard 5 370 / 9 161)
- status: modelled; scan reproduces

### F2 Art. 167.4 still taxes pensions above an amount 'defined in subparagraph 164.2.19', which was deleted in 2020
- kind: statute-fault
- 167.4: '18 відсотків ... щодо перевищення суми пенсії ..., визначеної у підпункті 164.2.19 пункту 164.2 статті 164'; the edition of 15.06.2025 prints at 164.2.19 '{Підпункт 164.2.19 ... виключено на підставі Закону № 466-IX від 16.01.2020}'. The rate provision refers to a threshold that no longer exists in the Code. (How pensions are treated in practice rests on other provisions not read; pensions are not modelled.)
- provisions: TC art. 167.4, 164.2.19 (deleted by Law 466-IX)
- Lean: -
- status: found by reading the dated text; not modelled

### F3 The military levy (5 %) applies to the full wage, including the part relieved by the benefit
- kind: model-fix
- XX/10/16-1 item 1.2: object = art. 163 income; the benefit reduces only the PIT base (art. 169). Combined statutory rate 23 % (scan top 23.02 %).
- provisions: XX/10/16-1 items 1.2-1.3
- Lean: UaTax.out
- status: modelled


## Round W5 review (W5 fix agent, 2026-11-20)

### W5-1 W5 grids: the art. 169 tax social benefit (input `uaPsp` added; one software limitation)
- kind: model-input / software-error
- Tax Code art. 169.2.1: the benefit is granted on the employee's application. The model claims it by default; new input
  `uaPsp` (default true) models an employee who has not applied. The calcular adapter runs "no PSP": with `uaPsp = false`
  its dev grid is 291 / 291 exact (test-side request filed). The odoo payroll rules apply the general benefit but not the
  art. 169.1.2 benefit for a parent of two or more children under 18 (software limitation; `ua_open_odoo_live_payroll_rules_grid`).

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 3,273 UAH a year for 1 UAH a month above 4,240; 6,543 for a parent of two above 8,480. exe and #guard L1UA.F1. Evidence: exe + Lean `L1UA.F1` (`world/loopholes/rest/lean/L1UA.lean`, 4 #guard): it(b)-it(a) = 3273; it(b)-it(a) = 3273; it(d)-it(c) = 6543; it(d)-it(c) = 6543; statute re-read: `law/ptk_wb20250620.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | statute-fault | explained | Dead cross-reference (164.2.19 deleted); not modelled. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5-1 | record | explained | Record (model-input / software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/UA.json`): METR 364 % / 704 % and notches 3,269 / 6,540 = F1; timing 3,271-9,813 = F1.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 18.0 % (Податковий кодекс п. 136.1: 'Базова (основна) ставка податку становить 18 відсотків' (law/ptk_wb20250620.txt:7120)); at a profit of 3 AW the best split costs 26.1 % of the profit, all salary 36.9 %, all dividends 26.2 % (employer contributions: statute rate 22.00 %); dividends beat salary once employer contributions exceed 5 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
