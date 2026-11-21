# Afghanistan (AF) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 Overlapping band limits: Afs 100,000 falls in two rows
- kind: statute-fault
- Art. 4 (3): 'From Afs. 12,501 to Afs. 100,000 10% + Afs. 150' and 'From Afs. 100,000 and above 20% + Afs.8,900': exactly 100,000 is in both rows (8,900 either way, so no tax difference at that point). The rows also start at 5,001 and 12,501, leaving fractions between 5,000 and 5,001 unassigned.
- provisions: ITL 2009 Art. 4 (3)
- Lean: AfTax.monthly
- status: model result (build phase)

### F2 A monthly schedule: uneven pay costs more if withholding is final
- kind: reading
- The schedule is printed per month. If each month's withholding (Art. 17) were final, 1,200,000 paid evenly costs 12 x 8,900 = 106,800, paid in one month 228,900. The model applies the schedule to the annual income / 12 (an annual return); which reading the administration uses was not verified.
- provisions: ITL 2009 Arts. 4 (3), 17
- Lean: AfTax.annual
- status: model result (build phase)

### F3 Whose law: the Islamic Republic's statute, status in 2025 unverified
- kind: fact
- No text issued by the de facto authorities after August 2021 was reachable; the model is the last accessible official consolidation (2016). Grade B with this caveat.
- provisions: -
- Lean: -
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Government pensions exempt | Art. 17 (2) | not modelled |
| Income splitting (individual taxation) | Art. 4 (3) | recreated (scanner unit family) |
| Business income taxed on the same schedule | Art. 4 (3) | modelled |

Catalogued 3, recreated 1, not modelled 1. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: ARD income tax manual (Dari/Pashto, archived), any de facto MoF decree or tax guide since 2021, UN/World Bank reports on Afghan revenue: not checked. Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Overlap with no tax difference. |
| F2 | reading | lead | Monthly vs annual reading unverified. |
| F3 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AF.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
