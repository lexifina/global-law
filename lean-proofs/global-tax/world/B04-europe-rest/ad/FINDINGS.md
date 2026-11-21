# AD findings (Andorra (impost sobre la renda de les persones físiques; cotitzacions CASS), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 40 000 EUR = the end of the 5 % effective band); leads: no METR band above 100 % and no notch above 0.1 % of the scale

### F1 The 10 % tax with the bonus is a three-band tariff
- kind: observation (proved)
- status: proved

Art. 35.1 (24 000), 41 (10 %), 46 (bonus 50 % of 10 % of the base less 24 000, at most 800) and 47 (not below 0) equal 0 % / 5 % / 10 % bands at 24 000 and 40 000 for a single person (`AdTax.literal_eq_effective`).

### F2 The bonus ignores the family reductions
- kind: observation (structure)
- status: proved (value)

The art. 46 bonus is computed on the base less 24 000 only, not less the child reductions: above 40 000 € each 750 € child reduction is worth 75 € (`child_worth_75`); just above 24 000 € the reductions can push the quota below the bonus, and the floor of art. 47 wastes the difference.

### F3 Spouse transfer up to 40 000 €
- kind: reading
- status: reading

Art. 35.1: 40 000 € when the spouse has no income; with some income the unused part of the spouse's 24 000 € passes to the other (third paragraph, read as up to 16 000 €).

### F4 Rounding artefact in the model (fixed)
- kind: model-fix
- status: fixed

The first build rounded the quota and the bonus to whole euros separately; the scanner found 358 unit steps where total tax fell by 1 €. The law's amounts carry cents and set no rounding rule: quota, bonus and savings tax are now computed in cents and the household's tax is rounded half-up to the euro once. Rescan: 0 unit steps where tax falls; `literal_eq_effective` and `child_worth_75` (now 7 500 cents) re-proved.


### W5R4-1 CASS employee general branch is 3 % since 31 March 2016, not Llei 18/2014's 2 % (model fixed, W5 review pass 4, 2026-11-20)
- kind: model-fix (missed amending law)
- provisions: Llei 17/2008 art. 100.1 as replaced by Llei 2/2016 (pressupost 2016) disposició final sisena §1 (BOPA 20/2016, 2016-03-30; in force 2016-03-31); Llei 18/2014 arts. 26 (6 % / 2 %, with art. 100.3: the budget law may change it) and 29 (retirement 8,5 % / 3,5 %)
- The model read art. 100 as Llei 18/2014 left it ("Part assalariada | 2%") and missed that the 2016 budget law rewrote it ("Part empresarial | 7%", "Part assalariada | 3%"); no later text in the Global law corpus replaces art. 100. Employee CASS is 6,5 % (3 + 3,5), which also lowers the IRPF work income (art. 13). Found on the Xenna grid (`ad_open_xenna_corto735_grid`, the tool at 6,5 %): employeeSocial 0 -> 1,047 / 1,047 dev exact.
- Lean: `AdTax.cassGeneral` 300 (#guard), `cass` / `workNet` take the flag; input `adCassGeneral2014: true` restores the old rate (check `world/w5/review4/check4.py AD`: 0 / 300 random households differ from the pre-change exe with it; 279 / 300 change without it). Sources: `law/w5/` (SHA256SUMS). Rescanned (`scan_world.py AD`).
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | proved | Model theorem. Evidence: model Lean: AdTax.literal_eq_effective. |
| F2 | fact | proved | Model theorem; structure, not a loophole. Evidence: model Lean: AdTax.child_worth_75. |
| F3 | reading | explained | The fresh scan's marriage bonus (1,600 EUR) is this spouse transfer. |
| F4 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5R4-1 | record | explained | Record (model-fix (missed amending law)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AD.json`): marriage bonus 1,600 = F3 (spouse transfer); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
