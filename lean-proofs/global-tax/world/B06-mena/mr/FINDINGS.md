# Mauritania (MR) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 The DGI's CGI 2024 PDF is truncated on the server
- kind: gov-error
- impots.gov.mr/DGI/files/CGI - RIM - FR - 2024.pdf (and the AR file, same length) is served as 261,908,483 bytes with no trailer or %%EOF: no PDF reader opens it; the Wayback copy breaks at 79.5 MB. The 2023 edition is the last readable consolidation.
- provisions: -
- Lean: -
- status: recorded (draft note to DGI, not filed)

### F2 Monthly final withholding: uneven pay costs double
- kind: loophole-new
- Arts. 112-115 make each payment the taxable event and give no annual reconciliation: 180,000 paid as 6 months of 30,000 costs 33,300, as 12 months of 15,000 16,200 (Lean #guard). Bonuses and 13th months are taxed at the month's marginal rate.
- provisions: arts. 112, 114
- Lean: MrTax #guard
- status: proved

### F3 Art. 114 prints the tariff as formulas; they equal the bands
- kind: model-fix
- The subtraction constants 900 and 4,050 are exactly the band differences: checked at 400 points by #guard.
- provisions: art. 114 2)
- Lean: #guard
- status: proved

### F4 The 6,000 monthly exemption and allowances up to 1,000 a month
- kind: loophole-known
- Art. 110 1) b), c): pay split into professional allowances (up to 1,000 a month) is exempt; benefits in kind count at 40 % (art. 113 1) b)) and are exempt up to 20 % of pay (art. 110 4)): paying in kind lowers the base.
- provisions: arts. 110, 113
- Lean: -
- status: catalogued

### F5 Press and airline staff capped at 20 %
- kind: loophole-known
- Art. 114 6) caps the barème at 20 % for staff of press organisations, airlines and air-navigation agencies.
- provisions: art. 114 6)
- Lean: not modelled
- status: catalogued

### Generic scan (scale 108000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 44.4 %, 0 bands > 100 %; couple_1earner_2: max METR 44.4 %, 0 bands > 100 %; couple_2earner_2: max METR 37.0 %, 0 bands > 100 %; second_earner_2: max METR 44.4 %, 0 bands > 100 %

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: CNSS page "Recouvrement des cotisations" (cnss.mr, Internet Archive capture 2021-08-12; same text on the 2016 page): plafond 70 000 UM a month, 14 % = 1 % worker + 13 % employer; official secondary; old-to-new ouguiya at 10:1 (reading)
- CNSS worker 1 % of pay up to 7 000 MRU a month (70 000 old UM), deducted (CGI art. 113 2) a)). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNAM health-insurance employee contribution not reached; CNSS ceiling printed in old ouguiya (revision after 2016 not found). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/MrTax/Verify.lean` (imported by the `MrTax` library and built; each guard evaluates `MrTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/MR.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Truncated official PDF: source record. |
| F2 | confirmed | Final monthly withholding: 180,000 as 6 x 30,000 bears 33,300, as 12 x 15,000 16,200 (the barème; with the W5 CNSS deduction the even case is 16,068). G: f2_uneven_pay (also the model's own #guard). S: law/cgi2023fr.txt:2180-2190 (art. 114 2): the monthly formulas 'I = R.I. x 0,15 / (R.I. x 0.25) - 900 / (R.I. x 0.40) - 4.050', base 'arrondie à la dizaine d'Ouguiya inférieure'). |
| F3 | explained | Formula tariff = band tariff (model #guard on 400 points). |
| F4, F5 | explained | Catalogued (allowances, benefits in kind, 20 % cap for press/airline staff). |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | CNSS 1 % present (840 at 180,000). |
| Leads | explained | Rescan bands 'above the top rate' (44.4 % max, 40.0 % average from 324,864) are the art. 114 3) rounding of the base to 10; the monthly-bonus effect (F2) is invisible to the annual timing scan. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: Final monthly withholding without reconciliation: uneven pay is taxed more | timing or bunching | **new**: PwC Mauritania describes monthly withholding, not its finality or the cost of uneven pay; OpenAlex: nothing on Mauritania. The mechanism is general to non-cumulative final withholding (GN, DJ, RW, ET). | 2026-11-20: OpenAlex specific queries 'Mauritania tax on salaries monthly withholding bonus'; 'Mauritanie impôt sur les traitements et salaires retenue mensuelle' (69 hits, titles checked); OpenAlex broad 'Mauritania personal income tax', 'Mauritania income tax wages', 'Mauritania tax system reform' (75 records, titles and abstracts grepped, 2 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (mauritania, 5 individual pages): 6 passages with the item's terms; Crossref IMF prefix 10.5089 'Mauritania tax policy' (8324 records, titles only). Record: world/loopholes/africa_mena/search/MR-F2.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.69 AW (contribution rate 1.1 -> 0.0 %, combined marginal 6 -> 16 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
