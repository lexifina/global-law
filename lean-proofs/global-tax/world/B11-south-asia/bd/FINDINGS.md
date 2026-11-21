# Bangladesh (BD) findings, B11-south-asia (2026-11-20T06:25Z)

Built from the statute only (no referee values seen). Amounts were computed with the built exe on the households named; each notch is also proved by a #guard in `lean/`. Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py at the scale in scale.json; b11scan.md fine grid).

### F1 Minimum tax of 5,000 taka from the first taka above the exempt limit
- kind: loophole-known
- Schedule 2 Part 1 proviso: 'মোট আয় করমুক্ত আয়ের সীমা অতিক্রম করিলে ন্যূনতম করের পরিমাণ হইবে ৫,০০০'. Total income 375,000 pays 0; 375,001 pays 5,000. For a salaried person (one third exempt) the notch is at a salary of 562,500 -> 562,501 (+5,000 taka for 1 taka); the minimum binds until total income 425,000. Found by both scanners (largest notch 4,999 at 562,500; for two earners again at 937,500).
- provisions: FO 2025 Schedule 2 Part 1 proviso (চ); ITA 2023 Sixth Schedule Part 1 para (27)
- Lean: BdTax (#guard minimum-tax notch)
- status: model result (build phase)

### F2 Net-wealth surcharge: 10 % of the whole tax from one taka above 4 crore of net wealth (or a second car)
- kind: loophole-known
- Schedule 2 Part 2 para (ক): surcharge on the tax at the Part 1 rates by net wealth; nil to 4 crore, 10 % above (also for more than one car or a house over 8,000 sq ft), 20 % above 10 crore, 30 % above 20 crore, 35 % above 50 crore, with no glide. Salary 3 m: surcharge 0 at a net wealth of 40,000,000 and 42,125 at 40,000,001. A wealth notch, not an income one: the incentive is to keep reported net wealth (s. 167 statement) below each step.
- provisions: FO 2025 Schedule 2 Part 2
- Lean: bdtax households 3m / 3m+
- status: model result (build phase)

### F3 Investment rebate: 15 % of eligible investment, up to 3 % of income or 10 lakh
- kind: loophole-known
- s. 78 (FO 2025 s. 58): rebate = least of 0.03 x income, 0.15 x investment, 1,000,000. Salary 3 m (income 2.5 m): investing 500,000 cuts tax from 421,250 to 346,250 (rebate 75,000 = 3 % of income, the binding cap). The rebate is a tax-saving instrument chosen by the taxpayer.
- provisions: ITA 2023 s. 78
- Lean: BdTax.rebate
- status: model result (build phase)

### F4 Exempt part of salary capped at 5 lakh: the marginal rate rises at a salary of 1.5 million
- kind: fact
- Sixth Schedule Part 1 para (27) as amended by FO 2025: one third of salary or 500,000, whichever is less. Below 1.5 m of salary the effective marginal rate is two thirds of the band rate; above it the full rate (the scanners' 32 % band for two earners at 1.39-1.41 m is this kink combined with the 20 % band edge).
- provisions: ITA 2023 Sixth Schedule Part 1 para (27); FO 2025 s. 130 (7)
- Lean: BdTax.salaryExempt
- status: model result (build phase)

### F5 The official consolidated schedule on bdlaws still prints the 4.5-lakh cap
- kind: gov-error
- The ITA 2023 schedule PDF on bdlaws (upload 1429__Schedule.pdf, Internet Archive copy of 2026-01-06) prints para (27) as 'এক-তৃতীয়াংশ বা ৪ (চার) লক্ষ ৫০ (পঞ্চাশ) হাজার' seven months after FO 2025 replaced it with 5 lakh; the section pages of the same site carry FO 2025 footnotes. Readers of the consolidated schedule get the old cap.
- provisions: bdlaws act-1429 schedule PDF vs FO 2025 s. 130 (7)
- Lean: -
- status: model result (build phase)

### F6 Finance Ordinance text layer unreadable
- kind: gov-error
- The official PDF of Ordinance 28/2025 uses a legacy (non-Unicode) Bengali font: pdftotext returns mojibake, so the gazette cannot be searched or machine-read; this batch OCR'd it. Accessibility, not law.
- provisions: bdlaws upload 2025-06-17 Ordinance-No.-28-of-2025.pdf
- Lean: -
- status: model result (build phase)

## Step 4: catalogue of known ways of paying less (statute-visible)

| item | provision | status |
|---|---|---|
| Stay below the exempt limit (minimum tax notch) | FO 2025 Sch. 2 proviso | recreated (scanner + guard) |
| Invest to claim the s. 78 rebate | ITA s. 78 | recreated (household) |
| Keep net wealth below 4 crore / a single car | FO 2025 Sch. 2 Part 2 | recreated (household) |
| Split income with a spouse (individual taxation, two exempt limits) | ITA (individual unit) | recreated (scanner unit family) |
| Higher exempt limits by category (women, 65+, disability) | Sch. 2 provisos | modelled (optional inputs) |
| Interest/dividends with withholding as final or minimum tax | s. 163 (2) | not modelled |
| Capital gains on listed securities exempt up to 50 lakh | Sixth Schedule (Paripatra 59.10) | not modelled |

Catalogued 7, recreated 4, not modelled 2. The catalogue is what the statute itself makes visible; it is not a literature review.

## Step 5: search record

No web search (session budget spent). Searched: Global law (find_provision, search_law, list_provisions, read_law, provision_history, search_changes; log `logs/gl_calls.log`), the official publisher sites named under Sources, and the Internet Archive CDX for official files. The generic scanners (`world/tools/scan_world.py`, results/search/SUMMARY.md) and the B11 fine-grid scan (results/search/b11scan.md, 0-2.5 x scale.json, 2,000 steps, three families) were run on the built exe.

Literature not checked: NBR Income Tax Guide (Nirdeshika) 2026-27 and the Paripatra worked examples (referee values: deferred), IMF Article IV and tax-expenditure studies, practitioner guides: not checked. Claims of novelty above say 'not found in the sources searched' only; with no literature search they are leads, not established novelties.

## Round W4 (improvement agent, 2026-11-20): W3 dev failures settled from the statute

### W4-1 Finance Act 2026 replaces FO 2025's rates for tax year 2026-27 (model fix: 400,000 threshold)
- kind: model-fix
- Finance Act 2026 (Act No. 96 of 2026, Gazette Extraordinary 30 June 2026, in force 1 July 2026: s. 1 (2);
  law/w4/fa2026.pdf from nbr.gov.bd, sha256 3063c8b4...; Bengali OCR, rate pages read as images) s. 160 (1): tax for
  "২০২৬-২০২৭ হইতে ২০৩০-২০৩১ করবর্ষের" at its Schedule 2 Part 1; para (ক) "২০২৬-২০২৭ এবং ২০২৭-২০২৮ করবর্ষের জন্য করহার":
  ৪,০০,০০০ nil, then 10 / 15 / 20 / 25 / 30 % on 3 / 4 / 5 / 20 lakh; women and 65+ ৪,৫০,০০০, third gender and disabled
  ৫,২৫,০০০, war-wounded and July warriors ৫,৫০,০০০, + ৫০,০০০ per disabled child; minimum tax 5,000 / 1,000; Part 2
  surcharge unchanged (gazette p. 20430). Tax year 2026-27 is the same tax year that FO 2025 s. 136 covered
  ("২০২৬ সালের ১ জুলাই তারিখে আরব্ধ করবর্ষ", income year 2025-26), so the later Act governs it. Both calculators were
  right; the model was one Act behind. Dev: bd-income-tax-skills 65 / 613 -> 1,053 / 1,053; mfaysal 53 / 610 -> 1,056 /
  1,057 (of 1,053 / 1,057). FA 2026 s. 61 (s. 78 rebate 0.10 and 7.50 lakh, from 1 July 2026) not applied to income
  year 2025-26 (the model applies Act amendments from the income year beginning on their date, as it did FO 2025's own
  s. 78 change): a reading, flagged in the source docstring. FINDINGS items that quote 375,000-based notches (F-items of
  the build) describe the FO 2025 schedule and are superseded for this year by 400,000.
- provisions: FA 2026 s. 1 (2), s. 160, Schedule 2 Parts 1-2; FO 2025 s. 136
- Lean: BdTax.sched, BdTax.exemptLimit (#guards updated)
- status: model changed

### W5S-1 @classytic/bd-tax (wronglaw grid): no s. 32 exemption (W5 review pass 3, 2026-11-20)
- kind: software-error
- `bd_open_bd_tax_classytic_grid`: salary taxed in full; the one-third / 500,000 exemption of salary income is not applied. Dev: the app is above by exactly 30 % x 500,000 = 150,000 at high wages and by one third of the salary x the marginal rate below; 33 / 1,042 exact.
- provisions: Income Tax Act 2023 s. 32 with the Sixth Schedule Part 1 (exempt one third of salary, at most 500,000)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 5,000 BDT for one taka of salary at 600,000 (total income just over the 400,000 exempt limit of FA 2026). exe and #guard L1BD.F1; corrected for FA 2026 (W4): FINDINGS' 375,000 / 562,500 edges are superseded by 400,000 / 600,000; also re-found at 1,000,000 and 1,500,001 for couples. Evidence: exe + Lean `L1BD.F1` (`world/loopholes/rest/lean/L1BD.lean`, 1 #guard): it(b)-it(a) = 5000; statute re-read: `law/ord28_2025.ocr.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | loophole | model-proved | 41,500 BDT of surcharge on a 3 M salary for one taka of net wealth above 4 crore (FA 2026 rates; FINDINGS' 42,125 was FO 2025). exe and #guard L1BD.F2; corrected amount. Evidence: exe + Lean `L1BD.F2` (`world/loopholes/rest/lean/L1BD.lean`, 1 #guard): tot(b)-tot(a) = 41500. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | fact | model-proved | Investment rebate: modelled; a choice the statute offers (not re-measured). Evidence: exe + Lean `L1BD.F3` (`world/loopholes/rest/lean/L1BD.lean`, 1 #guard): it(a) = 415000. |
| F4 | fact | explained | The scan's 32 % band (two earners) is this kink. |
| F5 | gov-error | explained | Stale consolidated schedule (builder's record). |
| F6 | gov-error | explained | Accessibility note. |
| W4-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BD.json`): notches 4,999 at 600,000 / 1,000,000 / 1,500,001 = F1 (FA 2026 edges, couples); band 32 % above 30 % = F4.
