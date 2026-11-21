# Thailand (TH) findings, B03-asia-east-se (2026-11-20T03:05Z)

Built from the statute only (no referee values seen). Scanner outputs: `results/search/` (SUMMARY.md from world/tools/scan_world.py; b03scan.md fine grid 0-2.5 x scale.json).

### F1 Minimum tax of 0.5 % of non-salary income from 120,000 baht is a notch
- kind: loophole-known
- s. 48 (2): with assessable income (other than s. 40 (1) salary) of 120,000 baht or more, tax is not less than 0.5 % of that income: at exactly 120,000 the floor jumps from 0 to 600 baht. A royal decree cited beside the section (No. 480) exempts small amounts and was not read; the model applies the Code's floor.
- provisions: Revenue Code s. 48 (2)
- Lean: ThTax.out (floor)
- status: model result

### F2 Interest: the 15 % separate tax is a choice that benefits higher earners only
- kind: fact
- s. 48 (3) lets bank interest be taxed at 15 % instead of being included; for a taxpayer whose marginal rate is under 15 % inclusion is cheaper (the model takes the cheaper).
- provisions: Revenue Code s. 48 (3) (ก)
- Lean: ThTax.out
- status: model result

### F3 Children's allowance doubles for the second child born from 2018
- kind: fact
- s. 47 (1) (ค) (1) (Act No. 46): 30,000 per child plus 30,000 for each second or later child born in or after 2018; the first child born after 2018 gets no supplement.
- provisions: Revenue Code s. 47 (1) (ค)
- Lean: ThTax.childrenAllowance
- status: model result


### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: กฎกระทรวงกำหนดอัตราเงินสมทบ พ.ศ. 2545 ข้อ 2-3, บัญชี ข-ค (1.5 % + 3 %); กฎกระทรวง ... ว่างงาน พ.ศ. 2546 ข้อ 1 (3) (0.5 %); กฎกระทรวง ฉบับที่ 7 (พ.ศ. 2538) ข้อ 1 (1,650-15,000); SSA s. 33, s. 46; Revenue Code s. 47 (1) (ฌ) (SSO copies via the Wayback Machine)
- social security 5 % of the monthly wage within 1,650-15,000 (max 750 a month), rounded to the baht; deducted under s. 47 (1) (ฌ). Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: social security: the 2012 rate regulation (พ.ศ. 2555) not read; a positive wage below 1,650 a month assessed on 1,650.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 600 THB at 120,000 of non-salary income. exe and #guard L1TH.F1; s. 48 (2) text not located by pattern (builder's citation); Royal Decree 480 not read. Evidence: exe + Lean `L1TH.F1` (`world/loopholes/rest/lean/L1TH.lean`, 1 #guard): it(b)-it(a) = 600. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | fact | model-proved | 15,000 THB on 100,000 of interest at the 15 % final rate for a top-band earner. exe and #guard L1TH.F2. Evidence: exe + Lean `L1TH.F2` (`world/loopholes/rest/lean/L1TH.lean`, 1 #guard): it(a)-it(b) = 15000. |
| F3 | fact | explained | Recorded fact with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TH.json`): notch 995 at the first baht = social security on the 1,650 minimum base for a positive wage (W5A reading; exe 996 on 1 baht); timing 6,965-13,608 = the SSO ceiling (15,000 a month).

## L1-S correction (2026-11-21)

F1 withdrawn. Royal Decree No. 480 (B.E. 2552) s. 3, read on rd.go.th (`law/rd_40923_rd480.html`, `law/dc480.pdf`):
"ให้ยกเว้นภาษีเงินได้ ... สำหรับภาษีที่ต้องเสียตามมาตรา 48(2) เฉพาะกรณีผู้มีเงินได้มีภาษีที่ต้องเสียทั้งสิ้นจำนวนไม่เกินห้าพันบาทในปีภาษีนั้น":
the s. 48 (2) minimum tax is exempt when it is 5,000 baht or less. There is no 600-baht notch at 120,000. The model now
charges the 0.5 % only when it exceeds 5,000 (`ThTax.minTax`, #guards `minTax 120000 = 0`, `minTax 1000001 = 5000`;
`lake build` OK; `world/loopholes/rest/spec/TH.json` F1 now asserts no jump at 120,000 or 1,000,000). A 5,000-baht notch
remains at 1,000,000 of gross non-salary income for people whose s. 48 (1) tax is below 5,000 (large expenses), which
the model (net self-employment) cannot show. Backup: `world/loopholes/strengthen/backup/ThTax_Basic.lean.bak-S1`.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.2604 AW (contribution rate 5.0 -> 0.0 %, combined marginal 5 -> 5 %); floor at low pay AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
