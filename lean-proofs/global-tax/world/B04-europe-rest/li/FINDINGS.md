# LI findings (Liechtenstein (Landessteuer on the Erwerb, Gemeindezuschlag, AHV/IV/ALV), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 79 300 CHF of pay (start of the 5 % row of Art. 19 Bst. a after expenses and contributions)); leads: no METR band above 100 % and no notch above 0.1 % of the scale

### F1 The printed tariff is not exactly continuous; at six thresholds tax falls
- kind: statute-fault (minor) / observation
- status: proved

Art. 19 prints 'rate · x − subtract' rows with subtractions rounded to the franc: at the thresholds the literal tax moves by −53 to +83 Rappen; one franc more of Erwerb lowers the tax at 6 of 24 thresholds (largest −0,53 CHF, tariff b at 206 116 CHF). Lean `LiTax.jumps_exact`, `jumps_below_one_franc` (like Colombia's rounded column).

### F2 The joint tariff is full splitting
- kind: observation (proved on probes)
- status: proved

Tariff c at 2x equals 2 × tariff a at x within 1 CHF on the probes (`joint_is_splitting`): marriage never costs and a one-earner couple gains the splitting advantage.

### F3 Capital income is taxed through wealth, not as income
- kind: observation (structure)
- status: noted

Interest and rent are not Erwerb when the wealth bears the Vermögenssteuer (Art. 15 Abs. 1 Bst. a); dividends (Abs. 2 Bst. n) and private capital gains (Bst. m, o) are free. The Sollertrag on wealth (rate set by the Finanzgesetz) needs wealth, which the household line lacks: not modelled.

### F4 Gemeindezuschlag of Vaduz not reached
- kind: model limitation
- status: open

Art. 75 Abs. 3: set yearly by each Gemeinderat between 150 % and 250 % of the Landessteuer. The 2025 Vaduz rate was not found in an official text; the model uses the statutory minimum 150 % and says so for every household (`unsupported`).

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | proved | Model theorems; at most 0.53 CHF. Evidence: model Lean: LiTax.jumps_exact, jumps_below_one_franc. |
| F2 | fact | proved | Model theorem; the scan's marriage bonus (12,572 CHF) is splitting. Evidence: model Lean: LiTax.joint_is_splitting. |
| F3 | fact | explained | Recorded observation (structure) with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F4 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/LI.json`): marriage bonus 12,572 = F2 (splitting); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F3).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 12.5 % (SteG Art. 61: 'Die Ertragssteuer beträgt 12,5 % des steuerpflichtigen Reinertrags' (src/steg_v31.txt:1949)); at a profit of 3 AW the best split costs 12.2 % of the profit, all salary 20.2 %, all dividends 12.5 % (employer contributions: statute rate 4.23 %); dividends beat salary once employer contributions exceed 0 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
