# Maldives (MV) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 Dividends from resident companies are exempt; salary is taxed at up to 15 % plus 7 % pension
- kind: loophole-known
- s. 12 (ހ) exempts dividends a resident receives from a resident company. 3 m of salary costs 204,900 tax + 210,000 pension; 3 m of dividends costs nothing at the personal level (the company pays business profit tax, s. 9: 15 % above 500,000, not in the household model).
- provisions: ITA 25/2019 s. 12 (ހ), s. 7, s. 9
- Lean: mvtax households sal3m / div3m
- status: model result (build phase)

### F2 Monthly withholding table is exactly the annual table / 12
- kind: fact
- s. 54 (ހ) brackets 60,000 / 100,000 / 150,000 / 200,000 a month with the same rates: #guard proves monthly x 12 = annual at 7 points, so even monthly pay withholds the annual tax exactly.
- provisions: ITA 25/2019 ss. 7, 54
- Lean: MvTax.monthly (#guard)
- status: model result (build phase)

### F3 Interest exempt only up to MVR 5,000 a period; listed-security interest fully exempt
- kind: fact
- s. 12 (ޅ): interest on listed securities exempt; other interest up to 5,000 per period.
- provisions: ITA 25/2019 s. 12 (ޅ)
- Lean: MvTax.interestExempt
- status: model result (build phase)

### F4 A smooth schedule: no notches
- kind: fact
- Both scanners: max METR 21 % (15 % + 7 % pension, with the pension deductible), no net-income falls.
- provisions: s. 7
- Lean: MvTax.sched
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Take dividends rather than salary (exempt) | s. 12 (ހ) | recreated (households) |
| Pension contributions deductible | s. 19 | modelled |
| Interest on listed securities exempt | s. 12 (ޅ)(1) | modelled (input interest treated as other interest) |
| Presidential special exemptions for projects | s. 12-1 | not modelled (business) |

Catalogued 4, recreated 1, not modelled 1. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: MIRA guides and calculators (mira.gov.mv answered 403 to scripts), MIRA's Income Tax Regulation, literature on the 2020 introduction of PIT: not checked. Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 204,900 MVR of tax on 3 M of salary (plus 7 % pension) vs 0 on 3 M of dividends. exe and #guard L1MV.F1. Evidence: exe + Lean `L1MV.F1` (`world/loopholes/rest/lean/L1MV.lean`, 2 #guard): it(a) = 204900; tot(b) = 0. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F2 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F3 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F4 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MV.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F1).
