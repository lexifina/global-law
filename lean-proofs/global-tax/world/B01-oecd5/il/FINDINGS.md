# IL findings (Israel (income tax with credit points and surtax; national insurance and health insurance), 2025 (calendar year))

Batch B01-oecd5, built 2026-11-20 01:48 UTC. Status: built (model frozen for the software phase; no referee values used). Scanner output: `results/search/SUMMARY.md` (run with a statutory reference wage instead of the OECD AW, `tools/scan_b01.py`).

### S1 The source's running text of s. 121(א)(2) contradicts its own table
- kind: source anomaly (unofficial consolidation)
- status: flagged

Wikisource rev. 2935650 s. 121(א)(2) reads 'על כל שקל חדש מ־560,280 שקלים חדשים עד 542,160 שקלים חדשים – 35%' (lower bound above upper bound), while its table for 2024–2027 gives 269,281–560,280 at 35 %. The model uses the table; the official Reshumot notice was not reached.

### F1 Indexation frozen 2025-2027
- kind: observation (statute)
- status: statutory

s. 120ב(ה) (amendment תשפ״ה־2): 'ב־1 בינואר של שנות המס 2025 עד 2027 לא יתואמו הסכומים', so the 2025 brackets, credit point (2.904) and surtax threshold (721.560) are those of 1 January 2024; with any inflation this is bracket creep for three years.

### F2 New 2 % surtax on capital income from 2025
- kind: observation (statute)
- status: statutory

s. 121ב(א1): a further 2 % on taxable income from capital sources above 721.560, on top of the 3 % surtax: dividends of a large holder face 25 + 3 + 2 = 30 %. Scanner METR with dividends: 62,4 % peak.

### F3 Credit points for children depend on the parent's sex
- kind: observation (statute)
- status: statutory; convention stated

s. 66(ג)(4)/(5): a mother gets 2 points per child aged 6-17 and ½ in the year of majority; a father 1 point for 6-17 and none at 18; equal points to age 5. The household's tax depends on which parent earns. The canonical household has no sex: defaults single = M, couple = M then F (`adult1Sex`/`adult2Sex` override).

### F4 Model gaps
- kind: model limitation
- status: open

NI/health ceiling (5 × the 2025 basic amount, לוח י״א) not reached: no ceiling, so METR above about 50.000 NIS a month is overstated by up to 12 points; the 2025 reduced band 7.522 NIS a month is inferred from s. 334(א) (the 2026 base). Pension exemptions (s. 9א), pension-contribution credits (s. 45א), rent tracks and child allowances not modelled.

## Round D2 (improvement agent, 2026-11-20): D1 dev failures settled from the statute

### D2-1 NI ceiling and child allowance from the NII's dated tables (model fix); reduced band confirmed
- kind: model-fix
- NII (btl.gov.il) "הסכום הבסיסי לחישוב קצבאות" (src/btl/d2/basic_amount.html, sha256 4c146a9f...): from 1.01.2025 "סכום
  בסיסי 3 ... וחישוב הכנסה מרבית לגביית דמי ביטוח" 10,139 -> NI Law s. 348 (א) with לוח י״א: ceiling 5 x 10,139 = 50,695 a
  month (was: no ceiling); child allowance (s. 66-68) 169 for the first and fifth+ child, 214 for the second to fourth,
  a month. "שכר ממוצע לפי סעיפים 1 ו-2" (src/btl/d2/avg_wage.html, sha256 67bbb69c...): from 1.01.2025 s. 2 average wage
  for contributions 12,536 (0.0 %): 60 % = 7,522, confirming the reduced band (F4's inference closed). #guards.
- Dev: TW 2025 62 / 68 -> 69 / 77 (of 80): two-child households' CTGG 4,596 now equal; Tax DB SSC 0 / 3 -> 0 / 5 (the
  4,194,707 case: 66,900 vs 66,904); Tax DB rates 36 / 44 -> 37 / 45; Tax DB PIT 5 / 14 -> 5 / 15. Remaining: SP67
  CTGG 6,948 vs 4,596 (the single parent's further amount, probably the study grant מענק לימודים: not modelled), a few
  NIS of monthly rounding on EECSSC, and TaxBEN METRs (benefit withdrawal TaxBEN models; not representable).
- Lean: IlTax.niCeilingMonth, childAllowance, employeeContrib (#guards)
- status: model changed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| S1 | explained | Wikisource text contradicts its table: source anomaly. |
| F1 | explained | Indexation frozen 2025-2027: statute (fiscal drag). |
| F2 | explained | 2 % capital surtax: statute. |
| F3 | explained | Children's credit points by the parent's sex: statute design (s. 66); known (the Tax Authority's own guidance describes the mother's points). |
| F4 | explained | Model limits. |
| D2-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch; split gain 74,405 with two children = F3 (points follow the mother) plus individual taxation. |

<!-- L1-VERIFICATION END -->
