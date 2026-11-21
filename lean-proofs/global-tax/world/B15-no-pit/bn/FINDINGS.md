# BN findings (Brunei Darussalam (citizen or PR employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 An income tax on individuals with an empty rate table
- kind: statute-fault (drafting curiosity)
- provisions: ITA Cap. 35 s. 8, 34, Sch. 2
- Cap. 35 s. 8(1)(b) counts employment income and s. 34 levies tax on every person other than a company 'at the rates specified in Schedule 2', but Schedule 2 lists no rate: the personal income tax exists in form and is zero in effect.
- status: recorded (build phase)

### F2 Employee 8.5 % without a ceiling, employer rate falling with salary
- kind: known
- provisions: NRS Act s. 10, Sch. 2
- NRS Act s. 10(2): 8.5 % of all wages; Schedule 2: employer 10.5 % (minimum $57.50) up to $1,500, 9.5 % to $2,800, 8.5 % above.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 8.9 % | 0.015 | 0 |  | 0 |`
- timing, single: `| single|none | 1 (0.00 % AW) | 672 | 840 / 504 | 0.0 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Empty rate table (builder). |
| F2 | fact | explained | Known. |
| Generic | record | explained | Record (scanner leads): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BN.json`): no lead.
