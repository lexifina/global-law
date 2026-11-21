# Timor-Leste (TL) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 Two separate zero bands: wages and other income each get one
- kind: loophole-new
- Wages pay 10 % above US$500 a month (Anexo V, final tax) while business and property income pay 10 % above US$6,000 a year (Anexo VI); art. 27 (1) e) keeps wages out of the income-tax base. A resident who can receive part of the pay as a contractor fee instead of wages uses both zero bands: US$12,000 split 6,000/6,000 pays 0 of income tax, against US$600 as wages only (plus 4 % social security on wages only).
- provisions: Lei 8/2008 art. 20, 26, 27 (1) e), Anexo V, Anexo VI
- Lean: TlTax.wageTax, TlTax.incomeSched; not checked against the literature (not found in 0 sources searched: no search budget)
- status: model result

### F2 Monthly wage tax with no annual reconciliation: uneven pay costs more
- kind: loophole-known
- The resident wage tax is computed on each month's wages (Anexo V) and withholding discharges the employee (art. 25); there is no annual return for wages. US$6,000 paid as 12 x 500 pays nothing; the same US$6,000 paid as six months of 1,000 pays 6 x 50 = US$300.
- provisions: Lei 8/2008 art. 20, 25, Anexo V
- Lean: TlTax.wageTaxMonthly
- status: model result

### F3 Fine-grid 'net-income falls' are whole-dollar rounding, not notches
- kind: model-fix
- The b03scan reports 30 tiny falls for a single earner: at US$7 grid steps the monthly floor of 10 % can add US$8 of tax+contributions. No statutory notch exists in Timor-Leste's wage tax.
- provisions: Anexo V
- Lean: results/search/b03scan.md
- status: model result

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 600 USD a year on 12,000 (two zero bands: 500 a month for wages, 6,000 a year for other income). exe and #guard L1TL.F1; both annex tables re-read in the OCR. Evidence: exe + Lean `L1TL.F1` (`world/loopholes/rest/lean/L1TL.lean`, 2 #guard): it(a) = 600; it(b) = 0; statute re-read: `law/jr2008_no26.txt`. Known/new: **new**: Both thresholds are published separately (PwC, Deloitte Timor-Leste highlights 2024); no hit describes using both by splitting pay; web search 12 + Crossref. |
| F2 | loophole | explained | Arithmetic of the monthly final wage tax (Anexo V, art. 25); not expressible with the even-month contract. Known pattern (monthly final withholding). |
| F3 | record | explained | Rounding falls; the fresh scan's 1-unit notches confirm it. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TL.json`): notches of 1 = rounding (F3); bands above the 3.3 % 'top' = the scale artefact of a monthly 10 % wage tax measured at 10 x the scale (no notch).
