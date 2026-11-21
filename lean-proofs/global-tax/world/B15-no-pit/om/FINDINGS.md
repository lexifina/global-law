# OM findings (Oman (Omani employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 Oman's personal income tax starts in 2028, not 2025
- kind: registry fix
- provisions: RD 56/2025 art. 4
- RD 56/2025 (22 June 2025) promulgates the Individuals' Income Tax Law and art. 4 of the decree puts it in force on 1 January 2028; 2025 wages bear no income tax.
- status: recorded (build phase)

### F2 Capped pension, uncapped job security
- kind: loophole-known
- provisions: SPL art. 52, 70, 116
- The old-age share (7.5 %) stops at OMR 3,000 a month (art. 52); the 0.5 % job-security share is on the whole wage (art. 52 last paragraph). Above the cap the marginal employee rate is 0.5 %. Lean `marginal_above_ceiling`.
- status: recorded (build phase)

### F3 The commencement article was amended in 2025
- kind: known
- provisions: RD 52/2023 art. 6 as amended
- RD 60/2025 replaced the decree's art. 6: injury insurance for non-Omanis after five years, the maternity chapter after three, the expatriate savings scheme within four years; the Omani old-age and job-security shares apply from 1 January 2024.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 8.9 % | 0.01 | 0 |  | 0 |`
- timing, single: `| single|none | 1,350 (7.50 % AW) | 36,000 | 54,000 / 18,000 | 32.7 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

## Round W5 review (W5 fix agent, 2026-11-20)

### W5-1 afnad-om-payroll's SPF_EMP: no wage ceiling, no job security (software error) and a partial-line mapping (test)
- kind: software-error / test-note
- Social Protection Law (RD 52/2023) art. 52: old-age, disability and death contributions on the wage up to "(٣٠٠٠) ثلاثة
  آلاف ريال عماني شهريا"; art. 116 (2): job security 0.5 % of the wage. The module charges 7.5 % of the whole wage and no
  job security; the grid compared that partial line with the model's total (request: compare detail.oldAgeDisabilityDeath).

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | PIT from 2028: registry fix. |
| F2 | explained | Capped pension, uncapped job security: known design (T: marginal_above_ceiling); rescan timing gain 1,350 = the cap. |
| F3 | explained | Commencement amended: record. |
| Generic scanners, W5-1 | explained | As F2. |

<!-- L1-VERIFICATION END -->
