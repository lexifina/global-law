# Jordan (JO) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 Reading: is the 30 % rate on the part above 1,000,000 or on the whole income?
- kind: statute-fault
- Art. 11 (أ) (7): "(30%) … عن كل دينار من الدخل الخاضع للضريبة للمكلف الذي يزيد على (1000000)". Grammatically "الذي يزيد" can attach to the income (marginal reading, modelled) or to the taxpayer (30 % on every dinar of a taxpayer above 1,000,000: 300,000 at 1,000,001 against 247,500 on the marginal reading, a notch of about 52,500). Measured on the exe (marginal reading): 1,009,000 -> 1,010,000 costs 310 (30 % + 1 % national contribution).
- provisions: art. 11 (أ) (6)-(7)
- Lean: JoTax.sched, #guard taxOn 1000100
- status: reading recorded; the marginal reading modelled

### F2 The consolidated text numbers the rate items 1, 2, 4, 5, 6, 7
- kind: gov-error
- The ISTD's consolidated art. 11 (أ) skips item 3 ("1 - 5% … 2- 10% … 4- 15% …"): a numbering slip in the published text (or a lost item). The amounts form a consistent 5,000-wide ladder, so no rate seems lost; the item numbers cannot be cited reliably.
- provisions: art. 11 (أ)
- Lean: -
- status: drafted note, not filed

### F3 Bank interest: final 5 % against up to 30 % on wages
- kind: loophole-known
- Art. 12 (أ) (2) withholds 5 % on bank interest as final tax and (ج) keeps it out of gross income. A single person with 30,000 of wages pays 5,000 (tax + SSC); with 20,000 of wages and 10,000 of interest 2,900. Shifting pay into interest-bearing deposits (e.g. owner-managers lending to their company through a bank) saves the marginal rate less 5 %.
- provisions: arts. 11, 12 (أ) (2), (ج)
- Lean: probe (logs/probe.json)
- status: measured

### F4 Dividends of resident companies and most capital gains are exempt
- kind: loophole-known
- Art. 4 (أ) (8) exempts dividends (except banks, telecoms, mining, insurance, financial companies) and (5) capital gains outside depreciation: an owner-manager can take profit as dividends taxed only at company level (20 % art. 11 (ب) (1)) rather than salary up to 25-30 %.
- provisions: art. 4 (أ) (5), (8); art. 11 (ب)
- Lean: not modelled (company side)
- status: catalogued

### F5 Couple's exemptions capped at 23,000: a child adds nothing for a one-earner couple
- kind: loophole-new
- The dependants' 9,000 covers dependants "مهما كان عددهم" (whatever their number): a one-earner couple with no child already uses it for the spouse, so children add no exemption. For a two-earner couple a first child adds 5,000 (cap 23,000 - 18,000) and further children nothing. Probe: couple 30,000 + 20,000: 6,350 with one child vs 7,400 without. Generic scan: splitting gain married up to 1,852 (10.3 % AW).
- provisions: art. 9 (أ) (2), (ب) (1)
- Lean: JoTax.exemptions
- status: measured

### F6 Social security ceiling indexed but not printed
- kind: gov-error
- SSL art. 20 (أ) fixes 3,000 a month and (ب) indexes it to inflation every January; the indexed amount is not in the law (published by the SSC). The model uses 3,000 and flags it.
- provisions: SSL art. 20
- Lean: JoTax.ssc
- status: flagged

### F7 End-of-service pay: first 15,000 exempt, the rest at 9 %
- kind: loophole-known
- Art. 4 (أ) (13) (ج), (د): severance for service from 2015 is exempt up to 15,000 and taxed 9 % above: deferring pay into end-of-service benefits beats the 20-30 % bands. Catalogued from the statute; not in the canonical household.
- provisions: art. 4 (أ) (13)
- Lean: not modelled
- status: catalogued

### F8 Pensions: 2,500 a month exempt
- kind: loophole-known
- Art. 4 (أ) (14): the first 2,500 JOD of the monthly pension is exempt (modelled), so retirement income is largely untaxed. Catalogued from the statute; not in the canonical household.
- provisions: art. 4 (أ) (14)
- Lean: not modelled
- status: catalogued

### Generic scan (scale 18000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 33.3 %, 0 bands > 100 %; couple_1earner_2: max METR 30.6 %, 0 bands > 100 %; couple_2earner_2: max METR 36.1 %, 0 bands > 100 %; second_earner_2: max METR 33.3 %, 0 bands > 100 %

### W5S-1 private-teachers-salary-calculator: no social-security wage ceiling (W5 review pass 2, 2026-11-20)
- kind: software-error
- `jo_open_private_teachers_salary_calculator_grid`: calculateSocialSecurity charges 7.5 % on the whole wage; the Social Security Law 1/2014 art. 20 caps the insurable wage (3,000 JOD a month, indexed; the indexation is open in the model, IMPROVE_W5 row 18).
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: SSL art. 20 (أ)-(ب); SSC press release on the 2026 ceiling (3,733; "كان العام الماضي (3668)"), official secondary
- SSC 7.5 % on wages up to the 2025 indexed ceiling 3,668 JOD / month (was the statutory 3,000). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/JoTax/Verify.lean` (imported by the `JoTax` library and built; each guard evaluates `JoTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/JO.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | Reading of art. 11 (a)(7) (30 % on every dinar of a taxpayer above 1,000,000): the marginal reading is modelled (no notch at 1,000,000 -> 1,000,001 on the exe); the other reading would be a 52,500 notch. Needs the ISTD's practice. |
| F2 | explained | Item numbering slip in the consolidation: law/itl_p2.txt:158-162 (items 1, 4, 6 shown). |
| F3 | confirmed | Bank interest at a final 5 %: moving 10,000 of a 30,000 income from wages to deposit interest keeps 2,100 more (tax + SSC 5,000 -> 2,900). G: f3_interest_final_5pct. S: law/itl_p2.txt:204 (art. 12 (a)(2): interest 'بنسبة (5%) للشخص الطبيعي ... على أن تعتبر هذه المبالغ المقتطعة ضريبة قطعية'). |
| F4 | explained | Dividends exempt (art. 4 (a)(8)): company side not modelled. |
| F5 | confirmed (qualified) | The dependants' 9,000 is one amount 'مهما كان عددهم' and the couple cap is 23,000: for two earners a first child adds 1,050 of net (5,000 of exemption) and further children nothing; for a one-earner couple children add nothing. Qualification: art. 9 (a)(3)(c) adds 1,000 per child (max 3,000) against invoices for treatment/education/rent, which the model leaves out, so a one-earner family with such bills gains up to 3,000 of exemption within the cap. G: f5_first_child_two_earners, f5_second_child_nothing, f5_one_earner_children_nothing. S: law/itl.txt:1390-1404 (art. 9 (a)(2), (a)(3), (b)(1) '(23000) دينار'). |
| F6 | explained | SSC ceiling indexed outside the law: W5A-1 now uses 3,668 a month (2025). |
| F7, F8 | explained | Catalogued. |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| W5S-1, W5A-1 | explained (record of model/test work, not a loophole; kept as written) | SSC 7.5 % to 3,668 a month present (2,250 at 30,000; 3,301 at the ceiling). |
| Leads | explained | Rescan timing gain 1,201 (single, 2.4 +- 1.0 'AW') comes from the SSC ceiling (44,016 a year: 7.5 % stops), a contribution-ceiling regressivity, not a tax loophole; split gain 2,453 = the 23,000 cap and individual taxation. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F3: Bank interest at a final 5 % against wage rates to 30 % | income-type gap | **unclear**: No source describes the gap, and PwC Jordan (Income determination) says 'Interest income is taxable and should be included in taxable income of the individual', contradicting art. 12 (a)(2)'s final 5 % for natural persons: the guide is wrong or practice differs (a draft note for its authors). | 2026-11-20: OpenAlex specific queries 'Jordan income tax bank interest final withholding 5%'; 'Jordan income tax law 2014 amendment 2018 interest deposits' (3209 hits, titles checked); OpenAlex broad 'Jordan personal income tax', 'Jordan income tax wages', 'Jordan tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (jordan, 5 individual pages): 9 passages with the item's terms; Crossref IMF prefix 10.5089 'Jordan income tax reform 2018' (5094 records, titles only). Record: world/loopholes/africa_mena/search/JO-F3.json |
| F5: Dependants' 9,000 JOD whatever their number; couple cap 23,000: further children add nothing | household-unit effect | **known**: PwC Jordan (Deductions): 'JOD 9,000 ... for the resident dependants, regardless of their number' and 'the exemption amount granted to a single family shall not exceed JOD 23,000'. | 2026-11-20: OpenAlex specific queries 'Jordan income tax exemptions dependents 23,000 family'; 'Jordan personal income tax exemption spouse dependents cap' (280 hits, titles checked); OpenAlex broad 'Jordan personal income tax', 'Jordan income tax wages', 'Jordan tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (jordan, 5 individual pages): 5 passages with the item's terms; Crossref IMF prefix 10.5089 'Jordan income tax reform 2018' (5094 records, titles only). Record: world/loopholes/africa_mena/search/JO-F5.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 2.25 AW (contribution rate 7.8 -> 7.2 %, combined marginal 32 -> 33 %); ceiling at 2.45 AW (contribution rate 7.2 -> 0.0 %, combined marginal 32 -> 25 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
