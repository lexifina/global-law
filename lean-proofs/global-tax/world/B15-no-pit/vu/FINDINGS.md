# VU findings (Vanuatu (employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 The VT 3,000 monthly floor is a notch
- kind: loophole-new (notch)
- provisions: VNPF Act s. 25(2)
- S. 25(2): no contribution in a month in which remuneration from one employer is under VT 3,000; at VT 3,000 the 6 % applies to the whole amount (VT 180 a month). Lean `vnpf_notch` (kernel floor_notch).
- status: recorded (build phase)

### F2 No income tax
- kind: model-fix (evidence)
- provisions: -
- No act levying a tax on individuals' income was found; the Global law corpus for Vanuatu holds only the Constitution.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 120.0 % | 0.095 | 1 | 2,159 at 35,999 (0.1 AW) | 0 |`
- timing, single: `| single|none | 2,052 (0.57 % AW) | 36,000 | 37,800 / 34,200 | 2.6 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 2,160 VUV a year (180 a month) at VT 3,000 a month. exe and #guard L1VU.F1. Evidence: exe + Lean `L1VU.F1` (`world/loopholes/rest/lean/L1VU.lean`, 1 #guard): tot(b)-tot(a) = 2160; statute re-read: `law/vnpf_act_consol_2026.txt`; model Lean: VuTax.vnpf_notch. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | record | explained | Evidence note. |
| Generic | record | explained | Record (scanner leads): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/VU.json`): METR 120 % and notches 2,159 = F1.
