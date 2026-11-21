# KW findings (Kuwait (Kuwaiti private-sector employee), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 Five stacked contributions: 10.5 % to 1,500 a month, 5.5 % to 2,750, then nothing
- kind: loophole-known (regressive cap)
- provisions: SIL art. 2, 11; Law 25/2001; Law 110/2014; DL 128/1992; DL 101/2013
- Basic 5 %, increase fund 2.5 %, end-of-contribution reward 2.5 % and unemployment 0.5 % on the salary up to KWD 1,500 a month; supplementary 5 % and unemployment 0.5 % on the next 1,250; none above 2,750. Lean `rate_below_ceiling`, `marginal_supplementary`, `flat_above`.
- status: recorded (build phase)

### F2 Two supplementary ceilings
- kind: statute-fault (inconsistency)
- provisions: DL 128/1992 art. 1(3) notes
- Decision 1/2005 sets the compulsory supplementary maximum at 1,250; decision 6/2019 raised it to 1,500 for optional contributors only (guide note to DL 128/1992 art. 1). Compulsory and voluntary members face different caps.
- status: recorded (build phase)

### F3 Law 25/2001's table of yearly rates
- kind: model-fix (reading)
- provisions: Law 25/2001 art. 8 and table
- The increase-fund table phases the insured's share in over ten years from 2001 (none, 1 %, 2 %, 2.5 % from the tenth year onward); the column order was read from the table header in the guide's PDF text.
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 13.3 % | 0.055 | 0 |  | 0 |`
- timing, single: `| single|none | 1,140 (6.33 % AW) | 32,940 | 50,940 / 14,940 | 45.7 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

### W5S4-1 GulfCalc (Sheharyar-ans): a flat 10.5 % up to KWD 3,000 a month (W5 review pass 4, 2026-11-20)
- kind: software-error
- `kw_open_gulfcalc_sheharyar_grid`: SIL art. 2 (maximum salary 1,500, Law 9/2011) and art. 11 (5 %), Law 110/2014 arts. 3-4 (2.5 %, maximum salary 1,500), Law 25/2001 art. 8 (2.5 %), DL 128/1992 art. 1(3), 4(a) (5 % on the next 1,250) and DL 101/2013 art. 3 (0.5 %): 10.5 % to 1,500 and 5.5 % on 1,500-2,750, nothing above (F1; PIFSS 2021 consolidation, later decisions not checked: reading). Dev: model below by 1,065 a year at and above 3,000 a month (tool 3,780 vs 2,715); the -1..-3 below 1,500 a month are the model's whole-KWD rounding per component.
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Contribution caps (1,500 / 2,750 a month) make the employee's rate regressive: known design (T: rate_below_ceiling, flat_above); rescan timing gain 1,140 = the caps. |
| F2 | explained | Two supplementary ceilings: statute fault. |
| F3 | explained | Phased rates: reading. |
| Generic scanners, W5S4-1 | explained | As F1. |

<!-- L1-VERIFICATION END -->

### D9S-1 ISSA contribution-rate table (Wayback 2025-10-24), Kuwait 'Insured person' total 8 %: omits a 2.5 % component (D9 review, 2026-11-20)
- Referee: `world_kw_issa_contribution_rates_2025` (ISSA 'Contribution rates' table, information date January 2024):
  insured person old age, invalidity and survivors 7.5 %, unemployment 0.5 %, total 8 %; the converter applied 8 % to
  five wages at or below KWD 1,500 a month (conversion checked: correct for the table as printed).
- The statute as consolidated by PIFSS (legislative guide, book 1, 16-9-2021; `law/pifss_book1_2021.pdf`) charges a
  Kuwaiti employee below the basic ceiling 10.5 %: SIL (DL 61/1976) art. 11, 5 %; Law 25/2001 art. 8 and its table
  (pension-increase fund: insured 2.5 % "العاشرة وما بعدها", the tenth year from 2001-07-01 onwards, so 2025);
  Law 110/2014 arts. 3-4 (end-of-contribution reward, 2.5 %, salary up to 1,500); DL 101/2013 art. 3 (unemployment
  0.5 %). ISSA's 7.5 % for old age covers 5 % and one of the two 2.5 % components; which one could not be read (the ISSA
  Kuwait profile text was not reached: the Internet Archive was offline during the review).
- Dev: model / referee = 1.3125 = 10.5 / 8 on all 5 cases. Category S (referee omits a statutory component, reading),
  recorded; no change to the model.
- provisions: DL 61/1976 arts. 2, 11 (Law 9/2011); Law 25/2001 art. 8 and table; Law 110/2014 arts. 3-4; DL 101/2013 art. 3
