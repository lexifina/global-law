# Nauru (NR) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The employment tax is final for each pay period with no annual reconciliation: $120,000 paid in one month costs $22,152, paid evenly $1,824
- kind: statute-fault
- ESTA s 11(1) 'imposed for each pay period', (3) on 'the gross amount of employment income of the employee for the period'; s 14(a) 'the tax is a final tax'. A bonus, back-pay or a contract paid in a lump loses eleven months of the $9,240 band (#guard: 22,152 vs 1,824). The annual timing scanner spreads pay evenly and cannot see this (B08/B10 lesson).
- provisions: ESTA ss 11, 14, Schedule (1)
- Lean: NrTax.periodTaxCents (#guard)
- status: modelled

### F2 The three printed pay-period bands are three different annual allowances: $110,880 monthly, $110,682 fortnightly, $110,708 weekly
- kind: statute-fault
- Schedule (1)(a)-(c): 9,240 x 12 = 110,880; 4,257 x 26 = 110,682; 2,129 x 52 = 110,708 (#guard). At $120,000 a year a fortnightly-paid employee pays $39 more than a monthly-paid one (#guard); employer choice of pay frequency changes the tax.
- provisions: ESTA Schedule (1)
- Lean: NrTax.residentTax (#guard)
- status: modelled (input payPeriod)

### F3 The consolidated Superannuation Act prints the 2026 employer rate (10 %); in 2025 it was 5 %
- kind: gov-error
- Naoero Superannuation Act 2018 Schedule 1 in the RONLAW/Global law text: 'Employer contribution rate - 10%' with the note 'am Act 49 of 2025 s 6, opn 1 Feb 2026'; Act 49 of 2025 s 6 'deleting 5% and substituting with 10%' and s 2 'commences on 1 Febuary 2026' (sic). A current-text reader gets 2025 employer costs wrong; the employee rate (5 %) is unchanged. Only the history note reveals it.
- provisions: NSA 2018 Sch 1; Act 49 of 2025 ss 2, 6
- Lean: NrTax.superRate (employee 5 %)
- status: recorded

### F4 Residents keep a $110,880 tax-free band; a non-resident employee pays 20 % from the first dollar unless employed by the Republic or a State-owned enterprise (first $20,000 free)
- kind: loophole-known
- Schedule (2)(b)-(c); s 7 (residence by citizenship, refugee status or marriage to a citizen). Marriage to a resident citizen makes an employee resident (s 7(1)(c) as printed in the current text; Act 21 of 2026 amended s 7(1) from 12 May 2026 and the 2025 wording of (c) was not seen): worth 20 % of up to $110,880 a year.
- provisions: ESTA s 7, Schedule (2)
- Lean: NrTax.nonResidentTax
- status: modelled (inputs resident, nrCategory)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay wages evenly (or monthly rather than fortnightly) to use every period's band | recreated: #guard (bunching, period choice) | ESTA ss 11, 14, Schedule (1) |
| K2 | Receive investment income (interest, dividends, rent): outside the Employment and Services Tax Act | recreated: income-type scanner +21 % (other tax acts not read) | ESTA preamble, ss 11-12 |
| K3 | Residence by marriage to a citizen (s 7(1)(c)) turns 20 % flat into a $110,880 band | recreated: input resident | ESTA s 7(1)(c), Schedule |
| K4 | Exemption by Cabinet-approved agreement provisions gazetted by name (s 13(1)(d)) | not modelled: gazetted per person | ESTA s 13(1)(d) |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 110,880, the monthly band x 12)
- #guard on the three period bands, bunching and the superannuation rate
- Global law history notes on the ESTA Schedule and the Superannuation Act Schedule 1; RONLAW API (POST-free GET /api/pdf/latest/<year>/any/acts/any/50) listing of 2022-2026 acts for tax and superannuation amendments

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | model-proved | 20,328 AUD: 120,000 paid in one month costs 22,152, evenly 1,824. Model #guard (build); not expressible with the even-month contract. Evidence: model Lean: NrTax.periodTaxCents (#guard). Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | statute-fault | confirmed | 39 AUD at 120,000 (fortnightly vs monthly). exe and #guard L1NR.F2. Evidence: exe + Lean `L1NR.F2` (`world/loopholes/rest/lean/L1NR.lean`, 1 #guard): it(b)-it(a) = 39; statute re-read: `law/gl_esta2014.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | gov-error | explained | Consolidation prints 2026 rate. |
| F4 | loophole | confirmed | 22,176 AUD at 110,880 (resident band vs 20 % flat). exe and #guard L1NR.F4. Evidence: exe + Lean `L1NR.F4` (`world/loopholes/rest/lean/L1NR.lean`, 1 #guard): it(b)-it(a) = 22176; statute re-read: `law/gl_esta2014.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/NR.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= K2).
