# Madagascar (MG) findings, B08-central-africa-fr (2026-11-20T04:05Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Every salary pays at least Ar 3 000 a month: an entry cost of 36 000 a year and a flat tax up to about 410 000 a month
- kind: statute-fault
- art. 01.03.16: the tax 'sans toutefois être inférieur à Ar 3000'. Below 350 000 a month the bands give 0 but 3 000 is due; the minimum binds up to about 410 000 a month (where 5 % above 350 000 reaches 3 000). The scanner reports a 36 000 notch at the first ariary of wages (METR 100 % / 200 % for two earners).
- provisions: CDI art. 01.03.16
- Lean: MgTax.irsaMonth (#guard 300 000 -> 3 000)
- status: modelled; scan reproduces

### F2 The dependants' reduction is worth nothing to low earners: the minimum absorbs it
- kind: statute-fault
- art. 01.03.19: Ar 2 000 a month per dependant, only if the base exceeds 350 000, and never below the minimum. At 400 000 a month the tax is 3 000 with or without two children (2 500 - 4 000 < 3 000) (#guard); the reduction only helps from about 410 000 + 2 000 x dependants / 5 %.
- provisions: CDI art. 01.03.19
- Lean: MgTax.irsaMonth (#guard)
- status: proved by #guard

### F3 Monthly tax without annual reconciliation: uneven pay costs more
- kind: loophole-known
- arts. 01.03.11, 01.03.16: the IRSA is computed on each month's base; nothing reconciles the year (art. 01.03.13 only for several employers). A bonus month is taxed at 20 % while a smooth wage of the same total stays in lower bands. The generic timing scanner works on annual totals spread evenly, so it does not see this; its largest two-year gain (36 000 = 0.5 % of the scale wage) comes from the Ar 3 000 minimum (F1): income bunched into one year escapes a year of minimums.
- provisions: CDI arts. 01.03.11-01.03.16
- Lean: MgTax.person
- status: modelled

### F4 2025 is the last year of the 20 % top rate
- kind: model-fix
- The CDI 'LFI 2026' adds 'tranche de revenu supérieure à Ar 4 000 000 : 25p. 100'; the 2025 text stops at 20 % above 600 000.
- provisions: CDI art. 01.03.16 (LFI 2025 vs LFI 2026)
- Lean: MgTax.sched
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Overtime up to 20 hours exempt | not modelled | CDI art. 01.03.03 9° |
| K2 | Benefits in kind valued low: company car 15 % of running costs, housing 50 % of rent capped at 25 % of cash pay, phone 15 % | not modelled | CDI art. 01.03.08 |
| K3 | Retirement indemnity up to one year's salary exempt | not modelled | CDI art. 01.03.03 7° |
| K4 | Give the dependants' reduction to the spouse for whom it is worth more | recreated: an election in the model | CDI art. 01.03.19 |
| K5 | Smooth pay across months (monthly tax) | not modelled: F3: the annual timing scanner cannot see monthly bunching | CDI art. 01.03.16 |
| K6 | Majority managers of SARL: remuneration exempt from IRSA (taxed under IR instead) | not modelled | CDI art. 01.03.03 6° |

## Step 5: what was searched

- kernel scanners via scan_world.py (scale 7.2 M = 600 000 x 12, art. 01.03.16 band)
- IRSA text 2025 vs 2026 compared
- minimum vs dependants (#guard)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (CM CG CD MG among the covered countries)
- IMF Article IV and technical-assistance reports on the CEMAC members, DRC, Madagascar, Burundi, Djibouti, Comoros
- CEMAC directives on the harmonisation of direct taxation (IRPP/IS) and the CIMA/CIPRES social-security rules
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- droit-afrique.com and juriafrique compilations (droit-afrique answered 403 to scripts and the laptop; not bypassed)
- Academic work on family quotients in francophone Africa and on informal-sector minimum taxes

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5R sweep P2-6: household-total employee-contribution input allotted by wages (W5 review pass 2, 2026-11-20)
- kind: model-fix (cross-country sweep from NI W5R-1)
- The optional household-total employee-contribution input was halved between two adults, so a one-earner couple
  deducted half of the earner's own contributions. The deduction provision this model already cites deducts each
  employee's own contributions from that employee's income; the total is now allotted in proportion to wages (halves
  only when nobody has wages). Checked on 400 random households: outputs change only for two adults with the input and
  unequal wages. Script: world/w5/review2/sweep_alloc.py. Rescanned (scan_world.py).
- status: model changed

### W5S-1 payroll_africa (Madagascar): 25 % and 30 % IRSA bands and a 2,000 minimum (W5 review pass 2, 2026-11-20)
- kind: software-error
- `mg_open_payroll_africa_grid`: calculators/madagascar.py taxes 800,001-1,000,000 a month at 25 % and above 1,000,000 at 30 %, with a minimum IRSA of 2,000 a month applied only when the tax is positive; the CDI 2025 barème (art. 01.03.16, the MG model) stops at 20 % above 600,000 and its minimum is 'Ar 3000'. The app is far above the model at high wages.
- status: recorded (world/IMPROVE_W5.md pass 2)

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary (ceiling rule: code text))
- provisions: Code de prévoyance sociale art. 37 (8 x SME of category M1; CNaPS copy); rate from the CNaPS "Taux des cotisations" page (2011 capture: Général 13 % / 1 %), SME 262 680 (1 Mar 2024 - 28 Feb 2026) from the CNaPS SME table: official secondary
- CNaPS worker 1 % of wages up to 8 x SME (Ar 2 101 440 a month in 2025), deducted within the 10 % pension limit (art. 01.03.09 1°); input cnapsEmployee still overrides. Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: CNaPS SME floor (CPS art. 37) and the health-organisation (SMIE) worker share not modelled. Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/MgTax/Verify.lean` (imported by the `MgTax` library and built; each guard evaluates `MgTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/MG.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | IRSA never below Ar 3,000 a month: 12 Ar of annual pay costs 35,988 of net; the minimum binds to about 410,000 a month. G: f1_minimum_3000_month. S: law/cdi_lfi2025.raw.txt:2093 (art. 01.03.16: '... sans toutefois être inférieur à Ar 3000'). |
| F2 | confirmed | The dependants' reduction is absorbed by the minimum: at 400,000 a month two children change nothing. G: f2_dependants_absorbed. S: art. 01.03.19 with :2093. |
| F3 | explained | Monthly IRSA without reconciliation: rescan timing_monthly 973,094 at 1 'AW' in one month; same mechanism as DJ F1 (not separately guarded). |
| F4 | explained | 2026 top rate: record. |
| W5R P2-6, W5S-1, W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan first-unit notch 35,999 = F1. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: IRSA never below Ar 3,000 a month: an entry cost and a flat tax to about 410,000 a month | cliff or notch | **known**: PwC Madagascar: 'In all cases, regardless of the income, the minimum salary income tax payable is MGA 3,000'. | 2026-11-20: OpenAlex specific queries 'Madagascar IRSA minimum de perception 3000 ariary'; 'Madagascar wage tax IRSA minimum tax low earners' (13 hits, titles checked); OpenAlex broad 'Madagascar personal income tax', 'Madagascar income tax wages', 'Madagascar tax system reform' (75 records, titles and abstracts grepped, 3 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (madagascar, 5 individual pages): 12 passages with the item's terms; Crossref IMF prefix 10.5089 'Madagascar tax policy' (8379 records, titles only). Record: world/loopholes/africa_mena/search/MG-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 3.5063 AW (contribution rate 1.0 -> 0.0 %, combined marginal 21 -> 20 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
