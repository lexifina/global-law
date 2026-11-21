# Lebanon (LB) findings, B06-mena (2026-11-20T05:30Z)

Built from the statute only (no referee values seen). Catalogue built from the statute's own features (no literature search: the session's web-search budget is zero); 'known' = a planning route the statute itself creates and that advisers in any system use; novelty is not claimed.

### F1 Second-earner notch: the wife's first lira costs the husband 225 M of deduction
- kind: loophole-new
- Art. 31 (Law 324/2024 art. 49): when both spouses work each takes the single deduction; the married supplement (225,000,000) disappears. Generic scan: notch of 18,899,999 LBP at a second-earner income of 0 -> 1 (marginal rate 8.4 % on 225 M). The wife's own 450 M is unused at low pay.
- provisions: art. 31 as rewritten 2024
- Lean: LbTax.out
- status: measured

### F2 The MoF's consolidated art. 56 has lost its deduction
- kind: gov-error
- The Ministry's PDF prints art. 56 as 'بعد ان ينزل منها لكل شخص من المكلفين إذا كان حاملا لبطاقة المعوق': the amount (or the reference to art. 31) and the disability supplement are missing (page image checked).
- provisions: art. 56
- Lean: -
- status: recorded

### F3 Brackets multiplied by 60 after the currency collapse
- kind: statute-fault
- The 1999 bands (6 M ... 120 M) became 360 M ... 13.5 B in 2024 (x60); the 2022 budget (Law 10/2022) had already changed them; the 2025 budget (Official Gazette supplement 11, 2025; no text layer, read by OCR) changes only art. 53 (FX conversion at the BdL rate).
- provisions: art. 58
- Lean: LbTax.sched
- status: recorded

### F4 Children deduction capped at five; shared 50/50 when both work
- kind: loophole-known
- Art. 31: at most five children; two earners split the children's deduction equally, which wastes it when one spouse has little income.
- provisions: art. 31
- Lean: LbTax.out
- status: modelled

### F5 Income split between spouses
- kind: loophole-known
- Probe: one earner 2.4 B with two children pays 80.25 M, two earners 1.2 B + 1.2 B pay 42 M.
- provisions: arts. 31, 58
- Lean: probe
- status: measured

### F6 Expense allowances outside the salary base
- kind: loophole-known
- Art. 50 (2): allowances for job, representation, transport and travel expenses are deducted from gross pay: paying part of pay as allowances lowers the base. Catalogued from the statute; not in the canonical household.
- provisions: art. 50 (2)
- Lean: not modelled
- status: catalogued

### F7 Education and family grants within the civil-service limits
- kind: loophole-known
- Art. 50 (4): education, birth, marriage and death grants under a permanent approved scheme are deducted. Catalogued from the statute; not in the canonical household.
- provisions: art. 50 (4)
- Lean: not modelled
- status: catalogued

### Generic scan (scale 1800000000, `results/search/SUMMARY.md`)
- kind: model-fix
- single: max METR 15.0 %, 0 bands > 100 %; couple_1earner_2: max METR 15.0 %, 0 bands > 100 %; couple_2earner_2: max METR 13.4 %, 0 bands > 100 %; second_earner_2: max METR 525.0 %, 1 bands > 100 %, notch 18,899,999 at 0 (0.0 AW)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/LbTax/Verify.lean` (imported by the `LbTax` library and built; each guard evaluates `LbTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/LB.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Second-earner trap: when both spouses work each takes the single deduction and the 225 M married supplement goes. The wife's first lira costs 15,749,999 LBP (18,899,999 with two children) of household net at a husband's 1.8 B. G: f1_second_earner_notch, f1_second_earner_notch_kids. S: law/b24_ocr_1_70.txt:1295-1302 (Budget Law 2024 art. 49 rewriting art. 31: 'في حال كان كل من الزوجين يتعاطى مهنة أو يشغل وظيفة يستفيد كل منهما' ...). |
| F2 | explained | Defective art. 56 in the MoF PDF: source record. |
| F3 | explained | Brackets x 60 in 2024: record. |
| F4 | explained | Five-child cap; equal split of children's deduction (part of F1's second figure). |
| F5 | confirmed | Individual taxation: 1.2 B + 1.2 B pays 38.25 M less than one earner on 2.4 B (two children). G: f5_split. S: as F1 (art. 31) and art. 58 bands. Household-unit effect, known in kind. |
| F6, F7 | explained | Catalogued. |
| Generic scan | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| Leads | explained | Rescan: the only notch is F1 (second earner's first unit, 18,899,999); its bunching gain (18.9 M) is the same notch. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Married supplement (225 M LBP) lost when the wife earns her first lira | second-earner trap | **new**: PwC Lebanon mentions the spouse only for NSSF family allowances; the IMF's 2023 'Lebanon: Technical Assistance Report on Putting Tax Policy Back on Track' came up in the broad search (abstract silent; full text not read); OpenAlex: nothing else. | 2026-11-20: OpenAlex specific queries 'Lebanon income tax family deduction working wife spouse'; 'Lebanon salaries tax family allowance married woman employed' (407 hits, titles checked); OpenAlex broad 'Lebanon personal income tax', 'Lebanon income tax wages', 'Lebanon tax system reform' (75 records, titles and abstracts grepped, 5 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (lebanon, 5 individual pages): 2 passages with the item's terms; Crossref IMF prefix 10.5089 'Lebanon tax system reform' (3546 records, titles only). Record: world/loopholes/africa_mena/search/LB-F1.json |
| F5: Individual taxation: splitting the same income between spouses | household-unit effect | **known**: A generic property of individual taxation with per-person deductions and bands (in kind: LaLumia (2008), 'The effects of joint taxation of married couples on labor supply and non-wage income', J. Public Econ. 92, doi 10.1016/j.jpubeco.2008.01.009); nothing Lebanon-specific found. | 2026-11-20: OpenAlex specific queries 'Lebanon salaries tax individual taxation spouses income splitting' (12 hits, titles checked); OpenAlex broad 'Lebanon personal income tax', 'Lebanon income tax wages', 'Lebanon tax system reform' (75 records, titles and abstracts grepped, 5 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (lebanon, 5 individual pages): 0 passages with the item's terms. Record: world/loopholes/africa_mena/search/LB-F5.json |

<!-- L1-VERIFICATION END -->
