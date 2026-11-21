# Pakistan (PK) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 Surcharge cliff at 10 million: one rupee of taxable income costs 241,290 rupees (salaried) or 359,000 (others)
- kind: loophole-known
- s. 4AB levies 9 % (salaried) or 10 % of the whole Division I tax once taxable income 'exceeds rupees ten million'; there is no marginal relief. Salaried: tax at 10,000,000 = 2,681,000; at 10,000,001 = 2,681,000 + 241,290. The generic METR scan finds the 1,212.6 % band from 9,983,500 to 10,004,000 (largest notch 241,289 at 10,000,000) in every family with a single earner above 2.44 x scale; the timing scanner finds that bunching income across two years around the threshold saves up to 240,771. Avoidance is obvious to a taxpayer near the threshold: defer income, contribute to an approved pension fund (s. 63 credit does not reduce taxable income, so it does not help) or split income with a spouse (individual taxation).
- provisions: ITO s. 4AB (FA 2024, proviso FA 2025)
- Lean: PkTax.salariedTotal (#guard)
- status: model result (build phase)

### F2 Profit on debt above 5 million leaves the 20 % separate tax and moves all of it into the progressive table
- kind: loophole-new
- s. 7B (3)(b): s. 7B 'shall not apply to a profit on debt that ... exceeds five million Rupees'. For a salaried person (2,400,000) with bank profit of 5,000,000 the tax is 162,000 + 1,000,000 = 1,162,000; at 5,000,001 the whole profit joins taxable income, salary falls below 75 % of it, the general table (to 45 %) applies to everything: 2,420,000 (+1,258,000 for one rupee). Holding deposits in two names (spouses are taxed separately) keeps each below 5 million. Not found in the sources searched (no literature search possible).
- provisions: ITO s. 7B (3)(b), First Schedule Div IIIA (a), Div I (1)-(2)
- Lean: PkTax.podCase (#guard)
- status: model result (build phase)

### F3 The 75 % salary test switches the whole income between two tables
- kind: loophole-known
- Div I (2) applies the salaried table only where salary 'exceeds seventy-five per cent of his taxable income'. A salaried person with 3,000,000 salary and 999,999 of business income pays 586,000; with 1,000,000 of business income the general table applies to all 4,000,000: 970,000 (+384,000 for one rupee). Conversely, converting business or rental income into salary (e.g. through an associate) can pull a taxpayer back under 75 %. The scanners' income-type families do not vary this mix; the #guard proves it.
- provisions: First Schedule Part I Div I (1), (2)
- Lean: PkTax.mixCase (#guard)
- status: model result (build phase)

### F4 One rupee of salary cuts the surcharge on a business income from 10 % to 9 %
- kind: loophole-new
- The FA 2025 proviso to s. 4AB applies the 9 % rate to 'an individual deriving income chargeable under the head "Salary"', with no minimum share (unlike the 75 % test). A sole proprietor with 20,000,000 of business income pays surcharge 809,000; with any salary at all, 728,100 (80,900 less). The FA 2026 removed the surcharge for salaried individuals altogether ('no surcharge shall be payable'), widening the gap from tax year 2027. Not found in the sources searched.
- provisions: ITO s. 4AB proviso (FA 2025; FA 2026)
- Lean: pktax households bus20m / bus20m+1sal
- status: model result (build phase)

### F5 Pensions up to 10 million pay nothing; the same amount as salary pays 2,681,000
- kind: loophole-known
- FA 2025 omitted the pension exemption (Second Schedule Part I cl. (8)) and added a proviso taxing 'pension received by an individual from a former employer' at 0 % up to ten million and 5 % above. Pension still counts in taxable income for the s. 4AB threshold: a pensioner with 12,000,000 pays 100,000 + 9 % surcharge (9,000). Pension vs salary is an income-type choice for those who can draw a pension while working for another employer.
- provisions: First Schedule Div I (2) proviso; Second Schedule cl. (8) omitted by FA 2025
- Lean: PkTax.pensionSched
- status: model result (build phase)

### F6 Super tax is a rate on the whole income: 1.5 million at 150 million
- kind: loophole-known
- Div IIB (FA 2025 column 'tax year 2026 and onwards'): 1 % of the income above 150 m, 1.5 % above 200 m, ... 10 % above 500 m, each 'of the income'. Each threshold is a notch (1.5 m, then +1.75 m at 200 m, etc.).
- provisions: ITO s. 4C, First Schedule Div IIB
- Lean: PkTax.superTax (#guard)
- status: model result (build phase)

### F7 Dividends at 15 % flat versus 35 % salary: owner-managers
- kind: loophole-known
- s. 5 / Div III (b) taxes dividends separately at 15 % (FA 2025). 2.5 m salary + 2.5 m dividends costs 560,000; 5 m salary costs 931,000. The company pays corporate tax first (29 %, Div II) so the overall comparison needs the company side (harness company.json has no PK entry: owner-manager scan skipped).
- provisions: ITO s. 5, First Schedule Div III (b), Div II
- Lean: pktax households sal5m / sal2.5m+div2.5m
- status: model result (build phase)

### F8 Section numbered '(4AB)' in brackets from 2024 until the Finance Act 2026
- kind: statute-fault
- FA 2024 inserted the surcharge as '(4AB)' (a sub-section label) in Chapter II; the FBR text of 31.07.2025 prints '4[(4AB)'; the Pakistan Code 2026 text notes 'The expression "(4AB)" substituted by the Finance Act, 2026'. A citation fault, harmless to the computation, corrected two years later.
- provisions: ITO s. 4AB footnotes 4-5
- Lean: -
- status: model result (build phase)

### F9 EOBI contributions are 1 % of the minimum wage, not of pay
- kind: fact
- EOBI Act s. 9B ('one per cent of the wages') with s. 2(p) ('wages' means the rates declared under the Minimum Wages for Unskilled Workers Ordinance): a flat amount whatever the pay, so its share of pay falls with income. The amount of the notified minimum wage was not reached (finance.gov.pk and eobi.gov.pk refuse scripts from both hosts): optional input.
- provisions: EOBI Act 1976 ss. 2(p), 9B
- Lean: PkTax.eobiRate
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Keep taxable income at or below 10 m (timing, spouse) | s. 4AB | recreated (scanner + guard) |
| Keep profit on debt per person at or below 5 m (split deposits) | s. 7B (3)(b) | recreated (guard) |
| Keep salary above 75 % of taxable income | Div I (2) | recreated (guard) |
| Receive dividends rather than salary | s. 5, Div III | recreated (households) |
| Draw a pension (0 % to 10 m) | Div I (2) proviso | recreated (households) |
| Approved pension fund and donation credits at the average rate | ss. 61, 63 | modelled, not a loophole |
| Zakat as deductible allowance | s. 60 | modelled (optional input zakat) |
| Capital gains on securities at reduced rates by holding period | s. 37A, Div VII | not modelled |
| Agricultural income exempt federally (provincial tax) | s. 41 (not read) | not modelled |
| Filer / non-filer withholding differences (ATL) | Tenth Schedule | not modelled |

Catalogued 10, recreated 5, not modelled 3. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: FBR circulars explaining the Finance Act 2025 (Income Tax Circular 2025-26), FBR Tax Expenditure Report, IMF Article IV/TA reports on Pakistan, practitioner guides (A.F. Ferguson/PwC, KPMG): not checked (no web search; fbr.gov.pk circular pages not navigated). Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 pk-tax agrees once the surcharge line is compared (case-building error, no model change)
- kind: test-note
- All 319 dev failures (wages above 10 million) are the s. 4AB surcharge, which the model already applies at 9 % for an
  individual deriving salary (proviso added by the Finance Act 2025; FBR text of 31.07.2025, ito25.txt l. 1796-1799) and
  books in `surtaxes.surcharge4AB`; the grid compares pk-tax's annualTax (surcharge included) with `contract.incomeTax`
  only. incomeTax + surcharge: 1,037 of 1,043 dev exact, 1,043 within 1 % (6 differ by 1.02-1.33 rupees: paisa).
- provisions: ITO s. 4AB and proviso (FA 2025)
- Lean: PkTax.person (unchanged)
- status: reported to the test agent (software/ISSUES.md, W2)

### W5S-1 tax-calculator-pk (waqarunnabi; wronglaw grid): a projected table (W5 review pass 3, 2026-11-20)
- kind: software-error
- `pk_open_tax_calculator_pk_waqarunnabi_grid`: the 2025-26 table is a projection (7 / 17 / 27 / 32 / 37 %), not the Finance Act 2025 salaried slabs (1 / 11 / 23 / 30 / 35 %). Dev: the app is above from about 0.8 M (2,534,955: 302,438 vs 193,040); 57 / 1,038 exact.
- provisions: ITO 2001 First Schedule Part I Division I clause (2) as substituted by the Finance Act 2025
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

### W5S4-1 salary_tax_calculator gem 0.1.4: no surcharge (W5 review pass 4, 2026-11-20)
- kind: software-error
- `pk_open_salary_tax_calculator_gem_grid` / `_y2026_grid`: ITO 2001 s. 4AB as it reads for tax year 2026 (Finance Act 2025) adds a surcharge on the tax of salaried individuals with taxable income above 10 million; the gem has none. Dev (`_y2026`): exact to 2 rupees below 10 million, model above in every case beyond (326 of 1,015).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 241,290 PKR for one rupee above 10 M (salaried, 9 %); 359,000 non-salaried. exe and #guard L1PK.F1; re-found by the fresh scan (1,212.6 %). Evidence: exe + Lean `L1PK.F1` (`world/loopholes/rest/lean/L1PK.lean`, 1 #guard): it(b)+sur(b)-it(a)-sur(a) = 241290; statute re-read: `law/ito25.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | loophole | model-proved | 1,258,000 PKR for one rupee of bank profit above 5 M (salary 2.4 M). exe and #guard L1PK.F2; the s. 7B (3) (b) text was not located by pattern in the FBR text (builder's citation). Evidence: exe + Lean `L1PK.F2` (`world/loopholes/rest/lean/L1PK.lean`, 2 #guard): tot(a) = 1162000; tot(b)-tot(a) = 1258000. Known/new: **known**: taxationpk.com 'How to Calculate Tax on Bank Profits' and pkrevenue.com 'Tax on profit on debt under Section 7B' state that profit on debt above 5 million is taxed as normal income (the cliff follows); web search 1. |
| F3 | loophole | confirmed | 384,000 PKR for one rupee of business income (3 M salary + 999,999 vs 1,000,000). exe and #guard L1PK.F3. Evidence: exe + Lean `L1PK.F3` (`world/loopholes/rest/lean/L1PK.lean`, 2 #guard): it(a)+sur(a) = 586000; it(b)+sur(b) = 970000; statute re-read: `law/ito25.txt`. Known/new: **known**: PwC Pakistan tax summaries describe the 75 % salary test and the two tables; Express Tribune on the salaried/non-salaried rates; web search 11. |
| F4 | loophole | confirmed | 80,900 PKR less surcharge on 20 M of business income with one rupee of salary. exe and #guard L1PK.F4. Evidence: exe + Lean `L1PK.F4` (`world/loopholes/rest/lean/L1PK.lean`, 1 #guard): sur(a)-sur(b) = 80900; statute re-read: `law/ito25.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F5 | loophole | confirmed | 2,681,000 PKR: 10 M of pension pays 0, 10 M of salary pays 2,681,000. exe and #guard L1PK.F5. Evidence: exe + Lean `L1PK.F5` (`world/loopholes/rest/lean/L1PK.lean`, 2 #guard): it(a)+sur(a) = 0; it(b)+sur(b) = 2681000; statute re-read: `law/ito25.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F6 | statute-fault | confirmed | 1.5 M PKR for one rupee above 150 M. exe and #guard L1PK.F6. Evidence: exe + Lean `L1PK.F6` (`world/loopholes/rest/lean/L1PK.lean`, 1 #guard): tot(b)-tot(a) = 1500000; statute re-read: `law/ito25.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F7 | loophole | model-proved | 371,000 PKR at 5 M (931,000 all salary vs 560,000 half dividends) before the 29 % company tax. exe and #guard L1PK.F7. Evidence: exe + Lean `L1PK.F7` (`world/loopholes/rest/lean/L1PK.lean`, 2 #guard): tot(a) = 931000; tot(b) = 560000. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| F8 | statute-fault | explained | Citation fault; harmless. |
| F9 | fact | explained | EOBI flat contribution (fact). |
| W2-1 | record | explained | Record (test-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PK.json`): METR 1,212.6 %, notch 241,289 and timing 240,771 = F1; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F5, F7).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 29.0 % (Income Tax Ordinance 2001, First Schedule Part I Division II: '29% for tax year 2019 and onwards' (law/ito25.txt:26994)); at a profit of 3 AW the best split costs 29.3 % of the profit, all salary 30.9 %, all dividends 39.6 % (employer contributions: not included); dividends beat salary once employer contributions exceed 17 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
