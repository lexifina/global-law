# Iraq (IQ) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 The GCT's consolidated page splices art. 12 into art. 13
- kind: gov-error
- On tax.mof.gov.iq the text of art. 13 (1) (ب) breaks off at '– بنسبة 1' and continues with art. 12's paragraphs 1 (non-Iraqi residents), 3 (children over 18), 4 and 5, then '6- 0% على المبالغ التي تتجاوز (500) الف' (the rest of '10%'): two articles interleaved in the official consolidation.
- provisions: arts. 12-13
- Lean: -
- status: recorded (draft note, not filed)

### F2 Housewife allowance: the wife's first dinar of income
- kind: loophole-new
- Art. 12 (1) (أ) gives the husband 2,000,000 for a wife 'ربة بيت لا دخل لها' or whose income is added to his. Without the joint election the first dinar a wife earns costs the husband 2,000,000 of allowance (generic scan before the election: notch 159,999). With the election (modelled: cheaper of separate and joint) a low-earning wife's income should be added to the husband's.
- provisions: art. 12 (1) (أ)
- Lean: IqTax.out (election)
- status: measured, fixed by the election

### F3 Two earners: 5 M + 5 M pays 590,000, one earner 10 M pays 745,000
- kind: loophole-known
- Each earning spouse has 2.5 M and the low bands; shifting income to a spouse saves up to 155,000 at 10 M (probe; scan split gain up to 401,437).
- provisions: arts. 12, 13
- Lean: probe
- status: measured

### F4 1982-2004 amounts: 15 % from 1 M dinars
- kind: statute-fault
- The bands (250,000 / 500,000 / 1,000,000) are CPA 2004 amounts; at 2025 wages the scale is a flat 15 % above the allowances.
- provisions: art. 13
- Lean: -
- status: recorded

### F5 Budget laws may change allowances and rates
- kind: statute-fault
- Art. 13 مكررة (4) lets the minister propose changes in the annual budget law: the in-force amounts depend on budget laws not consolidated in the tax law.
- provisions: art. 13 مكررة
- Lean: -
- status: recorded

### F6 Over-63 extra allowance
- kind: loophole-known
- Art. 12 (5): 300,000 more for a taxpayer over 63 (modelled). Catalogued from the statute; not in the canonical household.
- provisions: art. 12 (5)
- Lean: not modelled
- status: catalogued

### F7 Students to 25 keep the child allowance
- kind: loophole-known
- Art. 12 (3): children over 18 in secondary or higher education keep the 200,000 allowance to age 25. Catalogued from the statute; not in the canonical household.
- provisions: art. 12 (3)
- Lean: not modelled
- status: catalogued

### Generic scan (scale 4500000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 15.0 %, 0 bands > 100 %; couple_1earner_2: max METR 15.0 %, 0 bands > 100 %; couple_2earner_2: max METR 15.0 %, 0 bands > 100 %; second_earner_2: max METR 15.0 %, 0 bands > 100 %

### W5S-1 iraqi-salary-calculator (almukhader; wronglaw grid): brackets not the art. 13 scale (W5 review pass 3, 2026-11-20)
- kind: software-error
- `iq_open_iraqi_salary_calculator_almukhader_grid`: monthly brackets of 1 / 4 / 7 % from 69,000 instead of the art. 13 (1) (a) scale (3 / 5 / 10 / 15 % on income after the art. 12 allowances). Dev: the app is far below from about 4 M a year (15,390,632: 613,984 vs 1,853,594); 338 / 1,055 exact (mostly zero-tax cases).
- provisions: Income Tax Law No. 113 of 1982 as amended, arts. 12, 13 (1) (a)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/IqTax/Verify.lean` (imported by the `IqTax` library and built; each guard evaluates `IqTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/IQ.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Spliced articles on the GCT page: source record. |
| F2 | explained (not a loophole as modelled) | With the joint election (cheaper of separate and joint, art. 12 (1)(a)) the wife's first dinar costs nothing (G: f2_election_removes_notch, +1 of net). The 2 M allowance is lost only by couples who do not add the wife's income; whether the election is free in practice is open. S: law/itl113.html.txt:257 ('لزوجة دافع الضريبة ... ربة بيت لا دخل لها ، أو في حالة اضافة دخلها الى دخلــــه'). |
| F3 | confirmed | 5 M + 5 M pays 155,000 less than one earner on 10 M. G: f3_split. S: law/itl113.html.txt:257 (art. 12 allowances per taxpayer), art. 13 bands. Household-unit effect, known in kind (individual taxation). |
| F4, F5 | explained | Stale 2004 amounts; budget-law changes: records. |
| F6, F7 | explained | Catalogued. |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan timing gain 109,800 (second earner) and marriage bonus 257,812 come from the min(separate, joint) election (a minimum of two convex schedules is not convex) and the 2 M housewife allowance. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F3: Individual taxation with personal allowances: two earners pay less than one | household-unit effect | **known**: PwC Iraq (Deductions) prints the per-person allowances (bachelor IQD 2,500,000, married person 4,500,000); income splitting under individual taxation is known in kind (LaLumia (2008), 'The effects of joint taxation of married couples on labor supply and non-wage income', J. Public Econ. 92, doi 10.1016/j.jpubeco.2008.01.009). | 2026-11-20: OpenAlex specific queries 'Iraq income tax law 113 1982 allowances spouses'; 'Iraq personal income tax allowances wife joint' (781 hits, titles checked); OpenAlex broad 'Iraq personal income tax', 'Iraq income tax wages', 'Iraq tax system reform' (75 records, titles and abstracts grepped, 4 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (iraq, 5 individual pages): 13 passages with the item's terms; Crossref IMF prefix 10.5089 'Iraq tax policy' (8249 records, titles only). Record: world/loopholes/africa_mena/search/IQ-F3.json |

<!-- L1-VERIFICATION END -->
