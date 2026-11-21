# Azerbaijan (AZ) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 State-sector notch at 2 500 manat a month: the 200-manat exemption stops all at once
- kind: statute-fault
- TC 102.1.6 exempts 200 manat of monthly income 'aylıq gəliri 2500 manatadək olduqda'. At 2 500 a month the tax is 14 % of 2 300 = 322; at 2 501 it is 350 + 0.25 = 350: 28 manat a month (336 a year) more tax for 1 manat more pay. Applies to the state/oil sector table (101.1); private non-oil employees are on table 2 and are not affected in 2025.
- provisions: TC art. 101.1, 102.1.6
- Lean: AzTax.monthTax (#guard 322 / 350)
- status: proved by #guard; scanners run the default private sector only

### F2 Most private-sector wages are free of income tax until the end of 2025 (a 7-year temporary rule)
- kind: loophole-known
- Table 2 (101.1-1): 0 % up to 8 000 a month in the non-oil non-state sector 'from 1 January 2019 for 7 years'. An identical wage paid by a state or oil company bears 14-25 %; the classification of the employer is decided outside the Code (101.1-4).
- provisions: TC art. 101.1-1, 101.1-4
- Lean: AzTax.table2
- status: modelled (input sector)

### F3 Employee premiums exceed income tax for most private wages
- kind: model-fix
- Private sector: 3 % to 200 then 10 % social + 0.5 % unemployment + 2 % medical, about 11-12 % of the wage (111 on 1 000 a month), while income tax is 0 below 8 000 a month. Scan METR peak 40 % is monthly-rounding bunching (12 x whole manat), not a statutory rate.
- provisions: 250-IQ 14.4, 765-VQ 9.0.2, 725-IQ 15-10.1.2
- Lean: AzTax.monthSoc
- status: modelled

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 336 AZN a year for one manat a month above 2,500 (state and oil sector). exe and #guard L1AZ.F1. Evidence: exe + Lean `L1AZ.F1` (`world/loopholes/rest/lean/L1AZ.lean`, 1 #guard): it(b)-it(a) = 336; statute re-read: `law/m101_20250701.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | loophole | model-proved | 11,700 AZN a year on 60,000 of wages (0 in the private non-oil sector, 11,700 in the state/oil sector). exe and #guard L1AZ.F2; the hit re-read was the contribution law's parallel 7-year clause, not 101.1-1 itself. Evidence: exe + Lean `L1AZ.F2` (`world/loopholes/rest/lean/L1AZ.lean`, 2 #guard): it(a) = 0; it(b) = 11700. Known/new: **unclear**: Crossref only; the 2019 seven-year private non-oil zero rate is a widely reported reform, not searched. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AZ.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **AZ-R1** Wages on the art. 101.1 progressive table (14 % / 25 % above 2,500 a month), entrepreneurs' income at 20 % (art. 101.3). Money: 4,152 AZN a year on 180,000 (6 AW) vs all wages (2.3 %). Lean: `world/loopholes/round2/v/lean/R2AZ.lean` (R2AZ.R1 (4 #guard)); exe check `round2/v/out/AZ.json`. Provision: Tax Code art. 101.1, 101.3 'Hüquqi şəxs yaratmadan sahibkarlıq fəaliyyətini ... 20 faiz' (law/m101_20250701.txt:29). Status: confirmed. Known/new: new (weak): Crossref and OpenAlex (2026-11-21 00:02 UTC) nothing on the point; rate gap itself is published (Tax Code) (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
