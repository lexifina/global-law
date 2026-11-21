# Russia (RU) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 Child deduction cliff at 450,000 of cumulative income
- kind: loophole-known
- The standard child deduction stops from the month cumulative income exceeds 450,000 (art. 218 (1) 4 as amended): a parent with 2 children loses 4,200 of deduction (546 of tax) per month; the cut-off depends on the month the threshold is crossed, so paying the same annual salary earlier in the year loses more (timing).
- provisions: Tax Code art. 218 (1) 4 (330-FZ, 176-FZ)
- Lean: RuTax.childDeduction
- status: modelled; timing effect not captured by the even-month contract

### F2 Separate scale for investment income
- kind: loophole-known
- Dividends and securities gains form their own base (art. 210 (6)) with 13 % up to 2.4 m and 15 % above, so a person with 6 m of wages and 2 m of dividends pays 13 % on the dividends rather than the 18 % marginal wage rate: income type matters.
- provisions: art. 224 (1.1)
- Lean: RuTax.schedInv
- status: modelled

### F3 Generic scan: no net-income fall; max METR 18 % single, 30 % for parents near 450k
- kind: model-fix
- b02scan 0-2.5 × 5 m.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 548 RUB of tax for 12 rubles more at 450,000 a year with two children (the twelfth month's 4,200 deduction). exe and #guard L1RU.F1; statute text in the law folder not located by pattern (builder's citation). The month-of-crossing timing effect is not expressible with even months. Evidence: exe + Lean `L1RU.F1` (`world/loopholes/rest/lean/L1RU.lean`, 2 #guard): it(b)-it(a) = 548; it(b)-it(a) = 548. Known/new: **unclear**: Crossref only; the 450,000 limit is likely in Russian payroll guidance, not searched. |
| F2 | loophole | model-proved | 260,000 RUB on 2 M of dividends (13 %) beside an 18 % marginal wage rate at 6 M. exe and #guard L1RU.F2. Evidence: exe + Lean `L1RU.F2` (`world/loopholes/rest/lean/L1RU.lean`, 1 #guard): it(b)-it(a) = 260000. Known/new: **known**: pattern: flat or final tax on capital income beside a progressive labour tax (Dual Income Taxes: A Nordic Tax System, 10.4337/9781849804998.00012); the rates are published. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/RU.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F2).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 25.0 % (НК РФ ст. 284 п. 1 as amended by 176-ФЗ (2024): 'Налоговая ставка устанавливается в размере 25 процентов' (law/fz176_2024.txt:915)); at a profit of 3 AW the best split costs 16.7 % of the profit, all salary 16.7 %, all dividends 35.9 % (employer contributions: not included); dividends beat salary once employer contributions exceed 31 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
