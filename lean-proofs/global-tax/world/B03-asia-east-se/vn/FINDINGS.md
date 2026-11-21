# Viet Nam (VN) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 The consolidated Law still prints family deductions that are no longer applied
- kind: statute-fault
- Art. 19 (1) in the 2025 consolidation prints 9 million dong a month for the taxpayer and 3.6 million per dependant (Law 26/2012) and lets the Standing Committee adjust them when the CPI moves over 20 %. The adjusted amounts live only in that resolution, so the official consolidated text of 2025 does not show the deduction actually used; a reader must find a separate resolution.
- provisions: PIT Law art. 19 (1) (VBHN 103/VBHN-VPQH)
- Lean: VnTax.selfDeduction
- status: model result

### F2 Unindexed brackets since 2013: the same 7-band table in nominal dong
- kind: fact
- Art. 22's bands (5/10/18/32/52/80 million a month) have not changed since Law 26/2012 (in force 2013-07-01); only the deductions are adjusted. The 2026 law replaces them.
- provisions: PIT Law art. 22
- Lean: VnTax.sched
- status: model result


## Round W2 (improvement agent, 2026-11-20): pointers from the new software probes (coordinator)

### W2-1 Family deductions and social-insurance cap: the statute delegates both; now inputs (amounts not read)
- kind: model-fix
- Pointer (thue-2026 probe): 4.4 M per dependant (and 11 M self) under NQ 954/2020/UBTVQH14, and 10.5 % employee
  insurance with legal caps, against the model's printed 9 / 3.6 M and uncapped 8 %. The consolidated PIT law
  (103/VBHN-VPQH, art. 19 (1)) itself provides that the Standing Committee adjusts the deductions when the CPI moves by
  more than 20 %, so a resolution under it governs 2025 and the printed figures are known to be stale; but its text
  was not reached in an official source this round (vbpl.vn search is script-rendered from the laptop and 403 from
  lean1; vanban.chinhphu.vn search returned only the portal; Global law's Viet Nam corpus holds laws, not Standing
  Committee resolutions). Health insurance: Luật BHYT 25/2008 art. 13 (1) a) (Global law, as in force 2025-06-30)
  sets only a ceiling, "tối đa bằng 6% tiền lương tháng, trong đó người sử dụng lao động đóng 2/3 và người lao động
  đóng 1/3"; the 4.5 % actually levied (employee 1.5 %) is by decree (not read). Unemployment insurance (Law on
  Employment 38/2013 art. 57, employee 1 %) is not in Global law. Change: optional inputs `vnSelfDeductionMonthly`,
  `vnDependantDeductionMonthly` (defaults: the printed 9 / 3.6 M, unchanged) and `vnSiBaseCapMonthly` (20 x the
  reference amount, Law 41/2024 art. 31 (1) đ)); #guards. HI and UI stay unmodelled. Next: read NQ 954/2020 (and the
  base-salary decree for the cap) from congbao.chinhphu.vn or vbpl.vn by hand, then set the defaults from them.
- provisions: PIT law art. 19 (1); Law 41/2024 arts. 31, 33; Luật BHYT art. 13
- Lean: VnTax.Params, VnTax.siWith (#guard)
- status: model changed (defaults unchanged); amounts open

### W5S-1 salary-net-calculator-2026 (txhuy; wronglaw grid): insurance without a ceiling (W5 review pass 3, 2026-11-20)
- kind: software-error
- `vn_open_salary_net_calculator_txhuy_grid`: employee insurance is 10.5 % of the whole gross at every wage, including above 20 x the reference level (582.8 M a year: 61.2 M). The ceiling is the Social Insurance Law's (the model takes its amount as the input vnSiBaseCapMonthly; the base-salary decree was not reached). The 8 % vs 10.5 % gap below the ceiling is the model's (BHYT, BHTN: W5 pattern A), not the tool's.
- provisions: Law on Social Insurance 41/2024 (contribution base capped at 20 x the reference level)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Nghị định 73/2024/NĐ-CP Điều 3 (2) (datafiles.chinhphu.vn); Law 41/2024 art. 31 (1) đ)
- social-insurance ceiling defaulted to 20 x lương cơ sở 2,340,000 = 46.8 million a month (input vnSiBaseCapMonthly still wins). Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: BHYT (Decree 146/2018) and BHTN (Law on Employment 38/2013 art. 57) still not modelled: texts not reached on an official host.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Recorded statute-fault with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| F2 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| W2-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/VN.json`): timing 4,162,560-4,702,080 = the social-insurance base cap (46.8 M a month); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 20.0 % (Luật Thuế thu nhập doanh nghiệp 67/2025/QH15 Điều 10 khoản 1: 'Thuế suất thuế thu nhập doanh nghiệp là 20%' (Global law record vietnam/national/acts/luat/2025/6); at a profit of 3 AW the best split costs 18.9 % of the profit, all salary 20.0 %, all dividends 24.0 % (employer contributions: not included); dividends beat salary once employer contributions exceed 6 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- ceilings.py: ceiling at 2.6033 AW (contribution rate 8.0 -> 0.0 %, combined marginal 31 -> 25 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
