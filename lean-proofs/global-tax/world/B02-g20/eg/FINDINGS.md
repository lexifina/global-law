# Egypt (EG) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 Five notches: crossing 600k/700k/800k/900k/1.2m of net income by 10 pounds costs 2,752-10,002 pounds
- kind: loophole-new
- Law 7/2024 art. 8 removes the lower bands once net income passes each column limit: tax jumps by 4,002 at 600,000, 2,752 at 700,000, 3,502 at 800,000, 5,002 at 900,000 and 10,002 at 1,200,000 (measured on the exe; METR up to 693 % on the 1,250-pound scan step). Above each limit there is a dead zone where more pay leaves less net (about 13,800 pounds wide at 1.2 m). Known design (the 'bracket exclusion' introduced in 2020-2023); the notch sizes are not found in the sources read (no search).
- provisions: Law 91/2005 art. 8 (Law 7/2024)
- Lean: EgTax.column, #guard, results/search/b02scan.md
- status: measured

### F2 Generic scan: 5 net-income falls single, 9 for a 60/40 couple
- kind: model-fix
- b02scan.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Law 148/2019 arts. 19 (1) (b), 36 (1); NOSI notice 30/11/2025 (2025 limits, official secondary); ITL 91/2005 art. 13 (ETA circular 1/2005)
- Law 148/2019 employee 9 % + 1 % on the monthly contribution wage 2,300-14,500; deducted (ITL art. 13 item 5). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/EgTax/Verify.lean` (imported by the `EgTax` library and built; each guard evaluates `EgTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/EG.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Column tariff: once net income passes 600,000 / 700,000 / 800,000 / 900,000 / 1,200,000 the lower bands are withdrawn: one pound of gross at 937,410 costs 5,001 of net, at 1,237,410 10,001 (rescan: 15 notches up to 10,001; METR up to 443 %). G: f1_notch_600k, f1_notch_1200k. S: law/law_no.30-2023.txt:196-199 (the column heads 'يتجاوز ٦٠٠,٠٠٠ / ٧٠٠,٠٠٠ / ٨٠٠,٠٠٠ ... ١,٢٠٠,٠٠٠'; Law 7/2024 kept the structure). |
| F2 | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md). |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) | Social insurance present (17,400 at the ceiling). |
| Leads | explained | Rescan: all notches = F1 (single and each earner of a couple); timing gain 18,489 = F1. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Column tariff: crossing 600k/700k/800k/900k/1.2 M of net income withdraws the lower bands | cliff or notch | **known**: Described by PaySpace and Standard Bank's market guide ('taxpayers with a higher net taxable income are not allowed to avail of the lower tax brackets'; income between EGP 600,000 and 700,000 is not eligible for the 0 % bracket) and by Deloitte Middle East's note on Law 7/2024 (web search, see record); the notch amounts are not quantified there. | 2026-11-20: OpenAlex queries 'Egypt income tax brackets high earners lose lower brackets'; 'Egypt income tax law 7 2024 brackets exemption removal' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (egypt, 5 individual pages): 13 passages with the item's terms; Crossref IMF prefix 10.5089 'Egypt tax policy personal income tax' (9088 records, titles only); web search: WebSearch 2026-11-20 'Egypt income tax 2024 brackets taxpayers exceeding 600,000 lose lower brackets jump': Deloitte ME 'amendment to tax brackets and annual personal exemption'; payspace.com; tradeclub.standardbank.com/portal/en/market-potential/egypt/taxes; taxsummaries.pwc.com/egypt. Record: world/loopholes/africa_mena/search/EG-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- mix.py (wage vs fee split): lead: small (salary exemption).
- ceilings.py: ceiling at 0.15 AW (contribution rate 10.0 -> 0.0 %, combined marginal 27 -> 20 %); floor at low pay AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
