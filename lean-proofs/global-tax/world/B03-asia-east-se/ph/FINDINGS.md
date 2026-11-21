# Philippines (PH) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 Final taxes on passive income sit beside the graduated rates
- kind: fact
- Bank interest bears a 20 % final tax and dividends 10 % (Sec. 24 (B)) whatever the taxpayer's bracket: for anyone under the 20 % band the final tax on interest exceeds the graduated rate; above 30 % it is lower.
- provisions: NIRC Sec. 24 (B) (1), (2) as amended by RA 10963 Sec. 5
- Lean: PhTax.out
- status: model result

### F2 The official archived scan is the only scriptable copy of the 2018-2025 rate law
- kind: fact
- All official publishers refuse scripts; the archived Gazette PDF is truncated after 43 of its pages (Sections 1-10), enough for Sec. 24 and Sec. 32 but not for later sections.
- provisions: RA 10963
- Lean: ph/law
- status: model result


### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: RA 11199 s. 4 (a) (9); RA 11223 s. 10 with PhilHealth Circ. 2020-0005 and Adv. 2025-0002; RA 9679 s. 7 with HDMF Circ. 460 (per DBM CL 2024-2)
- SSS 5 % (MSC 5,000-35,000), PhilHealth 2.5 % (10,000-100,000), Pag-IBIG 2 % (max 10,000 / month); excluded from gross income (NIRC s. 32 (B) (7) (f)). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

### W5A-2 Contribution follow-up (W5 pattern A, reviewer 3 pass 3, 2026-11-20)
- kind: model gap fixed from the statute / official secondary
- provisions: SSS Circular No. 2024-006 (19 Dec 2024), Schedule of SSS contributions effective January 2025 (SSS table image, `law/w5/sss_circular_2024-006_schedule_2025.jpg`); RA 11199 Sec. 4 (a) (9)
- SSS monthly salary credit = compensation rounded to the nearest P500 (halves up) within 5,000-35,000 (was: compensation clamped), member 5 %. Switch: `"w5Contrib": false` still restores the pre-W5 outputs (0 of 300 random households differ).
- status: fixed

### W5S4-1 OpenHRPH TakeHomePayCalculator (kawayanmedia): withholding tax on gross compensation (W5 review pass 4, 2026-11-20)
- kind: software-error
- `ph_open_openhrph_kawayanmedia_grid`: the calculator computes the employee's SSS, PhilHealth and Pag-IBIG itself but passes `taxableCompensation: $gross` to the TRAIN table (its comment: 'the tax is applied to the gross regular and supplementary compensation'); NIRC Sec. 32 (B) (7) (f) excludes 'GSIS, SSS, Medicare and Pag-ibig contributions'. Dev: tool above by the marginal rate x the contributions (-13,350 = 25 % x 53,400 in 134 cases); employeeSocial 1,056 / 1,056 within 1 %.
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | confirmed | 20 % final on interest, 10 % on dividends. exe and #guard L1PH.F1; RA 10963 Sec. 5 re-read ('twenty percent (20%)'). Evidence: exe + Lean `L1PH.F1` (`world/loopholes/rest/lean/L1PH.lean`, 2 #guard): sur(a) = 20000; sur(b) = 10000; statute re-read: `law/ra_img/p04.txt`. |
| F2 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-2 | record | explained | Record (model gap fixed from the statute / official secondary): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PH.json`): METR 301 % at the first peso = contribution floors (SSS minimum salary credit 5,000 a month; exe: 500 on 1 peso); timing 6,654-12,012 = the SSS / PhilHealth ceilings; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 25.0 % (NIRC sec. 27 (A) as amended by RA 11534 (CREATE) sec. 6: 'an income tax rate of twenty-five percent (25%) effective July 1, 2020' (Global law record philippines); at a profit of 3 AW the best split costs 20.2 % of the profit, all salary 20.2 %, all dividends 32.5 % (employer contributions: not included); dividends beat salary once employer contributions exceed 21 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- ceilings.py: ceiling at 0.9 AW (contribution rate 9.9 -> 2.7 %, combined marginal 21 -> 21 %); ceiling at 2.99 AW (contribution rate 2.4 -> 0.0 %, combined marginal 27 -> 25 %); floor at low pay AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
