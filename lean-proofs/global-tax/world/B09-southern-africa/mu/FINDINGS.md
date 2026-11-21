# Mauritius (MU): findings, B09 build phase (2026-11-20T06:18Z)

Mauritius built from the ITA 1995 and FA 2025: 0/10/20 % with dependant deductions and a 15 % Fair Share Contribution above Rs 12 m; the CSG switches from 1.5 % to 3 % of the whole wage above Rs 50 000 a month (+Rs 9 001 a year for Rs 12 more), and a spouse earning one rupee above Rs 110 000 costs the family Rs 22 000.

Scale for scanner numbers: 1,000,000 MUR = threshold of the top (20 %) band (Income Tax Act 1995 First Schedule Part I as replaced by Finance (Miscellaneous Provisions) Act 2025 s. 26 (y)); a statutory threshold, not an average wage.

### F1 CSG rate applies to the whole wage once Rs 50 000 a month is passed
- kind: loophole-known
- SCSBA 2021 s. 4 (1) (a)-(b), First Schedule Part II 'Rs 50,000': 1.5 % of remuneration up to it, 3 % of the whole remuneration above. Rs 600 000 vs Rs 600 012 a year: contributions +9 001. Scanner (scale Rs 1 m): peak METR 192.9 % at 0.6 x scale; notch 8 999 at 600 011.
- provisions: SCSBA s. 4 (1)
- Lean: MuTax.csgMonthly (#guard)
- status: recreated by scanner

### F2 All-or-nothing dependant test for a spouse
- kind: loophole-known
- ITA s. 27 (5) (a): no deduction for a first dependant whose net and exempt income 'exceeds 110,000 rupees'. Couple: Rs 2 m + Rs 110 000 vs Rs 2 m + Rs 110 001: family taxes +22 000. Scanner (second earner): METR 171 % from 110 000 to 115 000.
- provisions: ITA s. 27 (5), Third Schedule
- Lean: MuTax.out
- status: recreated by scanner

### F3 Fair Share Contribution: threshold on net income, levy on chargeable income
- kind: fact
- s. 16C: liability arises when net income + resident dividends exceed Rs 12 m; the 15 % is charged on chargeable income + dividends above Rs 12 m, so with deductions the levy can be nil although the threshold is crossed (no notch). Top combined rate 35 % in 2025-26.
- provisions: ITA s. 16B, 16C
- Lean: MuTax.fsc
- status: modelled

### F4 FA 2026 already printed in the consolidation
- kind: fact
- The MRA consolidation shows the FA 2026 Part I (0/10/20/35 %, from 1 July 2026); the 2025-26 rates come from endnote 1052 and FA 2025 s. 26 (y). Readers of the consolidated text in late 2026 see next year's rates.
- provisions: First Schedule, endnote 1052
- Lean: MuTax.sched
- status: noted

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- CSG 1.5 %/3 % whole-wage switch: recreated
- dependant income test (all-or-nothing): recreated
- dividends exempt from income tax (Second Schedule): recreated
- Fair Share Contribution on high incomes incl. dividends: recreated
- additional Rs 500 000 deduction for a dependant in tertiary studies: not modelled
- solidarity levy repealed (Sub-Part AA): catalogued

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 7.3288, "netIncomeFalls": 1}, "couple1earner2kids": {"maxMETR": 7.2288, "netIncomeFalls": 1}, "couple60_40_2kids": {"maxMETR": 7.3192, "netIncomeFalls": 2}}
- `world/tools/scan_world.py MU` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- National Savings Fund contribution
- tertiary-education dependant deduction
- s. 27 (6) deeming of a dependant's income

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (statute)
- provisions: National Savings Fund Act 1995 s. 5 (2)-(3), First Schedule item 2 (c), s. 2 "basic wage or salary"; National Pensions Act 1976 Fifth Schedule (a) (18,740; GN 268 of 2021 w.e.f. 1 July 2019); ITA ss. 27D, 27DC (MRA consolidations)
- NSF employee 1 % of the basic wage up to Rs 18,740 a month, nil at or below Rs 3,000 (Government pays), not deducted. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: NSF "basic wage" (allowances excluded) taken as the whole wage. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/MuTax/Verify.lean` (imported by the `MuTax` library and built; each guard evaluates `MuTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/MU.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | CSG at 3 % of the whole remuneration once Rs 50,000 a month is passed (1.5 % below): 12 rupees more a year at Rs 600,000 cost 8,989 of net. G: f1_csg_whole_wage; T: MuTax.csgMonthly #guard. S: SCSBA 2021 s. 4 (1), First Schedule Part II as cited by the model (law/FinanceAct2024.txt amends the 50,000 thresholds elsewhere). |
| F2 | confirmed | The spouse dependant deduction ends when her income exceeds Rs 110,000: one rupee more costs the couple 21,999. G: f2_spouse_dependant_test. S: ITA s. 27 (5) (a) as cited by the model. |
| F3, F4 | explained | Fair Share Contribution design; FA 2026 already in the consolidation. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan notches 8,999 at 600,011 / 1,000,019 / 1,500,028 = F1 (one per earner); 8,499 at 110,000 (second earner) = F2. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: CSG at 3 % of the whole wage above Rs 50,000 a month (1.5 % below) | cliff or notch | **new**: PwC Mauritius (Other taxes) prints CSG at 1.5 % for a basic wage 'not exceeding MUR 50,000 in a month' and 3 % above, not that the higher rate applies to the whole wage at once; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'Mauritius contribution sociale généralisée employees 1.5% 3% Rs 50,000'; 'Mauritius CSG contribution rate threshold cliff' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (mauritius, 5 individual pages): 9 passages with the item's terms; Crossref IMF prefix 10.5089 'Mauritius tax policy' (8292 records, titles only). Record: world/loopholes/africa_mena/search/MU-F1.json |
| F2: Spouse dependant deduction ends when her income exceeds Rs 110,000 | second-earner trap | **new**: PwC Mauritius prints the dependant deductions (one dependant 110,000 ...) but not the spouse's income test as a cliff; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'Mauritius income exemption threshold dependent spouse 110,000' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (mauritius, 5 individual pages): 13 passages with the item's terms. Record: world/loopholes/africa_mena/search/MU-F2.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.23 AW (contribution rate 2.5 -> 1.6 %, combined marginal 2 -> 1 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
