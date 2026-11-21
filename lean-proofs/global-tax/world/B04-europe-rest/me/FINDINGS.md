# ME findings (Montenegro (porez na dohodak fizičkih lica, prirez — default Opština Žabljak, doprinosi zaposlenog), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 18 000 EUR = 12 × 1 500); leads: no METR band above 100 % and no notch above 0.1 % of the scale

### F1 The 2024 PIT amendment (SL CG 88/2024) is missing from Global law
- kind: lesson (source)
- status: noted

133/2025 cites the law as '... 152/22 i 88/24'; the record has no 88/2024 act. Read from the official gazette page images (7 pages): in force 1 January 2025 (član 26); it does not change the employment rates (član 4 narrows tačka 2).

### F2 The instruction's printed 27 € equals the bands
- kind: observation (statute check)
- status: proved

Uputstvo 3/22 član 1: '27,00€+15%' above 1 000 €: `MeTax.printed_eq_bands`; the annual self-employment tariff is exactly 12 × the monthly one (`annual_is_12_months`).

### F3 Monthly taxation without reconciliation
- kind: loophole-known (structure)
- status: proved

18 000 € paid evenly pays 1 224 €; paid in one month 2 577 € (`uneven_costs_more`).

### F4 Contributions after Europe Now
- kind: observation
- status: lead checked against the statute

Health contribution abolished from 2022 (145/2021); from 1 October 2024 the employee pays 10 % pension (94/2024) and 0,5 % unemployment, the employer 0 % pension. The minimum base (general collective agreement) and the highest annual pension base were not reached.

### F5 Municipal default
- kind: convention
- status: noted

The surtax is set by each municipality (13 % in Žabljak, the decision the record holds in force on 2025-06-01); `region` other municipalities not modelled.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | record | explained | Record (lesson (source)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F2 | fact | proved | Model theorems. Evidence: model Lean: MeTax.printed_eq_bands, annual_is_12_months. |
| F3 | loophole | proved | 1,353 EUR: 18,000 paid in one month pays 2,577, evenly 1,224. Model theorem (rebuilt). Known pattern. Evidence: model Lean: MeTax.uneven_costs_more. Known/new: **unclear**: pattern: final (non-cumulative) withholding penalises uneven pay; no description found in the Crossref record (hits on withholding were unrelated). |
| F4 | fact | explained | Recorded observation with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F5 | record | explained | Record (convention): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/ME.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **ME-R1** Wage tax (monthly, final) and the annual self-employment tariff each run their own bands. Money: 2,276 EUR a year on 18,000 (1 AW) vs all wages; 386 vs all self-employment. Lean: `world/loopholes/round2/v/lean/R2ME.lean` (R2ME.R1 (4 #guard)); exe check `round2/v/out/ME.json`. Provision: Zakon o porezu na dohodak fizičkih lica član 10 (model citation). Status: model-proved. Known/new: new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
