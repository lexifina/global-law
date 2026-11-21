# Kazakhstan (KZ) findings, B05-former-ussr (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`).

### F1 Contributions are deducted before the flat 10 %: effective 19 % on a typical wage, falling above the caps
- kind: model-fix
- OPV 10 % (cap 50 MZP = 4.25 m a month) and VOSMS 2 % (cap 10 MZP = 850 000 a month) are deducted from the base (art. 342(1)), so the combined rate is 10 % + 12 % - 1.2 % = 20.8 % below 850 000 a month (scan peak 20.8 %), falling to 19 % and then 10 % above the caps: regressive at the top.
- provisions: TC art. 320, 342; Social Code art. 249; Law on OSMS art. 28
- Lean: KzTax.adultRow
- status: modelled

### F2 Dividends from a resident company are tax-free up to 30 000 MRP (118 m tenge) a year
- kind: loophole-known
- art. 341(1)(8) excludes dividends from a resident legal entity within 30 000 MRP a year, against 10 % + 12 % contributions on salary: owner-managers prefer dividends (company-side profit tax not read).
- provisions: TC art. 341(1)(8)
- Lean: KzTax.divExempt
- status: modelled (conditions of art. 341 beyond the cap not read: flagged)

### F3 Large-family deduction (4+ minors) worth up to 108 523 tenge of tax a year
- kind: model-fix
- art. 347: 23 MRP a month to one parent (or 12 + 12), capped at 282 MRP.
- provisions: TC art. 347
- Lean: KzTax.largeFamilyYear
- status: modelled

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F2 | loophole | confirmed | 0 tax on 10 M KZT of dividends from a resident company (within 30,000 MRP). exe and #guard L1KZ.F2. Evidence: exe + Lean `L1KZ.F2` (`world/loopholes/rest/lean/L1KZ.lean`, 1 #guard): tot(a) = 0; statute re-read: `law/art341.txt`. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/KZ.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F2).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 20.0 % (Tax Code K1700000120 art. 313 p. 1: '... подлежит обложению налогом по ставке 20 процентов' (law/adilet_K1700000120_wb20250611.html:11978)); at a profit of 3 AW the best split costs 20.0 % of the profit, all salary 27.6 %, all dividends 20.0 % (employer contributions: statute rate 11.00 %); dividends beat salary once employer contributions exceed 1 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- mix.py (wage vs fee split): lead: the model gives the art. 346 standard deduction only when wages > 0; art. 342 (2) 2) lets a person apply it himself, so the SE-only case may be too high (model reading, not changed).
<!-- R2-SCANNERS:END -->
