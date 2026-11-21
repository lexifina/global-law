# SA findings (Saudi Arabia (Saudi employee, 1421 H Social Insurance Law), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 The SANED rate is not in any law
- kind: statute-fault (delegation)
- provisions: Unemployment Insurance Law art. 7
- Since Royal Decree M/160 (1441 H) art. 7 only bounds the unemployment insurance rate (0.5 %-2 %, half each) and leaves it to a CEDA decision, which is not published with the law. The model leaves it out and flags every Saudi wage earner.
- status: recorded (build phase)

### F2 Wage employment is not 'activity'
- kind: known
- provisions: Income Tax Law art. 1, 2
- Income Tax Law art. 1 defines activity as trade, profession or craft for profit (including the use of property); art. 2 taxes resident non-Saudi natural persons only on activity. Saudi citizens are not persons subject to income tax at all.
- status: recorded (build phase)

### F3 The official publisher refuses connections
- kind: access
- provisions: -
- laws.boe.gov.sa refused both hosts; the Internet Archive copies (the route Global law uses) were found by listing 585 archived law pages (Wayback CDX) and reading their titles.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 9.0 % | 0.005 | 0 |  | 0 |`
- timing, single: `| single|none | 24,300 (9.00 % AW) | 540,000 | 810,000 / 270,000 | 32.7 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Unemployment Insurance Law art. 7 as amended by M/160 (rate by CEDA decision, 0.5-2 %); rate in force from GOSI SANED guide (PDF 5 June 2023), official secondary
- SANED employee share 0.75 % on the SIL contribution wage (cap 45,000 / month). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1, F2, F3, W5A-1 | explained | SANED rate delegated outside the law; wage employment not an 'activity'; publisher refuses connections; GOSI contribution added: records (no PIT on wages). |
| Generic scanners | explained | Rescan timing gain 26,325 = the 45,000-a-month contribution ceiling. |

<!-- L1-VERIFICATION END -->
