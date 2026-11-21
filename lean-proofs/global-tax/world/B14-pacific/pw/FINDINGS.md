# Palau (PW) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Citizens earning $15,000 or less get all wage tax back; at $15,001 they keep none of it: a $1,180 cliff (METR 1,583 % on the scanner grid)
- kind: statute-fault
- 40 PNC 1104 (RPPL 11-11 s 5): 'If it is shown upon application by an employee who is a citizen of the Republic that the employee earned fifteen thousand dollars ($15,000) or less in a tax year, then the Director shall refund ... the entire amount of tax withheld'. 15,000 -> 0; 15,001 -> 1,180 (#guard). Scanner notch 1,179 at 1.0 x scale for singles, second earners and two-earner couples.
- provisions: 40 PNC 1101, 1104
- Lean: PwTax.person (#guard)
- status: modelled; scanner reproduces

### F2 The refund needs an application and 'earned' is undefined: whether non-wage income counts toward $15,000 is a reading
- kind: statute-fault
- § 1104 refunds 'upon application' to a citizen who 'earned' $15,000 or less; § 1101 taxes only wages and salaries. The model counts wages (the tax base) and assumes the refund is claimed.
- provisions: 40 PNC 1104
- Lean: PwTax.person
- status: documented reading

### F3 Non-citizen employees pay from the first dollar, citizens below $15,000 nothing: the refund is a citizenship test on the same wage
- kind: loophole-known
- § 1104 'an employee who is a citizen of the Republic'; non-citizen at 15,000 pays 1,180 (#guard).
- provisions: 40 PNC 1104
- Lean: PwTax.person (input citizen)
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Keep a citizen's annual wages at or below $15,000 (or split pay with a spouse) to get the whole tax back | recreated: notch and filing-unit scanners | 40 PNC 1104 |
| K2 | Tuition and donations to approved bodies refunded up to 10 % of tax | not modelled: needs inputs | 40 PNC 1104 |
| K3 | Investment income untaxed for individuals under the wage tax | recreated: income-type scanner (Business Profits Tax not modelled) | 40 PNC 1101 |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 15,000, the citizen refund limit)
- #guard on the bands and the refund edge
- Internet Archive CDX listing of palaugov.pw/wp-content/uploads for RPPLs 2018-2025 (no later wage-tax amendment found)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round D6 (improvement agent, 2026-11-20): holdout gaps checked against the statute (aggregates only)

### D6-1 Wage-tax bands for 2025 confirmed (RPPL 11-11); no change
- kind: test-note
- 40 PNC § 1101 as amended by RPPL No. 11-11 s. 5 (the Palau Tax Reform Act that also created the PGST), effective 1
  January 2023 (s. 21 (a)): "six percent (6%) upon the first eight thousand dollars ($8,000), ten percent (10%) upon the
  amount over the first eight thousand dollars ($8,000) but not over forty thousand dollars ($40,000), and twelve percent
  (12%) upon the amount over ... ($40,000)". No later amendment found (palaugov.pw uploads, Global law). The model's
  bands are these; § 1104's citizen refund at $15,000 or less is an annual refund on application, which a withholding
  table does not show.
- On the D6 gap (model lower on 11 of 15 by a median of 2,4 %): in monthly terms band b is 10 % of the amount over
  $666,67 up to $3 333,33, i.e. at most $2 666,67 of wages, the reading the test agent quoted; the statute gives no
  other band structure. With the cases sealed the gap cannot be traced further here: either the table's Table IV formula
  differs from § 1101 (then a withholding convention, which would need BRT's published method to flag) or the
  conversion. For the test agent: check how the converted cases treat band b and whether citizen status is set
  (the model defaults to citizen with the § 1104 refund).
- status: open (no statute change)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 1,180 USD for one dollar above 15,000 (citizens). exe and #guard L1PW.F1; re-found by the fresh scan (1,583 %). Evidence: exe + Lean `L1PW.F1` (`world/loopholes/rest/lean/L1PW.lean`, 1 #guard): it(b)-it(a) = 1180; statute re-read: `law/RPPL-11-11.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | reading | explained | Reading. |
| F3 | fact | model-proved | exe and #guard L1PW.F3: non-citizen pays 1,180 at 15,000. Evidence: exe + Lean `L1PW.F3` (`world/loopholes/rest/lean/L1PW.lean`, 1 #guard): it(a) = 1180. |
| D6-1 | record | explained | Record (test-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PW.json`): METR 1,583 %, notches 1,179 and timing 1,180-1,858 = F1 (couple multiples).
