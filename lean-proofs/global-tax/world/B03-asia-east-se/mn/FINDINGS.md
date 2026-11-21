# Mongolia (MN) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 Stepped wage-tax credit makes take-home pay fall at six thresholds
- kind: loophole-known
- Art. 23.1 gives 240,000 MNT a year up to 6,000,000 of annual taxable income, then 216,000 ... 120,000 to 36,000,000, then nothing. One more tugrik of taxable income at 6m, 12m, 18m, 24m, 30m costs 24,000 of credit; at 36m it costs 120,000. Fine-grid scan (b03scan): six net-income falls for a single earner (e.g. 6,771,600 -> 6,795,360 gross: tax +28,827 for +23,760). The #guard netTaxAt checks the 24,000 / 120,000 jumps on taxable income directly.
- provisions: PIT Law art. 23.1, 23.14
- Lean: MnTax.credit, MnTax.netTaxAt (#guard)
- status: model result

### F2 The 2025 rate table is not in the record of the law as currently published
- kind: statute-fault
- legalinfo.mn (and Global law, which mirrors it) shows only the 2026-06-26 wording of art. 21.1, in force from 2027; the 2022-11-11 wording that governs 2023-2026 is no longer published there and had to be read from an archived copy. A reader of the official site in 2026 sees rates that do not apply to the year being filed.
- provisions: PIT Law art. 21.1 (versions 2022-11-11 and 2026-06-26)
- Lean: MnTax.sched
- status: model result

### F3 Overlapping bracket wording in the credit table
- kind: statute-fault
- Art. 23.1 prints '0-6 000 000 хүртэл' and '6 000 000-12 000 000 хүртэл': exactly 6,000,000 falls in both rows (240,000 or 216,000). Art. 21.1 avoids this with '120 000 001-180 000 000'. The model reads the upper bounds as inclusive.
- provisions: PIT Law art. 23.1
- Lean: MnTax.credit
- status: model result

### F4 Health insurance has no ceiling while social insurance stops at 10 x the minimum wage
- kind: fact
- Employee social insurance 9.5 % stops at 7,920,000 a month (from April 2025); health insurance 2 % (Gov. res. 02/2025) has no ceiling in the Health Insurance Law: the employee contribution rate falls from 11.5 % to 2 % above the ceiling.
- provisions: SIGL art. 18.1, 19.4; HIL art. 8.1.1
- Lean: MnTax.siMonthly, MnTax.hiMonthly
- status: model result


## Round W5 review (W5 fix agent, 2026-11-20)

### W5-1 unenmedee omits the PIT Law art. 23.1 annual tax credit (software error)
- kind: software-error
- PIT Law art. 23.1 (as in force in 2025; the model's text, see Basic.lean): an annual credit on employment income by
  taxable income (240,000 up to 6 m, falling by 24,000 per 6 m band). The tool computes 10 % of income less social
  insurance with no credit, so it is above the model by the credit (e.g. 10.4 m: 921,372 vs 705,371). Grid
  `mn_open_unenmedee_grid` (W5 review). The employeeSocial misses are rounding (a few tugrik).

### W5S-1 two single-author calculators (wronglaw grids): flat credit instead of the art. 23.1 credit (W5 review pass 3, 2026-11-20)
- kind: software-error
- `mn_open_salary_calculator_b26fa1910_grid` (flat 12,000 a month) and `mn_open_erp_connect_tugsbayar0611_grid` (flat 18,000 a month) replace the art. 23.1 credit graded by annual taxable income: below the model at low wages (-96,000 at 4.3 M; -24,000 at 3.9 M), above by 144,000 = 12 x 12,000 and 216,000 = 12 x 18,000 where the statute gives no credit. Their other flagged features (no 15 / 20 % bands above 120 M; a 550,000 minimum wage for the ceiling) are outside the grids' wages. The third note (`mn_open_munkhzaisanapp_chinzo0805_grid`: flat 10 %, NDSh without ceiling, base gross less employer NDSh) is **not** confirmed: tax within 0-5 and ES -12..-21 (monthly rounding) on every sampled case.
- provisions: PIT Law art. 23.1 (credit), art. 21.1 (bands)
- status: recorded (world/IMPROVE_W5.md pass 3, wronglaw table)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 24,001 MNT of tax + SI for 10 more of pay at 6,779,650 (the credit step); 28,827 for +23,760 (FINDINGS' pair); 120,000 at the 36 M end. exe and #guard L1MN.F1; FINDINGS' 'tax +28,827' is tax plus social insurance. Evidence: exe + Lean `L1MN.F1` (`world/loopholes/rest/lean/L1MN.lean`, 2 #guard): tot(b)-tot(a) = 28827; tot(d)-tot(c) = 24001; statute re-read: `law/gl_pit_14410.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | gov-error | explained | Publication fault; not re-checked. |
| F3 | statute-fault | explained | Overlapping bracket wording; reading recorded. |
| F4 | fact | explained | Health insurance without ceiling (fact). |
| W5-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MN.json`): notches 23,999 at each 6 M step and 119,999 at 36 M = F1; bands above the 16.7 % top = the credit steps (F1).
