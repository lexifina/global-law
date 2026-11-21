# Nepal (NP) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 A woman with only remuneration loses her 10 % rebate with one rupee of other income
- kind: loophole-new
- Schedule 1 para 1 (11): 'पारिश्रमिक आय मात्र आर्जन गर्ने महिला' get 10 % off the tax. A woman with 1.5 m of wages pays 211,500; with one rupee of business income, 235,000 (+23,500). An all-or-nothing condition (the scanners do not vary sex: proved on two households). Not found in the sources searched.
- provisions: ITA 2058 Schedule 1 para 1 (11)
- Lean: nptax households fem / fem+1bus
- status: model result (build phase)

### F2 Couple election (s. 50) pays for one-earner couples
- kind: loophole-known
- A resident couple may elect to be assessed together (para 1 (2): first band 6 lakh, then 8 and 11 lakh). One earner with 1.5 m: separate 235,000, couple 206,000 (29,000 less). The model picks the cheaper unless npCoupleElection is given.
- provisions: ITA 2058 s. 50; Schedule 1 para 1 (2)
- Lean: nptax households sep / couple
- status: model result (build phase)

### F3 The 1 % social security tax falls only on employment income
- kind: loophole-known
- Para 1 (1)(क): '... रोजगारीको करयोग्य आय भएमा एक प्रतिशत'; registered sole proprietors, pension income and SSF contributors are excluded. 500,000 of wages pays 5,000; 500,000 of business income pays 0.
- provisions: ITA 2058 Schedule 1 para 1 (1)(क) and proviso
- Lean: NpTax.sst
- status: model result (build phase)

### F4 Interest (6 %) and dividends (5 %) are final; employment income reaches 39 %
- kind: loophole-known
- s. 88 (2)(क), (3) and s. 92 (1)(क), (ङ): final withholding on dividends (5 %) and on bank/listed interest to natural persons (6 %); the progressive table reaches 36 % above 20 lakh and 39 % above 50 lakh.
- provisions: ITA 2058 ss. 88, 92
- Lean: NpTax.dividendRate / interestRate
- status: model result (build phase)

### F5 Top rates written as surcharges on a rate
- kind: fact
- Para 1 (1)(ङ): above 20 lakh 'खण्ड (घ) बमोजिम लागेको करको दरमा थप बीस प्रतिशत' (20 % more on the 30 % rate = 36 %), above 50 lakh 30 % more (39 %): a rate-of-rate wording; modelled as 36 % / 39 % bands, a reading.
- provisions: Schedule 1 para 1 (1)(ङ)
- Lean: NpTax.single
- status: model result (build phase)

### F6 The official Finance Act PDFs refuse non-browser downloads
- kind: gov-error
- mof.gov.np and ird.gov.np show the Finance Act 2081 in a flip-book whose PDF on giwmscdnone.gov.np answers HEAD (200, 52 MB) but closes the connection on every GET from curl or PowerShell; the consolidated Income Tax Act was read from the Internet Archive. Accessibility, not law; no bypass attempted.
- provisions: giwmscdnone.gov.np/media/pdf_upload/ (Finance Act 2081)
- Lean: -
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Couple election vs separate assessment | s. 50 | recreated (household; scanner unit family) |
| Business vs employment income in the first band (1 % SST) | para 1 (1)(क) | recreated (household) |
| Final 5-6 % on dividends and interest | ss. 88, 92 | modelled |
| Retirement contributions (r. 21: 3 lakh or 1/3) | s. 63, r. 21 | modelled |
| Insurance premium deductions (40,000 life, 20,000 health, 5,000 building) | para 1 (12), (16), (16क) | not modelled (no inputs) |
| Remote-area allowance deduction | para 1 (5) | not modelled |
| Women's 10 % rebate (all-or-nothing) | para 1 (11) | recreated (household) |

Catalogued 7, recreated 3, not modelled 2. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: IRD Nepal guides, tax-calculator tables, and the Finance Act 2081/2082 bill speeches; the SSF directives; academic literature on Nepal's tax structure: not checked. Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

### W5S4-1 nepacalc (avash81): 36 % above 50 lakh; Bhargavi ERP: the 1 % charged twice (W5 review pass 4, 2026-11-20)
- kind: software-error
- `np_open_nepacalc_avash81_grid`: Schedule 1 para 1 (1) (ङ) as amended by the Finance Act 2080: above 50 lakh an additional 30 % of the 30 % rate (39 %); dev: model above by exactly 3 % of the excess over 5,000,000 (604 cases), exact below. `np_open_bhargavierp_hpupadhyay_grid`: for an employee not in the SSF the tool deducts a 1 % social security tax and a 10 % pension from basic and also charges the 1 % first slab (para 1 (1) (क), which is that tax) in the income tax; the SSF / provident-fund amounts themselves are Pattern A (open).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 23,500 NPR for one rupee of business income (woman with 1.5 M of remuneration). exe and #guard L1NP.F1 (amount includes the 1 % SST surtax); statute text is in a legacy font, not matched by pattern. Evidence: exe + Lean `L1NP.F1` (`world/loopholes/rest/lean/L1NP.lean`, 2 #guard): tot(a) = 211500; tot(b)-tot(a) = 23500. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | loophole | model-proved | 29,000 NPR for a one-earner couple on 1.5 M electing joint assessment. exe and #guard L1NP.F2. Evidence: exe + Lean `L1NP.F2` (`world/loopholes/rest/lean/L1NP.lean`, 1 #guard): tot(a)-tot(b) = 29000. Known/new: **unclear**: Crossref only; the couple election is the Act's own choice. |
| F3 | loophole | model-proved | 5,000 NPR on 500,000 as wages, 0 as business income. exe and #guard L1NP.F3. Evidence: exe + Lean `L1NP.F3` (`world/loopholes/rest/lean/L1NP.lean`, 2 #guard): sur(a) = 5000; sur(b) = 0. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F4 | loophole | explained | Final 5-6 % on dividends and interest (published rates; dual pattern). |
| F5 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F6 | gov-error | explained | Recorded gov-error with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/NP.json`): marriage bonus 29,000 = F2; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= F4).
