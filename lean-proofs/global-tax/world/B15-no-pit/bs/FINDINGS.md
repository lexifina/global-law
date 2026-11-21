# BS findings (The Bahamas (employed person), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 The ceiling is set outside the regulations
- kind: statute-fault (publication)
- provisions: NI (Contributions) Regs reg. 52
- Reg. 52 prints the ceiling only to July 2012 ($2,600 a month) and then delegates biennial RPI + 2 % increases without requiring publication in the regulations; the 2025 ceiling is not in the law. The model caps at the last printed ceiling and flags higher wages.
- status: recorded (build phase)

### F2 The schedule understates the employee rate
- kind: statute-fault (drafting)
- provisions: S.I. 37/2024 reg. 4, 9
- S.I. 37/2024 replaced the Fifth Schedule with 3.9 % for the employee but added in reg. 23(1A) a 1.5-point increase shared equally from 1 July 2024: the effective employee rate is 4.65 %, which the schedule does not show. Lean `rate_2025`.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 5.1 % | 0.015 | 0 |  | 0 |`
- timing, single: `| single|none | 1,450 (4.65 % AW) | 31,200 | 62,400 / 0 | 24.0 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Ceiling outside regulations. |
| F2 | statute-fault | explained | Lean rate_2025 (build). |
| Generic | record | explained | Record (scanner leads): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BS.json`): timing 1,450 = the NIB ceiling.
