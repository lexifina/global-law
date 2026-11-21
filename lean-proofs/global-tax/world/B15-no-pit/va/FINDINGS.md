# Holy See (Vatican City State) (VA) findings, B15-no-pit (rescue pass 2, 2026-11-20T13:10Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The employee pension rate left the published law in 2004
- kind: gov-error
- The 1992 Regolamento printed the employee withholding (5 %). The 2004 Regolamento Generale art. 15(2) leaves the total and the employee's share to the Secretary of State 'tempo per tempo'; the only later decision printed in the AAS changes the employer's share (25 -> 26 %, 2009). An employee cannot find the rate withheld from pay in the published law.
- provisions: Regolamento 1992 art. 8; Regolamento Generale 2004 art. 15(2); Rescriptum 6 Apr 2009
- Lean: VaTax.out (unsupported)
- status: model result

### F2 No tax on income: an absence, not a rule
- kind: fact
- No Vatican text levies an income tax; the Lateran Treaty art. 17 exempts Holy See pay from Italian taxes. The model's zero rests on that absence.
- provisions: Lateran Treaty art. 17
- Lean: VaTax.out
- status: model result

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Rate outside the published law (builder). |
| F2 | fact | explained | Absence. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/VA.json`): no lead.
