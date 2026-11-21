# AG findings (Antigua and Barbuda (private-sector employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 The PIT Act was repealed by another act; the official index does not say so
- kind: gov-error (index)
- provisions: UBT Act 2016 s. 47
- The repeal of the Personal Income Tax Act 2005 is in s. 47 of the Unincorporated Business Tax Act 2016, not in a PIT amendment; laws.gov.ag still lists the PIT Act and its amendments (2005-2016) without a repeal note, and the 2016 PIT amendment alone suggests only that 2016 was a half year.
- status: recorded (build phase)

### F2 Social security reached 16 % in 2025
- kind: known
- provisions: S.I. 60/2016 reg. 4(1)(b), Sch. 1
- S.I. 60/2016 raised the private-sector rate from 12 % (2017) to 16 % by 1 January 2025: employee 7 %, employer 9 %, up to $6,500 a month.
- status: recorded (build phase)

### F3 Education levy not found
- kind: model gap
- provisions: -
- No act or statutory instrument on an education levy on wages was found in the laws.gov.ag indexes (acts by letter, annual lists 2016-2025, statutory instruments 2005-2025, subsidiary volumes); the model omits it and flags every wage earner.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 10.8 % | 0.005 | 0 |  | 0 |`
- timing, single: `| single|none | 2,730 (7.00 % AW) | 78,000 | 117,000 / 39,000 | 32.6 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Index (builder). |
| F2 | fact | explained | Known. |
| F3 | record | explained | Model gap. |
| Generic | record | explained | Record (scanner leads): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AG.json`): timing 2,730 (7 % of the scale) = the social-security ceiling (6,500 a month); no income tax.
