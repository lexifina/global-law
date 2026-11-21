# Libya (LY) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 Authority: one law for a divided state
- kind: statute-fault
- Law 7/2010 predates the 2014 division; the source is the Tripoli Tax Authority's compilation (2016). Both administrations apply Law 7/2010; no later amendment of the modelled articles was found, but none could be excluded (access B).
- provisions: -
- Lean: -
- status: recorded

### F2 Jihad tax notches: whole-income rates at 50 and 100 a month
- kind: loophole-new
- Law 44/1970 art. 2: 1 % up to 50 a month, 2 % 'من كامل الدخل' above 50, 3 % above 100: passing 100 a month costs 1 % of the whole income (scan: METR 50 % at 0.1 AW, notch 11 at 1,211 a year). The amounts are 1970 pounds, so today every salary pays 3 %: a nominal relic.
- provisions: Law 44/1970 art. 2
- Lean: LyTax.jihad, #guard
- status: proved

### F3 Exemption amounts unchanged since 2010
- kind: statute-fault
- 1,800 / 2,400 + 300 per child (art. 36) are 2010 amounts; the 10 % band starts at 12,000 + exemption.
- provisions: art. 36, 58
- Lean: -
- status: recorded

### F4 Libyans' contribution in public companies struck down
- kind: gov-error
- The encyclopaedia keeps Law 1/1986 art. 8 (1.5 % of pay) but also prints the Tax Authority's circular stopping it after the Supreme Court found art. 8 unconstitutional: not modelled.
- provisions: Law 1/1986 art. 8
- Lean: -
- status: recorded

### F5 Bank interest 5 % vs work income up to 10 %
- kind: loophole-known
- Arts. 61-62 tax deposit interest at 5 %.
- provisions: arts. 61-62
- Lean: LyTax.out
- status: modelled

### F6 Insurance premiums deducted from the base
- kind: loophole-known
- Art. 36: life insurance for the spouse and dependants, general insurance (fire, theft) and health insurance premiums are exempt from the work-income tax base. Catalogued from the statute; not in the canonical household.
- provisions: art. 36
- Lean: not modelled
- status: catalogued

### F7 End-of-service pay and cashed leave outside the tax
- kind: loophole-known
- Art. 55: severance and the cash value of accumulated leave are not taxed: deferring pay into them avoids the 10 % band. Catalogued from the statute; not in the canonical household.
- provisions: art. 55
- Lean: not modelled
- status: catalogued

### Generic scan (scale 12000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 50.0 %, 0 bands > 100 %, notch 11.00 at 1,211 (0.10092 AW); couple_1earner_2: max METR 50.0 %, 0 bands > 100 %, notch 11.00 at 1,211 (0.10092 AW); couple_2earner_2: max METR 50.0 %, 0 bands > 100 %, notch 11.00 at 2,019 (0.16825 AW); second_earner_2: max METR 50.0 %, 0 bands > 100 %, notch 11.00 at 1,211 (0.10092 AW)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/LyTax/Verify.lean` (imported by the `LyTax` library and built; each guard evaluates `LyTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/LY.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Authority record (Law 7/2010 applied by both administrations). |
| F2 | confirmed | Jihad tax steps on the whole income: one dinar above 1,211 a year (100 a month) costs 11 of net. A 1970 relic: every 2025 wage pays 3 %. G: f2_jihad_notch; T: LyTax jihad #guard. S: law/ocr_100_112.txt:174-178 (Law 44/1970 art. 2: 1 % 'إذا لم يجاوز الدخل خمسين جنيها شهريا', 2 % 'من كامل الدخل إذا زاد على خمسين', 3 % 'من كامل الدخل إذا زاد على مائة جنيه شهرياً'). |
| F3 | explained | Amounts unchanged since 2010: record. |
| F4 | explained | Struck-down contribution not modelled: record. |
| F5 | explained | Interest at 5 % (arts. 61-62) vs work income to 10 %: rescan interest wedge +11.1 % at 5 'AW'; a schedular difference, small; not searched further. |
| F6, F7 | explained | Catalogued. |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| Leads | explained | Rescan bands 'above the top rate' (25-37.5 % max, 17.4 % average) are unit rounding of workIncomeTax on the 0.002-AW grid: the true marginal rate is a constant 17.4 % (10 % x 0.9625 + 3 % + 4.75 %), not a phase-out. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: Jihad tax: 1 / 2 / 3 % of the whole income at 50 and 100 a month (1970 amounts) | cliff or notch | **new**: Nothing found (PwC Libya: no jihad tax; OpenAlex: no tax paper on it). No practical money at 2025 wages: a relic. | 2026-11-20: OpenAlex specific queries 'Libya jihad tax wages'; 'Libya income tax law 7 of 2010 personal income' (7854 hits, titles checked); OpenAlex broad 'Libya personal income tax', 'Libya income tax wages', 'Libya tax system reform' (75 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (libya, 5 individual pages): 0 passages with the item's terms; Crossref IMF prefix 10.5089 'Libya tax revenue' (1340 records, titles only). Record: world/loopholes/africa_mena/search/LY-F2.json |

<!-- L1-VERIFICATION END -->
