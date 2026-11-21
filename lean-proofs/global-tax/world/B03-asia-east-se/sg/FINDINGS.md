# Singapore (SG) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 Spouse relief cliff at $8,000 of the spouse's income
- kind: loophole-known
- Spouse relief ($2,000) needs the spouse's annual income (including exempt interest, dividends and pensions) not to exceed $8,000. Earner $100,000 + spouse $8,000 -> spouse $8,001 changes the household's tax by 197 dollars (the $2,000 relief valued at the earner's 7 % / 11.5 % marginal rates: chargeable income moves from 79,240 to 81,240).
- provisions: ITA s. 39 (as published by IRAS: Spouse Relief, YA 2026)
- Lean: SgTax.spouseRelief
- status: model result

### F2 CPF phase-in band: 60 % employee contribution on wages between $500 and $750 a month
- kind: fact
- Employee CPF is nil up to $500 a month and 0.6 x (wage - 500) up to $750, where it reaches 20 % of the whole wage: each extra dollar in that band costs 60 cents of contributions.
- provisions: CPF Act First Schedule (CPF Board table)
- Lean: SgTax.cpfMonthly
- status: model result

### F3 No personal income tax rebate for YA 2026
- kind: fact
- IRAS lists rebates for YA 2024 (50 %, max $200) and YA 2025 (60 %, max $200) and none for YA 2026 (income 2025).
- provisions: IRAS individual income tax rates page
- Lean: SgTax.out
- status: model result


## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 CPF for employees above 55 (model fix from the CPF Board's 2025 table)
- kind: model-fix
- The model had no 2025 rates above age 55 (employeeSocial 0, `unsupported`). CPF Board, "CPF Contribution Rate Table
  from 1 January 2025" (law/cpf_rates_2025.pdf, Table 1, fetched 2026-11-20, sha256 in SHA256SUMS): employee's share
  [17 % (OW)] above 55-60, [11.5 %] above 60-65, [7.5 %] above 65-70, [5 %] above 70, phase-in 0.51 / 0.345 / 0.225 /
  0.15 (TW - 500) from 500 to 750, OW capped at 7,400; maxima 1,258 / 851 / 555 / 370 (#guard). CPF relief follows.
  Dev (local rerun): employeeSocial 32 / 281 -> 36 / 406 exact / within 1 %, incomeTax 104 / 182 -> 106 / 216.
- provisions: CPF Act First Schedule as tabled by the CPF Board (2025)
- Lean: SgTax.cpfBand, SgTax.cpfMonthlyAt (#guard)
- status: model changed

### W2-2 PolicyEngine-SG caps ordinary wages at the annual ceiling (software error); its income tax is YA 2025
- kind: software-error
- The package caps employee CPF at min(wages, 102,000) x rate and never applies the monthly OW ceiling ($7,400 in
  2025: "OW: Ordinary Wages (capped at OW ceiling of $7,400)", employee maximum $1,480 a month at 55 and below). Its
  income-tax parameters are by year of assessment (PIT rebate 60 %/$200 at 2025-01-01, 0 at 2026-01-01), so the grid's
  period 2025 is YA 2025, against the model's income year 2025 = YA 2026, for which IRAS lists no rebate. The child
  relief differences are who claims the QCR (the package: the first adult; the model: the higher earner; IRAS lets the
  parents share it) and the package's WMCR for married women (sex is not a contract input): allocation choices, no change.
- provisions: CPF 2025 Table 1; IRAS rates page (rebates YA 2024, YA 2025 only)
- Lean: SgTax.cpfAnnual
- status: recorded in software/ISSUES.md (W2)

### W5 note: iit-estimator child reliefs not entered (mapping) (W5 review pass 2, 2026-11-20)
- kind: test-side
- `sg_open_iit_estimator_economist1895_grid`: misses of 4,000 x the marginal rate per child are the adapter's (child reliefs are amount inputs, none entered); rebuild requested. Not a software error.
- status: recorded (world/IMPROVE_W5.md pass 2)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 196 SGD (FINDINGS said 197) for one dollar of the spouse's income above 8,000 with an earner on 100,000. exe and #guard L1SG.F1; corrected to 196. Evidence: exe + Lean `L1SG.F1` (`world/loopholes/rest/lean/L1SG.lean`, 1 #guard): it(b)-it(a) = 196; statute re-read: `law/iras_spouse.html`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | fact | confirmed | 60 cents per dollar of wages between 500 and 750 a month. exe and #guard L1SG.F2 (720 on 600 a month; 0 on 500); CPF Board page re-read. Evidence: exe + Lean `L1SG.F2` (`world/loopholes/rest/lean/L1SG.lean`, 2 #guard): soc(a) = 720; soc(b) = 0; statute re-read: `law/cpf_howmuch.html`. |
| F3 | fact | explained | IRAS rebates YA 2024-2025 only (official secondary). |
| W2-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W2-2 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5 | record | explained | Record (test-side): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/SG.json`): notch 140 at 8,000 (second earner) = F1; band 91 % above the top = F2 (CPF phase-in); timing 10,154 (11.4 % of the scale) = the CPF ordinary-wage ceiling (7,400 a month): bunching pay above it in one year saves employee CPF, explained; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
