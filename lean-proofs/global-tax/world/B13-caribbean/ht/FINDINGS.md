# Haiti (HT) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The tax authority publishes only the 2026 Code: the law that governed 2025 is not on its site
- kind: gov-error
- dgi.gouv.ht's media library (WordPress search 'code fiscal', 'decret', '2022', 'loi', 'bareme') returns only Code-Fiscal.pdf of October 2026 (in force 1 October 2026, art. 540). The Décret du 19 décembre 2022 it replaces was not found; the model is for 2026-27 and says so.
- provisions: Code Fiscal 2026 arts. 540-543
- Lean: HtTax.country (year 2026-27)
- status: recorded

### F2 The 1 % CAS levy on salaries is deductible from income for income tax
- kind: model-fix
- art. 243 1. b. (1 % of monthly salaries) and art. 126 1. c. ('les prélèvements légalement effectués sur les salaires autres que l'impôt sur le revenu'). The levy's net cost is reduced by the marginal rate.
- provisions: Code Fiscal arts. 126, 243
- Lean: HtTax.person
- status: modelled

### F3 Bonuses and supplements are withheld at flat 10 %/15 % but taxed at up to 30 % in the annual return
- kind: loophole-known
- art. 103: 'Toutes autres rémunérations en numéraire, additionnelles au salaire de base, sont frappées d'une retenue à la source de quinze pour cent (15 %), à l'exception du boni ... dix pour cent (10 %)'; art. 100: salaries are withheld at one twelfth of the annual tax. Withholding below the final rate shifts tax to the April return (cash-flow gain).
- provisions: Code Fiscal arts. 100, 103, 133
- Lean: -
- status: catalogued

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Deduct 25 % of rent of the main home, mortgage interest, insurance, medical and school costs | not modelled: inputs needed | Code Fiscal art. 126 |
| K2 | Split income between spouses (separate declarations) | recreated: filing-unit scanner | Code Fiscal art. 3 |
| K3 | Bonus paid instead of salary (10 % withholding) | not modelled: F3 | Code Fiscal art. 103 |

## Step 5: what was searched

- kernel scanners with scale 1,080,000 (start of the 25 % band)
- DGI site pages and WordPress media search

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Access (builder). |
| F2 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F3 | loophole | lead | Withholding below the final rate on bonuses (cash-flow); not modelled. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/HT.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
