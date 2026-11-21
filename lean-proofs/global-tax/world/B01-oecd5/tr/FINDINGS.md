# TR findings (Türkiye (gelir vergisi on wages, minimum-wage exemption, damga vergisi, SGK employee premiums), 2025 (calendar year))

Batch B01-oecd5, built 2026-11-20 01:48 UTC. Status: built (model frozen for the software phase; no referee values used). Scanner output: `results/search/SUMMARY.md` (run with a statutory reference wage instead of the OECD AW, `tools/scan_b01.py`).

### F1 The printed 2025 tariff is exact: both column forms equal their bands
- kind: observation (statute check)
- status: proved

Tebliğ 41166 m. 3 (3) prints the tax at each lower limit (23.700; 58.100; 185.000 / wages 293.000; 1.410.000 / wages 1.378.000). Lean `TrTax.printed_eq_bands`, `printedWage_eq_bands`, `printed_no_jumps` (kernel Tariff): the printed amounts are the exact band sums, no jump at any threshold. `wage_le_general`: the wage tariff never taxes more than the general tariff (its 27 % band runs to 1.200.000 instead of 800.000: worth up to 32.000 TRY).

### F2 Mid-income wages face a higher marginal rate than top incomes (SGK ceiling)
- kind: observation (structure)
- status: lead checked against the statute

Scanner METR (results/search/SUMMARY.md, statutory scale 624.132 TRY = 2 × annual minimum wage): peak 45,6 % at 1,65 M TRY a year (35 % band × 0,85 + 15 % premiums + 0,759 % stamp duty), against 40,75 % at the top (40 % + stamp duty) once the monthly wage exceeds the SSK art. 82 ceiling (7,5 × minimum wage = 195.041,40 TL a month). Provisions: GVK 103, 63; SSK 81-82; DVK. Known feature of capped contributions.

### F3 Reading R1: the minimum-wage exemption's cap
- kind: reading
- status: reading; to be checked against official guidance in the dataset phase

GVK art. 23 (18): the tax 'istisna tutara isabet eden kısım' is deducted, and the tax not collected 'ilgili ayda aylık asgari ücret üzerinden hesaplanması gereken vergiyi aşamaz'. The model deducts each month min(own tax, the cumulative-method tax of a minimum-wage earner in that month), so for a full-year employee the exemption is worth tariff(12 × 22.104,67) = 45.151 TRY (`detail.minimumWageExemption`). A Tebliğ (Seri 331) worked example was seen while reading the minimum-wage amount; it was not used to fit anything (exposure recorded for the dataset phase).

### F4 Reading R2: wages above the art. 86 (1) (b) limit and other declared income
- kind: reading
- status: reading

Single-employer wages are declared only above the 4th-bracket amount (4.300.000 TRY); the model then stacks the other declared income (rent after the 47.000 exemption and the 15 % lump sum, self-employment) on the wage base under the general tariff. Whether gross or net wages are compared with the limit is not settled by the text read.

### F5 Model gaps that show up as scanner 'gains'
- kind: model limitation
- status: open

Interest, dividends, capital gains and pensions are listed as unsupported (final withholding at rates set by presidential decisions not reached; SGK pensions). The income-type scanner therefore shows +38 % 'gains' for these types: artefacts of the gaps, not findings.

### F6 Global law record: the GVK is current-only; dates came from the 5510 entry-into-force list
- kind: lesson (source)
- status: noted

read_law on GVK art. 103 at 2025-07-01 answers that the record starts on 2026-10-28; the 2025 tariff is not in the consolidation (it prints the 2020 base and the 2026 amounts) but in Tebliğ 41166. The SSK art. 81/82 changes of Kanun 7566 (4/12/2025) would have applied in December 2025 if read from the footnotes alone; the yürürlük list dates them 1/1/2026.

## Round D2 (improvement agent, 2026-11-20): D1 dev failures settled from the statute

### D2-1 Residuals are rounding and TaxBEN's whole-percent METRs (no change)
- kind: test-note
- TW 2025 71 / 72 exact (one 1.03 TRY); Tax DB rates 45 / 47 (0.01 pp); TaxBEN METRs 48 of 64 within 1 % (TaxBEN
  publishes whole percent: M2 covers it); Tax DB SSC "EECSSC/gross jump" 15 at the SGK floor/ceiling step, not a
  statute question. No change.
- status: closed

### W5S-1 world-tax-brackets (TR): no minimum-wage exemption (W5 review pass 2, 2026-11-20)
- kind: software-error
- `tr_open_world_tax_brackets_tr_grid`: the tool applies the GVK art. 103 scale to the whole wage; GVK md. 23 (18) exempts the minimum-wage part ('asgari ücretin aylık brüt tutarından ... düşüldükten sonra kalan tutarına isabet eden ... vergi'), so below the minimum wage the model charges 0 and above it the model is lower by a constant 45,151.
- status: recorded (world/IMPROVE_W5.md pass 2)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | proved | Model theorems rebuilt. Evidence: model Lean: TrTax.printed_eq_bands, printedWage_eq_bands, printed_no_jumps, wage_le_general. |
| F2 | fact | explained | Exe: marginal cost at 1.65 M exceeds that at 6 M (L1TR.F2); the timing lead (15,216 TRY) is the SGK ceiling. The consolidated SSK art. 82 now prints the 2026 ceiling ('9 katı'); 7.5 x for 2025 by the yürürlük list (TR F6). Capped contributions: a known feature. Evidence: exe + Lean `L1TR.F2` (`world/loopholes/rest/lean/L1TR.lean`, 1 #guard): (tot(b)-tot(a))-(tot(d)-tot(c)) = 5. |
| F3 | reading | lead | Reading (reading): open as the builder left it; no amount depends on it in L1. |
| F4 | reading | lead | Reading (reading): open as the builder left it; no amount depends on it in L1. |
| F5 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F6 | record | explained | Record (lesson (source)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| D2-1 | record | explained | Record (test-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/TR.json`): timing 15,216 = F2 (SGK ceiling); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (F5 model gaps).

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Printed tariff exact (T: printed_eq_bands). |
| F2 | explained | Mid-income METR above the top (SGK ceiling): a contribution-ceiling regressivity, known in kind; rescan timing gain 15,216 at 3.25 +- 0.75 'AW' is the same ceiling. |
| F3, F4 | lead | Readings R1, R2. |
| F5 | explained | Model gaps shown as scanner gains. |
| F6, D2-1, W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | As F2. |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- mix.py (wage vs fee split): explained: round-1 TR note (single-employer wages under the GVK art. 86 declaration limit).
<!-- R2-SCANNERS:END -->
