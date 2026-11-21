# Suriname (SR) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The consolidated Income Tax Act still prints the 2021 solidarity levy that lapsed on 1 January 2022
- kind: gov-error
- art. 34 lid 1a and art. 34a lid 4 and 52g lid 3: 'Deze solidariteitsheffing heeft een tijdelijke karakter en gaat in op 1 februari 2021 en vervalt op 1 januari 2022' - three lapsed rate tables kept in the authority's 2024 consolidation. Harmless but confusing; the model ignores them.
- provisions: Wet IB arts. 34(1a), 34a(4), 52g(3)
- Lean: -
- status: recorded

### F2 Lump sums and overtime have their own lower scales: income can be relabelled
- kind: loophole-known
- art. 34a (lump sums: 5/15/25/35 % on request, from the first dollar) and art. 34c (overtime per month: 5/15/25 %) against 8-38 % on regular pay above 108,000. Paying part of pay as overtime lowers tax for high earners (not modelled: no input).
- provisions: Wet IB arts. 34a, 34c
- Lean: -
- status: catalogued

### F3 Deductions go to the spouse with the higher income (art. 31): no choice, no transfer of the zero band
- kind: loophole-known
- art. 31 lid 1: married couples are assessed separately and the art. 18 deductions are 'toebedeeld aan de echtgenoot met het hoogste onzuiver inkomen'.
- provisions: Wet IB art. 31
- Lean: SrTax.out
- status: modelled (no deductions modelled beyond costs)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Relabel pay as overtime (art. 34c) or a lump sum (art. 34a) | not modelled: F2 | Wet IB arts. 34a, 34c |
| K2 | Mortgage interest on the own home up to a 600,000 loan | not modelled | Wet IB art. 18 lid 1 g |
| K3 | Pay a spouse a business wage under a written agreement | not modelled | Wet IB art. 31 lid 2 |

## Step 5: what was searched

- kernel scanners with scale 234,000 (start of the 38 % band)
- belastingdienst.sr wetten page, loonbelasting and inkomstenbelasting pages

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Wet AOV (S.B. 1981 no. 30 as amended to S.B. 2002 no. 96) arts. 19-20
- AOV premium 4 % of zuiver loon for residents under 60; not deductible (IB art. 18 (1) (b), art. 8 (2) (a)). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Lapsed levy printed (builder). |
| F2 | loophole | lead | Overtime/lump-sum relabelling: not modelled. |
| F3 | fact | explained | Allocation rule (fact). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/SR.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
