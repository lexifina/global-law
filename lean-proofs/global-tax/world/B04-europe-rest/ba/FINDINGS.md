# BA findings (Bosnia and Herzegovina: Federation of BiH (porez na dohodak; doprinosi zaposlenika), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 36 000 BAM = 10 × the basic personal deduction); leads: second_earner_2|none: max 130.6 %, average 130.6 % (top 37.8 %) from 5,040 to 5,220 (0.14-0.145 AW); causes: taxableIncome, personalDeductions; second_earner_2|dividends_1AW: max 130.6 %, average 130.6 % (top 37.8 %) from 5,040 to 5,220 (0.14-0.145 AW); causes: taxableIncome, personalDeductions

### F1 Dependent-spouse cliff
- kind: loophole-new (structure; not found in the sources read)
- status: proved (value) / lead (scanner)

The spouse deduction (0,5 × 3 600 = 1 800 KM, worth 180 KM of tax) is lost entirely when the spouse's own income passes 3 600 KM (član 24 (3)). Scanner (second earner, scale 36 000): METR 130,6 % on the second earner's gross pay between 5 040 and 5 220 KM. Lean `BaTax.spouse_value`.

### F2 Combined marginal rate 37,9 % on pay
- kind: observation (structure)
- status: lead checked against the statute

31 % employee contributions (17 + 12,5 + 1,5, član 10 as replaced by 14/08) and 10 % tax on the rest: 31 % + 10 % × 69 % = 37,9 %, the scanner's top rate.

### F3 Child deductions: equal sharing or the parents' agreement
- kind: reading / election
- status: model-fix (election added)

Član 24 (4) shares the child deductions equally among the persons who support the children 'osim ako se ne dogovore drugačije'; the model takes the cheapest of equal sharing and all-to-one-parent (an election). Equal sharing alone wastes deductions when one parent's income is small (scanner, first run: 151,7 % METR at the second earner's first 180 KM).

### F4 Amendment 99/19 to the Zakon o doprinosima missing from Global law
- kind: lesson (source)
- status: noted

SN FBiH 33/25 lists '... 34/18, 99/19, 4/21 i 6/23' among the amendments; the record holds no 99/19 act. 33/25 quotes the employer rates it replaces and leaves the employee rates (član 10 tačka 1) untouched, so the employee rates are 14/08's.

### F5 Mid-year cut of employer contributions
- kind: observation
- status: noted

33/25 lowers the employer's PIO rate from 6 % to 2,5 % and health from 4 % to 2 % from 1 July 2025 (član 4, 7): employer side, outside the household contract.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | confirmed | 180 BAM for one mark of the spouse's pay at 5,218 (the 1,800 spouse deduction at 10 %). exe and #guard L1BA.F1. Evidence: exe + Lean `L1BA.F1` (`world/loopholes/rest/lean/L1BA.lean`, 1 #guard): tot(b)-tot(a) = 180; statute re-read: `src/pit_2008_sn010-d2c23a.md`; model Lean: BaTax.spouse_value. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | fact | explained | Combined rate arithmetic. |
| F3 | reading | lead | Reading (reading / election): open as the builder left it; no amount depends on it in L1. |
| F4 | record | explained | Record (lesson (source)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F5 | fact | explained | Recorded observation with no amount to reproduce; the provision is cited by the builder; not a loophole. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BA.json`): METR 130.6 % and notch 179 = F1; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
