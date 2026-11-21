# Tuvalu (TV) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Schedule 6 states its rates as '% of taxable income' against bands of the whole taxable income: read literally it is a slab tariff with jumps of $1,500 at $10,000 and $2,100 at $14,000
- kind: statute-fault
- Schedule 6 para 1: '% of taxable income | (a) Taxable income of an individual, not exceeding ten thousand dollars 0% | (b) ... exceeding ten thousand dollars but not exceeding fourteen thousand dollars 15% | (c) ... exceeding fourteen thousand dollars 30%'; the Regulations (reg 4(b)) apply 'progressive tax rates ... with allowance made for the annual tax-free threshold'. Slab: 0 at 10,000, 1,500 at 10,001; 2,100 at 14,000, 4,200 at 14,001 (#guard).
- provisions: ITA Schedule 6; Income Tax Regulations reg 4
- Lean: TvTax.slabTax (#guard)
- status: modelled (switch tvReading)

### F2 Employees pay a larger provident-fund share (13 %) than employers (10 %)
- kind: statute-fault
- Provident Fund (Contributions) Regulations Schedule 1 paras 1(i), 2. Deducted before tax as an approved-fund contribution (s 15(1)(a); reg 4(a)), so the net cost is 13 % x (1 - marginal rate).
- provisions: PF (Contributions) Regs Sch 1; ITA s 15(1)(a)
- Lean: TvTax.person (#guard)
- status: modelled

### F3 The withholding regulations give the tax-free threshold only to an employee's principal job
- kind: statute-fault
- Income Tax Regulations reg 4(b): threshold allowed 'only for those employees whose wage payment constitutes their principal source of employment income'; second jobs are withheld from the first dollar, and the annual assessment must reconcile.
- provisions: Income Tax Regulations reg 4(b)
- Lean: TvTax (annual assessment)
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Split income with a spouse (two 10,000 zero bands) | recreated: filing-unit scanner: 3,602 at 2.65 x scale | ITA Schedule 6 |
| K2 | Extra provident-fund contributions deductible as approved-fund contributions | not modelled: needs an input | ITA s 15(1)(a); PF Regs Sch 1 para 1(ii) |
| K3 | Presumptive tax of $100 or $20 a quarter for registered businesses | not modelled | ITA s 5A; Regulations reg 3 |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 14,000, start of the 30 % band)
- #guard on both readings
- tuvalu-legislation.tv point-in-time lists (letters I, N, P) for 2025-07-01 and the Act's history table

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
| F1 | statute-fault | model-proved | 1,500 AUD at 10,000 of taxable income (11,494-11,495 of pay after the 13 % provident fund) under the slab reading. exe (tvReading slab) and #guard L1TV.F1; corrected location (the PF deduction comes first). Evidence: exe + Lean `L1TV.F1` (`world/loopholes/rest/lean/L1TV.lean`, 1 #guard): it(b)-it(a) = 1500. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | fact | explained | PF shares (fact). |
| F3 | statute-fault | explained | Second-job withholding. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TV.json`): bands 40-41 % above 38.6 % = rounding of the 13 % PF and tax; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
