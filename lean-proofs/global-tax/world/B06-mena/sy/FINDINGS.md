# Syria (SY) findings, B06-mena (rescue pass 3, 2026-11-20T13:46Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; scale: `scale.json`).

### F1 The 2025 exempt minimum sits above the decree's lowest bands: the first taxed lira pays 11 %
- kind: statute-fault
- LD 30/2023 measures the bands on the whole net monthly income ('بين الحد الأدنى المعفى و/250,000/') and ties the exempt minimum to the public-sector minimum wage (art. 69). The minimum wage reached 279,000 (above the 250,000 top of the 5 % band) and, after Decree 102/2025, 837,000 (above the 7 % and 9 % bands and most of the 11 % one). From July 2025 the printed 5/7/9 % bands tax nobody and the schedule is in effect 11 % from 837,000 to 850,000, 13 % to 1,100,000 and 15 % above. #guard: monthTax 837,000 = 0, 850,000 = 1,500. The Executive Instructions' worked examples (exempt 'ينزل من الشريحة الأولى') confirm that the bands are measured on the whole net income.
- provisions: Law 24/2003 arts. 68-69 as amended by LD 30/2023 arts. 19-20; Executive Instructions on arts. 68-69; Minister's circular (SANA 20 July 2025)
- Lean: SyTax.wageSched, SyTax.monthTax; #guard monthTax exemptH2 850000 = 1500
- status: model result

### F2 The tax-free amount moves with the minimum wage by a minister's circular, published only as news
- kind: gov-error
- Art. 69 (LD 30/2023 art. 20) makes the exempt minimum equal to the public-sector minimum wage, so each pay decree changes the tax without a tax text. In 2025 the new figure (837,000) reached taxpayers through a Minister of Finance circular reported by SANA; the Ministry's site (mof.gov.sy) was 'under construction' and the circular was not found in any official legal publication. The January-June figure (279,000) is the Minister's rounded statement.
- provisions: LD 30/2023 art. 20; Decree 102/2025; SANA 20 July 2025
- Lean: SyTax.exemptH1, SyTax.exemptH2
- status: model result

### F3 One lira over the exempt minimum costs 100 SYP
- kind: fact
- LD 30/2023 art. 17(b) rounds every tax up to the next 100 SYP; applied to the monthly withholding, a salary one lira above the exempt minimum pays 100 SYP (#guard monthTax 837,010 = 100), and up to 99 SYP a month (1,188 a year) more than the exact tax in general. The generic edge scan sees only these rounding falls (largest 99), no notch.
- provisions: LD 30/2023 art. 17(b), art. 19
- Lean: SyTax.round100
- status: model result

### F4 Mid-year tripling of the exempt minimum: the same annual pay is taxed differently by month
- kind: fact
- The salary tax is final and monthly. With the exempt minimum at 279,000 for January-June and 837,000 for July-December, a worker on 1,000,000 a month pays 62,400 a month to June and 11,900 from July (445,800 in the year). Because the July rise came with a 200 % public pay rise, a public employee's 2025 tax depends on when the pay changed; the model assumes 12 equal months.
- provisions: Law 24/2003 arts. 68-69, 72; Decree 102/2025
- Lean: SyTax.overYear, SyTax.exemptOfMonth
- status: model result

### F5 Wages and business profits share one exempt minimum (art. 73), the taxpayer's choice
- kind: fact
- A person with both salary and business profits gets one exempt minimum and may choose the more favourable one (art. 73; the Instructions cite doctors, engineers, lawyers). The model takes the cheaper choice. The 3,000,000 annual business exempt is worth less than three months of the July salary exempt, so the salary exempt is normally the better choice.
- provisions: Law 24/2003 art. 73; LD 30/2023 arts. 4, 8
- Lean: SyTax.personTax
- status: model result

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Statute arithmetic (exempt minimum above the lowest bands), proved by the model's #guards (monthTax 837,000 = 0, 850,000 = 1,500); a design fault, not a household loophole. |
| F2 | explained | Exempt minimum set by circular (gov record). |
| F3 | explained | Rounding up to 100 SYP: a 100-lira step (#guard monthTax 837,010 = 100); rescan edges show only rounding-scale falls (largest 99). |
| F4 | lead | Mid-year change of the exempt minimum: the model assumes 12 equal months; month-specific effects not in the contract. |
| F5 | explained | Choice of one exempt minimum (art. 73): modelled as the cheaper choice. |
| Leads | explained | Rescan: no notch; bands above the top rate (22.4 %) are rounding. |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **SY-R1** Wage tax and the tax on profits (real basis) are separate scales; mixing uses both. Money: 2,373,596 SYP a year on 40,176,000 (4 AW) vs all wages; 557,376 vs all profits. Lean: `world/loopholes/round2/v/lean/R2SY.lean` (R2SY.R1 (4 #guard)); exe check `round2/v/out/SY.json`. Provision: LD 30/2023 and the profits-tax scale (model citation). Status: model-proved. Known/new: unclear: OpenAlex finds a 2025 comparison of Syria's tax on self-employment and on other income (doi 10.32978/sjp.2025.003); its abstract does not describe combining the two scales; Crossref nothing (`round2/v/novelty/`).
<!-- R2-SCANNERS:END -->
