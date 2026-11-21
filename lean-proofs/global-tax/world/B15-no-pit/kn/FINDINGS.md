# KN findings (Saint Kitts and Nevis (employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 The HSDL charges the whole wage once it passes the threshold
- kind: loophole-new (notch)
- provisions: HSDL Act s. 3(2); Act 14 of 2025
- S. 3(2)(a)-(b): 0 % up to the threshold, then 3.5 % 'in the case of an employee whose wages range between' the threshold and $78,000, i.e. on all wages. One dollar above $27,040 costs $946 a year (one-year reading). Lean `hsdl_notch`, `hsdl_notch_metr`. Marginal rates above: 10 % on $78,000-96,000 and 12 % above (marginal portions).
- status: recorded (build phase)

### F2 The threshold moved twice in 18 months
- kind: known
- provisions: Acts 1/2024, 14/2025
- $18,720 (2017) -> $23,400 (Act 1 of 2024) -> $27,040 (Act 14 of 2025, published 11 July 2025). The model weights 2025 six months each.
- status: recorded (build phase)

### F3 No tax on non-company income since 1980
- kind: known
- provisions: ITA Cap. 20.22 s. 3(3)
- Income Tax Act s. 3(3) (Act 14 of 1980): the charge does not apply to income accruing on or after 1 May 1980 to any person other than a company.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 250.3 % | 0.69 | 2 | 472 at 27,040 (0.69333 AW) | 0 |`
- timing, single: `| single|none | 819 (2.10 % AW) | 28,665 | 33,930 / 23,400 | 14.8 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

### W5S4-1 caribbean-payroll (oecstrading), KN config: a PAYE that KN does not levy; NIC ceiling and age (W5 review pass 4, 2026-11-20)
- kind: software-error
- `kn_open_caribbean_payroll_oecstrading_grid` / `_ss_grid`: Income Tax Act Cap. 20.22 s. 3(3): no tax on income of persons other than companies accruing from 1 May 1980; the tool charges PAYE (allowance 40,000, 15 / 20 / 30 %). NIC: the tool caps at 6,000 a month and charges at every age; SS Regulations Schedule 2 ceiling $6,500 a month and Schedule 1 Part I 'from 62: Nil' (2017 revised edition, no later instrument found: reading). Dev (`_ss`, NIC against detail.socialSecurity): +300 / +600 a year above the ceiling, -3,600 at 62+.
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 946 XCD a year at the 27,040 threshold on a full-year reading; 473 at 27,040 and 409 at 23,400 with the model's half-year weighting. exe and #guard L1KN.F1. Evidence: exe + Lean `L1KN.F1` (`world/loopholes/rest/lean/L1KN.lean`, 2 #guard): tot(b)-tot(a) = 473; tot(d)-tot(c) = 409; statute re-read: `law/hsdl_ch20_21_2017.txt`; model Lean: KnTax.hsdl_notch, hsdl_notch_metr. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | fact | explained | Known. |
| F3 | fact | explained | Known. |
| Generic | record | explained | Record (scanner leads): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/KN.json`): METR 216-250 % and notches 408 / 472 = F1 (the half-year weighting gives two edges, 23,400 and 27,040; couple multiples).
