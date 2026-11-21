# QA findings (Qatar (Qatari employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 Wages are outside the Income Tax Law by its issuing law
- kind: known
- provisions: Law 24/2018 issuing art. 2; art. 3, 4
- Law 24/2018 issuing art. 2: the Income Tax Law does not apply to 'الرواتب والأجور والبدلات وما في حكمها'; art. 4(12) further exempts all income of resident Qatari natural persons. A non-Qatari's rent from Qatari real estate remains State-source income (art. 3(3)).
- status: recorded (build phase)

### F2 Grandfathered ceiling
- kind: known
- provisions: Law 1/2022 art. 13
- Art. 13: an insured whose contribution salary exceeded QAR 100,000 before the law may keep contributing on it (not modelled).
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 7.0 % | 0.0 | 0 |  | 0 |`
- timing, single: `| single|none | 42,000 (7.00 % AW) | 1,200,000 | 1,800,000 / 600,000 | 32.7 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1, F2 | explained | Wages outside the Income Tax Law; grandfathered ceiling: records. |
| Generic scanners | explained | Rescan timing gain 42,000 = contribution ceiling. |

<!-- L1-VERIFICATION END -->
