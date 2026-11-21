# Zambia (ZM): findings, B09 build phase (2026-11-20T06:18Z)

Zambia built from the amending Acts (consolidated Act not reachable): 0 % to K61 200 a year, 20/30/37 % above, unchanged for 2025 by Acts 22/2024 and 10/2025; contributions sit in regulations not reached (grade B).

Scale for scanner numbers: 110,400 ZMW = threshold of the top (37 %) band (Income Tax Act Cap. 323 Charging Schedule para 2 (1) (f) as amended by Act 22 of 2023 (unchanged for 2025)); a statutory threshold, not an average wage.

### F1 Rental income is taxed on turnover at 4 % while wages pay up to 37 %
- kind: loophole-known
- Charging Schedule para 5 (e) as substituted by Act 22 of 2024: rental turnover 0 % to K12 000, 4 % to K800 000, 16 % above. The model puts rental income in the wage bands and flags it unsupported; the scanner's +14.6 % 'rental' gain is the model's own band effect, not this regime.
- provisions: Charging Schedule para 5 (e)
- Lean: ZmTax.out (unsupported flag)
- status: catalogued, not modelled

### F2 The consolidated Income Tax Act is not publicly reachable by script
- kind: gov-error
- ZambiaLII serves the Act as consolidated to 1996 and its document pages answer a Cloudflare challenge to every host; Parliament publishes only the amending Acts. Items (a)-(b) of para 2 (1) could not be read; item (c) is the zero band (Act 1 of 2008 cross-reference).
- provisions: Charging Schedule para 2 (1)
- Lean: -
- status: access

### F3 Scanner gains for interest, dividends and capital gains are model artefacts
- kind: model-fix
- The model marks them unsupported (Second Schedule exemptions and WHT rates not reached); income_type shows +31.8 % at 5 x scale only because they enter no tax. Not a loophole.
- provisions: -
- Lean: ZmTax.out
- status: listed

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- rental income under a 4 % turnover tax (para 5 (e)): not modelled
- minimum alternative tax 1 % of turnover (s. 14A, Act 10/2025) for businesses: not modelled
- final withholding on interest and dividends: not modelled
- turnover tax for small businesses (K5 m): not modelled
- progressive bands with no personal credit: recreated

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.3768, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.3768, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.3478, "netIncomeFalls": 0}}
- `world/tools/scan_world.py ZM` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- NAPSA and NHIMA contributions
- Charging Schedule para 2 (1) items (a)-(b)
- interest/dividends withholding
- rental turnover tax (para 5 (e))
- approved fund deduction

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: NAPSA public notice "Revision in Contribution Ceiling for the Year 2025" (7 Jan 2025): employee max 1,708.20, rate 10 % (5 + 5), NAE 8,541
- NAPSA employee 5 % of gross earnings up to ZMW 34,164 / month (max 1,708.20); not deducted for tax (ITA s. 37 not reached). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | Rental turnover tax 4 % (para 5 (e)): not modelled; the rescan's rental wedge is the model's own band effect. |
| F2 | explained | Consolidated Act not reachable: access record. |
| F3 | explained | Interest/dividend/gains wedges are model artefacts (unsupported). |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan timing gain 1,583 = NAPSA ceiling; no notch. |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 3.7179 AW (contribution rate 5.0 -> 0.0 %, combined marginal 42 -> 37 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
