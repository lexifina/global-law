# BH findings (Bahrain (private-sector employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 No text read states that Bahrain has no personal income tax
- kind: model-fix (evidence)
- provisions: -
- The model returns no income tax because no Bahraini act levies one; the LLOC classification of financial legislation was not searched exhaustively. Cited as absence, which the contract asks to avoid: tier B.
- status: recorded (build phase)

### F2 Social Insurance Law: 'any nationality' versus phased application
- kind: statute-fault (ambiguity)
- provisions: DL 24/1976 art. 1, 2
- Art. 2 applies the law compulsorily to all workers regardless of nationality, while art. 1 applies the branches in phases by Council of Ministers decisions. Whether expatriates pay the 7 % old-age share is decided outside the act. The model charges expatriates only the 1 % unemployment contribution and flags the rest.
- status: recorded (build phase)

### F3 A minimum contribution wage from 2026 for new registrants
- kind: known (future)
- provisions: DL 44/2026 art. 1-2
- Decree-Law 44/2026 adds art. 19 bis (a minimum wage base set by the Council of Ministers) for persons first registered after it: not relevant to 2025.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 9.2 % | 0.02 | 0 |  | 0 |`
- timing, single: `| single|none | 1,920 (8.00 % AW) | 48,000 | 72,000 / 24,000 | 32.7 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Absence of a PIT: evidence record. |
| F2 | lead | Expatriates' 7 % old-age share decided outside the act: reading. |
| F3 | explained | 2026 minimum base: future. |
| Generic scanners | explained | Rescan timing gain 1,920 = contribution ceiling. |

<!-- L1-VERIFICATION END -->
