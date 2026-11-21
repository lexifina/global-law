# Malaysia (MY) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 s. 6A rebate cliff at RM35,000 of chargeable income
- kind: loophole-known
- The RM400 rebate (RM800 with a non-earning spouse) stops above RM35,000 of chargeable income: salary RM44,000 -> RM44,001 (chargeable 35,000 -> 35,001 after the 9,000 relief) raises tax by 400 ringgit. Fine-grid scan: one net-income fall per family.
- provisions: ITA s. 6A (LHDN Rebates page)
- Lean: MyTax.person (#guard)
- status: model result

### F2 LHDN's heading says 'less than RM35,000' while the table is read as 'not exceeding'
- kind: gov-error
- The Rebates page is headed 'Chargeable Income Less Than RM35,000'; at exactly RM35,000 the two readings differ by RM400 (RM800 for a one-earner couple). The model gives the rebate at RM35,000 (reading; the Act's s. 6A text was not reachable to settle it).
- provisions: ITA s. 6A
- Lean: MyTax.rebateLimit
- status: model result


### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: EPF Act 1991 Third Schedule Parts A, E (KWSP copy 2022); Employees Social Security Act 1969 Third Schedule para 2 (as at 1 Sep 2022) and Act A1724 (2024) s. 3; EIS Act 2017 Second Schedule and Act A1725 (2024) s. 3; LHDN YA 2025 reliefs 17, 20
- EPF 11 % (Third Schedule bands, rounded up; nil from 60), SOCSO first category (0.5 % of the band mid-wage, ceiling RM6,000; under 60) and EIS (0.2 %, ceiling RM6,000; 18-59); reliefs EPF up to 4,000 and SOCSO+EIS up to 350. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: EIS schedule items 41-54 (Act A1657 of 2022) not read (same rule applied); EIS counted in the SOCSO relief (reading).
- status: fixed

### W5S-1 two calculators (wronglaw grids): PCB tables not Schedule 1 (W5 review pass 3, 2026-11-20)
- kind: software-error
- `my_open_mypayslip_generator_farisareziq_grid` (brackets neither YA 2025's nor earlier, EPF relief cap 6,000, only the 9,000 personal relief): tax above at low incomes (no s. 6A rebate), below where its EPF relief exceeds the statute's, above with children (no child relief); 136 / 1,009 exact. `my_open_nexus_payroll_mys_statutory_azaharizaman_grid` (self-declared simplified PCB table): -16..-356 at low incomes, +2,000..+5,000 at high; 171 / 2,152. The third note (`my_open_mcp_calculators_havahr_grid`: bands restarting from their own lower bound) is **not** confirmed: its misses are -10..-88 by band (monthly PCB x 12, a declared period deviation) and +440..+1,000 for earners aged 60+ (an EPF relief where EPF Act Third Schedule Part E gives the employee rate 0; pattern A ground).
- provisions: ITA 1967 Schedule 1 Part I; s. 46 (1); s. 6A
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | RM400 (RM800 with a non-earning spouse) for one ringgit; after the W5 EPF/SOCSO reliefs the edge is at a salary of RM48,340 (RM44,000 only with w5Contrib false). exe and #guard L1MY.F1: corrected location after W5. Evidence: exe + Lean `L1MY.F1` (`world/loopholes/rest/lean/L1MY.lean`, 2 #guard): tot(b)-tot(a) = 400; it(f)-it(e) = 400; statute re-read: `law/hasil_rebate.html`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | gov-error | explained | LHDN heading 'less than RM35,000' vs the table; s. 6A text not reached (builder). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MY.json`): METR 163-261 % and notches 399 / 599 = F1 (single at RM48,340; with children and a non-earning spouse at 52,350 / 56,350; couples); notches of 140 = the EPF Third Schedule wage bands (statutory step table, RM2.2-11 a month).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.04 AW (contribution rate 12.6 -> 9.6 %, combined marginal 10 -> 11 %); ceiling at 0.28 AW (contribution rate 13.6 -> 9.6 %, combined marginal 12 -> 11 %); ceiling at 0.52 AW (contribution rate 13.6 -> 9.6 %, combined marginal 12 -> 11 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
