# AL findings (Albania (tatimi mbi të ardhurat personale on employment and investment income; social and health contributions), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 960 000 ALL = 2 × 12 × minimum wage 40 000); leads: single|none: max 511.8 %, average 511.8 % (top 23.0 %) from 600,000 to 604,800 (0.625-0.63 AW); causes: taxableIncome, employmentIncomeTax; single|none: max 186.8 %, average 186.8 % (top 23.0 %) from 720,000 to 724,800 (0.75-0.755 AW); causes: taxableIncome, employmentIncomeTax; single|dividends_1AW: max 511.8 %, average 511.8 % (top 23.0 %) from 600,000 to 604,800 (0.625-0.63 AW); causes: taxableIncome, employmentIncomeTax

### F1 Two notches from the bracketed personal deduction (neni 22)
- kind: loophole-new (structure; known as a design feature, not found in the sources read)
- status: proved

The deduction is 600 000 lekë for income up to 600 000, 420 000 up to 720 000 and 360 000 above. One lek above 600 000 costs 23 400 lekë of tax and one lek above 720 000 another 7 800 (Lean `AlTax.notch_600k`, `notch_720k`, `notch_net`). Scanner (scale 960 000): METR 511,8 % from 600 000 to 604 800 and 186,8 % from 720 000 to 724 800. A taxpayer just above either limit is better off earning less (pay just above 600 000 nets less than 600 000 until about 627 000).

### F2 The 2023-2024 transitional monthly table and the 2025 annual tariff use the same band
- kind: observation (statute check)
- status: proved

Neni 69 (2) printed 22 100 lekë at 200 000 lekë a month (13 % of 170 000 after the 30 000 deduction); 2 040 000 = 12 × 170 000 (`monthly_table_consistent`, `annual_band_is_12_months`).

### F3 Contributions stop at 176 416 lekë a month
- kind: observation (structure)
- status: lead checked against the statute

Employee 9,5 % + 1,7 % on pay between the minimum (40 000) and maximum (176 416) monthly wage (Ligj 7703 neni 10; VKM 434/2023). Above 2,1 M lekë a year the combined marginal rate falls from 34,2 % (23 % + 11,2 %) to 23 %.

### F4 The maximum contributory wage for 2025 is not printed in any 2025 act
- kind: reading
- status: reading

Ligj 7703 neni 10 indexes the maximum wage to the minimum wage; the last printed amount is 176 416 (VKM 434/2023) and the minimum wage did not change in 2025 (VKM 776/2025 repeals VKM 113/2023 only from 1 January 2026), so the model keeps 176 416.

### F5 Model limits
- kind: model limitation
- status: open

Self-employment is taken as both gross and net (0 % up to 14 M under neni 69 (1) (dh)); employment-like self-employment (neni 12 (1) (ç)), private pensions, education expenses and the self-employed's contributions are not modelled (listed in `unsupported`).


## Round D7 (improvement agent, 2026-11-20)

### D7-1 Business income 3 250 000: 0 % in 2025 by Ligj 29/2023 neni 69 (1)(dh); the 2023 instruction's example is not 2025 law
- kind: finding
- Ligj 29/2023 (Global law, as in force 2025-07-01) neni 24 (2): net business income of individual traders and the
  self-employed 15 % to 14 000 000, 23 % above; but neni 69 (1)(dh) as amended by Ligj 9/2025 (in force 2025-03-13): for
  individual traders, the self-employed and entities "me të ardhura bruto deri 14 milionë lekë në vit, norma e tatimit mbi
  të ardhurat 0% do të aplikohet deri më 31 dhjetor 2029". With gross business income of 3 250 000 the 2025 tax is 0; the
  model applies this. Neni 69 (6) records that VKM 753/2023, which had excluded professional-service self-employed from
  the 0 %, was annulled by the Constitutional Court (decision 52 of 27.6.2024). Udhëzim 26/2023 predates both changes,
  so its example (419 100, which no 2025 reading of neni 24 (2) on 3 250 000 gives: 15 % would be 487 500) reflects
  2023-24 rules or additional facts of the example. No change; the dataset's year (2025) is the test agent's to review.
- status: finding (no model change)

### W5S-1 llogarit-pagen: no maximum contribution base (W5 review pass 2, 2026-11-20)
- kind: software-error
- `al_open_llogarit_pagen_grid`: the tool charges 9.5 % + 1.7 % on the whole wage; Ligj 7703 neni 10 and VKM 434/2023 pika 4 (b) cap the base at the paga maksimale 176,416 lekë a month (AlTax.Params). Its TAP is monthly withholding without the annual neni 22 (1)(ç) child compensation (a mapping matter: rebuild requested).
- status: recorded (world/IMPROVE_W5.md pass 2)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 23,400 ALL for one lek above 600,000; 7,800 above 720,000. exe and #guard L1AL.F1; model theorems. Evidence: exe + Lean `L1AL.F1` (`world/loopholes/rest/lean/L1AL.lean`, 2 #guard): tot(b)-tot(a) = 23400; tot(d)-tot(c) = 7800; statute re-read: `src/ligj29-2023_2025-07-01.md`; model Lean: AlTax.notch_600k, notch_720k, notch_net. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | fact | proved | Model theorems. Evidence: model Lean: AlTax.monthly_table_consistent, annual_band_is_12_months. |
| F3 | fact | explained | Contribution ceiling (fact). |
| F4 | reading | lead | Reading (reading): open as the builder left it; no amount depends on it in L1. |
| F5 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| D7-1 | fact | explained | Recorded finding with no amount to reproduce; the provision is cited by the builder; not a loophole. |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/AL.json`): METR 511.8 % / 186.8 % and notches 23,399 / 7,799 = F1 (and their couple multiples at 1.04-1.875 x scale); METR 1,120 % at the first lek = contributions on the minimum-wage base for a positive wage (Ligj 7703 neni 10; exe: 4,480 on 1 lek): a contribution floor.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 15.0 % (Ligji 29/2023 'Për tatimin mbi të ardhurat': 'Norma e tatimit mbi të ardhurat e korporatave është 15%. Përjashtimisht, norma tatimore për dividendët është 8%' (); at a profit of 3 AW the best split costs 21.8 % of the profit, all salary 30.6 %, all dividends 21.8 % (employer contributions: statute rate 13.80 %); dividends beat salary once employer contributions exceed 1 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- ceilings.py: floor: contribution rate 112 % at 0.05 AW vs 11 % at 0.5 AW. Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
