# UK (kernel-2.x full-tax model): findings

## FT review (2026-11-21; dev cases of the FT grids only)

### Model fixes
- **UK FTR-1 (4400 SDLT, non-resident rates).** The model had no non-resident rates. FA 2003 s. 75ZA (1) (inserted by FA
  2021 Sch. 16 para. 2; point in time 2025-07-01): "this Part has effect as if 2% were added to each rate specified in
  the rate-specifying provisions", which s. 75ZA (2) lists as s. 55 (1B) Table A, Sch. 4ZA para. 1 (2) Table A and
  Sch. 6ZA para. 4 Table A (not Table B). Now `nonResidentBp := 200` on the residential duty. Found by FT1a
  (`uk_ft_sdlt_mfaysal_grid`, 60 non-resident purchases 2 % of the price too low).
- **UK FTR-2 (4400 SDLT, £40,000 de minimis).** The model applied the Sch. 4ZA higher rates to additional dwellings of
  any price. Sch. 4ZA para. 3 (2): "Condition A is that the chargeable consideration for the transaction is £40,000 or
  more"; the same threshold for non-resident transactions, Sch. 9A para. 2 (1) (d), (3) (a). Now `deMinimis` clears both
  flags below £40,000. Found by FT1a (23 additional homes under £40,000, 5 % too high).
- Both in `tools/specs/UK_Property.py` (block "FT review"), 9 new `#guard`s (46 in all); `b1.sh UK`: build, adapter A
  identical, B/C 56/56; the PIT field and every heading other than 4400 unchanged against the FT1d exe on the four SDLT
  dev grids, the worked cases and the 56-household grid (`global/ftreview/cmp_exe.py`). Dev with the new exe:
  mfaysal 620 -> 703 / 703, foxdavidson 630 -> 641 / 670, letbuddypro 437 -> 498 / 506, moverly 629 -> 657 / 704.

### Software errors (each residual miss of the SDLT grids is below £40,000)
- **UK FTS-1, property-mortgage-mcp stamp duty (foxdavidson), `uk_ft_sdlt_foxdavidson_grid`:** charges the Sch. 4ZA
  higher rates (27 dev cases) and the s. 75ZA 2 % (2 cases) on purchases under £40,000. Sch. 4ZA para. 3 (2); Sch. 9A
  para. 2 (1) (d), (3) (a).
- **UK FTS-2, conveyancing-toolkit sdlt-calculator (MoverlyLtd), `uk_ft_sdlt_moverly_grid`:** the same (34 additional,
  10 non-resident, 3 both, all under £40,000). Same provisions.
- **UK FTS-3, LetBuddy Pro (`uk_ft_sdlt_letbuddypro_grid`):** applies the s. 75ZA 2 % under £40,000 (8 cases, 5 of them
  also additional homes, where it does respect the Sch. 4ZA threshold). Sch. 9A para. 2 (1) (d), (3) (a).
- **UK FTR-3 (1200 CIT, model fix).** Losses brought forward were set off without limit. CTA 2010 s. 269ZB (2), (5):
  carried-forward trade-loss deductions may not exceed "50% of the company's relevant trading profits" plus "the
  company's trading profits deductions allowance"; s. 269ZF (1) (relevant profits net of the allowance); s. 269ZW (2):
  "The company's deductions allowance for the accounting period is £5,000,000" (point in time 2025-07-01). Now
  `lossFull := 5000000, lossExcessBp := 5000`; 3 guards. Every other UK cit grid stays 100 % exact; PIT unchanged.
- **UK FTS-4, Tax-Provision (`uk_ft_cit_taxprovision_grid`, software error).** Sets losses brought forward against
  the whole profit: the Part 7ZA restriction is not applied (29 dev cases with profit above £5 m and losses).
- **UK FTS-5, iht-calc (`uk_ft_inheritance_ihtcalc_grid`, software error).** Tapers the nil-rate band by 1 for every
  2 above 2 m; IHTA 1984 s. 8D (5) tapers the residence nil-rate band only; Sch. 1 keeps the 325,000 band. All 173
  dev misses are -130,000 (40 % x 325,000).
- **UK FTS-6, LateGenXer CGT (`uk_ft_cgt_lategenxer_grid`, software error, the coordinator's note confirmed on the 7
  above-misses).** Widens the basic rate band by the unused personal allowance; TCGA 1992 s. 1H charges gains at the
  lower rate only within the basic rate band left after taxable income.

- **UK FTR-4 (5200 VED, expensive car supplement on the list price; FT review 6).** VERA 1994 Sch. 1 para. 1GE (1) (a) "the
  price of the vehicle exceeds £40,000"; para. 1GF (1) (a): the price is the list price (`uk/law/vera1994_sch1_20250601.txt`
  l. 461-487). The model tested the vehicle's `value`; it now reads kernel 2.5.0 `.listPrice`, and 1GD £195 for a car first
  registered from 2020 needs a list price of £40,000 or less (or CO2 0 g before 1 April 2025, para. 1GE (1) (c) (ii)); without
  a list price such a car is grade C. `uk_ft_vehicle_govukved_grid` dev 550 -> **566 / 566** covered. Block appended to
  `tools/specs/UK_Other.py`; pit unchanged, only 5200 (16 dev lines).
- **UK FTR-5 (5200 VED, cars first registered before March 2001; FT review 7, Dataset round 4 R4-2).** VERA 1994 Sch. 1
  para. 1 (1): a vehicle with no other annual rate pays the general rate; (2) £360, except an electrically propelled vehicle
  or one with a cylinder capacity not exceeding 1,549 cc, for which (2A) the general rate is £220 (FA 2025 s. 66 (2), licences
  from 1.4.2025; `uk/law/vera1994_sch1_20250601.txt` l. 111-113). Para. 1B starts at 1 March 2001, so earlier cars were
  unmatched (grade C). Three rules added for cars first registered 1985-2000 (calendar-year boundary as for 1B; before 1985
  left C: historic vehicles, Sch. 2 para. 1A, not held). `uk_ft_vehicle_govukved_grid` dev 566 / 566 of 676 -> **676 / 676**.
  Block appended to `tools/specs/UK_Other.py`; `b1.sh UK`: A identical, B/C 56/56, 69 guards (6 new), 0 sorry; `cmpcc.sh UK`
  34 391 lines: pit 0, only 5200 (110 lines).
