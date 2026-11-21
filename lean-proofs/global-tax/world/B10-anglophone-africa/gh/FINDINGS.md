# Ghana (GH) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Act 1111's 'Next' amounts add up to GH¢605,000 while its top row starts at 'Exceeding GH¢600,000'
- kind: statute-fault
- Act 1111 First Schedule para. 1(1): First 5,880 + 1,320 + 1,560 + 38,000 + 192,000 + 366,240 = 605,000 (page image checked); row 7 'Exceeding GH¢600,000 | 35 per cent'. Chargeable income between 600,000 and 605,000 is in both the 30 % and the 35 % row. Reading the chain of 'Next' amounts, 35 % starts at 605,000; reading row 7, at 600,000 (model default, input gh1111Reading=next for the other). The difference is 5 % of 5,000 = GH¢250 for everyone above 605,000 (exe gh-700k 184,770 vs 184,520). Act 1094 (2023) summed exactly to 600,000; Act 1178 (2026, GRA notice) again sums to 600,000 (7,056 + 960 + 1,200 + 34,800 + 192,000 + 363,984).
- provisions: Act 896 First Schedule para. 1(1) as substituted by Act 1111 s. 1
- Lean: GhTax.schedExplicit, GhTax.schedChain (#guard sums 605,000 / 600,000; 250 difference)
- status: statute fault; model reading documented

### F2 A dependent spouse who starts to earn one cedi costs the household the GH¢200 relief: a notch of up to GH¢70
- kind: loophole-new
- Fifth Schedule para. 1(a): relief of 200 currency points (cedis) for 'a dependant spouse or at least two dependant children'; para. 3: dependant = one 'for whom that individual provides the necessities of life'. Modelled as a spouse with no income; exe: married, earner 60,000, spouse 0 -> tax 9,307; spouse earns 1 -> 9,357 (+50 at the 25 % rate; up to 70 at 35 %). With two children the relief stays (the 'or' test).
- provisions: Act 896 s. 51, Fifth Schedule paras. 1(a), 3
- Lean: GhTax.out (spouseDependant)
- status: modelled; second-earner scanner

### F3 The reliefs are fixed in currency points (= cedis) unchanged since 2015 while the zero band was raised by Acts 1094 (4,824) and 1111 (5,880)
- kind: statute-fault
- Fifth Schedule (200 currency points) vs the bands rewritten by Acts 1094 (2023) and 1111 (2023): reliefs worth at most 200 x 35 % = 70 cedis a year. No amending Act read changes the Fifth Schedule (Acts 1071, 1094, 1111, 1134, 2021, and Global law's 902-973).
- provisions: Act 896 Fifth Schedule; Acts 1094, 1111
- Lean: GhTax.reliefFamily
- status: recorded

### F4 SSNIT contributions are tax-free (Act 766 s. 89(1)); employer contributions up to 13.5 % of salary are not taxed (s. 89(3))
- kind: model-fix
- Statutory top combined rate on wages 35 % x 0.945 + 5.5 % = 38.6 % (scanner 38.7 % with rounding).
- provisions: Act 766 ss. 3, 89
- Lean: GhTax.person
- status: modelled; scan reproduces

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Education relief: 200 cedis per child in a registered school, up to three | recreated: input childrenInSchool | Fifth Schedule para. 1(d) |
| K2 | Old-age relief at 60 | recreated | Fifth Schedule para. 1(c) |
| K3 | Training costs relief up to 400 cedis | not modelled | Fifth Schedule para. 1(f) |
| K4 | Voluntary pension contributions (third tier) tax-exempt | not modelled: only the 5.5 % mandatory | Act 766 s. 89(1) |
| K5 | Shift income to a spouse (individual taxation) | recreated: split gains | Act 896 s. 2 |

## Step 5: what was searched

- kernel scanners with scale 600,000 (Act 1111 top threshold)
- second-earner check of the dependant-spouse relief
- all amending Acts listed by GRA and in the Parliament repository searched for First and Fifth Schedule changes

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S-1 Odoo-19-Ghana-Localization: SSNIT cap applied to the year (W5 review pass 2, 2026-11-20)
- kind: software-error
- `gh_open_odoo19_ghana_localization_imadeit66_grid`: the module caps SSNIT at 61,000 a year (3,354.96 = 5.5 % x 61,000); the 2025 maximum insurable earnings is 61,000 a month, and Act 766 s. 3 (1) charges 5.5 % of salary below it. Its PAYE base (basic - SSNIT) follows.
- status: recorded (world/IMPROVE_W5.md pass 2)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/GhTax/Verify.lean` (imported by the `GhTax` library and built; each guard evaluates `GhTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/GH.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | 600,000 vs 605,000 top band: reading (input gh1111Reading). |
| F2 | confirmed | The GH¢200 relief for 'a dependant spouse' ends at her first cedi: tax +50 (a notch of up to GH¢70 at the 35 % rate). G: f2_spouse_relief. S: law/act896_ocr.txt:6812 (Fifth Schedule para. 1(a): 'in the case of an individual who has a dependant spouse or' [at least two dependant children]). Lead: PwC's Ghana summary gives this relief as GHS 1,200 (an amendment the batch did not find, FINDINGS F3); if so the notch is up to GHS 420. Not changed (statute not on disk). |
| F3 | explained | Reliefs frozen since 2015: statute fault. |
| F4 | explained | SSNIT tax-free: model fix. |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan marriage bonus 70 = F2; wedges are model gaps. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: The GH¢200 relief for a dependant spouse ends at her first cedi | second-earner trap | **unclear**: PwC Ghana gives the relief for 'an individual with a dependent spouse or at least two dependent children' as GHS 1,200, not the Fifth Schedule's 200 currency points: if 1,200 applies, the notch is up to GHS 420, and the model (and FINDINGS F3) may be missing an amendment; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'Ghana marriage responsibility relief dependent spouse GH 200'; 'Ghana personal reliefs income tax Act 896' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (ghana, 5 individual pages): 3 passages with the item's terms; Crossref IMF prefix 10.5089 'Ghana personal income tax reliefs' (2509 records, titles only). Record: world/loopholes/africa_mena/search/GH-F2.json |

<!-- L1-VERIFICATION END -->
