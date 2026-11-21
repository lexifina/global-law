# Yemen (YE) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 Authority: the Sana'a Tax Authority's text; two legal orders
- kind: statute-fault
- tax.gov.ye is run from Sana'a (Law 8/2020 'صدر برئاسة الجمهورية – بالعاصمة صنعاء' by the Supreme Political Council). Its art. 160 (ج) exempts employees of small and micro enterprises from payroll tax; the internationally recognised government in Aden has not enacted it. A worker's tax depends on which authority controls the employer's area.
- provisions: Law 8/2020 art. 1
- Lean: -
- status: recorded

### F2 Each income category gets its own 120,000 exemption and scale
- kind: loophole-new
- Art. 62 applies the scale separately to the proceeds of each tax (payroll, commercial/industrial profits, professions): 1,200,000 of wages costs 174,000, 600,000 of wages + 600,000 of business profit 132,000 (probe). Splitting income between categories saves up to the 120,000 exemption and the lower bands again.
- provisions: arts. 62, 67
- Lean: YeTax.out, probe
- status: measured

### F3 Bonuses taxed at a flat 15 % outside the scale
- kind: loophole-known
- Art. 66: bonuses, overtime, commissions and other non-salary payments to employees are taxed at 15 % without the exemption: for a high earner (20 % band) paying part of pay as bonuses saves 5 points; for a low earner it costs.
- provisions: art. 66
- Lean: not modelled
- status: catalogued

### F4 Amounts unchanged since 2010
- kind: statute-fault
- The 120,000 exemption (about 10,000 a month) and band limits are nominal amounts of 2010; with the rial's fall the 20 % band starts at a very low real income.
- provisions: art. 62
- Lean: -
- status: recorded

### F5 Only an English translation is published
- kind: gov-error
- The authority publishes Law 17/2010 as '17-en.pdf' (English); the Arabic original was not found on its site.
- provisions: -
- Lean: -
- status: recorded

### F6 Job-expense allowances outside taxable pay
- kind: loophole-known
- Art. 49 (b): allowances for representation, hospitality, travel and transport are not taxable within the executive regulations' limits: pay restructured as allowances. Catalogued from the statute; not in the canonical household.
- provisions: art. 49 (b)
- Lean: not modelled
- status: catalogued

### F7 Pensions and severance exempt
- kind: loophole-known
- Art. 50 (d): pension and severance allowances are exempt. Catalogued from the statute; not in the canonical household.
- provisions: art. 50 (d)
- Lean: not modelled
- status: catalogued

### Generic scan (scale 840000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 20.0 %, 0 bands > 100 %; couple_1earner_2: max METR 20.0 %, 0 bands > 100 %; couple_2earner_2: max METR 20.7 %, 0 bands > 100 %; second_earner_2: max METR 20.0 %, 0 bands > 100 %

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/YeTax/Verify.lean` (imported by the `YeTax` library and built; each guard evaluates `YeTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/YE.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Two legal orders (Sana'a / Aden): record. |
| F2 | confirmed (reading) | Each tax category passes through the art. 62 scale separately: 600,000 of wages + 600,000 of business profit pays 42,000 less than 1,200,000 of wages. G: f2_category_split. S: law/itl17_en.txt:1287-1293 (art. 62: the scale applies to 'the annual proceeds subject to the commercial and industrial profits tax, non-commercial and non-industrial professions tax, salary and wages tax'), :1414-1416 (art. 67: payroll tax monthly at 1/12 of the art. 62 rates). The separate application is the model's reading of art. 62 with arts. 67 and 24 (each tax its own base); an English translation only (F5). |
| F3 | explained | Bonuses at a flat 15 % (art. 66): catalogued, not modelled. |
| F4, F5 | explained | Nominal 2010 amounts; English-only publication: records. |
| F6, F7 | explained | Catalogued. |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| Leads | explained | Rescan: no notch; split gain 66,000 = individual taxation. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: Each income category gets its own exemption and bands | income-type gap | **new**: Nothing found (no PwC page for the country; OpenAlex: general MENA papers, e.g. 'Personal Income Taxes in the Middle East and North Africa: Prospects and Possibilities' (2023), abstract silent on Yemen). | 2026-11-20: OpenAlex specific queries 'Yemen income tax law 17 2010 salaries business profits separate'; 'Yemen personal income tax schedular' (1087 hits, titles checked); OpenAlex broad 'Yemen personal income tax', 'Yemen income tax wages', 'Yemen tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Yemen tax revenue reform' (2490 records, titles only). Record: world/loopholes/africa_mena/search/YE-F2.json |

<!-- L1-VERIFICATION END -->
