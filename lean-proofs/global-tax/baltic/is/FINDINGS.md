# Iceland (Reykjavík), income year 2025: findings

Model: `lean/IsTax` on the shared kernel `TaxKernel` (exe `istax`, contract JSONL). Parameters and sources:
`refs/PARAMS.md` (P1-P23). Theorems: `lean/IsTax/Theorems.lean` (38, no `sorry`). Validation files: `validation/`
(RSK calculators, published figures, OECD statute run), `results/oecd_check.*` (kernel harness). Scans:
`results/search/` (kernel's generic scanners via `baltic/harness/b38.py`), `results/is_scans/` (Iceland-specific:
`harness/scan_is.py`, `harness/scan_owner_is.py`). Known-loophole catalogue: `CATALOGUE.md`.

Novelty wording: "not found in the sources read" means the official Icelandic pages and statute editions listed in
`CATALOGUE.md` (Sources) plus 2 web searches; the search budget was 3 searches, so novelty claims are weak.

## Validation (summary)

| Referee | Cases | Exact | Within 1 % | Notes |
|---|---|---|---|---|
| OECD Taxing Wages 2025, ISL, 8 family types x 6 lines (CGTC, CGITLETC, CGITFP, SLT, EECSSC, CTGG), OECD conventions (`oecd_map.py`) | 48 | 48 | 48 | after switching to half-up rounding (P23). OECD conventions: útsvar at the 14,94 % average, levies at the álagning-2025 amounts, whole credit booked against central tax. Take-home pay from the mapped lines: 8/8 within 1 %, 7 exact, 1 off by 2 kr. |
| OECD 2025 take-home pay vs istax statute default (Reykjavík 14,97 %, levies of income year 2025) | 8 | 0 | 8 | gaps -3.720 to -9.804 kr., each fully decomposed (residual <= 1 kr.) into útsvar 0,03 % of taxable income and the levy amounts (1.321 kr. per adult): F5, F6. `validation/published_and_oecd.json` |
| RSK barnabætur calculator (reiknivelarws.rsk.is, tekjuár 2025) | 26 | 26 | 26 | couples/singles, 1-5 children, 0-3 under 7, incomes 0-25 M incl. rounding edges; established the half-up rounding and the single rounding of the under-7 reduction. The calculator does not apply the 5.000 kr. per-carer lapse (3 cases, F8): compared before the lapse. |
| RSK staðgreiðsla calculator (2025, January) | 14 | 13 | 14 | 1 case (4 % séreign, 700.000 kr.) differs by 1 kr. in the calculator's tax before credit; not explained. |
| Published figures (Stjórnarráðið 20.12.2024 skattleysismörk 2.617.618 / launa 2.726.686; Skatturinn levy table álagning 2026; útvarpsgjald 22.200; barnabætur table) | 5 | 5 | 5 | `validation/published_and_oecd.json` |

## Statute faults and readings (versioned law)

### F1 lög 4/1995 23. gr. points to a minimum in "2. mgr. 67. gr." of the tax act that is not there
- kind: statute-fault (reference not updated)
- households: children under 16 with their own wage income (the 2 % útsvar on children's income)
- text (editions 156b and 158a): "Útsvar af þeim tekjum barna, sem um ræðir í 2. og 3. mgr. 64. gr. laga nr. 90/2003,
  um tekjuskatt, skal vera 2% af tekjum umfram það lágmark sem tilgreint er í 2. mgr. 67. gr. sömu laga." 67. gr. 2. mgr.
  of lög 90/2003 is about how the personal credit is spent; it names no amount. The children's minimum (180.000 kr.
  for 2025, "[180.000 kr.]" by L. 139/2013; 300.000 kr. from 2026) is in 66. gr. 2. mgr. ("4% af tekjum umfram
  [180.000 kr.]").
- amounts: none in practice (Skatturinn applies 6 % = 4 % + 2 % above the same 180.000 kr.: Staðgreiðsla 2025
  "Skatthlutfall barna ... 6% (4% tekjuskattur, 2% útsvar) af tekjum umfram frítekjumark barna sem er 180.000 kr."),
  but the municipal rule rests on a reference to a paragraph that does not say it. The 2026 change of the minimum
  (Stjórnarráðið 23.12.2025) left the reference as it was (edition 158a).
- provisions: lög 4/1995 23. gr. 2. málsl.; lög 90/2003 66. gr. 2. mgr., 67. gr. A 2. mgr.
- Lean: none (a text fault).
- status: certain that the cited paragraph holds no minimum; the origin (likely the numbering of the earlier tax act
  75/1981) is unverified, because the codex mirror starts at edition 153c.

### F2 67. gr. A tests the credit against the tax "skv. 1. tölul. 1. mgr. 66. gr.": since 2009 that is the first band only
- kind: statute-fault (reference not updated after renumbering; no effect in 2025)
- households: all
- text: 67. gr. A 2. mgr. "Nemi persónuafsláttur skv. 1. mgr. hærri fjárhæð en reiknaður tekjuskattur af
  tekjuskattsstofni skv. 1. tölul. 1. mgr. 66. gr. ..." (twice). L. 128/2009 made 1.-3. tölul. the three bands;
  L. 165/2010 updated 66. gr. 6. tölul. to "[1.-3. tölul.]" but 67. gr. A kept "1. tölul.".
- amounts: read literally, the credit is compared with first-band tax only. In 2025 a full first band costs
  937.403 kr. > 824.288 kr. of credit, so the literal and intended readings give the same tax for everyone.
- provisions: 66. gr. 1. mgr. 1.-3., 6. tölul.; 67. gr. A 2. mgr.
- Lean: `firstBandTax_gt_credit` (`stateTax T1 > persCredit`).
- status: certain; harmless while 16,55 % x T1 exceeds the credit (both are indexed alike).

### F9 67. gr. A: does a single person's unused credit pay capital income tax? (reading)
- kind: statute-fault (classification: reading)
- households: single people with little earned income and capital income
- text: "Sá persónuafsláttur, sem þá er enn óráðstafað, fellur niður nema um sé að ræða óráðstafaðan persónuafslátt
  annars hjóna ... Af þeim persónuafslætti sem þá er óráðstafað skal [22/31] hlutum ráðstafað til að greiða tekjuskatt
  sem lagður er á fjármagnstekjur". Literally a single's leftover lapses before the 22/31 sentence; Skatturinn
  (Persónuafsláttur page) applies 22/31 to everyone's leftover ("Sé enn eftir ónýttur afsláttur ganga 22/31 ...").
- amounts: a single person with no earned income and 2.958.990 kr. of interest: 0 kr. capital income tax (practice,
  the model's default) vs 584.978 kr. (literal; option `--literal-67A`). `results/is_scans/is_scans.md` B.
- provisions: 67. gr. A 2. mgr.; 66. gr. 3. mgr.
- Lean: `capital_free_single`.
- status: the tax authority uses the generous reading; the text supports both. Moot from 2026 (L. 99/2025 31. gr.
  removes the 22/31 sentence).

### F15 Barnabætur 2025: amounts frozen by moving a year in a temporary provision
- kind: statute-fault (amounts not updated while related amounts were indexed; deliberate)
- households: all families with children in the withdrawal band
- text: brbákv. LXXXII (L. 127/2024 29. gr.) set barnabætur "við álagningu opinberra gjalda á árinu 2025" (income
  year 2024); L. 99/2025 34. gr. replaced "2025" with "[2026]". So income year 2025 has the same 345.000 / 514.500 /
  130.000 kr. and thresholds 11.688.000 / 5.844.000 kr. as 2024, while the tax bands and the credit rose 5,80 %
  (Stjórnarráðið 20.12.2024) and the OECD average wage 5,3 %. (Stjórnarráðið 23.12.2025: "reiknireglur og
  viðmiðunarfjárhæðir barnabóta verða þær sömu á árinu 2026 og á árinu 2025".) For versioned law: the consolidated
  text (158a) no longer shows the rule that governed the 2025 assessment; it now reads as a 2026 rule.
- amounts: against thresholds indexed like the bands, families lose 19.854 kr. (OECD couple, 1 AW, children 6 and
  10) to 27.116 kr. (couple 1 + 0,67 AW; couple 2 x 1 AW; single parent 0,67 AW). `is_scans.md` F.
- provisions: 68. gr. A 4. mgr.; brbákv. LXXXII; L. 99/2025 34. gr.
- Lean: none.
- status: certain; a policy choice, recorded because barnabætur are the only income-tested amounts not indexed by
  statute.

## Government publications

### F5 The OECD's 2025 row uses the levies of the 2025 assessment (income year 2024)
- kind: gov-error (OECD model; stale relative to its own series)
- households: every adult aged 16-69 above the levy floor (all eight OECD types)
- text: the two flat levies of an income year are assessed the following year at the amounts then in force (lög
  23/2013 14. gr.; 125/1999 10. gr.; Skatturinn: "Útvarpsgjaldið er lagt á ... í fyrsta skipti við álagningu ári eftir
  að 16 ára aldri er náð"; levy table "Í álagningu 2026 | 14.614"). The OECD's EECSSC (Framkvæmdasjóður aldraðra) for
  ISL is 13.284 (2022), 13.749 (2023), 14.093 (2024) and 14.093 (2025): 2022-2024 are the amounts assessed the next
  year, but 2025 repeats 14.093 instead of 14.614; its CGITFP likewise carries útvarpsgjald 21.400 in 2024 and 2025
  (22.200 assessed 2026). The 2026 amounts were enacted on 18 Dec 2025 (L. 99/2025), after Taxing Wages 2025 went to
  press.
- amounts: 800 + 521 = 1.321 kr. per adult (S100 take-home pay -4.902 kr. = -1.321 levies - 3.581 útsvar 14,97 vs
  14,94 %; all eight types decomposed to within 1 kr.).
- provisions: lög 23/2013 14. gr.; lög 125/1999 10. gr.
- Lean: `levies2025`, `leviesAssess2025` (both conventions in the model).
- status: certain; also a labelling convention (the ministry's own 20.12.2024 table lists 21.400 / 14.093 as
  "2025").

### F6 Withholding vs assessment (conventions)
- kind: gov-error (classification: convention)
- households: every Reykjavík taxpayer; every full-year employee
- amounts: withholding uses the 14,94 % average útsvar for everyone (Auglýsing 1665/2024); a Reykjavík resident owes
  0,03 % of taxable income at assessment (3.581 kr. at the average wage). Twelve monthly credits of 68.691 kr. are
  824.292 kr., 4 kr. more than the year's 824.288 kr.; twelve monthly first bands are 5.664.060 kr., 2 kr. short of
  5.664.062.
- provisions: lög 45/1987 (staðgreiðsla); Auglýsing 1665/2024.
- Lean: `withholding_credit_excess`, `withholding_band_gap`.
- status: certain; small by design.

### F7 Auglýsing 1665/2024 omits the indexed cap of the spouses' band transfer
- kind: gov-error (omission)
- households: couples where one spouse's taxable income exceeds 15.901.523 kr.
- text: 66. gr. 1. mgr. 5. tölul.: "Fjárhæðarmörk tekjuskattsstofns skv. 1.-4. tölul. skulu taka breytingum ...
  Breytingarnar ... skal birta með auglýsingu". The 2025 notice gives the 1.-3. tölul. amounts but not the 4. tölul.
  cap (base 3.581.173 kr.). Indexed like the rest it is 5.118.730 kr., which is half the 2025 middle band
  (5.118.730,5).
- amounts: none if the cap is read as half the band; a reader of the notice cannot check it.
- provisions: 66. gr. 1. mgr. 4., 5. tölul.
- Lean: `cap_is_half_middle`, `bandShift_half_middle` (the transfer is half of the lower spouse's unused middle band;
  the cap binds exactly when the lower spouse is below T1), `bandShift_le_cap`.
- status: certain (notice text `refs/gov/auglysing_1665_2024.txt`).

### F8 RSK's barnabætur calculator shows amounts the statute does not pay; and the 5.000 kr. notch
- kind: gov-error (calculator) + notch
- households: families at the end of the withdrawal band
- text: 68. gr. A 7. mgr.: "Barnabætur sem eru ákvarðaðar lægri en [5.000 kr.] á hvern framfæranda ... falla niður."
  The calculator (tekjuár 2025) returns 520 kr. for a couple ("skiptast jafnt ... 260", "Til greiðslu í hverjum
  ársfjórðungi 65"), 4.520 kr. for a couple and 4.260 kr. for a single parent (cases bb06, bb08, bb14).
- amounts: a single parent of one child gets 5.000 kr. at 18.581.500 kr. and nothing 25 kr. later; a couple drops
  10.000 -> 5.000 -> 0 kr. within 50 kr. (the split of an odd króna is a model assumption).
- provisions: 68. gr. A 1., 7. mgr.
- Lean: `bb_min_notch`, `bb_min_notch_couple`.
- status: certain for the calculator output; small amounts. Draft note to RSK (not filed): "Reiknivél barnabóta
  sýnir fjárhæðir undir 5.000 kr. á framfæranda sem falla niður skv. 7. mgr. A-liðar 68. gr. laga nr. 90/2003."

### F13 The ministry's 2025 barnabætur table misstates the withdrawal rate
- kind: gov-error (text)
- households: families with two or more children
- text: Stjórnarráðið 20.12.2024, "Viðmiðunarfjárhæðir barnabóta 2025": "Skerðingarhlutfall með hverju barni | 4% |
  4%". The statute: "Skerðingarhlutfallið skal vera 4% með öllum börnum óháð fjölda þeirra" (only the under-7
  supplement is withdrawn "4% með hverju barni"). Read as written the table implies 8 % for two children; RSK's
  calculator applies the statute (26/26).
- provisions: brbákv. LXXXII.
- status: certain.

### F14 Stale and inconsistent figures on Skatturinn's pages (2026 and history)
- kind: gov-error (text)
- (a) Persónuafsláttur page: "Fjárhæð persónuafsláttar 2026 er samtals 869.904 kr." and the English table's December
  "869.904" (= 12 x 72.492), but the 2026 notice (Auglýsing 1521/2025) and the Staðgreiðsla 2026 page give 869.898 kr.
  ("Persónuafsláttur er 869.898 kr. á ári"), as does the Icelandic table's December row (869.898, which is not
  12 x 72.492). (b) Skattþrep 2026 page: "Fari mánaðarlaun yfir 498.122 kr. ..." but its worked example says "Fyrsta
  skattþrep nær upp að 472.005 kr." (the 2025 figure). (c) Vaxtatekjur page states as current "Ekki er greiddur
  fjármagnstekjuskattur af heildarvaxtatekjum að fjárhæð 150.000 kr." and then "Frá og með álagningu 2021 verður
  frítekjumarkið 300.000 kr." (future tense; the 2025 value is 300.000).
- status: certain (pages in `refs/sk/`); none changes a 2025 tax.

## Loopholes and high marginal rates found by the model

### F3 The levy cliff: one króna above 2.617.618 kr. costs 36.814 kr.
- kind: loophole-new
- households: anyone aged 16-69 whose tekjustofn (earned base + capital base) is at or just above 2.617.618 kr.
  (wages 2.726.685 kr.): students and summer workers, part-time workers, pensioners under 70 with small pensions.
- amounts: útvarpsgjald 22.200 + Framkvæmdasjóður aldraðra 14.614 = 36.814 kr. due in full from the floor (exempt if
  "lægri en" the floor). Generic METR scan: 161,8 % over the 0,002 AW step that contains it. Net income falls by
  36.814 - 68,48 % x d for d kr. above the floor, so over 53.759 kr. of taxable income (2.617.618-2.671.377) earning
  less leaves more. A 10.000 kr. gift to a registered charity (30. gr. A 7. tölul.) or 13.000 kr. into séreign at
  wages of 2.730.000 kr. removes the levies: total taxes 38.602 -> 0 kr. The floor sits exactly where income tax starts
  at the withholding rate (824.288 / 31,49 % = 2.617.618).
- provisions: lög 23/2013 14. gr.; lög 125/1999 10. gr.; lög 90/2003 30. gr. A 4., 7. tölul.
- Lean: `levy_notch` (general), `levies_cliff_2025` (36.814 at 2.617.618), `levy_floor_is_taxfree_point`.
- novelty: the floor is published; the cliff, the dominated band and the gift/séreign remedy were not found in the
  sources read.
- status: certain under the statute.

### F4 Barnabætur withdrawal stacks per child under 7: up to 54 % marginal rates for middle incomes
- kind: loophole-new (METR finding)
- households: families with children under 7 in the withdrawal band
- amounts: the basic amount is withdrawn at 4 % for all children together, the under-7 supplement at 4 % per child
  under 7, on the same income above the threshold. A single parent with three children under 7 loses 16 % of each
  extra króna between 5.844.000 and 9.094.000 kr. of income, on top of 38,02 % tax: 54,02 % of taxable income,
  51,87 % of wages (wages 6,2-9,3 M kr.); a one-earner couple with three under 7 the same from 12,4 to 15,5 M kr. of
  wages. The top statutory rate on wages is 44,47 %.
- provisions: 68. gr. A, brbákv. LXXXII.
- Lean: `bb_single_three_under7` (-4 kr. per 25 kr.), `bb_couple_two_one` (-8 per 100), `bb_base_antitone`,
  `bb_base_is_taper` (kernel `Taper`).
- novelty: not found in the sources read (the per-child rule is visible in the statute; its stacking with the middle
  band is not discussed there).
- status: certain.

### F10 The 22/31 rule: in 2025 people without earned income pay no tax on almost 3 M kr. of capital income
- kind: loophole-known (statutory, removed for 2026; quantified here)
- households: retirees or others living on capital income
- amounts: a single person with no earned income: 2.958.990 kr. of interest (300.000 exempt + 2.658.990 at 22 % =
  584.978 kr., paid by 22/31 of the 824.288 kr. credit); a couple with no earned income: 5.917.980 kr. The levies still
  apply from a capital base of 2.617.618 kr. (ages 16-69). Removed from income year 2026 (L. 99/2025 31. gr.;
  Stjórnarráðið 23.12.2025 "sú heimild felld brott að nýta megi afgangs persónuafslátt til greiðslu
  fjármagnstekjuskatts").
- provisions: 67. gr. A 2. mgr.; 66. gr. 3. mgr.
- Lean: `capital_free_single`.
- status: certain.

### F11 Inside the spouses' band transfer the second earner pays 4,15 points more
- kind: loophole-new (marriage METR; 2025 only)
- households: couples where one spouse earns more than about 21 M kr. (T3 + cap) and the other is in the middle band
- amounts: the band transfer (66. gr. 1. mgr. 4. tölul.) moves up to 5.118.730 kr. of the higher spouse's top-band
  income to 23,05 %: worth at most 8,30 % x 5.118.730 = 424.855 kr. a year (scan A). The room is half of the lower
  spouse's distance to T3, so once the higher spouse is above T3 + cap every 2 kr. the lower spouse earns in the middle
  band removes 1 kr. of transfer: the second earner's marginal rate is 42,17 % of taxable income instead of 38,02 %
  (40,49 % of wages instead of 36,50 %; measured for the partner of a 30 M kr. earner at 6,5-12 M kr. of wages). Below
  T1 the cap binds and the effect vanishes (30,26 %). Splitting still pays: a one-earner couple at 3 AW saves
  1.226.323 kr. a year by earning the same total 50/50, even after both transfers (the generic filing-unit scanner
  found the same 1.226.324 kr.).
- provisions: 66. gr. 1. mgr. 4. tölul.; 62. gr.; 67. gr. A.
- Lean: `shift_secondary`, `bandShift_half_middle`, `max_transfer_gain_ticks`, `pair_le_separate` (the transfer never
  costs), `shifted_le`, `transfer_never_costs`.
- novelty: not found in the sources read. Gone from 2026.
- status: certain.

### F12 Living apart with a shared-residence agreement pays up to 566.040 kr. a year more barnabætur
- kind: loophole-new (design: a couple penalty in barnabætur)
- households: parents with children; the comparison is a couple vs two parents living apart with a registered
  shared residence (skipt búseta)
- amounts: with shared residence each parent is assessed by his own family status and income and gets half; a single
  parent's amount is 514.500 kr. a child against 345.000 kr. for a couple. Two parents earning 6.000.000 kr. each with
  two children (4 and 9): as a couple 820.000 kr.; apart with shared residence 1.159.000 kr. (+339.000 kr.); at
  12.000.000 kr. each +566.040 kr. Taxes are otherwise the same (both below T3, no credit to transfer).
- provisions: 68. gr. A 1. mgr. (L. 28/2021: "takmarkast við helming af útreiknuðum barnabótum"); brbákv. LXXXII.
  The statute treats parents living together with their child as a couple whether or not they register ("Að sama
  skapi teljast þeir sem halda heimili saman ásamt barni sínu framfærendur ... eins og um hjón sé að ræða"), so the
  gain requires actually living apart; recording two addresses while living together would be evasion, not planning.
- Lean: `shared_residence_bonus`.
- novelty: not found in the sources read.
- status: certain under the statute (model input `sharedResidence`).

### F16 Owner-manager: salary to the first band, dividends above (known; recreated blind)
- kind: loophole-known
- households: a single owner of an ehf., all profit paid out
- amounts: the best salary is 5.900.065 kr. (T1 grossed up for the 4 % pension) with all further profit as
  dividends: 20 % corporate tax then 22 % with no exemption (unlisted) = 37,6 %, the same rate 71. gr. 2. mgr. sets for
  partnerships, against 46,32 % + 6,35 % tryggingagjald on salary in the top band. At 2 AW of profit the owner saves
  1.043.545 kr. against all-salary; with RSK's reiknað endurgjald minimum B(5) 10.392.000 kr. still 915.003 kr.; with
  A(6) 16.044.000 kr. 753.266 kr. (`results/is_scans/owner_is.md`). The kernel's generic owner scan found the same
  corner (best salary 5.845.569 kr. on its own company data).
- provisions: 7. gr. A 1. tölul. 2. mgr. and 58. gr. (reiknað endurgjald); 66. gr. 3. mgr.; 71. gr.
- Lean: `dividend_route_rate`.
- status: certain for the arithmetic; RSK can raise a reiknað endurgjald below its minima.

### F17 Timing: bunching income into one year keeps barnabætur in the other
- kind: loophole-new (generic scanner)
- households: families in the barnabætur withdrawal band with income they can time (bonuses, self-employed profit)
- amounts: barnabætur are tested on one year's income; bunching two years' income into one saves a single parent with
  two children 481.655 kr. (3,87 % AW) against smooth income of 32,8 M kr. a year; a one-earner couple 316.260 kr.
  (`results/search/timing.md`).
- provisions: 68. gr. A.
- Lean: `bb_base_antitone` (the shape); the amounts are from istax runs.
- novelty: generic; not found for Iceland in the sources read.
- status: certain under the model (two-year horizon, no discounting).

### F18 Model fixes made during validation
- kind: model-fix
- rounding to the nearest króna (not down) and a single rounding of the under-7 reduction, found from the RSK
  calculators (bb01: 9.927,92 -> 9.928; bb02: 2 x 52.480,52 -> 104.961); withholding computed with decimals and rounded
  once (st03: 292.080). After the fix the OECD lines went from 41 to 48 exact.
