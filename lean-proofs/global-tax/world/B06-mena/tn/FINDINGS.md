# Tunisia (TN) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 CSS notch: 24-25 dinars at a net income of 5,000
- kind: loophole-new
- The contribution sociale de solidarité (LF 2018 art. 53, LF 2023 art. 22) adds half a point to every band, the 0 % band included, i.e. 0.5 % of the whole income, but exempts wage/pension-only earners whose net income after family deductions is at most 5,000. One dinar more costs 25 (Lean #guard css 5000 = 0, css 5001 = 25); generic scan: notch of 24 at a wage of 5,555 (single), 6,111 (couple, family deductions), 10,185 (two earners).
- provisions: LF 2018 art. 53; LF 2023 art. 22 (via NC 1/2026); Code IRPP art. 44
- Lean: TnTax.css, #guard
- status: proved

### F2 Global law's Tunisian code is the pre-2025 barème
- kind: gov-error
- tunisia/national/acts/code/code-irpp-is/art-0044.md (legislation-securite.tn copy, 'in force 2020-03-31') prints 0/26/28/32/35 %; the DGI's July 2025 code and LF 2025 art. 36 give eight bands 0-40 %. A record-staleness issue for the corpus (reported here, not filed).
- provisions: Code IRPP art. 44
- Lean: -
- status: recorded

### F3 Professional expenses capped at 2,000: marginal rate rises at 20,000 of salary
- kind: loophole-known
- Art. 26 I: 10 % of salary up to 2,000, so above a salary of 20,000 the deduction stops growing; probe: 20,000 -> 22,000 costs 510 (25.5 %).
- provisions: art. 26 I
- Lean: TnTax.netSalary
- status: measured

### F4 Family deductions belong to the chef de famille only
- kind: loophole-known
- Art. 5 makes the husband chef de famille (the wife only if he has no income); art. 40 gives 300 + 100 per child (first four) to him. Spouses are taxed separately, so a couple's best split is to put investment income (rents) on the lower earner: generic splitting scan gain up to 6,159 (30.8 % AW) at 4 AW.
- provisions: arts. 5, 40
- Lean: TnTax.out
- status: measured

### F5 Temporary CSS rate for 2023-2025, renewed for 2026
- kind: statute-fault
- LF 2023 art. 22 set half a point 'à titre conjoncturel' for 2023-2025 and LF 2026 art. 87 renews it for 2026 (NC 1/2026): a temporary rate renewed year by year rather than written into art. 53.
- provisions: LF 2018 art. 53; LF 2023 art. 22; LF 2026 art. 87
- Lean: -
- status: recorded

### F6 Share-savings accounts deductible up to 50,000
- kind: loophole-known
- Art. 39 VIII: deposits in comptes épargne en actions are deductible within 50,000 a year if kept five years. Catalogued from the statute; not in the canonical household.
- provisions: art. 39 VIII
- Lean: not modelled
- status: catalogued

### F7 Life-insurance premiums and housing-loan interest deductible
- kind: loophole-known
- Art. 39 I (2) premiums up to 10,000 a year; (4) interest on the loan for a single home costing at most 200,000. Catalogued from the statute; not in the canonical household.
- provisions: art. 39 I
- Lean: not modelled
- status: catalogued

### Generic scan (scale 20000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 62.5 %, 0 bands > 100 %, notch 24.00 at 5,555 (0.27775 AW); couple_1earner_2: max METR 65.0 %, 0 bands > 100 %, notch 24.00 at 6,111 (0.30555 AW); couple_2earner_2: max METR 75.0 %, 0 bands > 100 %, notch 24.00 at 10,185 (0.50925 AW); second_earner_2: max METR 62.5 %, 0 bands > 100 %, notch 24.00 at 5,555 (0.27775 AW)

## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 OpenFisca-Tunisia agrees once marital status is entered (case-building error)
- kind: test-note
- CGI art. 40 I: "le chef de famille tel que défini à l'article 5 du présent code a droit à une déduction de 300
  dinars"; art. 5: "l'époux; le divorcé qui a la garde des enfants; le veuf; l'adoptant". The package implements this
  (`chef_de_famille`), but `statut_marital` defaults to célibataire and the grid never set it, so the 300 dinars were
  missing for every husband and single parent (gaps of 300 x the marginal rate: 75 / 90 / 120). With it set, the model
  and the package agree to the dinar (millimes aside). The model's reading that a single adult with children is
  divorced with custody or widowed (art. 5) is an assumption about a fact the contract does not carry; a never-married
  parent is not chef de famille.
- provisions: CGI arts. 5, 40
- Lean: TnTax.familyDeduction (unchanged)
- status: reported to the test agent (software/ISSUES.md, W2)

### W5S-1 payroll_africa (Tunisia): CSS as 0.5 % of gross (W5 review pass 2, 2026-11-20)
- kind: software-error
- `tn_open_payroll_africa_grid` surtaxes: the app's contribution sociale de solidarité is 0.5 % of gross (calculators/tunisia.py); LF 2018 (loi 2017-66) art. 53 and LF 2023 art. 22 make it the difference between the tax on the barème raised by half a point and the tax on the barème, on the net taxable income, with wage-only income up to 5,000 exempt (TnTax.css).
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS page for non-agricultural employers, contributions tab (cnss.tn, fetched 2026-11-20): 25,75 % = 16,57 % employer + 9,18 % employee, base all remuneration (loi 60-30 arts. 40-47, 105); official secondary (décrets not reached); Code IRPP art. 26 I
- CNSS employee 9,18 % of all remuneration, deducted under Code IRPP art. 26 I before the 10 % frais. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNSS 9,18 % from the CNSS page (official secondary; the décrets under loi 60-30 not reached). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/TnTax/Verify.lean` (imported by the `TnTax` library and built; each guard evaluates `TnTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/TN.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (location moved by W5) | The CSS exemption ends at 5,000 of net income: one dinar more costs 24 of net. With the W5 CNSS 9.18 % deducted first, the single wage at the notch is 6,117 (was 5,555); rescan notches at 6,116 (single), 6,728 (single parent), 11,214 / 15,291 (two earners). G: f1_css_notch. S: law/nc.nfkc.txt:72-75 (Note commune 1/2026: exempt are persons with only wages/pensions 'والذين لا يتجاوز دخلهم السنوي الصافي 5.000 دينار بعد طرح التخفيضات بعنوان الحالة والأعباء العائلية'). |
| F2 | explained | Global law's art. 44 copy is the pre-2025 barème: source record. |
| F3 | explained (location moved) | The 10 % frais cap of 2,000 (art. 26 I; law/code2025fr.txt:894) is now reached at a gross wage of about 22,022 (after CNSS): a capped deduction, not a loophole. |
| F4 | explained | Chef de famille (art. 5; law/code2025fr.txt:94) takes the family deductions; split gains up to 5,645 (rescan) are individual taxation. |
| F5 | explained | Temporary CSS rate renewed yearly: legislative record. |
| F6, F7 | explained | Catalogued reliefs (not modelled). |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| W2-1, W5S-1, W5A-1 | explained (record of model/test work, not a loophole; kept as written) | CNSS 9.18 % present (1,836 at 20,000). |
| Leads | explained | All rescan notches are F1's CSS edge; bands above the top rate (80-82.5 %) are the same edge on the 0.002-AW grid. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: CSS exemption for wage/pension-only incomes up to 5,000 TND of net income ends all at once | cliff or notch | **new**: PwC Tunisia prints the exemption ('annual net income does not exceed TND 5,000 are exempted from the said SSC') and a '0/0.5*' first band, not the cliff; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Tunisia contribution sociale de solidarité income tax exemption 5000 dinars'; 'Tunisie contribution sociale de solidarité IRPP 5000 dinars seuil' (4 hits, titles checked); OpenAlex broad 'Tunisia personal income tax', 'Tunisia income tax wages', 'Tunisia tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (tunisia, 5 individual pages): 7 passages with the item's terms; Crossref IMF prefix 10.5089 'Tunisia personal income tax reform' (3479 records, titles only). Record: world/loopholes/africa_mena/search/TN-F1.json |

<!-- L1-VERIFICATION END -->
