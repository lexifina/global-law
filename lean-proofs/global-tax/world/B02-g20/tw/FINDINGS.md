# Taiwan (TW) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 Dividend credit refunded in cash to low-income households
- kind: loophole-known
- A household with only dividends of 900,000 pays 39,340 before the credit and gets 76,500 credit: a refund of 37,160 (art. 15 (4) credit 8.5 % up to 80,000 per household; art. 71 (3) allows refund of the credit). The model takes the cheaper of the credit and the 28 % option automatically.
- provisions: art. 15 (4)-(5), art. 71 (3)
- Lean: TwTax.methodTax / best
- status: lead (known design: integrated dividend credit)

### F2 Salary computed separately: the joint return is close to separate taxation for two earners
- kind: loophole-known
- For two earners (1.5m + 0.8m, two children) the cheapest method is salary-separate for the second spouse (tax 50,600). art. 15 (2) lets the couple pick the method each year; the model evaluates all five and both dividend options.
- provisions: art. 15 (2)
- Lean: TwTax.options
- status: lead

### F3 Generic scan: no notch, max METR 40 % (single), 36 % (two earners)
- kind: model-fix
- b02scan on 0-2.5 × 4.98m: no net-income fall; the basic-living-expense difference and the preschool deduction create no cliff.
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: 勞工保險條例 art. 13 (2) (12.5 % for 2025), 14, 15; 就業保險法 arts. 8, 40, 41 (2) (-1 %); 勞動部令 2024-11-15 勞動保2字第1130087589號 grading table; BLI 114 share table (official secondary); 全民健康保險法 arts. 2, 18, 19, 27; NHIA 114 grading and share tables (5.17 %, official secondary); 所得稅法 art. 17 (1) 2 (二) 2
- labour + employment insurance (20 % of 11.5 % + 1 % on the 2025 insured-salary grade, 28,590-45,800, part-time grades below) and NHI (30 % of 5.17 % on the 59-grade table 28,590-313,000, x (1 + dependants up to 3)); NHI and LI premiums added to the itemized deduction (art. 17 (1) 2 (二) 2). Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: NHI dependent parents and the supplementary premium not modelled; part-time LI grades applied to any monthly wage below 28,590.
- status: fixed

### W5S4-1 blog-vitepress useIncomeTax (Chuiantw1212): brackets that are not 114年度's (W5 review pass 4, 2026-11-20)
- kind: software-error
- `tw_open_blog_vitepress_chuiantw1212_grid`: brackets 610,000 / 1,380,000 / 2,770,000 / 5,190,000; the Ministry of Finance's art. 5 (4) announcement of 2024-11-28 for 114年度 (2025 income) kept 590,000 / 1,330,000 / 2,660,000 / 4,980,000 (CPI up 2.29 %, below the adjustment threshold; law/mof114_quick_formula.pdf). Dev singles: model above by exactly the bracket shift (1,400 / 5,399 / 16,399 / 37,400 = 7 % x 20,000 + 8 % x 50,000 + 10 % x 110,000 + 10 % x 210,000). Couples: the tool taxes each adult as a single person (declared unit deviation), the Act files jointly (art. 15).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 37,160 TWD refunded to a household with only 900,000 of dividends. exe and #guard L1TW.F1. Evidence: exe + Lean `L1TW.F1` (`world/loopholes/rest/lean/L1TW.lean`, 1 #guard): tot(a) = -37160; statute re-read: `law/ita_5-1_14_15_17_71.txt`. Known/new: **unclear**: Crossref only (OECD dividend tables, no description); the refundable 8.5 % credit is the 2018 reform's design. |
| F2 | loophole | confirmed | tax 50,600 TWD for 1.5 M + 0.8 M with two children under the cheapest of the art. 15 (2) methods (after W5 contributions). exe and #guard L1TW.F2 (value unchanged by W5). Evidence: exe + Lean `L1TW.F2` (`world/loopholes/rest/lean/L1TW.lean`, 1 #guard): it(a) = 50600; statute re-read: `law/ita_5-1_14_15_17_71.txt`. Known/new: **unclear**: Method choice under art. 15 (2) is the statute's election; not searched. |
| F3 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TW.json`): notch 8,639 at the first dollar = labour and health insurance minimum grades; notches 5,579-5,615 = NHI grade-table steps multiplied by (1 + dependants) for a parent of two (statutory grading table); marriage bonus 68,400 = joint filing (F2); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- mix.py (wage vs fee split): explained: salary special deduction and employee insurance apply to salary only; small.
- ceilings.py: ceiling at 0.1 AW (contribution rate 3.7 -> 1.7 %, combined marginal 5 -> 7 %); ceiling at 0.52 AW (contribution rate 2.8 -> 0.0 %, combined marginal 22 -> 21 %); floor at low pay AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
