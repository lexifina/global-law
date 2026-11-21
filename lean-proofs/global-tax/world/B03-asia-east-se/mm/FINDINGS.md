# Myanmar (MM) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 All-or-nothing salary exemption: one kyat over 4,800,000 costs 92,000 kyat
- kind: loophole-new
- Union Tax Law 2025 s. 19 (a) exempts salary up to 4,800,000 kyat a year; above it the whole salary less reliefs is taxed (s. 19 (c)). A single employee going from 4,800,000 to 4,800,001 pays 92,000 kyat more (taxable 3,840,001 after the 20 % basic relief; 5 % of the part above 2,000,000). Fine-grid scan: one net-income fall, METR peak above 15 at the 1-kyat step.
- provisions: Union Tax Law 2025 s. 19 (a), (c); Income Tax Law s. 6
- Lean: MmTax.salaryTax (#guard); not found in 0 sources searched
- status: model result


## Round W5 review (W5 fix agent, 2026-11-20)

### W5-1 myanmar-pit-calculator taxes salaries the Union Tax Law 2025 exempts (software error)
- kind: software-error
- Union Tax Law 2025 s. 19 (က): salary income up to 4,800,000 kyat a year is exempt. The tool applies the 20 % relief and
  the bands to such salaries (e.g. 4,142,840 single: tax 65,713.6), the model 0. Grid
  `mm_open_myanmar_pit_calculator_grid` (W5 review): all 78 misses are of this kind.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 92,000 MMK for one kyat above 4,800,000 of salary. exe and #guard L1MM.F1. Evidence: exe + Lean `L1MM.F1` (`world/loopholes/rest/lean/L1MM.lean`, 1 #guard): it(b)-it(a) = 92000; statute re-read: `law/ird_ind.html`. Known/new: **new**: The 4.8 M exemption is published (PwC Myanmar; DFDL; VDB Loi); no hit describes that the whole salary becomes taxable above it; web search 13 + Crossref. |
| W5-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MM.json`): METR 387 % and notches 91,999 / 41,999 = F1 (single and couples).
