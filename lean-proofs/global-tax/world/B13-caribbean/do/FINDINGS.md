# Dominican Republic (DO) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The DGII's printed 2025 table does not match its own bands: RD$79,776 where the bands give RD$79,775.15, and the table jumps RD$2 at its threshold
- kind: gov-error
- 15 % x (624,329 - 416,220) = 31,216.35 (printed 31,216); + 20 % x (867,123 - 624,329) = 79,775.15 (printed 79,776). Applying the printed formula, tax is 79,774 at 867,123 and 79,776 at 867,124 (#guard). The 2025 table also writes 'hasta RD$624,329.00' where the 2026 table writes '.01'.
- provisions: DGII Escala retencion asalariados 2025; Codigo Tributario art. 296
- Lean: DoTax.printedTax (#guard)
- status: recorded (official secondary)

### F2 The Code keeps a second, older exempt amount: RD$257,280 'ajustables por inflación' in art. 299 o) beside the art. 296 zero band
- kind: statute-fault
- Art. 299 o) (Ley 557-05) exempts net income up to RD$257,280 adjustable for inflation; art. 296 (Ley 253-12) makes income up to RD$399,923 (indexed) exempt. Two indexed exemptions for the same income; the later supersedes in practice.
- provisions: Codigo Tributario arts. 296, 299 o)
- Lean: -
- status: recorded

### F3 Indexation of the scale is statutory but was not applied in 2026: the 2026 table equals the 2025 table
- kind: loophole-known
- Art. 296 Párrafo I: the scale 'será ajustada anualmente por la inflación acumulada'; DGII's 2026 table prints the same thresholds as 2025 (bracket creep). Whether a budget law suspended the adjustment was not checked.
- provisions: Codigo Tributario arts. 296, 327
- Lean: -
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Dividends taxed by final withholding rather than the scale | not modelled | Codigo Tributario art. 308, 299 ñ) |
| K2 | Gain on sale of the main home exempt up to RD$500,000 | not modelled | art. 299 m) |
| K3 | Individual taxation: split income in the household | recreated: filing-unit scanner | art. 296 (personas naturales) |

## Step 5: what was searched

- kernel scanners with scale 867,123 (start of the 25 % band)
- Codigo Tributario Titulo II read for exemptions and deductions (arts. 287-300, 327)

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
| F1 | gov-error | model-proved | DoTax.printedTax #guard (model build): 79,775.15 by the bands vs 79,776 printed. |
| F2 | statute-fault | explained | Two exemptions (builder). |
| F3 | gov-error | confirmed | art. 296 Párrafo I re-read ('ajustada anualmente por la inflación acumulada'); DGII 2026 table unchanged (builder). Bracket creep; not a taxpayer loophole. Evidence: exe + Lean `L1DO.F3` (`world/loopholes/rest/lean/L1DO.lean`, 1 #guard): it(a) = 0; statute re-read: `law/t2.txt`. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/DO.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
