# MC findings (Monaco (private-sector employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 Rates from the funds' tables, not from the law
- kind: access
- provisions: -
- The C.A.R. and CMRC rates and ceilings are fixed by ministerial texts that were not reached; the model uses the Caisses Sociales tables as archived during 2025 (tier B).
- status: recorded (build phase)

### F2 No text read states the absence of a personal income tax
- kind: model-fix (evidence)
- provisions: -
- The model returns no income tax for residents other than French nationals; this rests on the absence of any act found, not on a text that says so.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 19.9 % | 1.38 | 0 |  | 0 |`
- timing, single: `| single|none | 1,838 (5.08 % AW) | 73,240 | 109,408 / 37,072 | 26.2 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

### W5S4-1 Xenna (Corto735), Monaco: no CMRC and no ceilings before 1 October 2025 (reading) (W5 review pass 4, 2026-11-20)
- kind: software-error
- `mc_open_xenna_corto735_grid`: the tool's database starts the CMRC tranche A/B employee contribution and the C.A.R. / unemployment ceilings on 2025-10-01 (migration 0137), so January-September carry no CMRC and no ceiling; the Caisses Sociales tables (official secondary, scale.json) apply them all year (C.A.R. ceiling 6,028 to September). Dev: model above in every case (ratio ~1.29 below the ceiling = nine months of CMRC missing).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | record | explained | Access. |
| F2 | record | explained | Evidence note. |
| Generic | record | explained | Record (scanner leads): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MC.json`): timing 1,838 = the C.A.R. / CMRC ceilings.
