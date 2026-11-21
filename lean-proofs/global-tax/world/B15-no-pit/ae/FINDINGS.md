# AE findings (United Arab Emirates (federal; GPSSA private sector), 2025)

Generated 2026-11-20 02:07 UTC by tools/gen_docs_b15.py from the batch agent's notes; sources in `law/`, model in `lean/`.

### F1 The ILOE premium doubles at a basic salary of AED 16,000 a month
- kind: loophole-new (notch)
- provisions: FDL 13/2022 art. 4; Cabinet Resolution 97/2022 (not read)
- Premium AED 5 a month up to a basic salary of 16,000 and AED 10 above (official secondary, FDL 13/2022 art. 4). One dirham more of basic salary costs AED 60 a year. Lean `iloe_notch`. Small, but a notch that a basic/allowance split can avoid: the premium follows the basic salary only.
- status: recorded (build phase)

### F2 Two pension laws for the same job: 5 % or 11 %
- kind: statute-fault (horizontal)
- provisions: FDL 57/2023 art. 2, 4, 5; FL 7/1999 art. 1, 2
- An Emirati who started work before 31 October 2023 pays 5 % on a salary up to 50,000 a month (FL 7/1999 art. 2); one who starts after pays 11 % up to 70,000 (FDL 57/2023 art. 2(1), 4, 5). At 30,000 a month the gap is AED 21,600 a year (input field `aePensionLaw`). Lean `pension2023_at_cap`, `pension1999_at_cap`.
- status: recorded (build phase)

### F3 Minimum contribution salary of 3,000 a month
- kind: loophole-new (floor)
- provisions: FDL 57/2023 art. 5(2)
- FDL 57/2023 art. 5(2): the contribution salary is 'not less than Dh3,000'. A part-time Emirati earning 1,000 a month pays 330 a month (33 % of pay). Lean `pension2023_floor`.
- status: recorded (build phase)

### F4 No federal text says that wages are untaxed
- kind: model-fix (evidence)
- provisions: FDL 47/2022 art. 11-12
- The absence of an income tax on wages rests on the Corporate Tax law's scope (natural persons only for Business) plus the FTA's published reading; the Cabinet decision listing natural persons' taxable business (Cabinet Decision 49/2023) was not reached (uaelegislation.gov.ae refuses scripts).
- status: recorded (build phase)

### Generic scanners (tools/scan_b15.py, statutory reference wage; results/search/SUMMARY.md)
- kind: scanner leads
- METR, single: `| single|none | 191.4 % | 0.0 | 1 | 4,019 at 0 (0.0 AW) | 0 |`
- timing, single: `| single|none | 46,200 (11.00 % AW) | 840,000 | 1,260,000 / 420,000 | 33.0 % |`
- reading: a notch listed is the floor or threshold named in the findings above, re-found without being told; a timing gain comes from a contribution ceiling (bunching pay above a cap in one year) or from that notch; no other lead.

### W5S4-1 Uplift demo (Uplift-HQ): the 2023 decree-law's 70,000 ceiling with the 1999 law's 5 %; Xenna: no 1,000 floor (W5 review pass 4, 2026-11-20)
- kind: software-error
- `ae_open_uplift_demo_upliftq_grid` / `_gpssa_grid`: Federal Law 7/1999 art. 1 (private sector: contribution salary Dh1,000-50,000 a month) with art. 2's 5 %; the tool caps at 70,000 (Decree-Law 57/2023's maximum, whose employee rate is 11 %): dev -12,000 a year above 50,000 a month. `ae_open_xenna_corto735_gpssa_grid`: no Dh1,000 minimum (art. 1): model above at very low wages (22 dev cases).
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/AeTax/Verify.lean` (imported by the `AeTax` library and built; each guard evaluates `AeTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/AE.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | ILOE premium AED 5 -> 10 a month above a basic salary of 16,000: AED 12 more a year costs AED 61 of contributions (60 of premium). Small; avoidable by a basic/allowance split. G: f1_iloe_doubling; T: iloe_notch. S: law/iloe_home.txt:56-62 ('Basic Salary 16,000 AED or below' / 'Above 16,000 AED'; official secondary, FDL 13/2022 art. 4). |
| F2 | explained | Two pension laws by start date (FL 7/1999 vs FDL 57/2023): horizontal statute fault (input aePensionLaw). |
| F3 | confirmed | Minimum contribution salary of 3,000 a month: an Emirati paid 1,000 a month (12,000 a year) pays 4,020 a year (33.5 % of pay). G: f3_pension_floor; T: pension2023_floor. S: law/fdl57-2023_en.txt:243 ('salary is not less than Dh3,000 (three thousand dirhams) with a maximum of Dh70,000'). |
| F4 | explained | No federal text exempting wages: evidence record. |
| Generic scanners, W5S4-1 | explained | Rescan: first-unit notch 4,019 = F3 (+ ILOE); timing gain 46,200 = the 70,000 contribution ceiling. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: ILOE premium doubles at a basic salary of AED 16,000 a month | cliff or notch | **known**: PwC UAE (Other taxes): the ILOE scheme 'divides subscribers into two categories: (i) those who earn AED 16,000 or less as basic salary per month and (ii) those who earn more'. | 2026-11-20: OpenAlex queries 'UAE involuntary loss of employment insurance premium basic salary 16,000' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (united-arab-emirates, 5 individual pages): 5 passages with the item's terms. Record: world/loopholes/africa_mena/search/AE-F1.json |
| F3: Minimum contribution salary AED 3,000 a month for Emirati pension members | cliff or notch | **new**: PwC UAE describes GPSSA contributions but not the AED 3,000 minimum contribution salary's cost to part-time workers; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'UAE federal decree-law 57 2023 pension contribution minimum salary 3,000' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (united-arab-emirates, 5 individual pages): 1 passages with the item's terms. Record: world/loopholes/africa_mena/search/AE-F3.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: floor: contribution rate 19 % at 0.05 AW vs 11 % at 0.5 AW. Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
