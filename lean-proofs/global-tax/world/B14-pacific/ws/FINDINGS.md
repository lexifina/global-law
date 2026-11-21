# Samoa (WS) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The fortnightly wage-tax bands are not the annual bands: 576 x 26 = 14,976 and 962 x 26 = 25,012, so wage earners and other taxpayers face different thresholds
- kind: statute-fault
- Schedule 1 clause (7) vs clause (1); a wage of $26,000 pays 2,273 under the final fortnightly tax and would pay 2,270 on the annual scale (#guard); s 9(6) then stacks other income on wages using the annual scale (B = annual tax on the wages), not the fortnightly tax actually paid.
- provisions: ITA 2012 ss 9(6), 59, 60; Schedule 1 (1), (7)
- Lean: WsTax.wageTax, person (#guard)
- status: modelled

### F2 The salary and wage tax is final per fortnight: uneven pay is taxed more, and a year with 27 Monday-fortnights has 27 zero bands
- kind: statute-fault
- s 59(3) 'during the fortnight', (5) 'each fortnight commences on a Monday'; s 60 'final tax'. A bonus paid in one fortnight bears 27 % above $962; a calendar year can hold 27 fortnights commencing on a Monday, giving a fortnightly-paid employee one more $576 band.
- provisions: ITA 2012 ss 59, 60
- Lean: WsTax.wageTax (26 fortnights assumed)
- status: modelled (assumption listed)

### F3 The NPF employee share stops when the wage rate is below the statutory minimum: a notch at the minimum rate
- kind: statute-fault
- NPF Act s 22(6): 'Where the rate of wages is less than the minimum rate ... no sum shall be retained or recovered from the employee'. At the minimum rate the employee starts paying 10 % of the whole wage. Hourly rates are not in the contract: not modelled.
- provisions: NPF Act 1972 s 22(2), (6)
- Lean: WsTax (not modelled)
- status: recorded

### F4 Dividends from resident companies are exempt and interest is not on the annual return: investment income escapes the 27 % rate
- kind: loophole-known
- Schedule 2 Part A (1)(b); income-type scanner dividends +34.2 % at 5 x scale (interest is a model limitation).
- provisions: ITA 2012 Schedule 2 Part A (1)(b)
- Lean: WsTax.out
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay an owner-manager in exempt dividends | recreated: income-type scanner | ITA Sch 2 Part A (1)(b) |
| K2 | Hold assets over 12 months? (CGT 10 % within 12 months, 27 % after: the reverse of the usual incentive) | not modelled: holding period not in the contract | ITA Sch 1 (8) |
| K3 | Spread pay evenly across fortnights | recreated: #guard (final fortnightly tax) | ITA ss 59-60 |
| K4 | NPF pensions exempt | not modelled | ITA Sch 2 Part A (1)(d) |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 25,000, start of the 27 % band)
- #guard on the two scales
- MJCA storage listing of legislation/ (270 principal acts) for tax and contribution acts; revision notes of each act read

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | model-proved | 2,273 WST on 26,000 under the fortnightly tax vs 2,270 on the annual scale. exe and #guard L1WS.F1. Evidence: exe + Lean `L1WS.F1` (`world/loopholes/rest/lean/L1WS.lean`, 1 #guard): it(a) = 2273. |
| F2 | loophole | explained | Fortnightly final tax (pattern). |
| F3 | statute-fault | explained | Not modelled. |
| F4 | loophole | model-proved | 0 tax on dividends vs 27 % top rate. exe and #guard L1WS.F4. Evidence: exe + Lean `L1WS.F4` (`world/loopholes/rest/lean/L1WS.lean`, 1 #guard): tot(a) = 0. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/WS.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F4).
