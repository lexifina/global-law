# MK findings (North Macedonia (данок на личен доход; придонеси од задолжително социјално осигурување), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 960 000 MKD = 10 × the tax reduction printed in the act); leads: no METR band above 100 % and no notch above 0.1 % of the scale

### F1 The 2025 tax reduction is a published amount, not reached
- kind: model limitation
- status: open

Член 10 (2) prints 96 000 MKD (2019) and (3)-(4) index it yearly by 50 % of average-wage growth, published by the Minister of Finance; the 2025 amount was not found (finance.gov.mk and ujp.gov.mk pages; the UJP PDF of the act is a scan without text). The model uses 96 000 and says so in `unsupported`.

### F2 Deposit-interest tax postponed to EU accession
- kind: observation (statute)
- status: noted

Член 116 as replaced by 274/2022 член 23: the taxation of term-deposit interest applies 'од денот на пристапувањето ... во Европската Унија'; until then it is untaxed, as is deposit interest up to 15 000 MKD (член 12 (1) 37)).

### F3 Combined marginal rate 35,2 % on pay
- kind: observation (structure)
- status: proved

28 % contributions on gross pay (18,8 + 7,5 + 0,5 + 1,2) and 10 % tax on the remainder: `MkTax.combined_marginal`.

### F4 Contribution bases need the January average wage
- kind: model limitation
- status: open

Minimum 50 % and maximum 16 × the average wage published in January 2025 (член 15-16): not reached, not applied.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F2 | fact | explained | Recorded observation (statute) with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F3 | fact | proved | Model theorem. Evidence: model Lean: MkTax.combined_marginal. |
| F4 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MK.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
