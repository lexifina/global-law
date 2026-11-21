# Guyana (GY) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 Above GY$4.68 million the marginal income-tax rate falls from 25 % to 23.3 %: the one-third deduction outruns the 35 % band
- kind: loophole-known
- s. 20(1)(a) allows the greater of 1,560,000 and one third of total income; above 4,680,000 every extra dollar adds 2/3 of a dollar to chargeable income, which is already in the 35 % band (threshold 3,120,000 = 2 x 1,560,000), so the marginal rate is 35 % x 2/3 = 23.3 %, below the 25 % paid between 1,560,000 and 4,680,000. The schedule is regressive at the top (scanner: top rate 23.3 %, peak 29.2 % at 0.53-0.6 AW).
- provisions: ITA ss. 20(1)(a), 36, 36A as amended by Act 2 of 2025
- Lean: GyTax.basicDeduction, GyTax.sched
- status: modelled; reproduced by the scanner

### F2 The 2025 Act amends words that the 2017 Act wrote differently ('twenty eight percent' for 'twenty-eight percent')
- kind: statute-fault
- Act 12 of 2017 s. 7 inserted in s. 36 the words 'twenty-eight percent'; Act 2 of 2025 s. 4(a) substitutes for 'twenty eight percent' (no hyphen) 'twenty five percent'. Read literally the substitution has no target; the intention is plain. Thresholds were amended with and without commas ('two million, four hundred thousand' / 'two million four hundred thousand'). Cheap to fix in a revision.
- provisions: Act 12 of 2017 s. 7; Act 2 of 2025 ss. 4, 5
- Lean: -
- status: recorded (reading: amendment applied)

### F3 The child deduction goes to one parent only and must be elected; the second-job and overtime deductions favour multiple job-holders
- kind: loophole-known
- s. 20(1)(b)-(d), (2) as replaced in 2025: GY$120,000 per child under 18 (at most 10,000 a month) to one person by election; 600,000 of second-job income and 600,000 of overtime are deductible. Splitting the same hours into a second job or overtime lowers tax.
- provisions: ITA s. 20 (Act 2 of 2025 s. 3)
- Lean: GyTax.person (inputs gyChildTo, secondJobIncome, overtimeIncome)
- status: modelled

### F4 The National Insurance rate and ceiling are not in any law: the Board sets them
- kind: gov-error
- Collection of Contributions Regulations reg. 17(1): the contribution is 'a percentage determined by actuarial calculations and approved by the Board'. The 2025 rate (5.6 %) and ceiling (280,000 a month, since January 2020) are published only on the Scheme's web page, which refuses scripts from lean1 (HTTP 406).
- provisions: NIS Collection Regs reg. 17
- Lean: GyTax.nisMonth
- status: official secondary

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Report part of the hours as overtime or a second job (600,000 each deductible) | recreated: inputs | ITA s. 20(1)(c),(d) |
| K2 | Give the child deduction to the parent with the higher marginal rate | recreated: input gyChildTo | ITA s. 20(1)(b),(2) |
| K3 | High earners benefit from the one-third deduction (23.3 % marginal rate) | recreated: F1 | ITA s. 20(1)(a) |
| K4 | Life and medical insurance premiums up to 10 % of income or 360,000 | not modelled | ITA s. 16(1)(l) |
| K5 | Interest of individuals up to 10,000 free of withholding | not modelled | ITA s. 39(1) proviso (FEA 2022) |

## Step 5: what was searched

- kernel scanners with scale 3,120,000 (start of the 35 % band)
- every Income Tax and Fiscal Enactments (Amendment) Act listed on parliament.gov.gy 2012-2026 (16 Acts, OCR)
- exe checks at 4,680,000

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
| F1 | loophole | model-proved | marginal income-tax rate 23.33 % above 4.68 M vs 23.6-25 % below: 233,334 GYD per extra million. exe and #guard L1GY.F1; statute pattern not located (the hit was the NIS text). Evidence: exe + Lean `L1GY.F1` (`world/loopholes/rest/lean/L1GY.lean`, 3 #guard): it(b)-it(a) = 233334; it(b)-it(a) = 233334; (it(d)-it(c))-(it(b)-it(a)) = 2665. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | statute-fault | explained | Amendment wording (builder). |
| F3 | loophole | model-proved | 150,000 GYD less tax on 3.6 M when 600,000 of it is overtime. exe and #guard L1GY.F3. Evidence: exe + Lean `L1GY.F3` (`world/loopholes/rest/lean/L1GY.lean`, 1 #guard): it(a)-it(b) = 150000. Known/new: **unclear**: Crossref only; the 2025 overtime and second-job deductions are a stated policy, relabelling not searched. |
| F4 | gov-error | explained | NIS rate outside law (builder). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/GY.json`): bands 26.6-26.7 % above the 23.3 % top = F1 (regressive top); timing 140,932-149,444 = F1 (non-convex schedule); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **GY-R2** Second-job income up to 50,000 a month is deductible (s. 20 as replaced 2025). Money: 150,000 GYD a year (874,000 of second-job pay at 1 AW). Lean: `world/loopholes/round2/v/lean/R2GY.lean` (R2GY.R2 (3 #guard)); exe check `round2/v/out/GY.json`. Provision: Income Tax Act Cap. 81:01 s. 20 as replaced by the 2025 amendment (model citation, GyTax/Basic.lean:10-15). Status: model-proved. Known/new: known: Budget 2025 measure, GRA guidance (web search 3); the model does not test the full-time-primary-job condition (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
